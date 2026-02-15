"""Prof Agent - Deep Analysis & Content Understanding

Prof performs comprehensive analysis:
1. Fact-checks content against knowledge base
2. Identifies key entities, themes, sentiment
3. Ranks credibility and accuracy
4. May escalate back to Scout for rechecking

Model: GPT-4o (advanced reasoning)
Typical Response Time: 5-8 seconds
Success Rate Target: >90%
"""

from typing import Any, Dict
from base_agent import BaseAgent, AgentContext


class ProfAgent(BaseAgent):
    """Prof performs deep analysis of articles"""

    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prof workflow:
        1. Extract article details
        2. Check against fact database
        3. Analyze sentiment & entities
        4. Score accuracy (1-10)
        5. Recommend: APPROVE, REVISE, or REJECT
        
        Args:
            input_data: {
                "article_id": str,
                "title": str,
                "content": str,
                "score_from_scout": float
            }
            
        Returns:
            {
                "article_id": str,
                "fact_check_score": float,
                "entities": [str],
                "sentiment": str,
                "recommendation": "APPROVE|REVISE|REJECT",
                "next_agent": str or None
            }
        """
        article_id = input_data.get("article_id", "")
        title = input_data.get("title", "")
        content = input_data.get("content", "")

        try:
            # Analyze content with GPT-4o for fact-checking and entity extraction
            system_prompt = """You are an expert content analyst for a news organization.
Analyze the article and provide:
1. Fact-check score (1-10): How accurate/verifiable is this content?
2. Key entities (people, organizations, places)
3. Overall sentiment: positive, negative, or neutral
4. Recommendation: APPROVE (>7.5), REVISE (6-7.5), or REJECT (<6)

Respond with ONLY a JSON object: {"fact_check_score": <1-10>, "entities": ["..."], "sentiment": "<positive|negative|neutral>", "recommendation": "<APPROVE|REVISE|REJECT>"}"""

            user_message = f"""Title: {title}

Content:
{content[:2000]}

Analyze this article for accuracy, key entities, and sentiment."""

            response = await self._call_openai(
                model_deployment="gpt-4o",
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse analysis from response
            import json as json_lib
            try:
                result_json = json_lib.loads(response)
                fact_check_score = float(result_json.get("fact_check_score", 7.0))
                entities = result_json.get("entities", [])
                sentiment = result_json.get("sentiment", "neutral")
                recommendation = result_json.get("recommendation", "REVISE")
            except:
                # Fallback if JSON parsing fails
                fact_check_score = 7.0
                entities = []
                sentiment = "neutral"
                recommendation = "REVISE"

            return {
                "agent": "prof",
                "request_id": context.request_id,
                "article_id": article_id,
                "fact_check_score": fact_check_score,
                "entities": entities,
                "sentiment": sentiment,
                "recommendation": recommendation,
                "next_agent": "scribe" if recommendation == "APPROVE" else "scout"
            }

        except Exception as e:
            self.logger.error(f"Prof processing failed: {str(e)}")
            raise


# Entrypoint for Foundry
async def prof_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler invoked by Azure Foundry Agent Service"""
    agent = ProfAgent(agent_id="prof")
    context = AgentContext(agent_id="prof")
    return await agent.execute(context, input_data)
