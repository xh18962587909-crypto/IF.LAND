# 衣见 API 接口文档

版本：`v0.1.0`

后端 Base URL：

```txt
http://localhost:8000
```

前端环境变量：

```txt
VITE_API_BASE_URL=http://localhost:8000
```

接口文档地址：

```txt
http://localhost:8000/docs
```

## 1. 通用约定

### 1.1 请求格式

普通 JSON 请求：

```txt
Content-Type: application/json
```

图片上传请求：

```txt
Content-Type: multipart/form-data
```

### 1.2 图片 URL 规则

后端返回相对路径：

```json
{
  "image_url": "/uploads/item_001.jpg"
}
```

前端拼接完整地址：

```ts
const imageUrl = `${import.meta.env.VITE_API_BASE_URL}${item.image_url}`
```

最终图片地址：

```txt
http://localhost:8000/uploads/item_001.jpg
```

### 1.3 错误格式

FastAPI 默认错误会放在 `detail` 字段中。MVP 阶段统一使用：

```json
{
  "detail": {
    "code": "ITEM_NOT_FOUND",
    "message": "衣物不存在"
  }
}
```

常见错误码：

| code | status | 含义 |
| --- | ---: | --- |
| `INVALID_FILE_TYPE` | 400 | 上传文件类型不支持 |
| `ITEM_NOT_FOUND` | 404 | 衣物不存在 |
| `OUTFIT_NOT_FOUND` | 404 | 搭配不存在 |
| `AI_SERVICE_UNAVAILABLE` | 503 | AI 服务暂不可用 |

### 1.4 枚举约定

衣物大类 `category`：

```txt
top, bottom, outerwear, dress, shoes, bag, accessory
```

季节 `season`：

```txt
spring, summer, autumn, winter
```

购买建议 `decision`：

```txt
recommend, cautious, reject
```

前端展示文案建议：

| decision | 展示文案 |
| --- | --- |
| `recommend` | 建议买 |
| `cautious` | 谨慎买 |
| `reject` | 不建议买 |

图片来源 `source_type`：

```txt
manual_upload, product_screenshot, outfit_photo, closet_photo, order_screenshot
```

说明：

- `source_type` 用来降低冷启动成本，允许用户从商品截图、穿搭照、衣柜照、订单截图等入口逐步建立衣橱。
- embedding 属于后端内部召回字段，MVP API 不强制返回给前端。

## 2. 基础接口

### 2.1 健康检查

状态：已实现

```txt
GET /health
```

响应：

```json
{
  "status": "ok",
  "service": "if-land-backend",
  "version": "0.1.0"
}
```

### 2.2 就绪检查

状态：已实现

```txt
GET /ready
```

响应：

```json
{
  "status": "ready",
  "database": "ok",
  "uploads": "ok"
}
```

### 2.3 静态图片访问

状态：已实现

```txt
GET /uploads/{filename}
```

示例：

```txt
GET /uploads/item_001.jpg
```

## 3. 衣橱模块

### 3.1 上传图片并识别衣物

状态：待实现

```txt
POST /api/wardrobe/items/detect
```

请求：

```txt
multipart/form-data
file: 图片文件
source_type: manual_upload | product_screenshot | outfit_photo | closet_photo | order_screenshot
```

响应：

```json
{
  "upload_id": "upload_001",
  "original_image_url": "/uploads/upload_001_original.jpg",
  "source_type": "closet_photo",
  "detected_items": [
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
      "description": "白色常规版型衬衫，适合通勤和上课场景",
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
      "occasion": ["上课", "周末", "旅行"],
      "material": "牛仔",
      "fit": "直筒",
      "description": "浅蓝直筒牛仔裤，适合日常和轻松场景",
      "cutout_image_url": "/uploads/det_002_cutout.jpg",
      "confidence": 0.87
    }
  ]
}
```

说明：

- 这个接口只负责“识别”，不直接保存到衣橱。
- 一张照片中有多件衣服时，`detected_items` 返回多个候选单品。
- 前端需要展示候选卡片，让用户确认、修改标签或删除误识别项。
- `cutout_image_url` 第一版可以直接返回原图地址。
- AI 未接入前，后端可以使用 mock 标签。

### 3.2 确认识别结果并批量保存

状态：待实现

```txt
POST /api/wardrobe/items/batch-confirm
```

请求：

