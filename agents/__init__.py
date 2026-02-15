"""
Agents Package

Azure Autonomous Newsroom agents:
- Scout: Article discovery & initial scoring
- Prof: Deep analysis & fact-checking
- Scribe: Content formatting & SEO
- Judge: Quality assurance & feedback
- Pixel: Image generation
- Ops: Publishing & operations

All agents inherit from BaseAgent and follow async/await patterns.
Orchestrated by Azure Foundry Agent Service.
"""

from base_agent import BaseAgent, AgentContext, AgentStatus
from scout import ScoutAgent
from prof import ProfAgent
from scribe import ScribeAgent
from judge import JudgeAgent
from pixel import PixelAgent
from ops import OpsAgent

__version__ = "0.1.0"
__all__ = [
    "BaseAgent",
    "AgentContext",
    "AgentStatus",
    "ScoutAgent",
    "ProfAgent",
    "ScribeAgent",
    "JudgeAgent",
    "PixelAgent",
    "OpsAgent",
]
