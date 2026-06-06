from __future__ import annotations

from collections import defaultdict

from sqlmodel import Session, select

from app.db import engine
from app.models import ClothingItem
from app.schemas import (
    OutfitConfirmRequest,
    OutfitConfirmResponse,
    OutfitConstraints,
    OutfitItemResponse,
    OutfitRecommendRequest,
    OutfitReplaceRequest,
    OutfitResponse,
    ReplaceSuggestionResponse,
)
from app.services.try_on_service import generate_try_on_preview


PRIMARY_CATEGORY_ORDER = ["top", "bottom", "outerwear", "shoes", "bag", "accessory"]


def recommend_outfits(request: OutfitRecommendRequest) -> list[OutfitResponse]:
    items = _load_items()
    eligible = _filter_items(items, request.avoid)

    if request.preferred_item_id is not None:
        preferred = _find_item(items, request.preferred_item_id)
        if preferred and preferred not in eligible and not _matches_avoid(preferred, request.avoid):
            eligible.append(preferred)

    outfits = _build_outfit_variants(eligible, request)
    if request.preferred_item_id is not None:
        outfits = _ensure_preferred_item(outfits, items, request)

    return outfits


def replace_outfit_item(request: OutfitReplaceRequest) -> OutfitResponse:
    current_items = _load_items_by_ids(request.current_item_ids)
    constraints = request.constraints
    avoid = constraints.avoid
    replacements = [
        item
        for item in _filter_items(_load_items(), avoid)
        if item.category == request.replace_category and item.id not in request.current_item_ids
    ]

    selected_replacement = _best_item(replacements, constraints.occasion, constraints.style)
    next_items: list[ClothingItem] = []
    replaced = False
    for item in current_items:
        if item.category == request.replace_category:
            if selected_replacement and not replaced:
                next_items.append(selected_replacement)
                replaced = True
            elif not selected_replacement:
                next_items.append(item)
        else:
            next_items.append(item)

    if selected_replacement and not replaced:
        next_items.append(selected_replacement)

    pseudo_request = OutfitRecommendRequest(
        occasion=constraints.occasion or "日常",
        temperature=constraints.temperature or "未知气温",
        weather=constraints.weather or "未知天气",
        mood=constraints.mood,
        style=constraints.style,
        avoid=constraints.avoid,
    )
    return _format_outfit(
        index=1,
        items=next_items,
        request=pseudo_request,
        title="调整后的穿搭",
        reason_prefix=f"只替换 {request.replace_category}，其他单品保持不变。",
    )


def confirm_outfit(request: OutfitConfirmRequest) -> OutfitConfirmResponse:
    stable_record_id = abs(hash(tuple(request.item_ids) + (request.feedback,))) % 1_000_000
    return OutfitConfirmResponse(
        confirmed=True,
        worn_record_id=stable_record_id or 1,
        feedback=request.feedback,
        item_ids=request.item_ids,
    )


def _load_items() -> list[ClothingItem]:
    with Session(engine) as session:
        return list(session.exec(select(ClothingItem)).all())


def _load_items_by_ids(item_ids: list[int]) -> list[ClothingItem]:
    if not item_ids:
        return []
    with Session(engine) as session:
        items = list(session.exec(select(ClothingItem).where(ClothingItem.id.in_(item_ids))).all())
    by_id = {item.id: item for item in items}
    return [by_id[item_id] for item_id in item_ids if item_id in by_id]


def _find_item(items: list[ClothingItem], item_id: int) -> ClothingItem | None:
    return next((item for item in items if item.id == item_id), None)


def _filter_items(items: list[ClothingItem], avoid: list[str]) -> list[ClothingItem]:
    return [item for item in items if not _matches_avoid(item, avoid)]


def _matches_avoid(item: ClothingItem, avoid: list[str]) -> bool:
    searchable = [item.name, item.category, item.color, *item.style]
    return any(term and any(term in value for value in searchable) for term in avoid)


def _build_outfit_variants(
    items: list[ClothingItem],
    request: OutfitRecommendRequest,
) -> list[OutfitResponse]:
    grouped = _group_by_category(items)
    variant_count = min(3, max(1, max((len(values) for values in grouped.values()), default=1)))
    outfits: list[OutfitResponse] = []

    for index in range(variant_count):
        outfit_items = []
        for category in PRIMARY_CATEGORY_ORDER:
            candidates = grouped.get(category, [])
            if not candidates:
                continue
            outfit_items.append(candidates[index % len(candidates)])

        if not outfit_items and items:
            outfit_items = [items[index % len(items)]]

        if outfit_items:
            outfits.append(_format_outfit(index + 1, outfit_items, request))

    return outfits


