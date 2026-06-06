# 电脑 C：买前决策、AI mock 与视觉生成兜底

一句话任务：你负责判断“这件衣服值不值得买”，并返回能用于路演展示的购买报告、搭配方案和模拟上身 mock。

## 1. 你负责什么

你不负责衣橱上传，也不负责今日穿搭主推荐。

你要做出这个效果：

```txt
用户上传一张商品图
-> 后端保存商品图
-> 后端 mock 识别商品为 candidate_item
-> 后端和已有衣橱比对
-> 后端判断重复度、可搭配数量、衣橱缺口、场景适配
-> 返回建议买 / 谨慎买 / 不建议买
-> 返回理由、风险、搭配方案、替代方案、try_on mock
```

## 2. 你的分支

```bash
git checkout -b codex/purchase-vision
```

## 3. 必须实现的接口

必须完成：

```txt
POST /api/purchase/analyze
```

有时间再做：

```txt
POST /api/purchase/convert-to-wardrobe
```

还要新增/补充这些服务函数：

```txt
vision_service.analyze_product
try_on_service.build_try_on_prompt
try_on_service.generate_try_on_preview
embedding_service.generate_image_embedding
embedding_service.generate_text_embedding
```

## 4. 必须修改/新增的文件

主要文件：

```txt
backend/app/routers/purchase.py
backend/app/services/purchase_service.py
backend/app/services/vision_service.py
backend/app/services/try_on_service.py
backend/app/services/embedding_service.py
backend/app/schemas.py
backend/tests/test_purchase.py
```

可能读取但尽量少改：

```txt
backend/app/models.py
backend/app/db.py
```

只允许最小修改：

```txt
backend/app/main.py
```

只在 `main.py` 里注册 router：

```python
from app.routers import purchase

app.include_router(purchase.router, prefix="/api/purchase", tags=["purchase"])
```

不要修改：

```txt
docs/api-contract.md
docs/codex-collaboration/computer-a-wardrobe.md
docs/codex-collaboration/computer-b-outfit.md
```

## 5. 硬性要求

### 5.1 analyze 接口响应必须包含

```txt
candidate_item
decision
decision_text
purchase_score
reasons
risks
matched_existing_items
outfit_options
alternative_plan
try_on_image_url
try_on_prompt
```

### 5.2 candidate_item 必须包含

```txt
name
category
color
season
style
occasion
material
fit
description
image_url
cutout_image_url
```

### 5.3 decision 规则

必须使用这三个值：

```txt
recommend
cautious
reject
```

展示文案：

```txt
recommend -> 建议买
cautious -> 谨慎买
reject -> 不建议买
```

### 5.4 purchase_score 规则

必须按这个结构计算：

```txt
outfit_score: 0-40
gap_score: 0-30
occasion_score: 0-20
duplicate_penalty: 0-30

purchase_score = outfit_score + gap_score + occasion_score - duplicate_penalty
```

最后把 `purchase_score` 限制在 0-100。

映射：

```txt
80-100 -> recommend
50-79  -> cautious
0-49   -> reject
```

### 5.5 try-on 要求

必须返回：

```txt
try_on_image_url 或 try_on_prompt
```

不能在文案里承诺“高精度虚拟试衣”。只能表达为：

```txt
穿搭氛围预览
模拟上身参考
效果图 mock
```

## 6. 允许 mock 的内容

这些都可以 mock：

```txt
商品图识别
白底素材
embedding
模拟上身图片
可搭配方案生成
```

但购买建议不能纯随机。必须由这些因素决定：

```txt
重复度
可搭配套数
是否补足衣橱缺口
是否适合高频场景
```

## 7. 最终验收效果

做到下面这些才算完成：

```txt
上传商品图后返回 candidate_item
candidate_item 是一件灰色西装外套或其他 mock 商品
返回 purchase_score，且范围是 0-100
返回 decision 和 decision_text，且映射正确
衣橱里已有相似外套时，matched_existing_items 不为空
可搭配方案不少于 1 套
reasons 至少 3 条
risks 至少 2 条
返回 alternative_plan
返回 try_on_image_url 或 try_on_prompt
重复高、可搭配少时，decision 不能是 recommend
```

## 8. 测试方案

新增测试文件：

```txt
backend/tests/test_purchase.py
```

必须写这些测试：

```txt
test_analyze_returns_purchase_report
test_analyze_returns_candidate_item_required_fields
test_purchase_score_is_between_0_and_100
test_decision_text_matches_decision
test_high_duplicate_penalty_prevents_recommend
test_analyze_returns_matched_existing_items_when_similar_item_exists
test_analyze_returns_outfit_options
test_analyze_returns_try_on_preview
test_invalid_upload_file_type_returns_400
```

每个测试的验收点：

```txt
analyze 状态码 200
candidate_item 字段完整
purchase_score >= 0 且 <= 100
decision 只能是 recommend/cautious/reject
decision_text 和 decision 对应
matched_existing_items 是数组
outfit_options 是数组
try_on_image_url 或 try_on_prompt 存在
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

买前分析：

```bash
curl -X POST http://127.0.0.1:8000/api/purchase/analyze \
  -F "file=@/path/to/product.jpg"
```

加入衣橱：

```bash
curl -X POST http://127.0.0.1:8000/api/purchase/convert-to-wardrobe \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_item": {
      "name": "灰色西装外套",
      "category": "outerwear",
      "color": "灰色",
      "season": ["spring", "autumn"],
      "style": ["通勤", "正式"],
      "occasion": ["通勤", "面试"],
      "material": "聚酯纤维",
      "fit": "宽松",
      "description": "灰色宽松西装外套",
      "image_url": "/uploads/candidate_001.jpg",
      "cutout_image_url": "/uploads/candidate_001_cutout.jpg"
    }
  }'
```

## 10. 给这台电脑 Codex 的启动提示词

```txt
你负责 IF.LAND 的电脑 C：买前决策、AI mock 与视觉生成兜底。

先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-c-purchase-ai.md
3. docs/api-contract.md

在分支 codex/purchase-vision 开发。

只实现买前决策模块：
- POST /api/purchase/analyze
- POST /api/purchase/convert-to-wardrobe

必须写 backend/tests/test_purchase.py，并按文档里的测试方案覆盖。
商品识别、白底素材、embedding、try-on 都先 mock。
purchase_score 必须按文档规则计算。
完成后运行 python -m pytest，提交并 push 到 codex/purchase-vision。
不要提交 PRD、.venv、SQLite db、上传图片。
```
