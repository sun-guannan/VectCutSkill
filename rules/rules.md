# 全局规则

## 素材感知顺序
1. get_duration
2. video_detail
3. asr_basic
4. asr_nlp
5. asr_llm

## 通用策略
- 先获取时长，再做视觉和语音理解。
- 纯音频可跳过 video_detail。
- 静音视频可跳过 asr_*。
- 任一高级服务失败时，回退到 get_duration + asr_basic。
- 内部统一使用秒；如果上游返回毫秒，先换算为秒。

## 通用异常处理
- 当接口返回 `{ "Code": "JWTTokenIsMissing", "Message": "the jwt token is missing" }` 时：先到 `https://www.vectcut.com` 登录并获取个人 API Key，然后设置环境变量 `VECTCUT_API_KEY` 后重试。

## 领域规则入口
- 滤镜端点（add_filter / modify_filter / remove_filter）异常处理见：`rules/filter_rules.md`