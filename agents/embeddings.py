"""
Vector Embeddings Module

Generates and manages vector embeddings for articles using Azure OpenAI.
Enables semantic search and similarity analysis across the content corpus.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

from openai import AzureOpenAI
from azure.cosmos import CosmosClient
from config import get_config

logger = logging.getLogger("embeddings")


class EmbeddingsManager:
    """Manages vector embeddings for articles and brand rules"""
    
    # Azure OpenAI embeddings model
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536  # text-embedding-3-small output dimension
    
    def __init__(self):
        self.config = get_config()
        self.openai_client = AzureOpenAI(
            api_key=self.config.openai.api_key,
            api_version=self.config.openai.api_version,
            azure_endpoint=self.config.openai.endpoint
        )
        
        self.cosmos_client = CosmosClient(
            url=self.config.cosmos_db.endpoint,
            credential=self.config.cosmos_db.key
        )
        
        logger.info("EmbeddingsManager initialized")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Vector embedding as list of floats
        """
        try:
            def call_embeddings():
                response = self.openai_client.embeddings.create(
                    model=self.EMBEDDING_MODEL,
                    input=text
                )
                return response.data[0].embedding
            
            # Call synchronous API via asyncio.to_thread
            embedding = await asyncio.to_thread(call_embeddings)
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise
    
    async def generate_embeddings_batch(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of vector embeddings
        """
        try:
            def call_embeddings_batch():
                response = self.openai_client.embeddings.create(
                    model=self.EMBEDDING_MODEL,
                    input=texts
                )
                # Sort by index to maintain order
                embeddings = sorted(response.data, key=lambda x: x.index)
                return [e.embedding for e in embeddings]
            
            embeddings = await asyncio.to_thread(call_embeddings_batch)
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise
    
    async def embed_article(
        self,
        article_id: str,
        title: str,
        content: str,
        seo_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate and store embedding for an article
        
        Args:
            article_id: Unique article identifier
            title: Article title
            content: Article content
            seo_keywords: Optional SEO keywords
            
        Returns:
            Article document with embedding
        """
        # Combine title, content preview, and keywords for embedding
        embedding_text = f"{title}\n{content[:1000]}"
        if seo_keywords:
            embedding_text += f"\nKeywords: {', '.join(seo_keywords)}"
        
        embedding = await self.generate_embedding(embedding_text)
        
        article_doc = {
            "id": article_id,
            "title": title,
            "content": content,
            "seo_keywords": seo_keywords or [],
            "embedding": embedding,
            "embedding_dimension": self.EMBEDDING_DIMENSION,
            "embedding_model": self.EMBEDDING_MODEL,
            "embedding_created_at": datetime.utcnow().isoformat(),
            "type": "article"
        }
        
        # Store in Cosmos DB
        try:
            database = self.cosmos_client.get_database_client(
                self.config.cosmos_db.database_name
            )
            container = database.get_container_client(
                self.config.cosmos_db.articles_container
            )
            
            container.upsert_item(article_doc)
            logger.info(f"Stored embedding for article {article_id}")
            
        except Exception as e:
            logger.warning(f"Could not store embedding in Cosmos: {str(e)}")
        
        return article_doc
    
    async def semantic_search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar articles using semantic search
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar articles with similarity scores
        """
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)
        
        # Search articles in Cosmos DB
        try:
            database = self.cosmos_client.get_database_client(
                self.config.cosmos_db.database_name
            )
            container = database.get_container_client(
                self.config.cosmos_db.articles_container
            )
            
            # Query all articles with embeddings
            items = list(container.query_items(
                query="SELECT * FROM c WHERE c.embedding != null OFFSET 0 LIMIT 1000",
                enable_cross_partition_query=True
            ))
            
            # Calculate similarity scores
            results = []
            for item in items:
                if "embedding" in item:
                    similarity = self._cosine_similarity(
                        query_embedding,
                        item["embedding"]
                    )
                    results.append({
                        "article_id": item.get("id"),
                        "title": item.get("title"),
                        "score": similarity,
                        "keywords": item.get("seo_keywords", [])
                    })
            
            # Sort by similarity and return top-k
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
    
    async def create_brand_rules_embeddings(
        self,
        brand_rules: List[Dict[str, str]]
    ):
        """
        Create embeddings for brand rules for compliance checking
        
        Args:
            brand_rules: List of brand rules {id, description, guideline}
        """
        try:
            # Generate embeddings for all rules
            descriptions = [br["description"] for br in brand_rules]
            embeddings = await self.generate_embeddings_batch(descriptions)
            
            # Store brand rules with embeddings
            database = self.cosmos_client.get_database_client(
                self.config.cosmos_db.database_name
            )
            container = database.get_container_client(
                self.config.cosmos_db.agent_state_container
            )
            
            for rule, embedding in zip(brand_rules, embeddings):
                rule_doc = {
                    "id": f"rule-{rule.get('id')}",
                    "type": "brand_rule",
                    "description": rule.get("description"),
                    "guideline": rule.get("guideline"),
                    "embedding": embedding,
                    "created_at": datetime.utcnow().isoformat()
                }
                container.upsert_item(rule_doc)
            
            logger.info(f"Created embeddings for {len(brand_rules)} brand rules")
            
        except Exception as e:
            logger.error(f"Failed to create brand rules embeddings: {str(e)}")
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        return dot_product / (norm_v1 * norm_v2)


async def test_embeddings():
    """Test embeddings functionality"""
    logger.info("Testing embeddings functionality")
    
    manager = EmbeddingsManager()
    
    # Test article embedding
    article_doc = await manager.embed_article(
        article_id="test-article-001",
        title="Test Article: Machine Learning Advances",
        content="""
        This article discusses recent advances in machine learning.
        New techniques are emerging for improving model accuracy and efficiency.
        """,
        seo_keywords=["machine learning", "AI", "neural networks"]
    )
    
    logger.info(f"Created article embedding with {len(article_doc['embedding'])} dimensions")
    
    # Test semantic search
    results = await manager.semantic_search("AI and machine learning", top_k=3)
    logger.info(f"Semantic search results: {results}")
    
    # Test brand rules
    brand_rules = [
        {
            "id": "tone-001",
            "description": "Maintain professional and objective tone",
            "guideline": "Avoid sensationalism and personal opinions"
        },
        {
            "id": "accuracy-001",
            "description": "Ensure factual accuracy",
            "guideline": "Verify all claims with reliable sources"
        }
    ]
    
    await manager.create_brand_rules_embeddings(brand_rules)
    logger.info("Created brand rules embeddings")
    
    print("\n" + "=" * 70)
    print("Embeddings Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_embeddings())
