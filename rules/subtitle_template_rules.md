# subtitle_template 端点规则（generate_smart_subtitle/sta_subtitle/smart_subtitle_task_status）

## 适用范围
- `POST /cut_jianying/generate_smart_subtitle`
- `POST /cut_jianying/sta_subtitle`
- `GET /cut_jianying/smart_subtitle_task_status`

## 请求路由与参数策略
- 当没有可用正确文案时，优先使用 `generate_smart_subtitle`，仅依赖 ASR 自动识别。
- 当已有正确文案时，优先使用 `sta_subtitle`，通过 `text` 提升字幕准确率与断句质量。
- 两种创建方式均为异步任务，创建后必须通过 `smart_subtitle_task_status` 轮询直到完成态。
- 两种创建方式都支持 `add_media`，用于控制是否把原始输入素材追加到草稿。
- 常见编排顺序：
  - 裸素材加字幕：直接以素材 URL 发起字幕模版任务。
  - 多素材拼接后加字幕：先执行 `generate_video -> task_status` 产出中间视频 URL，再以该 URL 发起字幕模版任务。
- 创建任务必填：
  - `generate_smart_subtitle`：`agent_id`、`url`
  - `sta_subtitle`：`agent_id`、`url`、`text`
- `agent_id` 选择约束（来自 `references/enums/subtitle_template_typs.json`）：
  - `generate_smart_subtitle` 必须使用 `asr_` 前缀模版 ID。
  - `sta_subtitle` 必须使用 `sta_` 前缀模版 ID。
- 查询任务必填：`task_id`

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
  - 判定：`task_id` / `id` / `output.task_id` / `result.task_id` 均缺失。
  - 含义：任务未成功创建，无法进入轮询。
  - 处理：标记失败并保留原始响应。
  - 重试上限：1 次。

- 当状态查询进入失败态：
  - 判定：`status` 为 `failed` / `failure` / `error`。
  - 处理：输出失败状态并停止轮询。
  - 重试上限：0 次。

- 当状态查询完成但关键结果缺失：
  - 判定：完成态缺少 `output.draft_id` 且缺少 `output.draft_url`。
  - 处理：标记失败并保留原始响应。
  - 重试上限：0 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `task_id`
- `agent_id`
- `url`
- `text`
- `draft_id`
- `add_media`
