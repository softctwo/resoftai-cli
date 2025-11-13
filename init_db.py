#!/usr/bin/env python
"""Initialize the database with all tables."""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from resoftai.db import init_db, Base, engine
from resoftai.models import user, project, file, llm_config, agent_activity, log, task


async def initialize_database():
    """Initialize the database with all tables."""
    print("Initializing database...")
    
    # Import all models to ensure they are registered with Base
    print("Models imported:")
    print(f"  - User: {hasattr(user, 'User')}")
    print(f"  - Project: {hasattr(project, 'Project')}")
    print(f"  - File: {hasattr(file, 'File')}")
    print(f"  - FileVersion: {hasattr(file, 'FileVersion')}")
    print(f"  - LLMConfig: {hasattr(llm_config, 'LLMConfigModel')}")
    print(f"  - AgentActivity: {hasattr(agent_activity, 'AgentActivity')}")
    print(f"  - Log: {hasattr(log, 'Log')}")
    print(f"  - Task: {hasattr(task, 'Task')}")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized successfully!")
    
    # Check what tables were created
    async with engine.begin() as conn:
        result = await conn.run_sync(lambda sync_conn: sync_conn.execute("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        print(f"\nTables created: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")


if __name__ == "__main__":
    asyncio.run(initialize_database())