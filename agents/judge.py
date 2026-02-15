"""Judge Agent - Quality Assurance & Feedback Loop

Judge validates published content and provides feedback:
1. Monitors published articles
2. Collects user feedback & metrics
3. Identifies issues and improvement areas
4. Updates brand rules based on patterns

Model: GPT-4o-mini (lightweight evaluation)
Typical Response Time: 3-4 seconds
Success Rate Target: >95%
"""

from typing import Any, Dict
from base_agent import BaseAgent, AgentContext


class JudgeAgent(BaseAgent):
    """Judge evaluates published content quality"""

    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Judge workflow:
        1. Review published article
        2. Check for brand compliance
        3. Analyze user feedback metrics
        4. Score quality (1-10)
        5. Recommend: APPROVED, NEEDS_REVISION, REJECT
        
        Args:
            input_data: {
                "article_id": str,
                "title": str,
                "content": str,
                "published_at": str,
                "user_feedback": dict
            }
            
        Returns:
            {
                "article_id": str,
                "quality_score": float,
                "brand_compliance": bool,
                "user_sentiment": str,
                "recommendation": "APPROVED|NEEDS_REVISION|REJECT",
                "feedback_patterns": [str]
            }
        """
        article_id = input_data.get("article_id", "")
        title = input_data.get("title", "")
        content = input_data.get("content", "")
        published_at = input_data.get("published_at", "")
        
        try:
            # Evaluate article quality and compliance using GPT-4o-mini
            system_prompt = """You are a quality assurance editor reviewing published articles.
Evaluate articles based on:
- Grammar & Spelling: Is writing error-free?
- Brand Voice: Does it match our style guide?
- Accuracy: Are facts verifiable?
- Tone Alignment: Is tone appropriate for our brand?
- Engagement: Is it compelling and readable?

Respond with ONLY JSON: {
  "quality_score": <1-10>,
  "brand_compliant": <true/false>,
  "issues": [<list of issues>],
  "recommendation": "<APPROVED|NEEDS_REVISION|REJECT>"
}"""

            user_message = f"""Article ID: {article_id}
Title: {title}
Published: {published_at}

Content:
{content[:2000]}...

Review this article for quality and brand compliance."""

            response = await self._call_openai(
                model_deployment="gpt-4o-mini",
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.4,
                max_tokens=300
            )
            
            # Parse response
            import json as json_lib
            try:
                result_json = json_lib.loads(response)
                quality_score = float(result_json.get("quality_score", 5.0))
                brand_compliant = bool(result_json.get("brand_compliant", False))
                feedback_patterns = result_json.get("issues", [])
                recommendation = result_json.get("recommendation", "NEEDS_REVISION")
            except:
                quality_score = 5.0
                brand_compliant = False
                feedback_patterns = ["Unable to parse evaluation"]
                recommendation = "NEEDS_REVISION"

            return {
                "agent": "judge",
                "request_id": context.request_id,
                "article_id": article_id,
                "quality_score": quality_score,
                "brand_compliance": brand_compliant,
                "recommendation": recommendation,
                "feedback_patterns": feedback_patterns,
                "next_agent": None  # Judge is end of pipeline
            }

        except Exception as e:
            self.logger.error(f"Judge processing failed: {str(e)}")
            raise


# Entrypoint for Foundry
async def judge_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler invoked by Azure Foundry Agent Service"""
    agent = JudgeAgent(agent_id="judge")
    context = AgentContext(agent_id="judge")
    return await agent.execute(context, input_data)
