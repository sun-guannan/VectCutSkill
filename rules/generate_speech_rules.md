# 语音合成规则（tts_generate）

## 适用范围
- `POST /llm/tts/generate`
- `POST /llm/tts/fish/clone_voice`
- `GET /llm/tts/voice_assets`

## 调用策略
- 用于 AI 配音与素材补全，优先在“素材不足”或“需要旁白”场景触发。
- 标准流程（合成）：准备文本与音色参数 -> 调用 `tts_generate` -> 校验 `url/provider` -> 按需继续 `add_audio` 入轨与渲染。
- 标准流程（克隆）：准备 `file_url/title` -> 调用 `fish_clone` -> 校验 `voice_id` -> 回填到后续 `tts_generate`。
- 标准流程（资产）：按需传 `provider/limit/offset` -> 调用 `voice_assets` -> 读取历史克隆音色资产。
- 入轨策略：`tts_generate` 返回 `url` 后，如需入轨需显式调用 `add_audio`。

## 入参约束
- 必填：`provider`、`text`、`voice_id`、`model`。
- `provider` 枚举：`azure`、`volc`、`minimax`、`fish`。
- `model` 当前仅 `provider=minimax` 生效，可选：`speech-2.6-turbo`、`speech-2.6-hd`。
- `text` 必须为非空字符串；建议控制单次文本长度，超长文案应先分段再调用。
- fish_clone 入参：
    - `file_url` (string, required): 安静人声录音链接，建议情感饱满，时长 10~30 秒。
    - `title` (string, optional): 音色命名。
- voice_assets 入参：
    - `limit` (integer, optional): 一次请求总数。
    - `offset` (integer, optional): 偏移量。
    - `provider` (string, optional): 可选值`fish` 或 `minimax`， 默认为空，表示全部查询。

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
- 当缺少 `url`：
  - 含义：语音结果不可独立复用。
  - 处理：中止并保留原始响应。
  - 重试上限：1 次。
- 当缺少 `provider`：
  - 含义：响应关键字段不完整。
  - 处理：中止并保留原始响应。
  - 重试上限：1 次。
- 当 `fish_clone` 缺少 `voice_id`：
  - 含义：克隆结果不可用于后续合成。
  - 处理：中止并保留原始响应。
  - 重试上限：1 次。
- 当 `voice_assets` 响应非 JSON：
  - 含义：资产列表不可解析。
  - 处理：中止并保留原始响应。
  - 重试上限：1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `text`
- `provider`
- `model`
- `voice_id`
- `error`
- `raw_response`
