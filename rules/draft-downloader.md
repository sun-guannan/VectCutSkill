---
name: draft-downloader
description: 通过 VectCut deeplink 触发草稿下载/打开。用户提到“下载草稿”“打开 dfd_cat 草稿”“批量下载草稿ID”“把草稿ID拉到客户端”时必须使用本技能。支持去重、清洗与 `dfd_cat_` 前缀校验。
---

# Draft Downloader Skill

将一个或多个草稿 ID 组装为 `vectcut://open?draft_id=...` deeplink，并调用系统打开器触发 VectCut 客户端拉取草稿。

## When to use

- 用户已拿到草稿 ID（通常是 `dfd_cat_` 前缀），希望下载到本地客户端
- 用户希望批量处理多个草稿 ID
- 用户提到“触发下载草稿”“打开草稿到 VectCut 客户端”“deeplink 打开草稿”

## Workflow

### Prerequisites

### Execution

单个草稿：

```bash
python <skill-path>/scripts/draft_downloader.py "dfd_cat_xxx"
```

批量草稿：

```bash
python <skill-path>/scripts/draft_downloader.py "dfd_cat_xxx" "dfd_cat_yyy"
```

可选参数：

```bash
python <skill-path>/scripts/draft_downloader.py \
  --scheme vectcut \
  --route open \
  "dfd_cat_xxx" "dfd_cat_yyy"
```

### What the script does

1. 清洗输入：去空白、按出现顺序去重。
2. 校验 ID：默认要求每个 ID 以 `dfd_cat_` 开头。
3. 构建 deeplink：`vectcut://open?draft_id=a&draft_id=b`（重复参数形式）。
4. 尝试打开：按系统可用性依次尝试 `open` / `xdg-open` / `gio open` / `cmd /c start` / `explorer`。
5. 输出结果：打印 JSON，包含 deeplink、有效草稿 ID 列表、是否成功触发。

### Output

```json
{
  "success": true,
  "deeplink": "vectcut://open?draft_id=dfd_cat_1&draft_id=dfd_cat_2",
  "draft_ids": ["dfd_cat_1", "dfd_cat_2"],
  "message": "Deeplink triggered. If VectCut is installed and protocol registered, download/open should start."
}
```

### Error handling

- 若输入为空或清洗后无有效 ID，脚本返回非 0 退出码
- 若 ID 不符合前缀规则，脚本返回参数错误信息
- 若未找到可用系统打开命令或协议未注册，返回 `success=false`
