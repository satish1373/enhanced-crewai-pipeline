#!/bin/bash
"""
Auto-Sync Manager for Replit
Easy management of the auto-sync daemon
"""

SCRIPT_NAME="auto_sync.py"
PID_FILE="auto_sync.pid"
LOG_FILE="auto_sync.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            # Stale PID file
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

start_daemon() {
    if is_running; then
        print_warning "Auto-sync daemon is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    print_status "Starting auto-sync daemon..."
    
    # Start the daemon in background
    nohup python3 "$SCRIPT_NAME" daemon > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if is_running; then
        print_success "Auto-sync daemon started successfully (PID: $(cat $PID_FILE))"
        print_status "Log file: $LOG_FILE"
        return 0
    else
        print_error "Failed to start auto-sync daemon"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_daemon() {
    if ! is_running; then
        print_warning "Auto-sync daemon is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    print_status "Stopping auto-sync daemon (PID: $PID)..."
    
    kill "$PID"
    sleep 2
    
    if ! is_running; then
        print_success "Auto-sync daemon stopped successfully"
        rm -f "$PID_FILE"
        return 0
    else
        print_warning "Daemon didn't stop gracefully, forcing termination..."
        kill -9 "$PID"
        rm -f "$PID_FILE"
        print_success "Auto-sync daemon forcefully stopped"
        return 0
    fi
}

restart_daemon() {
    print_status "Restarting auto-sync daemon..."
    stop_daemon
    sleep 1
    start_daemon
}

show_status() {
    print_status "=== Auto-Sync Status ==="
    
    if is_running; then
        PID=$(cat "$PID_FILE")
        print_success "✅ Daemon is running (PID: $PID)"
        
        # Show process info
        echo ""
        print_status "Process information:"
        ps -p "$PID" -o pid,ppid,cmd,etime,pcpu,pmem
        
    else
        print_warning "❌ Daemon is not running"
    fi
    
    # Show recent logs
    if [ -f "$LOG_FILE" ]; then
        echo ""
        print_status "Recent log entries (last 10 lines):"
        tail -10 "$LOG_FILE"
    fi
    
    # Show sync stats
    echo ""
    print_status "Sync statistics:"
    python3 "$SCRIPT_NAME" stats
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Auto-sync logs:"
        if [ "$1" = "follow" ]; then
            tail -f "$LOG_FILE"
        else
            tail -20 "$LOG_FILE"
        fi
    else
        print_warning "No log file found"
    fi
}

manual_sync() {
    print_status "Performing manual sync..."
    python3 "$SCRIPT_NAME" manual
}

check_changes() {
    print_status "Checking for changes..."
    python3 "$SCRIPT_NAME" check
}

install_service() {
    print_status "Setting up auto-sync as a background service..."
    
    # Create a simple startup script
    cat > start_auto_sync.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./sync_manager.sh start
EOF
    
    chmod +x start_auto_sync.sh
    
    print_success "Created start_auto_sync.sh"
    print_status "To auto-start on Replit boot, add this to your .replit file:"
    echo ""
    echo "  [deployment]"
    echo "  run = \"./start_auto_sync.sh\""
    echo ""
}

show_help() {
    echo "Auto-Sync Manager for Replit"
    echo "============================"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  start     - Start the auto-sync daemon"
    echo "  stop      - Stop the auto-sync daemon"
    echo "  restart   - Restart the auto-sync daemon"
    echo "  status    - Show daemon status and recent logs"
    echo "  logs      - Show recent log entries"
    echo "  follow    - Follow log entries in real-time"
    echo "  manual    - Perform a manual sync"
    echo "  check     - Check for changes without syncing"
    echo "  install   - Set up auto-sync as a service"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start auto-sync daemon"
    echo "  $0 status             # Check if daemon is running"
    echo "  $0 logs               # View recent sync activity"
    echo "  $0 manual             # Force immediate sync"
    echo "  $0 follow             # Watch logs in real-time"
}

# Main command handling
case "$1" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        restart_daemon
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    follow)
        show_logs follow
        ;;
    manual)
        manual_sync
        ;;
    check)
        check_changes
        ;;
    install)
        install_service
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
