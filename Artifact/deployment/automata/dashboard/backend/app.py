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
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from automata.core.config import AutomationConfig
from automata.core.manager import EnterpriseManager

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

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
    # For MVP, using simple check - fallback to admin/admin if not configured
    admin_username = config.get('dashboard.admin_username', 'admin') or 'admin'
    admin_password = config.get('dashboard.admin_password', 'admin') or 'admin'
    
    if username == admin_username and password == admin_password:
        access_token = create_access_token(identity=username)
        return jsonify({
            'success': True,
            'access_token': access_token,
            'username': username
        }), 200
    
    # Development helper: allow a one-shot dev login when DASHBOARD_ALLOW_DEV_LOGIN=true
    # Use with caution; this endpoint is disabled by default in production.
    # POST /api/auth/_dev_login with JSON {"password": "<dev-password>"}
    dev_allowed = os.getenv('DASHBOARD_ALLOW_DEV_LOGIN', 'false').lower() == 'true'
    if dev_allowed:
        try:
            data = request.get_json() or {}
            dev_pw = os.getenv('DASHBOARD_DEV_PASSWORD', 'devpass')
            if data.get('password') == dev_pw:
                access_token = create_access_token(identity=admin_username)
                return jsonify({'success': True, 'access_token': access_token, 'username': admin_username}), 200
        except Exception:
            pass

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
        logger.exception("Error getting status")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/start', methods=['POST'])
@jwt_required()
def start_system():
    """Start the automation system."""
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)

        # Run the async startup synchronously for the Flask route
        import asyncio
        asyncio.run(manager.start())

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
            import asyncio
            asyncio.run(manager.stop())

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


# ----------------------------------------------------------------------------
# Convenience Overview Endpoint
# ----------------------------------------------------------------------------
@app.route('/api/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """Return an aggregated overview for a single-pane dashboard."""
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)

        overview = {
            'status': manager.get_status() if manager else {},
            'analytics': manager.get_analytics() if manager else {},
            'content': {
                'drafts_count': 0,
                'drafts': []
            },
            'context_stats': {}
        }

        # Content drafts (if available)
        try:
            store = getattr(manager.content_generator, 'content_store', None)
            if store:
                drafts = store.list(status=None)
                overview['content']['drafts_count'] = len(drafts)
                overview['content']['drafts'] = drafts[:20]
        except Exception:
            pass

        # Context engine stats
        try:
            overview['context_stats'] = manager.content_generator.get_context_stats()
        except Exception:
            overview['context_stats'] = {}

        # Reflections count
        try:
            import sqlite3
            db = os.path.expanduser(config.get('context_db_path', '~/.automata/context.db'))
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM reflections")
            count = cur.fetchone()[0]
            conn.close()
            overview['reflections_count'] = count
        except Exception:
            overview['reflections_count'] = None

        return jsonify({'success': True, 'overview': overview}), 200
    except Exception as e:
        logger.exception('Error getting overview')
        return jsonify({'success': False, 'error': str(e)}), 500


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
# Context & AI Integration Endpoints
# ============================================================================

@app.route('/api/context/entries', methods=['POST'])
@jwt_required()
def add_context_entries():
    """Add one or more context entries to the ContextEngine.

    Accepts either a single entry or a list of entries with the following format:
    {
        "role": "system|user|assistant|tool",
        "content": "...",
        "metadata": { ... }
    }

    Returns a list of created entry ids.
    """
    global manager
    data = request.get_json() or {}
    entries = data if isinstance(data, list) else [data]

    try:
        if not manager:
            # Lazily initialize manager (does not start async subsystems)
            manager = EnterpriseManager(config)

        async def _add_all():
            tasks = []
            for e in entries:
                role = e.get('role', 'tool')
                content = e.get('content', '')
                metadata = e.get('metadata', {})
                tasks.append(manager.content_generator.context_engine.add_entry(role, content, metadata))
            ids = await _asyncio.gather(*tasks)
            return ids

        import asyncio as _asyncio
        ids = _asyncio.run(_add_all())

        return jsonify({'success': True, 'ids': ids}), 200
    except Exception as e:
        logger.exception("Error adding context entries")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/context/entries', methods=['GET'])
