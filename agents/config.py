"""
Agent Configuration

Configuration values for agents:
- Agent parameters (timeouts, retries)
- OpenAI model endpoints
- Azure service credentials
- Foundry orchestration settings
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class AgentConfig(BaseModel):
    """Configuration for individual agents"""
    agent_id: str
    max_failures: int = 5
    timeout_seconds: int = 30
    retry_count: int = 3
    log_level: str = "INFO"


class OpenAIConfig(BaseModel):
    """Azure OpenAI configuration"""
    endpoint: str
    api_key: str
    api_version: str = "2024-08-01-preview"
    gpt4o_deployment: str = "gpt-4o"
    gpt4o_mini_deployment: str = "gpt-4o-mini"
    dalle_deployment: str = "dall-e-3"


class CosmosDbConfig(BaseModel):
    """Cosmos DB configuration"""
    endpoint: str
    key: str
    database_name: str = "articles"
    articles_container: str = "articles"
    agent_state_container: str = "agent-state"


class SearchConfig(BaseModel):
    """Azure AI Search configuration (optional - using Cosmos vector search)"""
    endpoint: Optional[str] = None
    key: Optional[str] = None
    index_name: str = "brand-rules"


class ServiceBusConfig(BaseModel):
    """Azure Service Bus configuration"""
    connection_string: str
    dead_letter_topic: str = "dead-letter-queue"
    agent_events_topic: str = "agent-events"


class FoundryConfig(BaseModel):
    """Azure Foundry Agent Service configuration (optional)"""
    project_connection_string: Optional[str] = None
    agent_configs: dict = {}


class AppConfig(BaseModel):
    """Complete application configuration"""
    openai: OpenAIConfig
    cosmos_db: CosmosDbConfig
    search: SearchConfig
    service_bus: ServiceBusConfig
    foundry: FoundryConfig
    agent_configs: dict


def load_config_from_env() -> AppConfig:
    """Load configuration from environment variables"""
    
    openai_config = OpenAIConfig(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    
    cosmos_config = CosmosDbConfig(
        endpoint=os.getenv("COSMOS_ENDPOINT"),
        key=os.getenv("COSMOS_KEY")
    )
    
    search_config = SearchConfig(
        endpoint=os.getenv("SEARCH_ENDPOINT"),
        key=os.getenv("SEARCH_KEY")
    )
    
    servicebus_config = ServiceBusConfig(
        connection_string=os.getenv("SERVICE_BUS_CONNECTION_STRING")
    )
    
    foundry_config = FoundryConfig(
        project_connection_string=os.getenv("FOUNDRY_PROJECT_CONNECTION_STRING")
    )
    
    agent_configs = {
        "scout": AgentConfig(agent_id="scout", timeout_seconds=10),
        "prof": AgentConfig(agent_id="prof", timeout_seconds=15),
        "scribe": AgentConfig(agent_id="scribe", timeout_seconds=12),
        "judge": AgentConfig(agent_id="judge", timeout_seconds=10),
        "pixel": AgentConfig(agent_id="pixel", timeout_seconds=30),
        "ops": AgentConfig(agent_id="ops", timeout_seconds=10),
    }
    
    return AppConfig(
        openai=openai_config,
        cosmos_db=cosmos_config,
        search=search_config,
        service_bus=servicebus_config,
        foundry=foundry_config,
        agent_configs=agent_configs
    )


# Global config instance
config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or initialize global config"""
    global config
    if config is None:
        config = load_config_from_env()
    return config
