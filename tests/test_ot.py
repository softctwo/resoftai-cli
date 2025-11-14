"""Tests for Operational Transformation (OT) algorithm."""
import pytest
from resoftai.utils.ot import (
    Operation,
    OperationType,
    TextOperation,
    transform,
    OTDocument,
    DocumentRegistry
)


class TestOperation:
    """Test Operation class."""

    def test_insert_operation(self):
        """Test insert operation creation."""
        op = Operation(
            type=OperationType.INSERT,
            position=5,
            text="Hello"
        )

        assert op.type == OperationType.INSERT
        assert op.position == 5
        assert op.text == "Hello"
        assert "Insert" in str(op)

    def test_delete_operation(self):
        """Test delete operation creation."""
        op = Operation(
            type=OperationType.DELETE,
            position=5,
            length=3
        )

        assert op.type == OperationType.DELETE
        assert op.position == 5
        assert op.length == 3
        assert "Delete" in str(op)

    def test_retain_operation(self):
        """Test retain operation creation."""
        op = Operation(
            type=OperationType.RETAIN,
            position=0,
            length=10
        )

        assert op.type == OperationType.RETAIN
        assert op.position == 0
        assert op.length == 10
        assert "Retain" in str(op)


class TestTextOperation:
    """Test TextOperation class."""

    def test_create_empty_operation(self):
        """Test creating empty operation."""
        op = TextOperation()
        assert len(op.operations) == 0

    def test_create_with_operations(self):
        """Test creating operation with operations list."""
        ops = [
            Operation(OperationType.INSERT, 0, text="Hello")
        ]
        op = TextOperation(ops)
        assert len(op.operations) == 1

    def test_from_monaco_change_insert(self):
        """Test creating operation from Monaco insert change."""
        change = {
            'range': {
                'startLineNumber': 1,
                'startColumn': 1,
                'endLineNumber': 1,
                'endColumn': 1
            },
            'text': 'Hello'
        }

        op = TextOperation.from_monaco_change(change)
        assert len(op.operations) == 1
        assert op.operations[0].type == OperationType.INSERT
        assert op.operations[0].text == 'Hello'

    def test_from_monaco_change_replace(self):
        """Test creating operation from Monaco replace change."""
        change = {
            'range': {
                'startLineNumber': 1,
                'startColumn': 1,
                'endLineNumber': 1,
                'endColumn': 5
            },
            'text': 'Hi'
        }

        op = TextOperation.from_monaco_change(change)
        # Should have DELETE + INSERT
        assert len(op.operations) == 2
        assert op.operations[0].type == OperationType.DELETE
        assert op.operations[1].type == OperationType.INSERT

    def test_apply_insert(self):
        """Test applying insert operation."""
        text = "World"
        op = TextOperation([
            Operation(OperationType.INSERT, 0, text="Hello ")
        ])

        result = op.apply(text)
        assert result == "Hello World"

    def test_apply_delete(self):
        """Test applying delete operation."""
        text = "Hello World"
        op = TextOperation([
            Operation(OperationType.DELETE, 6, length=5)
        ])

        result = op.apply(text)
        assert result == "Hello "

    def test_apply_multiple_operations(self):
        """Test applying multiple operations."""
        text = "Hello"
        op = TextOperation([
            Operation(OperationType.INSERT, 5, text=" World"),
            Operation(OperationType.DELETE, 0, length=1)
        ])

        result = op.apply(text)
        assert result == "ello World"

    def test_compose(self):
        """Test composing operations."""
        op1 = TextOperation([
            Operation(OperationType.INSERT, 0, text="A")
        ])
        op2 = TextOperation([
            Operation(OperationType.INSERT, 1, text="B")
        ])

        composed = op1.compose(op2)
        assert len(composed.operations) == 2