```json
{
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
      "description": "白色常规版型衬衫，适合通勤和上课场景",
      "cutout_image_url": "/uploads/det_001_cutout.jpg",
      "save": true
    },
    {
      "temp_id": "det_002",
      "name": "浅蓝牛仔裤",
      "category": "bottom",
      "color": "浅蓝色",
      "season": ["spring", "autumn"],
      "style": ["休闲", "日常"],
      "occasion": ["上课", "周末", "旅行"],
      "material": "牛仔",
      "fit": "直筒",
      "description": "浅蓝直筒牛仔裤，适合日常和轻松场景",
      "cutout_image_url": "/uploads/det_002_cutout.jpg",
      "save": true
    }
  ]
}
```

响应：

```json
{
  "saved_items": [
    {
      "id": 1,
      "name": "白色衬衫",
      "category": "top",
      "color": "白色",
      "season": ["spring", "summer"],
      "style": ["通勤", "简约"],
      "occasion": ["通勤", "上课"],
      "material": "棉",
      "fit": "常规",
      "description": "白色常规版型衬衫，适合通勤和上课场景",
      "source_type": "closet_photo",
      "usage_count": 0,
      "image_url": "/uploads/upload_001_original.jpg",
      "cutout_image_url": "/uploads/det_001_cutout.jpg",
      "created_at": "2026-06-06T12:00:00Z"
    },
    {
      "id": 2,
      "name": "浅蓝牛仔裤",
      "category": "bottom",
      "color": "浅蓝色",
      "season": ["spring", "autumn"],
      "style": ["休闲", "日常"],
      "occasion": ["上课", "周末", "旅行"],
      "material": "牛仔",
      "fit": "直筒",
      "description": "浅蓝直筒牛仔裤，适合日常和轻松场景",
      "source_type": "closet_photo",
      "usage_count": 0,
      "image_url": "/uploads/upload_001_original.jpg",
      "cutout_image_url": "/uploads/det_002_cutout.jpg",
      "created_at": "2026-06-06T12:00:00Z"
    }
  ],
  "total_saved": 2,
  "duplicate_warnings": [
    {
      "temp_id": "det_001",
      "similar_item_id": 9,
      "message": "可能和已有白色衬衫重复"
    }
  ]
}
```

说明：

- `save: false` 的候选项不入库。
- 用户修改过的字段以后端收到的请求为准。
- `image_url` 保留原始上传图，`cutout_image_url` 用于衣橱卡片展示。

### 3.3 获取衣橱列表

状态：待实现

```txt
GET /api/wardrobe/items
```

可选查询参数：

| 参数 | 类型 | 示例 | 含义 |
| --- | --- | --- | --- |
| `category` | string | `top` | 按衣物大类筛选 |
| `color` | string | `白色` | 按颜色筛选 |
| `source_type` | string | `closet_photo` | 按图片来源筛选 |
| `low_usage` | boolean | `true` | 只看低利用率单品 |

响应：

```json
{
  "items": [
    {
      "id": 1,
      "name": "白色衬衫",
      "category": "top",
      "color": "白色",
      "season": ["spring", "summer"],
      "style": ["通勤", "简约"],
      "occasion": ["通勤", "上课"],
      "material": "棉",
      "fit": "常规",
      "description": "白色常规版型衬衫，适合通勤和上课场景",
      "source_type": "closet_photo",
      "usage_count": 0,
      "image_url": "/uploads/item_001_original.jpg",
      "cutout_image_url": "/uploads/item_001_cutout.jpg",
      "created_at": "2026-06-06T12:00:00Z"
    }
  ],
  "total": 1
}
```

### 3.4 获取单件衣物

状态：待实现

```txt
GET /api/wardrobe/items/{item_id}
```

响应：

```json
{
  "id": 1,
  "name": "白色衬衫",
  "category": "top",
  "color": "白色",
  "season": ["spring", "summer"],
  "style": ["通勤", "简约"],
  "occasion": ["通勤", "上课"],
  "material": "棉",
  "fit": "常规",
  "description": "白色常规版型衬衫，适合通勤和上课场景",
  "source_type": "closet_photo",
  "usage_count": 0,
  "image_url": "/uploads/item_001_original.jpg",
  "cutout_image_url": "/uploads/item_001_cutout.jpg",
  "created_at": "2026-06-06T12:00:00Z"
}
```

