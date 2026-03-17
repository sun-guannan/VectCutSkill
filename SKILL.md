---
name: "vectcut-skill"
description: "AI 视频导演与自动化剪辑专家。能够理解视频素材内容、视频创作指令，自主规划脚本结构，并通过调用 VectCut API 实现创建剪映草稿、编排素材（B-roll/转场/特效）、生成 AI 配音与字幕，实现端到端的视频创作流程。"
dependency:
---

# VectCut Skill（自主规划型 AI 视频架构师）

本技能赋予 AI 像专业剪辑师一样**“思考与执行”**的能力。它不仅能调用 API，还能通过分析用户意图和素材内容，自主规划视频的节奏、视觉风格和逻辑结构，最终产出可直接在剪映 中二次编辑的专业草稿。

## 核心智能行为

* **素材感知**：分析用户提供的视频/图片/音频 URL，理解画面内容与剪辑指令；优先调用现有服务 `get_duration`、`video_detail`、`asr_basic`、`asr_nlp`、`asr_llm` 完成时长获取、画面理解与语音内容解析。
* **脚本规划**：根据主题（如“成语故事”、“产品评测”）自动拆解分镜，确定各片段时长。
* **视觉编排**：自主选择合适的转场（Transitions）、特效（Effects）和滤镜（Filters）。
* **AI 资源补全**：当素材不足时，主动调用 `generate_image`，`generate_speech` 或 `generate_ai_video` 生成 B-roll 填充。
* **音画同步**：如果需要，可以利用`get_duration`计算素材的时长，精确对齐视频轨道与音频轨道。

## 环境变量配置

所有调用均依赖于远程服务，需在环境中配置：

```bash
export VECTCUT_API_KEY="<your_token>"
```

快捷脚本与示例请求体见：

- `skill_me/rules/`：决策规则与调用顺序
- `skill_me/scripts/`：最小可复用调用封装
- `skill_me/examples/`：端到端示例
- `skill_me/prompts/`：素材理解与脚本规划提示词
- `skill_me/references/`：端点参数与字段契约

## 执行路由

按“能力域”路由。每个能力域复用同一条五层调用链：

1. 规则层（rules）
   - 全局：`skill_me/rules/rules.md`
   - 领域：`skill_me/rules/<domain>_rules.md`
2. 参数层（references）
   - 端点：`skill_me/references/endpoints/<domain>.md`
   - 枚举：`skill_me/references/enums/*.json`
3. 提示层（prompts）
   - 路由与请求体生成：`skill_me/prompts/<domain>_ops.md`
4. 执行层（scripts）
   - API 调用与异常处理：`skill_me/scripts/<domain>_ops.py`
5. 验证层（examples）
   - 最小闭环验证：`skill_me/examples/<domain>_ops_demo.py`

### 当前已落地能力域：filter / effect
- 规则：`skill_me/rules/filter_rules.md`（含 filter 与 effect）
- 参数：`skill_me/references/endpoints/filter.md`（含 filter 与 effect）
- 提示：`skill_me/prompts/filter_ops.md`（含 filter 与 effect）
- 执行：`skill_me/scripts/filter_ops.py`（含 filter 与 effect）
- 示例：`skill_me/examples/filter_ops_demo.py`（含 filter 与 effect）

### 新增能力域时的约定
- 域命名统一使用小写下划线：`text` / `audio` / `subtitle` / `effect` / `keyframe`。
- 根文件只维护“能力域索引”，端点细节只写在对应 `<domain>.md`。
- 任意域新增端点时，只改该域文件，不改其他域。

## 交互约定（输出格式）

当你使用本技能完成“创建/编辑/渲染”类任务时，输出优先包含这些字段，便于后续继续编辑或查询：

- `draft_id`：草稿 ID
- `draft_url`：可打开的剪映/CapCut 草稿 URL，应封装为 markdown 超链接格式：`[草稿名称](draft_url)`
- `material_id`: 添加进草稿后的素材（图片、视频、音频、字幕、滤镜、贴纸、特效）的ID，方便后面继续操作

## 常用能力（可组合）

### 1) 创建草稿

调用：`POST /create_draft`

