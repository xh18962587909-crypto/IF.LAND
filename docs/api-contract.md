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

### 3.1 上传衣物图片

状态：待实现

```txt
POST /api/wardrobe/items/upload
```

请求：

```txt
multipart/form-data
file: 图片文件
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
  "material": "棉",
  "fit": "常规",
  "usage_count": 0,
  "image_url": "/uploads/item_001_original.jpg",
  "cutout_image_url": "/uploads/item_001_cutout.jpg",
  "created_at": "2026-06-06T12:00:00Z"
}
```

说明：

- `cutout_image_url` 第一版可以直接返回原图地址。
- AI 未接入前，后端可以使用 mock 标签。

### 3.2 获取衣橱列表

状态：待实现

```txt
GET /api/wardrobe/items
```

可选查询参数：

| 参数 | 类型 | 示例 | 含义 |
| --- | --- | --- | --- |
| `category` | string | `top` | 按衣物大类筛选 |
| `color` | string | `白色` | 按颜色筛选 |
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
      "material": "棉",
      "fit": "常规",
      "usage_count": 0,
      "image_url": "/uploads/item_001_original.jpg",
      "cutout_image_url": "/uploads/item_001_cutout.jpg",
      "created_at": "2026-06-06T12:00:00Z"
    }
  ],
  "total": 1
}
```

### 3.3 获取单件衣物

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
  "material": "棉",
  "fit": "常规",
  "usage_count": 0,
  "image_url": "/uploads/item_001_original.jpg",
  "cutout_image_url": "/uploads/item_001_cutout.jpg",
  "created_at": "2026-06-06T12:00:00Z"
}
```

### 3.4 修改衣物标签

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

### 3.5 删除衣物

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
      ]
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
    ]
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
    "image_url": "/uploads/candidate_001.jpg"
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
      ]
    }
  ],
  "alternative_plan": "可以先用已有深灰西装外套搭配白色衬衫和浅蓝牛仔裤，效果接近。"
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
    "image_url": "/uploads/candidate_001.jpg"
  }
}
```

响应：返回新加入衣橱的衣物对象。

## 6. 前端调用示例

### 6.1 上传图片

```ts
const formData = new FormData()
formData.append("file", file)

const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/wardrobe/items/upload`, {
  method: "POST",
  body: formData,
})

if (!response.ok) {
  const error = await response.json()
  throw new Error(error.detail?.message ?? "上传失败")
}

const item = await response.json()
```

### 6.2 获取衣橱

```ts
const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/wardrobe/items`)
const data = await response.json()
```

### 6.3 推荐穿搭

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
POST /api/wardrobe/items/upload
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
