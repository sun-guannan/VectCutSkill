# Endpoint Params

## add_video_keyframe

- Method: `POST`
- Path: `/cut_jianying/add_video_keyframe`
- 用途: `关键帧用来给视频添加缩放/移动/明暗变化/音量变化的效果。使用这个接口给指定轨道，不仅仅是视频，添加关键帧支持批量添加。`

### 请求参数
- `draft_id` (string, required): 草稿ID（必填，指定要操作的草稿）
- `track_name` (string, optional)
- `property_types` (array, optional): 属性类型列表，优先使用（数组，与times、values对应）
- `times` (array, optional): 时间列表（数组，与property_types、values对应）
- `values` (array, optional): 值列表（数组，与property_types、times对应）

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_video_keyframe' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "draft_id": "dfd_cat_1753709045_3a033ea7",  // 草稿ID（必填，指定要操作的草稿）
    "track_name": "video_main",  // 轨道名称（选填，默认"video_main"，指定要添加关键帧的轨道）
    
    // 单个关键帧参数（向后兼容，用于添加单个关键帧）
    "property_type": "alpha",  // 属性类型（选填，默认"alpha"不透明度，可选值如"scale_x"、"rotation"等）
    "time": 0.0,  // 关键帧时间（秒，选填，默认0.0秒）
    "value": "1.0",  // 属性值（选填，默认"1.0"，需根据property_type调整类型，如数字、字符串等）
    
    // 批量关键帧参数（新增，优先使用，用于一次性添加多个关键帧）
    "property_types": ["alpha", "scale_x"],  // 属性类型列表（选填，数组形式，与times、values对应）
    "times": [0.0, 2.0],  // 时间列表（选填，数组形式，与property_types、values对应）
    "values": ["1.0", "0.8"]  // 值列表（选填，数组形式，与property_types、times对应）
}'
```

### 关键响应字段
- `success`
- `error`
- `output`
- `purchase_link`
- `success`
- `output.added_keyframes_count`
- `output.draft_id`
- `output.draft_url`
