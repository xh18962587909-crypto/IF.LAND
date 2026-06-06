# 三台 Codex 协同开发总览

目标：三台电脑上的 Codex 同时开发《衣见》后端 MVP，围绕 `docs/api-contract.md` 完成第一批接口。

GitHub 仓库：

```txt
https://github.com/xh18962587909-crypto/IF.LAND
```

## 当前项目状态

已完成：

```txt
FastAPI 后端基础骨架
CORS 配置
SQLite 初始化
/health
/ready
/uploads 静态文件访问
API 接口文档
```

第一批要实现：

```txt
POST /api/wardrobe/items/detect
POST /api/wardrobe/items/batch-confirm
GET  /api/wardrobe/items
POST /api/outfits/recommend
POST /api/purchase/analyze
```

## 三台电脑分工

| 电脑 | 负责人方向 | 分支 | 文档 |
| --- | --- | --- | --- |
| 电脑 A | 衣橱模块 | `codex/wardrobe-api` | `docs/codex-collaboration/computer-a-wardrobe.md` |
| 电脑 B | 今日穿搭模块 | `codex/outfit-api` | `docs/codex-collaboration/computer-b-outfit.md` |
| 电脑 C | 买前决策 + AI mock | `codex/purchase-ai` | `docs/codex-collaboration/computer-c-purchase-ai.md` |

## 每台电脑开始前都要做

```bash
git clone https://github.com/xh18962587909-crypto/IF.LAND.git
cd IF.LAND
python3 -m venv backend/.venv
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

如果测试通过，再创建自己的分支。根据自己负责的电脑选择一个：

```bash
git checkout -b codex/wardrobe-api
git checkout -b codex/outfit-api
git checkout -b codex/purchase-ai
```

## 共同规则

1. 以 `docs/api-contract.md` 为接口真相，不要随便改接口字段。
2. 每台电脑只改自己模块的 router/service/test 文件。
3. 如果必须改 `backend/app/models.py` 或新增共享 schema，先在群里说。
4. 每个模块都要写测试，至少覆盖成功返回和一个基础错误/空数据场景。
5. AI 第一版全部允许 mock，不要因为真实模型卡住接口开发。
6. 不要提交本地 PRD、`.venv`、SQLite db、上传图片。
7. 完成后 push 到自己的分支，不要直接覆盖别人的分支。

## 推荐后端结构

```txt
backend/app/
  main.py
  db.py
  models.py
  schemas.py
  routers/
    wardrobe.py
    outfit.py
    purchase.py
  services/
    wardrobe_service.py
    outfit_service.py
    purchase_service.py
    vision_service.py
```

当前仓库还没有 `schemas.py`。第一位需要 schema 的 Codex 可以创建它，但要尽量放通用响应模型，不要塞业务逻辑。

## 交接格式

每台电脑完成后，在聊天里发：

```txt
我负责的模块：
完成的接口：
新增/修改的文件：
测试命令和结果：
分支名：
还需要别人配合的地方：
```

## 合并建议

推荐合并顺序：

```txt
电脑 A 衣橱模块
电脑 C AI mock / 买前决策
电脑 B 今日穿搭模块
```

原因：穿搭和买前决策都需要衣橱数据；先合衣橱，后面两个模块更容易接真实数据库。
