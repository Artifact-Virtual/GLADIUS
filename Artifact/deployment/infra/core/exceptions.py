"""
Custom exceptions for the business infrastructure.

Provides a hierarchy of exceptions for different error scenarios
in the market and asset management system.
"""


class BusinessInfrastructureError(Exception):
    """Base exception for all business infrastructure errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ValidationError(BusinessInfrastructureError):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, message: str, value=None):
        details = {"field": field, "value": value}
        super().__init__(f"Validation failed for '{field}': {message}", details)
        self.field = field
        self.value = value


class DataNotFoundError(BusinessInfrastructureError):
    """Raised when requested data is not found."""
    
    def __init__(self, entity_type: str, identifier: str):
        message = f"{entity_type} not found: {identifier}"
        details = {"entity_type": entity_type, "identifier": identifier}
        super().__init__(message, details)
        self.entity_type = entity_type
        self.identifier = identifier


class ConfigurationError(BusinessInfrastructureError):
    """Raised when there's a configuration error."""
    
    def __init__(self, config_key: str, message: str):
        details = {"config_key": config_key}
        super().__init__(f"Configuration error for '{config_key}': {message}", details)
        self.config_key = config_key


class DataIntegrityError(BusinessInfrastructureError):
    """Raised when data integrity constraints are violated."""
    
    def __init__(self, message: str, entity_type: str = None):
        details = {"entity_type": entity_type} if entity_type else {}
        super().__init__(f"Data integrity error: {message}", details)


class BusinessLogicError(BusinessInfrastructureError):
    """Raised when business logic rules are violated."""
    
    def __init__(self, rule: str, message: str):
        details = {"rule": rule}
        super().__init__(f"Business rule violation '{rule}': {message}", details)
        self.rule = rule


class RepositoryError(BusinessInfrastructureError):
    """Raised when repository operations fail."""
    
    def __init__(self, operation: str, message: str, entity_type: str = None):
        details = {"operation": operation, "entity_type": entity_type}
        super().__init__(f"Repository error during '{operation}': {message}", details)
        self.operation = operation
