"""
Repository pattern implementation for data persistence.

Provides abstract base class for repositories with CRUD operations.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from datetime import datetime

from .base_model import BaseModel
from .exceptions import DataNotFoundError, RepositoryError

T = TypeVar('T', bound=BaseModel)


class Repository(ABC, Generic[T]):
    """
    Abstract repository providing CRUD operations.
    
    This follows the Repository pattern to abstract data persistence
    and provide a clean interface for data access.
    """
    
    def __init__(self, entity_name: str):
        """
        Initialize repository.
        
        Args:
            entity_name: Name of the entity type for error messages
        """
        self.entity_name = entity_name
        self._storage: Dict[str, T] = {}
    
    def create(self, entity: T) -> T:
        """
        Create a new entity.
        
        Args:
            entity: Entity to create
            
        Returns:
            Created entity
            
        Raises:
            RepositoryError: If creation fails
            ValidationError: If entity validation fails
        """
        try:
            entity.validate()
            if entity.id in self._storage:
                raise RepositoryError(
                    "create",
                    f"{self.entity_name} with ID {entity.id} already exists",
                    self.entity_name
                )
            self._storage[entity.id] = entity
            return entity
        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError("create", str(e), self.entity_name)
    
    def get_by_id(self, entity_id: str) -> T:
        """
        Retrieve entity by ID.
        
        Args:
            entity_id: ID of entity to retrieve
            
        Returns:
            Retrieved entity
            
        Raises:
            DataNotFoundError: If entity not found
        """
        entity = self._storage.get(entity_id)
        if entity is None:
            raise DataNotFoundError(self.entity_name, entity_id)
        return entity
    
    def get_all(self) -> List[T]:
        """
        Retrieve all entities.
        
        Returns:
            List of all entities
        """
        return list(self._storage.values())
    
    def update(self, entity: T) -> T:
        """
        Update an existing entity.
        
        Args:
            entity: Entity to update
            
        Returns:
            Updated entity
            
        Raises:
            DataNotFoundError: If entity not found
            ValidationError: If entity validation fails
        """
        if entity.id not in self._storage:
            raise DataNotFoundError(self.entity_name, entity.id)
        
        entity.validate()
        entity.update_timestamp()
        self._storage[entity.id] = entity
        return entity
    
    def delete(self, entity_id: str) -> None:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: ID of entity to delete
            
        Raises:
            DataNotFoundError: If entity not found
        """
        if entity_id not in self._storage:
            raise DataNotFoundError(self.entity_name, entity_id)
        del self._storage[entity_id]
    
    def exists(self, entity_id: str) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: ID of entity to check
            
        Returns:
            True if entity exists, False otherwise
        """
        return entity_id in self._storage
    
    def count(self) -> int:
        """
        Count total number of entities.
        
        Returns:
            Number of entities
        """
        return len(self._storage)
    
    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[T]:
        """
        Find entities matching criteria.
        
        Args:
            criteria: Dictionary of field names and values to match
            
        Returns:
            List of matching entities
        """
        results = []
        for entity in self._storage.values():
            match = True
            for key, value in criteria.items():
                if not hasattr(entity, key) or getattr(entity, key) != value:
                    match = False
                    break
            if match:
                results.append(entity)
        return results
    
    def clear(self) -> None:
        """Clear all entities from repository."""
        self._storage.clear()
