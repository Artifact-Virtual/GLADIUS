#!/usr/bin/env python3
"""
SENTINEL Auto-Vectorization Daemon
===================================

Continuously monitors and vectorizes all incoming data from:
- SENTINEL (R&D research and data)
- SYNDICATE (Market and current affairs)

All data is vectorized into Hektor VDB for GLADIUS contextualization.

Author: ARTIFACT VIRTUAL
"""

import os
import sys
import json
import time
import asyncio
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import threading

# IMPORTANT: Remove SENTINEL from path to avoid local watchdog.py shadowing
_original_path = sys.path.copy()
sys.path = [p for p in sys.path if 'SENTINEL' not in p and 'services' not in p]

# Now import watchdog package
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Restore path and add gladius root
sys.path = _original_path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [VECTORIZER] %(levelname)s - %(message)s'
)
logger = logging.getLogger("SENTINEL.AutoVectorizer")

# Import Hektor memory (with SimpleVectorMemory fallback)
try:
    from GLADIUS.utils.hektor_memory import get_memory_manager
    VECTOR_MEMORY_AVAILABLE = True
except ImportError:
    try:
        from GLADIUS.utils.simple_vector_memory import get_vector_memory as get_memory_manager
        VECTOR_MEMORY_AVAILABLE = True
    except ImportError:
        VECTOR_MEMORY_AVAILABLE = False
        logger.warning("No vector memory available")


@dataclass
class VectorizationStats:
    """Track vectorization statistics"""
    total_processed: int = 0
    sentinel_docs: int = 0
    syndicate_docs: int = 0
    training_samples: int = 0
    failed: int = 0
    last_processed: Optional[datetime] = None
    start_time: datetime = None
    
    def to_dict(self) -> Dict:
        return {
            "total_processed": self.total_processed,
            "sentinel_docs": self.sentinel_docs,
            "syndicate_docs": self.syndicate_docs,
            "training_samples": self.training_samples,
            "failed": self.failed,
            "last_processed": self.last_processed.isoformat() if self.last_processed else None,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "docs_per_minute": self.total_processed / max(1, (datetime.now() - self.start_time).total_seconds() / 60) if self.start_time else 0
        }