### 3.5 修改衣物标签

状态：待实现

```txt
PATCH /api/wardrobe/items/{item_id}
```

请求：

```json
{
  "name": "白色短袖衬衫",
  "category": "top",
  "color": "白色",
  "season": ["spring", "summer"],
  "style": ["通勤", "简约"]
}
```

响应：返回修改后的衣物对象。

### 3.6 删除衣物

状态：待实现

```txt
DELETE /api/wardrobe/items/{item_id}
```

响应：

```json
{
  "deleted": true,
  "id": 1
}
```

## 4. 今日穿搭模块

### 4.1 推荐今日穿搭

状态：待实现

```txt
POST /api/outfits/recommend
```

请求：

```json
{
  "occasion": "通勤",
  "temperature": "18-25℃",
  "weather": "晴",
  "mood": ["轻松", "精致"],
  "style": ["浅色系", "显瘦"],
  "avoid": ["黑色"],
  "preferred_item_id": null
}
```

响应：

```json
{
  "outfits": [
    {
      "id": "outfit_001",
      "title": "浅色通勤搭配",
      "reason": "适合 18-25℃ 通勤场景，整体浅色，不包含黑色，并激活了一件低利用率单品。",
      "score": 86,
      "comfort_note": "适合 18-25℃ 晴天，不需要厚外套。",
      "scene_note": "适合通勤、上课和轻正式场景。",
      "items": [
        {
          "id": 1,
          "name": "白色衬衫",
          "category": "top",
          "color": "白色",
          "image_url": "/uploads/item_001_cutout.jpg"
        },
        {
          "id": 2,
          "name": "浅蓝牛仔裤",
          "category": "bottom",
          "color": "浅蓝色",
          "image_url": "/uploads/item_002_cutout.jpg"
        }
      ],
      "replace_suggestions": [
        {
          "category": "outerwear",
          "label": "换一件外套"
        },
        {
          "category": "shoes",
          "label": "鞋子换舒服点"
        }
      ],
      "try_on_image_url": "/uploads/mock_try_on_001.jpg"
    }
  ]
}
```

### 4.2 替换搭配中的单品

状态：待实现

```txt
POST /api/outfits/replace
```

请求：

```json
{
  "current_item_ids": [1, 2, 3],
  "replace_category": "top",
  "constraints": {
    "occasion": "通勤",
    "temperature": "18-25℃",
    "avoid": ["黑色"],
    "style": ["更正式一点"]
  }
}
```

响应：

```json
{
  "outfit": {
    "id": "outfit_002",
    "title": "更正式的通勤搭配",
    "reason": "保留下装和鞋子，只替换上衣，避开黑色并提高正式感。",
    "score": 88,
    "comfort_note": "适合 18-25℃ 室内外通勤。",
    "scene_note": "比上一套更正式。",
    "items": [
      {
        "id": 4,
        "name": "米色针织上衣",
        "category": "top",
        "color": "米色",
        "image_url": "/uploads/item_004_cutout.jpg"
      },
      {
        "id": 2,
        "name": "浅蓝牛仔裤",
        "category": "bottom",
        "color": "浅蓝色",
        "image_url": "/uploads/item_002_cutout.jpg"
      }
    ],
    "replace_suggestions": [
      {
        "category": "outerwear",
        "label": "换一件外套"
      }
    ],
    "try_on_image_url": "/uploads/mock_try_on_002.jpg"
  }
}
```

### 4.3 确认今天穿这套

状态：待实现

```txt
POST /api/outfits/confirm
```

请求：

```json
{
  "item_ids": [1, 2, 3],
  "feedback": "like"
}
```

响应：

```json
{
  "confirmed": true,
  "worn_record_id": 1
}
```

## 5. 买前决策模块

### 5.1 上传商品图并生成购买建议

状态：待实现

```txt
POST /api/purchase/analyze
```

请求：

```txt
multipart/form-data
file: 商品图片
```

响应：

