"""
Collaborative editing integration with OT algorithm and message batching.

This module integrates Operational Transformation (OT) algorithm with
WebSocket message handling for real-time collaborative editing.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict

from resoftai.utils.ot import (
    TextOperation,
    transform,
    document_registry,
    OTDocument
)
from resoftai.utils.performance import message_batcher, performance_monitor
from resoftai.websocket.manager import manager, sio

logger = logging.getLogger(__name__)


class CollaborativeEditManager:
    """
    Manages collaborative editing with OT and message batching.

    Coordinates between:
    - OT document state
    - WebSocket connections
    - Message batching for performance
    """

    def __init__(self):
        """Initialize collaborative edit manager."""
        self.pending_operations: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.batch_timers: Dict[int, asyncio.Task] = {}
        self.batch_interval = 0.1  # 100ms batching window

    async def handle_edit_operation(
        self,
        file_id: int,
        user_id: int,
        username: str,
        changes: Dict[str, Any],
        client_version: int
    ) -> Optional[Dict[str, Any]]:
        """
        Handle an edit operation with OT transformation.

        Args:
            file_id: File being edited
            user_id: User making the edit
            username: Username
            changes: Monaco editor change object
            client_version: Client's document version

        Returns:
            Transformed operation data or None if conflict
        """
        try:
            # Get or create OT document
            doc = document_registry.get_or_create(
                doc_id=f"file:{file_id}",
                initial_content=""  # TODO: Load from database
            )

            # Convert Monaco change to OT operation
            operation = TextOperation.from_monaco_change(changes)

            # Transform operation if client is behind
            if client_version < doc.version:
                logger.info(
                    f"Transforming operation from version {client_version} "
                    f"to {doc.version} for file {file_id}"
                )
                operation = doc.transform_operation(operation, client_version)

            # Apply operation
            if doc.apply_operation(operation):
                # Prepare broadcast data
                broadcast_data = {
                    'file_id': file_id,
                    'user_id': user_id,
                    'username': username,
                    'changes': changes,
                    'version': doc.version,
                    'transformed': client_version < doc.version
                }

                # Add to batch
                await self._batch_broadcast(file_id, broadcast_data)

                # Record metrics
                performance_monitor.increment_counter('ot.operations_applied')
                if broadcast_data['transformed']:
                    performance_monitor.increment_counter('ot.operations_transformed')

                return broadcast_data
            else:
                logger.warning(
                    f"Failed to apply operation for file {file_id}, "
                    f"version mismatch"
                )
                performance_monitor.increment_counter('ot.operation_conflicts')
                return None

        except Exception as e:
            logger.error(f"Error handling edit operation: {e}", exc_info=True)
            performance_monitor.increment_counter('ot.errors')
            return None

    async def _batch_broadcast(self, file_id: int, data: Dict[str, Any]):
        """
        Add operation to batch for broadcasting.

        Uses message batching to reduce network overhead.

        Args:
            file_id: File ID
            data: Operation data to broadcast
        """
        self.pending_operations[file_id].append(data)

        # Start batch timer if not already running
        if file_id not in self.batch_timers or self.batch_timers[file_id].done():
            self.batch_timers[file_id] = asyncio.create_task(
                self._flush_batch_after_delay(file_id)
            )

    async def _flush_batch_after_delay(self, file_id: int):
        """
        Flush batch after delay.

        Args:
            file_id: File ID
        """
        await asyncio.sleep(self.batch_interval)
        await self._flush_batch(file_id)

    async def _flush_batch(self, file_id: int):
        """
        Flush pending operations for a file.

        Args:
            file_id: File ID
        """
        if file_id not in self.pending_operations:
            return

        operations = self.pending_operations[file_id]
        if not operations:
            return

        # Clear pending operations
        self.pending_operations[file_id] = []

        # Cancel timer
        if file_id in self.batch_timers:
            if not self.batch_timers[file_id].done():
                self.batch_timers[file_id].cancel()
            del self.batch_timers[file_id]

        # Decide whether to send individual or batched
        if len(operations) == 1:
            # Single operation - send individually
            await manager.broadcast_to_file(
                file_id,
                "file.edit",
                operations[0],
                exclude_sid=operations[0].get('sid')
            )
        else:
            # Multiple operations - send as batch
            await manager.broadcast_to_file(
                file_id,
                "file.edit_batch",
                {
                    'file_id': file_id,
                    'operations': operations,
                    'count': len(operations)
                }
            )

        # Record metrics
        performance_monitor.increment_counter('collaborative.batches_flushed')
        performance_monitor.increment_counter(
            'collaborative.operations_batched',
            len(operations)
        )

        logger.debug(
            f"Flushed batch of {len(operations)} operations for file {file_id}"
        )

    async def handle_cursor_update(
        self,
        file_id: int,
        user_id: int,
        username: str,
        position: Dict[str, int],
        selection: Optional[Dict[str, Any]] = None
    ):
        """
        Handle cursor position update with batching.

        Cursor updates are batched separately from edit operations.

        Args:
            file_id: File ID
            user_id: User ID
            username: Username
            position: Cursor position
            selection: Selection range (optional)
        """
        # Use message batcher for cursor updates
        cursor_data = {
            'file_id': file_id,
            'user_id': user_id,
            'username': username,
            'position': position,
            'selection': selection
        }

        async def flush_cursor_batch(messages: List[Dict]):
            """Flush cursor update batch."""
            if len(messages) == 1:
                # Single cursor update
                await manager.broadcast_to_file(
                    file_id,
                    "cursor.position",
                    messages[0]
                )
            else:
                # Batch cursor updates
                await manager.broadcast_to_file(
                    file_id,
                    "cursor.batch",
                    {
                        'file_id': file_id,
                        'cursors': messages
                    }
                )

        await message_batcher.add_message(
            key=f"cursor:{file_id}",
            message=cursor_data,
            flush_callback=flush_cursor_batch
        )

    async def get_document_state(self, file_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current document state.

        Args:
            file_id: File ID

        Returns:
            Document state dict or None
        """
        doc = document_registry.get(f"file:{file_id}")
        if doc:
            return {
                'file_id': file_id,
                'content': doc.content,
                'version': doc.version,
                'operations_count': len(doc.history)
            }
        return None

    async def initialize_document(
        self,
        file_id: int,
        content: str
    ) -> OTDocument:
        """
        Initialize OT document with content.

        Args:
            file_id: File ID
            content: Initial content

        Returns:
            OTDocument instance
        """
        doc = document_registry.get_or_create(
            doc_id=f"file:{file_id}",
            initial_content=content
        )
        logger.info(f"Initialized OT document for file {file_id}")
        return doc

    async def cleanup_document(self, file_id: int):
        """
        Cleanup document when all users leave.

        Args:
            file_id: File ID
        """
        doc_id = f"file:{file_id}"

        # Flush any pending operations
        await self._flush_batch(file_id)

        # Remove document from registry
        if document_registry.delete(doc_id):
            logger.info(f"Cleaned up OT document for file {file_id}")

        # Cancel any pending timers
        if file_id in self.batch_timers:
            if not self.batch_timers[file_id].done():
                self.batch_timers[file_id].cancel()
            del self.batch_timers[file_id]

        # Clear pending operations
        if file_id in self.pending_operations:
            del self.pending_operations[file_id]