def _ensure_preferred_item(
    outfits: list[OutfitResponse],
    all_items: list[ClothingItem],
    request: OutfitRecommendRequest,
) -> list[OutfitResponse]:
    preferred = _find_item(all_items, request.preferred_item_id) if request.preferred_item_id else None
    if not preferred:
        return outfits
    if any(any(item.id == preferred.id for item in outfit.items) for outfit in outfits):
        return outfits

    first_items = _load_items_by_ids([item.id for item in outfits[0].items]) if outfits else []
    next_items = [item for item in first_items if item.category != preferred.category]
    next_items.append(preferred)
    preferred_outfit = _format_outfit(
        index=1,
        items=next_items,
        request=request,
        title="包含指定单品的穿搭",
        reason_prefix=f"已尽量保留你指定的 {preferred.name}。",
    )
    return [preferred_outfit, *outfits[1:]]


def _group_by_category(items: list[ClothingItem]) -> dict[str, list[ClothingItem]]:
    grouped: dict[str, list[ClothingItem]] = defaultdict(list)
    for item in sorted(items, key=lambda candidate: (_style_score(candidate, "", []), candidate.id or 0), reverse=True):
        grouped[item.category].append(item)
    return grouped


def _best_item(items: list[ClothingItem], occasion: str, styles: list[str]) -> ClothingItem | None:
    if not items:
        return None
    return max(items, key=lambda item: (_style_score(item, occasion, styles), -(item.id or 0)))


def _style_score(item: ClothingItem, occasion: str, styles: list[str]) -> int:
    score = 0
    if occasion and occasion in item.style:
        score += 3
    score += sum(1 for style in styles if style in item.style)
    if "通勤" in item.style:
        score += 1
    if "浅色系" in item.style:
        score += 1
    return score


def _format_outfit(
    index: int,
    items: list[ClothingItem],
    request: OutfitRecommendRequest,
    title: str | None = None,
    reason_prefix: str = "",
) -> OutfitResponse:
    score = _score_outfit(items, request)
    missing = _missing_categories(items)
    reason_parts = [
        reason_prefix,
        f"适合{request.occasion}场景",
        f"已结合{request.temperature}和{request.weather}做天气适配",
    ]
    if request.avoid:
        reason_parts.append(f"避开了{', '.join(request.avoid)}")
    if request.style:
        reason_parts.append(f"呼应{', '.join(request.style)}偏好")
    if missing:
        reason_parts.append(f"当前衣橱缺少{', '.join(missing)}数据，因此先给出可执行的部分搭配")

    return OutfitResponse(
        id=f"outfit_{index:03d}",
        title=title or _outfit_title(index, request),
        reason="，".join(part for part in reason_parts if part) + "。",
        score=score,
        comfort_note=f"{request.temperature}、{request.weather}条件下，这套搭配以舒适和可出门为优先。",
        scene_note=f"适合{request.occasion}，也可以根据心情调整为{'/'.join(request.mood) if request.mood else '日常'}。",
        items=[_item_response(item) for item in items],
        replace_suggestions=_replace_suggestions(items),
        try_on_image_url=generate_try_on_preview(items, request.occasion),
    )


def _outfit_title(index: int, request: OutfitRecommendRequest) -> str:
    style_label = request.style[0] if request.style else "实穿"
    return f"{style_label}{request.occasion}搭配 {index}"


def _item_response(item: ClothingItem) -> OutfitItemResponse:
    return OutfitItemResponse(
        id=item.id,
        name=item.name,
        category=item.category,
        color=item.color,
        image_url=item.cutout_image_url or item.image_url,
    )


def _replace_suggestions(items: list[ClothingItem]) -> list[ReplaceSuggestionResponse]:
    categories = {item.category for item in items}
    suggestions = []
    for category, label in [
        ("top", "换一件上衣"),
        ("bottom", "换一件下装"),
        ("outerwear", "换一件外套"),
        ("shoes", "鞋子换舒服点"),
    ]:
        if category in categories:
            suggestions.append(ReplaceSuggestionResponse(category=category, label=label))
    return suggestions


def _missing_categories(items: list[ClothingItem]) -> list[str]:
    present = {item.category for item in items}
    labels = {
        "top": "上衣",
        "bottom": "下装",
        "shoes": "鞋子",
    }
    return [label for category, label in labels.items() if category not in present]


def _score_outfit(items: list[ClothingItem], request: OutfitRecommendRequest) -> int:
    score = 50
    if any(request.occasion in item.style for item in items):
        score += 15
    if any(_season_matches_temperature(item, request.temperature) for item in items):
        score += 10
    if request.style and any(style in item.style for item in items for style in request.style):
        score += 10
    if not any(_matches_avoid(item, request.avoid) for item in items):
        score += 10
    if any((item.id or 0) % 2 == 0 for item in items):
        score += 5
    if {"top", "bottom"}.issubset({item.category for item in items}):
        score += 5
    if len({item.color for item in items}) >= 2:
        score += 5
    return max(0, min(100, score))


def _season_matches_temperature(item: ClothingItem, temperature: str) -> bool:
    if any(token in temperature for token in ["18", "20", "22", "25"]):
        return any(season in item.season for season in ["spring", "summer", "autumn"])
    if any(token in temperature for token in ["冷", "冬", "10"]):
        return "winter" in item.season or "autumn" in item.season
    return True
