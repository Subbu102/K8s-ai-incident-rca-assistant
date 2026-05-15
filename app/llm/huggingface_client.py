"""
HuggingFace LLM client for generating RCA analysis.
"""

import logging
from typing import Optional, Dict, Any
import json

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

logger = logging.getLogger(__name__)


class HuggingFaceClient:
    """Client for HuggingFace models."""
    
    def __init__(self, model_name: str = "gpt2", task: str = "text-generation"):
        """
        Initialize HuggingFace client.
        
        Args:
            model_name: Model name from HuggingFace hub
            task: Task type (text-generation, question-answering, etc.)
        """
        if pipeline is None:
            raise ImportError("transformers package required")
        
        try:
            self.model_name = model_name
            self.task = task
            self.pipeline = pipeline(task=task, model=model_name, device=-1)  # CPU
            logger.info(f"Loaded HuggingFace model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model {model_name}: {str(e)}")
            # Fall back to mock implementation for demo
            self.pipeline = None
    
    def generate(self, prompt: str, max_length: int = 200, temperature: float = 0.7) -> str:
        """
        Generate text using the model.
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            if self.pipeline is None:
                return self._mock_generate(prompt)
            
            outputs = self.pipeline(
                prompt,
                max_length=max_length,
                temperature=temperature,
                num_return_sequences=1,
                do_sample=True
            )
            
            return outputs[0]["generated_text"].replace(prompt, "").strip()
            
        except Exception as e:
            logger.error(f"Failed to generate text: {str(e)}")
            return self._mock_generate(prompt)
    
    def analyze_error(self, error_message: str, context: str) -> str:
        """
        Analyze an error message and provide insights.
        
        Args:
            error_message: The error message
            context: Additional context
            
        Returns:
            Analysis of the error
        """
        prompt = f"""Analyze the following Kubernetes error and provide insights:

Error: {error_message}
Context: {context}

Provide:
1. Root cause
2. Contributing factors
3. Recommended solution"""
        
        return self.generate(prompt, max_length=300)
    
    def suggest_fixes(self, problem_description: str) -> List[str]:
        """
        Suggest fixes for a problem.
        
        Args:
            problem_description: Description of the problem
            
        Returns:
            List of suggested fixes
        """
        prompt = f"""For the Kubernetes issue: {problem_description}
Suggest 3 actionable fixes. Format as numbered list."""
        
        response = self.generate(prompt, max_length=200)
        
        # Parse response into list
        fixes = [fix.strip() for fix in response.split('\n') if fix.strip()]
        return fixes[:3]
    
    @staticmethod
    def _mock_generate(prompt: str) -> str:
        """Mock generation for demo purposes."""
        mock_responses = {
            "OOMKilled": "The pod was terminated due to out-of-memory condition. Increase memory limits in the pod specification.",
            "CrashLoopBackOff": "The container is crashing repeatedly. Review application logs and fix the underlying issue.",
            "ImagePullBackOff": "Failed to pull the container image. Check image name, registry, and credentials.",
            "Pending": "Pod is waiting for resources. Check node capacity and resource requests/limits.",
            "Connection": "Network connectivity issue detected. Verify service endpoints and network policies.",
        }
        
        for key, response in mock_responses.items():
            if key.lower() in prompt.lower():
                return response
        
        return "Unable to determine root cause. Please review logs and consult documentation."
