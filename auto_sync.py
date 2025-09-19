#!/usr/bin/env python3
"""
Enhanced Auto-Sync Script for Replit
Automatically commits and pushes changes to GitHub with intelligent filtering
"""

import subprocess
import time
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class ReplicAutoSync:
    def __init__(self, sync_interval=300, quiet_hours=None):
        """
        Initialize the auto-sync system
        
        Args:
            sync_interval (int): Seconds between sync checks (default: 5 minutes)
            quiet_hours (tuple): (start_hour, end_hour) for quiet time (24h format)
        """
        self.sync_interval = sync_interval
        self.quiet_hours = quiet_hours or (23, 7)  # 11PM to 7AM
        self.last_sync = None
        self.sync_log = "auto_sync.log"
        self.stats_file = "sync_stats.json"
        
        # Files to ignore for auto-commit
        self.ignore_patterns = [
            '*.log',
            '*.tmp',
            '*.backup*',
            '__pycache__/*',
            '.cache/*',
            'sync_stats.json',
            'auto_sync.log',
            'processing_history.json',  # Your pipeline data
            'ticket_tracking.json'      # Your pipeline data
        ]
        
        self.log("🚀 Auto-sync system initialized")
        self.log(f"   Sync interval: {sync_interval} seconds ({sync_interval//60} minutes)")
        self.log(f"   Quiet hours: {self.quiet_hours[0]}:00 - {self.quiet_hours[1]}:00")

    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # Also write to log file
        with open(self.sync_log, 'a') as f:
            f.write(log_entry + "\n")

    def is_quiet_time(self):
        """Check if it's during quiet hours"""
        current_hour = datetime.now().hour
        start, end = self.quiet_hours
        
        if start < end:
            return start <= current_hour < end
        else:  # Quiet time spans midnight
            return current_hour >= start or current_hour < end

    def has_changes(self):
        """Check if there are uncommitted changes"""
        try:
            # Check for unstaged changes
            result = subprocess.run(['git', 'diff', '--quiet'], 
                                  capture_output=True, cwd='.')
            unstaged_changes = result.returncode != 0
            
            # Check for staged changes
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                  capture_output=True, cwd='.')
            staged_changes = result.returncode != 0
            
            # Check for untracked files (but ignore patterns)
            result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], 
                                  capture_output=True, text=True, cwd='.')
            untracked_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Filter untracked files based on ignore patterns
            important_untracked = []
            for file in untracked_files:
                if file and not any(self._matches_pattern(file, pattern) for pattern in self.ignore_patterns):
                    important_untracked.append(file)
            
            has_important_untracked = len(important_untracked) > 0
            
            if unstaged_changes or staged_changes or has_important_untracked:
                self.log(f"📝 Changes detected:")
                if unstaged_changes:
                    self.log("   - Modified files")
                if staged_changes:
                    self.log("   - Staged changes")
                if has_important_untracked:
                    self.log(f"   - New files: {', '.join(important_untracked[:3])}{'...' if len(important_untracked) > 3 else ''}")
                return True
            
            return False
            
        except Exception as e:
            self.log(f"❌ Error checking for changes: {e}")
            return False

    def _matches_pattern(self, filename, pattern):
        """Simple pattern matching for ignore patterns"""
        if pattern.startswith('*'):
            return filename.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return filename.startswith(pattern[:-1])
        elif '/*' in pattern:
            return filename.startswith(pattern.replace('/*', '/'))
        else:
            return filename == pattern

    def get_change_summary(self):
        """Get a summary of what changed"""
        try:
            # Get modified files
            result = subprocess.run(['git', 'diff', '--name-only'], 
                                  capture_output=True, text=True, cwd='.')
            modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Get untracked files
            result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], 
                                  capture_output=True, text=True, cwd='.')
            untracked_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Filter important files
            important_files = []
            for file in modified_files + untracked_files:
                if file and not any(self._matches_pattern(file, pattern) for pattern in self.ignore_patterns):
                    important_files.append(file)
            
            if not important_files:
                return "Minor updates"
            
            # Categorize changes
            categories = {
                'core': [],
                'config': [],
                'docs': [],
                'other': []
            }
            
            for file in important_files:
                if any(x in file.lower() for x in ['enhanced_', 'main.py', 'manage_']):
                    categories['core'].append(file)
                elif any(x in file.lower() for x in ['readme', '.md', 'requirements']):
                    categories['docs'].append(file)
                elif any(x in file.lower() for x in ['.env', 'config', '.gitignore']):
                    categories['config'].append(file)
                else:
                    categories['other'].append(file)
            
            summary_parts = []
            if categories['core']:
                summary_parts.append(f"Core updates ({len(categories['core'])} files)")
            if categories['config']:
                summary_parts.append(f"Config changes ({len(categories['config'])} files)")
            if categories['docs']:
                summary_parts.append(f"Documentation ({len(categories['docs'])} files)")
            if categories['other']:
                summary_parts.append(f"Other changes ({len(categories['other'])} files)")
            
            return "; ".join(summary_parts) if summary_parts else "General updates"
            
        except Exception as e:
            self.log(f"⚠️  Could not generate change summary: {e}")
            return "Updates"

    def sync_changes(self):
        """Commit and push changes to GitHub"""
        try:
            if self.is_quiet_time():
                self.log("😴 Quiet time - skipping sync")
                return False
            
            if not self.has_changes():
                return False
            
            self.log("🔄 Starting sync process...")
            
            # Stage all changes (except ignored files)
            subprocess.run(['git', 'add', '.'], cwd='.')
            self.log("   ✅ Staged changes")
            
            # Generate commit message
            change_summary = self.get_change_summary()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_message = f"Auto-sync: {change_summary} ({timestamp})"
            
            # Commit changes
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode != 0:
                self.log(f"⚠️  Nothing to commit: {result.stderr}")
                return False
            
            self.log(f"   ✅ Committed: {commit_message}")
            
            # Push to GitHub
            result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                self.log("   ✅ Pushed to GitHub successfully")
                self.last_sync = datetime.now()
                self.update_stats(success=True)
                return True
            else:
                self.log(f"   ❌ Push failed: {result.stderr}")
                self.update_stats(success=False, error=result.stderr)
                return False
                
        except Exception as e:
            self.log(f"❌ Sync error: {e}")
            self.update_stats(success=False, error=str(e))
            return False

    def update_stats(self, success=True, error=None):
        """Update sync statistics"""
        try:
            stats = {}
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
            
            stats.setdefault('total_syncs', 0)
            stats.setdefault('successful_syncs', 0)
            stats.setdefault('failed_syncs', 0)
            stats.setdefault('last_sync', None)
            stats.setdefault('last_error', None)
            
            stats['total_syncs'] += 1
            if success:
                stats['successful_syncs'] += 1
                stats['last_sync'] = datetime.now().isoformat()
                stats['last_error'] = None
            else:
                stats['failed_syncs'] += 1
                stats['last_error'] = error
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            self.log(f"⚠️  Could not update stats: {e}")

    def get_stats(self):
        """Get sync statistics"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}

    def print_stats(self):
        """Print current sync statistics"""
        stats = self.get_stats()
        if not stats:
            self.log("📊 No sync statistics available yet")
            return
        
        total = stats.get('total_syncs', 0)
        successful = stats.get('successful_syncs', 0)
        failed = stats.get('failed_syncs', 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        self.log(f"📊 Sync Statistics:")
        self.log(f"   Total syncs: {total}")
        self.log(f"   Successful: {successful}")
        self.log(f"   Failed: {failed}")
        self.log(f"   Success rate: {success_rate:.1f}%")
        
        if stats.get('last_sync'):
            last_sync = datetime.fromisoformat(stats['last_sync'])
            self.log(f"   Last sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")

    def run_daemon(self):
        """Run the auto-sync daemon"""
        self.log("🔄 Starting auto-sync daemon...")
        self.print_stats()
        
        try:
            while True:
                # Sync if changes detected
                if self.sync_changes():
                    self.log("✅ Sync cycle completed")
                else:
                    # Only log "no changes" occasionally to avoid spam
                    if datetime.now().minute % 15 == 0:  # Every 15 minutes
                        self.log("ℹ️  No changes to sync")
                
                # Wait for next cycle
                time.sleep(self.sync_interval)
                
        except KeyboardInterrupt:
            self.log("\n🛑 Auto-sync daemon stopped by user")
            self.print_stats()
        except Exception as e:
            self.log(f"💥 Daemon crashed: {e}")
            raise

    def manual_sync(self):
        """Perform a manual sync"""
        self.log("🔧 Manual sync requested...")
        success = self.sync_changes()
        if success:
            self.log("✅ Manual sync completed successfully")
        else:
            self.log("ℹ️  No changes to sync")
        self.print_stats()
        return success


def main():
    """Main function with command line options"""
    import sys
    
    # Configuration
    SYNC_INTERVAL = 300  # 5 minutes
    QUIET_HOURS = (23, 7)  # 11PM to 7AM
    
    # Create auto-sync instance
    auto_sync = ReplicAutoSync(
        sync_interval=SYNC_INTERVAL,
        quiet_hours=QUIET_HOURS
    )
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'manual':
            auto_sync.manual_sync()
        elif command == 'stats':
            auto_sync.print_stats()
        elif command == 'daemon':
            auto_sync.run_daemon()
        elif command == 'check':
            if auto_sync.has_changes():
                print("✅ Changes detected - sync would run")
            else:
                print("ℹ️  No changes detected")
        else:
            print(f"""
Enhanced Auto-Sync for Replit
=============================

Usage: python auto_sync.py [command]

Commands:
  daemon    - Run continuous auto-sync (default)
  manual    - Perform one-time manual sync
  stats     - Show sync statistics
  check     - Check for changes without syncing

Examples:
  python auto_sync.py daemon   # Start auto-sync daemon
  python auto_sync.py manual   # Sync once
  python auto_sync.py stats    # View statistics
            """)
    else:
        # Default: run daemon
        auto_sync.run_daemon()


if __name__ == "__main__":
    main()
