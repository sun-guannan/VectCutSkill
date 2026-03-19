# Endpoint Params

## generate_speech
- Method: `POST`
- Path: `/cut_jianying/generate_speech`
- 用途：将文案合成为语音并写入草稿，返回音频地址与草稿信息。

### 请求参数
- `text` (string, required): 待合成文本。
- `provider` (string, required): 供应商枚举：`azure` / `volc` / `minimax` / `fish`。
- `voice_id` (string, required): 音色 ID。
- `model` (string, optional): 当前仅 `provider=minimax` 生效，可选 `speech-2.6-turbo` / `speech-2.6-hd`。
- `volume` (number, optional): 音量强度。
- `target_start` (number, optional): 目标入轨时间。
- `effect_type` (string, optional): 音效类型，例如 `麦霸`。
- `effect_params` (array<number>, optional): 音效参数数组。
- `start`: (number, optional): 生成音频后，添加到轨道时截取生成音频的开始时间，一般不填。
- `end`: (number, optional): 生成音频后，添加到轨道时截取生成音频的结束时间，一般不填。
- `draft_id`: (string, optional): 草稿id, 基于某个草稿继续添加。
- `speed`: (number, optional): 倍速，>1表示加速。
- `track_name`: (string, optional): 目标轨道名称。
- `fade_in_duration`: (number, optional): 音频淡入时间，单位秒，支持小数。
- `fade_out_duration`: (number, optional): 音频淡出时间，单位秒，支持小数。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/generate_speech' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "text":"今天的视频，就给大家带来一个福利。",
  "provider":"minimax",
  "model":"speech-2.6-turbo",
  "voice_id":"audiobook_male_1",
  "volume":10,
  "target_start":3,
  "effect_type":"麦霸",
  "effect_params":[45,80]
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.audio_url` (string，可独立复用)
- `output.draft_id` (string)
- `output.draft_url` (string)
- `output.material_id` (string，表示已成功插入草稿)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY`。
- `success=false` 或 `error` 非空：业务失败，修正参数后重试。
- 响应非 JSON：中止流程并保留原始响应。
- 缺少 `output.audio_url`：视为语音结果不可用。
- 需要确认入稿时，若缺少 `output.material_id`：视为未确认插入草稿成功。

### 枚举引用
- `references/enums/minimax_voiceids.json`
- `references/enums/azure_voiceids.json`
- `references/enums/volc_voiceids.json`
- `references/enums/fish_voiceids.json`