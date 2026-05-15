"""
Slack notifications for incidents.
"""

import logging
import json
from typing import List, Optional

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    WebClient = None
    SlackApiError = None

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Send notifications to Slack."""
    
    def __init__(self, webhook_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize Slack notifier.
        
        Args:
            webhook_url: Slack incoming webhook URL
            token: Slack bot token for sending messages
        """
        self.webhook_url = webhook_url
        self.token = token
        self.client = None
        
        if token and WebClient is not None:
            try:
                self.client = WebClient(token=token)
                logger.info("Slack client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Slack client: {str(e)}")
    
    async def notify_incident_created(
        self,
        incident_id: str,
        pod_name: str,
        namespace: str,
        error_message: str
    ):
        """
        Notify about incident creation.
        
        Args:
            incident_id: Incident identifier
            pod_name: Name of the affected pod
            namespace: Kubernetes namespace
            error_message: Error description
        """
        message = {
            "text": "🚨 New Kubernetes Incident Created",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New Incident*\n*Pod:* {pod_name}\n*Namespace:* {namespace}\n*Error:* {error_message}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Incident ID: {incident_id}"
                        }
                    ]
                }
            ]
        }
        
        await self._send_message(message)
    
    async def notify_incident_resolved(
        self,
        incident_id: str,
        pod_name: str,
        root_cause: str,
        recommendations: List[str]
    ):
        """
        Notify about incident resolution.
        
        Args:
            incident_id: Incident identifier
            pod_name: Name of the affected pod
            root_cause: Identified root cause
            recommendations: Remediation recommendations
        """
        recommendation_text = "\n".join([f"• {rec}" for rec in recommendations[:3]])
        
        message = {
            "text": "✅ Incident Analysis Complete",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*RCA Analysis Completed*\n*Pod:* {pod_name}\n*Root Cause:* {root_cause}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Recommendations:*\n{recommendation_text}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Incident ID: {incident_id}"
                        }
                    ]
                }
            ]
        }
        
        await self._send_message(message)
    
    async def notify_analysis_failed(self, incident_id: str, error: str):
        """
        Notify about analysis failure.
        
        Args:
            incident_id: Incident identifier
            error: Error message
        """
        message = {
            "text": "❌ Analysis Failed",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Analysis Failed*\n*Error:* {error}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Incident ID: {incident_id}"
                        }
                    ]
                }
            ]
        }
        
        await self._send_message(message)
    
    async def _send_message(self, message: dict):
        """
        Send message to Slack.
        
        Args:
            message: Message payload
        """
        if self.client:
            try:
                self.client.chat_postMessage(
                    channel="#incidents",
                    **message
                )
                logger.info("Slack notification sent")
            except SlackApiError as e:
                logger.error(f"Failed to send Slack message: {str(e)}")
        elif self.webhook_url:
            try:
                import requests
                requests.post(self.webhook_url, json=message)
                logger.info("Slack webhook notification sent")
            except Exception as e:
                logger.error(f"Failed to send webhook: {str(e)}")
        else:
            logger.debug(f"Would send Slack message: {json.dumps(message)}")
