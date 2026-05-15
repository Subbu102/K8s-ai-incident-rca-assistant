"""
Prompt templates for RCA analysis.
"""

from typing import Dict, Any


class PromptTemplate:
    """Prompt templates for various RCA tasks."""
    
    @staticmethod
    def root_cause_analysis_prompt(pod_name: str, error_message: str, logs: str, context: str) -> str:
        """Create a prompt for root cause analysis."""
        return f"""
## Kubernetes Incident Root Cause Analysis

### Incident Details:
- Pod: {pod_name}
- Error: {error_message}

### Logs:
```
{logs[-500:] if len(logs) > 500 else logs}
```

### Additional Context:
{context}

### Analysis Task:
Based on the above information, provide a comprehensive root cause analysis including:

1. **Root Cause**: The primary reason for the incident
2. **Contributing Factors**: Secondary factors that contributed
3. **Severity Assessment**: Impact level of the incident
4. **Recommendations**: Specific steps to resolve and prevent recurrence

Format your response as a structured analysis."""
    
    @staticmethod
    def troubleshooting_prompt(symptoms: str, available_data: Dict[str, Any]) -> str:
        """Create a prompt for troubleshooting."""
        return f"""
## Kubernetes Troubleshooting

### Symptoms:
{symptoms}

### Available Data:
{available_data}

### Task:
Provide a step-by-step troubleshooting guide to diagnose and resolve this issue.
Include:
1. Diagnostic commands to run
2. Expected vs actual behavior
3. Potential solutions ranked by likelihood
4. When to escalate"""
    
    @staticmethod
    def recommendation_prompt(issue: str, patterns: Dict[str, Any]) -> str:
        """Create a prompt for generating recommendations."""
        return f"""
## Remediation Recommendations

### Identified Issue:
{issue}

### Patterns Detected:
{patterns}

### Task:
Provide actionable recommendations to:
1. Resolve the immediate issue
2. Prevent similar issues in the future
3. Improve system resilience

Be specific with configuration changes and code modifications."""
    
    @staticmethod
    def comparison_prompt(current_state: Dict[str, Any], expected_state: Dict[str, Any]) -> str:
        """Create a prompt for comparing states."""
        return f"""
## Configuration Comparison

### Current State:
{current_state}

### Expected State:
{expected_state}

### Task:
Identify differences and explain how they contribute to the incident."""
