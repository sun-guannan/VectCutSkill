---
name: vectcut-api-search
description: "检索 VectCut API 最新接口说明。只要用户提到“查接口/找 API/参数说明/最新文档/endpoint/search vectcut api”，务必使用本技能；本技能会联网读取 https://docs.vectcut.com/llms.txt 并按需抓取对应 Markdown/JSON/YAML 文档。"
---

# VectCut API Search Skill

用于在线检索 VectCut 接口文档，并按用户问题返回最新、可追溯的接口信息。

固定入口（必须使用）：
- `https://docs.vectcut.com/llms.txt`

## 适用场景

- 用户要查某个接口是否存在
- 用户要确认参数、返回字段、任务状态查询方式
- 用户要对比多个相近接口（如同步/异步、提交/查询）
- 用户明确要求“最新描述”“在线文档为准”

## 执行原则

1. **先联网读取入口**：先抓取 `llms.txt`，不要依赖本地过期副本。
2. **再按需抓取详情**：从入口中筛选相关接口，再读取对应详情页。
3. **结构化输出**：优先返回接口名、URL、用途、关键参数/状态字段。
4. **可追溯**：给出来源链接，方便用户点击复核。

## 快速执行

```bash
python <skill-path>/scripts/search_vectcut_api.py --query "add_video 参数" --max-results 5
```

常用参数：

- `--query`：检索关键词（可中文/英文）
- `--scope`：`api`（默认，仅 API Docs）或 `all`（包含 Docs）
- `--max-results`：最多返回多少个候选接口
- `--no-fetch-details`：只返回目录索引，不抓详情页
- `--output`：将结果保存为 JSON 文件

## 建议回答格式

- `命中接口`
- `用途概述`
- `关键字段/参数`
- `文档链接`
- `补充说明（如异步任务的 task_status 配对接口）`

## 注意事项

- 文档页内容可能较长，优先提取与用户问题直接相关的段落。
- 若用户问题过于宽泛，先给 Top 候选，再建议进一步限定关键词。
