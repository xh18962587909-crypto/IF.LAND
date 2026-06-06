from __future__ import annotations

import os
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ["DATABASE_URL"] = "sqlite:///data/manual_outfit_demo.db"

from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.db import engine, initialize_database
from app.main import app
from app.models import ClothingItem


def print_title(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def print_step(title: str) -> None:
    print("\n" + title)
    print("-" * len(title))


def seed_demo_wardrobe() -> dict[str, int]:
    initialize_database()
    demo_items = [
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
        session.exec(delete(ClothingItem))
        for item in demo_items:
            session.add(item)
        session.commit()
        for item in demo_items:
            session.refresh(item)

    return {
        "top": demo_items[0].id,
        "bottom": demo_items[1].id,
        "black_shoes": demo_items[2].id,
        "outerwear": demo_items[3].id,
        "white_shoes": demo_items[4].id,
    }


def show_items(items: list[dict]) -> None:
    for item in items:
        print(f"  - id={item['id']} | {item['name']} | {item['category']} | {item['color']}")


def assert_or_stop(condition: bool, success: str, failure: str) -> None:
    if not condition:
        print(f"  结果：失败 - {failure}")
        raise SystemExit(1)
    print(f"  结果：通过 - {success}")


def main() -> None:
    print_title("衣见 分工 B 人类版验收")
    print("这个脚本会做四件事：")
    print("1. 自动准备 5 件测试衣服")
    print("2. 调用推荐穿搭 API，检查 avoid=[黑色] 是否生效")
    print("3. 调用替换 API，检查是不是只换鞋子")
    print("4. 调用确认 API，检查是否返回 confirmed=true")

    ids = seed_demo_wardrobe()
    print_step("第 1 步：准备测试衣橱")
    print("已放入 5 件测试衣服：")
    print("  - 白色衬衫：上衣")
    print("  - 浅蓝牛仔裤：下装")
    print("  - 黑色乐福鞋：鞋子")
    print("  - 米色外套：外套")
    print("  - 白色运动鞋：鞋子")

    with TestClient(app) as client:
        print_step("第 2 步：测试推荐穿搭")
        recommend_payload = {
            "occasion": "通勤",
            "temperature": "18-25℃",
            "weather": "晴",
            "mood": ["轻松"],
            "style": ["浅色系"],
            "avoid": ["黑色"],
            "preferred_item_id": None,
        }
        print("请求：POST /api/outfits/recommend")
        print("人类理解：我要通勤穿，天气 18-25℃ 晴天，而且不要黑色。")
        response = client.post("/api/outfits/recommend", json=recommend_payload)
        assert_or_stop(response.status_code == 200, "接口返回 200", f"接口返回 {response.status_code}")

        outfits = response.json()["outfits"]
        assert_or_stop(bool(outfits), "返回了至少 1 套穿搭", "没有返回穿搭")
        print(f"返回穿搭数量：{len(outfits)}")
        first_outfit = outfits[0]
        print(f"第一套标题：{first_outfit['title']}")
        print(f"第一套分数：{first_outfit['score']}")
        print(f"推荐理由：{first_outfit['reason']}")
        print(f"舒适说明：{first_outfit['comfort_note']}")
        print("包含单品：")
        show_items(first_outfit["items"])

        all_recommended_items = [item for outfit in outfits for item in outfit["items"]]
        has_black = any(item["color"] == "黑色" or "黑色" in item["name"] for item in all_recommended_items)
        assert_or_stop(not has_black, "你说不要黑色，结果里确实没有黑色单品", "结果里出现了黑色单品")

        print_step("第 3 步：测试只替换鞋子")
        print("替换前：白色衬衫 + 浅蓝牛仔裤 + 黑色乐福鞋")
        replace_payload = {
            "current_item_ids": [ids["top"], ids["bottom"], ids["black_shoes"]],
            "replace_category": "shoes",
            "constraints": {
                "occasion": "通勤",
                "temperature": "18-25℃",
                "weather": "晴",
                "mood": ["轻松"],
                "style": ["浅色系"],
                "avoid": ["黑色"],
            },
        }
        print("请求：POST /api/outfits/replace")
        print("人类理解：只换鞋，并且新鞋不能是黑色。")
        response = client.post("/api/outfits/replace", json=replace_payload)
        assert_or_stop(response.status_code == 200, "接口返回 200", f"接口返回 {response.status_code}")

        replaced_outfit = response.json()["outfit"]
        replaced_items = replaced_outfit["items"]
        print("替换后：")
        show_items(replaced_items)

        replaced_ids = {item["id"] for item in replaced_items}
        assert_or_stop(ids["top"] in replaced_ids, "上衣没有变", "上衣被错误替换了")
        assert_or_stop(ids["bottom"] in replaced_ids, "裤子没有变", "裤子被错误替换了")
        assert_or_stop(ids["black_shoes"] not in replaced_ids, "黑色鞋子被换掉了", "黑色鞋子还在")
        assert_or_stop(ids["white_shoes"] in replaced_ids, "新鞋是白色运动鞋", "没有换成可用的新鞋")

        print_step("第 4 步：测试确认今天穿这套")
        confirm_payload = {"item_ids": [ids["top"], ids["bottom"], ids["white_shoes"]], "feedback": "like"}
        print("请求：POST /api/outfits/confirm")
        print("人类理解：我决定今天就穿这套。")
        response = client.post("/api/outfits/confirm", json=confirm_payload)
        assert_or_stop(response.status_code == 200, "接口返回 200", f"接口返回 {response.status_code}")

        confirm_result = response.json()
        print(f"confirmed：{confirm_result['confirmed']}")
        print(f"worn_record_id：{confirm_result['worn_record_id']}")
        assert_or_stop(confirm_result["confirmed"] is True, "确认穿搭成功", "没有返回 confirmed=true")

    print_title("最终结论")
    print("分工 B 的核心功能可以被人类读懂地验收：")
    print("  - 能推荐穿搭")
    print("  - 能避开黑色")
    print("  - 能只替换指定品类")
    print("  - 能确认今天穿这套")
    print("如果你看到这里，说明这条人类版验收也通过了。")


if __name__ == "__main__":
    main()
