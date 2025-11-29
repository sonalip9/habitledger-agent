"""
Typed domain models for HabitLedger.

This module defines strongly-typed dataclasses for all domain entities
used throughout the application, promoting type safety and reducing
runtime errors.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ConversationRole(str, Enum):
    """Role of a participant in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class BehaviourPrincipleEnum(str, Enum):
    """Enumeration of supported behavioural science principles."""

    LOSS_AVERSION = "loss_aversion"
    HABIT_LOOPS = "habit_loops"
    COMMITMENT_DEVICES = "commitment_devices"
    TEMPTATION_BUNDLING = "temptation_bundling"
    FRICTION_REDUCTION = "friction_reduction"
    FRICTION_INCREASE = "friction_increase"
    DEFAULT_EFFECT = "default_effect"
    MICRO_HABITS = "micro_habits"


class BaseModel:
    """Base model with common functionality for all domain models."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        raise NotImplementedError("Subclasses must implement to_dict method.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseModel":
        """Create instance from dictionary."""
        raise NotImplementedError("Subclasses must implement from_dict method.")


@dataclass
class Goal(BaseModel):
    """Represents a user's financial goal."""

    description: str
    target: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "description": self.description,
            "target": self.target,
            "created_at": self.created_at,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Goal":
        """Create Goal from dictionary."""
        return cls(
            description=data.get("description", ""),
            target=data.get("target"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            completed=data.get("completed", False),
        )


@dataclass
class StreakData(BaseModel):
    """Tracks streak information for a specific habit."""

    current: int = 0
    best: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "current": self.current,
            "best": self.best,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StreakData":
        """Create StreakData from dictionary."""
        return cls(
            current=data.get("current", 0),
            best=data.get("best", 0),
            last_updated=data.get("last_updated", datetime.now().isoformat()),
        )


@dataclass
class Struggle(BaseModel):
    """Represents a recorded user struggle or challenge."""

    description: str
    first_noted: str = field(default_factory=lambda: datetime.now().isoformat())
    last_noted: str = field(default_factory=lambda: datetime.now().isoformat())
    count: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "description": self.description,
            "first_noted": self.first_noted,
            "last_noted": self.last_noted,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Struggle":
        """Create Struggle from dictionary."""
        timestamp = datetime.now().isoformat()
        return cls(
            description=data.get("description", ""),
            first_noted=data.get("first_noted", timestamp),
            last_noted=data.get("last_noted", timestamp),
            count=data.get("count", 1),
        )


@dataclass
class Intervention(BaseModel):
    """Represents a suggested intervention or action."""

    date: str
    intervention_type: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "date": self.date,
            "type": self.intervention_type,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Intervention":
        """Create Intervention from dictionary."""
        return cls(
            date=data.get("date", datetime.now().isoformat()),
            intervention_type=data.get("type", "unknown"),
            description=data.get("description", ""),
        )


@dataclass
class ConversationTurn(BaseModel):
    """Represents a single turn in the conversation history."""

    role: ConversationRole
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationTurn":
        """Create ConversationTurn from dictionary."""
        role_str = data.get("role", "user")
        try:
            role = ConversationRole(role_str)
        except ValueError:
            role = ConversationRole.USER

        return cls(
            role=role,
            content=data.get("content", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )


@dataclass
class InterventionFeedback(BaseModel):
    """Tracks the effectiveness of a specific principle."""

    successes: int = 0
    failures: int = 0
    total: int = 0
    success_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "successes": self.successes,
            "failures": self.failures,
            "total": self.total,
            "success_rate": self.success_rate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InterventionFeedback":
        """Create InterventionFeedback from dictionary."""
        return cls(
            successes=data.get("successes", 0),
            failures=data.get("failures", 0),
            total=data.get("total", 0),
            success_rate=data.get("success_rate", 0.0),
        )


@dataclass
class BehaviouralPrinciple(BaseModel):
    """Represents a behavioural science principle from the knowledge base."""

    id: str
    name: str
    description: str
    typical_triggers: list[str]
    interventions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "typical_triggers": self.typical_triggers,
            "interventions": self.interventions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BehaviouralPrinciple":
        """Create BehaviouralPrinciple from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            typical_triggers=data.get("typical_triggers", []),
            interventions=data.get("interventions", []),
        )


@dataclass
class BehaviourDatabase(BaseModel):
    """Container for all behavioural principles."""

    version: str
    description: str
    principles: list[BehaviouralPrinciple]

    def get_principle_by_id(self, principle_id: str) -> Optional[BehaviouralPrinciple]:
        """
        Get a principle by its ID.

        Args:
            principle_id: The principle ID to search for.

        Returns:
            BehaviouralPrinciple or None: The principle if found, None otherwise.
        """
        return next((p for p in self.principles if p.id == principle_id), None)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "description": self.description,
            "principles": [p.to_dict() for p in self.principles],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BehaviourDatabase":
        """Create BehaviourDatabase from dictionary."""
        principles = [
            BehaviouralPrinciple.from_dict(p) for p in data.get("principles", [])
        ]
        return cls(
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            principles=principles,
        )


@dataclass
class BehaviourPattern(BaseModel):
    """Represents a detected behavioural pattern (e.g., end_of_month_overspending)."""

    detected: bool = False
    occurrences: int = 0
    last_detected: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "detected": self.detected,
            "occurrences": self.occurrences,
            "last_detected": self.last_detected,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BehaviourPattern":
        """Create BehaviourPattern from dictionary."""
        return cls(
            detected=data.get("detected", False),
            occurrences=data.get("occurrences", 0),
            last_detected=data.get("last_detected", datetime.now().isoformat()),
        )


@dataclass
class AnalysisResult(BaseModel):
    """Result of behaviour analysis."""

    detected_principle_id: Optional[str]
    reason: str
    intervention_suggestions: list[str]
    triggers_matched: list[str]
    source: str  # "adk", "keyword", or "template"
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "detected_principle_id": self.detected_principle_id,
            "reason": self.reason,
            "intervention_suggestions": self.intervention_suggestions,
            "triggers_matched": self.triggers_matched,
            "source": self.source,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisResult":
        """Create AnalysisResult from dictionary."""
        return cls(
            detected_principle_id=data.get("detected_principle_id"),
            reason=data.get("reason", ""),
            intervention_suggestions=data.get("intervention_suggestions", []),
            triggers_matched=data.get("triggers_matched", []),
            source=data.get("source", "unknown"),
            confidence=data.get("confidence", 0.7),
        )