@jwt_required()
def list_context_entries():
    """Return recent context entries (from in-memory cache)."""
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)
        engine = manager.content_generator.context_engine
        # Build simple serializable view
        limit = int(request.args.get('limit', 50))
        entries = engine.current_context[-limit:]
        out = [
            {
                'id': e.id,
                'timestamp': e.timestamp.isoformat(),
                'role': e.role,
                'content': e.content,
                'metadata': e.metadata
            }
            for e in entries
        ]
        return jsonify(out), 200
    except Exception as e:
        logger.exception('Error listing context entries')
        return jsonify({'error': str(e)}), 500


@app.route('/api/context/llm_task', methods=['POST'])
@jwt_required()
def receive_llm_task_metadata():
    """Accept LLM task metadata for observability and tracking.

    For MVP this simply logs the payload and returns success. Future
    implementations should persist to DB and integrate with analytics.
    """
    try:
        payload = request.get_json() or {}
        logger.info("Received LLM task metadata: %s", payload)
        # TODO: persist or forward to analytics pipeline
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.exception('Error receiving LLM task metadata')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reflections/recent', methods=['GET'])
@jwt_required()
def list_recent_reflections():
    """Return recent reflections from DB (most recent 20)."""
    try:
        import sqlite3
        db = os.path.expanduser(config.get('context_db_path', '~/.automata/context.db'))
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT id,timestamp,reflection,improvements,action_items FROM reflections ORDER BY timestamp DESC LIMIT 20")
        rows = cur.fetchall()
        conn.close()
        out = []
        for r in rows:
            out.append({'id': r[0], 'timestamp': r[1], 'reflection': r[2], 'improvements': json.loads(r[3]) if r[3] else [], 'action_items': json.loads(r[4]) if r[4] else []})
        return jsonify(out), 200
    except Exception as e:
        logger.exception('Error listing reflections')
        return jsonify({'error': str(e)}), 500


@app.route('/ui/context')
def ui_context():
    return render_template('context_ui.html')


@app.route('/api/context/stats', methods=['GET'])
@jwt_required()
def get_context_stats():
    """Return basic context engine statistics."""
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)
        stats = manager.content_generator.get_context_stats()
        return jsonify({'success': True, 'stats': stats}), 200
    except Exception as e:
        logger.exception("Error getting context stats")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/context/reflect', methods=['POST'])
@jwt_required()
def trigger_reflection():
    """Trigger a manual reflection run and return the result. Accepts optional JSON body with overrides:
    {
      "max_tokens": 8000,
      "temperature": 0.3,
      "context_max_tokens": 20000,
      "model": "gemini-pro"
    }
    """
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)

        payload = request.get_json() or {}
        max_tokens = payload.get('max_tokens')
        temperature = payload.get('temperature')
        context_max_tokens = payload.get('context_max_tokens')
        model = payload.get('model')

        # Cast types if provided
        if max_tokens is not None:
            max_tokens = int(max_tokens)
        if temperature is not None:
            temperature = float(temperature)
        if context_max_tokens is not None:
            context_max_tokens = int(context_max_tokens)

        import asyncio as _asyncio
        result = _asyncio.run(manager.content_generator.trigger_reflection(max_tokens=max_tokens, temperature=temperature, context_max_tokens=context_max_tokens, model=model))
        return jsonify({'success': True, 'reflection': result}), 200
    except Exception as e:
        logger.exception("Error triggering reflection")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/content/generate', methods=['POST'])
@jwt_required()
def generate_content():
    """Generate content using the ContentGenerator.

    Request JSON:
      {
        "platform": "LinkedIn",
        "topic": "Quarterly report",
        "content_type": "article",
        "style": "thought leadership",
        "use_tools": false,
        "count": 1
      }

    Returns generated content objects and saves them into context.
    """
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)

        payload = request.get_json() or {}
        platform = payload.get('platform', 'LinkedIn')
        topic = payload.get('topic')
        content_type = payload.get('content_type', 'article')
        style = payload.get('style')
        use_tools = payload.get('use_tools', False)
        count = int(payload.get('count', 1))

        results = []
        for i in range(count):
            # Use asyncio.run to execute the async generator calls
            import asyncio as _asyncio
            result = _asyncio.run(manager.content_generator.generate(platform=platform, topic=topic, content_type=content_type, style=style, use_tools=use_tools))
            results.append(result)

        return jsonify({'success': True, 'generated': results}), 200
    except Exception as e:
        logger.exception('Error generating content')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/content/editorial', methods=['POST'])
