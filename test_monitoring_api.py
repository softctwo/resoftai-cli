"""Test script for monitoring API endpoints."""
import asyncio
import aiohttp
import json


async def test_monitoring_api():
    """Test the monitoring API endpoints."""
    
    base_url = "http://localhost:8000/api"
    
    async with aiohttp.ClientSession() as session:
        print("Testing Monitoring API Endpoints...")
        print("=" * 50)
        
        # First, authenticate as admin
        print("\n1. Authenticating as admin...")
        auth_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        async with session.post(f"{base_url}/auth/login", data=auth_data) as response:
            if response.status != 200:
                print(f"   Authentication failed: {response.status}")
                return
            
            auth_result = await response.json()
            access_token = auth_result["access_token"]
            print(f"   Authentication successful")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test monitoring metrics endpoint
        print("\n2. Testing /api/monitoring/metrics...")
        async with session.get(f"{base_url}/monitoring/metrics", headers=headers) as response:
            if response.status == 200:
                metrics = await response.json()
                print(f"   Success! Metrics retrieved:")
                print(f"     Request Count: {metrics['request_count']}")
                print(f"     Average Response Time: {metrics['average_response_time']:.3f}s")
                print(f"     Active Agents: {metrics['active_agents']}")
            else:
                error = await response.text()
                print(f"   Failed: {response.status} - {error}")
        
        # Test monitoring agent activities endpoint
        print("\n3. Testing /api/monitoring/agent-activities...")
        async with session.get(f"{base_url}/monitoring/agent-activities", headers=headers) as response:
            if response.status == 200:
                activities = await response.json()
                print(f"   Success! {len(activities)} agent activities retrieved")
                for agent_id, activity in list(activities.items())[:3]:  # Show first 3
                    print(f"     Agent {agent_id}: {activity['agent_type']} - {activity['duration']}s")
            else:
                error = await response.text()
                print(f"   Failed: {response.status} - {error}")
        
        # Test monitoring status endpoint
        print("\n4. Testing /api/monitoring/status...")
        async with session.get(f"{base_url}/monitoring/status", headers=headers) as response:
            if response.status == 200:
                status = await response.json()
                print(f"   Success! Complete monitoring status retrieved")
                print(f"     Metrics: {status['metrics']['request_count']} requests")
                print(f"     Agent Activities: {len(status['agent_activities'])} activities")
            else:
                error = await response.text()
                print(f"   Failed: {response.status} - {error}")
        
        # Test monitoring reset endpoint
        print("\n5. Testing /api/monitoring/reset...")
        async with session.post(f"{base_url}/monitoring/reset", headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print(f"   Success! {result['message']}")
            else:
                error = await response.text()
                print(f"   Failed: {response.status} - {error}")
        
        print("\n" + "=" * 50)
        print("Monitoring API test completed!")


if __name__ == "__main__":
    asyncio.run(test_monitoring_api())