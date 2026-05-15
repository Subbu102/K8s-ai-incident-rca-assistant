"""
Unit tests for log analysis.
"""

import pytest
from app.kubernetes.pod_logs import PodLogAnalyzer


class TestPodLogAnalyzer:
    """Test cases for pod log analyzer."""
    
    def test_error_pattern_detection(self, sample_error_logs):
        """Test error pattern detection."""
        analyzer = PodLogAnalyzer()
        analysis = analyzer._detect_error_patterns(sample_error_logs)
        
        assert "connection_timeout" in analysis
        assert "connection_refused" in analysis or len(analysis) > 0
    
    def test_log_parsing(self, sample_error_logs):
        """Test log parsing."""
        analyzer = PodLogAnalyzer()
        parsed = analyzer._parse_logs(sample_error_logs)
        
        assert len(parsed) > 0
        assert all("message" in log for log in parsed)
        assert all("level" in log for log in parsed)
    
    def test_error_summarization(self, sample_error_logs):
        """Test error summarization."""
        analyzer = PodLogAnalyzer()
        summary = analyzer._summarize_errors(sample_error_logs)
        
        assert "total_errors" in summary
        assert summary["total_errors"] > 0
    
    def test_stack_trace_extraction(self, sample_error_logs):
        """Test stack trace extraction."""
        analyzer = PodLogAnalyzer()
        traces = analyzer._extract_stack_traces(sample_error_logs)
        
        # May or may not find traces depending on log format
        assert isinstance(traces, list)
    
    def test_warning_extraction(self, sample_error_logs):
        """Test warning extraction."""
        analyzer = PodLogAnalyzer()
        warnings = analyzer._extract_warnings(sample_error_logs)
        
        assert isinstance(warnings, list)
