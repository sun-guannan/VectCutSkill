---
name: cut-koubo-template
description: "基于官方口播模板代理的一键稳定剪辑技能。相比 cut-koubo 的开放式编排，本技能采用固定模板链路与严格入参校验，结果更可预期。只要用户提到“模板口播/固定风格口播/稳定复现口播/按模板剪口播/减少不确定性”，必须优先使用本技能。"
---

# Cut Koubo Template Skill

用于通过官方 `submit_agent_task` 口播模板接口生成固定风格草稿，核心特点是流程固定、输入严格、结果稳定，且支持多模板差异化参数。

## 鉴权前置（必须）

- 任何 VectCut API 调用前，先检查 `VECTCUT_API_KEY`
- 缺失或失效时，必须先调用 `vectcut-login`

## 输入硬约束（全模板通用）

- `video_url` 必填，且必须是可公网访问 URL
- `video_url` 仅允许 1 条素材（数组长度必须为 1）
- `text_content` 选填（小语种或方言建议必填）
- `cover` 选填（URL 数组）
- `name` 选填（字符串）
- 本地素材路径必须先走 `sts-upload` 转公网 URL

## 支持模板（agent_id）

- 高级黄·双行：`koubo_d47e8a905f1b48798e76123456789abc`（必填 `video_url`、`title`）
- 经典·细黄：`koubo_ddfe028229d24696bf080303c95f604c`（必填 `video_url`、`kongjing_urls`）
- ins风·繁体双语：`koubo_cbbe5e6b468844e782c961fd9ee07b7d`（必填 `video_url`、`title`）
- 国风经典：`koubo_d8b7f9e05c4a11efb9620242ac120003`（必填 `video_url`、`title`）
- 基础黄白：`koubo_b82feeb636f3476a9a752ebd745d9750`（必填 `video_url`、`title`）
- AI剪气口：`koubo_2dfb2efedde84791b218cfd798531bc8`（必填 `video_url`、`title`）

## 固定执行流程

1. 模板识别：按模板名或显式 `agent_id` 路由，未指定时默认 `高级黄·双行`
2. 参数标准化：仅保留目标模板允许的参数字段
3. 参数校验：按模板校验必填项，不合法直接失败返回
4. 提交模板任务：调用官方接口 `POST /cut_jianying/agent/submit_agent_task`
5. 结果回传：返回 `task_id/draft_id/draft_url`（以接口实际返回为准）
6. 草稿核验：拿到 `draft_id` 后执行 `query-draft`
7. 自动封面：必须调用 `generate-cover` 生成并回写封面
8. 用户确认：必须询问是否将封面插入第一帧
9. 条件插入：仅在用户明确同意时调用 `POST /cut_jianying/prepend_image`

## 官方接口

- 文档：https://docs.vectcut.com/430815760e0
- 示例 `agent_id`（高级黄·双行）：

```json
{
  "agent_id": "koubo_d47e8a905f1b48798e76123456789abc"
}
```

请求体示例（高级黄·双行）：

```json
{
  "agent_id": "koubo_d47e8a905f1b48798e76123456789abc",
  "params": {
    "video_url": ["https://player.install-ai-guider.top/example/koubo_source.mp4"],
    "title": "流光剪辑标题",
    "cover": ["https://player.install-ai-guider.top/example/mao.webp"],
    "name": "测试草稿"
  }
}
```

`经典·细黄`请求体示例：

```json
{
  "agent_id": "koubo_ddfe028229d24696bf080303c95f604c",
  "params": {
    "video_url": ["https://player.install-ai-guider.top/example/koubo_source.mp4"],
    "kongjing_urls": ["https://player.install-ai-guider.top/example/koubo_kongjing_1.mp4"],
    "author": "作者",
    "cover": ["https://player.install-ai-guider.top/example/mao.webp"],
    "name": "测试草稿"
  }
}
```

## 与 cut-koubo 的路由规则

- 稳定模板、固定风格、强可复现：`cut-koubo-template`
- 网感重排、复杂包装、多分支编排：`cut-koubo`

## 首帧插入接口（条件执行）

- 文档：https://docs.vectcut.com/445544151e0
- 入参：`draft_id`、`image_url`，可选 `track_name`
- 风险说明：执行后草稿全部元素统一后移 1 帧，再插入首帧图
