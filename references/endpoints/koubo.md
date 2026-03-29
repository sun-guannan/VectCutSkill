# Endpoint Params

## submit_agent_task
- Method: `POST`
- Path: `/cut_jianying/agent/submit_agent_task`
- 用途：提交口播模版任务，返回异步任务 `task_id`。

### 请求参数
- `agent_id` (string, required): 口播模版 ID，需来自 `references/enums/koubo_template_types.json`。
- `params` (object, required): 模版参数对象，不同 `agent_id` 的字段要求不同，必须以 `references/enums/koubo_template_types.json` 中对应模版的 `params_example` 为准。
  - 通用约束：`video_url` 为数组，当前仅支持 1 个 URL。
  - 常见字段：`title`、`text_content`、`cover`、`name`、`kongjing_urls`、`author`。
  - 必填/选填判定：以对应模版 `params_example` 的字段说明为准（包含“必填/选填”提示）。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/agent/submit_agent_task' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "agent_id": "koubo_d47e8a905f1b48798e76123456789abc",
  "params": {
    "video_url": ["https://player.install-ai-guider.top/example/koubo_source.mp4"],
    "title": "流光剪辑标题",
    "cover": ["https://player.install-ai-guider.top/example/mao.webp"],
    "name": "测试草稿"
  }
}'
```

### 关键响应字段
- 回包以服务端实际返回为准，建议至少校验：
  - `task_id`
  - `output.task_id`
  - `id`
  - `output.id`

## agent_task_status
- Method: `GET`
- Path: `/cut_jianying/agent/task_status`
- 用途：查询口播模版任务状态。成功时通常返回草稿信息；若需最终可播放视频，可继续调用 `generate_video` 云渲染。

### 请求参数
- Query `task_id` (string, required): `submit_agent_task` 返回的任务 ID。

### 示例请求
```bash
curl --location --request GET 'https://open.vectcut.com/cut_jianying/agent/task_status?task_id=TASK_ID' \
--header 'Authorization: Bearer <token>'
```

### 关键响应字段
- `status` (string): 常见 `processing` / `success` / `failed`。
- `task_id` (string)
- `output.draft_id` (string)
- `output.draft_url` (string)
- `output.video_url` (string, 可能为空)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- 响应非 JSON：中止流程并保留原始响应。
- 创建接口缺少任务标识：视为任务未创建成功。
- 状态查询 `status=failed`：视为任务失败并停止轮询。
