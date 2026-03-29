# koubo 端点规则（submit_agent_task/agent_task_status）

## 适用范围
- `POST /cut_jianying/agent/submit_agent_task`
- `GET /cut_jianying/agent/task_status`

## 请求路由与参数策略
- 口播模版用于固定范围的口播剪辑任务，目标是快速产出结构化草稿，后续仍可继续编辑。
- 常规流程：`submit_agent_task -> agent_task_status(轮询)`。
- 提交任务必填：
  - `agent_id`
  - `params`（对象）
- `params` 字段要求按模版 ID 决定，必须对照 `references/enums/koubo_template_types.json` 中对应项的 `params_example`：
  - `params.video_url` 仍需满足数组且仅 1 个 URL。
  - 其余字段（如 `title`、`text_content`、`cover`、`name`、`kongjing_urls`、`author`）是否必填，以对应模版说明为准。
- `agent_id` 必须来自 `references/enums/koubo_template_types.json` 的 `items.id`。
- 任务成功后通常返回草稿信息（`draft_id/draft_url`）。若需可播放成片，应继续执行 `generate_video -> task_status`。
- 当用户需要“先看视频是否达标”时，可在拿到草稿后触发中间云渲染，若不符合预期再基于草稿继续改。

## 专属异常处理
- 当 HTTP 状态码非 2xx：
  - 含义：鉴权失败、参数非法或服务端异常。
  - 处理：记录状态码与响应体；若为鉴权问题先检查 `VECTCUT_API_KEY`，再重试 1 次。
  - 重试上限：1 次。

- 当响应体不是合法 JSON：
  - 含义：网关异常或服务返回格式不符合约定。
  - 处理：保留原始响应体并中止，不做盲目重试。
  - 重试上限：0 次。

- 当创建任务响应缺少任务标识：
  - 判定：`task_id` / `id` / `output.task_id` / `output.id` 均缺失。
  - 含义：任务未成功创建，无法进入轮询。
  - 处理：标记失败并保留原始响应。
  - 重试上限：1 次。

- 当状态查询进入失败态：
  - 判定：`status` 为 `failed` / `failure` / `error`。
  - 处理：输出失败状态并停止轮询。
  - 重试上限：0 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `task_id`
- `agent_id`
- `video_url`
- `title`
- `text_content`
