# Endpoint Params

## generate_ai_video
- Method: `POST`
- Path: `/cut_jianying/generate_ai_video`
- 用途：调用聚合视频模型生成视频，返回异步任务 `task_id`。

### 请求参数
- `prompt` (string, required): 视频生成提示词。
- `model` (string, required): 模型名，常用 `veo3.1`、`veo3.1-pro`、`seedance-1.5-pro`、`grok-video-3`。
- `resolution` (string, required): 输出分辨率，格式 `宽x高`，如 `1280x720`、`1080x1920`。
- `gen_duration` (number, optional): 生成时长（秒），部分模型支持。
- `generate_audio` (boolean, optional): 是否生成声音，seedance-1.5-pro模型支持，默认 `false`。
- `images` (array<string>, optional): 参考图或首尾帧图。通常第一张为首帧，第二张为尾帧，其余为参考图。

### 模型能力约束
- `veo3.1`/`veo3.1-pro`/`seedance-1.5-pro`/`grok-video-3`：当前主要可用模型。
- `grok-video-3`：按服务端能力灰度支持，建议以实时接口能力为准。
- `gen_duration`、`generate_audio` 与 `images` 的可用性受模型能力约束。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/generate_ai_video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "model": "veo3.1",
  "prompt": "一张超写实的微距照片，照片中，迷你冲浪者在古朴的石制浴室水槽内乘风破浪。",
  "resolution": "1080x1920",
  "generate_audio": true,
  "images": ["https://example.com/frame_start.jpg"]
}'
```

### 关键响应字段
- `status` (string)
- `task_id` (string)

## ai_video_task_status
- Method: `GET`
- Path: `/cut_jianying/aivideo/task_status`
- 用途：查询 AI 视频聚合任务状态，获取进度、草稿与视频结果。

### 请求参数
- Query `task_id` (string, required): `generate_ai_video` 返回的任务 ID。

### 示例请求
```bash
curl --location --request GET 'https://open.vectcut.com/cut_jianying/aivideo/task_status?task_id=AEA270BE7BEE0001160E360AABEFF17D' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json'
```

### 关键响应字段
- `status` (string): `processing` / `completed` / `failed` 等。
- `progress` (number)
- `video_url` (string，完成态可用)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- 响应非 JSON：中止流程并保留原始响应。
- 生成接口缺少 `task_id`：视为任务未创建成功。
- 状态查询接口在完成态缺少 `video_url`：视为结果不可用。
