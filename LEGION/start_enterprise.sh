#!/bin/bash
# 
# Unified Enterprise Startup Script (Bash Version) - Production Ready
# - Ensures proper virtual environment setup
# - Installs all dependencies (Python and Node)
# - Initializes databases and config
# - Starts backend_api.py and server.py
# - Starts the React dashboard (optimized production build)
# - Supports automated deployment pipeline
#

set -e  # Exit on any error

ENTERPRISE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ENTERPRISE_DIR/venv"

# Environment variables for deployment
export NODE_ENV=${NODE_ENV:-production}
export DEPLOYMENT_MODE=${DEPLOYMENT_MODE:-manual}
export BUILD_MODE=${BUILD_MODE:-production}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
    logger "START_ENTERPRISE: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
    logger "START_ENTERPRISE WARNING: $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
    logger "START_ENTERPRISE ERROR: $1"
    exit 1
}

print_info() {
    echo -e "${BLUE}🔧${NC} $1"
    logger "START_ENTERPRISE INFO: $1"
}

# Enhanced logging for deployment pipeline
logger() {
    if [ "$DEPLOYMENT_MODE" = "automated" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> logs/deployment.log
    fi
}

# Health check function for deployment validation
health_check() {
    print_info "Running deployment health checks..."
    
    # Check if backend is responding
    local backend_health=0
    for i in {1..30}; do
        if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
            backend_health=1
            break
        fi
        sleep 2
    done
    
    if [ $backend_health -eq 0 ]; then
        print_error "Backend health check failed - deployment unsuccessful"
        return 1
    fi
    
    # Check if frontend is serving
    local frontend_health=0
    for i in {1..30}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            frontend_health=1
            break
        fi
        sleep 2
    done
    
    if [ $frontend_health -eq 0 ]; then
        print_error "Frontend health check failed - deployment unsuccessful"
        return 1
    fi
    
    print_status "All health checks passed - deployment successful"
    return 0
}

# Automated deployment mode support
deploy_production() {
    print_info "Starting automated production deployment..."
    
    # Create deployment log
    mkdir -p logs
    echo "=== DEPLOYMENT START: $(date) ===" >> logs/deployment.log
    
    # Pre-deployment checks
    if [ ! -f "package.json" ]; then
        print_error "package.json not found - cannot proceed with deployment"
    fi
    
    if [ ! -f "backend_api.py" ]; then
        print_error "backend_api.py not found - cannot proceed with deployment"
    fi
    
    # Run full deployment sequence
    setup_environment
    install_dependencies
    setup_configuration
    initialize_databases
    build_production_assets
    start_services
    
    # Validate deployment
    sleep 10
    if health_check; then
        echo "=== DEPLOYMENT SUCCESS: $(date) ===" >> logs/deployment.log
        print_status "Production deployment completed successfully"
        return 0
    else
        echo "=== DEPLOYMENT FAILED: $(date) ===" >> logs/deployment.log
        print_error "Production deployment failed health checks"
        return 1
    fi
}

# Check if we're in a virtual environment
is_venv_active() {
    if [[ -n "$VIRTUAL_ENV" ]] || [[ -n "$CONDA_DEFAULT_ENV" ]]; then
        return 0  # True - in venv
    else
        return 1  # False - not in venv
    fi
}

# Create virtual environment if it doesn't exist
create_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        echo -e "${BLUE}📦${NC} Creating virtual environment at $VENV_DIR..."
        python3 -m venv "$VENV_DIR"
        if [[ $? -eq 0 ]]; then
            print_status "Virtual environment created successfully"
        else
            print_error "Failed to create virtual environment"
            exit 1
        fi
    else
        print_status "Virtual environment already exists"
    fi
}

# Activate virtual environment and restart script
activate_venv_and_restart() {
    local venv_python="$VENV_DIR/bin/python"
    
    if [[ ! -f "$venv_python" ]]; then
        print_error "Virtual environment Python not found at $venv_python"
        exit 1
    fi
    
    echo -e "${BLUE}🔄${NC} Restarting script in virtual environment..."
    
    # Set environment variable and restart with venv Python
    export ENTERPRISE_VENV_ACTIVE=1
    exec "$venv_python" "$ENTERPRISE_DIR/start_enterprise.py" "$@"
}

