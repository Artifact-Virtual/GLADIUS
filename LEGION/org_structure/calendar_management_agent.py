"""
Calendar Management Agent - Enterprise Legion Framework
Optimize scheduling and time management across the organization
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core_framework import BaseAgent, AgentMessage
import uuid


@dataclass
class CalendarEvent:
    """Calendar event data structure"""
    event_id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    location: str
    event_type: str
    priority: str
    description: str
    recurring: bool
    meeting_url: Optional[str]


@dataclass
class TimeSlot:
    """Time slot data structure"""
    start_time: datetime
    end_time: datetime
    available: bool
    attendee: str
    conflict_reason: Optional[str]


class CalendarManagementAgent(BaseAgent):
    """
    Calendar Management Agent for optimizing scheduling and time
    management across the organization.
    """
    
    def __init__(self, agent_id: str = "calendarmanagementagent"):
        capabilities = ["calendar_management", "scheduling"]
        super().__init__(agent_id, "CalendarManagementAgent", "org_structure", capabilities)
        self.calendars = {}
        self.scheduled_events = []
        self.scheduling_preferences = {}
        self.time_zones = {}
        self.recurring_events = []
        
    async def initialize(self):
        """Initialize the agent with calendar settings and preferences"""
        await super().initialize()
        
        # Setup default scheduling preferences
        self._setup_scheduling_preferences()
        self._setup_time_zones()
        
        # Subscribe to relevant message types
        await self.subscribe_to_messages([
            "meeting_request",
            "schedule_update_request",
            "availability_check_request",
            "calendar_sync_request",
            "time_optimization_request",
            "recurring_event_request",
            "conflict_resolution_request"
        ])
        
        self.logger.info("Calendar Management Agent initialized")
        
    def _setup_scheduling_preferences(self):
        """Setup default scheduling preferences"""
        self.scheduling_preferences = {
            'default_meeting_duration': 60,  # minutes
            'buffer_time': 15,  # minutes between meetings
            'working_hours': {
                'start': '09:00',
                'end': '17:00'
            },
            'lunch_break': {
                'start': '12:00',
                'duration': 60
            },
            'max_consecutive_meetings': 4,
            'preferred_meeting_types': {
                'quick_sync': 15,
                'standup': 30,
                'review': 60,
                'planning': 120,
                'presentation': 90
            },
            'scheduling_restrictions': {
                'no_early_morning': True,  # Before 8 AM
                'no_late_evening': True,   # After 6 PM
                'no_weekend_meetings': True,
                'respect_lunch_breaks': True
            }
        }
        
    def _setup_time_zones(self):
        """Setup supported time zones"""
        self.time_zones = {
            'EST': 'America/New_York',
            'CST': 'America/Chicago',
            'MST': 'America/Denver',
            'PST': 'America/Los_Angeles',
            'UTC': 'UTC',
            'GMT': 'Europe/London',
            'CET': 'Europe/Paris'
        }

    async def process_message(self, message: AgentMessage):
        """Process incoming scheduling requests and calendar operations"""
        try:
            if message.message_type == "meeting_request":
                await self._handle_meeting_request(message)
            elif message.message_type == "schedule_update_request":
                await self._handle_schedule_update(message)
            elif message.message_type == "availability_check_request":
                await self._handle_availability_check(message)
            elif message.message_type == "calendar_sync_request":
                await self._handle_calendar_sync(message)
            elif message.message_type == "time_optimization_request":
                await self._handle_time_optimization(message)
            elif message.message_type == "recurring_event_request":
                await self._handle_recurring_event(message)
            elif message.message_type == "conflict_resolution_request":
                await self._handle_conflict_resolution(message)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            
    async def _handle_meeting_request(self, message: AgentMessage):
        """Handle meeting scheduling requests"""
        request = message.content
        
        # Extract meeting details
        attendees = request.get('attendees', [])
        duration = request.get('duration', self.scheduling_preferences['default_meeting_duration'])
        preferred_times = request.get('preferred_times', [])
        meeting_type = request.get('meeting_type', 'general')
        priority = request.get('priority', 'normal')
        
        # Find optimal meeting time
        optimal_times = await self._find_optimal_meeting_times(
            attendees, duration, preferred_times, meeting_type, priority
        )
        
        if optimal_times:
            # Schedule the best option
            best_time = optimal_times[0]
            event = await self._create_calendar_event(request, best_time)
            
            # Send confirmation
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="meeting_scheduled_confirmation",
                content={
                    'event': event.__dict__,
                    'alternative_times': [time.__dict__ for time in optimal_times[1:3]],
                    'scheduling_notes': await self._generate_scheduling_notes(event)
                }
            )
            await self.send_message(response)
            
            # Notify attendees
            await self._notify_attendees(event)
            
        else:
            # No suitable time found
            suggestions = await self._generate_scheduling_suggestions(request)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="meeting_scheduling_conflict",
                content={
                    'conflict_reason': 'No suitable time slots available',
                    'suggestions': suggestions,
                    'next_available_slots': await self._find_next_available_slots(attendees, duration)
                }
            )
            await self.send_message(response)
            
    async def _find_optimal_meeting_times(self, attendees: List[str], 
                                        duration: int, preferred_times: List[str],
                                        meeting_type: str, priority: str) -> List[TimeSlot]:
        """Find optimal meeting times for given attendees and constraints"""
        
        # Get time window for search (next 30 days)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        # Generate possible time slots
        possible_slots = await self._generate_time_slots(
            start_date, end_date, duration, meeting_type
        )
        
        # Check availability for each attendee
        available_slots = []
        for slot in possible_slots:
            if await self._check_slot_availability(slot, attendees):
                # Calculate score for this slot
                score = await self._calculate_slot_score(
                    slot, attendees, preferred_times, meeting_type, priority
                )
                slot.score = score
                available_slots.append(slot)
                
        # Sort by score (best first)
        available_slots.sort(key=lambda x: x.score, reverse=True)
        
        return available_slots[:5]  # Return top 5 options
        
    async def _generate_time_slots(self, start_date: datetime, end_date: datetime,
                                 duration: int, meeting_type: str) -> List[TimeSlot]:
        """Generate possible time slots within date range"""
        slots = []
        current_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current_date < end_date:
            # Skip weekends if configured
            if (self.scheduling_preferences['scheduling_restrictions']['no_weekend_meetings'] 
                and current_date.weekday() >= 5):
                current_date += timedelta(days=1)
                continue
                
            # Generate slots for this day
            day_start = current_date.replace(
                hour=int(self.scheduling_preferences['working_hours']['start'].split(':')[0]),
                minute=int(self.scheduling_preferences['working_hours']['start'].split(':')[1])
            )
            day_end = current_date.replace(
                hour=int(self.scheduling_preferences['working_hours']['end'].split(':')[0]),
                minute=int(self.scheduling_preferences['working_hours']['end'].split(':')[1])
            )
            
            slot_start = day_start
            while slot_start + timedelta(minutes=duration) <= day_end:
                slot_end = slot_start + timedelta(minutes=duration)
                
                # Skip lunch time if configured
                lunch_start = current_date.replace(
                    hour=int(self.scheduling_preferences['lunch_break']['start'].split(':')[0]),
                    minute=int(self.scheduling_preferences['lunch_break']['start'].split(':')[1])
                )
                lunch_end = lunch_start + timedelta(minutes=self.scheduling_preferences['lunch_break']['duration'])
                
                if not (slot_start < lunch_end and slot_end > lunch_start):
                    slots.append(TimeSlot(
                        start_time=slot_start,
                        end_time=slot_end,
                        available=True,
                        attendee="",
                        conflict_reason=None
                    ))
                    
                # Move to next slot with buffer
                slot_start += timedelta(minutes=duration + self.scheduling_preferences['buffer_time'])
                
            current_date += timedelta(days=1)
            
        return slots
        
    async def _check_slot_availability(self, slot: TimeSlot, attendees: List[str]) -> bool:
        """Check if time slot is available for all attendees"""
        for attendee in attendees:
            attendee_calendar = self.calendars.get(attendee, [])
            
            for event in attendee_calendar:
                if (slot.start_time < event.end_time and slot.end_time > event.start_time):
                    slot.conflict_reason = f"Conflict with {attendee}'s existing meeting: {event.title}"
                    return False
                    
        return True
        
    async def _calculate_slot_score(self, slot: TimeSlot, attendees: List[str],
                                  preferred_times: List[str], meeting_type: str,
                                  priority: str) -> float:
        """Calculate score for a time slot based on various factors"""
        score = 100.0  # Base score
        
        # Preferred time bonus
        slot_time_str = slot.start_time.strftime('%H:%M')
        if slot_time_str in preferred_times:
            score += 50
            
        # Time of day preferences
        hour = slot.start_time.hour
        if 10 <= hour <= 11 or 14 <= hour <= 15:  # Optimal meeting hours
            score += 30
        elif hour < 9 or hour > 16:  # Less optimal
            score -= 20
            
        # Day of week preferences
        if slot.start_time.weekday() in [0, 1, 2, 3]:  # Monday-Thursday
            score += 10
        elif slot.start_time.weekday() == 4:  # Friday
            score -= 10
            
        # Meeting type optimization
        if meeting_type in ['standup', 'quick_sync'] and hour in [9, 10]:
            score += 20
        elif meeting_type in ['planning', 'review'] and hour in [10, 11, 14, 15]:
            score += 15
            
        # Priority adjustment
        if priority == 'high':
            score += 25
        elif priority == 'low':
            score -= 10
            
        # Attendee count penalty (harder to schedule with more people)
        if len(attendees) > 5:
            score -= len(attendees) * 2
            
        return score
        
    async def _create_calendar_event(self, request: Dict[str, Any], 
                                   time_slot: TimeSlot) -> CalendarEvent:
        """Create a calendar event from meeting request and time slot"""
        event = CalendarEvent(
            event_id=f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=request.get('title', 'Meeting'),
            start_time=time_slot.start_time,
            end_time=time_slot.end_time,
            attendees=request.get('attendees', []),
            location=request.get('location', 'Conference Room / Virtual'),
            event_type=request.get('meeting_type', 'general'),
            priority=request.get('priority', 'normal'),
            description=request.get('description', ''),
            recurring=request.get('recurring', False),
            meeting_url=request.get('meeting_url')
        )
        
        # Add to scheduled events
        self.scheduled_events.append(event)
        
        # Add to each attendee's calendar
        for attendee in event.attendees:
            if attendee not in self.calendars:
                self.calendars[attendee] = []
            self.calendars[attendee].append(event)
            
        return event
        
    async def _notify_attendees(self, event: CalendarEvent):
        """Notify attendees about scheduled meeting"""
        for attendee in event.attendees:
            notification = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=attendee,
                message_type="meeting_invitation",
                content={
                    'event': event.__dict__,
                    'response_required': True,
                    'calendar_link': await self._generate_calendar_link(event)
                }
            )
            await self.send_message(notification)
            
    async def _handle_availability_check(self, message: AgentMessage):
        """Handle availability check requests"""
        request = message.content
        attendees = request.get('attendees', [])
        date_range = request.get('date_range', {})
        duration = request.get('duration', 60)
        
        availability = {}
        
        for attendee in attendees:
            attendee_availability = await self._get_attendee_availability(
                attendee, date_range, duration
            )
            availability[attendee] = attendee_availability
            
        # Find common available times
        common_availability = await self._find_common_availability(availability, duration)
        
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="availability_response",
            content={
                'individual_availability': availability,
                'common_availability': common_availability,
                'optimal_times': await self._rank_available_times(common_availability)
            }
        )
        await self.send_message(response)
        
    async def _get_attendee_availability(self, attendee: str, 
                                       date_range: Dict[str, str],
                                       duration: int) -> List[Dict[str, Any]]:
        """Get availability for a specific attendee"""
        attendee_calendar = self.calendars.get(attendee, [])
        
        start_date = datetime.fromisoformat(date_range.get('start', datetime.now().isoformat()))
        end_date = datetime.fromisoformat(date_range.get('end', (datetime.now() + timedelta(days=7)).isoformat()))
        
        # Generate all possible slots
        all_slots = await self._generate_time_slots(start_date, end_date, duration, 'general')
        
        # Check which slots are free
        available_slots = []
        for slot in all_slots:
            is_free = True
            for event in attendee_calendar:
                if (slot.start_time < event.end_time and slot.end_time > event.start_time):
                    is_free = False
                    break
                    
            if is_free:
                available_slots.append({
                    'start_time': slot.start_time.isoformat(),
                    'end_time': slot.end_time.isoformat(),
                    'duration': duration
                })
                
        return available_slots
        
    async def _find_common_availability(self, availability: Dict[str, List], 
                                      duration: int) -> List[Dict[str, str]]:
        """Find time slots available to all attendees"""
        if not availability:
            return []
            
        # Start with first attendee's availability
        common_slots = set()
        attendees = list(availability.keys())
        
        if attendees:
            first_attendee_slots = availability[attendees[0]]
            for slot in first_attendee_slots:
                slot_key = f"{slot['start_time']}_{slot['end_time']}"
                common_slots.add(slot_key)
                
        # Intersect with other attendees' availability
        for attendee in attendees[1:]:
            attendee_slots = set()
            for slot in availability[attendee]:
                slot_key = f"{slot['start_time']}_{slot['end_time']}"
                attendee_slots.add(slot_key)
                
            common_slots = common_slots.intersection(attendee_slots)
            
        # Convert back to slot format
        common_availability = []
        for slot_key in common_slots:
            start_time_str, end_time_str = slot_key.split('_')
            common_availability.append({
                'start_time': start_time_str,
                'end_time': end_time_str,
                'duration': duration
            })
            
        return common_availability

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the Calendar Management Agent"""
        today = datetime.now().date()
        today_events = [event for event in self.scheduled_events 
                       if event.start_time.date() == today]
        
        upcoming_events = [event for event in self.scheduled_events 
                          if event.start_time > datetime.now()]
        
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'total_events_scheduled': len(self.scheduled_events),
            'events_today': len(today_events),
            'upcoming_events': len(upcoming_events),
            'managed_calendars': len(self.calendars),
            'recurring_events': len(self.recurring_events),
            'supported_time_zones': len(self.time_zones)
        }
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process assigned tasks"""
        try:
            task_type = task.get('type', 'unknown')
            
            if task_type == 'status_check':
                return {"status": "completed", "agent_status": "active"}
            elif task_type == 'ping':
                return {"status": "completed", "response": "pong"}
            else:
                return {"status": "failed", "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages from other agents"""
        try:
            # Default handling - can be overridden by specific agents
            self.logger.info(f"Received message of type: {message.message_type}")
            
            if message.message_type == "ping":
                response = AgentMessage(
                    id=str(uuid.uuid4()),
                    source_agent=self.agent_id,
                    target_agent=message.source_agent,
                    message_type="pong",
                    payload={"response": "pong"},
                    timestamp=datetime.now()
                )
                return response
            
            self.performance_metrics["messages_processed"] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            self.performance_metrics["errors"] += 1
            return None

