"""
SENTINEL Comprehensive Health Monitor
=====================================

Full system health checks including:
- Database connectivity and integrity
- File system permissions
- Authentication validation
- API connectivity
- Memory/CPU usage
- Network availability
- Service status
- Regression detection

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import time
import asyncio
import logging
import sqlite3
import hashlib
import smtplib
import socket
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SENTINEL.HealthMonitor")


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a single health check"""
    name: str
    status: HealthStatus
    message: str
    latency_ms: float
    details: Dict[str, Any]
    timestamp: datetime


@dataclass
class SystemHealthReport:
    """Complete system health report"""
    overall_status: HealthStatus
    checks: List[HealthCheckResult]
    summary: Dict[str, int]
    timestamp: datetime
    duration_ms: float


class HealthMonitor:
    """
    Comprehensive health monitoring for SENTINEL and GLADIUS systems.
    
    Checks:
    - Database: SQLite connectivity, schema integrity, write permissions
    - Authentication: SMTP, API keys, tokens
    - Network: External APIs, rate limits
    - System: Memory, CPU, disk
    - Services: SENTINEL daemons, GLADIUS router
    - Regression: Compare against baseline metrics
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_path = Path(__file__).parent.parent
        self.gladius_root = self.base_path.parent
        
        # Paths to check
        self.db_paths = [
            self.base_path / "services" / "learning_state.db",
            self.gladius_root / "Artifact" / "syndicate" / "data" / "syndicate.db",
            self.gladius_root / "LEGION" / "legion" / "data" / "enterprise_operations.db",
        ]
        
        # Load config
        self.config = self._load_config()
        
        # Health history for regression detection
        self.history_db = self.base_path / "services" / "health_history.db"
        self._init_history_db()
        
        logger.info("HealthMonitor initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load health check configuration"""
        default_config = {
            "thresholds": {
                "memory_percent_max": 85.0,
                "cpu_percent_max": 90.0,
                "disk_percent_max": 90.0,
                "api_timeout_seconds": 10,
                "db_query_timeout_seconds": 5,
                "latency_warning_ms": 1000,
                "latency_critical_ms": 5000
            },
            "checks_enabled": {
                "database": True,
                "authentication": True,
                "network": True,
                "system": True,
                "services": True,
                "regression": True
            },
            "endpoints": {
                "ollama": "http://localhost:11434/api/tags",
                "arxiv": "https://export.arxiv.org/api/query?search_query=all:test&max_results=1",
                "github": "https://api.github.com/rate_limit"
            }
        }
        
        config_path = self.base_path / "services" / "config" / "health_config.json"
        try:
            if config_path.exists():
                with open(config_path) as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except Exception as e:
            logger.warning(f"Could not load health config: {e}")
        
        return default_config
    
    def _init_history_db(self):
        """Initialize health history database"""
        try:
            conn = sqlite3.connect(self.history_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    overall_status TEXT,
                    healthy_count INTEGER,
                    degraded_count INTEGER,
                    unhealthy_count INTEGER,
                    duration_ms REAL,
                    details TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT UNIQUE,
                    baseline_value REAL,
                    threshold_warning REAL,
                    threshold_critical REAL,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to init health history DB: {e}")
    
    # ==================== DATABASE CHECKS ====================
    
    async def check_database(self, db_path: Path) -> HealthCheckResult:
        """Check database connectivity and integrity"""
        start = time.time()
        name = f"db_{db_path.stem}"
        
        try:
            if not db_path.exists():
                return HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Database not found: {db_path}",
                    latency_ms=(time.time() - start) * 1000,
                    details={"path": str(db_path), "exists": False},
                    timestamp=datetime.now()
                )
            
            # Test connection
            conn = sqlite3.connect(db_path, timeout=self.config["thresholds"]["db_query_timeout_seconds"])
            cursor = conn.cursor()
            
            # Test read
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Test write (to temp table)
            cursor.execute("CREATE TABLE IF NOT EXISTS _health_check (id INTEGER PRIMARY KEY, ts TEXT)")
            cursor.execute("INSERT OR REPLACE INTO _health_check (id, ts) VALUES (1, ?)", 
                          (datetime.now().isoformat(),))
            conn.commit()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            # Get size
            file_size = db_path.stat().st_size
            
            conn.close()
            
            latency = (time.time() - start) * 1000
            
            if integrity != "ok":
                return HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Integrity check failed: {integrity}",
                    latency_ms=latency,
                    details={"tables": tables, "integrity": integrity, "size_bytes": file_size},
                    timestamp=datetime.now()
                )
            
            status = HealthStatus.HEALTHY
            if latency > self.config["thresholds"]["latency_warning_ms"]:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                name=name,
                status=status,
                message=f"Database healthy: {len(tables)} tables, {file_size/1024:.1f}KB",
                latency_ms=latency,
                details={"tables": tables, "integrity": integrity, "size_bytes": file_size},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database error: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    async def check_all_databases(self) -> List[HealthCheckResult]:
        """Check all configured databases"""
        results = []
        for db_path in self.db_paths:
            result = await self.check_database(db_path)
            results.append(result)
        return results
    
    # ==================== AUTHENTICATION CHECKS ====================
    
    async def check_smtp_auth(self) -> HealthCheckResult:
        """Check SMTP authentication"""
        start = time.time()
        
        try:
            from dotenv import load_dotenv
            load_dotenv(self.gladius_root / ".env")
            
            host = os.getenv("SMTP_HOST", "smtp.hostinger.com")
            port = int(os.getenv("SMTP_PORT", "465"))
            user = os.getenv("SMTP_USER", "")
            password = os.getenv("SMTP_PASSWORD", "")
            use_ssl = os.getenv("SMTP_SSL", "true").lower() == "true"
            
            if not user or not password:
                return HealthCheckResult(
                    name="auth_smtp",
                    status=HealthStatus.UNHEALTHY,
                    message="SMTP credentials not configured",
                    latency_ms=(time.time() - start) * 1000,
                    details={"host": host, "port": port},
                    timestamp=datetime.now()
                )
            
            # Test connection
            if use_ssl:
                server = smtplib.SMTP_SSL(host, port, timeout=10)
            else:
                server = smtplib.SMTP(host, port, timeout=10)
                server.starttls()
            
            server.login(user, password)
            server.quit()
            
            latency = (time.time() - start) * 1000
            
            return HealthCheckResult(
                name="auth_smtp",
                status=HealthStatus.HEALTHY,
                message=f"SMTP authenticated: {user}",
                latency_ms=latency,
                details={"host": host, "port": port, "user": user},
                timestamp=datetime.now()
            )
            
        except smtplib.SMTPAuthenticationError as e:
            return HealthCheckResult(
                name="auth_smtp",
                status=HealthStatus.UNHEALTHY,
                message=f"SMTP auth failed: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
                details={"error": str(e)},
                timestamp=datetime.now()
            )
        except Exception as e:
            return HealthCheckResult(
                name="auth_smtp",
                status=HealthStatus.DEGRADED,
                message=f"SMTP connection error: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    async def check_api_keys(self) -> List[HealthCheckResult]:
        """Check API key validity"""
        results = []
        
        from dotenv import load_dotenv
        load_dotenv(self.gladius_root / ".env")
        
        # Check Discord
        discord_token = os.getenv("DISCORD_BOT_TOKEN", "")
        if discord_token:
            start = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bot {discord_token}"}
                    async with session.get("https://discord.com/api/v10/users/@me", 
                                          headers=headers, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results.append(HealthCheckResult(
                                name="auth_discord",
                                status=HealthStatus.HEALTHY,
                                message=f"Discord bot: {data.get('username', 'unknown')}",
                                latency_ms=(time.time() - start) * 1000,
                                details={"bot_id": data.get("id"), "username": data.get("username")},
                                timestamp=datetime.now()
                            ))
                        else:
                            results.append(HealthCheckResult(
                                name="auth_discord",
                                status=HealthStatus.UNHEALTHY,
                                message=f"Discord auth failed: {resp.status}",
                                latency_ms=(time.time() - start) * 1000,
                                details={"status": resp.status},
                                timestamp=datetime.now()
                            ))
            except Exception as e:
                results.append(HealthCheckResult(
                    name="auth_discord",
                    status=HealthStatus.DEGRADED,
                    message=f"Discord check error: {str(e)}",
                    latency_ms=(time.time() - start) * 1000,
                    details={"error": str(e)},
                    timestamp=datetime.now()
                ))
        
        # Check GitHub (rate limit endpoint)
        start = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.github.com/rate_limit", timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        core_remaining = data.get("rate", {}).get("remaining", 0)
                        status = HealthStatus.HEALTHY if core_remaining > 10 else HealthStatus.DEGRADED
                        results.append(HealthCheckResult(
                            name="api_github",
                            status=status,
                            message=f"GitHub API: {core_remaining} requests remaining",
                            latency_ms=(time.time() - start) * 1000,
                            details={"rate_limit": data.get("rate", {})},
                            timestamp=datetime.now()
                        ))
        except Exception as e:
            results.append(HealthCheckResult(
                name="api_github",
                status=HealthStatus.DEGRADED,
                message=f"GitHub check error: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
                details={"error": str(e)},
                timestamp=datetime.now()
            ))
        
        return results
    
    # ==================== NETWORK CHECKS ====================
    
    async def check_endpoint(self, name: str, url: str) -> HealthCheckResult:
        """Check network endpoint availability"""
        start = time.time()
        
        try:
            timeout = aiohttp.ClientTimeout(
                total=self.config["thresholds"]["api_timeout_seconds"]
            )
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    latency = (time.time() - start) * 1000
                    
                    if resp.status == 200:
                        status = HealthStatus.HEALTHY
                        if latency > self.config["thresholds"]["latency_warning_ms"]:
                            status = HealthStatus.DEGRADED
                        return HealthCheckResult(
                            name=f"net_{name}",
                            status=status,
                            message=f"{name} reachable ({latency:.0f}ms)",
                            latency_ms=latency,
                            details={"url": url, "status_code": resp.status},
                            timestamp=datetime.now()
                        )
                    else:
                        return HealthCheckResult(
                            name=f"net_{name}",
                            status=HealthStatus.DEGRADED,
                            message=f"{name} returned {resp.status}",
                            latency_ms=latency,
                            details={"url": url, "status_code": resp.status},
                            timestamp=datetime.now()
                        )
                        
        except asyncio.TimeoutError:
            return HealthCheckResult(
                name=f"net_{name}",
                status=HealthStatus.UNHEALTHY,
                message=f"{name} timeout",
                latency_ms=(time.time() - start) * 1000,
                details={"url": url, "error": "timeout"},
                timestamp=datetime.now()
            )
        except Exception as e:
            return HealthCheckResult(
                name=f"net_{name}",
                status=HealthStatus.UNHEALTHY,
                message=f"{name} error: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
                details={"url": url, "error": str(e)},
                timestamp=datetime.now()
            )
    
    async def check_all_endpoints(self) -> List[HealthCheckResult]:
        """Check all configured network endpoints"""
        results = []
        for name, url in self.config.get("endpoints", {}).items():
            result = await self.check_endpoint(name, url)
            results.append(result)
        return results
    
    # ==================== SYSTEM CHECKS ====================
    
    async def check_system_resources(self) -> List[HealthCheckResult]:
        """Check system resource usage"""
        results = []
        thresholds = self.config["thresholds"]
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        status = HealthStatus.HEALTHY
        if memory_percent > thresholds["memory_percent_max"]:
            status = HealthStatus.UNHEALTHY
        elif memory_percent > thresholds["memory_percent_max"] - 10:
            status = HealthStatus.DEGRADED
            
        results.append(HealthCheckResult(
            name="sys_memory",
            status=status,
            message=f"Memory: {memory_percent:.1f}% used ({memory.used/1024/1024/1024:.1f}GB/{memory.total/1024/1024/1024:.1f}GB)",
            latency_ms=0,
            details={
                "percent": memory_percent,
                "used_gb": memory.used/1024/1024/1024,
                "total_gb": memory.total/1024/1024/1024,
                "available_gb": memory.available/1024/1024/1024
            },
            timestamp=datetime.now()
        ))
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        status = HealthStatus.HEALTHY
        if cpu_percent > thresholds["cpu_percent_max"]:
            status = HealthStatus.UNHEALTHY
        elif cpu_percent > thresholds["cpu_percent_max"] - 10:
            status = HealthStatus.DEGRADED
            
        results.append(HealthCheckResult(
            name="sys_cpu",
            status=status,
            message=f"CPU: {cpu_percent:.1f}% ({psutil.cpu_count()} cores)",
            latency_ms=0,
            details={
                "percent": cpu_percent,
                "cores": psutil.cpu_count(),
                "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            timestamp=datetime.now()
        ))
        
        # Disk
        disk = psutil.disk_usage(str(self.gladius_root))
        disk_percent = disk.percent
        status = HealthStatus.HEALTHY
        if disk_percent > thresholds["disk_percent_max"]:
            status = HealthStatus.UNHEALTHY
        elif disk_percent > thresholds["disk_percent_max"] - 10:
            status = HealthStatus.DEGRADED
            
        results.append(HealthCheckResult(
            name="sys_disk",
            status=status,
            message=f"Disk: {disk_percent:.1f}% used ({disk.used/1024/1024/1024:.1f}GB/{disk.total/1024/1024/1024:.1f}GB)",
            latency_ms=0,
            details={
                "percent": disk_percent,
                "used_gb": disk.used/1024/1024/1024,
                "total_gb": disk.total/1024/1024/1024,
                "free_gb": disk.free/1024/1024/1024
            },
            timestamp=datetime.now()
        ))
        
        return results
    
    # ==================== SERVICE CHECKS ====================
    
    async def check_sentinel_services(self) -> List[HealthCheckResult]:
        """Check SENTINEL service status"""
        results = []
        
        # Check watchdog
        watchdog_heartbeat = self.base_path / "services" / "watchdog_heartbeat.log"
        if watchdog_heartbeat.exists():
            try:
                with open(watchdog_heartbeat) as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1]
                        data = json.loads(last_line)
                        last_beat = datetime.fromisoformat(data.get("timestamp", ""))
                        age_seconds = (datetime.now() - last_beat).total_seconds()
                        
                        status = HealthStatus.HEALTHY
                        if age_seconds > 120:
                            status = HealthStatus.UNHEALTHY
                        elif age_seconds > 60:
                            status = HealthStatus.DEGRADED
                            
                        results.append(HealthCheckResult(
                            name="svc_watchdog",
                            status=status,
                            message=f"Watchdog: last heartbeat {age_seconds:.0f}s ago",
                            latency_ms=0,
                            details={"last_heartbeat": data.get("timestamp"), "age_seconds": age_seconds},
                            timestamp=datetime.now()
                        ))
            except Exception as e:
                results.append(HealthCheckResult(
                    name="svc_watchdog",
                    status=HealthStatus.DEGRADED,
                    message=f"Watchdog heartbeat parse error: {str(e)}",
                    latency_ms=0,
                    details={"error": str(e)},
                    timestamp=datetime.now()
                ))
        else:
            results.append(HealthCheckResult(
                name="svc_watchdog",
                status=HealthStatus.UNKNOWN,
                message="Watchdog heartbeat log not found",
                latency_ms=0,
                details={},
                timestamp=datetime.now()
            ))
        
        # Check learning daemon state
        learning_db = self.base_path / "services" / "learning_state.db"
        if learning_db.exists():
            try:
                conn = sqlite3.connect(learning_db)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM state ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    last_checkpoint = datetime.fromisoformat(row[6]) if row[6] else None
                    if last_checkpoint:
                        age_seconds = (datetime.now() - last_checkpoint).total_seconds()
                        status = HealthStatus.HEALTHY
                        if age_seconds > 7200:  # 2 hours
                            status = HealthStatus.DEGRADED
                        elif age_seconds > 86400:  # 24 hours
                            status = HealthStatus.UNHEALTHY
                            
                        results.append(HealthCheckResult(
                            name="svc_learning",
                            status=status,
                            message=f"Learning daemon: {row[4]} cycles, last checkpoint {age_seconds/60:.0f}m ago",
                            latency_ms=0,
                            details={
                                "phase": row[1],
                                "cycles": row[4],
                                "last_checkpoint": row[6],
                                "age_seconds": age_seconds
                            },
                            timestamp=datetime.now()
                        ))
            except Exception as e:
                results.append(HealthCheckResult(
                    name="svc_learning",
                    status=HealthStatus.DEGRADED,
                    message=f"Learning daemon state error: {str(e)}",
                    latency_ms=0,
                    details={"error": str(e)},
                    timestamp=datetime.now()
                ))
        
        # Check GLADIUS router
        start = time.time()
        try:
            sys.path.insert(0, str(self.gladius_root))
            from GLADIUS.router.pattern_router import NativeToolRouter
            router = NativeToolRouter()
            result = router.route("test query")
            latency = (time.time() - start) * 1000
            
            results.append(HealthCheckResult(
                name="svc_gladius",
                status=HealthStatus.HEALTHY,
                message=f"GLADIUS router: {result.tool_name} ({latency:.1f}ms)",
                latency_ms=latency,
                details={"tool": result.tool_name, "confidence": result.confidence},
                timestamp=datetime.now()
            ))
        except Exception as e:
            results.append(HealthCheckResult(
                name="svc_gladius",
                status=HealthStatus.DEGRADED,
                message=f"GLADIUS router error: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
                details={"error": str(e)},
                timestamp=datetime.now()
            ))
        
        return results
    
    # ==================== REGRESSION CHECKS ====================
    
    async def check_regression(self) -> List[HealthCheckResult]:
        """Check for performance regression against baseline"""
        results = []
        
        try:
            conn = sqlite3.connect(self.history_db)
            cursor = conn.cursor()
            
            # Get last 10 health checks
            cursor.execute('''
                SELECT overall_status, healthy_count, unhealthy_count, duration_ms
                FROM health_history
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) >= 5:
                # Calculate averages
                avg_healthy = sum(r[1] for r in rows) / len(rows)
                avg_unhealthy = sum(r[2] for r in rows) / len(rows)
                avg_duration = sum(r[3] for r in rows) / len(rows)
                
                # Check for regression
                latest_unhealthy = rows[0][2] if rows else 0
                
                status = HealthStatus.HEALTHY
                message = "No regression detected"
                
                if latest_unhealthy > avg_unhealthy * 1.5 and latest_unhealthy > 0:
                    status = HealthStatus.DEGRADED
                    message = f"Regression: unhealthy checks increased ({latest_unhealthy} vs avg {avg_unhealthy:.1f})"
                
                results.append(HealthCheckResult(
                    name="regression",
                    status=status,
                    message=message,
                    latency_ms=0,
                    details={
                        "avg_healthy": avg_healthy,
                        "avg_unhealthy": avg_unhealthy,
                        "avg_duration_ms": avg_duration,
                        "sample_size": len(rows)
                    },
                    timestamp=datetime.now()
                ))
            else:
                results.append(HealthCheckResult(
                    name="regression",
                    status=HealthStatus.UNKNOWN,
                    message="Insufficient history for regression detection",
                    latency_ms=0,
                    details={"sample_size": len(rows)},
                    timestamp=datetime.now()
                ))
                
        except Exception as e:
            results.append(HealthCheckResult(
                name="regression",
                status=HealthStatus.UNKNOWN,
                message=f"Regression check error: {str(e)}",
                latency_ms=0,
                details={"error": str(e)},
                timestamp=datetime.now()
            ))
        
        return results
    
    # ==================== MAIN HEALTH CHECK ====================
    
    async def run_full_health_check(self) -> SystemHealthReport:
        """Run complete health check"""
        start_time = time.time()
        all_checks: List[HealthCheckResult] = []
        checks_enabled = self.config.get("checks_enabled", {})
        
        logger.info("Starting full health check...")
        
        # Database checks
        if checks_enabled.get("database", True):
            db_results = await self.check_all_databases()
            all_checks.extend(db_results)
        
        # Authentication checks
        if checks_enabled.get("authentication", True):
            smtp_result = await self.check_smtp_auth()
            all_checks.append(smtp_result)
            
            api_results = await self.check_api_keys()
            all_checks.extend(api_results)
        
        # Network checks
        if checks_enabled.get("network", True):
            net_results = await self.check_all_endpoints()
            all_checks.extend(net_results)
        
        # System checks
        if checks_enabled.get("system", True):
            sys_results = await self.check_system_resources()
            all_checks.extend(sys_results)
        
        # Service checks
        if checks_enabled.get("services", True):
            svc_results = await self.check_sentinel_services()
            all_checks.extend(svc_results)
        
        # Regression checks
        if checks_enabled.get("regression", True):
            reg_results = await self.check_regression()
            all_checks.extend(reg_results)
        
        # Calculate summary
        summary = {
            "healthy": sum(1 for c in all_checks if c.status == HealthStatus.HEALTHY),
            "degraded": sum(1 for c in all_checks if c.status == HealthStatus.DEGRADED),
            "unhealthy": sum(1 for c in all_checks if c.status == HealthStatus.UNHEALTHY),
            "unknown": sum(1 for c in all_checks if c.status == HealthStatus.UNKNOWN),
            "total": len(all_checks)
        }
        
        # Determine overall status
        if summary["unhealthy"] > 0:
            overall = HealthStatus.UNHEALTHY
        elif summary["degraded"] > 0:
            overall = HealthStatus.DEGRADED
        elif summary["unknown"] == summary["total"]:
            overall = HealthStatus.UNKNOWN
        else:
            overall = HealthStatus.HEALTHY
        
        duration = (time.time() - start_time) * 1000
        
        report = SystemHealthReport(
            overall_status=overall,
            checks=all_checks,
            summary=summary,
            timestamp=datetime.now(),
            duration_ms=duration
        )
        
        # Save to history
        self._save_to_history(report)
        
        logger.info(f"Health check complete: {overall.value} ({summary['healthy']}/{summary['total']} healthy) in {duration:.0f}ms")
        
        return report
    
    def _save_to_history(self, report: SystemHealthReport):
        """Save health report to history"""
        try:
            conn = sqlite3.connect(self.history_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO health_history 
                (timestamp, overall_status, healthy_count, degraded_count, unhealthy_count, duration_ms, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.timestamp.isoformat(),
                report.overall_status.value,
                report.summary["healthy"],
                report.summary["degraded"],
                report.summary["unhealthy"],
                report.duration_ms,
                json.dumps([asdict(c) for c in report.checks], default=str)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save health history: {e}")
    
    def format_report(self, report: SystemHealthReport) -> str:
        """Format health report for display"""
        lines = []
        lines.append("=" * 60)
        lines.append("SENTINEL HEALTH REPORT")
        lines.append("=" * 60)
        lines.append(f"Timestamp: {report.timestamp.isoformat()}")
        lines.append(f"Duration:  {report.duration_ms:.0f}ms")
        lines.append(f"Overall:   {report.overall_status.value.upper()}")
        lines.append("")
        lines.append(f"Summary: {report.summary['healthy']} healthy, "
                    f"{report.summary['degraded']} degraded, "
                    f"{report.summary['unhealthy']} unhealthy, "
                    f"{report.summary['unknown']} unknown")
        lines.append("")
        lines.append("-" * 60)
        lines.append("DETAILED CHECKS")
        lines.append("-" * 60)
        
        # Group by status
        for status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED, 
                       HealthStatus.HEALTHY, HealthStatus.UNKNOWN]:
            checks = [c for c in report.checks if c.status == status]
            if checks:
                icon = {"healthy": "✅", "degraded": "⚠️", 
                       "unhealthy": "❌", "unknown": "❓"}[status.value]
                lines.append(f"\n{icon} {status.value.upper()}")
                for check in checks:
                    lines.append(f"   {check.name}: {check.message} ({check.latency_ms:.0f}ms)")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# CLI interface
async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SENTINEL Health Monitor")
    parser.add_argument("command", choices=["check", "history", "baseline"],
                       help="Command to execute")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    monitor = HealthMonitor()
    
    if args.command == "check":
        report = await monitor.run_full_health_check()
        if args.json:
            output = {
                "overall_status": report.overall_status.value,
                "summary": report.summary,
                "timestamp": report.timestamp.isoformat(),
                "duration_ms": report.duration_ms,
                "checks": [asdict(c) for c in report.checks]
            }
            print(json.dumps(output, indent=2, default=str))
        else:
            print(monitor.format_report(report))
    
    elif args.command == "history":
        try:
            conn = sqlite3.connect(monitor.history_db)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM health_history ORDER BY timestamp DESC LIMIT 10")
            rows = cursor.fetchall()
            conn.close()
            
            print("Recent Health Check History:")
            print("-" * 60)
            for row in rows:
                print(f"{row[1]}: {row[2]} | H:{row[3]} D:{row[4]} U:{row[5]} | {row[6]:.0f}ms")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