class TestTransform:
    """Test OT transformation algorithm."""

    def test_transform_concurrent_inserts_same_position(self):
        """Test transforming two inserts at same position."""
        # User A inserts "A" at position 0
        op_a = TextOperation([
            Operation(OperationType.INSERT, 0, text="A")
        ])

        # User B inserts "B" at position 0
        op_b = TextOperation([
            Operation(OperationType.INSERT, 0, text="B")
        ])

        # Transform
        op_a_prime, op_b_prime = transform(op_a, op_b)

        # Both should have operations
        assert len(op_a_prime.operations) > 0
        assert len(op_b_prime.operations) > 0

    def test_transform_concurrent_inserts_different_positions(self):
        """Test transforming two inserts at different positions."""
        # User A inserts "A" at position 0
        op_a = TextOperation([
            Operation(OperationType.INSERT, 0, text="A")
        ])

        # User B inserts "B" at position 5
        op_b = TextOperation([
            Operation(OperationType.INSERT, 5, text="B")
        ])

        # Transform
        op_a_prime, op_b_prime = transform(op_a, op_b)

        # Position of op_b should be adjusted for op_a's insert
        assert len(op_b_prime.operations) > 0
        # B should now be at position 6 (5 + len("A"))
        assert op_b_prime.operations[0].position == 6

    def test_transform_concurrent_deletes(self):
        """Test transforming two deletes."""
        # User A deletes 3 chars at position 0
        op_a = TextOperation([
            Operation(OperationType.DELETE, 0, length=3)
        ])

        # User B deletes 2 chars at position 5
        op_b = TextOperation([
            Operation(OperationType.DELETE, 5, length=2)
        ])

        # Transform
        op_a_prime, op_b_prime = transform(op_a, op_b)

        # Position of op_b should be adjusted
        assert len(op_b_prime.operations) > 0
        # B's delete should now be at position 2 (5 - 3)
        assert op_b_prime.operations[0].position == 2

    def test_transform_insert_and_delete(self):
        """Test transforming insert and delete operations."""
        # User A inserts "ABC" at position 0
        op_a = TextOperation([
            Operation(OperationType.INSERT, 0, text="ABC")
        ])

        # User B deletes 2 chars at position 5
        op_b = TextOperation([
            Operation(OperationType.DELETE, 5, length=2)
        ])

        # Transform
        op_a_prime, op_b_prime = transform(op_a, op_b)

        # Both operations should be preserved
        assert len(op_a_prime.operations) > 0
        assert len(op_b_prime.operations) > 0


class TestOTDocument:
    """Test OTDocument class."""

    def test_create_document(self):
        """Test creating OT document."""
        doc = OTDocument("Hello World", "doc1")

        assert doc.content == "Hello World"
        assert doc.doc_id == "doc1"
        assert doc.version == 0
        assert len(doc.history) == 0

    def test_apply_operation_success(self):
        """Test applying operation successfully."""
        doc = OTDocument("Hello", "doc1")

        op = TextOperation([
            Operation(OperationType.INSERT, 5, text=" World")
        ])

        result = doc.apply_operation(op)

        assert result is True
        assert doc.content == "Hello World"
        assert doc.version == 1
        assert len(doc.history) == 1

    def test_apply_operation_version_mismatch(self):
        """Test applying operation with wrong version."""
        doc = OTDocument("Hello", "doc1")

        # Apply first operation
        op1 = TextOperation([
            Operation(OperationType.INSERT, 5, text=" World")
        ])
        doc.apply_operation(op1)

        # Try to apply another operation with old version
        op2 = TextOperation([
            Operation(OperationType.INSERT, 0, text="Hi ")
        ])
        result = doc.apply_operation(op2, version=0)

        assert result is False  # Should fail due to version mismatch
        assert doc.version == 1  # Version unchanged
        assert doc.content == "Hello World"  # Content unchanged

    def test_get_operations_since(self):
        """Test getting operations since version."""
        doc = OTDocument("", "doc1")

        # Apply several operations
        for i in range(5):
            op = TextOperation([
                Operation(OperationType.INSERT, i, text=str(i))
            ])
            doc.apply_operation(op)

        # Get operations since version 2
        ops = doc.get_operations_since(2)

        assert len(ops) == 3  # Versions 3, 4, 5

    def test_transform_operation(self):
        """Test transforming operation to current version."""
        doc = OTDocument("ABC", "doc1")

        # Apply operation (version 0 -> 1)
        op1 = TextOperation([
            Operation(OperationType.INSERT, 0, text="X")
        ])
        doc.apply_operation(op1)  # Content: "XABC"

        # Create operation at old version (0)
        op_old = TextOperation([
            Operation(OperationType.INSERT, 0, text="Y")
        ])

        # Transform to current version
        op_transformed = doc.transform_operation(op_old, from_version=0)

        # Apply transformed operation
        result = op_transformed.apply(doc.content)

        # Should work without conflict
        assert "Y" in result


