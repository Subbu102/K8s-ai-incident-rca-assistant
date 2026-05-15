"""
Root Cause Analysis Engine combining RAG, LLM, and K8s data.
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.rag.retriever import RAGRetriever
from app.llm.huggingface_client import HuggingFaceClient
from app.kubernetes.kube_client import KubernetesClient
from app.kubernetes.pod_logs import PodLogAnalyzer
from app.llm.prompt_template import PromptTemplate

logger = logging.getLogger(__name__)


class RCAResult:
    """Result of RCA analysis."""
    
    def __init__(
        self,
        root_cause: str,
        contributing_factors: List[str],
        affected_resources: List[str],
        confidence_score: float,
        recommendations: List[str],
        analysis_data: Dict[str, Any]
    ):
        self.root_cause = root_cause
        self.contributing_factors = contributing_factors
        self.affected_resources = affected_resources
        self.confidence_score = confidence_score
        self.recommendations = recommendations
        self.analysis_data = analysis_data
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "root_cause": self.root_cause,
            "contributing_factors": self.contributing_factors,
            "affected_resources": self.affected_resources,
            "confidence_score": self.confidence_score,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
            "analysis_data": self.analysis_data
        }


class RCAEngine:
    """Root Cause Analysis Engine."""
    
    def __init__(
        self,
        rag_retriever: Optional[RAGRetriever] = None,
        llm_client: Optional[HuggingFaceClient] = None,
        kube_client: Optional[KubernetesClient] = None
    ):
        """
        Initialize RCA Engine.
        
        Args:
            rag_retriever: RAG retriever instance
            llm_client: LLM client instance
            kube_client: Kubernetes client instance
        """
        self.rag_retriever = rag_retriever or RAGRetriever()
        self.llm_client = llm_client or HuggingFaceClient()
        self.kube_client = kube_client or KubernetesClient()
        self.log_analyzer = PodLogAnalyzer(kube_client=self.kube_client)
        
        logger.info("RCA Engine initialized")
    
    async def analyze(
        self,
        pod_name: str,
        namespace: str = "default",
        error_message: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> RCAResult:
        """
        Perform comprehensive RCA for a Kubernetes incident.
        
        Args:
            pod_name: Name of the affected pod
            namespace: Kubernetes namespace
            error_message: Error message/symptoms
            context: Additional context
            
        Returns:
            RCAResult with analysis findings
        """
        try:
            logger.info(f"Starting RCA for pod {pod_name} in namespace {namespace}")
            
            # Gather data
            pod_data = await self._gather_pod_data(pod_name, namespace)
            log_analysis = await self._analyze_logs(pod_name, namespace)
            kb_context = await self._retrieve_knowledge(error_message)
            
            # Perform analysis
            analysis_result = await self._perform_analysis(
                pod_name=pod_name,
                pod_data=pod_data,
                log_analysis=log_analysis,
                error_message=error_message,
                kb_context=kb_context,
                context=context
            )
            
            logger.info(f"RCA completed for pod {pod_name}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"RCA analysis failed: {str(e)}")
            raise
    
    async def _gather_pod_data(self, pod_name: str, namespace: str) -> Dict[str, Any]:
        """Gather pod information."""
        try:
            pod_desc = self.kube_client.get_pod_description(pod_name, namespace)
            pod_events = self.kube_client.get_pod_events(pod_name, namespace)
            node_info = None
            
            if pod_desc.get("node_name"):
                node_info = self.kube_client.get_node_info(pod_desc["node_name"])
            
            return {
                "pod_description": pod_desc,
                "events": pod_events,
                "node_info": node_info
            }
        except Exception as e:
            logger.error(f"Failed to gather pod data: {str(e)}")
            return {}
    
    async def _analyze_logs(self, pod_name: str, namespace: str) -> Dict[str, Any]:
        """Analyze pod logs."""
        try:
            return self.log_analyzer.analyze_pod_logs(pod_name, namespace)
        except Exception as e:
            logger.error(f"Failed to analyze logs: {str(e)}")
            return {}
    
    async def _retrieve_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge base documents."""
        try:
            return self.rag_retriever.retrieve(query, k=3)
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge: {str(e)}")
            return []
    
    async def _perform_analysis(
        self,
        pod_name: str,
        pod_data: Dict[str, Any],
        log_analysis: Dict[str, Any],
        error_message: str,
        kb_context: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> RCAResult:
        """Perform RCA analysis using LLM."""
        
        # Build context
        context_str = self._build_analysis_context(
            pod_data=pod_data,
            log_analysis=log_analysis,
            kb_context=kb_context
        )
        
        # Create prompt
        prompt = PromptTemplate.root_cause_analysis_prompt(
            pod_name=pod_name,
            error_message=error_message,
            logs=log_analysis.get("current_logs", [])[:5],
            context=context_str
        )
        
        # Generate analysis using LLM
        analysis_text = self.llm_client.generate(prompt, max_length=500)
        
        # Parse and structure results
        root_cause, factors, recommendations = self._parse_analysis(analysis_text)
        
        # Identify affected resources
        affected_resources = self._identify_affected_resources(pod_data)
        
        # Calculate confidence
        confidence = self._calculate_confidence(log_analysis, pod_data)
        
        return RCAResult(
            root_cause=root_cause,
            contributing_factors=factors,
            affected_resources=affected_resources,
            confidence_score=confidence,
            recommendations=recommendations,
            analysis_data={
                "pod_data": pod_data,
                "log_analysis": log_analysis,
                "kb_context": kb_context,
                "analysis_text": analysis_text
            }
        )
    
    @staticmethod
    def _build_analysis_context(
        pod_data: Dict[str, Any],
        log_analysis: Dict[str, Any],
        kb_context: List[Dict[str, Any]]
    ) -> str:
        """Build context string for analysis."""
        parts = []
        
        if pod_data:
            parts.append(f"Pod Status: {json.dumps(pod_data.get('pod_description', {}), indent=2)}")
        
        if log_analysis:
            parts.append(f"Error Patterns: {json.dumps(log_analysis.get('error_patterns', {}), indent=2)}")
        
        if kb_context:
            parts.append("Related Knowledge:")
            for doc in kb_context:
                parts.append(f"- {doc.get('text', '')}")
        
        return "\n".join(parts)
    
    @staticmethod
    def _parse_analysis(analysis_text: str) -> tuple:
        """Parse analysis text to extract root cause, factors, and recommendations."""
        root_cause = "Unable to determine root cause from analysis"
        factors = []
        recommendations = []
        
        # Simple parsing (can be enhanced with NLP)
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if 'root cause' in line.lower() and i + 1 < len(lines):
                root_cause = lines[i + 1].strip()
            elif 'factor' in line.lower() or 'contributing' in line.lower():
                factors.append(line.strip())
            elif 'recommend' in line.lower() or 'solution' in line.lower():
                recommendations.append(line.strip())
        
        return root_cause, factors[:3], recommendations[:3]
    
    @staticmethod
    def _identify_affected_resources(pod_data: Dict[str, Any]) -> List[str]:
        """Identify affected Kubernetes resources."""
        resources = []
        
        if pod_data.get("pod_description"):
            resources.append(f"Pod: {pod_data['pod_description'].get('name')}")
        
        if pod_data.get("node_info"):
            resources.append(f"Node: {pod_data['node_info'].get('name')}")
        
        return resources
    
    @staticmethod
    def _calculate_confidence(log_analysis: Dict[str, Any], pod_data: Dict[str, Any]) -> float:
        """Calculate confidence score of analysis."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if error patterns found
        if log_analysis.get("error_patterns"):
            confidence += 0.2
        
        # Increase confidence if pod data available
        if pod_data.get("pod_description"):
            confidence += 0.15
        
        # Increase confidence if events found
        if pod_data.get("events"):
            confidence += 0.15
        
        return min(confidence, 1.0)
