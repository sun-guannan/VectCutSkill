# Endpoint Params

## tts_generate
- Method: `POST`
- Path: `/llm/tts/generate`
- 用途：将文案合成为语音，返回可复用音频地址。

### 请求参数
- `provider` (string, required): 供应商枚举：`azure` / `volc` / `minimax` / `fish`。
- `text` (string, required): 待合成文本。
- `voice_id` (string, required): 音色 ID。
- `model` (string, optional): 当前仅 `provider=minimax` 生效，可选 `speech-2.6-turbo` / `speech-2.6-hd`。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/llm/tts/generate' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "provider":"azure",
  "text":"今天的视频，就给大家带来一个福利。",
  "voice_id":"audiobook_male_1",
  "model":"speech-2.6-turbo"
}'
```

### 关键响应字段
- `success` (boolean)
- `provider` (string)
- `url` (string，可独立复用)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY`。
- `success=false` 或 `error` 非空：业务失败，修正参数后重试。
- 响应非 JSON：中止流程并保留原始响应。
- 缺少 `url`：视为语音结果不可用。
- 缺少 `provider`：视为响应字段不完整。

### 枚举引用
- `references/enums/minimax_voiceids.json`
- `references/enums/azure_voiceids.json`
- `references/enums/volc_voiceids.json`
- `references/enums/fish_voiceids.json`

## fish_clone
- Method: `POST`
- Path: `/llm/tts/fish/clone_voice`
- 用途：克隆用户音色并返回可用于 `tts_generate` 的 `voice_id`。

### 请求参数
- `file_url` (string, required): 音频文件链接，需满足：安静人声录音、情感饱满、时长 10~30 秒。
- `title` (string, optional): 音色命名，便于后续检索。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/llm/tts/fish/clone_voice' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "file_url":"https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/dfd_707531.mp3",
  "title":"我的克隆音色"
}'
```

### 关键响应字段
- `success` (boolean)
- `voice_id` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `success=false`：克隆失败，先检查音频质量与时长。
- 缺少 `voice_id`：视为不可用结果。

## voice_assets
- Method: `GET`
- Path: `/llm/tts/voice_assets`
- 用途：查看已克隆的音色资产列表。

### 请求参数
- `limit` (integer, optional): 一次请求总数，示例 `20`。
- `offset` (integer, optional): 偏移量，示例 `0`。
- `provider` (string, optional): 克隆模型，`fish` 或 `minimax`；为空时查询全部。

### 示例请求
```bash
curl --location --request GET 'https://open.vectcut.com/llm/tts/voice_assets?limit=20&offset=0&provider=fish' \
--header 'Authorization: Bearer <token>'
```

### 关键响应字段
- 响应体字段以服务端实际返回为准，至少要求响应为合法 JSON。

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- 响应非 JSON：中止流程并保留原始响应。
