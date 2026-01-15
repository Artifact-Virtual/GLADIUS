"""
Continuous Operation Framework for LEGION Enterprise System
Runs 500-1000 cycles with comprehensive error detection, monitoring, and recovery
"""

import asyncio
import logging
import json
import sqlite3
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_operation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ContinuousOperation')

@dataclass
class CycleMetrics:
    """Metrics for a single operation cycle"""
    cycle_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    messages_sent: int = 0
    errors_encountered: List[str] = None
    warnings_encountered: List[str] = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    agent_stats: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors_encountered is None:
            self.errors_encountered = []
        if self.warnings_encountered is None:
            self.warnings_encountered = []
        if self.agent_stats is None:
            self.agent_stats = {}

@dataclass
class SystemHealth:
    """Overall system health status"""
    is_healthy: bool
    uptime_seconds: float
    total_cycles_completed: int
    total_errors: int
    error_rate: float
    current_throughput: float  # tasks/second
    average_cycle_time: float
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None


class ContinuousOperationFramework:
    """Framework for running LEGION in continuous operation mode"""
    
    def __init__(self, target_cycles: int = 1000):
        self.base_path = Path(__file__).resolve().parent.parent
        self.legion_path = self.base_path / "legion"
        self.db_path = self.base_path / "data" / "continuous_operation.db"
        
        self.target_cycles = target_cycles
        self.current_cycle = 0
        self.start_time = None
        self.stop_requested = False
        
        # Metrics storage
        self.cycle_metrics: List[CycleMetrics] = []
        self.system_health = SystemHealth(
            is_healthy=True,
            uptime_seconds=0.0,
            total_cycles_completed=0,
            total_errors=0,
            error_rate=0.0,
            current_throughput=0.0,
            average_cycle_time=0.0
        )
        
        # Error tracking
        self.error_counts: Dict[str, int] = {}
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # Initialize database
        self._init_database()
        
        logger.info(f"🚀 Continuous Operation Framework initialized for {target_cycles} cycles")
    
    def _init_database(self):
        """Initialize database for metrics storage"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycle_metrics (
                cycle_number INTEGER PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds REAL,
                tasks_completed INTEGER,
                tasks_failed INTEGER,
                messages_sent INTEGER,
                errors TEXT,
                warnings TEXT,
                memory_usage_mb REAL,
                cpu_usage_percent REAL,
                agent_stats TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_health_log (
                timestamp TEXT PRIMARY KEY,
                is_healthy BOOLEAN,
                uptime_seconds REAL,
                total_cycles_completed INTEGER,
                total_errors INTEGER,
                error_rate REAL,
                current_throughput REAL,
                average_cycle_time REAL,
                last_error TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_log (
                timestamp TEXT,
                cycle_number INTEGER,
                error_type TEXT,
                error_message TEXT,
                stack_trace TEXT,
                severity TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database initialized for continuous operation")
    
    async def run_single_cycle(self, cycle_number: int) -> CycleMetrics:
        """Execute a single operation cycle"""
        metrics = CycleMetrics(
            cycle_number=cycle_number,
            start_time=datetime.now()
        )
        
        try:
            # Import orchestrator dynamically to avoid circular imports
            from enhanced_orchestrator import EnhancedEnterpriseOrchestrator
            
            # Create orchestrator instance
            orchestrator = EnhancedEnterpriseOrchestrator()
            
            # Run single cycle
            logger.info(f"📊 Cycle {cycle_number}/{self.target_cycles} starting...")
            
            # Execute workflow
            result = await orchestrator.execute_single_cycle()
            
            # Extract metrics from result
            metrics.tasks_completed = result.get('tasks_completed', 0)
            metrics.tasks_failed = result.get('tasks_failed', 0)
            metrics.messages_sent = result.get('messages_sent', 0)
            metrics.agent_stats = result.get('agent_stats', {})
            
            # Check for errors in result
            if result.get('errors'):
                metrics.errors_encountered = result['errors']
                self.consecutive_errors += 1
            else:
                self.consecutive_errors = 0
            
            if result.get('warnings'):
                metrics.warnings_encountered = result['warnings']
            
            metrics.end_time = datetime.now()
            metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
            
            # Get system resources
            try:
                import psutil
                process = psutil.Process()
                metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                metrics.cpu_usage_percent = process.cpu_percent(interval=0.1)
            except ImportError:
                pass  # psutil not available, skip resource metrics
            
            logger.info(f"✅ Cycle {cycle_number} completed in {metrics.duration_seconds:.2f}s")
            logger.info(f"   Tasks: {metrics.tasks_completed} completed, {metrics.tasks_failed} failed")
            logger.info(f"   Messages: {metrics.messages_sent} sent")
            
            # Check for critical errors
            if self.consecutive_errors >= self.max_consecutive_errors:
                logger.error(f"❌ {self.consecutive_errors} consecutive errors detected!")
                self.system_health.is_healthy = False
                raise Exception(f"Too many consecutive errors: {self.consecutive_errors}")
            
            return metrics
            
        except Exception as e:
            metrics.end_time = datetime.now()
            metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
            
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            metrics.errors_encountered.append(error_msg)
            
            logger.error(f"❌ Error in cycle {cycle_number}: {error_msg}")
            logger.debug(f"Stack trace: {stack_trace}")
            
            # Log error to database
            self._log_error(cycle_number, type(e).__name__, error_msg, stack_trace, "ERROR")
            
            # Track error counts
            error_type = type(e).__name__
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            
            self.consecutive_errors += 1
            
            return metrics
    
    def _log_error(self, cycle_number: int, error_type: str, error_message: str, 
                   stack_trace: str, severity: str):
        """Log error to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO error_log (timestamp, cycle_number, error_type, error_message, stack_trace, severity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), cycle_number, error_type, error_message, stack_trace, severity))
        
        conn.commit()
        conn.close()
    
    def _save_cycle_metrics(self, metrics: CycleMetrics):
        """Save cycle metrics to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cycle_metrics 
            (cycle_number, start_time, end_time, duration_seconds, tasks_completed, tasks_failed,
             messages_sent, errors, warnings, memory_usage_mb, cpu_usage_percent, agent_stats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.cycle_number,
            metrics.start_time.isoformat(),
            metrics.end_time.isoformat() if metrics.end_time else None,
            metrics.duration_seconds,
            metrics.tasks_completed,
            metrics.tasks_failed,
            metrics.messages_sent,
            json.dumps(metrics.errors_encountered),
            json.dumps(metrics.warnings_encountered),
            metrics.memory_usage_mb,
            metrics.cpu_usage_percent,
            json.dumps(metrics.agent_stats)
        ))
        
        conn.commit()
        conn.close()
    
    def _update_system_health(self):
        """Update system health metrics"""
        if not self.start_time:
            return
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        total_cycles = len(self.cycle_metrics)
        total_errors = sum(1 for m in self.cycle_metrics if m.errors_encountered)
        
        self.system_health.uptime_seconds = uptime
        self.system_health.total_cycles_completed = total_cycles
        self.system_health.total_errors = total_errors
        self.system_health.error_rate = total_errors / total_cycles if total_cycles > 0 else 0.0
        
        # Calculate throughput (tasks per second)
        total_tasks = sum(m.tasks_completed for m in self.cycle_metrics)
        self.system_health.current_throughput = total_tasks / uptime if uptime > 0 else 0.0
        
        # Calculate average cycle time
        cycle_times = [m.duration_seconds for m in self.cycle_metrics if m.duration_seconds > 0]
        self.system_health.average_cycle_time = sum(cycle_times) / len(cycle_times) if cycle_times else 0.0
        
        # Get last error
        errors = [m for m in self.cycle_metrics if m.errors_encountered]
        if errors:
            last_error_cycle = errors[-1]
            self.system_health.last_error = last_error_cycle.errors_encountered[-1] if last_error_cycle.errors_encountered else None
            self.system_health.last_error_time = last_error_cycle.end_time
        
        # Save to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_health_log 
            (timestamp, is_healthy, uptime_seconds, total_cycles_completed, total_errors,
             error_rate, current_throughput, average_cycle_time, last_error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            self.system_health.is_healthy,
            self.system_health.uptime_seconds,
            self.system_health.total_cycles_completed,
            self.system_health.total_errors,
            self.system_health.error_rate,
            self.system_health.current_throughput,
            self.system_health.average_cycle_time,
            self.system_health.last_error
        ))
        
        conn.commit()
        conn.close()
    
    def print_status_summary(self):
        """Print current status summary"""
        print("\n" + "="*80)
        print(f"📊 CONTINUOUS OPERATION STATUS - Cycle {self.current_cycle}/{self.target_cycles}")
        print("="*80)
        print(f"⏱️  Uptime: {self.system_health.uptime_seconds/60:.1f} minutes")
        print(f"✅ Completed Cycles: {self.system_health.total_cycles_completed}")
        print(f"❌ Total Errors: {self.system_health.total_errors}")
        print(f"📈 Error Rate: {self.system_health.error_rate*100:.2f}%")
        print(f"⚡ Throughput: {self.system_health.current_throughput:.2f} tasks/sec")
        print(f"⏳ Avg Cycle Time: {self.system_health.average_cycle_time:.2f}s")
        print(f"🏥 System Health: {'✅ HEALTHY' if self.system_health.is_healthy else '❌ UNHEALTHY'}")
        
        if self.system_health.last_error:
            print(f"\n⚠️  Last Error: {self.system_health.last_error[:100]}...")
        
        # Top errors
        if self.error_counts:
            print("\n📊 Top Errors:")
            sorted_errors = sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for error_type, count in sorted_errors:
                print(f"   • {error_type}: {count} occurrences")
        
        print("="*80 + "\n")
    
    async def run(self):
        """Run continuous operation for target number of cycles"""
        self.start_time = datetime.now()
        
        logger.info("="*80)
        logger.info(f"🚀 STARTING CONTINUOUS OPERATION: {self.target_cycles} CYCLES")
        logger.info("="*80)
        
        try:
            for cycle in range(1, self.target_cycles + 1):
                if self.stop_requested:
                    logger.info("⏹️  Stop requested, ending continuous operation")
                    break
                
                self.current_cycle = cycle
                
                # Run cycle
                metrics = await self.run_single_cycle(cycle)
                self.cycle_metrics.append(metrics)
                
                # Save metrics
                self._save_cycle_metrics(metrics)
                
                # Update system health
                self._update_system_health()
                
                # Print status every 10 cycles
                if cycle % 10 == 0:
                    self.print_status_summary()
                
                # Check if system is still healthy
                if not self.system_health.is_healthy:
                    logger.error("❌ System unhealthy, stopping continuous operation")
                    break
                
                # Small delay between cycles to prevent resource exhaustion
                await asyncio.sleep(0.1)
            
            # Final summary
            self.print_final_summary()
            
            return self.system_health.is_healthy
            
        except KeyboardInterrupt:
            logger.info("\n⏹️  Keyboard interrupt received, stopping gracefully...")
            self.print_final_summary()
            return False
        except Exception as e:
            logger.error(f"❌ Fatal error in continuous operation: {e}")
            logger.debug(traceback.format_exc())
            self.print_final_summary()
            return False
    
    def print_final_summary(self):
        """Print final operation summary"""
        print("\n" + "="*80)
        print("📋 CONTINUOUS OPERATION FINAL SUMMARY")
        print("="*80)
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        print(f"\n⏱️  Total Runtime: {total_time/60:.1f} minutes ({total_time:.1f} seconds)")
        print(f"🔄 Cycles Completed: {self.system_health.total_cycles_completed}/{self.target_cycles}")
        print(f"✅ Success Rate: {((self.system_health.total_cycles_completed - self.system_health.total_errors) / self.system_health.total_cycles_completed * 100):.2f}%")
        print(f"❌ Total Errors: {self.system_health.total_errors}")
        print(f"📈 Error Rate: {self.system_health.error_rate*100:.2f}%")
        print(f"⚡ Average Throughput: {self.system_health.current_throughput:.2f} tasks/sec")
        print(f"⏳ Average Cycle Time: {self.system_health.average_cycle_time:.2f}s")
        
        # Task statistics
        total_tasks = sum(m.tasks_completed for m in self.cycle_metrics)
        total_failed = sum(m.tasks_failed for m in self.cycle_metrics)
        total_messages = sum(m.messages_sent for m in self.cycle_metrics)
        
        print(f"\n📊 Task Statistics:")
        print(f"   • Total Tasks Completed: {total_tasks}")
        print(f"   • Total Tasks Failed: {total_failed}")
        print(f"   • Total Messages Sent: {total_messages}")
        
        # Error breakdown
        if self.error_counts:
            print(f"\n❌ Error Breakdown:")
            sorted_errors = sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)
            for error_type, count in sorted_errors:
                print(f"   • {error_type}: {count} occurrences")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if self.system_health.error_rate > 0.1:
            print("   ⚠️  High error rate detected - investigate error logs")
        if self.system_health.average_cycle_time > 10.0:
            print("   ⚠️  Slow cycle times - consider optimization")
        if self.system_health.is_healthy and self.system_health.error_rate < 0.01:
            print("   ✅ System performing well - ready for production")
        
        print("\n📁 Data Location:")
        print(f"   • Database: {self.db_path}")
        print(f"   • Logs: continuous_operation.log")
        
        print("="*80 + "\n")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LEGION Continuous Operation Framework')
    parser.add_argument('--cycles', type=int, default=1000, 
                       help='Number of cycles to run (default: 1000)')
    args = parser.parse_args()
    
    framework = ContinuousOperationFramework(target_cycles=args.cycles)
    success = await framework.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
