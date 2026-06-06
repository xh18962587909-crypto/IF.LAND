# 电脑 B：每日穿搭召回与多轮调整

一句话任务：你负责从衣橱里选衣服，生成“今天能穿”的 2-3 套搭配，并支持用户说“换一件”“不要黑色”“更正式一点”。

## 1. 你负责什么

你不负责上传衣服，也不负责买前分析。

你要做出这个效果：

```txt
数据库里已经有衣服
-> 用户输入天气、气温、场景、风格、禁忌
-> 后端召回合适单品
-> 后端返回 2-3 套穿搭
-> 每套有理由、分数、替换建议、mock 上身图
-> 用户要求替换某类单品时，只替换那一类
```

## 2. 你的分支

```bash
git checkout -b codex/outfit-recall
```

## 3. 必须实现的接口

必须完成：

```txt
POST /api/outfits/recommend
```

有时间再做：

```txt
POST /api/outfits/replace
POST /api/outfits/confirm
```

## 4. 必须修改/新增的文件

主要文件：

```txt
backend/app/routers/outfit.py
backend/app/services/outfit_service.py
backend/app/services/try_on_service.py
backend/app/schemas.py
backend/tests/test_outfit.py
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
from app.routers import outfit

app.include_router(outfit.router, prefix="/api/outfits", tags=["outfits"])
```

不要修改：

```txt
docs/api-contract.md
docs/codex-collaboration/computer-a-wardrobe.md
docs/codex-collaboration/computer-c-purchase-ai.md
```

## 5. 硬性要求

### 5.1 recommend 请求必须支持

```txt
occasion
temperature
weather
mood
style
avoid
preferred_item_id
```

### 5.2 recommend 响应必须包含

每个 outfit 必须包含：

```txt
id
title
reason
score
comfort_note
scene_note
items
replace_suggestions
try_on_image_url
```

每个 item 至少包含：

```txt
id
name
category
color
image_url
```

### 5.3 推荐逻辑要求

必须做到：

```txt
avoid 里有黑色，就不能推荐 color=黑色 的衣物
preferred_item_id 不为空时，推荐结果必须尽量包含该 item
temperature/weather/season 至少参与打分说明
occasion/style 至少参与筛选或打分
每套 score 必须在 0-100
衣橱不完整时不能崩溃
```

### 5.4 replace 接口要求

`POST /api/outfits/replace` 必须做到：

```txt
只替换 replace_category 对应品类
其他品类 item 保持不变
新的 outfit 仍然包含 reason、score、items、try_on_image_url
```

### 5.5 confirm 接口要求

`POST /api/outfits/confirm` 必须做到：

```txt
返回 confirmed=true
记录 worn_record_id 或 mock record id
尽量更新 usage_count
```

## 6. 允许 mock 的内容

这些都可以 mock：

```txt
try_on_image_url
长期偏好记忆
复杂颜色协调算法
复杂 embedding 召回
```

但穿搭推荐本身不能完全随机，必须能解释：

```txt
为什么适合场景
为什么适合天气
为什么避开了用户禁忌
为什么推荐这件低利用率单品
```

## 7. 推荐算法第一版

使用规则分数：

```txt
基础分 50
符合 occasion +15
符合 temperature/season +10
命中 style +10
避开 avoid +10
激活低利用率单品 +5
品类完整 +5
颜色协调 +5
```

最终 score 限制在 0-100。

## 8. 最终验收效果

做到下面这些才算完成：

```txt
数据库里有白色上衣、蓝色裤子、黑色鞋子、米色外套
用户请求 avoid=["黑色"] 时，返回 outfit 不包含黑色鞋子
用户请求 occasion="通勤" 时，reason 里解释适合通勤
用户请求 temperature="18-25℃" 时，comfort_note 里解释天气适配
recommend 返回 2-3 套 outfit，或衣橱不足时返回清晰 fallback
replace_category="outerwear" 时，只替换外套，其他 item id 不变
confirm 后返回 confirmed=true
```

## 9. 测试方案

新增测试文件：

```txt
backend/tests/test_outfit.py
```

必须写这些测试：

```txt
test_recommend_returns_outfits_from_seeded_wardrobe
test_recommend_excludes_avoided_color
test_recommend_includes_preferred_item_when_possible
test_recommend_returns_required_display_fields
test_recommend_handles_incomplete_wardrobe_without_crashing
test_replace_only_changes_requested_category
test_confirm_returns_confirmed_true
test_outfit_score_is_between_0_and_100
```

每个测试的验收点：

```txt
recommend 状态码 200
outfits 是数组
outfits 长度在 1-3 之间
每套 outfit 有 reason/score/items/replace_suggestions/try_on_image_url
avoid 黑色时 items 中没有 color=黑色
replace 后非替换品类 id 不变
score >= 0 且 <= 100
```

测试命令：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

## 10. 手动联调 curl

启动服务：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

推荐穿搭：

```bash
curl -X POST http://127.0.0.1:8000/api/outfits/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "occasion": "通勤",
    "temperature": "18-25℃",
    "weather": "晴",
    "mood": ["轻松"],
    "style": ["浅色系"],
    "avoid": ["黑色"],
    "preferred_item_id": null
  }'
```

替换外套：

```bash
curl -X POST http://127.0.0.1:8000/api/outfits/replace \
  -H "Content-Type: application/json" \
  -d '{
    "current_item_ids": [1, 2, 3],
    "replace_category": "outerwear",
    "constraints": {
      "occasion": "通勤",
      "temperature": "18-25℃",
      "avoid": ["黑色"],
      "style": ["更正式一点"]
    }
  }'
```

确认穿搭：

```bash
curl -X POST http://127.0.0.1:8000/api/outfits/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "item_ids": [1, 2, 3],
    "feedback": "like"
  }'
```

## 11. 给这台电脑 Codex 的启动提示词

```txt
你负责 IF.LAND 的电脑 B：每日穿搭召回与多轮调整。

先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-b-outfit.md
3. docs/api-contract.md

在分支 codex/outfit-recall 开发。

只实现穿搭模块：
- POST /api/outfits/recommend
- POST /api/outfits/replace
- POST /api/outfits/confirm

必须写 backend/tests/test_outfit.py，并按文档里的测试方案覆盖。
第一版使用规则召回和评分，try_on_image_url 先 mock。
完成后运行 python -m pytest，提交并 push 到 codex/outfit-recall。
不要提交 PRD、.venv、SQLite db、上传图片。
```
