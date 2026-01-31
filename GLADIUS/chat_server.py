#!/usr/bin/env python3
"""
GLADIUS Chat Server
===================

Real-time conversational interface for GLADIUS AI.
Supports HTTP API, WebSocket, and CLI modes.

The chat server connects to the native GLADIUS model and provides:
- Semantic memory via Hektor vector database
- Context from SENTINEL (R&D) and Syndicate (market data)
- Tool execution for actions
- Conversation history with learning

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import hashlib

# Add paths
GLADIUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))

# Try to import web server dependencies
try:
    from aiohttp import web
    import aiohttp
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

# Import GLADIUS components
try:
    from GLADIUS.speak import GladiusInterface
except ImportError:
    GladiusInterface = None

try:
    from GLADIUS.utils.hektor_memory import get_memory_manager, remember, recall
    HEKTOR_AVAILABLE = True
except ImportError:
    HEKTOR_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GLADIUS.ChatServer")


@dataclass
class ChatMessage:
    """A chat message with metadata."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str
    session_id: str
    message_id: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = hashlib.md5(
                f"{self.timestamp}{self.content[:50]}".encode()
            ).hexdigest()[:12]
        if self.metadata is None:
            self.metadata = {}


class GladiusChatServer:
    """
    GLADIUS Chat Server
    
    Provides conversational AI interface with:
    - Native GLADIUS model inference
    - Hektor vector memory for context
    - Session management
    - Learning from conversations
    """
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8765,
        use_memory: bool = True,
        max_context_messages: int = 10
    ):
        self.host = host
        self.port = port
        self.use_memory = use_memory and HEKTOR_AVAILABLE
        self.max_context_messages = max_context_messages
        
        # Sessions storage
        self.sessions: Dict[str, List[ChatMessage]] = {}
        
        # Initialize GLADIUS interface
        self.gladius: Optional[GladiusInterface] = None
        self._init_gladius()
        
        # Memory manager
        self.memory = get_memory_manager() if self.use_memory else None
        
        # Web app
        self.app = None
        if WEB_AVAILABLE:
            self._init_web_app()
        
        logger.info(f"GLADIUS Chat Server initialized")
        logger.info(f"  Memory enabled: {self.use_memory}")
        logger.info(f"  GLADIUS model: {self.gladius.model if self.gladius else 'unavailable'}")
    
    def _init_gladius(self):
        """Initialize GLADIUS interface."""
        if GladiusInterface is None:
            logger.warning("GladiusInterface not available")
            return
        
        try:
            self.gladius = GladiusInterface(verbose=False, direct=True)
            logger.info(f"GLADIUS interface ready: {self.gladius.model}")
        except Exception as e:
            logger.error(f"Failed to initialize GLADIUS: {e}")
    
    def _init_web_app(self):
        """Initialize aiohttp web application."""
        self.app = web.Application()
        self.app.router.add_post('/chat', self.handle_chat)
        self.app.router.add_get('/status', self.handle_status)
        self.app.router.add_get('/sessions/{session_id}', self.handle_get_session)
        self.app.router.add_delete('/sessions/{session_id}', self.handle_delete_session)
        self.app.router.add_get('/health', self.handle_health)
        
        # Add CORS middleware
        self.app.middlewares.append(self._cors_middleware)
    
    @web.middleware
    async def _cors_middleware(self, request, handler):
        """CORS middleware for browser access."""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    def _get_or_create_session(self, session_id: str) -> List[ChatMessage]:
        """Get or create a chat session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            logger.info(f"Created new session: {session_id}")
        return self.sessions[session_id]
    
    def _build_context(self, session_id: str, user_message: str) -> str:
        """
        Build context for GLADIUS from:
        1. Recent conversation history
        2. Relevant memories from Hektor
        3. System context (time, capabilities)
        """
        context_parts = []
        
        # Add system context
        now = datetime.now()
        context_parts.append(f"[Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}]")
        
        # Add relevant memories from Hektor
        if self.memory and self.use_memory:
            try:
                # Search across all memory stores
                memories = self.memory.recall_all(user_message, top_k=3)
                
                relevant_context = []
                for store_name, results in memories.items():
                    for r in results:
                        if r.get('score', 0) > 0.3:  # Relevance threshold
                            relevant_context.append(
                                f"[{store_name}] {r.get('text', '')[:200]}"
                            )
                
                if relevant_context:
                    context_parts.append("\n[Relevant Context:]")
                    context_parts.extend(relevant_context[:5])
                    
            except Exception as e:
                logger.warning(f"Memory retrieval failed: {e}")
        
        # Add recent conversation history
        session = self._get_or_create_session(session_id)
        if session:
            context_parts.append("\n[Recent Conversation:]")
            for msg in session[-self.max_context_messages:]:
                role = "User" if msg.role == "user" else "GLADIUS"
                context_parts.append(f"{role}: {msg.content[:200]}")
        
        return "\n".join(context_parts)
    
    async def chat(
        self,
        message: str,
        session_id: str = "default",
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        Process a chat message and return GLADIUS response.
        
        Args:
            message: User message
            session_id: Session identifier
            include_context: Include memory and history context
            
        Returns:
            Response dict with text, metadata
        """
        if not self.gladius:
            return {
                "success": False,
                "error": "GLADIUS model not available",
                "session_id": session_id
            }
        
        timestamp = datetime.now().isoformat()
        
        # Store user message
        user_msg = ChatMessage(
            role="user",
            content=message,
            timestamp=timestamp,
            session_id=session_id
        )
        session = self._get_or_create_session(session_id)
        session.append(user_msg)
        
        # Store in memory for learning
        if self.memory and self.use_memory:
            try:
                self.memory.remember(
                    message,
                    store="conversations",
                    doc_type="user_message",
                    source=session_id
                )
            except Exception as e:
                logger.warning(f"Failed to store in memory: {e}")
        
        # Build context if requested
        context = ""
        if include_context:
            context = self._build_context(session_id, message)
        
        # Query GLADIUS
        try:
            # Prepend context to the query if available
            full_query = message
            if context:
                full_query = f"Context:\n{context}\n\nUser Query: {message}"
            
            result = self.gladius.query(full_query, include_system=True)
            
            if result.get("success"):
                response_text = result.get("response", "")
                
                # Store assistant response
                assistant_msg = ChatMessage(
                    role="assistant",
                    content=response_text,
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id,
                    metadata={
                        "model": result.get("model"),
                        "latency_ms": result.get("latency_ms"),
                        "direct": result.get("direct", False)
                    }
                )
                session.append(assistant_msg)
                
                # Store response in memory for learning
                if self.memory and self.use_memory:
                    try:
                        self.memory.remember(
                            response_text,
                            store="conversations",
                            doc_type="assistant_response",
                            source=session_id
                        )
                    except Exception as e:
                        logger.warning(f"Failed to store response in memory: {e}")
                
                return {
                    "success": True,
                    "response": response_text,
                    "session_id": session_id,
                    "message_id": assistant_msg.message_id,
                    "model": result.get("model"),
                    "latency_ms": result.get("latency_ms"),
                    "direct": result.get("direct", False),
                    "timestamp": assistant_msg.timestamp
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    # HTTP Handlers
    async def handle_chat(self, request: web.Request) -> web.Response:
        """Handle POST /chat requests."""
        try:
            data = await request.json()
            message = data.get("message", "")
            session_id = data.get("session_id", "default")
            include_context = data.get("include_context", True)
            
            if not message:
                return web.json_response(
                    {"success": False, "error": "No message provided"},
                    status=400
                )
            
            result = await self.chat(message, session_id, include_context)
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"Chat handler error: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )
    
    async def handle_status(self, request: web.Request) -> web.Response:
        """Handle GET /status requests."""
        status = {
            "status": "online",
            "model": self.gladius.model if self.gladius else "unavailable",
            "memory_enabled": self.use_memory,
            "active_sessions": len(self.sessions),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.gladius:
            gladius_status = self.gladius.get_status()
            status["gladius"] = gladius_status
        
        if self.memory:
            try:
                status["memory"] = self.memory.stats_all()
            except:
                pass
        
        return web.json_response(status)
    
    async def handle_get_session(self, request: web.Request) -> web.Response:
        """Handle GET /sessions/{session_id} requests."""
        session_id = request.match_info['session_id']
        
        if session_id not in self.sessions:
            return web.json_response(
                {"error": "Session not found"},
                status=404
            )
        
        messages = [asdict(m) for m in self.sessions[session_id]]
        return web.json_response({
            "session_id": session_id,
            "messages": messages,
            "count": len(messages)
        })
    
    async def handle_delete_session(self, request: web.Request) -> web.Response:
        """Handle DELETE /sessions/{session_id} requests."""
        session_id = request.match_info['session_id']
        
        if session_id in self.sessions:
            del self.sessions[session_id]
            return web.json_response({"deleted": True, "session_id": session_id})
        
        return web.json_response(
            {"error": "Session not found"},
            status=404
        )
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Handle GET /health requests."""
        return web.json_response({"status": "healthy"})
    
    def run(self):
        """Run the chat server."""
        if not WEB_AVAILABLE:
            logger.error("aiohttp not installed. Install with: pip install aiohttp")
            return
        
        logger.info(f"Starting GLADIUS Chat Server on http://{self.host}:{self.port}")
        web.run_app(self.app, host=self.host, port=self.port)


def interactive_cli():
    """Run interactive CLI chat session."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              G L A D I U S   C H A T   C L I                  ║
║                                                               ║
║          Artifact Virtual · Native AI · Real-time             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    server = GladiusChatServer(use_memory=HEKTOR_AVAILABLE)
    session_id = f"cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Session: {session_id}")
    print(f"Memory: {'enabled' if server.use_memory else 'disabled'}")
    print(f"Model: {server.gladius.model if server.gladius else 'unavailable'}")
    print("\nType your message (or 'quit' to exit):\n")
    
    while True:
        try:
            user_input = input("\033[94mYou:\033[0m ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n\033[96mGoodbye!\033[0m")
                break
            
            # Get response
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                server.chat(user_input, session_id)
            )
            
            if result.get("success"):
                response = result.get("response", "")
                latency = result.get("latency_ms", 0)
                print(f"\n\033[92mGLADIUS:\033[0m {response}")
                print(f"\033[2m[{result.get('model', 'unknown')} | {latency:.0f}ms]\033[0m\n")
            else:
                print(f"\n\033[91mError:\033[0m {result.get('error', 'Unknown error')}\n")
                
        except KeyboardInterrupt:
            print("\n\n\033[96mInterrupted. Goodbye!\033[0m")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(description="GLADIUS Chat Server")
    parser.add_argument(
        "--mode", "-m",
        choices=["server", "cli"],
        default="cli",
        help="Run mode: server (HTTP API) or cli (interactive)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8765,
        help="Server port (default: 8765)"
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disable Hektor memory"
    )
    
    args = parser.parse_args()
    
    if args.mode == "server":
        server = GladiusChatServer(
            host=args.host,
            port=args.port,
            use_memory=not args.no_memory
        )
        server.run()
    else:
        interactive_cli()


if __name__ == "__main__":
    main()
