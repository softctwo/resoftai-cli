"""
Slack Integration Plugin - Example Integration Plugin for ResoftAI

Sends notifications to Slack channels for various project events.
"""
import json
import asyncio
from typing import Dict, Any
from datetime import datetime
import aiohttp

from resoftai.plugins.base import IntegrationPlugin, PluginContext


class SlackIntegrationPlugin(IntegrationPlugin):
    """
    Slack integration plugin for sending notifications
    
    Sends messages to Slack channels when:
    - Projects are created/completed
    - Agents complete tasks
    - Code quality issues are found
    - Errors occur
    """

    def __init__(self, metadata, config):
        super().__init__(metadata, config)
        self.webhook_url = config.get("webhook_url")
        self.default_channel = config.get("default_channel", "#resoftai")
        self.username = config.get("username", "ResoftAI Bot")
        self.icon_emoji = config.get("icon_emoji", ":robot_face:")
        self.enabled_events = config.get("enabled_events", [
            "project.created",
            "project.completed",
            "agent.completed",
            "code_quality.failed"
        ])

    def load(self, context: PluginContext) -> bool:
        """Initialize plugin"""
        self.context = context
        self.context.log_info(f"Loading {self.metadata.name} v{self.metadata.version}")

        # Validate configuration
        if not self.webhook_url:
            self.context.log_error("Slack webhook URL not configured")
            return False

        self.context.log_info(f"Slack webhook configured for channel: {self.default_channel}")
        self.context.log_info(f"Enabled events: {', '.join(self.enabled_events)}")

        return True

    def activate(self) -> bool:
        """Activate plugin and register hooks"""
        self.context.log_info(f"Activating {self.metadata.name}")

        # Register action hooks for events we want to monitor
        # Note: In a real implementation, this would be done via HookManager
        # This is a demonstration of the intent

        self.context.log_info(f"{self.metadata.name} activated successfully")
        return True

    def deactivate(self) -> bool:
        """Deactivate plugin"""
        self.context.log_info(f"Deactivating {self.metadata.name}")
        return True

    def unload(self) -> bool:
        """Clean up resources"""
        self.context.log_info(f"Unloading {self.metadata.name}")
        return True

    def get_integration_name(self) -> str:
        """Return integration identifier"""
        return "slack"

    async def send_notification(self, event: str, data: Dict[str, Any]) -> bool:
        """
        Send notification to Slack

        Args:
            event: Event type (e.g., "project.created")
            data: Event data

        Returns:
            True if sent successfully
        """
        # Check if event is enabled
        if event not in self.enabled_events:
            return True  # Skip silently

        # Build message based on event type
        message = self._build_message(event, data)

        if not message:
            return True

        # Send to Slack
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "channel": data.get("channel", self.default_channel),
                    "username": self.username,
                    "icon_emoji": self.icon_emoji,
                    "attachments": [message]
                }

                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.context.log_info(f"Sent Slack notification for event: {event}")
                        return True
                    else:
                        error_text = await response.text()
                        self.context.log_error(f"Failed to send Slack notification: {error_text}")
                        return False

        except Exception as e:
            self.context.log_error(f"Error sending Slack notification: {str(e)}")
            return False

    def _build_message(self, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build Slack message attachment based on event type"""

        if event == "project.created":
            return {
                "color": "good",
                "title": f"🚀 New Project Created: {data.get('name', 'Unknown')}",
                "text": data.get("requirements", "No description"),
                "fields": [
                    {
                        "title": "Project ID",
                        "value": str(data.get("id", "N/A")),
                        "short": True
                    },
                    {
                        "title": "Owner",
                        "value": data.get("owner", "Unknown"),
                        "short": True
                    }
                ],
                "footer": "ResoftAI",
                "ts": int(datetime.utcnow().timestamp())
            }

        elif event == "project.completed":
            return {
                "color": "good",
                "title": f"✅ Project Completed: {data.get('name', 'Unknown')}",
                "text": f"Project has been successfully completed!",
                "fields": [
                    {
                        "title": "Duration",
                        "value": data.get("duration", "N/A"),
                        "short": True
                    },
                    {
                        "title": "Files Created",
                        "value": str(data.get("files_count", 0)),
                        "short": True
                    }
                ],
                "footer": "ResoftAI",
                "ts": int(datetime.utcnow().timestamp())
            }

        elif event == "agent.completed":
            agent_name = data.get("agent", "Unknown")
            return {
                "color": "#36a64f",
                "title": f"🤖 Agent Task Completed: {agent_name}",
                "text": data.get("task", "Task completed"),
                "fields": [
                    {
                        "title": "Status",
                        "value": data.get("status", "success"),
                        "short": True
                    },
                    {
                        "title": "Tokens Used",
                        "value": str(data.get("tokens", 0)),
                        "short": True
                    }
                ],
                "footer": "ResoftAI",
                "ts": int(datetime.utcnow().timestamp())
            }

        elif event == "code_quality.failed":
            return {
                "color": "danger",
                "title": f"⚠️ Code Quality Issues Found",
                "text": f"Found {data.get('issue_count', 0)} issues in the code",
                "fields": [
                    {
                        "title": "Critical",
                        "value": str(data.get("critical", 0)),
                        "short": True
                    },
                    {
                        "title": "High",
                        "value": str(data.get("high", 0)),
                        "short": True
                    },
                    {
                        "title": "Medium",
                        "value": str(data.get("medium", 0)),
                        "short": True
                    },
                    {
                        "title": "Low",
                        "value": str(data.get("low", 0)),
                        "short": True
                    }
                ],
                "footer": "ResoftAI",
                "ts": int(datetime.utcnow().timestamp())
            }

        elif event == "error":
            return {
                "color": "danger",
                "title": f"❌ Error Occurred",
                "text": data.get("message", "An error occurred"),
                "fields": [
                    {
                        "title": "Error Type",
                        "value": data.get("type", "Unknown"),
                        "short": True
                    },
                    {
                        "title": "Component",
                        "value": data.get("component", "Unknown"),
                        "short": True
                    }
                ],
                "footer": "ResoftAI",
                "ts": int(datetime.utcnow().timestamp())
            }

        return None

    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON Schema for plugin configuration"""
        return {
            "type": "object",
            "required": ["webhook_url"],
            "properties": {
                "webhook_url": {
                    "type": "string",
                    "format": "uri",
                    "description": "Slack webhook URL (obtain from Slack App settings)"
                },
                "default_channel": {
                    "type": "string",
                    "default": "#resoftai",
                    "description": "Default channel for notifications"
                },
                "username": {
                    "type": "string",
                    "default": "ResoftAI Bot",
                    "description": "Bot username to display in Slack"
                },
                "icon_emoji": {
                    "type": "string",
                    "default": ":robot_face:",
                    "description": "Emoji icon for bot"
                },
                "enabled_events": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "project.created",
                            "project.completed",
                            "agent.completed",
                            "code_quality.failed",
                            "error"
                        ]
                    },
                    "default": [
                        "project.created",
                        "project.completed",
                        "agent.completed",
                        "code_quality.failed"
                    ],
                    "description": "Events to send notifications for"
                }
            }
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        # Check webhook URL
        if "webhook_url" not in config:
            return False

        webhook_url = config["webhook_url"]
        if not webhook_url.startswith("https://hooks.slack.com/"):
            return False

        return True
