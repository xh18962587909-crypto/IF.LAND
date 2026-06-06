from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.db import engine, initialize_database
from app.main import app
from app.models import ClothingItem


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_clothing_items() -> Iterator[None]:
    initialize_database()
    with Session(engine) as session:
        session.exec(delete(ClothingItem))
        session.commit()
    yield
    with Session(engine) as session:
        session.exec(delete(ClothingItem))
        session.commit()


def seed_wardrobe() -> dict[str, int]:
    items = [
        ClothingItem(
            name="白色衬衫",
            category="top",
            color="白色",
            season=["spring", "summer", "autumn"],
            style=["通勤", "浅色系", "简约"],
            image_url="/uploads/white-shirt.jpg",
            cutout_image_url="/uploads/white-shirt-cutout.jpg",
        ),
        ClothingItem(
            name="浅蓝牛仔裤",
            category="bottom",
            color="浅蓝色",
            season=["spring", "summer", "autumn"],
            style=["通勤", "浅色系", "休闲"],
            image_url="/uploads/blue-jeans.jpg",
            cutout_image_url="/uploads/blue-jeans-cutout.jpg",
        ),
        ClothingItem(
            name="黑色乐福鞋",
            category="shoes",
            color="黑色",
            season=["spring", "summer", "autumn", "winter"],
            style=["通勤", "正式"],
            image_url="/uploads/black-shoes.jpg",
            cutout_image_url="/uploads/black-shoes-cutout.jpg",
        ),
        ClothingItem(
            name="米色外套",
            category="outerwear",
            color="米色",
            season=["spring", "autumn"],
            style=["通勤", "浅色系", "正式"],
            image_url="/uploads/beige-jacket.jpg",
            cutout_image_url="/uploads/beige-jacket-cutout.jpg",
        ),
        ClothingItem(
            name="白色运动鞋",
            category="shoes",
            color="白色",
            season=["spring", "summer", "autumn"],
            style=["通勤", "浅色系", "舒适"],
            image_url="/uploads/white-sneakers.jpg",
            cutout_image_url="/uploads/white-sneakers-cutout.jpg",
        ),
    ]
    with Session(engine) as session:
        for item in items:
            session.add(item)
        session.commit()
        for item in items:
            session.refresh(item)
        return {
            "top": items[0].id,
            "bottom": items[1].id,
            "black_shoes": items[2].id,
            "outerwear": items[3].id,
            "white_shoes": items[4].id,
        }


def recommend_payload(**overrides):
    payload = {
        "occasion": "通勤",
        "temperature": "18-25℃",
        "weather": "晴",
        "mood": ["轻松"],
        "style": ["浅色系"],
        "avoid": [],
        "preferred_item_id": None,
    }
    payload.update(overrides)
    return payload


def post_recommend(**overrides):
    return client.post("/api/outfits/recommend", json=recommend_payload(**overrides))


def flatten_items(outfits):
    return [item for outfit in outfits for item in outfit["items"]]


def test_recommend_returns_outfits_from_seeded_wardrobe():
    seed_wardrobe()

    response = post_recommend()

    assert response.status_code == 200
    outfits = response.json()["outfits"]
    assert 1 <= len(outfits) <= 3
    assert outfits[0]["items"]


def test_recommend_excludes_avoided_color():
    seed_wardrobe()

    response = post_recommend(avoid=["黑色"])

    assert response.status_code == 200
    items = flatten_items(response.json()["outfits"])
    assert items
    assert all(item["color"] != "黑色" for item in items)


def test_recommend_includes_preferred_item_when_possible():
    ids = seed_wardrobe()

    response = post_recommend(preferred_item_id=ids["outerwear"])

    assert response.status_code == 200
    items = flatten_items(response.json()["outfits"])
    assert any(item["id"] == ids["outerwear"] for item in items)


def test_recommend_returns_required_display_fields():
    seed_wardrobe()

    response = post_recommend()

    assert response.status_code == 200
    outfit = response.json()["outfits"][0]
    for field in [
        "id",
        "title",
        "reason",
        "score",
        "comfort_note",
        "scene_note",
        "items",
        "replace_suggestions",
        "try_on_image_url",
    ]:
        assert field in outfit


def test_recommend_handles_incomplete_wardrobe_without_crashing():
    with Session(engine) as session:
        session.add(
            ClothingItem(
                name="白色衬衫",
                category="top",
                color="白色",
                season=["spring", "summer"],
                style=["通勤", "浅色系"],
                image_url="/uploads/white-shirt.jpg",
                cutout_image_url="/uploads/white-shirt-cutout.jpg",
            )
        )
        session.commit()

    response = post_recommend()

    assert response.status_code == 200
    outfits = response.json()["outfits"]
    assert outfits
    assert "当前衣橱" in outfits[0]["reason"]


def test_replace_only_changes_requested_category():
    ids = seed_wardrobe()
    response = client.post(
        "/api/outfits/replace",
        json={
            "current_item_ids": [ids["top"], ids["bottom"], ids["black_shoes"]],
            "replace_category": "shoes",
            "constraints": {
                "occasion": "通勤",
                "temperature": "18-25℃",
                "avoid": ["黑色"],
                "style": ["浅色系"],
            },
        },
    )

    assert response.status_code == 200
    item_ids = {item["id"] for item in response.json()["outfit"]["items"]}
    assert ids["top"] in item_ids
    assert ids["bottom"] in item_ids
    assert ids["black_shoes"] not in item_ids
    assert ids["white_shoes"] in item_ids


def test_confirm_returns_confirmed_true():
    ids = seed_wardrobe()

    response = client.post(
        "/api/outfits/confirm",
        json={"item_ids": [ids["top"], ids["bottom"]], "feedback": "like"},
    )

    assert response.status_code == 200
    assert response.json()["confirmed"] is True
    assert response.json()["worn_record_id"]


def test_outfit_score_is_between_0_and_100():
    seed_wardrobe()

    response = post_recommend()

    assert response.status_code == 200
    for outfit in response.json()["outfits"]:
        assert 0 <= outfit["score"] <= 100
