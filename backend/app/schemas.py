from typing import Any, Optional

from pydantic import BaseModel, Field


class OutfitRecommendRequest(BaseModel):
    occasion: str
    temperature: str
    weather: str
    mood: list[str] = Field(default_factory=list)
    style: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    preferred_item_id: Optional[int] = None


class OutfitConstraints(BaseModel):
    occasion: str = ""
    temperature: str = ""
    weather: str = ""
    mood: list[str] = Field(default_factory=list)
    style: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)


class OutfitReplaceRequest(BaseModel):
    current_item_ids: list[int]
    replace_category: str
    constraints: OutfitConstraints = Field(default_factory=OutfitConstraints)


class OutfitConfirmRequest(BaseModel):
    item_ids: list[int]
    feedback: str = "neutral"


class OutfitItemResponse(BaseModel):
    id: int
    name: str
    category: str
    color: str
    image_url: str


class ReplaceSuggestionResponse(BaseModel):
    category: str
    label: str


class OutfitResponse(BaseModel):
    id: str
    title: str
    reason: str
    score: int
    comfort_note: str
    scene_note: str
    items: list[OutfitItemResponse]
    replace_suggestions: list[ReplaceSuggestionResponse]
    try_on_image_url: str


class OutfitRecommendResponse(BaseModel):
    outfits: list[OutfitResponse]


class OutfitReplaceResponse(BaseModel):
    outfit: OutfitResponse


class OutfitConfirmResponse(BaseModel):
    confirmed: bool
    worn_record_id: int
    feedback: str
    item_ids: list[int]


class ApiErrorDetail(BaseModel):
    code: str
    message: str
    extra: dict[str, Any] = Field(default_factory=dict)