# Kill processes on specific ports
kill_port_processes() {
    local port=$1
    echo "   Killing processes on port $port..."
    
    # Try different methods to kill processes on the port
    if command -v fuser &> /dev/null; then
        fuser -k "${port}/tcp" 2>/dev/null || true
    elif command -v lsof &> /dev/null; then
        local pid=$(lsof -ti tcp:$port 2>/dev/null)
        if [[ -n "$pid" ]]; then
            kill -9 $pid 2>/dev/null || true
        fi
    elif command -v netstat &> /dev/null; then
        local pid=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)
        if [[ -n "$pid" ]] && [[ "$pid" != "-" ]]; then
            kill -9 $pid 2>/dev/null || true
        fi
    fi
}

# Reusable function definitions for deployment pipeline
setup_environment() {
    print_info "Setting up environment..."
    
    # Check if we're already in the correct venv
    if [[ "$ENTERPRISE_VENV_ACTIVE" != "1" ]]; then
        if is_venv_active; then
            if [ "$DEPLOYMENT_MODE" = "automated" ]; then
                print_error "Automated deployment cannot run in existing venv"
            fi
            print_warning "Already running in a virtual environment!"
            echo "   Please deactivate the current venv and run this script again."
            echo "   Command: deactivate"
            exit 1
        else
            print_info "Setting up virtual environment..."
            create_venv
            
            if [ "$DEPLOYMENT_MODE" = "automated" ]; then
                # For automated deployment, activate without restart
                source "$VENV_DIR/bin/activate"
                export ENTERPRISE_VENV_ACTIVE=1
            else
                activate_venv_and_restart "$@"
            fi
        fi
    fi
    
    print_status "Environment setup completed"
}

install_dependencies() {
    print_info "Installing dependencies..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Run install.py for dependency installation
    local install_py="$ENTERPRISE_DIR/install.py"
    if [[ -f "$install_py" ]]; then
        print_info "Running install.py for full environment setup..."
        if python "$install_py"; then
            print_status "Dependencies installed successfully"
        else
            print_error "install.py failed"
        fi
    else
        print_error "install.py not found. Cannot install dependencies."
    fi
}

setup_configuration() {
    print_info "Setting up configuration..."
    
    # Ensure config directory exists
    mkdir -p config logs data
    
    # Copy production config if it doesn't exist
    if [[ ! -f "config/.env" ]]; then
        print_warning "Production config not found, using defaults"
    else
        print_status "Production configuration loaded"
    fi
}

initialize_databases() {
    print_info "Initializing databases..."
    
    # Initialize database schema if needed
    local init_db="$ENTERPRISE_DIR/initialize_database_schema.py"
    if [[ -f "$init_db" ]]; then
        python "$init_db"
        print_status "Database initialization completed"
    else
        print_warning "Database initialization script not found"
    fi
}

build_production_assets() {
    print_info "Building production assets..."
    
    # Build production version
    if [[ ! -d "$ENTERPRISE_DIR/build" ]] || [[ "$BUILD_MODE" = "force" ]]; then
        print_info "Building production version..."
        npm run build
        if [[ $? -ne 0 ]]; then
            print_error "Failed to build production version"
        fi
        print_status "Production build completed"
    else
        print_status "Production build already exists"
    fi
}

start_services() {
    print_info "Starting services..."
    
    # Kill processes on ports before starting
    print_info "Cleaning up ports..."
    kill_port_processes "5001"
    kill_port_processes "3000"
    
    # Start backend_api.py
    local backend_api="$ENTERPRISE_DIR/backend_api.py"
    if [[ -f "$backend_api" ]]; then
        print_info "Starting backend API..."
        python "$backend_api" &
        print_status "Backend API started"
    else
        print_warning "backend_api.py not found"
    fi
    
    # Start server.py
    local server_py="$ENTERPRISE_DIR/server.py"
    if [[ -f "$server_py" ]]; then
        print_info "Starting server..."
        python "$server_py" &
        print_status "Server started"
    else
        print_warning "server.py not found"
    fi
    
    # Start social media service
    local social_service="$ENTERPRISE_DIR/communication/social_media_service.py"
    if [[ -f "$social_service" ]]; then
        print_info "Starting social media service..."
        python "$social_service" &
        print_status "Social Media Service started"
    else
        print_warning "Social media service not found"
    fi
    
    # Start production dashboard
    print_info "Starting production dashboard..."
    npx serve -s build -l 3000 &
    if [[ $? -eq 0 ]]; then
        print_status "Production dashboard started on port 3000"
    else
        print_error "Failed to start production dashboard"
    fi
}

