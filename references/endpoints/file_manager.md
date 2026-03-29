# Endpoint Params

## upload_init
- Method: `POST`
- Path: `/sts/upload/init`
- 用途：按文件名与大小申请临时上传凭证，返回 OSS 临时凭证、`bucket_name` 与 `object_key`。

### 请求参数
- `file_name` (string, required): 文件名。
- `file_size_bytes` (int, required): 文件字节数。

### 关键响应字段
- `success` (boolean)
- `credentials.AccessKeyId`
- `credentials.AccessKeySecret`
- `credentials.SecurityToken`
- `bucket_name`
- `object_key`

## upload_complete
- Method: `POST`
- Path: `/sts/upload/complete`
- 用途：通知服务端上传完成并换取可访问 URL。

### 请求参数
- `object_key` (string, required): `upload_init` 返回的对象路径。

### 关键响应字段
- `success` (boolean)
- `public_signed_url` (string)

## upload_file
- Method: `COMPOSED`
- Path: `upload_init -> OSS PUT -> upload_complete`
- 用途：素材管理一键上传流程。先申请 STS，再直传 OSS，最后拿可访问 URL。

### 关键步骤
1) `POST /sts/upload/init`
2) 使用返回的 STS 凭证对 `https://{bucket_name}.{oss_endpoint}/{object_key}` 执行 `PUT`
3) `POST /sts/upload/complete`

### 关键结果
- `object_key`
- `public_signed_url`

## 通用错误判定
- HTTP 非 2xx：请求失败。
- 响应非 JSON：返回格式异常。
- `success=false`：业务失败。
- 上传流程关键字段缺失：`credentials` / `object_key` / `bucket_name` / `public_signed_url`。
