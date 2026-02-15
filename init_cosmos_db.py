"""
Initialize and verify Cosmos DB container for approval system

This script ensures the approval-queue container exists with correct configuration
"""

import sys
import os
import logging
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosResourceExistsError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from config import get_config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("cosmos_init")


def initialize_cosmos_db():
    """Initialize and verify Cosmos DB containers"""
    
    print("\n" + "="*80)
    print("COSMOS DB INITIALIZATION")
    print("="*80)
    
    try:
        config = get_config()
        logger.info("Loading Azure credentials from config...")
        
        cosmos_endpoint = config.cosmos_db.endpoint
        cosmos_key = config.cosmos_db.key
        
        logger.info(f"Connecting to Cosmos DB: {cosmos_endpoint}")
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        
        # Get or create database
        logger.info("Checking 'articles' database...")
        try:
            database = client.get_database_client("articles")
            logger.info("✓ Database 'articles' found")
        except CosmosResourceNotFoundError:
            logger.info("✗ Database not found, creating...")
            database = client.create_database(id="articles")
            logger.info("✓ Database 'articles' created")
        
        # Get or create approval-queue container
        logger.info("Checking 'approval-queue' container...")
        try:
            container = database.get_container_client("approval-queue")
            logger.info("✓ Container 'approval-queue' found")
            # Try to delete and recreate to ensure clean state
            logger.info("Recreating container for clean state...")
            try:
                database.delete_container("approval-queue")
                logger.info("  Deleted existing container")
            except:
                pass
            
            container = database.create_container(
                id="approval-queue",
                partition_key=PartitionKey(path="/status"),
                offer_throughput=400
            )
            logger.info("✓ Container 'approval-queue' recreated")
            logger.info("  Partition key: /status")
            logger.info("  Throughput: 400 RU/s")
        except CosmosResourceNotFoundError:
            logger.info("✗ Container not found, creating...")
            container = database.create_container(
                id="approval-queue",
                partition_key=PartitionKey(path="/status"),
                offer_throughput=400
            )
            logger.info("✓ Container 'approval-queue' created")
            logger.info("  Partition key: /status")
            logger.info("  Throughput: 400 RU/s")
        
        # Test container access
        logger.info("Testing container access...")
        try:
            # Try to query items (even if empty)
            items = list(container.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            ))
            logger.info(f"✓ Container accessible - {len(items)} items found")
        except Exception as e:
            logger.error(f"✗ Failed to access container: {str(e)}")
            return False
        
        print("\n" + "="*80)
        print("✅ COSMOS DB INITIALIZATION SUCCESSFUL")
        print("="*80)
        print("\nContainer Status:")
        print("  Database: articles")
        print("  Container: approval-queue")
        print("  Partition Key: /status")
        print("  Throughput: 400 RU/s")
        print("  Status: ✓ READY FOR USE")
        print("\nYou can now:")
        print("  1. Restart the Flask service: python approval_service.py")
        print("  2. Test queue operations: curl http://localhost:8000/api/approval/queue/stats")
        print("  3. Submit articles: curl -X POST http://localhost:8000/api/articles/submit ...")
        print("\n" + "="*80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Cosmos DB: {str(e)}")
        print("\n" + "="*80)
        print("❌ COSMOS DB INITIALIZATION FAILED")
        print("="*80)
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Verify credentials in config.py")
        print("  2. Check network access to Azure")
        print("  3. Verify Cosmos DB account exists")
        print("  4. Check IAM permissions")
        print("\n" + "="*80 + "\n")
        return False


if __name__ == "__main__":
    success = initialize_cosmos_db()
    sys.exit(0 if success else 1)
