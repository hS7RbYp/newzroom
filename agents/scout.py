"""Scout Agent - Article Discovery & Initial Processing

Scout is the first agent in the pipeline:
1. Monitors news feeds and social media
2. Identifies newsworthy articles
3. Passes high-scoring articles to Prof for deep analysis

Model: GPT-4o-mini (cost optimized)
Typical Response Time: 2-3 seconds
Success Rate Target: >95%
"""

from typing import Any, Dict
from base_agent import BaseAgent, AgentContext


class ScoutAgent(BaseAgent):
    """Scout discovers and analyzes incoming articles"""

    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Scout workflow:
        1. Extract article content
        2. Score newsworthiness (1-10)
        3. Return if score > threshold (default: 6)
        
        Args:
            input_data: {
                "article_url": str,
                "title": str,
                "content": str,
                "source": str
            }
            
        Returns:
            {
                "article_id": str,
                "score": float,
                "recommendation": "PASS|REJECT",
                "reasoning": str
            }
        """
        article_url = input_data.get("article_url", "")
        title = input_data.get("title", "")
        content = input_data.get("content", "")

        try:
            # Score article newsworthiness using GPT-4o-mini
            system_prompt = """You are a news editor evaluating article quality.
Score articles 1-10 based on:
- Timeliness: How current/urgent is the topic?
- Relevance: Is it relevant to our audience?
- Credibility: Is the source trustworthy?
- Engagement: Will this interest readers?
- Uniqueness: Is this a unique angle?

Respond with ONLY a JSON object: {"score": <1-10>, "reason": "<brief reason>"}"""

            user_message = f"""Article Title: {title}
URL: {article_url}

Content Preview:
{content[:1000]}...

Score this article and provide reasoning."""

            response = await self._call_openai(
                model_deployment="gpt-4o-mini",
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.5,
                max_tokens=200
            )
            
            # Parse score from response
            import json as json_lib
            try:
                result_json = json_lib.loads(response)
                score = float(result_json.get("score", 5.0))
                reasoning = result_json.get("reason", "")
            except:
                # Fallback if JSON parsing fails
                score = 5.0
                reasoning = response[:100]

            is_relevant = score > 6.0

            return {
                "agent": "scout",
                "request_id": context.request_id,
                "article_id": context.article_id,
                "article_url": article_url,
                "score": score,
                "reasoning": reasoning,
                "recommendation": "PASS" if is_relevant else "REJECT",
                "should_escalate": is_relevant,
                "next_agent": "prof" if is_relevant else None
            }

        except Exception as e:
            self.logger.error(f"Scout processing failed: {str(e)}")
            raise


# Entrypoint for Foundry
async def scout_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler invoked by Azure Foundry Agent Service"""
    agent = ScoutAgent(agent_id="scout")
    context = AgentContext(agent_id="scout")
    return await agent.execute(context, input_data)
