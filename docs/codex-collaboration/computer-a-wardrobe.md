# 电脑 A：衣橱模块开发说明

你负责让衣橱“存得进去、查得出来”。这是后续穿搭推荐和买前决策的基础。

## 你的分支

```bash
git checkout -b codex/wardrobe-api
```

## 你要实现的接口

以 `docs/api-contract.md` 为准，实现：

```txt
POST /api/wardrobe/items/detect
POST /api/wardrobe/items/batch-confirm
GET  /api/wardrobe/items
GET  /api/wardrobe/items/{item_id}
PATCH /api/wardrobe/items/{item_id}
DELETE /api/wardrobe/items/{item_id}
```

第一优先级是前三个：

```txt
detect
batch-confirm
list items
```

## 推荐文件边界

你主要改：

```txt
backend/app/routers/wardrobe.py
backend/app/services/wardrobe_service.py
backend/app/services/vision_service.py
backend/app/schemas.py
backend/app/models.py
backend/tests/test_wardrobe.py
```

你需要少改或不改：

```txt
backend/app/main.py
docs/api-contract.md
```

如果要在 `main.py` 里注册 router，只做最小改动：

```python
from app.routers import wardrobe

app.include_router(wardrobe.router, prefix="/api/wardrobe", tags=["wardrobe"])
```

## 功能设计

`POST /api/wardrobe/items/detect`：

1. 接收上传图片。
2. 保存原图到 `backend/uploads/`。
3. 调用 `vision_service.detect_clothing_items(image_path)`。
4. 返回 `upload_id`、`original_image_url`、`detected_items`。
5. 不直接写入衣橱 item 表。

`POST /api/wardrobe/items/batch-confirm`：

1. 接收前端确认后的 `items`。
2. 只保存 `save: true` 的候选项。
3. 写入 SQLite。
4. 返回 `saved_items` 和 `total_saved`。

`GET /api/wardrobe/items`：

1. 从 SQLite 查询衣橱。
2. 支持 `category`、`color`、`low_usage` 查询参数。
3. 返回 `{ "items": [], "total": 0 }`。

## mock 规则

现在不要接真实 AI。`vision_service.detect_clothing_items` 可以根据文件名或固定逻辑返回 2 件衣物：

```json
[
  {
    "temp_id": "det_001",
    "name": "白色衬衫",
    "category": "top",
    "color": "白色",
    "season": ["spring", "summer"],
    "style": ["通勤", "简约"],
    "material": "棉",
    "fit": "常规",
    "cutout_image_url": "/uploads/det_001_cutout.jpg",
    "confidence": 0.91
  },
  {
    "temp_id": "det_002",
    "name": "浅蓝牛仔裤",
    "category": "bottom",
    "color": "浅蓝色",
    "season": ["spring", "autumn"],
    "style": ["休闲", "日常"],
    "material": "牛仔",
    "fit": "直筒",
    "cutout_image_url": "/uploads/det_002_cutout.jpg",
    "confidence": 0.87
  }
]
```

第一版 `cutout_image_url` 可以直接等于原图 URL。

## 给这台电脑 Codex 的启动提示词

复制下面这段给电脑 A 的 Codex：

```txt
你现在负责 IF.LAND 项目的衣橱模块后端开发。

请先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-a-wardrobe.md
3. docs/api-contract.md
4. backend/app/main.py
5. backend/app/models.py

目标是在分支 codex/wardrobe-api 上实现：
- POST /api/wardrobe/items/detect
- POST /api/wardrobe/items/batch-confirm
- GET /api/wardrobe/items

可以顺手实现：
- GET /api/wardrobe/items/{item_id}
- PATCH /api/wardrobe/items/{item_id}
- DELETE /api/wardrobe/items/{item_id}

要求：
- 使用 FastAPI + Pydantic/SQLModel。
- 用测试驱动开发，新增 backend/tests/test_wardrobe.py。
- AI 识别先 mock，不要接真实模型。
- 一张上传图要能返回多个 detected_items。
- batch-confirm 后要能写入 SQLite。
- 跑通 python -m pytest。
- 完成后提交并 push 到 codex/wardrobe-api。
- 不要提交 PRD、.venv、SQLite db、上传图片。
```

## 验收标准

必须通过：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

至少验证：

```txt
detect 上传一张图片，返回 detected_items 数组
batch-confirm 保存两件衣服，返回 total_saved = 2
GET /api/wardrobe/items 能查到保存结果
GET /api/wardrobe/items?category=top 能筛选
```

## 交接内容

完成后汇报：

```txt
分支：codex/wardrobe-api
完成接口：
测试结果：
给电脑 B/C 的注意事项：
```
