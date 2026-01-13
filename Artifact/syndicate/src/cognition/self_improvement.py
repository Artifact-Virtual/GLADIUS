"""
Self-Improvement Engine - Autonomous learning loop with full audit trail.

Provides:
- Proposal generation for system improvements
- Review and iteration cycles
- Implementation planning with checklists
- Full audit trail of all decisions
- Snapshot management for rollback
"""

import os
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import uuid


class ProposalStatus(Enum):
    """Status of an improvement proposal."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTING = "implementing"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


class ImprovementCategory(Enum):
    """Categories of improvements."""
    COGNITION = "cognition"
    MEMORY = "memory"
    TOOLS = "tools"
    STRUCTURE = "structure"
    AUTOMATION = "automation"
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    DOCUMENTATION = "documentation"


@dataclass
class ProposalItem:
    """A single item within a proposal."""
    id: str
    description: str
    rationale: str
    impact: str  # high, medium, low
    risk: str  # high, medium, low
    estimated_effort: str  # hours or complexity
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ReviewComment:
    """A review comment on a proposal."""
    id: str
    reviewer: str
    comment: str
    action: str  # approve, request_changes, reject
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ChecklistItem:
    """An item in an implementation checklist."""
    id: str
    task: str
    completed: bool = False
    completed_at: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Snapshot:
    """A system state snapshot for rollback."""
    id: str
    name: str
    description: str
    created_at: str
    files_backed_up: List[str]
    database_backup: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImprovementProposal:
    """
    A complete improvement proposal with full audit trail.
    
    Tracks the entire lifecycle from draft to implementation.
    """
    id: str
    title: str
    category: ImprovementCategory
    status: ProposalStatus
    
    # Content
    summary: str
    items: List[ProposalItem] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "cognition_engine"
    
    # Review history
    reviews: List[ReviewComment] = field(default_factory=list)
    revision_count: int = 0
    
    # Implementation
    implementation_plan: Optional[str] = None
    checklist: List[ChecklistItem] = field(default_factory=list)
    blueprint: Optional[Dict[str, Any]] = None
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Snapshots
    pre_implementation_snapshot: Optional[str] = None
    post_implementation_snapshot: Optional[str] = None
    
    def add_review(self, reviewer: str, comment: str, action: str):
        """Add a review comment."""
        self.reviews.append(ReviewComment(
            id=f"review_{len(self.reviews)}",
            reviewer=reviewer,
            comment=comment,
            action=action
        ))
        self.updated_at = datetime.now().isoformat()
        
        if action == "approve":
            self.status = ProposalStatus.APPROVED
        elif action == "request_changes":
            self.status = ProposalStatus.REVISION_REQUESTED
            self.revision_count += 1
        elif action == "reject":
            self.status = ProposalStatus.REJECTED
    
    def add_checklist_item(self, task: str) -> str:
        """Add an item to the implementation checklist."""
        item_id = f"check_{len(self.checklist)}"
        self.checklist.append(ChecklistItem(id=item_id, task=task))
        return item_id
    
    def complete_checklist_item(self, item_id: str, notes: Optional[str] = None):
        """Mark a checklist item as complete."""
        for item in self.checklist:
            if item.id == item_id:
                item.completed = True
                item.completed_at = datetime.now().isoformat()
                item.notes = notes
                break
    
    def log_execution(self, action: str, details: Dict[str, Any]):
        """Log an execution action."""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        })
    
    def progress(self) -> float:
        """Get implementation progress (0-100)."""
        if not self.checklist:
            return 0.0
        completed = sum(1 for item in self.checklist if item.completed)
        return (completed / len(self.checklist)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category.value,
            "status": self.status.value,
            "summary": self.summary,
            "items": [asdict(i) for i in self.items],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "reviews": [asdict(r) for r in self.reviews],
            "revision_count": self.revision_count,
            "implementation_plan": self.implementation_plan,
            "checklist": [asdict(c) for c in self.checklist],
            "blueprint": self.blueprint,
            "execution_log": self.execution_log,
            "pre_implementation_snapshot": self.pre_implementation_snapshot,
            "post_implementation_snapshot": self.post_implementation_snapshot,
            "progress": self.progress()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImprovementProposal':
        """Create from dictionary."""
        proposal = cls(
            id=data["id"],
            title=data["title"],
            category=ImprovementCategory(data["category"]),
            status=ProposalStatus(data["status"]),
            summary=data["summary"]
        )
        
        proposal.items = [ProposalItem(**i) for i in data.get("items", [])]
        proposal.created_at = data.get("created_at", proposal.created_at)
        proposal.updated_at = data.get("updated_at", proposal.updated_at)
        proposal.created_by = data.get("created_by", "unknown")
        proposal.reviews = [ReviewComment(**r) for r in data.get("reviews", [])]
        proposal.revision_count = data.get("revision_count", 0)
        proposal.implementation_plan = data.get("implementation_plan")
        proposal.checklist = [ChecklistItem(**c) for c in data.get("checklist", [])]
        proposal.blueprint = data.get("blueprint")
        proposal.execution_log = data.get("execution_log", [])
        proposal.pre_implementation_snapshot = data.get("pre_implementation_snapshot")
        proposal.post_implementation_snapshot = data.get("post_implementation_snapshot")
        
        return proposal


class SelfImprovementEngine:
    """
    Autonomous self-improvement engine with full audit trail.
    
    Manages the complete lifecycle of system improvements:
    1. Proposal generation (from cognition analysis)
    2. Review cycles (with iteration requests)
    3. Implementation planning (checklists, blueprints)
    4. Execution with snapshots
    5. Full audit trail
    """
    
    def __init__(
        self,
        base_dir: str = ".",
        proposals_dir: str = "./data/improvements/proposals",
        snapshots_dir: str = "./data/improvements/snapshots",
        logger: Optional[logging.Logger] = None
    ):
        self.base_dir = Path(base_dir).resolve()
        self.proposals_dir = Path(proposals_dir)
        self.snapshots_dir = Path(snapshots_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        # Create directories
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing proposals
        self.proposals: Dict[str, ImprovementProposal] = {}
        self.snapshots: Dict[str, Snapshot] = {}
        self._load_state()
        
        self.logger.info(f"[IMPROVE] Initialized with {len(self.proposals)} proposals, {len(self.snapshots)} snapshots")
    
    def _load_state(self):
        """Load existing proposals and snapshots."""
        # Load proposals
        for f in self.proposals_dir.glob("*.json"):
            try:
                with open(f, 'r') as fp:
                    data = json.load(fp)
                    proposal = ImprovementProposal.from_dict(data)
                    self.proposals[proposal.id] = proposal
            except Exception as e:
                self.logger.warning(f"[IMPROVE] Failed to load proposal {f}: {e}")
        
        # Load snapshots index
        snapshots_index = self.snapshots_dir / "index.json"
        if snapshots_index.exists():
            try:
                with open(snapshots_index, 'r') as f:
                    index = json.load(f)
                    for sid, sdata in index.items():
                        self.snapshots[sid] = Snapshot(**sdata)
            except Exception as e:
                self.logger.warning(f"[IMPROVE] Failed to load snapshots index: {e}")
    
    def _save_proposal(self, proposal: ImprovementProposal):
        """Save a proposal to disk."""
        path = self.proposals_dir / f"{proposal.id}.json"
        with open(path, 'w') as f:
            json.dump(proposal.to_dict(), f, indent=2)
    
    def _save_snapshots_index(self):
        """Save snapshots index."""
        index_path = self.snapshots_dir / "index.json"
        index = {sid: asdict(s) for sid, s in self.snapshots.items()}
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
    
    # ==================== Proposal Management ====================
    
    def create_proposal(
        self,
        title: str,
        category: ImprovementCategory,
        summary: str,
        items: Optional[List[Dict[str, Any]]] = None
    ) -> ImprovementProposal:
        """
        Create a new improvement proposal.
        
        Args:
            title: Proposal title
            category: Category of improvement
            summary: Brief summary of the proposal
            items: List of specific items to implement
        
        Returns:
            Created proposal
        """
        proposal_id = f"prop_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        proposal = ImprovementProposal(
            id=proposal_id,
            title=title,
            category=category,
            status=ProposalStatus.DRAFT,
            summary=summary
        )
        
        # Add items
        if items:
            for i, item_data in enumerate(items):
                proposal.items.append(ProposalItem(
                    id=f"{proposal_id}_item_{i}",
                    description=item_data.get("description", ""),
                    rationale=item_data.get("rationale", ""),
                    impact=item_data.get("impact", "medium"),
                    risk=item_data.get("risk", "low"),
                    estimated_effort=item_data.get("effort", "unknown"),
                    dependencies=item_data.get("dependencies", [])
                ))
        
        self.proposals[proposal_id] = proposal
        self._save_proposal(proposal)
        
        self.logger.info(f"[IMPROVE] Created proposal: {proposal_id} - {title}")
        return proposal
    
    def submit_for_review(self, proposal_id: str) -> bool:
        """Submit a proposal for review."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        if proposal.status != ProposalStatus.DRAFT:
            self.logger.warning(f"[IMPROVE] Proposal {proposal_id} not in DRAFT status")
            return False
        
        proposal.status = ProposalStatus.PENDING_REVIEW
        proposal.updated_at = datetime.now().isoformat()
        self._save_proposal(proposal)
        
        self.logger.info(f"[IMPROVE] Submitted for review: {proposal_id}")
        return True
    
    async def route_to_consensus(
        self,
        proposal_id: str,
        consensus_system: 'ConsensusSystem'  # Type hint as string to avoid circular import
    ) -> Dict[str, Any]:
        """
        Route a proposal through the consensus system based on impact level.
        
        - low impact: Auto-approve
        - medium impact: Discord community vote
        - high/critical: Email escalation
        """
        if proposal_id not in self.proposals:
            return {"error": "Proposal not found"}
        
        proposal = self.proposals[proposal_id]
        
        # Determine impact level from items
        impacts = [item.impact for item in proposal.items]
        if "critical" in impacts or "high" in impacts:
            impact_level = "high"
        elif "medium" in impacts:
            impact_level = "medium"
        else:
            impact_level = "low"
        
        # Route through consensus
        result = await consensus_system.route_proposal(
            proposal_id=proposal_id,
            title=proposal.title,
            summary=proposal.summary,
            impact_level=impact_level,
            items=[{
                "description": item.description,
                "impact": item.impact,
                "risk": item.risk
            } for item in proposal.items],
            category=proposal.category.value
        )
        
        # Update proposal status based on routing
        if result.get("auto_approved"):
            proposal.status = ProposalStatus.APPROVED
            proposal.add_review("consensus_system", "Auto-approved (low impact)", "approve")
        elif result.get("session_id"):
            proposal.status = ProposalStatus.PENDING_REVIEW
            proposal.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": "routed_to_consensus",
                "session_id": result["session_id"],
                "impact_level": impact_level
            })
        
        self._save_proposal(proposal)
        return result
    
    def review_proposal(
        self,
        proposal_id: str,
        reviewer: str,
        action: str,
        comment: str
    ) -> bool:
        """
        Review a proposal.
        
        Args:
            proposal_id: Proposal to review
            reviewer: Reviewer identifier
            action: 'approve', 'request_changes', or 'reject'
            comment: Review comment
        
        Returns:
            True if review was recorded
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        proposal.add_review(reviewer, comment, action)
        self._save_proposal(proposal)
        
        self.logger.info(f"[IMPROVE] Review recorded for {proposal_id}: {action}")
        return True
    
    def revise_proposal(
        self,
        proposal_id: str,
        new_summary: Optional[str] = None,
        new_items: Optional[List[Dict]] = None
    ) -> bool:
        """Revise a proposal after review feedback."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.REVISION_REQUESTED:
            self.logger.warning(f"[IMPROVE] Proposal {proposal_id} not in revision state")
            return False
        
        if new_summary:
            proposal.summary = new_summary
        
        if new_items:
            proposal.items = [
                ProposalItem(
                    id=f"{proposal_id}_item_{i}_r{proposal.revision_count}",
                    description=item.get("description", ""),
                    rationale=item.get("rationale", ""),
                    impact=item.get("impact", "medium"),
                    risk=item.get("risk", "low"),
                    estimated_effort=item.get("effort", "unknown"),
                    dependencies=item.get("dependencies", [])
                )
                for i, item in enumerate(new_items)
            ]
        
        proposal.status = ProposalStatus.PENDING_REVIEW
        proposal.updated_at = datetime.now().isoformat()
        self._save_proposal(proposal)
        
        self.logger.info(f"[IMPROVE] Revised proposal: {proposal_id} (revision {proposal.revision_count})")
        return True
    
    # ==================== Implementation Planning ====================
    
    def create_implementation_plan(
        self,
        proposal_id: str,
        plan: str,
        checklist_items: List[str],
        blueprint: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create an implementation plan for an approved proposal.
        
        Args:
            proposal_id: Proposal to implement
            plan: Detailed implementation plan (markdown)
            checklist_items: List of tasks to complete
            blueprint: Optional structured blueprint
        
        Returns:
            True if plan was created
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.APPROVED:
            self.logger.warning(f"[IMPROVE] Proposal {proposal_id} not approved")
            return False
        
        proposal.implementation_plan = plan
        proposal.blueprint = blueprint
        
        for task in checklist_items:
            proposal.add_checklist_item(task)
        
        proposal.updated_at = datetime.now().isoformat()
        self._save_proposal(proposal)
        
        self.logger.info(f"[IMPROVE] Created implementation plan for {proposal_id} with {len(checklist_items)} tasks")
        return True
    
    # ==================== Snapshots ====================
    
    def create_snapshot(
        self,
        name: str,
        description: str,
        files_to_backup: List[str],
        database_paths: Optional[List[str]] = None
    ) -> Snapshot:
        """
        Create a system state snapshot.
        
        Args:
            name: Snapshot name
            description: Why this snapshot was created
            files_to_backup: List of file paths to backup
            database_paths: Optional database files to backup
        
        Returns:
            Created snapshot
        """
        snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        snapshot_dir = self.snapshots_dir / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        backed_up = []
        
        # Backup files (handle both files and directories)
        for file_path in files_to_backup:
            src = Path(file_path).resolve()
            
            # Skip if the source is inside the snapshots directory (prevent recursion)
            try:
                src.relative_to(self.snapshots_dir.resolve())
                self.logger.debug(f"[IMPROVE] Skipping snapshot dir: {src}")
                continue
            except ValueError:
                pass  # Not inside snapshots dir, safe to backup
            
            if src.exists():
                dest = snapshot_dir / src.name
                if src.is_dir():
                    # Copy directory but exclude snapshots subdirectory
                    if dest.exists():
                        shutil.rmtree(dest)
                    
                    def ignore_snapshots(dir, files):
                        # Ignore any 'snapshots' directory to prevent recursion
                        ignored = []
                        for f in files:
                            full_path = Path(dir) / f
                            if 'snapshots' in str(full_path) or full_path.name.startswith('snap_'):
                                ignored.append(f)
                        return ignored
                    
                    shutil.copytree(src, dest, ignore=ignore_snapshots)
                else:
                    shutil.copy2(src, dest)
                backed_up.append(str(src))
        
        # Backup databases
        db_backup = None
        if database_paths:
            db_dir = snapshot_dir / "databases"
            db_dir.mkdir(exist_ok=True)
            for db_path in database_paths:
                src = Path(db_path)
                if src.exists() and src.is_file():
                    shutil.copy2(src, db_dir / src.name)
            db_backup = str(db_dir)
        
        snapshot = Snapshot(
            id=snapshot_id,
            name=name,
            description=description,
            created_at=datetime.now().isoformat(),
            files_backed_up=backed_up,
            database_backup=db_backup,
            metadata={
                "base_dir": str(self.base_dir),
                "total_files": len(backed_up)
            }
        )
        
        self.snapshots[snapshot_id] = snapshot
        self._save_snapshots_index()
        
        self.logger.info(f"[IMPROVE] Created snapshot: {snapshot_id} ({len(backed_up)} files)")
        return snapshot
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore from a snapshot."""
        if snapshot_id not in self.snapshots:
            self.logger.error(f"[IMPROVE] Snapshot {snapshot_id} not found")
            return False
        
        snapshot = self.snapshots[snapshot_id]
        snapshot_dir = self.snapshots_dir / snapshot_id
        
        if not snapshot_dir.exists():
            self.logger.error(f"[IMPROVE] Snapshot directory not found: {snapshot_dir}")
            return False
        
        # Restore files
        for file_path in snapshot.files_backed_up:
            src = snapshot_dir / Path(file_path).name
            if src.exists():
                dest = Path(file_path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                self.logger.info(f"[IMPROVE] Restored: {dest}")
        
        # Restore databases
        if snapshot.database_backup:
            db_dir = Path(snapshot.database_backup)
            if db_dir.exists():
                for db_file in db_dir.iterdir():
                    # Assuming databases go back to their original locations
                    # This is simplified - in production, store original paths
                    self.logger.info(f"[IMPROVE] Database backup available: {db_file}")
        
        self.logger.info(f"[IMPROVE] Restored snapshot: {snapshot_id}")
        return True
    
    # ==================== Execution ====================
    
    def begin_implementation(self, proposal_id: str) -> bool:
        """Begin implementing an approved proposal."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.APPROVED:
            self.logger.warning(f"[IMPROVE] Proposal {proposal_id} not approved")
            return False
        
        if not proposal.implementation_plan:
            self.logger.warning(f"[IMPROVE] No implementation plan for {proposal_id}")
            return False
        
        # Create pre-implementation snapshot
        files_to_backup = self._get_files_for_category(proposal.category)
        snapshot = self.create_snapshot(
            name=f"pre_{proposal_id}",
            description=f"Pre-implementation snapshot for {proposal.title}",
            files_to_backup=files_to_backup
        )
        proposal.pre_implementation_snapshot = snapshot.id
        
        proposal.status = ProposalStatus.IMPLEMENTING
        proposal.log_execution("started", {"snapshot": snapshot.id})
        proposal.updated_at = datetime.now().isoformat()
        self._save_proposal(proposal)
        
        self.logger.info(f"[IMPROVE] Started implementation: {proposal_id}")
        return True
    
    def complete_task(
        self,
        proposal_id: str,
        task_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Mark an implementation task as complete."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        proposal.complete_checklist_item(task_id, notes)
        proposal.log_execution("task_completed", {"task_id": task_id, "notes": notes})
        proposal.updated_at = datetime.now().isoformat()
        self._save_proposal(proposal)
        
        self.logger.info(f"[IMPROVE] Completed task {task_id} for {proposal_id}")
        return True
    
    def complete_implementation(self, proposal_id: str) -> bool:
        """Mark implementation as complete."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.IMPLEMENTING:
            return False
        
        # Check all tasks completed
        if proposal.progress() < 100:
            self.logger.warning(f"[IMPROVE] Not all tasks complete ({proposal.progress():.1f}%)")
        
        # Create post-implementation snapshot
        files_to_backup = self._get_files_for_category(proposal.category)
        snapshot = self.create_snapshot(
            name=f"post_{proposal_id}",
            description=f"Post-implementation snapshot for {proposal.title}",
            files_to_backup=files_to_backup
        )
        proposal.post_implementation_snapshot = snapshot.id
        
        proposal.status = ProposalStatus.COMPLETED
        proposal.log_execution("completed", {"snapshot": snapshot.id, "progress": proposal.progress()})
        proposal.updated_at = datetime.now().isoformat()
        self._save_proposal(proposal)
        
        self.logger.info(f"[IMPROVE] Completed implementation: {proposal_id}")
        return True
    
    def rollback_implementation(self, proposal_id: str) -> bool:
        """Rollback an implementation to pre-implementation state."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if not proposal.pre_implementation_snapshot:
            self.logger.error(f"[IMPROVE] No pre-implementation snapshot for {proposal_id}")
            return False
        
        success = self.restore_snapshot(proposal.pre_implementation_snapshot)
        
        if success:
            proposal.status = ProposalStatus.ROLLED_BACK
            proposal.log_execution("rolled_back", {"snapshot": proposal.pre_implementation_snapshot})
            proposal.updated_at = datetime.now().isoformat()
            self._save_proposal(proposal)
            
            self.logger.info(f"[IMPROVE] Rolled back: {proposal_id}")
        
        return success
    
    def _get_files_for_category(self, category: ImprovementCategory) -> List[str]:
        """Get relevant files to backup for a category."""
        base = self.base_dir
        
        files = []
        
        if category == ImprovementCategory.COGNITION:
            cognition_dir = base / "Artifact/syndicate/src/cognition"
            if cognition_dir.exists():
                files.extend(str(f) for f in cognition_dir.glob("*.py"))
        
        elif category == ImprovementCategory.MEMORY:
            files.append(str(base / "Artifact/syndicate/src/cognition/memory_module.py"))
            files.append(str(base / "Artifact/syndicate/src/cognition/hektor_store.py"))
        
        elif category == ImprovementCategory.DOCUMENTATION:
            files.extend([
                str(base / "ARCHITECTURE.md"),
                str(base / "COMMANDS.md"),
                str(base / "CONTEXT.md"),
                str(base / "README.md")
            ])
        
        # Filter to existing files
        return [f for f in files if Path(f).exists()]
    
    # ==================== Reporting ====================
    
    def get_proposal(self, proposal_id: str) -> Optional[ImprovementProposal]:
        """Get a proposal by ID."""
        return self.proposals.get(proposal_id)
    
    def list_proposals(
        self,
        status: Optional[ProposalStatus] = None,
        category: Optional[ImprovementCategory] = None
    ) -> List[ImprovementProposal]:
        """List proposals with optional filters."""
        proposals = list(self.proposals.values())
        
        if status:
            proposals = [p for p in proposals if p.status == status]
        
        if category:
            proposals = [p for p in proposals if p.category == category]
        
        return sorted(proposals, key=lambda p: p.created_at, reverse=True)
    
    def get_audit_trail(self, proposal_id: str) -> List[Dict[str, Any]]:
        """Get full audit trail for a proposal."""
        if proposal_id not in self.proposals:
            return []
        
        proposal = self.proposals[proposal_id]
        trail = []
        
        # Creation
        trail.append({
            "timestamp": proposal.created_at,
            "action": "created",
            "details": {"title": proposal.title, "category": proposal.category.value}
        })
        
        # Reviews
        for review in proposal.reviews:
            trail.append({
                "timestamp": review.timestamp,
                "action": f"review_{review.action}",
                "details": {"reviewer": review.reviewer, "comment": review.comment}
            })
        
        # Execution log
        for entry in proposal.execution_log:
            trail.append(entry)
        
        return sorted(trail, key=lambda x: x["timestamp"])
    
    def generate_report(self) -> str:
        """Generate a status report of all improvements."""
        lines = ["# Self-Improvement Status Report", ""]
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("")
        
        # Summary
        by_status = {}
        for p in self.proposals.values():
            status = p.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        lines.append("## Summary")
        lines.append("")
        for status, count in sorted(by_status.items()):
            lines.append(f"- {status}: {count}")
        lines.append("")
        
        # Active proposals
        active = self.list_proposals(status=ProposalStatus.IMPLEMENTING)
        if active:
            lines.append("## Active Implementations")
            lines.append("")
            for p in active:
                lines.append(f"### {p.title}")
                lines.append(f"- ID: {p.id}")
                lines.append(f"- Progress: {p.progress():.1f}%")
                lines.append(f"- Tasks: {len([c for c in p.checklist if c.completed])}/{len(p.checklist)}")
                lines.append("")
        
        # Pending reviews
        pending = self.list_proposals(status=ProposalStatus.PENDING_REVIEW)
        if pending:
            lines.append("## Pending Reviews")
            lines.append("")
            for p in pending:
                lines.append(f"- **{p.title}** ({p.id})")
                lines.append(f"  - Created: {p.created_at}")
                lines.append(f"  - Revisions: {p.revision_count}")
            lines.append("")
        
        # Recent completions
        completed = self.list_proposals(status=ProposalStatus.COMPLETED)[:5]
        if completed:
            lines.append("## Recent Completions")
            lines.append("")
            for p in completed:
                lines.append(f"- {p.title} ({p.updated_at})")
            lines.append("")
        
        # Snapshots
        lines.append("## Snapshots")
        lines.append(f"Total: {len(self.snapshots)}")
        
        return "\n".join(lines)
    
    def stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            "total_proposals": len(self.proposals),
            "by_status": {
                s.value: len([p for p in self.proposals.values() if p.status == s])
                for s in ProposalStatus
            },
            "by_category": {
                c.value: len([p for p in self.proposals.values() if p.category == c])
                for c in ImprovementCategory
            },
            "total_snapshots": len(self.snapshots),
            "total_revisions": sum(p.revision_count for p in self.proposals.values())
        }
    
    # ==================== Obsidian Sync ====================
    
    def sync_to_obsidian(
        self,
        obsidian_dir: str,
        impact_levels: List[str] = ["low", "medium"],
        include_completed: bool = True
    ) -> int:
        """
        Sync proposals to Obsidian for visibility.
        
        Args:
            obsidian_dir: Path to obsidian_sync/gladius directory
            impact_levels: Which impact levels to sync
            include_completed: Whether to include completed proposals
        
        Returns:
            Number of proposals synced
        """
        obsidian_path = Path(obsidian_dir)
        obsidian_path.mkdir(parents=True, exist_ok=True)
        
        synced = 0
        
        for proposal in self.proposals.values():
            # Check impact level
            item_impacts = [item.impact for item in proposal.items]
            max_impact = max(item_impacts) if item_impacts else "low"
            
            if max_impact not in impact_levels:
                continue
            
            # Skip completed unless requested
            if proposal.status == ProposalStatus.COMPLETED and not include_completed:
                continue
            
            # Generate markdown
            md_content = self._proposal_to_markdown(proposal)
            
            # Write to obsidian
            filename = f"{proposal.id}_{proposal.title[:30].replace(' ', '_')}.md"
            filepath = obsidian_path / filename
            
            with open(filepath, 'w') as f:
                f.write(md_content)
            
            synced += 1
            self.logger.info(f"[OBSIDIAN] Synced: {proposal.id}")
        
        # Write index file
        self._write_obsidian_index(obsidian_path)
        
        return synced
    
    def _proposal_to_markdown(self, proposal: ImprovementProposal) -> str:
        """Convert a proposal to Obsidian-compatible markdown."""
        lines = [
            "---",
            f"id: {proposal.id}",
            f"status: {proposal.status.value}",
            f"category: {proposal.category.value}",
            f"created: {proposal.created_at}",
            f"updated: {proposal.updated_at}",
            "tags: [gladius, improvement, system]",
            "---",
            "",
            f"# {proposal.title}",
            "",
            f"> **Status**: {proposal.status.value}  ",
            f"> **Category**: {proposal.category.value}  ",
            f"> **Created**: {proposal.created_at}",
            "",
            "## Summary",
            "",
            proposal.summary,
            "",
            "## Items",
            ""
        ]
        
        for item in proposal.items:
            lines.extend([
                f"### {item.description}",
                f"- **Impact**: {item.impact}",
                f"- **Risk**: {item.risk}",
                f"- **Effort**: {item.estimated_effort}",
                f"- **Rationale**: {item.rationale}",
                ""
            ])
        
        # Reviews
        if proposal.reviews:
            lines.extend(["## Reviews", ""])
            for review in proposal.reviews:
                lines.append(f"- **{review.reviewer}** ({review.action}): {review.comment}")
            lines.append("")
        
        # Checklist
        if proposal.checklist:
            lines.extend(["## Implementation Checklist", ""])
            for item in proposal.checklist:
                status = "x" if item.completed else " "
                lines.append(f"- [{status}] {item.task}")
            lines.append("")
        
        # Implementation plan
        if proposal.implementation_plan:
            lines.extend([
                "## Implementation Plan",
                "",
                proposal.implementation_plan,
                ""
            ])
        
        return "\n".join(lines)
    
    def _write_obsidian_index(self, obsidian_path: Path):
        """Write an index file for Obsidian."""
        proposals_by_status = {}
        for p in self.proposals.values():
            status = p.status.value
            if status not in proposals_by_status:
                proposals_by_status[status] = []
            proposals_by_status[status].append(p)
        
        lines = [
            "---",
            "tags: [gladius, index]",
            "---",
            "",
            "# Gladius Improvement Proposals",
            "",
            f"**Last Updated**: {datetime.now().isoformat()}",
            f"**Total Proposals**: {len(self.proposals)}",
            ""
        ]
        
        for status, proposals in sorted(proposals_by_status.items()):
            lines.append(f"## {status.title()} ({len(proposals)})")
            lines.append("")
            for p in sorted(proposals, key=lambda x: x.updated_at, reverse=True):
                filename = f"{p.id}_{p.title[:30].replace(' ', '_')}"
                lines.append(f"- [[{filename}|{p.title}]] - {p.category.value}")
            lines.append("")
        
        with open(obsidian_path / "_index.md", 'w') as f:
            f.write("\n".join(lines))
