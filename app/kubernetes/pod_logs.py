"""
Module for comprehensive pod log analysis.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .kube_client import KubernetesClient

logger = logging.getLogger(__name__)


class PodLogAnalyzer:
    """Analyzer for pod logs and error patterns."""
    
    # Common error patterns
    ERROR_PATTERNS = {
        "out_of_memory": r"(OOMKilled|Out of memory|OOM|insufficient memory)",
        "cpu_throttling": r"(CPU throttling|cpu_throttling)",
        "connection_timeout": r"(Connection timeout|connection refused|connect timed out)",
        "disk_space": r"(No space left|disk full|ENOSPC)",
        "permission_denied": r"(Permission denied|EACCES)",
        "segmentation_fault": r"(Segmentation fault|SIGSEGV)",
        "signal_9": r"(Signal 9|SIGKILL)",
        "exit_code_1": r"(Exit code 1|exit status 1)",
        "panic": r"(panic:|fatal error)",
        "exception": r"(Exception|Error:.*at)",
    }
    
    def __init__(self, kube_client: Optional[KubernetesClient] = None):
        """
        Initialize log analyzer.
        
        Args:
            kube_client: Kubernetes client instance
        """
        self.kube_client = kube_client or KubernetesClient()
    
    def analyze_pod_logs(
        self,
        pod_name: str,
        namespace: str = "default",
        lines: int = 200
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of pod logs.
        
        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace
            lines: Number of lines to analyze
            
        Returns:
            Analysis results including errors, warnings, and patterns
        """
        try:
            # Get logs
            logs = self.kube_client.get_pod_logs(
                pod_name=pod_name,
                namespace=namespace,
                lines=lines
            )
            
            # Also get previous logs if available
            previous_logs = ""
            try:
                previous_logs = self.kube_client.get_pod_logs(
                    pod_name=pod_name,
                    namespace=namespace,
                    lines=lines,
                    previous=True
                )
            except Exception:
                pass
            
            # Analyze logs
            analysis = {
                "current_logs": self._parse_logs(logs),
                "previous_logs": self._parse_logs(previous_logs) if previous_logs else None,
                "error_patterns": self._detect_error_patterns(logs),
                "error_summary": self._summarize_errors(logs),
                "warnings": self._extract_warnings(logs),
                "key_timestamps": self._extract_key_timestamps(logs),
                "stack_traces": self._extract_stack_traces(logs)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze logs for pod {pod_name}: {str(e)}")
            raise
    
    def _parse_logs(self, logs: str) -> List[Dict[str, Any]]:
        """Parse logs into structured format."""
        lines = logs.split('\n') if logs else []
        
        parsed = []
        for line in lines:
            if not line.strip():
                continue
            
            parsed.append({
                "timestamp": self._extract_timestamp(line),
                "level": self._determine_log_level(line),
                "message": line.strip(),
                "is_error": self._is_error_line(line)
            })
        
        return parsed
    
    def _detect_error_patterns(self, logs: str) -> Dict[str, List[str]]:
        """Detect known error patterns in logs."""
        patterns = {}
        
        for pattern_name, pattern in self.ERROR_PATTERNS.items():
            matches = re.findall(pattern, logs, re.IGNORECASE)
            if matches:
                patterns[pattern_name] = matches
        
        return patterns
    
    def _summarize_errors(self, logs: str) -> Dict[str, Any]:
        """Create error summary."""
        lines = logs.split('\n')
        error_lines = [l for l in lines if self._is_error_line(l)]
        
        return {
            "total_errors": len(error_lines),
            "unique_errors": len(set(error_lines)),
            "most_common": self._get_most_common_error(error_lines),
            "error_frequency": self._calculate_error_frequency(error_lines)
        }
    
    def _extract_warnings(self, logs: str) -> List[str]:
        """Extract warning messages."""
        lines = logs.split('\n')
        warnings = [
            l.strip() for l in lines
            if 'warning' in l.lower() or 'warn' in l.lower()
        ]
        return warnings[:10]  # Return top 10
    
    def _extract_key_timestamps(self, logs: str) -> List[str]:
        """Extract important timestamps from logs."""
        timestamps = set()
        
        # Look for common timestamp patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO format
            r'\d{2}/\w+/\d{4}\s+\d{2}:\d{2}:\d{2}',  # Apache format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, logs)
            timestamps.update(matches)
        
        return sorted(list(timestamps))
    
    def _extract_stack_traces(self, logs: str) -> List[str]:
        """Extract stack traces from logs."""
        stack_traces = []
        current_trace = []
        in_trace = False
        
        for line in logs.split('\n'):
            if 'traceback' in line.lower() or 'stack trace' in line.lower():
                in_trace = True
                current_trace = [line]
            elif in_trace:
                if line.strip() and (line.startswith('\t') or line.startswith(' ') or 'at ' in line):
                    current_trace.append(line)
                elif current_trace:
                    stack_traces.append('\n'.join(current_trace))
                    current_trace = []
                    in_trace = False
        
        if current_trace:
            stack_traces.append('\n'.join(current_trace))
        
        return stack_traces[:5]  # Return top 5
    
    @staticmethod
    def _extract_timestamp(line: str) -> Optional[str]:
        """Extract timestamp from log line."""
        patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{2}/\w+/\d{4}\s+\d{2}:\d{2}:\d{2}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group()
        return None
    
    @staticmethod
    def _determine_log_level(line: str) -> str:
        """Determine log level from line."""
        line_lower = line.lower()
        
        if 'error' in line_lower or 'exception' in line_lower:
            return 'ERROR'
        elif 'warning' in line_lower or 'warn' in line_lower:
            return 'WARNING'
        elif 'info' in line_lower or 'information' in line_lower:
            return 'INFO'
        elif 'debug' in line_lower:
            return 'DEBUG'
        
        return 'UNKNOWN'
    
    @staticmethod
    def _is_error_line(line: str) -> bool:
        """Check if line contains error information."""
        error_keywords = ['error', 'exception', 'failed', 'failure', 'panic', 'fatal']
        return any(keyword in line.lower() for keyword in error_keywords)
    
    @staticmethod
    def _get_most_common_error(error_lines: List[str]) -> Optional[str]:
        """Get most common error message."""
        if not error_lines:
            return None
        
        from collections import Counter
        counter = Counter(error_lines)
        return counter.most_common(1)[0][0] if counter else None
    
    @staticmethod
    def _calculate_error_frequency(error_lines: List[str]) -> Dict[str, int]:
        """Calculate error frequency."""
        if not error_lines:
            return {}
        
        from collections import Counter
        return dict(Counter(error_lines).most_common(5))
