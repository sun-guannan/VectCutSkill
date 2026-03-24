# Endpoint Params

## generate_ai_image
- Method: `POST`
- Path: `/llm/image/generate`
- 用途：调用聚合图像模型生成图片，返回图片 URL。

### 请求参数
- `prompt` (string, required): 图像生成提示词。
- `model` (string, optional): 模型 ID，默认 `jimeng-4.5`，常用 `nano_banana_2`、`nano_banana_pro`、`jimeng-4.5`。
- `reference_image` (string, optional): 参考图 URL，支持图生图。
- `size` (string, optional): 输出尺寸，格式 `宽x高`，默认 `1024x1024`。

### 模型与分辨率约束
- `nano_banana_2`、`nano_banana_pro`：支持 1K/2K/4K 多比例分辨率。
- `jimeng-4.5`：支持 1K/2K/4K，常用 `1:1`、`16:9`、`9:16`、`4:3`、`3:2`、`21:9`。
- 具体可选分辨率组合以官方文档为准。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/llm/image/generate' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "prompt": "给这个人带上红色的帽子",
  "model": "nano_banana_2",
  "reference_image": "https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/shuziren.jpg",
  "size": "1024x1024"
}'
```

### 关键响应字段
- `error` (string)
- `image` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `error` 非空：业务失败，修正参数后重试。
- 响应非 JSON：中止流程并保留原始响应。
- 缺少 `image`：视为生成结果不可用。
