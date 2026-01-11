"""
Base model class for all domain entities.

Provides common functionality for validation, serialization,
and equality comparison.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


class BaseModel(ABC):
    """
    Abstract base class for all domain models.
    
    Provides:
    - Unique ID generation
    - Timestamp tracking (created_at, updated_at)
    - Validation framework
    - Serialization to dictionary
    - Equality comparison
    """
    
    def __init__(self, id: str = None, created_at: datetime = None, updated_at: datetime = None):
        """
        Initialize base model.
        
        Args:
            id: Unique identifier (generated if not provided)
            created_at: Creation timestamp (set to now if not provided)
            updated_at: Last update timestamp (set to now if not provided)
        """
        self.id = id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    @abstractmethod
    def validate(self) -> None:
        """
        Validate the model's data.
        
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary representation.
        
        Returns:
            Dictionary with all model attributes
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, BaseModel):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [item.to_dict() if isinstance(item, BaseModel) else item for item in value]
            elif hasattr(value, 'value'):  # Enum
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now(timezone.utc)
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, BaseModel):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Generate hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}(id={self.id})"