示例（1080x1920 竖屏）：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"width":1080,"height":1920,"name":"demo"}'
```

### 2) 添加素材与时间线编排

你可以按需组合以下操作（都为 `POST` JSON）：

- `/add_video`：添加视频（支持裁切、速度、变换、蒙版、混合、转场等）
- `/add_image`：添加图片（支持入/出场动画、转场、蒙版、混合等）
- `/add_audio`：添加音频（支持音量、变速、淡入淡出、音效等）
- `/add_text`：添加文字（支持字体、描边、阴影、背景、动画、多样式范围等）
- `/add_subtitle`：添加字幕（SRT + 样式）
- `/add_sticker`：添加贴纸
- `/add_effect`：添加特效（scene/character）
- `/add_filter`：添加滤镜
- `/add_video_keyframe`：添加关键帧（如透明度等）
- `/get_video_scene_effect_types`：获取场景特效（用于 effect_category=scene）
- `/get_video_character_effect_types`：获取人物特效（用于 effect_category=character）
- `/get_filter_types`：添加滤镜

### 3) 高级能力（AI 与搜索）

- `/generate_image`：AI 文生图并添加到草稿
- `/generate_ai_video`：AI 文生视频（异步任务）
- `/generate_speech`：TTS 语音合成并添加到草稿
- `/remove_bg`：智能抠像（移除背景）并生成合成预设
- `/search_sticker`：搜索在线贴纸素材

### 4) 获取可用枚举（动画/转场/特效/滤镜/字体）

用于让 AI 在可用范围内选型：

- `GET /get_transition_types`
- `GET /get_mask_types`
- `GET /get_intro_animation_types`、`/get_outro_animation_types`、`/get_combo_animation_types`
- `GET /get_text_intro_types`、`/get_text_outro_types`、`/get_text_loop_anim_types`
- `GET /get_video_scene_effect_types`、`/get_video_character_effect_types`
- `GET /get_filter_types`
- `GET /get_font_types`
- `GET /get_audio_effect_types`

示例（以转场枚举为例）：

```bash
curl -X GET "http://open.vectcut.com/cut_jianying/get_transition_types" \
  -H "Authorization: Bearer $VECTCUT_API_KEY"
```

### 4) 发起渲染并查询状态

- `POST /generate_video`：对草稿 `draft_id` 发起渲染（返回 `task_id`）
- `POST /task_status`：轮询 `task_id` 获取渲染进度与结果

### 5. 典型场景示例

#### 场景 A：成语故事/绘本视频制作（文生图 + 配音 + 自动对齐）

当用户需要制作“亡羊补牢”这样的故事视频时，建议按以下逻辑编排：

1.  **分镜拆解**：将故事拆分为 N 个片段（图片 Prompt + 旁白文本）。
2.  **生成循环**（对每个片段）：
    *   调用 `generate_image` 生成插图，获得 `image_url`。
    *   调用 `generate_speech` 生成配音，获得 `audio_url`。
    *   **关键点**：调用 `get_duration(url=audio_url)` 获取配音时长 `duration`。
    *   调用 `add_image`，将 `image_url` 加入草稿，并设置 `duration` 等于配音时长，确保音画同步。
    *   （如果 `generate_speech` 未自动添加）调用 `add_audio` 添加配音。

参考 Prompt 模板：`assets/prompts/story_creation_zh.md`

#### 场景 B：素材混剪

1) 创建草稿 → 2) add_video/add_audio/add_subtitle → 3) generate_video → 4) task_status 轮询

```bash
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -d '{"name":"my short"}'
```

假设返回 `draft_id=xxx` 后：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/add_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"draft_id":"xxx","video_url":"https://example.com/a.mp4","start":0,"end":10,"target_start":0}'
```

```bash
curl -X POST http://open.vectcut.com/cut_jianying/add_subtitle \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"draft_id":"xxx","srt":"1\\n00:00:00,000 --> 00:00:02,000\\n你好\\n"}'
```

发起渲染：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/generate_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"draft_id":"xxx","resolution":"1080P","framerate":"30"}'
```

轮询：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/task_status \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task_id":"TASK_ID"}'
```

## 使用提示（让 AI 更“会剪”）

- 让用户提供素材 URL、期望时长、画面比例（9:16/16:9/1:1）、字幕风格、BGM 风格
- 需要严格可控的效果时，先拉取枚举（转场/特效/滤镜/字体），再进行选择与组装
- 复杂需求可以在上层自己组织调用顺序，这里只负责暴露基础视频编辑与渲染接口
