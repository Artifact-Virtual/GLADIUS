import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import requests
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from strenum import StrEnum

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LaunchMode(StrEnum):
    SELF_HOST = "self-host"
    HOST = "host"


class RAGFlowException(Exception):
    """Custom exception for RAGFlow operations"""
    pass


class Config:
    """Configuration management"""
    def __init__(self):
        self.base_url = "http://127.0.0.1:9380"
        self.host = "127.0.0.1"
        self.port = "9382"
        self.host_api_key = ""
        self.mode = LaunchMode.SELF_HOST
        self.request_timeout = 30
        self.max_retries = 3

    def update_from_args(self, args):
        """Update config from command line arguments"""
        self.base_url = args.base_url
        self.host = args.host
        self.port = args.port
        self.mode = args.mode
        self.host_api_key = args.api_key

    def update_from_env(self, env_vars):
        """Update config from environment variables"""
        self.base_url = env_vars.get("RAGFLOW_MCP_BASE_URL", self.base_url)
        self.host = env_vars.get("RAGFLOW_MCP_HOST", self.host)
        self.port = env_vars.get("RAGFLOW_MCP_PORT", self.port)
        self.mode = env_vars.get("RAGFLOW_MCP_LAUNCH_MODE", self.mode)
        self.host_api_key = env_vars.get("RAGFLOW_MCP_HOST_API_KEY", self.host_api_key)


config = Config()


class RAGFlowConnector:
    def __init__(self, base_url: str, version: str = "v1", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.version = version
        self.api_url = f"{self.base_url}/api/{self.version}"
        self.timeout = timeout
        self.api_key: Optional[str] = None
        self.authorization_header: Dict[str, str] = {}
        
        # Setup session for connection pooling
        self.session = requests.Session()
        self.session.timeout = self.timeout

    def bind_api_key(self, api_key: str):
        """Bind API key for authentication"""
        if not api_key:
            raise RAGFlowException("API key cannot be empty")
        
        self.api_key = api_key
        self.authorization_header = {"Authorization": f"Bearer {self.api_key}"}
        self.session.headers.update(self.authorization_header)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response with proper error checking"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise RAGFlowException(f"HTTP error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise RAGFlowException(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise RAGFlowException("Invalid JSON response from server")

    def _post(self, path: str, json_data: Optional[Dict] = None, stream: bool = False, files: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request with error handling"""
        if not self.api_key:
            raise RAGFlowException("API key not configured")
        
        try:
            response = self.session.post(
                url=f"{self.api_url}{path}",
                json=json_data,
                stream=stream,
                files=files,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"POST request failed for {path}: {e}")
            raise

    def _get(self, path: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request with error handling"""
        if not self.api_key:
            raise RAGFlowException("API key not configured")
        
        try:
            response = self.session.get(
                url=f"{self.api_url}{path}",
                params=params,
                json=json_data,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"GET request failed for {path}: {e}")
            raise

    def list_datasets(self, page: int = 1, page_size: int = 1000, orderby: str = "create_time", 
                     desc: bool = True, dataset_id: Optional[str] = None, name: Optional[str] = None) -> str:
        """List datasets with improved error handling"""
        try:
            params = {
                "page": page,
                "page_size": page_size,
                "orderby": orderby,
                "desc": desc,
                "id": dataset_id,
                "name": name
            }
            # Remove None values
            params
    connector = ragflow_ctx.conn

    if MODE == LaunchMode.HOST:
        api_key = ctx.session._init_options.capabilities.experimental["headers"]["api_key"]
        if not api_key:
            raise ValueError("RAGFlow API_KEY is required.")
    else:
        api_key = HOST_API_KEY
    connector.bind_api_key(api_key)

    if name == "ragflow_retrieval":
        document_ids = arguments.get("document_ids", [])
        return connector.retrieval(dataset_ids=arguments["dataset_ids"], document_ids=document_ids, question=arguments["question"])
    raise ValueError(f"Tool not found: {name}")


async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options(experimental_capabilities={"headers": dict(request.headers)}))


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/sse") or request.url.path.startswith("/messages"):
            api_key = request.headers.get("api_key")
            if not api_key:
                return JSONResponse({"error": "Missing unauthorization header"}, status_code=401)
        return await call_next(request)


middleware = None
if MODE == LaunchMode.HOST:
    middleware = [Middleware(AuthMiddleware)]

starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
    middleware=middleware,
)


if __name__ == "__main__":
    """
    Launch example:
        self-host:
            uv run mcp/server/server.py --host=127.0.0.1 --port=9382 --base_url=http://127.0.0.1:9380 --mode=self-host --api_key=ragflow-xxxxx
        host:
            uv run mcp/server/server.py --host=127.0.0.1 --port=9382 --base_url=http://127.0.0.1:9380 --mode=host
    """

    import argparse
    import os

    import uvicorn
    from dotenv import load_dotenv

    load_dotenv()

    parser = argparse.ArgumentParser(description="RAGFlow MCP Server")
    parser.add_argument("--base_url", type=str, default="http://127.0.0.1:9380", help="api_url: http://<host_address>")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="RAGFlow MCP SERVER host")
    parser.add_argument("--port", type=str, default="9382", help="RAGFlow MCP SERVER port")
    parser.add_argument(
        "--mode",
        type=str,
        default="self-host",
        help="Launch mode options:\n"
        "  * self-host: Launches an MCP server to access a specific tenant space. The 'api_key' argument is required.\n"
        "  * host: Launches an MCP server that allows users to access their own spaces. Each request must include a header "
        "indicating the user's identification.",
    )
    parser.add_argument("--api_key", type=str, default="", help="RAGFlow MCP SERVER HOST API KEY")
    args = parser.parse_args()
    if args.mode not in ["self-host", "host"]:
        parser.error("--mode is only accept 'self-host' or 'host'")
    if args.mode == "self-host" and not args.api_key:
        parser.error("--api_key is required when --mode is 'self-host'")

    BASE_URL = os.environ.get("RAGFLOW_MCP_BASE_URL", args.base_url)
    HOST = os.environ.get("RAGFLOW_MCP_HOST", args.host)
    PORT = os.environ.get("RAGFLOW_MCP_PORT", args.port)
    MODE = os.environ.get("RAGFLOW_MCP_LAUNCH_MODE", args.mode)
    HOST_API_KEY = os.environ.get("RAGFLOW_MCP_HOST_API_KEY", args.api_key)

    print(
        r"""
__  __  ____ ____       ____  _____ ______     _______ ____
|  \/  |/ ___|  _ \     / ___|| ____|  _ \ \   / / ____|  _ \
| |\/| | |   | |_) |    \___ \|  _| | |_) \ \ / /|  _| | |_) |
| |  | | |___|  __/      ___) | |___|  _ < \ V / | |___|  _ <
|_|  |_|\____|_|        |____/|_____|_| \_\ \_/  |_____|_| \_\
    """,
        flush=True,
    )
    print(f"MCP launch mode: {MODE}", flush=True)
    print(f"MCP host: {HOST}", flush=True)
    print(f"MCP port: {PORT}", flush=True)
    print(f"MCP base_url: {BASE_URL}", flush=True)

    uvicorn.run(
        starlette_app,
        host=HOST,
        port=int(PORT),
    )
