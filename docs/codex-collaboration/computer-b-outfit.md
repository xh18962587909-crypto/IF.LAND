# 电脑 B：每日穿搭召回与多轮调整

你负责让衣橱里的衣服“能被重新组织成今天能穿的方案”。新方案 v1.0 强调：前端先用白底素材拼搭配卡，再接模拟上身图，不要让展示完全依赖图像生成。

## 1. 你的分支

```bash
git checkout -b codex/outfit-recall
```

## 2. 你要实现的接口

第一优先级：

```txt
POST /api/outfits/recommend
```

第二优先级：

```txt
POST /api/outfits/replace
POST /api/outfits/confirm
```

## 3. 你负责的产品能力

输入包括：

```txt
天气 weather
气温 temperature
场景 occasion：通勤、上课、约会、旅行、拍照
心情/偏好 mood：轻松、精致、低调、显瘦
风格 style：浅色系、松弛感、韩系、正式一点
禁忌 avoid：不要黑色、不要裙子、不穿高跟鞋
指定单品 preferred_item_id
```

输出 2-3 套穿搭，每套包括：

```txt
衣物列表
搭配理由
适合场景
舒适度 / 天气适配说明
替换建议
白底素材搭配卡所需图片 URL
try_on_image_url mock
```

## 4. 推荐文件边界

主要修改：

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
docs/api-contract.md
```

如果电脑 A 还没合并，测试里可以直接创建 SQLite item 数据。

## 5. 实现细节

`POST /api/outfits/recommend`：

1. 接收天气、气温、场景、风格、禁忌、指定单品。
2. 从衣橱读取 item。
3. 先过滤季节、场景、禁忌。
4. 再按品类组合 top / bottom / outerwear / shoes / bag。
5. 生成 2-3 套 outfit。
6. 每套返回 `reason`、`score`、`items`、`replace_suggestions`、`try_on_image_url`。

`POST /api/outfits/replace`：

1. 接收当前搭配 item ids。
2. 锁定不需要替换的 item。
3. 只替换 `replace_category` 对应品类。
4. 支持指令：“换一件外套”“不要黑色”“更正式一点”。

`POST /api/outfits/confirm`：

1. 接收 `item_ids` 和 `feedback`。
2. 记录今天穿了这套。
3. 更新 `usage_count`。
4. 如果反馈多次出现同一偏好，可以写入 mock 长期偏好。

## 6. 推荐算法第一版

不要接复杂模型，先规则化：

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

衣橱不完整时不要崩溃，可以返回部分搭配，并在 reason 里说明缺少鞋/包/外套数据。

## 7. 给这台电脑 Codex 的启动提示词

复制下面这段给电脑 B 的 Codex：

```txt
你现在负责 IF.LAND 项目的每日穿搭召回与多轮调整模块。

请先阅读：
1. docs/codex-collaboration/README.md
2. docs/codex-collaboration/computer-b-outfit.md
3. docs/api-contract.md
4. backend/app/main.py
5. backend/app/models.py

请在分支 codex/outfit-recall 上开发。

目标：
- 实现 POST /api/outfits/recommend
- 尽量实现 POST /api/outfits/replace
- 尽量实现 POST /api/outfits/confirm

要求：
- 使用 FastAPI + Pydantic/SQLModel。
- 用测试驱动开发，新增 backend/tests/test_outfit.py。
- 第一版用规则召回和评分，不接真实 AI。
- 支持天气、气温、场景、风格、禁忌、指定单品。
- 返回 2-3 套 outfit，每套包含 reason、score、items、replace_suggestions、try_on_image_url。
- try_on_image_url 可以先 mock。
- 衣橱数据不足时也要返回可演示结果或清晰错误，不要崩溃。
- 跑通 cd backend && source .venv/bin/activate && python -m pytest。
- 完成后提交并 push 到 codex/outfit-recall。
- 不要提交 PRD、.venv、SQLite db、上传图片。
```

## 8. 验收标准

必须验证：

```txt
衣橱有 top/bottom 时 recommend 返回 outfits 数组
返回 2-3 套或在衣橱不足时给出清晰 fallback
avoid 黑色时，不返回黑色 item
replace_category = outerwear 时，只替换外套
confirm 返回 confirmed = true，并更新 usage_count 或记录反馈
```

测试命令：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```
