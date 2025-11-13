#!/usr/bin/env python3
"""
Database initialization script.

This script creates all database tables from the SQLAlchemy models.
"""
import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from resoftai.db.connection import init_db, Base
from resoftai.models import user, project, agent_activity, task, file, llm_config, log


async def main():
    """Initialize the database."""
    print("🔧 Initializing database...")
    print(f"📁 Database models loaded:")
    print(f"   - User")
    print(f"   - Project")
    print(f"   - AgentActivity")
    print(f"   - Task")
    print(f"   - File")
    print(f"   - LLMConfig")
    print(f"   - Log")

    try:
        await init_db()
        print("\n✅ Database initialized successfully!")
        print(f"📊 Tables created:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
