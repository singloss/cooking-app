"""数据模型定义"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Step:
    order: int
    description: str
    duration_minutes: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Step:
        return cls(
            order=int(data.get("order", 1)),
            description=str(data.get("description", "")),
            duration_minutes=int(data.get("duration_minutes", 0)),
        )


@dataclass
class Recipe:
    id: str
    name: str
    cuisine: str
    description: str
    ingredients: list[str]
    steps: list[Step]
    difficulty: str = "中等"
    prep_time: str = "30分钟"
    is_custom: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "cuisine": self.cuisine,
            "description": self.description,
            "ingredients": self.ingredients,
            "steps": [s.to_dict() for s in self.steps],
            "difficulty": self.difficulty,
            "prep_time": self.prep_time,
            "is_custom": self.is_custom,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Recipe:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            cuisine=str(data["cuisine"]),
            description=str(data.get("description", "")),
            ingredients=list(data.get("ingredients", [])),
            steps=[Step.from_dict(s) for s in data.get("steps", [])],
            difficulty=str(data.get("difficulty", "中等")),
            prep_time=str(data.get("prep_time", "30分钟")),
            is_custom=bool(data.get("is_custom", False)),
        )


@dataclass
class CuisineInfo:
    id: str
    name: str
    region: str
    emoji: str
    description: str
