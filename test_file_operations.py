#!/usr/bin/env python
"""Test file operations for ResoftAI."""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from resoftai.db import get_db
from resoftai.crud import file as crud_file
from resoftai.crud.project import create_project
from resoftai.models.user import User


async def test_file_operations():
    """Test file creation, update, and versioning."""
    print("Testing file operations...")
    
    async for db in get_db():
        # Create a test user
        test_user = User(
            username="test_user",
            email="test@example.com",
            password_hash="test_hash",
            role="user"
        )
        db.add(test_user)
        await db.flush()
        
        # Create a test project
        project = await create_project(
            db,
            name="Test Project",
            requirements="Test project for file operations",
            user_id=test_user.id
        )
        await db.commit()
        
        print(f"Created project: {project.name} (ID: {project.id})")
        
        # Test 1: Create a file
        print("\n1. Creating a Python file...")
        file1 = await crud_file.create_file(
            db,
            project_id=project.id,
            path="main.py",
            content="print('Hello, World!')\n",
            language="python",
            created_by=test_user.id
        )
        await db.commit()
        print(f"   Created file: {file1.path} (ID: {file1.id})")
        print(f"   Content: {file1.content}")
        
        # Test 2: Update the file
        print("\n2. Updating the file...")
        updated_file = await crud_file.update_file(
            db,
            file_id=file1.id,
            content="def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()\n",
            created_by=test_user.id
        )
        await db.commit()
        print(f"   Updated file: version {updated_file.current_version}")
        print(f"   New content: {updated_file.content}")
        
        # Test 3: Get file versions
        print("\n3. Getting file versions...")
        versions = await crud_file.get_file_versions(db, file1.id)
        print(f"   Found {len(versions)} versions:")
        for version in versions:
            print(f"     Version {version.version}: {len(version.content)} chars")
        
        # Test 4: Restore to previous version
        print("\n4. Restoring to version 1...")
        restored_file = await crud_file.restore_file_version(
            db,
            file_id=file1.id,
            version=1,
            created_by=test_user.id
        )
        await db.commit()
        print(f"   Restored file: version {restored_file.current_version}")
        print(f"   Content: {restored_file.content}")
        
        # Test 5: List project files
        print("\n5. Listing project files...")
        files = await crud_file.get_files_by_project(db, project.id)
        print(f"   Found {len(files)} files:")
        for file in files:
            print(f"     {file.path} (v{file.current_version})")
        
        # Clean up
        await db.delete(test_user)
        await db.commit()
        
        print("\n✅ All file operations tests passed!")
        return True


if __name__ == "__main__":
    asyncio.run(test_file_operations())