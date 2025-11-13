#!/usr/bin/env python3
"""Initialize database with tables and default data."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resoftai.db import init_db, AsyncSessionLocal
from resoftai.crud.user import create_user, get_user_by_username
from resoftai.config import Settings


async def create_default_admin():
    """Create default admin user if not exists."""
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        admin = await get_user_by_username(db, username="admin")

        if not admin:
            print("Creating default admin user...")
            admin = await create_user(
                db=db,
                username="admin",
                email="admin@resoftai.com",
                password="admin123",  # Change this in production!
                role="admin"
            )
            print(f"✓ Created admin user: {admin.username}")
        else:
            print(f"✓ Admin user already exists: {admin.username}")


async def main():
    """Main initialization function."""
    settings = Settings()

    print("=" * 60)
    print("ResoftAI Database Initialization")
    print("=" * 60)

    print(f"\nDatabase URL: {settings.database_url}")

    print("\n1. Creating database tables...")
    await init_db()
    print("✓ Database tables created")

    print("\n2. Creating default admin user...")
    await create_default_admin()

    print("\n" + "=" * 60)
    print("Database initialization completed!")
    print("=" * 60)

    print("\nDefault credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n⚠️  CHANGE THE DEFAULT PASSWORD IN PRODUCTION!")


if __name__ == "__main__":
    asyncio.run(main())