```json
{
  "candidate_item": {
    "name": "灰色西装外套",
    "category": "outerwear",
    "color": "灰色",
    "season": ["spring", "autumn"],
    "style": ["通勤", "正式"],
    "occasion": ["通勤", "面试", "正式场合"],
    "material": "聚酯纤维",
    "fit": "宽松",
    "description": "灰色宽松西装外套，适合春秋通勤和正式场景",
    "image_url": "/uploads/candidate_001.jpg",
    "cutout_image_url": "/uploads/candidate_001_cutout.jpg"
  },
  "decision": "cautious",
  "decision_text": "谨慎买",
  "purchase_score": 72,
  "reasons": [
    "可搭配 2 套已有衣物",
    "适合通勤场景",
    "与已有灰色外套存在一定重复"
  ],
  "risks": [
    "重复度偏高",
    "可穿场景集中在通勤"
  ],
  "matched_existing_items": [
    {
      "id": 8,
      "name": "深灰西装外套",
      "category": "outerwear",
      "color": "深灰色",
      "similarity": 0.82,
      "image_url": "/uploads/item_008_cutout.jpg"
    }
  ],
  "outfit_options": [
    {
      "id": "purchase_outfit_001",
      "title": "灰色外套通勤搭配",
      "items": [
        {
          "id": 1,
          "name": "白色衬衫",
          "category": "top",
          "image_url": "/uploads/item_001_cutout.jpg"
        }
      ],
      "try_on_image_url": "/uploads/mock_try_on_purchase_001.jpg",
      "try_on_prompt": "模特全身照，站姿自然，干净背景，柔和自然光。穿搭包括灰色西装外套、白色衬衫和浅蓝牛仔裤。风格为通勤、简约、轻正式。画面用途是穿搭氛围预览，不追求精确虚拟试衣。"
    }
  ],
  "alternative_plan": "可以先用已有深灰西装外套搭配白色衬衫和浅蓝牛仔裤，效果接近。",
  "try_on_image_url": "/uploads/mock_try_on_purchase_001.jpg",
  "try_on_prompt": "模特全身照，站姿自然，干净背景，柔和自然光。穿搭包括灰色西装外套、白色衬衫和浅蓝牛仔裤。风格为通勤、简约、轻正式。画面用途是穿搭氛围预览，不追求精确虚拟试衣。"
}
```

### 5.2 将候选商品加入衣橱

状态：待实现

```txt
POST /api/purchase/convert-to-wardrobe
```

请求：

```json
{
  "candidate_item": {
    "name": "灰色西装外套",
    "category": "outerwear",
    "color": "灰色",
    "season": ["spring", "autumn"],
    "style": ["通勤", "正式"],
    "occasion": ["通勤", "面试", "正式场合"],
    "material": "聚酯纤维",
    "fit": "宽松",
    "description": "灰色宽松西装外套，适合春秋通勤和正式场景",
    "image_url": "/uploads/candidate_001.jpg",
    "cutout_image_url": "/uploads/candidate_001_cutout.jpg"
  }
}
```

响应：返回新加入衣橱的衣物对象。

## 6. 前端调用示例

### 6.1 上传图片并识别多件衣物

```ts
const formData = new FormData()
formData.append("file", file)
formData.append("source_type", "closet_photo")

const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/wardrobe/items/detect`, {
  method: "POST",
  body: formData,
})

if (!response.ok) {
  const error = await response.json()
  throw new Error(error.detail?.message ?? "上传失败")
}

const detection = await response.json()
```

### 6.2 确认并保存识别结果

```ts
const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/wardrobe/items/batch-confirm`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    upload_id: detection.upload_id,
    items: detection.detected_items.map((item) => ({
      ...item,
      save: true,
    })),
  }),
})

const result = await response.json()
```

### 6.3 获取衣橱

```ts
const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/wardrobe/items`)
const data = await response.json()
```

### 6.4 推荐穿搭

```ts
const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/outfits/recommend`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    occasion: "通勤",
    temperature: "18-25℃",
    weather: "晴",
    mood: ["轻松"],
    style: ["浅色系"],
    avoid: ["黑色"],
  }),
})

const data = await response.json()
```

## 7. 开发优先级

第一批必须实现：

```txt
GET  /health
GET  /ready
POST /api/wardrobe/items/detect
POST /api/wardrobe/items/batch-confirm
GET  /api/wardrobe/items
POST /api/outfits/recommend
POST /api/purchase/analyze
```

第二批再实现：

```txt
GET    /api/wardrobe/items/{item_id}
PATCH  /api/wardrobe/items/{item_id}
DELETE /api/wardrobe/items/{item_id}
POST   /api/outfits/replace
POST   /api/outfits/confirm
POST   /api/purchase/convert-to-wardrobe
```
