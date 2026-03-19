# 语音合成规则（generate_speech）

## 适用范围
- `POST /cut_jianying/generate_speech`

## 调用策略
- 用于 AI 配音与素材补全，优先在“素材不足”或“需要旁白”场景触发。
- 标准流程：准备文本与音色参数 -> 调用 `generate_speech` -> 校验 `audio_url/material_id` 与草稿字段 -> 按需继续 `query_script` 或渲染。
- 入轨策略：有时间编排需求时传 `target_start`；无需精确编排时可省略。

## 入参约束
- 必填：`text`、`provider`、`voice_id`。
- `provider` 枚举：`azure`、`volc`、`minimax`、`fish`。
- `model` 当前仅 `provider=minimax` 生效，可选：`speech-2.6-turbo`、`speech-2.6-hd`。
- `text` 必须为非空字符串；建议控制单次文本长度，超长文案应先分段再调用。
- `effect_params` 仅在传入 `effect_type` 时透传，避免无效参数。
- 可选：
    - `volume` (number, optional): 音量强度。
    - `target_start` (number, optional): 目标入轨时间。
    - `effect_type` (string, optional): 音效类型，例如 `麦霸`。
    - `effect_params` (array<number>, optional): 仅在传入 `effect_type` 时透传，避免无效参数。
    - `start`: (number, optional): 生成音频后，添加到轨道时截取生成音频的开始时间，一般不填。
    - `end`: (number, optional): 生成音频后，添加到轨道时截取生成音频的结束时间，一般不填。
    - `draft_id`: (string, optional): 草稿id, 基于某个草稿继续添加。
    - `speed`: (number, optional): 倍速，>1表示加速。
    - `track_name`: (string, optional): 目标轨道名称。
    - `fade_in_duration`: (number, optional): 音频淡入时间，单位秒，支持小数。
    - `fade_out_duration`: (number, optional): 音频淡出时间，单位秒，支持小数。

## 专属异常处理
- 当 HTTP 非 2xx：
  - 含义：鉴权或服务异常。
  - 处理：检查 `VECTCUT_API_KEY` 与请求体后重试 1 次。
  - 重试上限：1 次。
- 当响应非 JSON：
  - 含义：网关或服务返回异常。
  - 处理：保留原始响应并中止。
  - 重试上限：0 次。
- 当 `success=false` 或 `error` 非空：
  - 含义：业务失败（参数、音色模型或服务侧异常）。
  - 处理：修正参数后重试 1 次。
  - 重试上限：1 次。
- 当缺少 `output.audio_url`：
  - 含义：语音结果不可独立复用。
  - 处理：中止并保留原始响应。
  - 重试上限：1 次。
- 当需要确认“插入草稿成功”且缺少 `output.material_id`：
  - 含义：无法确认入稿成功。
  - 处理：中止并保留原始响应。
  - 重试上限：1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `text`
- `provider`
- `model`
- `voice_id`
- `target_start`
- `error`
- `raw_response`