# Endpoint Params

本文件作为总索引，不再承载完整端点细节。

## 按能力域拆分
- `endpoints/filter.md`：滤镜相关端点（add_filter/modify_filter/remove_filter）
- `endpoints/effect.md`：特效相关端点（add_effect/modify_effect/remove_effect）

## 枚举文件
- `enums/filter_types.json`：`filter_type` 可选值
- `enums/character_effect_types.json`：`effect_category` 为 `character` 时的 `effect_type` 可选值
- `enums/scene_effect_types.json`：`effect_category` 为 `scene` 时的 `effect_type` 可选值

## 维护规则
- 新端点优先写入对应能力域文件。
- 本文件仅维护目录结构与跳转入口。