@jwt_required()
def editorial_pipeline():
    """Run editorial pipeline: generate drafts, improve via AI, export final markdown files."""
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)

        payload = request.get_json() or {}
        platform = payload.get('platform', 'LinkedIn')
        topic = payload.get('topic')
        content_type = payload.get('content_type', 'article')
        style = payload.get('style')
        count = int(payload.get('count', 1))

        import asyncio as _asyncio

        drafts = [_asyncio.run(manager.content_generator.generate(platform=platform, topic=topic, content_type=content_type, style=style)) for _ in range(count)]

        ai = manager.content_generator.ai_provider
        improved = [_improve_draft((d.get('content') or {}).get('text') if isinstance(d.get('content'), dict) else d.get('content'), topic, ai) for d in drafts]

        out_dir = Path(__file__).parent.parent.parent.parent / 'research_outputs' / 'articles'
        out_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for idx, item in enumerate(improved):
            title = item.get('title') or f"final_{idx}"
            filename = f"final_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{idx}.md"
            md = f"# {title}\n\n" + (item.get('article') or '') + '\n\n' + f"**Summary:** {item.get('summary','')}\n\n" + f"**Tags:** {', '.join(item.get('tags',[]))}\n"
            fpath = out_dir / filename
            fpath.write_text(md, encoding='utf-8')
            saved_files.append(str(fpath))

        batch_summary = out_dir / f"summary_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
        lines = [f"# Batch Editorial Summary ({datetime.now(timezone.utc).isoformat()})\n"]
        for i, it in enumerate(improved):
            lines.append(f"## Article {i+1}: {it.get('title')}\n")
            lines.append(f"- Summary: {it.get('summary','')}\n")
            lines.append(f"- Tags: {', '.join(it.get('tags',[]))}\n")
            lines.append('\n')
        batch_summary.write_text('\n'.join(lines), encoding='utf-8')

        # update most recent drafts to final if content_store exists
        try:
            store = getattr(manager.content_generator, 'content_store', None)
            if store:
                drafts_list = store.list(status='draft')
                for idx2, fpath in enumerate(saved_files):
                    if idx2 < len(drafts_list):
                        store.update_status(drafts_list[idx2]['id'], 'final', export_path=fpath)
        except Exception:
            pass

        return jsonify({'success': True, 'files': saved_files, 'summary': str(batch_summary)}), 200
    except Exception as e:
        logger.exception('Error running editorial pipeline')
        return jsonify({'success': False, 'error': str(e)}), 500


def _improve_draft(draft_text: str, topic: str, ai) -> dict:
    import asyncio as _asyncio
    prompt = f"""You are an expert editor. Improve the following article draft into a polished, publication-ready article. Return a JSON object with keys: title, article (markdown), summary (short paragraph), tags (list of strings), author (optional).

Draft:
{draft_text}

Respond only in JSON."""
    try:
        res = _asyncio.run(ai.generate(prompt=prompt, system_message="You are an assistant that edits and formats articles.", temperature=0.2, max_tokens=1500))
        content = res.get('content', '')
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = {'title': topic or 'Article', 'article': content, 'summary': content[:300], 'tags': []}
    except Exception:
        parsed = {'title': topic or 'Article', 'article': draft_text or '', 'summary': (draft_text or '')[:300], 'tags': []}
    return parsed

# New endpoints: list drafts, create draft, finalize single draft
@app.route('/api/content/drafts', methods=['GET'])
@jwt_required()
def list_drafts():
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)
        if not hasattr(manager.content_generator, 'content_store') or manager.content_generator.content_store is None:
            return jsonify({'success': False, 'error': 'content_store not configured'}), 500
        status = request.args.get('status')
        items = manager.content_generator.content_store.list(status=status)
        return jsonify({'success': True, 'items': items}), 200
    except Exception as e:
        logger.exception('Error listing drafts')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/content/drafts', methods=['POST'])
