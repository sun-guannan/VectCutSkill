# generate_ai_video 端点规则（generate_ai_video/ai_video_task_status）

## 适用范围
- `POST /llm/generate_ai_video`
- `GET /cut_jianying/aivideo/task_status`

## 请求路由与参数策略
- 生成任务必填：`prompt`、`resolution`。
- `model` 可选，默认 `veo3.1`；可选值：`veo3.1`、`veo3.1-pro`、`seedance-1.5-pro`、`grok-video-3`。
- 轮询任务必填：`task_id`。
- 图生视频与首尾帧模式统一使用 `images`（array<string>）传图，按顺序表达首帧、尾帧与参考图。
- `gen_duration` 为可选 number，仅在支持模型下传入。
- `generate_audio` 为可选 boolean，仅在seedance-1.5-pro模型下传入。

## 专属异常处理
- 当 HTTP 状态码非 2xx：
  - 含义：鉴权失败、参数非法或服务端异常。
  - 处理：记录状态码与响应体；若为鉴权问题先检查 `VECTCUT_API_KEY`，再重试 1 次。
  - 重试上限：1 次。

- 当响应体不是合法 JSON：
  - 含义：网关异常或服务返回格式不符合约定。
  - 处理：保留原始响应体并中止，不做盲目重试。
  - 重试上限：0 次。

- 当任务创建响应缺少 `task_id`：
  - 含义：任务未成功创建。
  - 处理：标记失败并回收上下文，修正参数后可重试 1 次。
  - 重试上限：1 次。

- 当状态查询进入 `failed` / `failure`：
  - 含义：模型生成失败。
  - 处理：输出失败状态与 `draft_error`，停止轮询。
  - 重试上限：0 次。

- 当状态查询 `completed` 但缺少 `video_url`：
  - 含义：结果不完整不可用。
  - 处理：标记失败并保留原始响应。
  - 重试上限：0 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `task_id`
- `prompt`
- `model`
- `resolution`
- `images`
- `gen_duration`
- `generate_audio`
