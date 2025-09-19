#!/usr/bin/env python3
"""
Solution Management Script
Command-line interface for managing stored AI-generated solutions
"""

import sys
import json
import argparse
from pathlib import Path
from code_storage_system import CodeStorageManager

def setup_parser():
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(description='Manage AI-generated solutions')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search solutions')
    search_parser.add_argument('--query', '-q', help='Search query')
    search_parser.add_argument('--language', '-l', help='Filter by language')
    search_parser.add_argument('--domain', '-d', help='Filter by domain')
    search_parser.add_argument('--tags', '-t', nargs='+', help='Filter by tags')
    search_parser.add_argument('--limit', type=int, default=10, help='Limit results')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get solution details')
    get_parser.add_argument('solution_id', help='Solution ID to retrieve')
    get_parser.add_argument('--show-content', action='store_true', help='Show file contents')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all solutions')
    list_parser.add_argument('--language', '-l', help='Filter by language')
    list_parser.add_argument('--recent', '-r', type=int, default=20, help='Show N recent solutions')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show storage statistics')
    
    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Create solution archive')
    archive_parser.add_argument('name', help='Archive name')
    archive_parser.add_argument('solution_ids', nargs='+', help='Solution IDs to archive')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export solution to directory')
    export_parser.add_argument('solution_id', help='Solution ID to export')
    export_parser.add_argument('target_dir', help='Target directory')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old solutions')
    cleanup_parser.add_argument('--days', type=int, default=90, help='Remove solutions older than N days')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted')
    
    return parser

def format_solution_list(solutions, limit=None):
    """Format solutions for display"""
    if limit:
        solutions = solutions[:limit]
    
    if not solutions:
        print("No solutions found.")
        return
    
    print(f"\n📋 Found {len(solutions)} solution(s):\n")
    
    for solution in solutions:
        print(f"🔹 **{solution['solution_id']}**")
        print(f"   Title: {solution['title']}")
        print(f"   Language: {solution['language']} | Domain: {solution['domain']}")
        print(f"   Created: {solution['created_at'][:19]}")
        print(f"   Files: {solution.get('file_count', 'Unknown')}")
        if solution.get('reusable'):
            print(f"   🔄 Reusable components available")
        print()

def show_solution_details(storage, solution_id, show_content=False):
    """Show detailed information about a solution"""
    try:
        solution = storage.get_solution(solution_id)
        metadata = solution['metadata']
        
        print(f"\n📄 Solution Details: {solution_id}")
        print("=" * 50)
        
        # Basic info
        print(f"**Title:** {metadata['title']}")
        print(f"**Ticket:** {metadata['ticket_key']}")
        print(f"**Language:** {metadata['language']}")
        print(f"**Domain:** {metadata['domain']}")
        print(f"**Created:** {metadata['created_at'][:19]}")
        print(f"**Agent:** {metadata.get('agent_used', 'Unknown')}")
        print(f"**Processing Time:** {metadata.get('processing_time', 0):.2f}s")
        print(f"**Complexity:** {metadata.get('complexity', 'Unknown')}")
        
        # Tags
        if metadata.get('tags'):
            print(f"**Tags:** {', '.join(metadata['tags'])}")
        
        # Dependencies
        if metadata.get('dependencies'):
            print(f"**Dependencies:** {', '.join(metadata['dependencies'])}")
        
        # Reusable components
        if metadata.get('reusable_components'):
            print(f"**Reusable Components:** {', '.join(metadata['reusable_components'])}")
        
        # Files
        print(f"\n📁 **Files ({len(solution['files'])}):**")
        for filename, filepath in solution['files'].items():
            file_size = Path(filepath).stat().st_size if Path(filepath).exists() else 0
            print(f"   - {filename} ({file_size} bytes)")
        
        # Location
        print(f"\n📍 **Storage Location:**")
        print(f"   {solution['solution_path']}")
        
        # Show file contents if requested
        if show_content:
            print(f"\n📄 **File Contents:**")
            for filename, filepath in solution['files'].items():
                if Path(filepath).exists() and Path(filepath).stat().st_size < 10000:  # Only small files
                    print(f"\n--- {filename} ---")
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) > 1000:
                                print(content[:1000] + "\n... (truncated)")
                            else:
                                print(content)
                    except Exception as e:
                        print(f"Error reading file: {e}")
                    print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error retrieving solution: {e}")

def show_storage_stats(storage):
    """Display storage statistics"""
    stats = storage.get_storage_stats()
    
    print("\n📊 Storage Statistics")
    print("=" * 30)
    print(f"Total Solutions: {stats['total_solutions']}")
    print(f"Storage Size: {stats['total_size_mb']} MB")
    print(f"Reusable Solutions: {stats['reusable_solutions']}")
    
    print(f"\n📈 By Language:")
    for language, count in sorted(stats['by_language'].items()):
        print(f"   {language}: {count}")
    
    print(f"\n🏷️  By Domain:")
    for domain, count in sorted(stats['by_domain'].items()):
        print(f"   {domain}: {count}")

def export_solution(storage, solution_id, target_dir):
    """Export solution to a directory"""
    try:
        solution = storage.get_solution(solution_id)
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📤 Exporting solution {solution_id} to {target_path}")
        
        # Copy all files
        import shutil
        copied_files = []
        
        for filename, filepath in solution['files'].items():
            source_path = Path(filepath)
            if source_path.exists():
                target_file = target_path / filename
                shutil.copy2(source_path, target_file)
                copied_files.append(filename)
                print(f"   ✅ Copied: {filename}")
        
        print(f"\n✅ Export complete!")
        print(f"   Files copied: {len(copied_files)}")
        print(f"   Target directory: {target_path}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

def main():
    """Main function"""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize storage manager
    storage = CodeStorageManager()
    
    try:
        if args.command == 'search':
            print(f"🔍 Searching solutions...")
            if args.query:
                print(f"   Query: '{args.query}'")
            if args.language:
                print(f"   Language: {args.language}")
            if args.domain:
                print(f"   Domain: {args.domain}")
            if args.tags:
                print(f"   Tags: {', '.join(args.tags)}")
            
            results = storage.search_solutions(
                query=args.query,
                language=args.language,
                domain=args.domain,
                tags=args.tags
            )
            
            format_solution_list(results, args.limit)
            
        elif args.command == 'get':
            show_solution_details(storage, args.solution_id, args.show_content)
            
        elif args.command == 'list':
            print(f"📋 Listing solutions...")
            
            results = storage.search_solutions(language=args.language)
            format_solution_list(results, args.recent)
            
        elif args.command == 'stats':
            show_storage_stats(storage)
            
        elif args.command == 'archive':
            print(f"📦 Creating archive: {args.name}")
            archive_path = storage.create_solution_archive(args.solution_ids, args.name)
            print(f"✅ Archive created: {archive_path}")
            
        elif args.command == 'export':
            export_solution(storage, args.solution_id, args.target_dir)
            
        elif args.command == 'cleanup':
            print(f"🧹 Cleanup not implemented yet (safety feature)")
            print(f"   Would clean solutions older than {args.days} days")
            if args.dry_run:
                print("   (This was a dry run)")
        
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
