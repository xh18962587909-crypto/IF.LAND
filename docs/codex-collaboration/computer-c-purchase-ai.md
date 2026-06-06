# 电脑 C：买前决策、AI mock 与视觉生成兜底

你负责让产品“判断得像真的、展示得像真的”。新方案 v1.0 强调买前决策、白底素材、模拟上身三种体验并行存在，黑客松阶段不要完全依赖高精度试穿生成。

## 1. 你的分支

```bash
git checkout -b codex/purchase-vision
```

## 2. 你要实现的接口

第一优先级：

```txt
POST /api/purchase/analyze
```

第二优先级：

```txt
POST /api/purchase/convert-to-wardrobe
```

你还要补服务：

```txt
vision_service.analyze_product
try_on_service.build_try_on_prompt
try_on_service.generate_try_on_preview
embedding_service mock 函数
```

## 3. 你负责的产品能力

用户上传想买的商品图，系统要输出：

```txt
商品临时衣物 candidate_item
是否重复
能搭几套
是否补足衣橱缺口
适合哪些场景
建议买 / 谨慎买 / 不建议买
具体理由
风险点
可搭配方案
替代方案
模拟上身图 mock
```

模拟上身定位：

```txt
穿搭氛围预览
不是高精度虚拟试衣
第一版可以返回预生成图片或 mock URL
```

## 4. 推荐文件边界

主要修改：

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
docs/api-contract.md
```

如果电脑 A 已经创建了 `vision_service.py` 或 `embedding_service.py`，不要覆盖；在原文件里补函数。

## 5. 实现细节

`POST /api/purchase/analyze`：

1. 接收商品图。
2. 保存商品图到 `uploads/`。
3. 调用 `vision_service.analyze_product(image_path)`，第一版 mock。
4. 把商品标准化成 `candidate_item`。
5. 与已有衣橱比对重复度。
6. 计算可搭配套数。
7. 判断是否补足缺口。
8. 生成购买建议和风险。
9. 生成 `try_on_image_url` 或 `try_on_prompt`。

`POST /api/purchase/convert-to-wardrobe`：

1. 接收 `candidate_item`。
2. 写入衣橱。
3. 返回新 item。

如果电脑 A 的衣橱写入还没合并，这个接口可以先返回 mock 或暂缓。

## 6. purchase_score 规则

第一版规则：

```txt
搭配能力分 outfit_score: 0-40
缺口补足分 gap_score: 0-30
场景适配分 occasion_score: 0-20
重复惩罚 duplicate_penalty: 0-30

purchase_score = outfit_score + gap_score + occasion_score - duplicate_penalty
```

映射：

```txt
80-100: recommend / 建议买
50-79: cautious / 谨慎买
0-49: reject / 不建议买
```

## 7. mock 商品识别

`vision_service.analyze_product` 可以固定返回：

```json
{
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
```

## 8. try-on prompt 规则

先构建 prompt，不强依赖真实图片生成：

```txt
模特全身照，站姿自然，干净背景，柔和自然光。
穿搭包括：灰色西装外套、白色衬衫、浅蓝牛仔裤。
风格：通勤、简约、轻正式。
画面用途：穿搭氛围预览，不追求精确虚拟试衣。
```

`generate_try_on_preview` 第一版可以返回：

```json
{
  "try_on_image_url": "/uploads/mock_try_on_001.jpg",
  "try_on_prompt": "..."
}
```

## 9. 给这台电脑 Codex 的启动提示词

复制下面这段给电脑 C 的 Codex：

```txt
你现在负责 IF.LAND 项目的买前决策、AI mock 与视觉生成兜底模块。

请先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-c-purchase-ai.md
3. docs/api-contract.md
4. backend/app/main.py
5. backend/app/models.py

请在分支 codex/purchase-vision 上开发。

目标：
- 实现 POST /api/purchase/analyze
- 尽量实现 POST /api/purchase/convert-to-wardrobe
- 补充 vision_service.analyze_product
- 补充 try_on_service.build_try_on_prompt / generate_try_on_preview

要求：
- 使用 FastAPI + Pydantic/SQLModel。
- 用测试驱动开发，新增 backend/tests/test_purchase.py。
- AI 商品识别、白底素材、embedding、模拟上身都先 mock。
- purchase_score 按文档规则计算。
- 输出文案要适合路演展示，理由要具体。
- 返回 matched_existing_items、outfit_options、risks、alternative_plan、try_on_image_url。
- 不要承诺高精度虚拟试衣，只做穿搭氛围预览。
- 跑通 cd backend && source .venv/bin/activate && python -m pytest。
- 完成后提交并 push 到 codex/purchase-vision。
- 不要提交 PRD、.venv、SQLite db、上传图片。
```

## 10. 验收标准

必须验证：

```txt
上传商品图后返回 decision 和 purchase_score
purchase_score 在 0-100 范围
decision_text 与 decision 匹配
有相似衣物时 matched_existing_items 不为空
返回 outfit_options
返回 try_on_image_url 或 try_on_prompt
重复高且搭配少时返回 reject 或 cautious
```

测试命令：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```
