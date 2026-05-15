"""
Kubernetes client for interacting with K8s clusters.
"""

import logging
from typing import List, Dict, Any, Optional

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


class KubernetesClient:
    """Client for Kubernetes API interactions."""
    
    def __init__(self, in_cluster: bool = False):
        """
        Initialize Kubernetes client.
        
        Args:
            in_cluster: Whether running inside a K8s cluster
        """
        try:
            if in_cluster:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes config")
            else:
                config.load_kube_config()
                logger.info("Loaded local Kubernetes config")
        except Exception as e:
            logger.error(f"Failed to load Kubernetes config: {str(e)}")
            raise
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.custom_api = client.CustomObjectsApi()
    
    def get_pod_logs(
        self,
        pod_name: str,
        namespace: str = "default",
        lines: int = 100,
        previous: bool = False
    ) -> str:
        """
        Get logs from a specific pod.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace
            lines: Number of log lines to retrieve
            previous: Get logs from previous container if crashed
            
        Returns:
            Pod logs as string
        """
        try:
            logs = self.v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=lines,
                previous=previous
            )
            return logs
        except ApiException as e:
            logger.error(f"Failed to get logs for pod {pod_name}: {str(e)}")
            raise
    
    def get_pod(self, pod_name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get detailed pod information.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace
            
        Returns:
            Pod object as dictionary
        """
        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            return self._pod_to_dict(pod)
        except ApiException as e:
            logger.error(f"Failed to get pod {pod_name}: {str(e)}")
            raise
    
    def get_pod_events(self, pod_name: str, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        Get events related to a pod.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace
            
        Returns:
            List of events
        """
        try:
            events = self.v1.list_namespaced_event(namespace=namespace)
            pod_events = [
                self._event_to_dict(e) for e in events.items
                if e.involved_object.name == pod_name
            ]
            return pod_events
        except ApiException as e:
            logger.error(f"Failed to get events for pod {pod_name}: {str(e)}")
            raise
    
    def get_pod_description(self, pod_name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get comprehensive pod description including status and conditions.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace
            
        Returns:
            Detailed pod description
        """
        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            
            description = {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": pod.status.phase,
                "conditions": [
                    {
                        "type": c.type,
                        "status": c.status,
                        "reason": c.reason,
                        "message": c.message
                    }
                    for c in (pod.status.conditions or [])
                ],
                "container_statuses": [
                    {
                        "name": c.name,
                        "ready": c.ready,
                        "restart_count": c.restart_count,
                        "state": self._container_state_to_dict(c.state)
                    }
                    for c in (pod.status.container_statuses or [])
                ],
                "resource_requests": self._get_resource_requests(pod),
                "node_name": pod.spec.node_name
            }
            
            return description
        except ApiException as e:
            logger.error(f"Failed to get pod description for {pod_name}: {str(e)}")
            raise
    
    def get_node_info(self, node_name: str) -> Dict[str, Any]:
        """
        Get information about a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Node information
        """
        try:
            node = self.v1.read_node(name=node_name)
            
            return {
                "name": node.metadata.name,
                "status": node.status.conditions[-1].status if node.status.conditions else "Unknown",
                "allocatable": node.status.allocatable,
                "capacity": node.status.capacity,
                "conditions": [
                    {
                        "type": c.type,
                        "status": c.status,
                        "message": c.message
                    }
                    for c in (node.status.conditions or [])
                ]
            }
        except ApiException as e:
            logger.error(f"Failed to get node info for {node_name}: {str(e)}")
            raise
    
    def list_pods(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List all pods in a namespace.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            List of pod objects
        """
        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            return [self._pod_to_dict(p) for p in pods.items]
        except ApiException as e:
            logger.error(f"Failed to list pods in namespace {namespace}: {str(e)}")
            raise
    
    @staticmethod
    def _pod_to_dict(pod) -> Dict[str, Any]:
        """Convert pod object to dictionary."""
        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "phase": pod.status.phase,
            "restart_count": sum(
                c.restart_count for c in (pod.status.container_statuses or [])
            ),
            "node": pod.spec.node_name
        }
    
    @staticmethod
    def _event_to_dict(event) -> Dict[str, Any]:
        """Convert event object to dictionary."""
        return {
            "type": event.type,
            "reason": event.reason,
            "message": event.message,
            "first_timestamp": event.first_timestamp,
            "last_timestamp": event.last_timestamp,
            "count": event.count
        }
    
    @staticmethod
    def _container_state_to_dict(state) -> Dict[str, Any]:
        """Convert container state to dictionary."""
        if state.running:
            return {"state": "running", "started_at": state.running.started_at}
        elif state.waiting:
            return {"state": "waiting", "reason": state.waiting.reason, "message": state.waiting.message}
        elif state.terminated:
            return {
                "state": "terminated",
                "reason": state.terminated.reason,
                "message": state.terminated.message,
                "exit_code": state.terminated.exit_code
            }
        return {"state": "unknown"}
    
    @staticmethod
    def _get_resource_requests(pod) -> Dict[str, Any]:
        """Extract resource requests from pod."""
        resources = {}
        for container in pod.spec.containers or []:
            if container.resources and container.resources.requests:
                resources[container.name] = container.resources.requests
        return resources
