# 电脑 A：衣橱资产标准化与入库

你负责把用户上传的图片变成“可管理、可召回、可搭配”的衣橱资产。新方案 v1.0 特别强调降低冷启动成本，所以你的模块是整个项目的入口。

## 1. 你的分支

```bash
git checkout -b codex/wardrobe-standardization
```

## 2. 你要实现的接口

第一优先级：

```txt
POST /api/wardrobe/items/detect
POST /api/wardrobe/items/batch-confirm
GET  /api/wardrobe/items
```

第二优先级：

```txt
GET    /api/wardrobe/items/{item_id}
PATCH  /api/wardrobe/items/{item_id}
DELETE /api/wardrobe/items/{item_id}
```

## 3. 你负责的产品能力

用户可以上传：

```txt
商品截图
已有衣物图
穿搭照片
衣柜照片
订单截图
```

MVP 阶段每张图只需要识别 1-3 件主要衣服，不追求完整切出复杂照片里的所有衣物。

每件衣物要被标准化成：

```txt
数据库 item_id
原图 original image
白底素材 cutout image
品类 category
颜色 color
风格 style
季节 season
场景 occasion
材质 material
版型 fit
文字描述 description
来源类型 source_type
图像 embedding mock
文字 embedding mock
```

## 4. 推荐文件边界

主要修改：

```txt
backend/app/routers/wardrobe.py
backend/app/services/wardrobe_service.py
backend/app/services/vision_service.py
backend/app/services/embedding_service.py
backend/app/schemas.py
backend/app/models.py
backend/tests/test_wardrobe.py
```

尽量少改：

```txt
backend/app/main.py
docs/api-contract.md
```

如果要在 `main.py` 注册 router，只做最小改动：

```python
from app.routers import wardrobe

app.include_router(wardrobe.router, prefix="/api/wardrobe", tags=["wardrobe"])
```

## 5. 实现细节

`POST /api/wardrobe/items/detect`：

1. 接收 `multipart/form-data` 图片。
2. 可选接收 `source_type`，默认 `manual_upload`。
3. 保存原图到 `backend/uploads/`。
4. 调用 `vision_service.detect_clothing_items(image_path, source_type)`。
5. 返回 `upload_id`、`original_image_url`、`detected_items`。
6. 不直接写入正式衣橱表。

`POST /api/wardrobe/items/batch-confirm`：

1. 接收前端确认后的候选衣物。
2. 只保存 `save: true` 的候选项。
3. 为每件衣服生成数据库 item。
4. 生成 mock embedding。
5. 做最小去重判断：同 category + 同 color + 相似 name 视为可能重复。
6. 返回 `saved_items`、`total_saved`，可以附带 `duplicate_warnings`。

`GET /api/wardrobe/items`：

支持查询：

```txt
category
color
source_type
low_usage
```

返回 `{ "items": [], "total": 0 }`。

## 6. AI / 图像 mock 规则

不要接真实模型。先做可替换接口：

```python
detect_clothing_items(image_path: str, source_type: str) -> list[DetectedItem]
generate_cutout_image(image_path: str, temp_id: str) -> str
generate_image_embedding(image_path: str) -> list[float]
generate_text_embedding(text: str) -> list[float]
```

白底图第一版可以直接返回原图 URL，但字段名必须保留 `cutout_image_url`。

## 7. 给这台电脑 Codex 的启动提示词

复制下面这段给电脑 A 的 Codex：

```txt
你现在负责 IF.LAND 项目的衣橱资产标准化与入库模块。

请先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-a-wardrobe.md
3. docs/api-contract.md
4. backend/app/main.py
5. backend/app/models.py

请在分支 codex/wardrobe-standardization 上开发。

目标：
- 实现 POST /api/wardrobe/items/detect
- 实现 POST /api/wardrobe/items/batch-confirm
- 实现 GET /api/wardrobe/items
- 尽量实现 GET/PATCH/DELETE /api/wardrobe/items/{item_id}

要求：
- 使用 FastAPI + Pydantic/SQLModel。
- 用测试驱动开发，新增 backend/tests/test_wardrobe.py。
- 支持一张图返回 1-3 件 detected_items。
- 支持 source_type: manual_upload, product_screenshot, outfit_photo, closet_photo, order_screenshot。
- 每个 item 以数据库 id 为主键。
- 保留 cutout_image_url、description、occasion、mock embedding 字段。
- AI、白底图和 embedding 都先 mock。
- 跑通 cd backend && source .venv/bin/activate && python -m pytest。
- 完成后提交并 push 到 codex/wardrobe-standardization。
- 不要提交 PRD、.venv、SQLite db、上传图片。
```

## 8. 验收标准

必须验证：

```txt
detect 上传一张图片，返回 detected_items 数组
detected_items 至少包含 category/color/style/season/occasion/cutout_image_url
batch-confirm 保存两件衣服，返回 total_saved = 2
GET /api/wardrobe/items 能查到保存结果
GET /api/wardrobe/items?category=top 能筛选
重复衣物能给出 duplicate warning 或相似提示
```

测试命令：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```
