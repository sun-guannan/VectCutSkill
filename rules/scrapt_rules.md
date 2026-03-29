# scrapt 端点规则（parse_xiaohongshu/parse_douyin/parse_kuaishou/parse_bilibili/parse_tiktok/parse_youtube）

## 适用范围
- `POST /scrapt/parse_xiaohongshu`
- `POST /scrapt/parse_douyin`
- `POST /scrapt/parse_kuaishou`
- `POST /scrapt/parse_bilibili`
- `POST /scrapt/parse_tiktok`
- `POST /scrapt/parse_youtube`

## 请求路由与参数策略
- 当用户给出平台明确的分享链接时，优先路由到对应平台端点。
- 当用户仅给出混合文本时，先通过域名判断平台再路由：
  - `xiaohongshu.com` -> `parse_xiaohongshu`
  - `douyin.com` -> `parse_douyin`
  - `kuaishou.com` -> `parse_kuaishou`
  - `bilibili.com` / `b23.tv` -> `parse_bilibili`
  - `tiktok.com` -> `parse_tiktok`
  - `youtube.com` / `youtu.be` -> `parse_youtube`
- 六个动作统一只需 `url` 入参。
- 成功后优先抽取并返回：
  - `data.video.url`
  - `data.title` / `data.desc`
  - `data.author`
  - `data.stats`
- 输出的视频直链可直接用于后续 `add_video`、`video_detail`、`asr_*`、`generate_smart_subtitle`、`query_script` 分析链路。

## 专属异常处理
- 当 HTTP 状态码非 2xx：
  - 含义：鉴权失败、参数非法或服务端异常。
  - 处理：记录状态码与响应体；若为鉴权问题先检查 `VECTCUT_API_KEY`，再重试 1 次。
  - 重试上限：1 次。

- 当响应体不是合法 JSON：
  - 含义：网关异常或服务返回格式不符合约定。
  - 处理：保留原始响应体并中止，不做盲目重试。
  - 重试上限：0 次。

- 当业务标识失败：
  - 判定：`success=false` 或 `error` 非空。
  - 处理：输出失败状态并停止。
  - 重试上限：0 次。

- 当关键字段缺失：
  - 判定：缺少 `data.platform` 或缺少 `data.original_url` 或缺少 `data.video.url`。
  - 处理：标记失败并保留原始响应。
  - 重试上限：0 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `url`
- `platform_guess`
