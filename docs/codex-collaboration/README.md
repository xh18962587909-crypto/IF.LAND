# 三台 Codex 协同开发总览

目标：三台电脑上的 Codex 同时开发《衣见》后端 MVP。本文已根据本地补充文档 `“衣见”方案v1.0.docx` 更新。

GitHub 仓库：

```txt
https://github.com/xh18962587909-crypto/IF.LAND
```

## 1. 产品共识

《衣见》不是普通电子衣橱，而是围绕“今天穿什么”和“这件值不值得买”的个人衣橱 Agent。

MVP 要证明一个闭环：

```txt
用户低成本上传图片
-> 系统识别 1-3 件主要衣物
-> 标准化成可管理的衣橱资产
-> 每日穿搭可以召回这些资产
-> 买前决策可以判断重复、缺口和可搭配性
-> 必要时给出白底素材 / 模拟上身图 mock
```

核心工程取舍：

```txt
不要追求一次性完美识别整个衣柜。
先证明衣物可以标准化入库、被召回、被推荐、被用于买前判断。
模拟上身阶段定位为“穿搭氛围预览”，不要承诺高精度虚拟试衣。
```

## 2. 当前项目状态

已完成：

```txt
FastAPI 后端基础骨架
CORS 配置
SQLite 初始化
/health
/ready
/uploads 静态文件访问
API 接口文档
三台 Codex 协作文档
```

第一批接口目标：

```txt
POST /api/wardrobe/items/detect
POST /api/wardrobe/items/batch-confirm
GET  /api/wardrobe/items
POST /api/outfits/recommend
POST /api/purchase/analyze
```

## 3. 三台电脑新版分工

| 电脑 | 方向 | 分支 | 文档 |
| --- | --- | --- | --- |
| 电脑 A | 衣橱资产标准化与入库 | `codex/wardrobe-standardization` | `docs/codex-collaboration/computer-a-wardrobe.md` |
| 电脑 B | 每日穿搭召回与多轮调整 | `codex/outfit-recall` | `docs/codex-collaboration/computer-b-outfit.md` |
| 电脑 C | 买前决策、AI mock 与视觉生成兜底 | `codex/purchase-vision` | `docs/codex-collaboration/computer-c-purchase-ai.md` |

推荐当前这台已经初始化项目的电脑优先负责电脑 A 或最终集成；另外两台电脑分别负责 B/C。

## 4. 怎么把任务交给另外两台 Codex

给每台电脑的 Codex 只需要发对应文档里的“启动提示词”。

每份个人文档都按同一套结构写：

```txt
你负责什么
你的分支
必须实现的接口
必须修改/新增的文件
硬性要求
允许 mock 的内容
最终验收效果
测试方案
手动联调 curl
启动提示词
```

如果那台电脑的 Codex 问“我要做什么”，让它重新阅读自己的文档，不要让它自由发挥。

每台电脑最终必须交付：

```txt
一个独立分支
对应模块的 router
对应模块的 service
对应模块的 pytest 测试文件
所有测试通过
一段交接说明
```

每台电脑不能只说“代码写完了”，必须说清楚：

```txt
哪些接口已经实现
哪些 mock 了
跑了哪些测试
测试结果是什么
哪些地方需要别的电脑配合
```

## 5. 每台电脑开始前都要做

```bash
git clone https://github.com/xh18962587909-crypto/IF.LAND.git
cd IF.LAND
python3 -m venv backend/.venv
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

如果测试通过，再按自己负责方向创建分支：

```bash
git checkout -b codex/wardrobe-standardization
git checkout -b codex/outfit-recall
git checkout -b codex/purchase-vision
```

每台电脑只执行自己的那一条。

## 6. 共享数据结构原则

每件衣服必须以数据库 `item_id` 为主键，不要用图片路径当唯一身份。

衣物最小字段：

```txt
id
name
category
color
season
style
occasion
material
fit
description
source_type
image_url
cutout_image_url
image_embedding/mock_embedding
text_embedding/mock_embedding
usage_count
created_at
```

MVP 可以把 embedding 存成 JSON 数组或字符串占位；重点是保留字段和服务边界，方便后续替换真实模型。

## 7. 共同规则

1. 以 `docs/api-contract.md` 为接口真相；如果新方案要求补字段，先更新接口文档再写代码。
2. 每台电脑只改自己模块的 router/service/test 文件。
3. 共享文件 `backend/app/models.py`、`backend/app/schemas.py`、`backend/app/services/vision_service.py` 容易冲突，改之前在群里说。
4. 每个模块都要写测试，必须按照个人文档里的“测试方案”逐项覆盖。
5. AI、白底图、embedding、模拟上身第一版都允许 mock，不要因为真实模型卡住接口开发。
6. 不要提交本地 PRD、`.venv`、SQLite db、上传图片。
7. 完成后 push 到自己的分支，不要直接覆盖别人的分支。

## 8. 推荐后端结构

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
    embedding_service.py
    try_on_service.py
```

服务职责：

```txt
vision_service.py: 图片理解、标签抽取、白底图 mock
embedding_service.py: image/text embedding mock
try_on_service.py: 模拟上身图 mock / prompt 构建
wardrobe_service.py: 入库、查询、去重、低利用率
outfit_service.py: 衣橱召回、搭配组合、替换
purchase_service.py: 商品临时衣物、重复分析、购买分数
```

## 9. 合并建议

推荐合并顺序：

```txt
1. 电脑 A：衣橱资产标准化
2. 电脑 C：AI mock / 买前决策 / 视觉兜底
3. 电脑 B：每日穿搭召回
```

原因：B/C 都依赖衣橱 item 数据；C 的 `vision_service` 和 `try_on_service` 也会被 A/B 调用。

## 10. 每台电脑完成后的交接格式

```txt
我负责的模块：
分支名：
完成的接口：
新增/修改的文件：
测试命令和结果：
mock 了哪些 AI/图像能力：
需要别人配合的地方：
```
