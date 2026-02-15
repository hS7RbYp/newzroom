"""
Base Agent Class

Abstract base class for all Azure Autonomous Newsroom agents.
All agents (Scout, Prof, Scribe, Judge, Pixel, Ops) inherit from this.

Architecture:
- Azure Foundry Agent Service orchestration
- Async/await execution model
- Structured logging with JSON
- Error handling with circuit breaker
- Memory management (Immediate/Working/Long-term)
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from opentelemetry import trace, metrics
from opentelemetry.trace import Tracer
from opentelemetry.metrics import Meter


class AgentStatus(str, Enum):
    """Agent lifecycle status"""
    IDLE = "idle"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CIRCUIT_OPEN = "circuit_open"


class AgentContext(BaseModel):
    """Execution context passed between agents"""
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    article_id: Optional[str] = None
    parent_agent: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class BaseAgent(ABC):
    """
    Abstract base agent for Autonomous Newsroom.
    
    Attributes:
        agent_id: Unique identifier (scout, prof, scribe, judge, pixel, ops)
        logger: Structured logger (JSON)
        tracer: OpenTelemetry tracer
        meter: OpenTelemetry metrics
        circuit_breaker: Failure threshold before opening circuit
    """

    def __init__(
        self,
        agent_id: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique agent identifier
            config: Configuration dictionary with:
                - max_failures: Circuit breaker failure threshold
                - timeout: Request timeout in seconds
                - retry_count: Number of retries on failure
                - log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.failure_count = 0
        self.max_failures = self.config.get("max_failures", 5)

        # Setup logging
        self.logger = self._setup_logger()

        # Setup observability
        self.tracer: Tracer = trace.get_tracer(__name__)
        self.meter: Meter = metrics.get_meter(__name__)

        # Circuit breaker state
        self.circuit_open = False

        self.logger.info(
            f"Initialized agent",
            extra={"agent_id": self.agent_id, "config": self.config}
        )

    def _setup_logger(self) -> logging.Logger:
        """Setup structured JSON logger"""
        logger = logging.getLogger(self.agent_id)
        logger.setLevel(self.config.get("log_level", "INFO"))

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            json.dumps({
                "timestamp": "%(asctime)s",
                "agent": self.agent_id,
                "level": "%(levelname)s",
                "message": "%(message)s"
            })
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main execution method. Callable by Foundry orchestrator.
        
        Args:
            context: Execution context with correlation IDs
            input_data: Input payload from previous agent or trigger
            
        Returns:
            Output payload for next agent or consumer
        """
        try:
            # Check circuit breaker
            if self.circuit_open:
                self.status = AgentStatus.CIRCUIT_OPEN
                self.logger.warning(
                    "Circuit breaker is OPEN",
                    extra={"request_id": context.request_id}
                )
                raise Exception(f"Agent {self.agent_id} circuit is open")

            # Update context
            context.agent_id = self.agent_id
            self.status = AgentStatus.PROCESSING

            # Span for tracing
            with self.tracer.start_as_current_span(f"execute_{self.agent_id}") as span:
                span.set_attribute("request_id", context.request_id)
                span.set_attribute("agent_id", self.agent_id)

                # Execute agent logic
                result = await self._execute_agent(context, input_data)

                # Track success
                self.failure_count = 0
                self.status = AgentStatus.SUCCESS

                self.logger.info(
                    f"{self.agent_id} execution successful",
                    extra={
                        "request_id": context.request_id,
                        "status": "success"
                    }
                )

                return result

        except Exception as e:
            # Handle failure
            self.failure_count += 1
            self.status = AgentStatus.FAILED

            self.logger.error(
                f"{self.agent_id} execution failed",
                extra={
                    "request_id": context.request_id,
                    "error": str(e),
                    "failure_count": self.failure_count
                }
            )

            # Open circuit if threshold exceeded
            if self.failure_count >= self.max_failures:
                self.circuit_open = True
                self.logger.critical(
                    "Circuit breaker OPENED",
                    extra={"request_id": context.request_id}
                )

            raise

    @abstractmethod
    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Agent-specific implementation. Must be overridden by subclasses.
        
        Args:
            context: Execution context
            input_data: Input data
            
        Returns:
            Output data
        """
        pass

    def reset_circuit_breaker(self) -> None:
        """Reset circuit breaker (called after recovery)"""
        self.circuit_open = False
        self.failure_count = 0
        self.logger.info(f"Circuit breaker reset for {self.agent_id}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint. Can be called by orchestrator.
        
        Returns:
            Health status
        """
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "circuit_open": self.circuit_open,
            "failure_count": self.failure_count,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# EXAMPLE AGENT (template for Scout, Prof, etc.)
# ============================================================================

class ExampleAgent(BaseAgent):
    """Example agent demonstrating base class usage"""

    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Example implementation.
        
        Process article, perform analysis, return structured output.
        """
        article = input_data.get("article", {})

        # Simulate processing
        await asyncio.sleep(0.1)

        return {
            "agent": self.agent_id,
            "request_id": context.request_id,
            "article_id": article.get("id"),
            "result": "Processing complete",
            "timestamp": datetime.utcnow().isoformat()
        }
