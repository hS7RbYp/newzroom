"""Scribe Agent - Content Formatting & Publishing

Scribe formats articles for publishing:
1. Reformats content per brand guidelines
2. Optimizes for readability
3. Generates SEO metadata
4. Prepares for publication

Model: GPT-4o (high-quality output)
Typical Response Time: 4-6 seconds
Success Rate Target: >95%
"""

from typing import Any, Dict
from base_agent import BaseAgent, AgentContext


class ScribeAgent(BaseAgent):
    """Scribe prepares articles for publication"""

    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Scribe workflow:
        1. Format content per brand guidelines
        2. Optimize headlines
        3. Generate SEO metadata
        4. Prepare for CMS
        
        Args:
            input_data: {
                "article_id": str,
                "title": str,
                "content": str,
                "entities": [str],
                "sentiment": str
            }
            
        Returns:
            {
                "article_id": str,
                "formatted_title": str,
                "formatted_content": str,
                "seo_keywords": [str],
                "seo_description": str,
                "ready_for_publication": bool,
                "next_agent": str
            }
        """
        article_id = input_data.get("article_id", "")
        title = input_data.get("title", "")
        content = input_data.get("content", "")

        try:
            # Format content and generate SEO metadata
            system_prompt = """You are an expert content formatter and SEO specialist.
Format the article per brand guidelines and optimize for search:
1. Rewrite headline for clarity and engagement
2. Generate 5 SEO keywords
3. Write a 160-char meta description
4. Identify optimal publication angle

Respond with ONLY a JSON object: {"formatted_title": "...", "seo_keywords": [...], "seo_description": "...", "publication_angle": "..."}"""

            user_message = f"""Original Title: {title}

Content:
{content[:2000]}

Entities: {input_data.get('entities', [])}
Sentiment: {input_data.get('sentiment', 'neutral')}

Format this article with optimized headline, keywords, and SEO metadata."""

            response = await self._call_openai(
                model_deployment="gpt-4o",
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7,
                max_tokens=400
            )
            
            # Parse formatting response
            import json as json_lib
            try:
                result_json = json_lib.loads(response)
                formatted_title = result_json.get("formatted_title", title)
                seo_keywords = result_json.get("seo_keywords", [])
                seo_description = result_json.get("seo_description", "")
            except:
                # Fallback if JSON parsing fails
                formatted_title = title
                seo_keywords = []
                seo_description = ""

            return {
                "agent": "scribe",
                "request_id": context.request_id,
                "article_id": article_id,
                "formatted_title": formatted_title,
                "formatted_content": content,  # Placeholder
                "seo_keywords": seo_keywords,
                "seo_description": seo_description,
                "ready_for_publication": True,
                "next_agent": "pixel"  # Image generation next
            }

        except Exception as e:
            self.logger.error(f"Scribe processing failed: {str(e)}")
            raise


# Entrypoint for Foundry
async def scribe_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler invoked by Azure Foundry Agent Service"""
    agent = ScribeAgent(agent_id="scribe")
    context = AgentContext(agent_id="scribe")
    return await agent.execute(context, input_data)
