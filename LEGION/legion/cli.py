#!/usr/bin/env python3
"""
LEGION Enterprise System - Command Line Interface

A comprehensive CLI for controlling and monitoring the LEGION enterprise system.
Provides complete access to all system components, agents, and telemetry.
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3
from tabulate import tabulate

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from message_bus import MessageBus
from agent_memory import AgentMemorySystem
from distributed_tracing import TracingSystem
from self_improvement import SelfImprovementSystem


class LegionCLI:
    """
    Command-line interface for LEGION Enterprise System.
    
    Provides comprehensive control over:
    - System operations (start, stop, status, health)
    - Agent management (list, spawn, despawn, status)
    - Message bus (send, receive, statistics)
    - Memory system (query, clear, statistics)
    - Tracing (view, analyze, performance)
    - Self-improvement (insights, suggestions, performance)
    - Continuous operation (start cycles, monitor, reports)
    - Configuration (view, set, reset)
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.message_bus = None
        self.memory_system = None
        self.tracing = None
        self.improvement = None
        
    async def initialize_systems(self):
        """Initialize all LEGION systems asynchronously."""
        self.message_bus = MessageBus()
        self.memory_system = AgentMemorySystem()
        self.tracing = TracingSystem()
        self.improvement = SelfImprovementSystem()
        
        # Start background tasks
        await self.message_bus.start()
        
    async def cleanup_systems(self):
        """Clean up and close all systems."""
        if self.message_bus:
            await self.message_bus.stop()
            
    # ==================== SYSTEM COMMANDS ====================
    
    async def cmd_system_status(self, args):
        """Display comprehensive system status."""
        print("\n" + "="*70)
        print("LEGION ENTERPRISE SYSTEM - STATUS")
        print("="*70 + "\n")
        
        # System Information
        print("System Information:")
        print(f"  Base Directory: {self.base_dir}")
        print(f"  Timestamp: {datetime.now().isoformat()}")
        
        # Database Status
        print("\nDatabase Status:")
        dbs = [
            ("Message Bus", self.data_dir / "message_bus.db"),
            ("Agent Memory", self.data_dir / "agent_memory.db"),
            ("Tracing", self.data_dir / "tracing.db"),
            ("Self-Improvement", self.data_dir / "self_improvement.db"),
            ("Continuous Operation", self.data_dir / "continuous_operation.db"),
        ]
        
        for name, path in dbs:
            if path.exists():
                size = path.stat().st_size / 1024  # KB
                print(f"  ✓ {name:25s} {size:>10.2f} KB")
            else:
                print(f"  ✗ {name:25s} NOT FOUND")
                
        # Message Bus Status
        if self.message_bus:
            try:
                stats = self.message_bus.get_stats()
                print(f"\nMessage Bus:")
                print(f"  Total Sent: {stats.get('total_sent', 0)}")
                print(f"  Total Delivered: {stats.get('total_delivered', 0)}")
                print(f"  Failed: {stats.get('failed', 0)}")
                print(f"  Pending: {stats.get('pending', 0)}")
            except Exception as e:
                print(f"\nMessage Bus: Error retrieving stats ({e})")
            
        # Memory System Status
        if self.memory_system:
            db_path = self.base_dir / "data" / "agent_memory.db"
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM episodic_memory")
                episodic = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM semantic_memory")
                semantic = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM procedural_memory")
                procedural = cursor.fetchone()[0]
                
                print(f"\nMemory System:")
                print(f"  Episodic Memories: {episodic}")
                print(f"  Semantic Memories: {semantic}")
                print(f"  Procedural Memories: {procedural}")
                
                conn.close()
            else:
                print(f"\nMemory System: No database found")
            
        # Tracing System Status
        if self.tracing:
            db_path = self.base_dir / "data" / "tracing.db"
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM spans")
                spans = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(DISTINCT trace_id) FROM spans")
                traces = cursor.fetchone()[0]
                
                print(f"\nTracing System:")
                print(f"  Total Spans: {spans}")
                print(f"  Total Traces: {traces}")
                
                conn.close()
            else:
                print(f"\nTracing System: No database found")
            
        print("\n" + "="*70 + "\n")
        
    async def cmd_system_health(self, args):
        """Display system health metrics."""
        print("\n" + "="*70)
        print("LEGION ENTERPRISE SYSTEM - HEALTH CHECK")
        print("="*70 + "\n")
        
        health_checks = []
        
        # Check databases
        dbs = [
            ("Message Bus DB", self.base_dir / "message_bus.db"),
            ("Agent Memory DB", self.data_dir / "agent_memory.db"),
            ("Tracing DB", self.data_dir / "tracing.db"),
            ("Self-Improvement DB", self.data_dir / "self_improvement.db"),
        ]
        
        for name, path in dbs:
            status = "✓ HEALTHY" if path.exists() else "✗ MISSING"
            health_checks.append([name, status])
            
        # Check systems
        systems = [
            ("Message Bus", self.message_bus is not None),
            ("Memory System", self.memory_system is not None),
            ("Tracing System", self.tracing is not None),
            ("Self-Improvement", self.improvement is not None),
        ]
        
        for name, initialized in systems:
            status = "✓ INITIALIZED" if initialized else "✗ NOT INITIALIZED"
            health_checks.append([name, status])
            
        print(tabulate(health_checks, headers=["Component", "Status"], tablefmt="grid"))
        print()
        
    # ==================== AGENT COMMANDS ====================
    
    async def cmd_agent_list(self, args):
        """List all agents and their status."""
        print("\n" + "="*70)
        print("LEGION AGENTS")
        print("="*70 + "\n")
        
        # Get agents from memory system
        conn = sqlite3.connect(str(self.data_dir / "agent_memory.db"))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT agent_id FROM episodic_memory
            UNION
            SELECT DISTINCT agent_id FROM semantic_memory
            UNION
            SELECT DISTINCT agent_id FROM procedural_memory
            ORDER BY agent_id
        """)
        
        agents = [row[0] for row in cursor.fetchall()]
        
        if not agents:
            print("No agents found in the system.")
            print("Agents are created dynamically when needed.\n")
            conn.close()
            return
            
        agent_data = []
        for agent_id in agents:
            # Get memory counts
            cursor.execute("SELECT COUNT(*) FROM episodic_memory WHERE agent_id = ?", (agent_id,))
            episodic = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM semantic_memory WHERE agent_id = ?", (agent_id,))
            semantic = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM procedural_memory WHERE agent_id = ?", (agent_id,))
            procedural = cursor.fetchone()[0]
            
            agent_data.append([
                agent_id,
                episodic,
                semantic,
                procedural,
                episodic + semantic + procedural
            ])
            
        print(tabulate(
            agent_data,
            headers=["Agent ID", "Episodic", "Semantic", "Procedural", "Total"],
            tablefmt="grid"
        ))
        print()
        
        conn.close()
        
    async def cmd_agent_status(self, args):
        """Get detailed status of a specific agent."""
        agent_id = args.agent_id
        
        print(f"\n" + "="*70)
        print(f"AGENT STATUS: {agent_id}")
        print("="*70 + "\n")
        
        # Check if agent exists
        conn = sqlite3.connect(str(self.data_dir / "agent_memory.db"))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM episodic_memory WHERE agent_id = ?
            UNION ALL
            SELECT COUNT(*) FROM semantic_memory WHERE agent_id = ?
            UNION ALL
            SELECT COUNT(*) FROM procedural_memory WHERE agent_id = ?
        """, (agent_id, agent_id, agent_id))
        
        counts = cursor.fetchall()
        total = sum(row[0] for row in counts)
        
        if total == 0:
            print(f"Agent '{agent_id}' not found in the system.\n")
            conn.close()
            return
            
        # Memory statistics
        print("Memory Statistics:")
        cursor.execute("SELECT COUNT(*), AVG(confidence) FROM episodic_memory WHERE agent_id = ?", (agent_id,))
        ep_count, ep_conf = cursor.fetchone()
        print(f"  Episodic: {ep_count} memories (avg confidence: {ep_conf or 0:.2f})")
        
        cursor.execute("SELECT COUNT(*), AVG(confidence) FROM semantic_memory WHERE agent_id = ?", (agent_id,))
        sem_count, sem_conf = cursor.fetchone()
        print(f"  Semantic: {sem_count} memories (avg confidence: {sem_conf or 0:.2f})")
        
        cursor.execute("SELECT COUNT(*), AVG(confidence) FROM procedural_memory WHERE agent_id = ?", (agent_id,))
        proc_count, proc_conf = cursor.fetchone()
        print(f"  Procedural: {proc_count} memories (avg confidence: {proc_conf or 0:.2f})")
        
        # Recent activity
        print("\nRecent Episodic Memories:")
        cursor.execute("""
            SELECT timestamp, event, context
            FROM episodic_memory
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT 5
        """, (agent_id,))
        
        memories = cursor.fetchall()
        if memories:
            for ts, event, context in memories:
                print(f"  [{ts}] {event}")
                if context:
                    ctx = json.loads(context) if isinstance(context, str) else context
                    if ctx:
                        print(f"    Context: {list(ctx.keys())}")
        else:
            print("  No recent memories")
            
        print()
        conn.close()
        
    # ==================== MESSAGE COMMANDS ====================
    
    async def cmd_message_send(self, args):
        """Send a message to an agent."""
        message = {
            'to': args.to,
            'from': args.sender or 'cli',
            'content': args.content,
            'type': args.type or 'command',
            'priority': args.priority or 5
        }
        
        message_id = await self.message_bus.send_message(message)
        print(f"\nMessage sent successfully!")
        print(f"Message ID: {message_id}")
        print(f"To: {args.to}")
        print(f"Priority: {message['priority']}\n")
        
    async def cmd_message_stats(self, args):
        """Display message bus statistics."""
        stats = self.message_bus.get_stats()
        
        print("\n" + "="*70)
        print("MESSAGE BUS STATISTICS")
        print("="*70 + "\n")
        
        data = [
            ["Total Sent", stats.get('total_sent', 0)],
            ["Total Delivered", stats.get('total_delivered', 0)],
            ["Failed", stats.get('failed', 0)],
            ["Pending", stats.get('pending', 0)],
        ]
        
        print(tabulate(data, headers=["Metric", "Value"], tablefmt="grid"))
        print()
        
    # ==================== MEMORY COMMANDS ====================
    
    async def cmd_memory_query(self, args):
        """Query agent memory."""
        agent_id = args.agent_id
        memory_type = args.type
        limit = args.limit or 10
        
        print(f"\n" + "="*70)
        print(f"MEMORY QUERY: {agent_id} ({memory_type})")
        print("="*70 + "\n")
        
        conn = sqlite3.connect(str(self.data_dir / "agent_memory.db"))
        cursor = conn.cursor()
        
        if memory_type == "episodic":
            cursor.execute("""
                SELECT timestamp, event, context, confidence
                FROM episodic_memory
                WHERE agent_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, limit))
            
            results = cursor.fetchall()
            if results:
                data = [[ts, event[:50], f"{conf:.2f}"] for ts, event, ctx, conf in results]
                print(tabulate(data, headers=["Timestamp", "Event", "Confidence"], tablefmt="grid"))
            else:
                print("No episodic memories found.")
                
        elif memory_type == "semantic":
            cursor.execute("""
                SELECT timestamp, concept, knowledge, confidence
                FROM semantic_memory
                WHERE agent_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, limit))
            
            results = cursor.fetchall()
            if results:
                data = [[ts, concept[:30], knowledge[:40], f"{conf:.2f}"] for ts, concept, knowledge, conf in results]
                print(tabulate(data, headers=["Timestamp", "Concept", "Knowledge", "Confidence"], tablefmt="grid"))
            else:
                print("No semantic memories found.")
                
        elif memory_type == "procedural":
            cursor.execute("""
                SELECT timestamp, skill, procedure, confidence
                FROM procedural_memory
                WHERE agent_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, limit))
            
            results = cursor.fetchall()
            if results:
                data = [[ts, skill[:30], f"{conf:.2f}"] for ts, skill, proc, conf in results]
                print(tabulate(data, headers=["Timestamp", "Skill", "Confidence"], tablefmt="grid"))
            else:
                print("No procedural memories found.")
                
        print()
        conn.close()
        
    async def cmd_memory_stats(self, args):
        """Display memory system statistics."""
        print("\n" + "="*70)
        print("MEMORY SYSTEM STATISTICS")
        print("="*70 + "\n")
        
        conn = sqlite3.connect(str(self.data_dir / "agent_memory.db"))
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute("SELECT COUNT(*) FROM episodic_memory")
        episodic_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM semantic_memory")
        semantic_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM procedural_memory")
        procedural_total = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM episodic_memory")
        episodic_conf = cursor.fetchone()[0] or 0
        cursor.execute("SELECT AVG(confidence) FROM semantic_memory")
        semantic_conf = cursor.fetchone()[0] or 0
        cursor.execute("SELECT AVG(confidence) FROM procedural_memory")
        procedural_conf = cursor.fetchone()[0] or 0
        
        data = [
            ["Episodic", episodic_total, f"{episodic_conf:.2f}"],
            ["Semantic", semantic_total, f"{semantic_conf:.2f}"],
            ["Procedural", procedural_total, f"{procedural_conf:.2f}"],
            ["TOTAL", episodic_total + semantic_total + procedural_total, "-"],
        ]
        
        print(tabulate(data, headers=["Memory Type", "Count", "Avg Confidence"], tablefmt="grid"))
        print()
        
        conn.close()
        
    async def cmd_memory_clear(self, args):
        """Clear memory for an agent."""
        agent_id = args.agent_id
        memory_type = args.type
        
        if not args.confirm:
            print(f"\nWARNING: This will delete {memory_type} memory for agent '{agent_id}'")
            print("Use --confirm to proceed.\n")
            return
            
        conn = sqlite3.connect(str(self.data_dir / "agent_memory.db"))
        cursor = conn.cursor()
        
        if memory_type == "all":
            cursor.execute("DELETE FROM episodic_memory WHERE agent_id = ?", (agent_id,))
            cursor.execute("DELETE FROM semantic_memory WHERE agent_id = ?", (agent_id,))
            cursor.execute("DELETE FROM procedural_memory WHERE agent_id = ?", (agent_id,))
        else:
            cursor.execute(f"DELETE FROM {memory_type}_memory WHERE agent_id = ?", (agent_id,))
            
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        
        print(f"\nCleared {deleted} {memory_type} memories for agent '{agent_id}'\n")
        
    # ==================== TRACING COMMANDS ====================
    
    async def cmd_trace_list(self, args):
        """List recent traces."""
        limit = args.limit or 10
        
        print(f"\n" + "="*70)
        print("RECENT TRACES")
        print("="*70 + "\n")
        
        conn = sqlite3.connect(str(self.data_dir / "tracing.db"))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT trace_id, MIN(start_time), COUNT(*), SUM(duration_ms)
            FROM spans
            GROUP BY trace_id
            ORDER BY MIN(start_time) DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        if results:
            data = [[tid[:16], ts, spans, f"{dur:.2f}ms"] for tid, ts, spans, dur in results]
            print(tabulate(data, headers=["Trace ID", "Start Time", "Spans", "Total Duration"], tablefmt="grid"))
        else:
            print("No traces found.")
            
        print()
        conn.close()
        
    async def cmd_trace_view(self, args):
        """View details of a specific trace."""
        trace_id = args.trace_id
        
        print(f"\n" + "="*70)
        print(f"TRACE DETAILS: {trace_id}")
        print("="*70 + "\n")
        
        conn = sqlite3.connect(str(self.data_dir / "tracing.db"))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT span_id, operation_name, start_time, duration_ms, status, tags
            FROM spans
            WHERE trace_id = ?
            ORDER BY start_time
        """, (trace_id,))
        
        results = cursor.fetchall()
        if results:
            data = [[sid[:16], op[:30], ts, f"{dur:.2f}ms", status] for sid, op, ts, dur, status, tags in results]
            print(tabulate(data, headers=["Span ID", "Operation", "Start Time", "Duration", "Status"], tablefmt="grid"))
        else:
            print(f"Trace '{trace_id}' not found.")
            
        print()
        conn.close()
        
    async def cmd_trace_performance(self, args):
        """Display performance metrics from tracing."""
        print("\n" + "="*70)
        print("PERFORMANCE METRICS")
        print("="*70 + "\n")
        
        conn = sqlite3.connect(str(self.data_dir / "tracing.db"))
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_spans,
                AVG(duration_ms) as avg_duration,
                MIN(duration_ms) as min_duration,
                MAX(duration_ms) as max_duration
            FROM spans
        """)
        
        total, avg, min_dur, max_dur = cursor.fetchone()
        
        print(f"Total Spans: {total}")
        print(f"Average Duration: {avg:.2f}ms")
        print(f"Min Duration: {min_dur:.2f}ms")
        print(f"Max Duration: {max_dur:.2f}ms")
        
        # Slowest operations
        print("\nSlowest Operations:")
        cursor.execute("""
            SELECT operation_name, AVG(duration_ms) as avg_dur, COUNT(*) as count
            FROM spans
            GROUP BY operation_name
            ORDER BY avg_dur DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        if results:
            data = [[op[:40], f"{dur:.2f}ms", count] for op, dur, count in results]
            print(tabulate(data, headers=["Operation", "Avg Duration", "Count"], tablefmt="grid"))
            
        print()
        conn.close()
        
    # ==================== SELF-IMPROVEMENT COMMANDS ====================
    
    async def cmd_improvement_insights(self, args):
        """Display learning insights."""
        agent_id = args.agent_id if args.agent_id else None
        limit = args.limit or 10
        
        print("\n" + "="*70)
        print("SELF-IMPROVEMENT INSIGHTS")
        print("="*70 + "\n")
        
        conn = sqlite3.connect(str(self.data_dir / "self_improvement.db"))
        cursor = conn.cursor()
        
        if agent_id:
            cursor.execute("""
                SELECT timestamp, insight_type, description, confidence
                FROM learning_insights
                WHERE agent_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, limit))
        else:
            cursor.execute("""
                SELECT timestamp, agent_id, insight_type, description, confidence
                FROM learning_insights
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
        results = cursor.fetchall()
        if results:
            if agent_id:
                data = [[ts, itype, desc[:50], f"{conf:.2f}"] for ts, itype, desc, conf in results]
                headers = ["Timestamp", "Type", "Description", "Confidence"]
            else:
                data = [[ts, aid[:20], itype, desc[:40], f"{conf:.2f}"] for ts, aid, itype, desc, conf in results]
                headers = ["Timestamp", "Agent", "Type", "Description", "Confidence"]
                
            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            print("No learning insights found.")
            
        print()
        conn.close()
        
    async def cmd_improvement_suggestions(self, args):
        """Display improvement suggestions."""
        limit = args.limit or 10
        
        print("\n" + "="*70)
        print("IMPROVEMENT SUGGESTIONS")
        print("="*70 + "\n")
        
        conn = sqlite3.connect(str(self.data_dir / "self_improvement.db"))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, agent_id, suggestion_type, description, priority
            FROM improvement_suggestions
            ORDER BY priority DESC, timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        if results:
            data = [[ts, aid[:20], stype, desc[:40], priority] for ts, aid, stype, desc, priority in results]
            print(tabulate(data, headers=["Timestamp", "Agent", "Type", "Description", "Priority"], tablefmt="grid"))
        else:
            print("No improvement suggestions found.")
            
        print()
        conn.close()
        
    # ==================== CONTINUOUS OPERATION COMMANDS ====================
    
    async def cmd_operation_start(self, args):
        """Start continuous operation mode."""
        cycles = args.cycles or 100
        
        print(f"\nStarting continuous operation mode for {cycles} cycles...")
        print("This may take several minutes depending on the number of cycles.")
        print("Press Ctrl+C to stop gracefully.\n")
        
        # Import and run continuous operation
        from continuous_operation import main as run_continuous
        
        sys.argv = ['continuous_operation.py', '--cycles', str(cycles)]
        await run_continuous()
        
    async def cmd_operation_status(self, args):
        """Display continuous operation status."""
        print("\n" + "="*70)
        print("CONTINUOUS OPERATION STATUS")
        print("="*70 + "\n")
        
        db_path = self.data_dir / "continuous_operation.db"
        if not db_path.exists():
            print("No continuous operation data found.")
            print("Run 'legion operation start --cycles N' to begin.\n")
            return
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get latest metrics
        cursor.execute("""
            SELECT cycle_number, timestamp, tasks_completed, tasks_failed,
                   messages_sent, errors, warnings, cycle_duration_seconds
            FROM cycle_metrics
            ORDER BY cycle_number DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            cycle, ts, tasks_ok, tasks_fail, msgs, errs, warns, dur = result
            print(f"Last Cycle: {cycle}")
            print(f"Timestamp: {ts}")
            print(f"Tasks: {tasks_ok} completed, {tasks_fail} failed")
            print(f"Messages: {msgs}")
            print(f"Errors: {errs}, Warnings: {warns}")
            print(f"Duration: {dur:.2f}s")
        else:
            print("No cycle data found.")
            
        print()
        conn.close()
        
    async def cmd_operation_report(self, args):
        """Generate continuous operation report."""
        print("\n" + "="*70)
        print("CONTINUOUS OPERATION REPORT")
        print("="*70 + "\n")
        
        db_path = self.data_dir / "continuous_operation.db"
        if not db_path.exists():
            print("No continuous operation data found.\n")
            return
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Summary statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cycles,
                SUM(tasks_completed) as total_tasks,
                SUM(tasks_failed) as failed_tasks,
                SUM(messages_sent) as total_messages,
                SUM(errors) as total_errors,
                AVG(cycle_duration_seconds) as avg_duration
            FROM cycle_metrics
        """)
        
        cycles, tasks, fails, msgs, errs, avg_dur = cursor.fetchone()
        
        print("Summary:")
        print(f"  Total Cycles: {cycles}")
        print(f"  Total Tasks: {tasks}")
        print(f"  Failed Tasks: {fails}")
        print(f"  Success Rate: {(tasks-fails)/tasks*100 if tasks > 0 else 0:.2f}%")
        print(f"  Total Messages: {msgs}")
        print(f"  Total Errors: {errs}")
        print(f"  Average Cycle Duration: {avg_dur:.2f}s")
        
        # Recent errors
        print("\nRecent Errors:")
        cursor.execute("""
            SELECT timestamp, error_type, error_message
            FROM error_log
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        
        errors = cursor.fetchall()
        if errors:
            for ts, etype, emsg in errors:
                print(f"  [{ts}] {etype}: {emsg[:60]}")
        else:
            print("  No errors recorded")
            
        print()
        conn.close()
        
    # ==================== CONFIGURATION COMMANDS ====================
    
    async def cmd_config_view(self, args):
        """View system configuration."""
        config_files = [
            ("Legion Config", self.base_dir / "legion_config.json"),
            ("Enhanced Config", self.base_dir / "enhanced_config.json"),
        ]
        
        print("\n" + "="*70)
        print("SYSTEM CONFIGURATION")
        print("="*70 + "\n")
        
        for name, path in config_files:
            print(f"{name} ({path.name}):")
            if path.exists():
                with open(path, 'r') as f:
                    config = json.load(f)
                    print(json.dumps(config, indent=2))
            else:
                print("  File not found")
            print()
            
    # ==================== MAIN CLI HANDLER ====================
    
    def build_parser(self):
        """Build the argument parser."""
        parser = argparse.ArgumentParser(
            description="LEGION Enterprise System CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  legion system status              Show system status
  legion agent list                 List all agents
  legion agent status agent_id      Show agent details
  legion message send --to agent1 --content "Hello"
  legion memory query agent1 episodic
  legion trace list                 Show recent traces
  legion improvement insights       Show learning insights
  legion operation start --cycles 100
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # SYSTEM commands
        system = subparsers.add_parser('system', help='System operations')
        system_sub = system.add_subparsers(dest='subcommand')
        
        system_sub.add_parser('status', help='Show system status')
        system_sub.add_parser('health', help='Show system health')
        
        # AGENT commands
        agent = subparsers.add_parser('agent', help='Agent management')
        agent_sub = agent.add_subparsers(dest='subcommand')
        
        agent_sub.add_parser('list', help='List all agents')
        
        agent_status = agent_sub.add_parser('status', help='Show agent status')
        agent_status.add_argument('agent_id', help='Agent ID')
        
        # MESSAGE commands
        message = subparsers.add_parser('message', help='Message bus operations')
        message_sub = message.add_subparsers(dest='subcommand')
        
        msg_send = message_sub.add_parser('send', help='Send message')
        msg_send.add_argument('--to', required=True, help='Recipient agent ID')
        msg_send.add_argument('--content', required=True, help='Message content')
        msg_send.add_argument('--sender', help='Sender ID')
        msg_send.add_argument('--type', help='Message type')
        msg_send.add_argument('--priority', type=int, help='Priority (1-10)')
        
        message_sub.add_parser('stats', help='Show message statistics')
        
        # MEMORY commands
        memory = subparsers.add_parser('memory', help='Memory system operations')
        memory_sub = memory.add_subparsers(dest='subcommand')
        
        mem_query = memory_sub.add_parser('query', help='Query agent memory')
        mem_query.add_argument('agent_id', help='Agent ID')
        mem_query.add_argument('type', choices=['episodic', 'semantic', 'procedural'], help='Memory type')
        mem_query.add_argument('--limit', type=int, help='Result limit')
        
        memory_sub.add_parser('stats', help='Show memory statistics')
        
        mem_clear = memory_sub.add_parser('clear', help='Clear agent memory')
        mem_clear.add_argument('agent_id', help='Agent ID')
        mem_clear.add_argument('type', choices=['episodic', 'semantic', 'procedural', 'all'], help='Memory type')
        mem_clear.add_argument('--confirm', action='store_true', help='Confirm deletion')
        
        # TRACE commands
        trace = subparsers.add_parser('trace', help='Distributed tracing operations')
        trace_sub = trace.add_subparsers(dest='subcommand')
        
        trace_list = trace_sub.add_parser('list', help='List recent traces')
        trace_list.add_argument('--limit', type=int, help='Result limit')
        
        trace_view = trace_sub.add_parser('view', help='View trace details')
        trace_view.add_argument('trace_id', help='Trace ID')
        
        trace_sub.add_parser('performance', help='Show performance metrics')
        
        # IMPROVEMENT commands
        improvement = subparsers.add_parser('improvement', help='Self-improvement operations')
        improvement_sub = improvement.add_subparsers(dest='subcommand')
        
        imp_insights = improvement_sub.add_parser('insights', help='Show learning insights')
        imp_insights.add_argument('--agent-id', help='Filter by agent ID')
        imp_insights.add_argument('--limit', type=int, help='Result limit')
        
        imp_sugg = improvement_sub.add_parser('suggestions', help='Show improvement suggestions')
        imp_sugg.add_argument('--limit', type=int, help='Result limit')
        
        # OPERATION commands
        operation = subparsers.add_parser('operation', help='Continuous operation management')
        operation_sub = operation.add_subparsers(dest='subcommand')
        
        op_start = operation_sub.add_parser('start', help='Start continuous operation')
        op_start.add_argument('--cycles', type=int, help='Number of cycles to run')
        
        operation_sub.add_parser('status', help='Show operation status')
        operation_sub.add_parser('report', help='Generate operation report')
        
        # CONFIG commands
        config = subparsers.add_parser('config', help='Configuration management')
        config_sub = config.add_subparsers(dest='subcommand')
        
        config_sub.add_parser('view', help='View configuration')
        
        return parser
        
    async def run(self, args=None):
        """Run the CLI."""
        parser = self.build_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return
            
        # Initialize systems
        await self.initialize_systems()
        
        try:
            # Route to appropriate command handler
            if parsed_args.command == 'system':
                if parsed_args.subcommand == 'status':
                    await self.cmd_system_status(parsed_args)
                elif parsed_args.subcommand == 'health':
                    await self.cmd_system_health(parsed_args)
                    
            elif parsed_args.command == 'agent':
                if parsed_args.subcommand == 'list':
                    await self.cmd_agent_list(parsed_args)
                elif parsed_args.subcommand == 'status':
                    await self.cmd_agent_status(parsed_args)
                    
            elif parsed_args.command == 'message':
                if parsed_args.subcommand == 'send':
                    await self.cmd_message_send(parsed_args)
                elif parsed_args.subcommand == 'stats':
                    await self.cmd_message_stats(parsed_args)
                    
            elif parsed_args.command == 'memory':
                if parsed_args.subcommand == 'query':
                    await self.cmd_memory_query(parsed_args)
                elif parsed_args.subcommand == 'stats':
                    await self.cmd_memory_stats(parsed_args)
                elif parsed_args.subcommand == 'clear':
                    await self.cmd_memory_clear(parsed_args)
                    
            elif parsed_args.command == 'trace':
                if parsed_args.subcommand == 'list':
                    await self.cmd_trace_list(parsed_args)
                elif parsed_args.subcommand == 'view':
                    await self.cmd_trace_view(parsed_args)
                elif parsed_args.subcommand == 'performance':
                    await self.cmd_trace_performance(parsed_args)
                    
            elif parsed_args.command == 'improvement':
                if parsed_args.subcommand == 'insights':
                    await self.cmd_improvement_insights(parsed_args)
                elif parsed_args.subcommand == 'suggestions':
                    await self.cmd_improvement_suggestions(parsed_args)
                    
            elif parsed_args.command == 'operation':
                if parsed_args.subcommand == 'start':
                    await self.cmd_operation_start(parsed_args)
                elif parsed_args.subcommand == 'status':
                    await self.cmd_operation_status(parsed_args)
                elif parsed_args.subcommand == 'report':
                    await self.cmd_operation_report(parsed_args)
                    
            elif parsed_args.command == 'config':
                if parsed_args.subcommand == 'view':
                    await self.cmd_config_view(parsed_args)
                    
        finally:
            # Cleanup
            await self.cleanup_systems()


def main():
    """Main entry point."""
    cli = LegionCLI()
    asyncio.run(cli.run())


if __name__ == '__main__':
    main()
