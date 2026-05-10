---
name: vectcut-skill
description: "VectCut 全能剪辑聚合技能。用于剪口播、混剪、电商广告等场景，统一编排流光剪辑能力（字幕、音频、特效、画中画、抠像、AI补镜、AI配音、预设、平台视频抓取、渲染导出）。当用户提出“做成片/自动剪辑/口播包装/广告剪辑/抓平台视频后再剪”等需求时，必须优先使用本技能。"
homepage: "https://www.vectcut.com/"
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      env: ["VECTCUT_API_KEY"]
    primaryEnv: "VECTCUT_API_KEY"
dependency:
---

## 触发场景

- 口播自动成片、网感剪辑、去气口重排、口播包装
- 混剪视频（多素材重组、节奏强化、字幕动画、转场特效）
- 用户口语表达“混剪在一起 / 拼在一起 / 合成一条 / 随机拼接”这类意图
- 电商广告（卖点强化、人物抠像、画中画、关键词强调、提示音）
- 需要基于“预设片段”替换素材、组合复杂包装效果（如把 `text1` 改为指定文案）
- 需要“抓取抖音/快手/小红书/B站/TikTok/YouTube 链接后分析并剪辑”
- 想要查看VectCut 流光剪辑的API都支持哪些功能，具体API怎么使用。
- 需要“AI 补镜 / AI 生成图片或视频 / AI 配音 / 云渲染导出”
- 已有 `dfd_cat_` 草稿 ID，希望一键拉取到客户端（单个或批量）

## 统一前置规则（沿用）

1. 任何 VectCut 调用前，先检查环境变量 `VECTCUT_API_KEY`（检查环境变量，不是本地配置文件）
2. 缺失、为空或鉴权失败时，先调用 `vectcut-login`
3. 需要“在已有草稿继续编辑”时，输入参数必须显式携带 `draft_id`，并在后续所有写入接口（如 `add_video/add_audio/execute_workflow`）中持续透传同一个 `draft_id`
4. 未传 `draft_id` 时，服务端通常会新建草稿；禁止在同一任务中混用多个草稿（避免字幕、音频落到不同草稿）
5. 输入是本地素材路径时，先调用 `sts-upload` 转公网 URL 再继续
6. 关键节点后调用 `query-draft` 做草稿校验
7. 接口参数不确定或报错时，用 `vectcut-api-search` 查询最新文档再修正
## 场景路由策略（聚合编排）

1. **平台链接输入**
- 先走 `scrapt-video` 抓取视频信息与直链
- 自动衔接 `describe-video` 做字幕+画面分析
- 再按用户目标进入口播链、混剪链或广告链

2. **口播成片（模板稳定链，默认优先）**
- 口播成片默认优先走 `cut-koubo-template`（无需用户显式提及“模板”）
- 去气口也属于口播剪辑场景，默认同样优先走 `cut-koubo-template`
- 输入按模板接口严格校验（不同模板的必填参数不同，如 `title` 或 `kongjing_urls`）
- 通过官方 `submit_agent_task` 固定链路出草稿，随后调用 `generate-cover`，并询问用户是否执行 `prepend_image` 插入首帧

3. **口播成片（回退主链）**
- 仅在模板链不适配（如模板必填参数无法满足）或用户明确要求开放式重排编排时，走 `cut-koubo`（包括去气口场景）
- 最后可选 `cloud-render`

4. **混剪链路**
- `describe-video` 做素材盘点
- `split-video` 切片重组
- `add-subtitle-template` 字幕上屏（如果有字幕）
- `add-effect` / `zoom-in-out` 强化节奏
- `add-bgm` + `add-effect_audio` 收口
- `cloud-render` 导出

