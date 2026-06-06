# 电脑 C：买前决策 + AI mock 开发说明

你负责让产品“看起来聪明”：商品图识别、重复判断、搭配能力分析、购买建议。

## 你的分支

```bash
git checkout -b codex/purchase-ai
```

## 你要实现的接口

以 `docs/api-contract.md` 为准，实现：

```txt
POST /api/purchase/analyze
POST /api/purchase/convert-to-wardrobe
```

第一优先级：

```txt
POST /api/purchase/analyze
```

## 推荐文件边界

你主要改：

```txt
backend/app/routers/purchase.py
backend/app/services/purchase_service.py
backend/app/services/vision_service.py
backend/app/schemas.py
backend/tests/test_purchase.py
```

你可能需要读但尽量少改：

```txt
backend/app/models.py
backend/app/db.py
docs/api-contract.md
```

如果电脑 A 已经创建了 `vision_service.py`，不要覆盖它；在原文件里补充 `analyze_product`，或者和电脑 A 约定函数名。

## 功能设计

`POST /api/purchase/analyze`：

1. 接收商品图片。
2. 保存商品图到 `uploads/`。
3. 调用 `vision_service.analyze_product(image_path)`，第一版 mock。
4. 从衣橱读取已有 item。
5. 计算重复风险、可搭配数量、缺口价值、场景适配。
6. 返回 `decision`、`decision_text`、`purchase_score`、`reasons`、`risks`、`matched_existing_items`、`outfit_options`、`alternative_plan`。

`POST /api/purchase/convert-to-wardrobe`：

1. 接收 `candidate_item`。
2. 写入衣橱。
3. 返回新 item。

如果电脑 A 的衣橱写入还没有合并，这个接口可以先暂缓。

## purchase_score 规则

第一版建议：

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

## mock 商品识别

`vision_service.analyze_product` 可以固定返回：

```json
{
  "name": "灰色西装外套",
  "category": "outerwear",
  "color": "灰色",
  "season": ["spring", "autumn"],
  "style": ["通勤", "正式"],
  "material": "聚酯纤维",
  "fit": "宽松",
  "image_url": "/uploads/candidate_001.jpg"
}
```

## 给这台电脑 Codex 的启动提示词

复制下面这段给电脑 C 的 Codex：

```txt
你现在负责 IF.LAND 项目的买前决策和 AI mock 后端开发。

请先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-c-purchase-ai.md
3. docs/api-contract.md
4. backend/app/main.py
5. backend/app/models.py

目标是在分支 codex/purchase-ai 上实现：
- POST /api/purchase/analyze

可以继续实现：
- POST /api/purchase/convert-to-wardrobe

要求：
- 使用 FastAPI + Pydantic/SQLModel。
- 用测试驱动开发，新增 backend/tests/test_purchase.py。
- AI 商品识别先 mock，不接真实模型。
- purchase_score 按文档规则计算。
- 输出文案要适合路演展示，理由要具体。
- 返回格式必须符合 docs/api-contract.md。
- 跑通 python -m pytest。
- 完成后提交并 push 到 codex/purchase-ai。
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
上传商品图后返回 decision 和 purchase_score
有相似衣物时 matched_existing_items 不为空
purchase_score 在 0-100 范围
decision_text 与 decision 匹配
```

## 交接内容

完成后汇报：

```txt
分支：codex/purchase-ai
完成接口：
测试结果：
vision_service 新增了哪些函数：
依赖电脑 A 的地方：
```
