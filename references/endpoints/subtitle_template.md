# Endpoint Params

## generate_smart_subtitle
- Method: `POST`
- Path: `/cut_jianying/generate_smart_subtitle`
- 用途：在无正确文案输入场景下，基于原始视频或音频 URL 自动识别并添加字幕模版，返回异步任务。

### 请求参数
- `agent_id` (string, required): 字幕模版 ID，必须选用 `references/enums/subtitle_template_typs.json` 中 `id` 以 `asr_` 开头的项。
- `url` (string, required): 视频或音频链接。
- `draft_id` (string, optional): 基于已有草稿继续添加字幕。
- `add_media` (boolean, optional): 是否把原始素材加入草稿。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/generate_smart_subtitle' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "agent_id": "asr_f5f42fbfdd9045409c9b783bfdf4ba14",
  "url": "https://example.com/raw.mp4",
  "add_media": true
}'
```

### 关键响应字段
- 回包以服务端实际返回为准，建议优先提取任务标识候选：
  - `task_id`
  - `id`
  - `output.task_id`
  - `result.task_id`

## sta_subtitle
- Method: `POST`
- Path: `/cut_jianying/sta_subtitle`
- 用途：在有正确文案输入场景下，基于原始视频或音频 URL 生成字幕模版，返回异步任务。

### 请求参数
- `agent_id` (string, required): 字幕模版 ID，必须选用 `references/enums/subtitle_template_typs.json` 中 `id` 以 `sta_` 开头的项。
- `url` (string, required): 视频或音频链接。
- `text` (string, required): 正确文案，用于提高字幕准确率。
- `draft_id` (string, optional): 基于已有草稿继续添加字幕。
- `add_media` (boolean, optional): 是否把原始素材加入草稿。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/sta_subtitle' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "agent_id": "sta_9d550677d16a4c879a19bfeee1623a38",
  "url": "https://example.com/raw.mp4",
  "text": "这是正确文案",
  "add_media": false
}'
```

### 关键响应字段
- 回包以服务端实际返回为准，建议优先提取任务标识候选：
  - `task_id`
  - `id`
  - `output.task_id`
  - `result.task_id`

## smart_subtitle_task_status
- Method: `GET`
- Path: `/cut_jianying/smart_subtitle_task_status`
- 用途：查询字幕模版任务状态，获取草稿与结果链接。

### 请求参数
- Query `task_id` (string, required): `generate_smart_subtitle` 或 `sta_subtitle` 返回的任务 ID。

### 示例请求
```bash
curl --location --request GET 'https://open.vectcut.com/cut_jianying/smart_subtitle_task_status?task_id=TASK_ID' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json'
```

### 关键响应字段
- `task_id` (string)
- `result.output.draft_id` (string)
- `result.output.draft_url` (string)
- `result.output.video_url` (string)
- `result.output.status` 或 `result.status` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- 响应非 JSON：中止流程并保留原始响应。
- 创建接口缺少任务标识：视为任务未创建成功。
- 查询接口在完成态缺少 `draft_id/draft_url`：视为结果不可用。