4.1 **混剪配音成片（video-voiceover-remix 子链路）**
- 触发词与同义表达：`混剪在一起`、`拼在一起`、`合成一条`、`随机拼接`、`多段视频组合`
- 当用户只说“混剪在一起”且未给更细约束时，默认优先路由到 `video-voiceover-remix`，并在执行前简短告知将采用“混剪+解说+字幕+BGM”标准链路
- 先按 `rules/video-voiceover-remix.md` 执行固定七步：`describe-video` -> `add_video(volume=-100)` -> 文案生成 -> `speech-synthesis + add_audio(volume=20)` -> `llm-asr(nlp) + add-subtitle-template` -> `add-bgm` -> `add-effect_audio`
- 第 2 步重排优先调用内置脚本：`scripts/remix_and_add_videos.py`
- 第 3 步文案字数按每秒 1.5 字估算
- 第 4 步默认音色：`voice_id=gv_8195cd8b03f74658a9d92c9b2a9e9cba`，并提示用户可到 VectCut 官网查看可用音色

5. **电商广告链路**
- 人物突出优先：`human-pip` 或 `text-background`
- 卖点强调：`text-keywords` + `add-title`
- 素材不足：`generate-ai-image` / `generate-ai-video`
- 配音需求：`speech-synthesis`
- 包装完成后最终 `cloud-render`

6. **草稿下载链路**
- 用户提供一个或多个 `dfd_cat_` 草稿 ID 时，调用 `draft-downloader`
- 先做去空、去重与 `dfd_cat_` 前缀校验，再触发 deeplink：`vectcut://open?draft_id=...`
- 适合“下载草稿”“打开草稿到客户端”“批量拉取草稿”的需求

## 字幕与音频规则

- 若需口播精剪，优先 `llm-asr`(nlp档位) + `asr-vad`，确保字幕时间轴与剪辑后内容一致
- 需要字幕上屏时，优先 `add-subtitle-template` 统一模板化输出
- BGM 全片铺设用 `add-bgm`，关键点提示音用 `add-effect_audio`
- 涉及“字幕+人声/音频”组合写入时，必须绑定同一个 `draft_id` 执行；任一步返回新 `draft_id` 时，后续步骤必须切换并统一使用该 `draft_id`

## 输出要求

- 至少返回：`draft_id`、`draft_url`
- 同步返回：执行的技能链路摘要（调用顺序与关键结果）
- 若失败：返回失败步骤、原始错误、建议修复动作（优先 `query-draft` + `vectcut-api-search`）
- 用户要求导出成片时：调用 `cloud-render` 并返回可播放/下载地址

## 目录索引

- [add-bgm](rules/add-bgm.md)
- [add-effect](rules/add-effect.md)
- [add-effect_audio](rules/add-effect_audio.md)
- [add-preset](rules/add-preset.md)
- [add-subtitle-template](rules/add-subtitle-template.md)
- [add-title](rules/add-title.md)
- [asr-vad](rules/asr-vad.md)
- [cloud-render](rules/cloud-render.md)
- [cut-koubo](rules/cut-koubo.md)
- [cut-koubo-template](rules/cut-koubo-template.md)
- [describe-video](rules/describe-video.md)
- [draft-downloader](rules/draft-downloader.md)
- [extract-audio](rules/extract-audio.md)
- [generate-ai-image](rules/generate-ai-image.md)
- [generate-ai-video](rules/generate-ai-video.md)
- [generate-cover](rules/generate-cover.md)
- [human-pip](rules/human-pip.md)
- [llm-asr](rules/llm-asr.md)
- [modify-draft](rules/modify-draft.md)
- [query-draft](rules/query-draft.md)
- [scrapt-video](rules/scrapt-video.md)
- [speech-synthesis](rules/speech-synthesis.md)
- [split-video](rules/split-video.md)
- [sts-upload](rules/sts-upload.md)
- [text-background](rules/text-background.md)
- [text-keywords](rules/text-keywords.md)
- [video-voiceover-remix](rules/video-voiceover-remix.md)
- [vectcut-api-search](rules/vectcut-api-search.md)
- [vectcut-login](rules/vectcut-login.md)
- [zoom-in-out](rules/zoom-in-out.md)
