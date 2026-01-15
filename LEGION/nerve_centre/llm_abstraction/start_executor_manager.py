#!/usr/bin/env python3
"""
Matrix Executor Manager Startup Script
Starts the code execution service for the matrix subsystem
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path

# Add the matrix executor path to Python path
matrix_path = Path(__file__).parent.parent / 'matrix' / 'executor_manager'
sys.path.insert(0, str(matrix_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExecutorManagerService:
    """Service wrapper for the matrix executor manager"""
    
    def __init__(self):
        self.app = None
        self.server = None
        self.running = False
        
    async def start(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the executor manager service"""
        try:
            # Import the FastAPI app from matrix executor manager
            from main import app
            
            import uvicorn
            
            logger.info(f"Starting Matrix Executor Manager on {host}:{port}")
            
            # Configure uvicorn
            config = uvicorn.Config(
                app=app,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                loop="asyncio"
            )
            
            self.server = uvicorn.Server(config)
            self.running = True
            
            # Start the server
            await self.server.serve()
            
        except Exception as e:
            logger.error(f"Failed to start executor manager: {e}")
            self.running = False
            raise
    
    async def stop(self):
        """Stop the executor manager service"""
        if self.server:
            logger.info("Stopping Matrix Executor Manager...")
            self.server.should_exit = True
            self.running = False
            logger.info("Matrix Executor Manager stopped")
    
    def is_running(self) -> bool:
        """Check if the service is running"""
        return self.running


# Global service instance
executor_service = ExecutorManagerService()


async def main():
    """Main startup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Matrix Executor Manager Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(executor_service.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("="*50)
        logger.info("Matrix Executor Manager Service")
        logger.info("="*50)
        logger.info(f"Host: {args.host}")
        logger.info(f"Port: {args.port}")
        logger.info(f"Log Level: {args.log_level}")
        logger.info("="*50)
        
        # Start the service
        await executor_service.start(args.host, args.port)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Service error: {e}")
        return 1
    finally:
        await executor_service.stop()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
