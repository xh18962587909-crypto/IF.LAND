from app.models import ClothingItem


def generate_try_on_preview(items: list[ClothingItem], context: str) -> str:
    categories = "-".join(item.category for item in items) or "empty"
    safe_context = context.replace(" ", "-") or "outfit"
    return f"/uploads/mock_try_on_{safe_context}_{categories}.jpg"
