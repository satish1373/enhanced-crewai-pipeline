#!/usr/bin/env python3
"""
Enhanced Pipeline Management Script
Manage tickets, view statistics, and control reprocessing
"""

import json
import sys
from datetime import datetime
from enhanced_ticket_tracking import EnhancedTicketTracker

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_pipeline.py <command>")
        print("Commands:")
        print("  status        - Show pipeline statistics")
        print("  failed        - Show failed tickets")
        print("  retry <key>   - Mark ticket for retry")
        print("  clear <key>   - Clear ticket from tracking")
        print("  reset         - Reset all tracking data")
        return
    
    command = sys.argv[1]
    tracker = EnhancedTicketTracker()
    
    if command == "status":
        stats = tracker.get_processing_statistics()
        print("Pipeline Statistics:")
        print(f"  Total tickets: {stats['total_tickets']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Processing: {stats['processing']}")
        print(f"  Retry candidates: {stats['retry_candidates']}")
        print(f"  By language: {stats['by_language']}")
        print(f"  By domain: {stats['by_domain']}")
    
    elif command == "failed":
        failed = tracker.get_failed_tickets()
        print(f"Failed tickets ready for retry ({len(failed)}):")
        for ticket in failed:
            print(f"  {ticket.ticket_key}: {ticket.summary}")
            print(f"    Attempts: {ticket.attempt_count}")
            print(f"    Last error: {ticket.last_error}")
            print()
    
    elif command == "retry" and len(sys.argv) > 2:
        ticket_key = sys.argv[2]
        if ticket_key in tracker.ticket_versions:
            version = tracker.ticket_versions[ticket_key]
            version.processing_status = version.processing_status.NEEDS_REPROCESSING
            tracker.save_ticket_data()
            print(f"Marked {ticket_key} for reprocessing")
        else:
            print(f"Ticket {ticket_key} not found")
    
    elif command == "clear" and len(sys.argv) > 2:
        ticket_key = sys.argv[2]
        if ticket_key in tracker.ticket_versions:
            del tracker.ticket_versions[ticket_key]
            tracker.save_ticket_data()
            print(f"Cleared {ticket_key} from tracking")
        else:
            print(f"Ticket {ticket_key} not found")
    
    elif command == "reset":
        confirm = input("Are you sure you want to reset all tracking data? (yes/no): ")
        if confirm.lower() == "yes":
            tracker.ticket_versions = {}
            tracker.save_ticket_data()
            print("All tracking data cleared")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
