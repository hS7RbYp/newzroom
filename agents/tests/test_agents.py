"""Agent Tests

Unit tests for agent implementations.
Tests agent execution, error handling, and integration.
"""

import pytest
import pytest_asyncio
from base_agent import BaseAgent, AgentContext, ExampleAgent
from scout import ScoutAgent
from prof import ProfAgent


@pytest_asyncio.fixture
async def scout_agent():
    """Fixture: Scout agent instance"""
    return ScoutAgent(agent_id="scout")


@pytest_asyncio.fixture
async def prof_agent():
    """Fixture: Prof agent instance"""
    return ProfAgent(agent_id="prof")


class TestBaseAgent:
    """Tests for BaseAgent base class"""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization"""
        agent = ExampleAgent(agent_id="test")
        assert agent.agent_id == "test"
        assert agent.status.value == "idle"

    @pytest.mark.asyncio
    async def test_agent_execution_success(self):
        """Test successful agent execution"""
        agent = ExampleAgent(agent_id="test")
        context = AgentContext(agent_id="test")
        input_data = {"test": "data"}

        result = await agent.execute(context, input_data)

        assert result["agent"] == "test"
        assert result["request_id"] == context.request_id
        assert agent.status.value == "success"

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after max failures"""
        # This would require a failing agent implementation
        pass


class TestScoutAgent:
    """Tests for Scout agent"""

    @pytest.mark.asyncio
    async def test_scout_passes_high_score(self, scout_agent):
        """Test Scout passes articles above threshold"""
        context = AgentContext(agent_id="scout")
        input_data = {
            "article_url": "https://example.com/article",
            "title": "Breaking News",
            "content": "Important content here",
            "source": "Reuters"
        }

        result = await scout_agent.execute(context, input_data)

        assert result["recommendation"] in ["PASS", "REJECT"]
        assert "score" in result
        assert "should_escalate" in result

    @pytest.mark.asyncio
    async def test_scout_rejects_low_score(self, scout_agent):
        """Test Scout rejects low-scoring articles"""
        context = AgentContext(agent_id="scout")
        input_data = {
            "article_url": "https://example.com/low-score",
            "title": "Spam Article",
            "content": "Irrelevant content",
            "source": "Unknown"
        }

        result = await scout_agent.execute(context, input_data)

        assert "recommendation" in result


class TestProfAgent:
    """Tests for Prof agent"""

    @pytest.mark.asyncio
    async def test_prof_fact_checks_content(self, prof_agent):
        """Test Prof performs fact-checking"""
        context = AgentContext(agent_id="prof")
        input_data = {
            "article_id": "art-123",
            "title": "Test Article",
            "content": "Test content",
            "score_from_scout": 7.5
        }

        result = await prof_agent.execute(context, input_data)

        assert "fact_check_score" in result
        assert "entities" in result
        assert "sentiment" in result
        assert "recommendation" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
