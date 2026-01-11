"""
Reflection Engine - AI self-reflection and improvement system.

The AI analyzes its own thoughts, responses, and outcomes to identify
improvements and incorporate them into its context memory.
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import logging
import asyncio


@dataclass
class Reflection:
    """A single reflection session."""
    id: str
    timestamp: datetime
    context_snapshot: str
    reflection_text: str
    improvements: List[str]
    action_items: List[str]
    performance_metrics: Dict[str, Any]


class ReflectionEngine:
    """
    AI reflection and self-improvement system.
    
    Features:
    - Periodic self-reflection on actions and outcomes
    - Identifies patterns and areas for improvement
    - Stores improvements in context for learning
    - Tracks performance metrics over time
    """
    
    def __init__(self, config: Dict[str, Any], ai_provider, context_engine):
        """
        Initialize reflection engine.
        
        Args:
            config: Configuration dictionary
            ai_provider: AI provider for reflection
            context_engine: Context engine for storing reflections
        """
        self.config = config
        self.ai_provider = ai_provider
        self.context_engine = context_engine
        self.logger = logging.getLogger(__name__)
        
        self.enabled = config.get('enable_reflection', True)
        self.reflection_interval = int(config.get('reflection_interval', 3600))  # 1 hour default
        
        self.db_path = context_engine.db_path
        self.last_reflection = None
        self.reflection_task = None
    
    async def start(self):
        """Start periodic reflection."""
        if not self.enabled:
            self.logger.info("Reflection engine disabled")
            return
        
        self.logger.info(f"Starting reflection engine (interval: {self.reflection_interval}s)")
        self.reflection_task = asyncio.create_task(self._reflection_loop())
    
    async def stop(self):
        """Stop reflection engine."""
        if self.reflection_task:
            self.reflection_task.cancel()
            try:
                await self.reflection_task
            except asyncio.CancelledError:
                pass
    
    async def _reflection_loop(self):
        """Main reflection loop."""
        while True:
            try:
                await asyncio.sleep(self.reflection_interval)
                await self.reflect()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Reflection error: {e}")
    
    async def reflect(self) -> Reflection:
        """
        Perform a reflection session.
        
        Returns:
            Reflection object with insights and improvements
        """
        self.logger.info("Starting reflection session...")
        
        # Get recent context
        context_snapshot = self.context_engine.get_context_for_prompt(max_tokens=5000)
        
        # Get performance metrics
        metrics = await self._gather_performance_metrics()
        
        # Create reflection prompt
        reflection_prompt = f"""You are reflecting on your recent actions and performance as an AI assistant managing enterprise automation.

## Recent Context:
{context_snapshot}

## Performance Metrics:
{json.dumps(metrics, indent=2)}

Reflect on the following:
1. What worked well in recent interactions?
2. What could have been done better?
3. What patterns or insights do you notice?
4. What specific improvements can be made?
5. What should be remembered for future interactions?

Provide a thoughtful reflection and actionable improvements:"""
        
        try:
            result = await self.ai_provider.generate(
                prompt=reflection_prompt,
                system_message="""You are an AI system capable of self-reflection and improvement. 
Analyze your performance honestly and identify concrete improvements.
Focus on actionable insights that will make you more effective.""",
                temperature=0.7,
                max_tokens=2000
            )
            
            reflection_text = result['content']
            
            # Extract improvements and action items using AI
            extraction_prompt = f"""Based on this reflection, extract:
1. Key improvements (list of specific improvements to make)
2. Action items (concrete steps to take)

Reflection:
{reflection_text}

