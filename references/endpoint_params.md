# Endpoint Params

本文件作为总索引，不再承载完整端点细节。

## 按能力域拆分
- `endpoints/filter.md`：滤镜相关端点（add_filter/modify_filter/remove_filter）
- `endpoints/effect.md`：特效相关端点（add_effect/modify_effect/remove_effect）
- `endpoints/material.md`：素材感知端点（get_duration/get_resolution/video_detail）
- `endpoints/draft.md`：草稿管理端点（create_draft/modify_draft/remove_draft/query_script）
- `endpoints/asr.md`：语音识别端点（asr_basic/asr_nlp/asr_llm）
- `endpoints/generate_video.md`：云渲染端点（generate_video/task_status）

## 枚举文件
- `enums/filter_types.json`：`filter_type` 可选值
- `enums/character_effect_types.json`：`effect_category` 为 `character` 时的 `effect_type` 可选值
- `enums/scene_effect_types.json`：`effect_category` 为 `scene` 时的 `effect_type` 可选值

## Query Script 输出解析
- `query_script` 的 `output` 为草稿结构体解析入口。
- 结构解读文档：`draft_query_notes.md`（建议与 `endpoints/draft.md` 配套阅读）。
- 样例数据：`draft_info.json`（用于字段对照与校验规则落地）。

## ASR 输出解析
- `asr_basic`：重点解析 `result.raw.result.utterances`，结构说明见 `asr_basic_notes.md`。
- `asr_nlp`：重点解析 `segments`（含 `phrase/words`），结构说明见 `asr_nlp_notes.md`。
- `asr_llm`：重点解析 `segments`（含 `keywords/en/words`），结构说明见 `asr_llm_notes.md`。

## 维护规则
- 新端点优先写入对应能力域文件。
- 涉及复杂返回结构的端点，需在 `references/` 增加专用解读文档并在本文件登记入口。
- 本文件仅维护目录结构与跳转入口。
