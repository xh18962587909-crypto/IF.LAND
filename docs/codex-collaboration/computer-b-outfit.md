# 电脑 B：今日穿搭模块开发说明

你负责让衣服“搭得出来、换得动”。这个模块服务首页“今日穿搭”。

## 你的分支

```bash
git checkout -b codex/outfit-api
```

## 你要实现的接口

以 `docs/api-contract.md` 为准，实现：

```txt
POST /api/outfits/recommend
POST /api/outfits/replace
POST /api/outfits/confirm
```

第一优先级：

```txt
POST /api/outfits/recommend
```

## 推荐文件边界

你主要改：

```txt
backend/app/routers/outfit.py
backend/app/services/outfit_service.py
backend/app/schemas.py
backend/tests/test_outfit.py
```

你可能需要读但尽量少改：

```txt
backend/app/models.py
backend/app/db.py
docs/api-contract.md
```

如果电脑 A 的衣橱模块还没合并，你可以先在测试里直接创建 SQLite item 数据，或者在 service 里写一个空衣橱 fallback。

## 功能设计

`POST /api/outfits/recommend`：

1. 接收 `occasion`、`temperature`、`weather`、`style`、`avoid`、`preferred_item_id`。
2. 从 SQLite 读取衣橱单品。
3. 过滤掉 `avoid` 中提到的颜色或风格。
4. 尽量组合 `top + bottom + shoes + outerwear`。
5. 衣橱不完整时，也要返回可演示结果，不要直接报错。
6. 返回 1-3 套 outfit。

`POST /api/outfits/replace`：

1. 接收当前搭配 item ids。
2. 锁定不需要替换的 item。
3. 只替换 `replace_category` 对应品类。
4. 返回新版 outfit。

`POST /api/outfits/confirm`：

1. 接收 `item_ids` 和 `feedback`。
2. 第一版可以只返回确认成功。
3. 如果电脑 A 已经支持 `usage_count`，可以给对应 item 的使用次数 +1。

## 推荐规则算法

第一版不要接 AI，直接规则化：

```txt
基础分 60
符合 occasion +10
符合 season/weather +10
未命中 avoid +10
包含低利用率 item +5
颜色不冲突 +5
```

没有鞋子或外套时也可以生成搭配，reason 里说明“当前衣橱缺少鞋/外套数据”。

## 给这台电脑 Codex 的启动提示词

复制下面这段给电脑 B 的 Codex：

```txt
你现在负责 IF.LAND 项目的今日穿搭模块后端开发。

请先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-b-outfit.md
3. docs/api-contract.md
4. backend/app/main.py
5. backend/app/models.py

目标是在分支 codex/outfit-api 上实现：
- POST /api/outfits/recommend

可以继续实现：
- POST /api/outfits/replace
- POST /api/outfits/confirm

要求：
- 使用 FastAPI + Pydantic/SQLModel。
- 用测试驱动开发，新增 backend/tests/test_outfit.py。
- 第一版用规则推荐，不接真实 AI。
- 衣橱数据不足时也要返回可演示结果或清晰错误，不要崩溃。
- 返回格式必须符合 docs/api-contract.md。
- 跑通 python -m pytest。
- 完成后提交并 push 到 codex/outfit-api。
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
衣橱有 top/bottom 时，recommend 返回 outfits 数组
avoid 黑色时，不返回黑色 item
replace_category = top 时，只替换上衣
confirm 返回 confirmed = true
```

## 交接内容

完成后汇报：

```txt
分支：codex/outfit-api
完成接口：
测试结果：
依赖电脑 A 的地方：
```