Respond in JSON format:
{{
  "improvements": ["improvement 1", "improvement 2", ...],
  "action_items": ["action 1", "action 2", ...]
}}"""
            
            extraction_result = await self.ai_provider.generate(
                prompt=extraction_prompt,
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse extraction
            try:
                extracted = json.loads(extraction_result['content'])
                improvements = extracted.get('improvements', [])
                action_items = extracted.get('action_items', [])
            except json.JSONDecodeError:
                # Fallback: extract manually
                improvements = self._extract_list_items(reflection_text, "improvement")
                action_items = self._extract_list_items(reflection_text, "action")
            
            # Create reflection object
            reflection = Reflection(
                id=f"reflection_{datetime.now(timezone.utc).timestamp()}",
                timestamp=datetime.now(timezone.utc),
                context_snapshot=context_snapshot,
                reflection_text=reflection_text,
                improvements=improvements,
                action_items=action_items,
                performance_metrics=metrics
            )
            
            # Save reflection
            self._save_reflection(reflection)
            
            # Add to context as learning
            await self.context_engine.add_entry(
                role="system",
                content=f"[REFLECTION & LEARNING]\n\n{reflection_text}\n\nKey Improvements:\n" + 
                       "\n".join(f"- {imp}" for imp in improvements),
                metadata={
                    'type': 'reflection',
                    'reflection_id': reflection.id,
                    'improvements_count': len(improvements)
                }
            )
            
            self.last_reflection = reflection
            self.logger.info(f"Reflection complete. {len(improvements)} improvements identified.")
            
            return reflection
            
        except Exception as e:
            self.logger.error(f"Reflection failed: {e}")
            raise
    
    def _save_reflection(self, reflection: Reflection):
        """Save reflection to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reflections 
            (id, timestamp, context_snapshot, reflection, improvements, action_items)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            reflection.id,
            reflection.timestamp.isoformat(),
            reflection.context_snapshot,
            reflection.reflection_text,
            json.dumps(reflection.improvements),
            json.dumps(reflection.action_items)
        ))
        
        conn.commit()
        conn.close()
    
    async def _gather_performance_metrics(self) -> Dict[str, Any]:
        """Gather performance metrics for reflection."""
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'context_stats': self.context_engine.get_statistics(),
        }
        
        # Get database metrics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count entries in last hour
        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        cursor.execute(
            'SELECT COUNT(*) FROM context_entries WHERE timestamp > ?',
            (one_hour_ago,)
        )
        metrics['entries_last_hour'] = cursor.fetchone()[0]
        
        # Count reflections
        cursor.execute('SELECT COUNT(*) FROM reflections')
        metrics['total_reflections'] = cursor.fetchone()[0]
        
        # Get recent improvement count
        cursor.execute('''
            SELECT improvements FROM reflections 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''', (one_hour_ago,))
        
        recent_improvements = []
        for row in cursor.fetchall():
            recent_improvements.extend(json.loads(row[0]))
        
        metrics['recent_improvements_count'] = len(recent_improvements)
        
        conn.close()
        
        return metrics
    
    def _extract_list_items(self, text: str, keyword: str) -> List[str]:
        """Extract list items from text (fallback method)."""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith('-') or line.startswith('•') or 
                line.startswith('*') or any(char.isdigit() for char in line[:3])):
                if keyword.lower() in line.lower():
                    # Clean up the line
                    item = line.lstrip('-•*0123456789. ').strip()
                    if item:
                        items.append(item)
        
        return items[:10]  # Limit to 10 items
    
    def get_recent_improvements(self, limit: int = 10) -> List[str]:
        """
        Get recent improvements from reflections.
        
        Args:
            limit: Maximum number of improvements to return
            
        Returns:
            List of improvement strings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT improvements FROM reflections 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        all_improvements = []
        for row in cursor.fetchall():
            all_improvements.extend(json.loads(row[0]))
        
        conn.close()
        
        return all_improvements[:limit]
    
    def get_reflection_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get reflection history.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of reflection summaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT id, timestamp, reflection, improvements, action_items
            FROM reflections
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'id': row[0],
                'timestamp': row[1],
                'reflection': row[2],
                'improvements': json.loads(row[3]),
                'action_items': json.loads(row[4])
            })
        
        conn.close()
        
        return history
    
    async def analyze_improvement_trends(self) -> Dict[str, Any]:
        """
        Analyze trends in improvements over time.
        
        Returns:
            Analysis of improvement patterns
        """
        history = self.get_reflection_history(days=30)
        
        if not history:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough reflection history for trend analysis'
            }
        
        # Collect all improvements
        all_improvements = []
        for reflection in history:
            all_improvements.extend(reflection['improvements'])
        
        # Use AI to analyze trends
        analysis_prompt = f"""Analyze these AI improvement items collected over time to identify patterns and trends:

{json.dumps(all_improvements, indent=2)}

Provide an analysis of:
1. Common themes or categories
2. Progression over time
3. Most impactful improvements
4. Areas that need more focus

Analysis:"""
        
        try:
            result = await self.ai_provider.generate(
                prompt=analysis_prompt,
                system_message="You are analyzing improvement trends to identify patterns and guide future development.",
                temperature=0.5,
                max_tokens=1500
            )
            
            return {
                'status': 'success',
                'improvement_count': len(all_improvements),
                'reflection_count': len(history),
                'time_period_days': 30,
                'analysis': result['content']
            }
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
