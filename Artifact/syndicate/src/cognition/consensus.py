"""
Consensus System - Routes proposals through Discord community voting or email escalation.

Provides:
- Discord integration for community voting on medium-impact proposals
- Email escalation for high-impact proposals requiring dev review
- Voting periods with configurable thresholds
- Full audit trail of votes and decisions
"""

import os
import json
import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import uuid

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class VoteType(Enum):
    """Types of votes."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    REQUEST_CHANGES = "request_changes"


class EscalationLevel(Enum):
    """Escalation levels for proposals."""
    COMMUNITY = "community"  # Discord voting
    SENIOR_REVIEW = "senior_review"  # Email to senior devs
    EXECUTIVE = "executive"  # Email to executives
    EMERGENCY = "emergency"  # Immediate escalation


@dataclass
class Vote:
    """A single vote on a proposal."""
    id: str
    voter_id: str
    voter_name: str
    vote_type: VoteType
    comment: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    platform: str = "discord"  # discord, email, api


@dataclass
class VotingSession:
    """A voting session for a proposal."""
    id: str
    proposal_id: str
    title: str
    summary: str
    impact_level: str  # low, medium, high, critical
    
    # Voting configuration
    voting_period_hours: int = 24
    approval_threshold: float = 0.6  # 60% approval needed
    minimum_votes: int = 3
    
    # State
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    closes_at: str = ""
    status: str = "open"  # open, closed, approved, rejected, escalated
    
    # Votes
    votes: List[Vote] = field(default_factory=list)
    
    # Discord integration
    discord_message_id: Optional[str] = None
    discord_channel_id: Optional[str] = None
    
    # Email tracking
    emails_sent: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.closes_at:
            close_time = datetime.now() + timedelta(hours=self.voting_period_hours)
            self.closes_at = close_time.isoformat()
    
    def add_vote(self, voter_id: str, voter_name: str, vote_type: VoteType, 
                 comment: Optional[str] = None, platform: str = "discord") -> Vote:
        """Add a vote to the session."""
        # Check if voter already voted
        for v in self.votes:
            if v.voter_id == voter_id:
                # Update existing vote
                v.vote_type = vote_type
                v.comment = comment
                v.timestamp = datetime.now().isoformat()
                return v
        
        vote = Vote(
            id=f"vote_{uuid.uuid4().hex[:8]}",
            voter_id=voter_id,
            voter_name=voter_name,
            vote_type=vote_type,
            comment=comment,
            platform=platform
        )
        self.votes.append(vote)
        return vote
    
    def tally(self) -> Dict[str, Any]:
        """Get vote tally."""
        tally = {
            VoteType.APPROVE.value: 0,
            VoteType.REJECT.value: 0,
            VoteType.ABSTAIN.value: 0,
            VoteType.REQUEST_CHANGES.value: 0
        }
        for vote in self.votes:
            tally[vote.vote_type.value] += 1
        
        total = len(self.votes)
        voting_total = total - tally[VoteType.ABSTAIN.value]
        approval_rate = tally[VoteType.APPROVE.value] / voting_total if voting_total > 0 else 0
        
        return {
            "total_votes": total,
            "voting_total": voting_total,
            "approve": tally[VoteType.APPROVE.value],
            "reject": tally[VoteType.REJECT.value],
            "abstain": tally[VoteType.ABSTAIN.value],
            "request_changes": tally[VoteType.REQUEST_CHANGES.value],
            "approval_rate": approval_rate,
            "meets_threshold": approval_rate >= self.approval_threshold,
            "meets_minimum": total >= self.minimum_votes,
            "can_decide": total >= self.minimum_votes and voting_total > 0
        }
    
    def is_expired(self) -> bool:
        """Check if voting period has expired."""
        return datetime.now() >= datetime.fromisoformat(self.closes_at)
    
    def finalize(self) -> str:
        """Finalize voting and determine outcome."""
        tally = self.tally()
        
        if not tally["can_decide"]:
            self.status = "no_quorum"
            return "no_quorum"
        
        if tally["meets_threshold"]:
            self.status = "approved"
            return "approved"
        else:
            self.status = "rejected"
            return "rejected"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "proposal_id": self.proposal_id,
            "title": self.title,
            "summary": self.summary,
            "impact_level": self.impact_level,
            "voting_period_hours": self.voting_period_hours,
            "approval_threshold": self.approval_threshold,
            "minimum_votes": self.minimum_votes,
            "created_at": self.created_at,
            "closes_at": self.closes_at,
            "status": self.status,
            "votes": [{
                "id": v.id,
                "voter_id": v.voter_id,
                "voter_name": v.voter_name,
                "vote_type": v.vote_type.value,  # Convert enum to string
                "comment": v.comment,
                "timestamp": v.timestamp,
                "platform": v.platform
            } for v in self.votes],
            "discord_message_id": self.discord_message_id,
            "discord_channel_id": self.discord_channel_id,
            "emails_sent": self.emails_sent,
            "tally": self.tally()
        }


class ConsensusSystem:
    """
    Manages proposal consensus through Discord voting and email escalation.
    
    Impact routing:
    - low: Auto-approve, log only
    - medium: Discord community vote
    - high: Email to dev team + Discord notification
    - critical: Email to executives + immediate escalation
    """
    
    def __init__(
        self,
        data_dir: str = "./data/consensus",
        discord_webhook_url: Optional[str] = None,
        discord_channel_id: Optional[str] = None,
        email_config: Optional[Dict[str, str]] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logger or logging.getLogger(__name__)
        
        # Discord config - try consensus-specific first, then fall back to general webhook
        self.discord_webhook_url = discord_webhook_url or os.getenv("DISCORD_CONSENSUS_WEBHOOK") or os.getenv("DISCORD_WEBHOOK_URL")
        self.discord_channel_id = discord_channel_id or os.getenv("DISCORD_CONSENSUS_CHANNEL_ID") or os.getenv("DISCORD_CHANNEL_ID")
        
        # Email config
        self.email_config = email_config or {
            "smtp_host": os.getenv("SMTP_HOST", "smtp.hostinger.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "465")),
            "smtp_ssl": os.getenv("SMTP_SSL", "true").lower() == "true",
            "smtp_user": os.getenv("SMTP_USER", ""),
            "smtp_password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("EMAIL_FROM", os.getenv("FROM_EMAIL", "support@artifactvirtual.com")),
            "dev_team_emails": [e.strip() for e in os.getenv("DEV_TEAM_EMAILS", os.getenv("ESCALATION_EMAIL", "")).split(",") if e.strip()],
            "executive_emails": [e.strip() for e in os.getenv("EXECUTIVE_EMAILS", os.getenv("ESCALATION_EMAIL", "")).split(",") if e.strip()],
        }
        
        # Load sessions
        self.sessions: Dict[str, VotingSession] = {}
        self._load_sessions()
    
    def _load_sessions(self):
        """Load existing voting sessions."""
        sessions_file = self.data_dir / "sessions.json"
        if sessions_file.exists():
            with open(sessions_file) as f:
                data = json.load(f)
                for session_data in data.get("sessions", []):
                    # Reconstruct votes
                    votes = []
                    for v in session_data.get("votes", []):
                        votes.append(Vote(
                            id=v["id"],
                            voter_id=v["voter_id"],
                            voter_name=v["voter_name"],
                            vote_type=VoteType(v["vote_type"]),
                            comment=v.get("comment"),
                            timestamp=v["timestamp"],
                            platform=v.get("platform", "discord")
                        ))
                    
                    session = VotingSession(
                        id=session_data["id"],
                        proposal_id=session_data["proposal_id"],
                        title=session_data["title"],
                        summary=session_data["summary"],
                        impact_level=session_data["impact_level"],
                        voting_period_hours=session_data.get("voting_period_hours", 24),
                        approval_threshold=session_data.get("approval_threshold", 0.6),
                        minimum_votes=session_data.get("minimum_votes", 3),
                        created_at=session_data["created_at"],
                        closes_at=session_data["closes_at"],
                        status=session_data["status"],
                        votes=votes,
                        discord_message_id=session_data.get("discord_message_id"),
                        discord_channel_id=session_data.get("discord_channel_id"),
                        emails_sent=session_data.get("emails_sent", [])
                    )
                    self.sessions[session.id] = session
    
    def _save_sessions(self):
        """Save voting sessions to disk."""
        sessions_file = self.data_dir / "sessions.json"
        data = {
            "sessions": [s.to_dict() for s in self.sessions.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(sessions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_session(
        self,
        proposal_id: str,
        title: str,
        summary: str,
        impact_level: str,
        voting_period_hours: int = 24,
        approval_threshold: float = 0.6,
        minimum_votes: int = 3
    ) -> VotingSession:
        """Create a new voting session for a proposal."""
        session = VotingSession(
            id=f"session_{uuid.uuid4().hex[:12]}",
            proposal_id=proposal_id,
            title=title,
            summary=summary,
            impact_level=impact_level,
            voting_period_hours=voting_period_hours,
            approval_threshold=approval_threshold,
            minimum_votes=minimum_votes
        )
        self.sessions[session.id] = session
        self._save_sessions()
        
        self.logger.info(f"Created voting session {session.id} for proposal {proposal_id}")
        return session
    
    async def route_proposal(
        self,
        proposal_id: str,
        title: str,
        summary: str,
        impact_level: str,
        items: List[Dict[str, Any]] = None,
        category: str = "general"
    ) -> Dict[str, Any]:
        """
        Route a proposal based on impact level.
        
        - low: Auto-approve
        - medium: Discord community vote
        - high/critical: Email escalation + Discord notification
        """
        result = {
            "proposal_id": proposal_id,
            "impact_level": impact_level,
            "action": None,
            "session_id": None,
            "discord_sent": False,
            "email_sent": False,
            "auto_approved": False
        }
        
        if impact_level == "low":
            # Auto-approve low impact
            result["action"] = "auto_approved"
            result["auto_approved"] = True
            self.logger.info(f"Auto-approved low-impact proposal {proposal_id}")
            
        elif impact_level == "medium":
            # Create voting session and send to Discord
            session = self.create_session(
                proposal_id=proposal_id,
                title=title,
                summary=summary,
                impact_level=impact_level
            )
            result["session_id"] = session.id
            result["action"] = "community_vote"
            
            # Send to Discord
            discord_result = await self._send_discord_vote(session, items)
            result["discord_sent"] = discord_result.get("success", False)
            
        elif impact_level in ("high", "critical"):
            # Create session for tracking
            session = self.create_session(
                proposal_id=proposal_id,
                title=title,
                summary=summary,
                impact_level=impact_level,
                voting_period_hours=48,  # Longer for high-impact
                minimum_votes=5
            )
            result["session_id"] = session.id
            result["action"] = "email_escalation"
            
            # Send email
            email_result = await self._send_email_escalation(
                session, 
                items,
                escalation_level=EscalationLevel.SENIOR_REVIEW if impact_level == "high" else EscalationLevel.EXECUTIVE
            )
            result["email_sent"] = email_result.get("success", False)
            
            # Also notify Discord
            discord_result = await self._send_discord_notification(session, "escalated")
            result["discord_sent"] = discord_result.get("success", False)
        
        return result
    
    async def _send_discord_vote(
        self, 
        session: VotingSession,
        items: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send voting embed to Discord."""
        if not self.discord_webhook_url:
            self.logger.warning("Discord webhook URL not configured")
            return {"success": False, "error": "No webhook URL"}
        
        if not HTTPX_AVAILABLE:
            self.logger.warning("httpx not available for Discord integration")
            return {"success": False, "error": "httpx not installed"}
        
        # Build embed
        items_text = ""
        if items:
            for i, item in enumerate(items[:5]):
                items_text += f"• {item.get('description', 'No description')[:100]}\n"
        
        embed = {
            "title": f"🗳️ Proposal: {session.title}",
            "description": session.summary[:2000],
            "color": 0x5865F2,  # Discord blurple
            "fields": [
                {"name": "Impact", "value": session.impact_level.upper(), "inline": True},
                {"name": "Voting Closes", "value": f"<t:{int(datetime.fromisoformat(session.closes_at).timestamp())}:R>", "inline": True},
                {"name": "Threshold", "value": f"{int(session.approval_threshold * 100)}% approval", "inline": True},
            ],
            "footer": {"text": f"Session: {session.id} | Proposal: {session.proposal_id}"},
            "timestamp": session.created_at
        }
        
        if items_text:
            embed["fields"].append({"name": "Changes", "value": items_text[:1000], "inline": False})
        
        embed["fields"].append({
            "name": "How to Vote",
            "value": "React: ✅ Approve | ❌ Reject | ⏸️ Abstain | 🔄 Request Changes",
            "inline": False
        })
        
        payload = {
            "embeds": [embed],
            "username": "Gladius Consensus",
            "avatar_url": "https://raw.githubusercontent.com/amuzetnoM/gladius/main/docs/images/gladius-icon.png"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.discord_webhook_url,
                    json=payload,
                    params={"wait": "true"}
                )
                if response.status_code == 200:
                    data = response.json()
                    session.discord_message_id = data.get("id")
                    session.discord_channel_id = data.get("channel_id")
                    self._save_sessions()
                    self.logger.info(f"Sent Discord vote for session {session.id}")
                    return {"success": True, "message_id": session.discord_message_id}
                else:
                    self.logger.error(f"Discord webhook failed: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            self.logger.error(f"Discord send error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_discord_notification(
        self,
        session: VotingSession,
        notification_type: str
    ) -> Dict[str, Any]:
        """Send a notification to Discord (not a vote)."""
        if not self.discord_webhook_url or not HTTPX_AVAILABLE:
            return {"success": False}
        
        color_map = {
            "escalated": 0xFF9900,  # Orange
            "approved": 0x00FF00,  # Green
            "rejected": 0xFF0000,  # Red
            "expired": 0x808080,  # Gray
        }
        
        title_map = {
            "escalated": "⚠️ Proposal Escalated to Dev Team",
            "approved": "✅ Proposal Approved",
            "rejected": "❌ Proposal Rejected",
            "expired": "⏰ Voting Session Expired",
        }
        
        embed = {
            "title": title_map.get(notification_type, "📢 Proposal Update"),
            "description": f"**{session.title}**\n\n{session.summary[:500]}",
            "color": color_map.get(notification_type, 0x5865F2),
            "fields": [
                {"name": "Impact", "value": session.impact_level.upper(), "inline": True},
                {"name": "Status", "value": notification_type.upper(), "inline": True},
            ],
            "footer": {"text": f"Proposal: {session.proposal_id}"},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.discord_webhook_url,
                    json={"embeds": [embed], "username": "Gladius Consensus"}
                )
                return {"success": response.status_code == 200}
        except Exception as e:
            self.logger.error(f"Discord notification error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_email_escalation(
        self,
        session: VotingSession,
        items: List[Dict[str, Any]] = None,
        escalation_level: EscalationLevel = EscalationLevel.SENIOR_REVIEW
    ) -> Dict[str, Any]:
        """Send email escalation for high-impact proposals."""
        recipients = []
        if escalation_level == EscalationLevel.SENIOR_REVIEW:
            recipients = [e.strip() for e in self.email_config.get("dev_team_emails", []) if e.strip()]
        elif escalation_level == EscalationLevel.EXECUTIVE:
            recipients = [e.strip() for e in self.email_config.get("executive_emails", []) if e.strip()]
            recipients.extend([e.strip() for e in self.email_config.get("dev_team_emails", []) if e.strip()])
        
        if not recipients:
            self.logger.warning("No email recipients configured")
            return {"success": False, "error": "No recipients"}
        
        # Build email
        items_html = ""
        if items:
            items_html = "<ul>"
            for item in items:
                items_html += f"<li><strong>{item.get('description', '')}</strong><br>Impact: {item.get('impact', 'N/A')} | Risk: {item.get('risk', 'N/A')}</li>"
            items_html += "</ul>"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🔔 {escalation_level.value.replace('_', ' ').title()} Required</h2>
            <h3>{session.title}</h3>
            <p><strong>Impact Level:</strong> {session.impact_level.upper()}</p>
            <p><strong>Proposal ID:</strong> {session.proposal_id}</p>
            <hr>
            <h4>Summary</h4>
            <p>{session.summary}</p>
            {f'<h4>Proposed Changes</h4>{items_html}' if items_html else ''}
            <hr>
            <p><strong>Response Required By:</strong> {session.closes_at}</p>
            <p>Reply to this email with your decision: APPROVE, REJECT, or REQUEST_CHANGES</p>
            <p style="color: #666; font-size: 12px;">Session ID: {session.id}</p>
        </body>
        </html>
        """
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[GLADIUS] {escalation_level.value.upper()}: {session.title}"
            msg["From"] = self.email_config.get("from_email", "gladius@artifactvirtual.com")
            msg["To"] = ", ".join(recipients)
            
            msg.attach(MIMEText(html_body, "html"))
            
            # Send email
            smtp_host = self.email_config.get("smtp_host", "smtp.gmail.com")
            smtp_port = self.email_config.get("smtp_port", 587)
            smtp_user = self.email_config.get("smtp_user", "")
            smtp_password = self.email_config.get("smtp_password", "")
            use_ssl = self.email_config.get("smtp_ssl", smtp_port == 465)
            
            if not smtp_user or not smtp_password:
                self.logger.warning("SMTP credentials not configured")
                return {"success": False, "error": "SMTP not configured"}
            
            # Use SSL for port 465, STARTTLS for 587
            if use_ssl or smtp_port == 465:
                import ssl
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
            
            # Record email sent
            session.emails_sent.append({
                "timestamp": datetime.now().isoformat(),
                "recipients": recipients,
                "escalation_level": escalation_level.value
            })
            self._save_sessions()
            
            self.logger.info(f"Sent email escalation for session {session.id} to {len(recipients)} recipients")
            return {"success": True, "recipients": len(recipients)}
            
        except Exception as e:
            self.logger.error(f"Email send error: {e}")
            return {"success": False, "error": str(e)}
    
    def record_vote(
        self,
        session_id: str,
        voter_id: str,
        voter_name: str,
        vote_type: str,
        comment: Optional[str] = None,
        platform: str = "discord"
    ) -> Optional[Dict[str, Any]]:
        """Record a vote on a session."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if session.status != "open":
            return {"error": "Voting session is closed"}
        
        vote = session.add_vote(
            voter_id=voter_id,
            voter_name=voter_name,
            vote_type=VoteType(vote_type),
            comment=comment,
            platform=platform
        )
        self._save_sessions()
        
        return {
            "vote_id": vote.id,
            "session_id": session_id,
            "tally": session.tally()
        }
    
    def check_and_finalize_sessions(self) -> List[Dict[str, Any]]:
        """Check all open sessions and finalize expired ones."""
        finalized = []
        
        for session in self.sessions.values():
            if session.status == "open" and session.is_expired():
                outcome = session.finalize()
                self._save_sessions()
                finalized.append({
                    "session_id": session.id,
                    "proposal_id": session.proposal_id,
                    "outcome": outcome,
                    "tally": session.tally()
                })
                self.logger.info(f"Finalized session {session.id}: {outcome}")
        
        return finalized
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a voting session by ID."""
        session = self.sessions.get(session_id)
        return session.to_dict() if session else None
    
    def get_open_sessions(self) -> List[Dict[str, Any]]:
        """Get all open voting sessions."""
        return [s.to_dict() for s in self.sessions.values() if s.status == "open"]
    
    def stats(self) -> Dict[str, Any]:
        """Get consensus system statistics."""
        sessions = list(self.sessions.values())
        return {
            "total_sessions": len(sessions),
            "open_sessions": sum(1 for s in sessions if s.status == "open"),
            "approved": sum(1 for s in sessions if s.status == "approved"),
            "rejected": sum(1 for s in sessions if s.status == "rejected"),
            "total_votes": sum(len(s.votes) for s in sessions),
            "discord_configured": bool(self.discord_webhook_url),
            "email_configured": bool(self.email_config.get("smtp_user"))
        }
