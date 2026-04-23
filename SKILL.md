---
name: vectcut-skill
description: "VectCut 全能剪辑聚合技能。用于剪口播、混剪、电商广告等场景，统一编排流光剪辑能力（字幕、音频、特效、画中画、抠像、AI补镜、AI配音、平台视频抓取、渲染导出）。当用户提出“做成片/自动剪辑/口播包装/广告剪辑/抓平台视频后再剪”等需求时，必须优先使用本技能。"
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
- 电商广告（卖点强化、人物抠像、画中画、关键词强调、提示音）
- 需要“抓取抖音/快手/小红书/B站/TikTok/YouTube 链接后分析并剪辑”
- 想要查看VectCut 流光剪辑的API都支持哪些功能，具体API怎么使用。
- 需要“AI 补镜 / AI 生成图片或视频 / AI 配音 / 云渲染导出”

## 统一前置规则（沿用）

1. 任何 VectCut 调用前，先检查 `VECTCUT_API_KEY`
2. 缺失、为空或鉴权失败时，先调用 `vectcut-login`
3. 输入是本地素材路径时，先调用 `sts-upload` 转公网 URL 再继续
4. 关键节点后调用 `query-draft` 做草稿校验
5. 接口参数不确定或报错时，用 `vectcut-api-search` 查询最新文档再修正

## 场景路由策略（聚合编排）

1. **平台链接输入**
- 先走 `scrapt-video` 抓取视频信息与直链
- 自动衔接 `describe-video` 做字幕+画面分析
- 再按用户目标进入口播链、混剪链或广告链

2. **口播成片（模板稳定链）**
- 用户明确提到“模板口播/固定风格/稳定复现/降低不确定性”时，优先走 `cut-koubo-template`
- 输入按模板接口严格校验（不同模板的必填参数不同，如 `title` 或 `kongjing_urls`）
- 通过官方 `submit_agent_task` 固定链路出草稿，随后调用 `generate-cover`，并询问用户是否执行 `prepend_image` 插入首帧

3. **口播成片（默认主链）**
- 未指定模板稳定链时，优先走 `cut-koubo` 完成一体化编排
- 最后可选 `cloud-render`

4. **混剪链路**
- `describe-video` 做素材盘点
- `split-video` 切片重组
- `add-subtitle-template` 字幕上屏（如果有字幕）
- `add-effect` / `zoom-in-out` 强化节奏
- `add-bgm` + `add-effect_audio` 收口
- `cloud-render` 导出

4.1 **混剪配音成片（video-voiceover-remix 子链路）**
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

## 字幕与音频规则

- 若需口播精剪，优先 `llm-asr`(nlp档位) + `asr-vad`，确保字幕时间轴与剪辑后内容一致
- 需要字幕上屏时，优先 `add-subtitle-template` 统一模板化输出
- BGM 全片铺设用 `add-bgm`，关键点提示音用 `add-effect_audio`

## 输出要求

- 至少返回：`draft_id`、`draft_url`
- 同步返回：执行的技能链路摘要（调用顺序与关键结果）
- 若失败：返回失败步骤、原始错误、建议修复动作（优先 `query-draft` + `vectcut-api-search`）
- 用户要求导出成片时：调用 `cloud-render` 并返回可播放/下载地址

## 目录索引

- [add-bgm](rules/add-bgm.md)
- [add-effect](rules/add-effect.md)
- [add-effect_audio](rules/add-effect_audio.md)
- [add-subtitle-template](rules/add-subtitle-template.md)
- [add-title](rules/add-title.md)
- [asr-vad](rules/asr-vad.md)
- [cloud-render](rules/cloud-render.md)
- [cut-koubo](rules/cut-koubo.md)
- [cut-koubo-template](rules/cut-koubo-template.md)
- [describe-video](rules/describe-video.md)
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
