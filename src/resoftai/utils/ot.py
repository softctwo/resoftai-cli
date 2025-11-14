"""
Operational Transformation (OT) algorithm for collaborative text editing.

This module implements a simplified OT algorithm for resolving conflicts
in real-time collaborative editing.

References:
- https://en.wikipedia.org/wiki/Operational_transformation
- https://operational-transformation.github.io/
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class OperationType(Enum):
    """Types of text operations."""
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"


@dataclass
class Operation:
    """
    Represents a single text operation.

    An operation can be:
    - INSERT: Insert text at position
    - DELETE: Delete n characters at position
    - RETAIN: Skip n characters (no change)
    """
    type: OperationType
    position: int
    text: Optional[str] = None  # For INSERT
    length: Optional[int] = None  # For DELETE/RETAIN

    def __repr__(self):
        if self.type == OperationType.INSERT:
            return f"Insert('{self.text}' at {self.position})"
        elif self.type == OperationType.DELETE:
            return f"Delete({self.length} chars at {self.position})"
        else:
            return f"Retain({self.length} chars from {self.position})"


class TextOperation:
    """
    A sequence of operations that transforms one text to another.

    Operations are stored in a normalized form for efficient transformation.
    """

    def __init__(self, operations: List[Operation] = None):
        """
        Initialize text operation.

        Args:
            operations: List of operations
        """
        self.operations = operations or []

    @classmethod
    def from_monaco_change(cls, change: Dict[str, Any]) -> 'TextOperation':
        """
        Create operation from Monaco editor change object.

        Args:
            change: Monaco editor change object with range and text

        Returns:
            TextOperation instance

        Example:
            change = {
                'range': {
                    'startLineNumber': 1,
                    'startColumn': 1,
                    'endLineNumber': 1,
                    'endColumn': 5
                },
                'text': 'Hello'
            }
        """
        operations = []

        # Extract range information
        range_obj = change.get('range', {})
        start_line = range_obj.get('startLineNumber', 1)
        start_col = range_obj.get('startColumn', 1)
        end_line = range_obj.get('endLineNumber', 1)
        end_col = range_obj.get('endColumn', 1)

        # Calculate position (simplified: assume 80 chars per line)
        position = (start_line - 1) * 80 + (start_col - 1)
        end_position = (end_line - 1) * 80 + (end_col - 1)

        text = change.get('text', '')

        # If range is not empty, it's a replace (delete + insert)
        if end_position > position:
            delete_length = end_position - position
            operations.append(Operation(
                type=OperationType.DELETE,
                position=position,
                length=delete_length
            ))

        # If text is not empty, insert it
        if text:
            operations.append(Operation(
                type=OperationType.INSERT,
                position=position,
                text=text
            ))

        return cls(operations)

    def apply(self, text: str) -> str:
        """
        Apply this operation to text.

        Args:
            text: Original text

        Returns:
            Transformed text
        """
        result = text
        offset = 0  # Track position changes due to insertions/deletions

        for op in self.operations:
            if op.type == OperationType.INSERT:
                pos = op.position + offset
                result = result[:pos] + op.text + result[pos:]
                offset += len(op.text)
            elif op.type == OperationType.DELETE:
                pos = op.position + offset
                result = result[:pos] + result[pos + op.length:]
                offset -= op.length

        return result

    def compose(self, other: 'TextOperation') -> 'TextOperation':
        """
        Compose this operation with another operation.

        compose(A, B) means: apply A first, then apply B.

        Args:
            other: Operation to compose with

        Returns:
            Composed operation
        """
        # Simplified composition - in production use a proper OT library
        return TextOperation(self.operations + other.operations)

    def __repr__(self):
        return f"TextOperation({self.operations})"


def transform(op1: TextOperation, op2: TextOperation) -> Tuple[TextOperation, TextOperation]:
    """
    Transform two concurrent operations against each other.

    This is the core of OT. Given two operations that were applied to the same
    document state, transform them so they can be applied in any order and
    produce the same result.

    Args:
        op1: First operation
        op2: Second operation

    Returns:
        Tuple of (transformed_op1, transformed_op2)

    Example:
        User A inserts "Hello" at position 0
        User B inserts "World" at position 0
        After transformation:
        - A's operation adjusted for B's change
        - B's operation adjusted for A's change
    """
    # Simplified transformation - handles basic cases
    # In production, use a proper OT library like ShareDB

    transformed_ops1 = []
    transformed_ops2 = []

    for op_a in op1.operations:
        for op_b in op2.operations:
            # Both are inserts
            if op_a.type == OperationType.INSERT and op_b.type == OperationType.INSERT:
                if op_b.position <= op_a.position:
                    # op_b comes before op_a, adjust op_a's position
                    transformed_ops1.append(Operation(
                        type=OperationType.INSERT,
                        position=op_a.position + len(op_b.text),
                        text=op_a.text
                    ))
                    transformed_ops2.append(op_b)
                else:
                    # op_a comes before op_b, adjust op_b's position
                    transformed_ops1.append(op_a)
                    transformed_ops2.append(Operation(
                        type=OperationType.INSERT,
                        position=op_b.position + len(op_a.text),
                        text=op_b.text
                    ))

            # Both are deletes
            elif op_a.type == OperationType.DELETE and op_b.type == OperationType.DELETE:
                # Handle overlapping deletes
                if op_b.position <= op_a.position:
                    # op_b comes before op_a
                    if op_b.position + op_b.length <= op_a.position:
                        # No overlap
                        transformed_ops1.append(Operation(
                            type=OperationType.DELETE,
                            position=op_a.position - op_b.length,
                            length=op_a.length
                        ))
                        transformed_ops2.append(op_b)
                    else:
                        # Overlapping - complex case
                        # For simplicity, keep both
                        transformed_ops1.append(op_a)
                        transformed_ops2.append(op_b)
                else:
                    transformed_ops1.append(op_a)
                    transformed_ops2.append(Operation(
                        type=OperationType.DELETE,
                        position=op_b.position - op_a.length,
                        length=op_b.length
                    ))

            # One insert, one delete
            elif op_a.type == OperationType.INSERT and op_b.type == OperationType.DELETE:
                if op_b.position <= op_a.position:
                    transformed_ops1.append(Operation(
                        type=OperationType.INSERT,
                        position=max(0, op_a.position - op_b.length),
                        text=op_a.text
                    ))
                else:
                    transformed_ops1.append(op_a)
                transformed_ops2.append(op_b)

            elif op_a.type == OperationType.DELETE and op_b.type == OperationType.INSERT:
                if op_b.position <= op_a.position:
                    transformed_ops1.append(Operation(
                        type=OperationType.DELETE,
                        position=op_a.position + len(op_b.text),
                        length=op_a.length
                    ))
                else:
                    transformed_ops1.append(op_a)
                transformed_ops2.append(op_b)

    # If no transformations were made, return original operations
    if not transformed_ops1:
        transformed_ops1 = op1.operations
    if not transformed_ops2:
        transformed_ops2 = op2.operations

    return (
        TextOperation(transformed_ops1),
        TextOperation(transformed_ops2)
    )


class OTDocument:
    """
    Document with OT support for collaborative editing.

    Maintains document state and version history.
    """

    def __init__(self, initial_content: str = "", doc_id: str = None):
        """
        Initialize OT document.

        Args:
            initial_content: Initial document content
            doc_id: Document identifier
        """
        self.content = initial_content
        self.doc_id = doc_id
        self.version = 0
        self.history: List[Tuple[int, TextOperation]] = []

    def apply_operation(self, operation: TextOperation, version: int = None) -> bool:
        """
        Apply operation to document.

        Args:
            operation: Operation to apply
            version: Client's document version (for conflict detection)

        Returns:
            True if successful, False if version mismatch
        """
        # Check version
        if version is not None and version != self.version:
            return False

        # Apply operation
        try:
            self.content = operation.apply(self.content)
            self.version += 1
            self.history.append((self.version, operation))
            return True
        except Exception:
            return False

    def get_operations_since(self, version: int) -> List[TextOperation]:
        """
        Get all operations since a specific version.

        Args:
            version: Starting version

        Returns:
            List of operations
        """
        return [op for v, op in self.history if v > version]

    def transform_operation(self, operation: TextOperation, from_version: int) -> TextOperation:
        """
        Transform an operation from an old version to current version.

        Args:
            operation: Operation to transform
            from_version: Version the operation was created at

        Returns:
            Transformed operation that can be applied to current version
        """
        # Get all operations between from_version and current version
        concurrent_ops = self.get_operations_since(from_version)

        # Transform against each concurrent operation
        transformed = operation
        for concurrent_op in concurrent_ops:
            transformed, _ = transform(transformed, concurrent_op)

        return transformed

    def __repr__(self):
        return f"OTDocument(version={self.version}, length={len(self.content)})"


# Document registry for managing multiple documents
class DocumentRegistry:
    """Registry for managing multiple OT documents."""

    def __init__(self):
        """Initialize document registry."""
        self.documents: Dict[str, OTDocument] = {}

    def get_or_create(self, doc_id: str, initial_content: str = "") -> OTDocument:
        """
        Get or create a document.

        Args:
            doc_id: Document identifier
            initial_content: Initial content if creating new document

        Returns:
            OTDocument instance
        """
        if doc_id not in self.documents:
            self.documents[doc_id] = OTDocument(initial_content, doc_id)
        return self.documents[doc_id]

    def get(self, doc_id: str) -> Optional[OTDocument]:
        """Get document by ID."""
        return self.documents.get(doc_id)

    def delete(self, doc_id: str) -> bool:
        """Delete document."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False


# Global document registry
document_registry = DocumentRegistry()
