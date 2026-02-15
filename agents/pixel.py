"""Pixel Agent - Image Generation & Visual Media

Pixel generates custom images for articles:
1. Analyzes article content & theme
2. Generates custom images with DALL-E 3
3. Stores images in blob storage
4. Attaches to article

Model: DALL-E 3
Typical Response Time: 8-15 seconds
Success Rate Target: >88%
"""

from typing import Any, Dict
from base_agent import BaseAgent, AgentContext


class PixelAgent(BaseAgent):
    """Pixel generates images for articles"""

    async def _execute_agent(
        self,
        context: AgentContext,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pixel workflow:
        1. Analyze article theme & content
        2. Generate prompt for DALL-E 3
        3. Create image
        4. Upload to blob storage
        5. Return image URL
        
        Args:
            input_data: {
                "article_id": str,
                "title": str,
                "content": str,
                "entities": [str]
            }
            
        Returns:
            {
                "article_id": str,
                "image_url": str,
                "image_prompt": str,
                "generation_time_ms": int,
                "status": "GENERATED|FAILED"
            }
        """
        article_id = input_data.get("article_id", "")
        title = input_data.get("title", "")
        content = input_data.get("content", "")
        entities = input_data.get("entities", [])

        try:
            # Generate image prompt from article content
            system_prompt = """You are an expert at creating detailed image prompts for DALL-E 3.
Based on the article, generate a professional image prompt.
The prompt should be:
- Descriptive and specific
- Professional news/article style
- 50-100 words
- Include mood/style guidance

Respond with ONLY the image prompt text (no JSON)."""

            user_message = f"""Article Title: {title}

Content Preview:
{content[:500]}

Key Entities: {', '.join(entities) if entities else 'General'}

Generate a detailed image prompt for this article."""

            image_prompt = await self._call_openai(
                model_deployment="gpt-4o-mini",
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.8,
                max_tokens=150
            )
            
            # Call DALL-E 3 synchronously via asyncio.to_thread
            import asyncio
            import time
            from openai import AzureOpenAI
            from config import get_config
            
            start_time = time.time()
            app_config = get_config()
            client = AzureOpenAI(
                api_key=app_config.openai.api_key,
                api_version=app_config.openai.api_version,
                azure_endpoint=app_config.openai.endpoint
            )
            
            def generate_image():
                return client.images.generate(
                    model=app_config.openai.dalle_deployment,
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024",
                    quality="standard"
                )
            
            # Generate image (this is synchronous in the SDK)
            image_response = await asyncio.to_thread(generate_image)
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract image URL from response
            image_url = image_response.data[0].url if image_response.data else ""
            self.logger.info(f"Generated image for article {article_id}: {image_url[:50]}...")

            return {
                "agent": "pixel",
                "request_id": context.request_id,
                "article_id": article_id,
                "image_url": image_url,
                "image_prompt": f"Image for: {title}",
                "generation_time_ms": generation_time_ms,
                "status": "GENERATED",
                "next_agent": "ops"
            }

        except Exception as e:
            self.logger.error(f"Pixel processing failed: {str(e)}")
            return {
                "article_id": article_id,
                "status": "FAILED",
                "error": str(e),
                "next_agent": "ops"
            }


# Entrypoint for Foundry
async def pixel_handler(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler invoked by Azure Foundry Agent Service"""
    agent = PixelAgent(agent_id="pixel")
    context = AgentContext(agent_id="pixel")
    return await agent.execute(context, input_data)