class TestDocumentRegistry:
    """Test DocumentRegistry class."""

    def test_get_or_create_new(self):
        """Test getting or creating new document."""
        registry = DocumentRegistry()

        doc = registry.get_or_create("doc1", "Initial content")

        assert doc is not None
        assert doc.doc_id == "doc1"
        assert doc.content == "Initial content"

    def test_get_or_create_existing(self):
        """Test getting existing document."""
        registry = DocumentRegistry()

        doc1 = registry.get_or_create("doc1", "Content 1")
        doc2 = registry.get_or_create("doc1", "Content 2")

        # Should return same document
        assert doc1 is doc2
        assert doc1.content == "Content 1"  # Original content preserved

    def test_get(self):
        """Test getting document."""
        registry = DocumentRegistry()

        registry.get_or_create("doc1", "Content")
        doc = registry.get("doc1")

        assert doc is not None
        assert doc.doc_id == "doc1"

        # Non-existent document
        assert registry.get("doc2") is None

    def test_delete(self):
        """Test deleting document."""
        registry = DocumentRegistry()

        registry.get_or_create("doc1", "Content")
        result = registry.delete("doc1")

        assert result is True
        assert registry.get("doc1") is None

        # Delete non-existent
        result = registry.delete("doc2")
        assert result is False


# Integration tests

class TestOTIntegration:
    """Integration tests for OT system."""

    def test_concurrent_editing_scenario(self):
        """Test realistic concurrent editing scenario."""
        # Initial document state
        doc = OTDocument("Hello World", "doc1")

        # User A at version 0: Insert "!" at end
        op_a = TextOperation([
            Operation(OperationType.INSERT, 11, text="!")
        ])

        # User B at version 0: Insert "Beautiful " after "Hello "
        op_b = TextOperation([
            Operation(OperationType.INSERT, 6, text="Beautiful ")
        ])

        # Apply A's operation first
        doc.apply_operation(op_a)  # "Hello World!"

        # Transform B's operation to version 1
        op_b_transformed = doc.transform_operation(op_b, from_version=0)

        # Apply transformed B's operation
        doc.apply_operation(op_b_transformed)

        # Result should be "Hello Beautiful World!"
        assert "Hello" in doc.content
        assert "Beautiful" in doc.content
        assert "World!" in doc.content

    def test_multiple_users_editing(self):
        """Test multiple users editing concurrently."""
        doc = OTDocument("", "doc1")

        # User 1 inserts "A"
        op1 = TextOperation([Operation(OperationType.INSERT, 0, text="A")])
        doc.apply_operation(op1)

        # User 2 inserts "B" (at same version as User 1)
        op2 = TextOperation([Operation(OperationType.INSERT, 0, text="B")])
        op2_transformed = doc.transform_operation(op2, from_version=0)
        doc.apply_operation(op2_transformed)

        # User 3 inserts "C"
        op3 = TextOperation([Operation(OperationType.INSERT, 0, text="C")])
        op3_transformed = doc.transform_operation(op3, from_version=0)
        doc.apply_operation(op3_transformed)

        # All characters should be present
        assert len(doc.content) == 3
        assert "A" in doc.content
        assert "B" in doc.content
        assert "C" in doc.content
