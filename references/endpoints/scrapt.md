# Endpoint Params

## parse_xiaohongshu
- Method: `POST`
- Path: `/scrapt/parse_xiaohongshu`
- 用途：解析小红书分享链接，提取视频直链与元数据。

## parse_douyin
- Method: `POST`
- Path: `/scrapt/parse_douyin`
- 用途：解析抖音分享链接，提取视频直链与元数据。

## parse_kuaishou
- Method: `POST`
- Path: `/scrapt/parse_kuaishou`
- 用途：解析快手分享链接，提取视频直链与元数据。

## parse_bilibili
- Method: `POST`
- Path: `/scrapt/parse_bilibili`
- 用途：解析 B 站分享链接，提取视频直链与元数据。

## parse_tiktok
- Method: `POST`
- Path: `/scrapt/parse_tiktok`
- 用途：解析 TikTok 分享链接，提取视频直链与元数据。

## parse_youtube
- Method: `POST`
- Path: `/scrapt/parse_youtube`
- 用途：解析 YouTube 分享链接，提取视频直链与元数据。

## 通用请求参数
- `url` (string, required): 待解析的分享链接或含链接文本。

## 通用示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/scrapt/parse_douyin' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "url": "https://v.douyin.com/3d79h4hnEHc/"
}'
```

## 通用响应结构
- `success` (boolean)
- `data.platform` (string)
- `data.original_url` (string)
- `data.type` (string)
- `data.video.url` (string)
- `data.video.duration` / `height` / `width` / `size` (number)
- `data.title` / `data.desc` (string)
- `data.author` (object)
- `data.stats` (object)

## 常见平台值
- `xiaohongshu`
- `douyin`
- `kuaishou`
- `bilibili`
- `tiktok`
- `youtube`

## 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- 响应非 JSON：中止流程并保留原始响应。
- `success=false` 或缺失 `data.video.url`：视为解析失败或返回不完整。
