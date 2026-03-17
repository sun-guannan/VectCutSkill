# References Index

## Endpoint Docs
- `endpoint_params.md`：端点总索引
- `endpoints/filter.md`：滤镜端点明细
- `endpoints/effect.md`：特效端点明细
- `endpoints/material.md`：素材感知端点明细（get_duration/get_resolution/video_detail）
- `endpoints/draft.md`：草稿管理端点明细（create_draft/modify_draft/remove_draft/query_script）

## Enums
- `enums/filter_types.json`：滤镜枚举
- `enums/character_effect_types.json`：人物特效枚举
- `enums/scene_effect_types.json`：场景特效枚举

## Draft Query 解析
- `draft_query_notes.md`：`query_script` 返回 `output` 的结构解读（总体配置、materials、ID 关联、轨道、关键帧）
- `draft_info.json`：真实样例草稿结构（用于对照字段）

## 约定
- 明细写在 `endpoints/`，总览写在 `endpoint_params.md`。
- 枚举统一放在 `enums/`，端点文档只做引用。