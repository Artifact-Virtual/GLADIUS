#!/bin/bash
#
# Automated Deployment Script for Enterprise Dashboard
# This script enables CI/CD deployment with health checking and rollback capabilities
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_LOG="$SCRIPT_DIR/logs/deployment.log"

# Configuration
export NODE_ENV="production"
export DEPLOYMENT_MODE="automated"
export BUILD_MODE="force"
export LOG_LEVEL="INFO"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $1" >> "$DEPLOYMENT_LOG"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$DEPLOYMENT_LOG"
    exit 1
}

print_info() {
    echo -e "${BLUE}🔧${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO: $1" >> "$DEPLOYMENT_LOG"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1" >> "$DEPLOYMENT_LOG"
}

# Create deployment log directory
mkdir -p logs

# Pre-deployment validation
validate_environment() {
    print_info "Validating deployment environment..."
    
    # Check required files
    local required_files=(
        "package.json"
        "backend_api.py"
        "start_enterprise.sh"
        "install.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file missing: $file"
        fi
    done
    
    # Check Node.js and Python
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found - required for deployment"
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found - required for deployment"
    fi
    
    print_status "Environment validation passed"
}

# Backup current deployment
backup_current_deployment() {
    print_info "Creating backup of current deployment..."
    
    local backup_dir="backups/deployment_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup critical files and directories
    if [[ -d "build" ]]; then
        cp -r build "$backup_dir/"
    fi
    
    if [[ -f "config/.env" ]]; then
        cp config/.env "$backup_dir/"
    fi
    
    if [[ -d "data" ]]; then
        cp -r data "$backup_dir/"
    fi
    
    echo "$backup_dir" > .last_backup_path
    print_status "Backup created at $backup_dir"
}

# Stop running services
stop_services() {
    print_info "Stopping existing services..."
    
    # Use the kill script if available
    if [[ -f "kill_enterprise.sh" ]]; then
        chmod +x kill_enterprise.sh
        ./kill_enterprise.sh
    else
        # Manual port cleanup
        for port in 3000 5001 5000; do
            if command -v fuser &> /dev/null; then
                fuser -k ${port}/tcp 2>/dev/null || true
            fi
        done
    fi
    
    print_status "Services stopped"
}

# Run deployment
deploy() {
    print_info "Starting automated deployment..."
    
    # Make start script executable
    chmod +x start_enterprise.sh
    
    # Run automated deployment
    if ./start_enterprise.sh; then
        print_status "Deployment script completed successfully"
    else
        print_error "Deployment script failed"
    fi
}

# Health check with retry logic
health_check_with_retry() {
    print_info "Running post-deployment health checks..."
    
    local max_attempts=10
    local attempt=1
    
    # Check backend health
    while [[ $attempt -le $max_attempts ]]; do
        print_info "Backend health check attempt $attempt/$max_attempts..."
        
        if curl -s http://localhost:5000/api/health >/dev/null 2>&1 || \
           curl -s http://localhost:5001/api/health >/dev/null 2>&1; then
            print_status "Backend health check passed"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            print_error "Backend health check failed after $max_attempts attempts"
            return 1
        fi
        
        sleep 10
        ((attempt++))
    done
    
    # Check frontend health
    attempt=1
    while [[ $attempt -le $max_attempts ]]; do
        print_info "Frontend health check attempt $attempt/$max_attempts..."
        
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            print_status "Frontend health check passed"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            print_error "Frontend health check failed after $max_attempts attempts"
            return 1
        fi
        
        sleep 5
        ((attempt++))
    done
    
    print_status "All health checks passed"
    return 0
}

# Rollback function
rollback() {
    print_warning "Initiating rollback procedure..."
    
    if [[ ! -f ".last_backup_path" ]]; then
        print_error "No backup path found - cannot rollback"
    fi
    
    local backup_path=$(cat .last_backup_path)
    
    if [[ ! -d "$backup_path" ]]; then
        print_error "Backup directory not found: $backup_path"
    fi
    
    # Stop current services
    stop_services
    
    # Restore backup
    if [[ -d "$backup_path/build" ]]; then
        rm -rf build
        cp -r "$backup_path/build" .
    fi
    
    if [[ -f "$backup_path/.env" ]]; then
        cp "$backup_path/.env" config/
    fi
    
    if [[ -d "$backup_path/data" ]]; then
        rm -rf data
        cp -r "$backup_path/data" .
    fi
    
    # Restart services with backup
    export DEPLOYMENT_MODE="manual"
    ./start_enterprise.sh &
    
    sleep 20
    
    if health_check_with_retry; then
        print_status "Rollback completed successfully"
    else
        print_error "Rollback failed - manual intervention required"
    fi
}

# Main deployment flow
main() {
    echo "=== AUTOMATED DEPLOYMENT START: $(date) ==="
    echo "=== AUTOMATED DEPLOYMENT START: $(date) ===" >> "$DEPLOYMENT_LOG"
    
    # Deployment steps
    validate_environment
    backup_current_deployment
    stop_services
    deploy
    
    # Post-deployment validation
    sleep 15  # Give services time to start
    
    if health_check_with_retry; then
        echo "=== DEPLOYMENT SUCCESS: $(date) ===" >> "$DEPLOYMENT_LOG"
        print_status "🎉 Automated deployment completed successfully!"
        print_info "Dashboard available at: http://localhost:3000"
        print_info "API available at: http://localhost:5000 or http://localhost:5001"
    else
        print_error "Post-deployment health checks failed - initiating rollback"
        rollback
    fi
}

# Handle rollback command
if [[ "$1" == "rollback" ]]; then
    rollback
    exit 0
fi

# Run main deployment
main
