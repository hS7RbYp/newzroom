#!/usr/bin/env python3
"""Debug approval workflow"""
import asyncio
from agents.approval import ApprovalQueue, ApprovalStatus

async def test_approve():
    queue = ApprovalQueue()
    
    # Get pending items
    print("Getting pending items...")
    pending = await queue.get_queue(ApprovalStatus.PENDING_REVIEW)
    print(f"Found {len(pending)} pending items")
    
    if pending:
        article = pending[0]
        article_id = article["article_id"]
        doc_id = article["id"]
        print(f"\nArticle ID: {article_id}")
        print(f"Doc ID: {doc_id}")
        print(f"Current Status: {article['status']}")
        
        # Try to approve
        print(f"\nApproving article {article_id}...")
        result = await queue.approve_article(article_id, "editor-001", "Test approval")
        print(f"Approval result: {result}")
        
        # Check updated status
        print(f"\nChecking updated status...")
        query = "SELECT * FROM c WHERE c.article_id = @article_id"
        items = list(queue.approval_container.query_items(
            query=query,
            parameters=[{"name": "@article_id", "value": article_id}],
            enable_cross_partition_query=True
        ))
        
        if items:
            updated = items[0]
            print(f"Updated Status: {updated['status']}")
            print(f"Approved At: {updated.get('approved_at')}")
        else:
            print("Item not found after approval!")

asyncio.run(test_approve())