class DataFileHandler(FileSystemEventHandler):
    """Handle file system events for auto-vectorization"""
    
    def __init__(self, vectorizer: 'AutoVectorizer'):
        self.vectorizer = vectorizer
        self._debounce: Dict[str, float] = {}
        self._debounce_seconds = 2.0
    
    def _should_process(self, path: str) -> bool:
        """Debounce rapid file changes"""
        now = time.time()
        last = self._debounce.get(path, 0)
        if now - last < self._debounce_seconds:
            return False
        self._debounce[path] = now
        return True
    
    def on_created(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            self.vectorizer.queue_file(event.src_path, "created")
    
    def on_modified(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            self.vectorizer.queue_file(event.src_path, "modified")


class AutoVectorizer:
    """
    Continuously vectorizes data from SENTINEL and SYNDICATE.
    
    Data sources:
    - SENTINEL: Research papers, insights, discoveries
    - SYNDICATE: Market data, news, current affairs
    - Training: Generated training samples
    
    All vectorized into Hektor VDB with proper categorization.
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.json', '.jsonl', '.txt', '.md', '.csv'}
    
    # Data source paths relative to gladius root
    DATA_SOURCES = {
        "sentinel": [
            "SENTINEL/data",
            "SENTINEL/research_outputs",
            "SENTINEL/logs"
        ],
        "syndicate": [
            "syndicate/data",
            "syndicate/market_data",
            "syndicate/news"
        ],
        "training": [
            "GLADIUS/training/data",
            "data/training"
        ]
    }
    
    def __init__(self, gladius_root: str = None):
        if gladius_root is None:
            gladius_root = str(Path(__file__).parent.parent.parent)
        
        self.root = Path(gladius_root)
        self.running = False
        self.stats = VectorizationStats()
        
        # File queue for processing
        self._queue: asyncio.Queue = None
        self._processed_hashes: Set[str] = set()
        self._hash_file = self.root / ".vectorizer_hashes.json"
        
        # Load previously processed hashes
        self._load_processed_hashes()
        
        # Initialize Hektor memory
        if VECTOR_MEMORY_AVAILABLE:
            self.memory = get_memory_manager()
            logger.info(f"Hektor memory initialized with stores: {list(self.memory._stores.keys())}")
        else:
            self.memory = None
            logger.error("Cannot initialize - Hektor not available")
        
        # File system observer
        self.observer = Observer()
        self.handler = DataFileHandler(self)
        
        # State file for persistence
        self.state_file = self.root / ".vectorizer_state.json"
    
    def _load_processed_hashes(self):
        """Load previously processed file hashes"""
        if self._hash_file.exists():
            try:
                data = json.loads(self._hash_file.read_text())
                self._processed_hashes = set(data.get("hashes", []))
                logger.info(f"Loaded {len(self._processed_hashes)} processed hashes")
            except Exception as e:
                logger.warning(f"Could not load hashes: {e}")
    
    def _save_processed_hashes(self):
        """Save processed file hashes"""
        try:
            # Keep only last 100k hashes to prevent unbounded growth
            hashes = list(self._processed_hashes)[-100000:]
            self._hash_file.write_text(json.dumps({
                "hashes": hashes,
                "updated": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.warning(f"Could not save hashes: {e}")
    
    def _get_content_hash(self, content: str) -> str:
        """Get hash of content for deduplication"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _determine_source(self, file_path: str) -> str:
        """Determine data source from file path"""
        path_lower = file_path.lower()
        if 'sentinel' in path_lower or 'research' in path_lower:
            return "sentinel"
        elif 'syndicate' in path_lower or 'market' in path_lower or 'news' in path_lower:
            return "syndicate"
        elif 'training' in path_lower:
            return "training"
        return "knowledge"
    
    def _get_store_name(self, source: str) -> str:
        """Map source to Hektor store name"""
        mapping = {
            "sentinel": "knowledge",
            "syndicate": "knowledge",
            "training": "training",
            "conversation": "conversations"
        }
        return mapping.get(source, "knowledge")
    
    async def vectorize_text(self, text: str, source: str, metadata: Dict = None) -> bool:
        """
        Vectorize a piece of text into Hektor.
        
        Args:
            text: Text content to vectorize
            source: Data source (sentinel, syndicate, training)
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        if not self.memory:
            return False
        
        if not text or len(text.strip()) < 10:
            return False
        
        # Check for duplicates
        content_hash = self._get_content_hash(text)
        if content_hash in self._processed_hashes:
            logger.debug(f"Skipping duplicate content: {text[:50]}...")
            return True
        
        try:
            store_name = self._get_store_name(source)
            store = self.memory.get_store(store_name)
            
            # Add to vector store
            vec_id = store.add_text(
                text=text,
                doc_type=source,
                source=metadata.get("file", "") if metadata else "",
                extra=metadata
            )
            
            # Track processed
            self._processed_hashes.add(content_hash)
            self.stats.total_processed += 1
            self.stats.last_processed = datetime.now()
            
            if source == "sentinel":
                self.stats.sentinel_docs += 1
            elif source == "syndicate":
                self.stats.syndicate_docs += 1
            elif source == "training":
                self.stats.training_samples += 1
            
            logger.debug(f"Vectorized [{source}]: {text[:50]}... -> ID {vec_id}")
            return True
            
        except Exception as e:
            logger.error(f"Vectorization failed: {e}")
            self.stats.failed += 1
            return False
    
    async def process_json_file(self, file_path: Path) -> int:
        """Process a JSON/JSONL file and vectorize contents"""
        count = 0
        source = self._determine_source(str(file_path))
        
        try:
            content = file_path.read_text()
            
            # Try JSONL first
            if file_path.suffix == '.jsonl' or '\n{' in content:
                for line in content.strip().split('\n'):
                    if line.strip():
                        try:
                            obj = json.loads(line)
                            text = self._extract_text_from_obj(obj)
                            if text and await self.vectorize_text(text, source, {"file": str(file_path)}):
                                count += 1
                        except json.JSONDecodeError:
                            continue
            else:
                # Regular JSON
                data = json.loads(content)
                if isinstance(data, list):
                    for obj in data:
                        text = self._extract_text_from_obj(obj)
                        if text and await self.vectorize_text(text, source, {"file": str(file_path)}):
                            count += 1
                elif isinstance(data, dict):
                    text = self._extract_text_from_obj(data)
                    if text and await self.vectorize_text(text, source, {"file": str(file_path)}):
                        count += 1
                        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        
        return count
    
    def _extract_text_from_obj(self, obj: Dict) -> Optional[str]:
        """Extract vectorizable text from a JSON object"""
        if not isinstance(obj, dict):
            return str(obj) if obj else None
        
        # Common text fields in order of preference
        text_fields = [
            'text', 'content', 'summary', 'description', 'message',
            'title', 'body', 'input', 'output', 'instruction',
            'content_summary', 'abstract', 'snippet'
        ]
        
        parts = []
        for field in text_fields:
            if field in obj and obj[field]:
                val = obj[field]
                if isinstance(val, str):
                    parts.append(val)
                elif isinstance(val, list):
                    parts.extend([str(v) for v in val if v])
        
        # Also check nested 'data' field
        if 'data' in obj and isinstance(obj['data'], dict):
            nested = self._extract_text_from_obj(obj['data'])
            if nested:
                parts.append(nested)
        
        return ' '.join(parts) if parts else None
    
    async def process_text_file(self, file_path: Path) -> int:
        """Process a text/markdown file"""
        count = 0
        source = self._determine_source(str(file_path))
        
        try:
            content = file_path.read_text()
            
            # Split into chunks if large
            if len(content) > 2000:
                # Split by paragraphs
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if len(para.strip()) > 50:  # Skip tiny paragraphs
                        if await self.vectorize_text(para.strip(), source, {"file": str(file_path)}):
                            count += 1
            else:
                if await self.vectorize_text(content, source, {"file": str(file_path)}):
                    count += 1
                    
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
        
        return count
    
    async def process_file(self, file_path: str) -> int:
        """Process a single file"""
        path = Path(file_path)
        
        if not path.exists():
            return 0
        
        if path.suffix not in self.SUPPORTED_EXTENSIONS:
            return 0
        
        # Skip if already fully processed (by file hash)
        try:
            file_hash = hashlib.md5(path.read_bytes()).hexdigest()
            if file_hash in self._processed_hashes:
                logger.debug(f"Skipping already processed file: {path.name}")
                return 0
            self._processed_hashes.add(file_hash)
        except:
            pass
        
        if path.suffix in {'.json', '.jsonl'}:
            return await self.process_json_file(path)
        elif path.suffix in {'.txt', '.md'}:
            return await self.process_text_file(path)
        
        return 0
    
    def queue_file(self, file_path: str, event_type: str):
        """Queue a file for processing"""
        if self._queue:
            try:
                self._queue.put_nowait((file_path, event_type))
                logger.debug(f"Queued file [{event_type}]: {file_path}")
            except asyncio.QueueFull:
                logger.warning("Queue full, dropping file")
    
    async def process_queue(self):
        """Process files from the queue"""
        while self.running:
            try:
                file_path, event_type = await asyncio.wait_for(
                    self._queue.get(), timeout=1.0
                )
                count = await self.process_file(file_path)
                if count > 0:
                    logger.info(f"Processed {count} vectors from {Path(file_path).name}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
    
    async def scan_existing_data(self):
        """Scan and vectorize all existing data files"""
        logger.info("Scanning existing data files...")
        total = 0
        
        for source, paths in self.DATA_SOURCES.items():
            for rel_path in paths:
                full_path = self.root / rel_path
                if not full_path.exists():
                    continue
                
                for ext in self.SUPPORTED_EXTENSIONS:
                    for file_path in full_path.rglob(f"*{ext}"):
                        # Skip node_modules and venv
                        if 'node_modules' in str(file_path) or 'venv' in str(file_path):
                            continue
                        
                        count = await self.process_file(str(file_path))
                        total += count
                        
                        # Yield control periodically
                        if total % 100 == 0:
                            await asyncio.sleep(0.01)
        
        logger.info(f"Initial scan complete: {total} vectors added")
        self._save_processed_hashes()
        return total
    
    def _setup_watchers(self):
        """Setup file system watchers for data directories"""
        for source, paths in self.DATA_SOURCES.items():
            for rel_path in paths:
                full_path = self.root / rel_path
                if full_path.exists():
                    self.observer.schedule(self.handler, str(full_path), recursive=True)
                    logger.info(f"Watching: {full_path}")
    
    def _save_state(self):
        """Save vectorizer state"""
        try:
            state = {
                "stats": self.stats.to_dict(),
                "updated": datetime.now().isoformat()
            }
            self.state_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            logger.warning(f"Could not save state: {e}")
    
    def _load_state(self):
        """Load vectorizer state"""
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text())
                stats = state.get("stats", {})
                self.stats.total_processed = stats.get("total_processed", 0)
                self.stats.sentinel_docs = stats.get("sentinel_docs", 0)
                self.stats.syndicate_docs = stats.get("syndicate_docs", 0)
                self.stats.training_samples = stats.get("training_samples", 0)
                logger.info(f"Loaded state: {self.stats.total_processed} previously processed")
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
    
    async def run(self):
        """Run the auto-vectorizer daemon"""
        if not self.memory:
            logger.error("Cannot run - Hektor memory not available")
            return
        
        logger.info("=" * 60)
        logger.info("SENTINEL Auto-Vectorizer Starting")
        logger.info("=" * 60)
        
        self.running = True
        self.stats.start_time = datetime.now()
        self._queue = asyncio.Queue(maxsize=1000)
        
        # Load previous state
        self._load_state()
        
        # Setup file watchers
        self._setup_watchers()
        self.observer.start()
        
        # Scan existing data first
        await self.scan_existing_data()
        
        logger.info("Auto-vectorizer running. Press Ctrl+C to stop.")
        
        # Main loop
        save_interval = 60  # Save state every 60 seconds
        last_save = time.time()
        
        try:
            while self.running:
                # Process queue
                await self.process_queue()
                
                # Periodic state save
                if time.time() - last_save > save_interval:
                    self._save_state()
                    self._save_processed_hashes()
                    last_save = time.time()
                    
                    # Log stats
                    logger.info(
                        f"Stats: {self.stats.total_processed} total | "
                        f"SENTINEL: {self.stats.sentinel_docs} | "
                        f"SYNDICATE: {self.stats.syndicate_docs} | "
                        f"Training: {self.stats.training_samples}"
                    )
                
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
        finally:
            self.running = False
            self.observer.stop()
            self.observer.join()
            self._save_state()
            self._save_processed_hashes()
            logger.info("Auto-vectorizer stopped")
    
    def get_status(self) -> Dict:
        """Get current status"""
        status = {
            "running": self.running,
            "stats": self.stats.to_dict(),
            "hektor_available": VECTOR_MEMORY_AVAILABLE
        }
        
        if self.memory:
            status["memory_stats"] = self.memory.stats_all()
        
        return status
    
    def stop(self):
        """Stop the vectorizer"""
        self.running = False


async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SENTINEL Auto-Vectorizer")
    parser.add_argument("command", choices=["start", "status", "scan"],
                       help="Command to execute")
    parser.add_argument("--root", help="GLADIUS root directory")
    
    args = parser.parse_args()
    
    vectorizer = AutoVectorizer(args.root)
    
    if args.command == "start":
        await vectorizer.run()
    elif args.command == "status":
        print(json.dumps(vectorizer.get_status(), indent=2))
    elif args.command == "scan":
        if not vectorizer.memory:
            print("ERROR: Hektor memory not available")
            return
        count = await vectorizer.scan_existing_data()
        print(f"Scanned and vectorized {count} documents")


if __name__ == "__main__":
    asyncio.run(main())
