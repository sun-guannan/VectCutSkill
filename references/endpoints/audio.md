# Endpoint Params

## add_audio

- Method: `POST`
- Path: `/cut_jianying/add_audio`
- 用途: `添加音频`

### 请求参数

- `audio_url` (string, required): 音频文件URL（必填）
- `start` (number, optional): 音频素材的起始截取时间（秒，默认0）
- `end` (number, optional): 音频素材的结束截取时间（秒，可选，默认取完整音频长度）
- `draft_id` (string, optional): 草稿ID（可选，用于指定操作的草稿）
- `volume` (number, optional): 音量（选填，单位db，默认0.0，-100表示静音）
- `target_start` (number, optional): 音频在时间线上的起始位置（秒，默认0）
- `speed` (number, optional): 音频速度（默认1.0，>1加速，<1减速）
- `track_name` (string, optional): 轨道名称
- `duration` (number, optional): 音频素材的总时长（秒）主动设置可以提升请求速度
- `effect_type` (string, optional): 音效，用get_audio_effect_types工具查看支持的音效
- `effect_params` (array, optional): 音效参数，get_audio_effect_types工具会返回params列表，这里填的值与之对应
- `width` (integer, optional): 视频宽度（默认1080）
- `height` (integer, optional): 视频高度（默认1920）
- `fade_in_duration` (number, optional): 淡入时间，单位秒
- `fade_out_duration` (number, optional): 淡出时间，单位秒

### 示例请求

```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_audio' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "audio_url": "https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",  // 音频文件URL（必填）
  "start": 0,  // 音频素材的起始截取时间（秒，默认0）
  "end": 30,  // 音频素材的结束截取时间（秒，可选，默认取完整音频长度）
  "draft_id": "your_draft_id",  // 草稿ID（可选，用于指定操作的草稿）
  "volume": 0.8,  // 音量大小（默认1.0）
  "target_start": 5,  // 音频在时间线上的起始位置（秒，默认0）
  "speed": 1.2,  // 音频速度（默认1.0，>1加速，<1减速）
  "track_name": "audio_background",  // 轨道名称（默认"audio_main"）
  "duration": 20,  // 音频素材的总时长（秒）主动设置可以提升请求速度
  "effect_type": "回音",  // 音效类型
  "effect_params": [45],  // 音效参数（可选，根据effect_type设置）
  "width": 1080,  // 视频宽度（默认1080）
  "height": 1920  // 视频高度（默认1920）
}'
```

### 关键响应字段

- `success`
- `error`
- `output`
- `purchase_link`
- `output.draft_id`
- `output.draft_url`
- `output.material_id`

## modify_audio

- Method: `POST`
- Path: `/cut_jianying/modify_audio`
- 用途: `修改音频`

### 请求参数

- `draft_id` (string, required): 草稿ID
- `material_id` (string, required): 素材ID
- `audio_url` (string, optional): 音频文件URL（必填）
- `start` (number, optional): 音频素材的起始截取时间（秒，默认0）
- `end` (number, optional): 音频素材的结束截取时间（秒，可选，默认取完整音频长度）
- `volume` (number, optional): 音量（选填，单位db，默认0.0，-100表示静音）
- `target_start` (number, optional): 音频在时间线上的起始位置（秒，默认0）
- `speed` (number, optional): 音频速度（默认1.0，>1加速，<1减速）
- `track_name` (string, optional): 轨道名称
- `duration` (number, optional): 音频素材的总时长（秒）主动设置可以提升请求速度
- `effect_type` (string, optional): 音效，用get_audio_effect_types工具查看支持的音效
- `effect_params` (array, optional): 音效参数，get_audio_effect_types工具会返回params列表，这里填的值与之对应
- `fade_in_duration` (number, optional): 淡入时间，单位秒
- `fade_out_duration` (number, optional): 淡出时间，单位秒

### 示例请求

```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/modify_audio' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "draft_id": "dfd_cat_1773889936_4fa0ec90",
    "material_id": "d06c5d16a9434f35827cf03527836b0f",
    "volume": -100
}'
```

### 关键响应字段

- `success`
- `error`
- `output`
- `purchase_link`
- `output.draft_id`
- `output.draft_url`
- `output.material_id`

## remove_audio

- Method: `POST`
- Path: `/cut_jianying/remove_audio`
- 用途: `删除音频`

### 请求参数

- `draft_id` (string, required): 草稿ID
- `material_id` (string, required): 素材ID

### 示例请求

```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/remove_audio' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "draft_id": "dfd_cat_1773889936_4fa0ec90",
    "material_id": "d06c5d16a9434f35827cf03527836b0f"
}'
```

### 关键响应字段

- `success`
- `error`
- `output`
- `purchase_link`
- `output.draft_id`
- `output.draft_url`
