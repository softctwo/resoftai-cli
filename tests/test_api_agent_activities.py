"""Tests for agent activities API routes."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.api.main import app
from resoftai.models.user import User
from resoftai.models.project import Project
from resoftai.models.agent_activity import AgentActivity
from resoftai.auth.security import create_access_token


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers."""
    token = create_access_token(
        data={"sub": test_user.username, "user_id": test_user.id}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_agent_activity(db: AsyncSession, test_project: Project) -> AgentActivity:
    """Create test agent activity."""
    activity = AgentActivity(
        project_id=test_project.id,
        agent_role="developer",
        status="idle",
        current_task="Implementing feature X",
        tokens_used=1500
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


@pytest.mark.asyncio
async def test_create_agent_activity(db: AsyncSession, test_project: Project, auth_headers: dict):
    """Test creating an agent activity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/agent-activities", headers=auth_headers, json={
            "project_id": test_project.id,
            "agent_role": "architect",
            "status": "working",
            "current_task": "Designing system architecture"
        })

    assert response.status_code == 201
    data = response.json()
    assert data["agent_role"] == "architect"
    assert data["status"] == "working"
    assert data["current_task"] == "Designing system architecture"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_agent_activity_project_not_found(db: AsyncSession, auth_headers: dict):
    """Test creating agent activity for non-existent project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/agent-activities", headers=auth_headers, json={
            "project_id": 99999,
            "agent_role": "developer",
            "status": "working"
        })

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_agent_activities(db: AsyncSession, test_project: Project, test_agent_activity: AgentActivity, auth_headers: dict):
    """Test listing agent activities for a project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/agent-activities?project_id={test_project.id}",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert "activities" in data
    assert data["total"] >= 1
    assert len(data["activities"]) >= 1


@pytest.mark.asyncio
async def test_list_agent_activities_missing_project_id(db: AsyncSession, auth_headers: dict):
    """Test listing agent activities without project_id."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/agent-activities", headers=auth_headers)

    assert response.status_code == 400
    assert "project_id is required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_agent_activities_filter_by_role(db: AsyncSession, test_project: Project, auth_headers: dict):
    """Test filtering agent activities by role."""
    # Create activities with different roles
    activity1 = AgentActivity(
        project_id=test_project.id,
        agent_role="developer",
        status="working",
        tokens_used=1000
    )
    activity2 = AgentActivity(
        project_id=test_project.id,
        agent_role="architect",
        status="working",
        tokens_used=500
    )
    db.add(activity1)
    db.add(activity2)
    await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/agent-activities?project_id={test_project.id}&agent_role=developer",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert all(a["agent_role"] == "developer" for a in data["activities"])


@pytest.mark.asyncio
async def test_list_agent_activities_filter_by_status(db: AsyncSession, test_project: Project, auth_headers: dict):
    """Test filtering agent activities by status."""
    # Create activities with different statuses
    activity1 = AgentActivity(
        project_id=test_project.id,
        agent_role="developer",
        status="working",
        tokens_used=1000
    )
    activity2 = AgentActivity(
        project_id=test_project.id,
        agent_role="developer",
        status="idle",
        tokens_used=500
    )
    db.add(activity1)
    db.add(activity2)
    await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/agent-activities?project_id={test_project.id}&status=working",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert all(a["status"] == "working" for a in data["activities"])


@pytest.mark.asyncio
async def test_list_active_agents(db: AsyncSession, test_project: Project, auth_headers: dict):
    """Test listing active agents."""
    # Create a working agent
    activity = AgentActivity(
        project_id=test_project.id,
        agent_role="developer",
        status="working",
        tokens_used=1000
    )
    db.add(activity)
    await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/agent-activities/active?project_id={test_project.id}",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_agent_activity(db: AsyncSession, test_agent_activity: AgentActivity, auth_headers: dict):
    """Test getting a specific agent activity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/agent-activities/{test_agent_activity.id}",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_agent_activity.id
    assert data["agent_role"] == test_agent_activity.agent_role


@pytest.mark.asyncio
async def test_get_agent_activity_not_found(db: AsyncSession, auth_headers: dict):
    """Test getting a non-existent agent activity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/agent-activities/99999", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_agent_activity(db: AsyncSession, test_agent_activity: AgentActivity, auth_headers: dict):
    """Test updating an agent activity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            f"/api/v1/agent-activities/{test_agent_activity.id}",
            headers=auth_headers,
            json={
                "status": "completed",
                "tokens_used": 2500
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["tokens_used"] == 2500


@pytest.mark.asyncio
async def test_update_agent_activity_not_found(db: AsyncSession, auth_headers: dict):
    """Test updating a non-existent agent activity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/agent-activities/99999",
            headers=auth_headers,
            json={"status": "completed"}
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_agent_activity(db: AsyncSession, test_project: Project, auth_headers: dict):
    """Test deleting an agent activity."""
    # Create an activity to delete
    activity = AgentActivity(
        project_id=test_project.id,
        agent_role="developer",
        status="idle",
        tokens_used=1000
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(
            f"/api/v1/agent-activities/{activity.id}",
            headers=auth_headers
        )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_agent_activity_not_found(db: AsyncSession, auth_headers: dict):
    """Test deleting a non-existent agent activity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/v1/agent-activities/99999", headers=auth_headers)

    assert response.status_code == 404