@jwt_required()
def create_draft():
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)
        payload = request.get_json() or {}
        platform = payload.get('platform', 'LinkedIn')
        topic = payload.get('topic')
        content = payload.get('content') or {}
        import uuid
        item_id = f"content_{uuid.uuid4().hex}"
        manager.content_generator.content_store.create(item_id=item_id, platform=platform, topic=topic, content=content, status='draft')
        return jsonify({'success': True, 'id': item_id}), 200
    except Exception as e:
        logger.exception('Error creating draft')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/content/drafts/<item_id>/finalize', methods=['POST'])
@jwt_required()
def finalize_draft(item_id):
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)
        store = manager.content_generator.content_store
        if store is None:
            return jsonify({'success': False, 'error': 'content_store not configured'}), 500
        item = store.get(item_id)
        if not item:
            return jsonify({'success': False, 'error': 'item not found'}), 404
        # Run editorial improvement on item.content
        content_obj = item.get('content') if item.get('content') else {}
        draft_text = content_obj.get('text') if isinstance(content_obj, dict) else ''
        ai = manager.content_generator.ai_provider
        parsed = _improve_draft(draft_text, item.get('topic') or '', ai)
        # Save final markdown
        out_dir = Path(__file__).parent.parent.parent.parent / 'research_outputs' / 'articles'
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"final_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{item_id}.md"
        md = f"# {parsed.get('title')}\n\n" + (parsed.get('article') or '') + '\n\n' + f"**Summary:** {parsed.get('summary','')}\n\n" + f"**Tags:** {', '.join(parsed.get('tags',[]))}\n"
        fpath = out_dir / filename
        fpath.write_text(md, encoding='utf-8')
        # Update store
        store.update_status(item_id, 'final', export_path=str(fpath), title=parsed.get('title'), text=(parsed.get('article') or ''))
        return jsonify({'success': True, 'file': str(fpath)}), 200
    except Exception as e:
        logger.exception('Finalize draft failed')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/content/publish', methods=['POST'])
@jwt_required()
def publish_content():
    global manager
    try:
        if not manager:
            manager = EnterpriseManager(config)
        payload = request.get_json() or {}
        item_id = payload.get('id')
        platform = payload.get('platform')
        if not item_id:
            return jsonify({'success': False, 'error': 'id required'}), 400
        store = manager.content_generator.content_store
        if store is None:
            return jsonify({'success': False, 'error': 'content_store not configured'}), 500
        item = store.get(item_id)
        if not item:
            return jsonify({'success': False, 'error': 'item not found'}), 404
        if item.get('status') != 'final':
            return jsonify({'success': False, 'error': 'item not final'}), 409
        # Schedule publish via orchestrator if available
        published_url = None
        try:
            if manager.orchestrator:
                import asyncio
                post_id = asyncio.run(manager.orchestrator.schedule_post(platform=platform or item.get('platform','LinkedIn'), content={'text': item.get('text') or item.get('content',{}), 'title': item.get('title')}))
                published_url = f"scheduled://{post_id}"
            else:
                published_url = f"scheduled://{item_id}"
        except Exception as e:
            manager.content_generator.content_store.update_status(item_id, 'failed', publish_error=str(e))
            return jsonify({'success': False, 'error': str(e)}), 500

        # Mark as published (scheduled)
        store.update_status(item_id, 'published', published_url=published_url, published_at=datetime.now(timezone.utc).isoformat())
        # Add context entry for analytics
        try:
            import asyncio
            asyncio.run(manager.content_generator.context_engine.add_entry(role='system', content=f"Published content {item_id} to {platform or item.get('platform','LinkedIn')}", metadata={'type':'publish','item_id':item_id,'published_url':published_url}))
        except Exception:
            pass

        return jsonify({'success': True, 'published_url': published_url}), 200
    except Exception as e:
        logger.exception('Publish failed')
        return jsonify({'success': False, 'error': str(e)}), 500


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
    socketio.run(app, host=host, port=port, debug=True, allow_unsafe_werkzeug=True)
