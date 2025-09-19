#!/usr/bin/env python3
"""
Test Enhanced Ticket Tracking
"""

import asyncio
from enhanced_ticket_tracking import EnhancedTicketTracker, SmartTicketProcessor

async def test_enhanced_tracking():
    print("Testing Enhanced Ticket Tracking...")
    
    # Test tracker initialization
    tracker = EnhancedTicketTracker("test_tracking.json")
    print("✓ Tracker initialized")
    
    # Test JQL generation
    jql = tracker.generate_enhanced_jql("TEST")
    print(f"✓ Generated JQL: {jql[:100]}...")
    
    # Test statistics
    stats = tracker.get_processing_statistics()
    print(f"✓ Statistics: {stats}")
    
    print("Enhanced tracking tests completed!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_tracking())
