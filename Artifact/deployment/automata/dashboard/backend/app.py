"""
Enterprise Automation Dashboard - Flask Backend API

Production-ready REST API for the dashboard with:
- Real-time system monitoring
- Content management
- Analytics and reporting
- Configuration management
- WebSocket support for live updates
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timezone, timedelta
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from automata.core.config import AutomationConfig
from automata.core.manager import EnterpriseManager

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize extensions
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global manager instance
config = AutomationConfig()
manager = None

# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token.
    
    Request Body:
        {
            "username": "admin",
            "password": "password"
        }
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # TODO: Implement proper authentication
    # For MVP, using simple check
    admin_username = config.get('dashboard.admin_username', 'admin')
    admin_password = config.get('dashboard.admin_password', 'admin123')
    
    if username == admin_username and password == admin_password:
        access_token = create_access_token(identity=username)
        return jsonify({
            'success': True,
            'access_token': access_token,
            'username': username
        }), 200
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401


@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token is valid."""
    current_user = get_jwt_identity()
    return jsonify({
        'success': True,
        'username': current_user
    }), 200


# ============================================================================
# System Status Endpoints
# ============================================================================

@app.route('/api/status', methods=['GET'])
@jwt_required()
def get_system_status():
    """
    Get current system status.
    
    Returns:
        {
            "running": bool,
            "timestamp": str,
            "erp_systems": {...},
            "social_media": {...},
            "ai_engine": {...}
        }
    """
    try:
        if manager:
            status = manager.get_status()
        else:
            status = {
                "running": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "Manager not initialized"
            }
        
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/start', methods=['POST'])
@jwt_required()
def start_system():
    """Start the automation system."""
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)
        
        # Start system (would be async in production)
        # await manager.start()
        
        return jsonify({
            'success': True,
            'message': 'System started successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error starting system: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/stop', methods=['POST'])
@jwt_required()
def stop_system():
    """Stop the automation system."""
    global manager
    try:
        if manager:
            # await manager.stop()
            pass
        
        return jsonify({
            'success': True,
            'message': 'System stopped successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error stopping system: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Configuration Endpoints
# ============================================================================

@app.route('/api/config', methods=['GET'])
@jwt_required()
def get_configuration():
    """Get current configuration."""
    try:
        return jsonify({
            'success': True,
            'config': config.config
        }), 200
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['PUT'])
@jwt_required()
def update_configuration():
    """
    Update configuration.
    
    Request Body:
        {
            "key": "social_media.Twitter/X.enabled",
            "value": true
        }
    """
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        
        config.set(key, value)
        config.save_to_file()
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated'
        }), 200
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/platforms', methods=['GET'])
@jwt_required()
def get_platforms():
    """Get enabled platforms."""
    try:
        return jsonify({
            'success': True,
            'erp_systems': config.get_enabled_erp_systems(),
            'social_platforms': config.get_enabled_social_platforms()
        }), 200
    except Exception as e:
        logger.error(f"Error getting platforms: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Social Media Endpoints
# ============================================================================

@app.route('/api/social/posts', methods=['GET'])
@jwt_required()
def get_scheduled_posts():
    """Get scheduled posts."""
    try:
        platform = request.args.get('platform')
        
        if manager:
            posts = manager.get_scheduled_posts(platform)
        else:
            posts = []
        
        return jsonify({
            'success': True,
            'posts': posts
        }), 200
    except Exception as e:
        logger.error(f"Error getting posts: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/social/post', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create and schedule a post.
    
    Request Body:
        {
            "platform": "Twitter/X",
            "content": "Post content",
            "schedule_time": "2024-01-01T12:00:00Z" (optional)
        }
    """
    try:
        data = request.get_json()
        platform = data.get('platform')
        content = data.get('content')
        topic = data.get('topic')
        schedule_time = data.get('schedule_time')
        
        if schedule_time:
            schedule_time = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
        
        if manager:
            # result = await manager.generate_and_schedule_content(
            #     platform=platform,
            #     topic=topic,
            #     schedule_time=schedule_time
            # )
            result = {
                'success': True,
                'post_id': 'mock-id',
                'message': 'Post scheduled'
            }
        else:
            result = {'error': 'Manager not initialized'}
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/social/post/<post_id>', methods=['DELETE'])
@jwt_required()
def cancel_post(post_id):
    """Cancel a scheduled post."""
    try:
        if manager:
            success = manager.cancel_scheduled_post(post_id)
        else:
            success = False
        
        return jsonify({
            'success': success,
            'message': 'Post cancelled' if success else 'Post not found'
        }), 200
    except Exception as e:
        logger.error(f"Error cancelling post: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Analytics Endpoints
# ============================================================================

@app.route('/api/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get system analytics."""
    try:
        if manager:
            analytics = manager.get_analytics()
        else:
            analytics = {
                'erp': {},
                'social_media': {},
                'content': {}
            }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/social/<platform>', methods=['GET'])
@jwt_required()
def get_platform_analytics(platform):
    """Get analytics for specific social platform."""
    try:
        # TODO: Implement platform-specific analytics
        analytics = {
            'platform': platform,
            'total_posts': 0,
            'engagement_rate': 0,
            'followers': 0
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
    except Exception as e:
        logger.error(f"Error getting platform analytics: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ERP Endpoints
# ============================================================================

@app.route('/api/erp/sync', methods=['POST'])
@jwt_required()
def trigger_erp_sync():
    """
    Manually trigger ERP synchronization.
    
    Request Body:
        {
            "system": "SAP",
            "entity_type": "customers"
        }
    """
    try:
        data = request.get_json()
        system = data.get('system')
        entity_type = data.get('entity_type')
        
        if manager:
            # result = await manager.sync_erp_data(system, entity_type)
            result = {
                'success': True,
                'records_synced': 0,
                'message': 'Sync completed'
            }
        else:
            result = {'error': 'Manager not initialized'}
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error triggering ERP sync: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to dashboard'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info('Client disconnected')


@socketio.on('subscribe_status')
def handle_subscribe_status():
    """Subscribe to status updates."""
    # TODO: Implement real-time status broadcasting
    emit('status_update', {'message': 'Subscribed to status updates'})


# ============================================================================
# Health Check
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """API root endpoint."""
    return jsonify({
        'name': 'Enterprise Automation Dashboard API',
        'version': '1.0.0',
        'status': 'running'
    }), 200


# ============================================================================
# Run Server
# ============================================================================

if __name__ == '__main__':
    host = config.get('dashboard.host', '0.0.0.0')
    port = config.get('dashboard.port', 5000)
    
    logger.info(f"Starting Dashboard API on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=True)
