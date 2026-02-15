# Azure Autonomous Newsroom - Agents

Python implementation of the six-agent newsroom system orchestrated by Azure Foundry Agent Service.

## 📋 Agent Overview

| Agent | Purpose | Model | Priority | Timeout |
|-------|---------|-------|----------|---------|
| **Scout** | Discover & score articles | GPT-4o-mini | P0 | 10s |
| **Prof** | Deep analysis & fact-check | GPT-4o | P0 | 15s |
| **Scribe** | Format & optimize | GPT-4o | P0 | 12s |
| **Judge** | QA & feedback loop | GPT-4o-mini | P1 | 10s |
| **Pixel** | Generate images | DALL-E 3 | P2 | 30s |
| **Ops** | Publish & operations | N/A | P1 | 10s |

## 🚀 Quick Start

### Prerequisites
```bash
python 3.11+
pip or uv
Azure subscription
```

### Setup Development Environment

```bash
# Clone and navigate
git clone <repository>
cd newsroom/agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy and configure .env
cp ../.env.example .env
# Edit .env with your Azure credentials
```

### Run Tests

```bash
# All tests
pytest tests/ -v --cov=agents

# Specific agent tests
pytest tests/test_agents.py::TestScoutAgent -v

# With coverage report
pytest tests/ --cov=agents --cov-report=html
```

### Run Locally

```bash
# Start the agent system
python -m agents

# Or run individual agent for testing
python agents/scout.py
```

## 📁 Structure

```
agents/
├── __init__.py                 # Package entry
├── __main__.py                 # Application startup
├── base_agent.py               # Abstract base class
├── config.py                   # Configuration management
├── scout.py                    # Scout agent
├── prof.py                     # Prof agent
├── scribe.py                   # Scribe agent
├── judge.py                    # Judge agent
├── pixel.py                    # Pixel agent
├── ops.py                      # Ops agent
├── tests/
│   ├── __init__.py
│   ├── test_agents.py         # Unit tests
│   ├── test_integration.py    # Integration tests (TODO)
│   └── fixtures/              # Test data
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
└── README.md                   # This file
```

## 🔧 Agent Development

### Creating a New Agent

```python
from base_agent import BaseAgent, AgentContext
from typing import Any, Dict

class MyAgent(BaseAgent):
    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Your agent logic here.
        
        Args:
            context: Request context with correlation IDs
            input_data: Input from previous agent or trigger
            
        Returns:
            Output for next agent
        """
        # Process input
        result = await self._do_work(input_data)
        
        # Log
        self.logger.info(f"Processing complete", extra={
            "request_id": context.request_id,
            "result": result
        })
        
        return result
    
    async def _do_work(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass

# Entrypoint for Foundry
async def my_agent_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    agent = MyAgent(agent_id="my-agent")
    context = AgentContext(agent_id="my-agent")
    return await agent.execute(context, input_data)
```

### Base Agent Features

- **Async execution**: All agents support async/await
- **Circuit breaker**: Automatic failure handling
- **Error handling**: Structured error logging
- **Observability**: OpenTelemetry tracing & metrics
- **Context passing**: Correlation IDs across agents

## 🔌 Azure Integration

### OpenAI Calls

```python
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=config.openai.api_key,
    api_version=config.openai.api_version,
    azure_endpoint=config.openai.endpoint
)

response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "..."}]
)
```

### Cosmos DB Access

```python
from azure.cosmos import CosmosClient

client = CosmosClient(
    url=config.cosmos_db.endpoint,
    credential=config.cosmos_db.key
)

database = client.get_database_client("articles")
container = database.get_container_client("articles")

# Read
item = container.read_item(item="article-id", partition_key="publisher-id")

# Write
container.upsert_item({"id": "article-id", ...})
```

### AI Search

```python
from azure.search.documents import SearchClient

search_client = SearchClient(
    endpoint=config.search.endpoint,
    index_name="brand-rules",
    credential=config.search.key
)

results = search_client.search("brand rules query")
```

## 📊 Monitoring & Debugging

### View Agent Logs

```bash
# Scout logs
grep "scout" logs/*.log

# With timestamp
tail -f logs/agents.log | grep scout
```

### Enable Debug Logging

In `.env`:
```
LOG_LEVEL=DEBUG
```

### Circuit Breaker Status

```python
agent = ScoutAgent("scout")
status = await agent.health_check()
print(status)
# Output: {"agent_id": "scout", "status": "idle", "circuit_open": false, ...}
```

## 🧪 Testing

### Unit Tests

Test individual agent logic without Azure dependencies:

```bash
pytest tests/test_agents.py::TestScoutAgent::test_scout_passes_high_score -v
```

### Integration Tests (Coming)

Test end-to-end agent pipeline with real Azure services.

### Mocking Azure Services

```python
from unittest.mock import patch, AsyncMock

@patch('agents.scout.OpenAI')
async def test_scout_with_mock(mock_openai):
    mock_openai.return_value.chat.completions.create = AsyncMock(
        return_value={"choices": [{"message": {"content": "..."}}]}
    )
    
    agent = ScoutAgent("scout")
    result = await agent.execute(...)
    assert result["score"] > 0
```

## 🚨 Troubleshooting

### Agent Not Responding

```bash
# Check health
curl http://localhost:8000/health/scout

# Check logs
tail -f logs/scout.log

# Restart agent
python -m agents
```

### Azure Credential Issues

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription <subscription-id>

# Verify credentials
az account show
```

### Circuit Breaker Open

The circuit breaker opens after 5 consecutive failures. It can be reset:

```python
agent = ScoutAgent("scout")
agent.reset_circuit_breaker()
```

## 📝 Code Style

All code follows:
- **Black** formatting: `black agents/`
- **Pylint** linting: `pylint agents/`
- **MyPy** type checking: `mypy agents/`
- **PEP 8** style guide

Run all checks:
```bash
black agents/ && pylint agents/ && mypy agents/ && pytest agents/tests/
```

## 🔐 Security

- Credentials stored in Key Vault
- Managed identities for Azure service auth
- API keys never in code (use .env)
- Secrets marked `sensitive=true` in Pydantic

## 📚 Related Documentation

- [System Design v3.0](/docs/SYSTEM_DESIGN_v3.0.md) - Architecture overview
- [Agent Mesh Communication](/docs/AGENT_MESH_COMMUNICATION.md) - Agent protocols
- [Memory Architecture](/docs/MEMORY_ARCHITECTURE.md) - Storage & persistence
- [Implementation Roadmap](/docs/IMPLEMENTATION_ROADMAP.md) - Development plan

## 🤝 Contributing

See [CONTRIBUTING.md](/CONTRIBUTING.md) for guidelines.

Quick checklist:
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Linting passes: `pylint agents/`
- [ ] Types check: `mypy agents/`
- [ ] Code formatted: `black agents/`

## 📞 Support

- **Issues**: Create GitHub issue with `[AGENT]` tag
- **Questions**: Ask in #newsroom-dev Slack
- **Architecture**: See [System Design](/docs/SYSTEM_DESIGN_v3.0.md)

---

**Status**: Phase 0 (In Development)  
**Last Updated**: 2026-02-14  
**Version**: 0.1.0
