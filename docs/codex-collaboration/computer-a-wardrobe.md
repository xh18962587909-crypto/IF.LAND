# 电脑 A：衣橱资产标准化与入库

一句话任务：你负责把用户上传的图片变成数据库里的衣物资产，让后续推荐和买前分析有数据可用。

## 1. 你负责什么

你只负责衣橱模块，不负责今日穿搭算法，不负责买前决策。

你要做出这个效果：

```txt
用户上传一张图片
-> 后端保存原图
-> 后端 mock 识别出 1-3 件主要衣物
-> 前端拿到 detected_items 让用户确认
-> 用户确认后批量保存到 SQLite
-> 衣橱列表能查到这些衣物
```

## 2. 你的分支

```bash
git checkout -b codex/wardrobe-standardization
```

## 3. 必须实现的接口

必须完成：

```txt
POST /api/wardrobe/items/detect
POST /api/wardrobe/items/batch-confirm
GET  /api/wardrobe/items
```

有时间再做：

```txt
GET    /api/wardrobe/items/{item_id}
PATCH  /api/wardrobe/items/{item_id}
DELETE /api/wardrobe/items/{item_id}
```

## 4. 必须修改/新增的文件

主要文件：

```txt
backend/app/routers/wardrobe.py
backend/app/services/wardrobe_service.py
backend/app/services/vision_service.py
backend/app/services/embedding_service.py
backend/app/schemas.py
backend/app/models.py
backend/tests/test_wardrobe.py
```

只允许最小修改：

```txt
backend/app/main.py
```

只在 `main.py` 里注册 router：

```python
from app.routers import wardrobe

app.include_router(wardrobe.router, prefix="/api/wardrobe", tags=["wardrobe"])
```

不要修改：

```txt
docs/api-contract.md
docs/codex-collaboration/computer-b-outfit.md
docs/codex-collaboration/computer-c-purchase-ai.md
```

## 5. 硬性要求

### 5.1 图片来源

`detect` 接口必须支持 `source_type`，默认是 `manual_upload`。

允许值：

```txt
manual_upload
product_screenshot
outfit_photo
closet_photo
order_screenshot
```

### 5.2 detect 接口要求

`POST /api/wardrobe/items/detect` 必须：

1. 接收 `multipart/form-data`。
2. 接收 `file`。
3. 可选接收 `source_type`。
4. 把原图保存到 `backend/uploads/`。
5. 返回 `upload_id`。
6. 返回 `original_image_url`。
7. 返回 `source_type`。
8. 返回 `detected_items` 数组。
9. 一张图至少 mock 返回 2 件衣物。
10. 这个接口不能写入正式衣橱表。

每个 `detected_item` 必须包含：

```txt
temp_id
name
category
color
season
style
occasion
material
fit
description
cutout_image_url
confidence
```

### 5.3 batch-confirm 接口要求

`POST /api/wardrobe/items/batch-confirm` 必须：

1. 接收 `upload_id`。
2. 接收 `source_type`。
3. 接收 `items` 数组。
4. 只保存 `save: true` 的 item。
5. 为每个保存的 item 创建数据库 id。
6. 保存 `image_url` 和 `cutout_image_url`。
7. 保存 `description`、`occasion`、`source_type`。
8. 生成 mock image/text embedding。
9. 返回 `saved_items`。
10. 返回 `total_saved`。
11. 如果发现重复，返回 `duplicate_warnings`。

### 5.4 list 接口要求

`GET /api/wardrobe/items` 必须：

1. 返回 `{ "items": [], "total": 0 }`。
2. 支持 `category` 筛选。
3. 支持 `color` 筛选。
4. 支持 `source_type` 筛选。
5. 支持 `low_usage=true` 筛选。

## 6. 允许 mock 的内容

这些都可以 mock：

```txt
衣物识别
白底图生成
image_embedding
text_embedding
重复判断
```

但函数边界要保留：

```python
detect_clothing_items(image_path: str, source_type: str)
generate_cutout_image(image_path: str, temp_id: str)
generate_image_embedding(image_path: str)
generate_text_embedding(text: str)
```

## 7. 最终验收效果

做到下面这些才算完成：

```txt
上传一张图片后，接口返回 2 件 detected_items
detect 后立刻查衣橱，衣橱里不会新增 item
batch-confirm 两件都 save=true 后，衣橱新增 2 件 item
batch-confirm 一件 save=true、一件 save=false 后，只新增 1 件 item
GET /api/wardrobe/items 能看到保存的 item
GET /api/wardrobe/items?category=top 只返回上衣
GET /api/wardrobe/items?source_type=closet_photo 只返回对应来源
重复上传相似白色衬衫时，返回 duplicate_warnings
```

## 8. 测试方案

新增测试文件：

```txt
backend/tests/test_wardrobe.py
```

必须写这些测试：

```txt
test_detect_returns_multiple_items_without_persisting
test_detect_accepts_source_type
test_batch_confirm_saves_only_selected_items
test_batch_confirm_returns_saved_items_and_total
test_list_items_returns_saved_items
test_list_items_filters_by_category
test_list_items_filters_by_source_type
test_duplicate_warning_for_similar_item
test_invalid_upload_file_type_returns_400
```

每个测试的验收点：

```txt
detect 返回状态码 200
detect 返回 detected_items 长度 >= 2
detect 返回字段包含 temp_id/category/color/occasion/cutout_image_url
detect 不写入数据库 item 表
batch-confirm 后数据库 item 数量正确
list 查询返回 total 正确
非法文件类型返回 400 和 INVALID_FILE_TYPE
```

测试命令：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

## 9. 手动联调 curl

启动服务：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

上传检测：

```bash
curl -X POST http://127.0.0.1:8000/api/wardrobe/items/detect \
  -F "file=@/path/to/test.jpg" \
  -F "source_type=closet_photo"
```

批量确认：

```bash
curl -X POST http://127.0.0.1:8000/api/wardrobe/items/batch-confirm \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "upload_001",
    "source_type": "closet_photo",
    "items": [
      {
        "temp_id": "det_001",
        "name": "白色衬衫",
        "category": "top",
        "color": "白色",
        "season": ["spring", "summer"],
        "style": ["通勤", "简约"],
        "occasion": ["通勤", "上课"],
        "material": "棉",
        "fit": "常规",
        "description": "白色常规版型衬衫",
        "cutout_image_url": "/uploads/mock.jpg",
        "save": true
      }
    ]
  }'
```

查询衣橱：

```bash
curl "http://127.0.0.1:8000/api/wardrobe/items?category=top"
```

## 10. 给这台电脑 Codex 的启动提示词

```txt
你负责 IF.LAND 的电脑 A：衣橱资产标准化与入库。

先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-a-wardrobe.md
3. docs/api-contract.md

在分支 codex/wardrobe-standardization 开发。

只实现衣橱模块：
- POST /api/wardrobe/items/detect
- POST /api/wardrobe/items/batch-confirm
- GET /api/wardrobe/items

必须写 backend/tests/test_wardrobe.py，并按文档里的测试方案覆盖。
AI、白底图、embedding 都先 mock。
完成后运行 python -m pytest，提交并 push 到 codex/wardrobe-standardization。
不要提交 PRD、.venv、SQLite db、上传图片。
```
