#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load more articles into the approval system for testing
"""

import requests
import time
import random
import sys
import io
from typing import Dict, Any, List

# Fix encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:8000"

# Diverse test articles
TEST_ARTICLES = [
    {
        "title": "Quantum Computing Breakthrough: New Processor Achieves Quantum Advantage",
        "content": "Scientists at leading tech company announce major breakthrough in quantum computing. The new processor successfully demonstrates quantum advantage, solving a complex problem 100 times faster than classical computers.",
        "source": "Tech News Daily"
    },
    {
        "title": "Climate Summit Results: 150 Nations Commit to Net-Zero Targets",
        "content": "Global climate summit concludes with unprecedented commitment. 150 nations have pledged to achieve net-zero emissions by 2050, signaling major shift in climate policy worldwide.",
        "source": "Environmental News"
    },
    {
        "title": "Healthcare Innovation: AI Diagnoses Disease Earlier Than Human Doctors",
        "content": "Major medical research reveals AI system can detect early-stage disease with 95% accuracy, often before human physicians. Study covers 50,000 patient cases across multiple institutions.",
        "source": "Medical Gazette"
    },
    {
        "title": "Market Analysis: Tech Stocks Rally on Strong Earnings Reports",
        "content": "Technology sector surges after series of strong quarterly earnings. Major companies report double-digit growth, signaling continued strength in digital transformation investments.",
        "source": "Financial Times"
    },
    {
        "title": "Space Exploration: NASA Announces Lunar Base Construction Plans",
        "content": "NASA reveals detailed plans for permanent lunar base, targeted for completion in 2030. Project will serve as staging point for Mars missions and scientific research.",
        "source": "Space News"
    },
    {
        "title": "Education Transformation: Universities Embrace Hybrid Learning Models",
        "content": "Major universities announce permanent shift to hybrid learning following pandemic. Combines in-person and online education to improve accessibility and learning outcomes.",
        "source": "Education Weekly"
    },
    {
        "title": "Energy Transition: Solar and Wind Now Exceed 50% of Grid Capacity",
        "content": "Historic milestone achieved as renewable energy sources surpass 50% of electrical grid capacity in major developed nation. Accelerates timeline for complete energy transition.",
        "source": "Clean Energy Report"
    },
    {
        "title": "Cybersecurity Alert: New Vulnerability Found in Enterprise Software",
        "content": "Security researchers discover critical vulnerability affecting millions of enterprise systems. Patches available now. Organizations urged to update immediately to prevent exploitation.",
        "source": "Security Today"
    },
    {
        "title": "Biotech Breakthrough: Gene Therapy Shows Promise Against Genetic Disorders",
        "content": "Clinical trials demonstrate gene therapy successfully treats previously untreatable genetic condition. Offers new hope for patients with rare genetic diseases.",
        "source": "Biotech News"
    },
    {
        "title": "Infrastructure Investment: $2 Trillion Development Plan Approved",
        "content": "Government approves massive infrastructure investment spanning roads, bridges, and digital networks. Will create 500,000 jobs and modernize aging infrastructure.",
        "source": "Infrastructure Today"
    },
    {
        "title": "Artificial Intelligence in Legal: AI Lawyers Reduce Case Processing Time by 70%",
        "content": "Law firms implementing AI document review systems report 70% reduction in case processing time. Some legal experts warn about job displacement concerns.",
        "source": "Legal Tech Weekly"
    },
    {
        "title": "Retail Innovation: Autonomous Stores Expand to 100 Locations",
        "content": "Retailer announces rapid expansion of cashier-less stores to 100 cities. Technology uses computer vision and AI to enable seamless shopping experience.",
        "source": "Retail News"
    },
]


def submit_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """Submit an article to the approval system"""
    try:
        response = requests.post(
            f"{API_URL}/api/articles/submit",
            json=article,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_queue_stats() -> Dict[str, Any]:
    """Get approval queue statistics"""
    try:
        response = requests.get(f"{API_URL}/api/approval/queue/stats", timeout=10)
        response.raise_for_status()
        return response.json().get("stats", {})
    except Exception as e:
        return {"error": str(e)}


def get_queue_items(status: str = None) -> List[Dict[str, Any]]:
    """Get items from queue filtered by status"""
    try:
        url = f"{API_URL}/api/approval/queue"
        if status:
            url += f"?status={status}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"Error getting queue: {e}")
        return []


def main():
    print("=" * 70)
    print("📰 Newsroom AI - Article Load Test")
    print("=" * 70)
    print()
    
    print("Starting article submission...")
    print()
    
    results = {
        "submitted": 0,
        "auto_published": 0,
        "queued": 0,
        "rejected": 0,
        "error": 0,
        "by_routing": {}
    }
    
    # Submit all articles
    for i, article in enumerate(TEST_ARTICLES, 1):
        print(f"[{i:2d}/{len(TEST_ARTICLES)}] Submitting: {article['title'][:50]}...")
        
        result = submit_article(article)
        
        if result.get("status") == "submitted":
            results["submitted"] += 1
            routing = result.get("routing", "unknown")
            
            # Count by routing decision
            if routing not in results["by_routing"]:
                results["by_routing"][routing] = 0
            results["by_routing"][routing] += 1
            
            # Track routing outcomes
            if routing == "AUTO_PUBLISHED":
                results["auto_published"] += 1
                print(f"         ✓ AUTO-PUBLISHED (high confidence)")
            elif routing in ["PENDING_REVIEW", "QUEUE_FOR_REVIEW"]:
                results["queued"] += 1
                print(f"         ⏱ QUEUED FOR REVIEW (medium confidence)")
            elif routing in ["REJECTED", "REJECTED_BY_PROF", "REJECTED_BY_SCOUT"]:
                results["rejected"] += 1
                print(f"         ✗ REJECTED (low confidence)")
            else:
                print(f"         ? UNKNOWN ROUTING: {routing}")
        else:
            results["error"] += 1
            print(f"         ✗ ERROR: {result.get('message', 'Unknown error')}")
        
        # Small delay between submissions
        time.sleep(0.5)
    
    print()
    print("=" * 70)
    print("📊 Load Test Results")
    print("=" * 70)
    print()
    
    print(f"Articles Submitted: {results['submitted']}/{len(TEST_ARTICLES)}")
    print()
    
    print("Routing Distribution:")
    print(f"  🟢 Auto-Published:  {results['auto_published']:3d}")
    print(f"  🟡 Queued:          {results['queued']:3d}")
    print(f"  🔴 Rejected:        {results['rejected']:3d}")
    print(f"  ⚠️  Errors:         {results['error']:3d}")
    print()
    
    # Wait for processing
    print("Waiting for queue to update...")
    time.sleep(5)
    
    # Get final stats
    print()
    print("Final Queue Statistics:")
    stats = get_queue_stats()
    
    if "error" not in stats:
        pending = stats.get("pending", 0)
        approved = stats.get("approved", 0)
        rejected = stats.get("rejected", 0)
        total = stats.get("total", 0)
        
        print(f"  🟡 Pending Review:  {pending:3d}")
        print(f"  ✅ Approved:        {approved:3d}")
        print(f"  ❌ Rejected:        {rejected:3d}")
        print(f"  📊 Total:           {total:3d}")
        print()
        
        # Show breakdown by status
        if pending > 0:
            pending_items = get_queue_items("pending_review")
            print(f"📋 Pending Articles ({pending}):")
            for item in pending_items[:5]:  # Show first 5
                score = item.get("confidence_score", 0)
                print(f"   • {item.get('title', 'Untitled')[:45]}...")
                print(f"     Confidence: {score:.1f}/10")
            if len(pending_items) > 5:
                print(f"   ... and {len(pending_items) - 5} more")
    else:
        print(f"  Error retrieving stats: {stats['error']}")
    
    print()
    print("=" * 70)
    print("✅ Load Test Complete!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  1. Review articles: http://localhost:3000")
    print("  2. Approve high-quality articles")
    print("  3. Reject low-quality articles")
    print("  4. Monitor queue updates")
    print()


if __name__ == "__main__":
    main()
