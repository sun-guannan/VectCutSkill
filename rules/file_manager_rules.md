# file_manager 端点规则（upload_init/upload_complete/upload_file）

## 适用范围
- `POST /sts/upload/init`
- `POST /sts/upload/complete`
- `upload_file` 组合流程（init -> OSS PUT -> complete）

## 请求路由与参数策略
- 当目标是“上传本地素材并获取可访问地址”时，优先执行 `upload_file` 组合流程。
- 当已有 `object_key` 且仅需回收 URL 时，执行 `upload_complete`。
- `upload_init` 必填：
  - `file_name`
  - `file_size_bytes`
- `upload_complete` 必填：
  - `object_key`
- 上传文件前必须先检查本地文件存在且可读。
- 上传成功后优先返回：
  - `object_key`
  - `public_signed_url`

## 上传签名约束
- 使用 OSS V1 签名串：
  - `PUT\n\n{Content-Type}\n{Date}\n{x-oss-security-token:{SecurityToken}\n}/{bucket_name}/{object_key}`
- 使用 `credentials.AccessKeySecret` 做 HMAC-SHA1，并 Base64 编码。
- 请求头至少包含：
  - `Date`
  - `Content-Type`
  - `x-oss-security-token`
  - `Authorization: OSS {AccessKeyId}:{signature}`

## 专属异常处理
- `upload_init` 或 `upload_complete` HTTP 非 2xx：直接失败并输出状态码与响应体。
- 响应非 JSON：直接失败并保留原始响应。
- `success=false`：业务失败。
- OSS PUT 非 200/201：上传失败。
- 关键字段缺失：
  - init 缺失 `credentials` / `bucket_name` / `object_key`
  - complete 缺失 `public_signed_url`

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `file_path`
- `file_name`
- `file_size_bytes`
- `object_key`
