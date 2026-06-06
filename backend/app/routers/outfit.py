from fastapi import APIRouter

from app.schemas import (
    OutfitConfirmRequest,
    OutfitConfirmResponse,
    OutfitRecommendRequest,
    OutfitRecommendResponse,
    OutfitReplaceRequest,
    OutfitReplaceResponse,
)
from app.services.outfit_service import confirm_outfit, recommend_outfits, replace_outfit_item


router = APIRouter()


@router.post("/recommend", response_model=OutfitRecommendResponse)
def recommend(request: OutfitRecommendRequest) -> OutfitRecommendResponse:
    return OutfitRecommendResponse(outfits=recommend_outfits(request))


@router.post("/replace", response_model=OutfitReplaceResponse)
def replace(request: OutfitReplaceRequest) -> OutfitReplaceResponse:
    return OutfitReplaceResponse(outfit=replace_outfit_item(request))


@router.post("/confirm", response_model=OutfitConfirmResponse)
def confirm(request: OutfitConfirmRequest) -> OutfitConfirmResponse:
    return confirm_outfit(request)