# Global collaborative edit manager
collaborative_manager = CollaborativeEditManager()


# Enhanced WebSocket event handlers with OT

async def handle_file_edit_with_ot(
    sid: str,
    file_id: int,
    changes: Dict[str, Any],
    client_version: int = 0
):
    """
    Handle file edit with OT transformation.

    Args:
        sid: Session ID
        file_id: File ID
        changes: Monaco editor changes
        client_version: Client's document version
    """
    # Get user info
    user_info = manager.session_user_info.get(sid)
    if not user_info:
        await sio.emit('error', {
            'message': 'Not in a file session'
        }, room=sid)
        return

    # Handle with OT
    result = await collaborative_manager.handle_edit_operation(
        file_id=file_id,
        user_id=user_info['user_id'],
        username=user_info['username'],
        changes=changes,
        client_version=client_version
    )

    if result:
        # Acknowledge to sender
        await sio.emit('file.edit_ack', {
            'file_id': file_id,
            'version': result['version'],
            'transformed': result.get('transformed', False)
        }, room=sid)
    else:
        # Send conflict notification
        await sio.emit('file.edit_conflict', {
            'file_id': file_id,
            'message': 'Version conflict, please refresh'
        }, room=sid)


async def handle_cursor_position_with_batching(
    sid: str,
    file_id: int,
    position: Dict[str, int],
    selection: Optional[Dict[str, Any]] = None
):
    """
    Handle cursor position with batching.

    Args:
        sid: Session ID
        file_id: File ID
        position: Cursor position
        selection: Selection range (optional)
    """
    # Get user info
    user_info = manager.session_user_info.get(sid)
    if not user_info:
        return

    # Handle with batching
    await collaborative_manager.handle_cursor_update(
        file_id=file_id,
        user_id=user_info['user_id'],
        username=user_info['username'],
        position=position,
        selection=selection
    )