# Main execution
main() {
    echo
    echo "=== ENTERPRISE SYSTEM STARTUP ==="
    echo
    
    # Check if we're already in the correct venv
    if [[ "$ENTERPRISE_VENV_ACTIVE" != "1" ]]; then
        if is_venv_active; then
            print_warning "Already running in a virtual environment!"
            echo "   Please deactivate the current venv and run this script again."
            echo "   Command: deactivate"
            exit 1
        else
            print_info "Setting up virtual environment..."
            create_venv
            activate_venv_and_restart "$@"
        fi
    fi
    
    print_status "Running in Enterprise virtual environment"
    
    # Kill processes on ports 5001 and 3000 before starting
    echo -e "${RED}🔪${NC} Killing processes on ports 5001 and 3000..."
    kill_port_processes "5001"
    kill_port_processes "3000"
    print_status "Port cleanup completed"
    echo
    
    # Activate the virtual environment for the rest of the script
    source "$VENV_DIR/bin/activate"
    
    # 1. Run install.py (handles all dependency installation and dashboard setup)
    local install_py="$ENTERPRISE_DIR/install.py"
    if [[ -f "$install_py" ]]; then
        echo -e "${BLUE}🛠️${NC} Running install.py for full environment and dashboard setup..."
        if python "$install_py"; then
            print_status "Installation completed successfully"
        else
            print_error "install.py failed"
            exit 1
        fi
    else
        print_error "install.py not found. Cannot continue startup."
        exit 1
    fi
    
    # 2. Start backend_api.py
    local backend_api="$ENTERPRISE_DIR/backend_api.py"
    if [[ -f "$backend_api" ]]; then
        echo -e "${BLUE}🌐${NC} Starting backend_api.py on port 5001..."
        python "$backend_api" &
        print_status "Backend API started"
    else
        print_warning "backend_api.py not found, skipping API backend"
    fi
    
    # 3. Start server.py
    local server_py="$ENTERPRISE_DIR/server.py"
    if [[ -f "$server_py" ]]; then
        echo -e "${BLUE}${NC} Starting server.py..."
        python "$server_py" &
        print_status "Server started"
    else
        print_warning "server.py not found, skipping server"
    fi
    
    # 4. Start social media automation service (optional)
    local social_service="$ENTERPRISE_DIR/communication/social_media_service.py"
    if [[ -f "$social_service" ]]; then
        echo -e "${BLUE}📱${NC} Starting Social Media Automation Service..."
        python "$social_service" &
        print_status "Social Media Service started"
    else
        print_warning "social_media_service.py not found in communication/, skipping social media automation"
    fi
    
    # 5. Start dashboard (production build with serve)
    echo -e "${BLUE}🖥️${NC} Starting React dashboard (production build)..."
    
    # Build production version if build directory doesn't exist
    if [[ ! -d "$ENTERPRISE_DIR/build" ]]; then
        echo -e "${BLUE}�${NC} Building production version..."
        npm run build
        if [[ $? -ne 0 ]]; then
            print_error "Failed to build production version"
            exit 1
        fi
        print_status "Production build completed"
    else
        print_status "Production build already exists"
    fi
    
    # Start production server with serve
    echo -e "${BLUE}${NC} Starting production server on port 3000..."
    npx serve -s build -l 3000 &
    if [[ $? -eq 0 ]]; then
        print_status "Production dashboard started on port 3000"
    else
        print_error "Failed to start production dashboard"
        exit 1
    fi
    
    echo
    print_status "All systems started. See logs and dashboard for status."
    echo
    
    # Keep the script running and show status
    echo "Press Ctrl+C to stop all services..."
    
    # Wait for user input or signals
    trap 'echo; echo "Stopping all services..."; kill $(jobs -p) 2>/dev/null || true; exit 0' SIGINT SIGTERM
    
    # Monitor services
    while true; do
        sleep 30
        echo "$(date): Enterprise services running... (Press Ctrl+C to stop)"
    done
}

# Run main function with all arguments
main "$@"
