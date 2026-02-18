---
name: seedance2-api
description: Out-of-the-box Seedance 2.0 API skill — just one API key to generate AI videos. Builds storyboards, generates reference images with Seedream 4.5, submits video tasks, and polls results. Supports both MCP and standalone Python script mode. Use when the user mentions seedance, AI video, storyboard, or video generation.
license: MIT
compatibility: Requires Python 3.8+ with requests. Works with Cursor, Claude Code, or any SKILL.md-compatible agent.
metadata:
  author: hexiaochun
  version: "1.0"
  tags: video-generation ai-video seedance storyboard bytedance seedream
---

# Seedance 2.0 分镜创作与视频生成

从创意到成片的全流程：引导分镜 → 画参考图 → 提交视频 → 获取结果。

## Step 0: 确定执行方式（MCP 或脚本）

**优先检测 MCP 是否可用：**

1. 检查 `xskill-ai` MCP 服务状态（读取 `mcps/user-xskill-ai/STATUS.md`）
2. 如果 MCP 可用 → 使用 `submit_task` / `get_task` 等 MCP 工具
3. 如果 MCP 不可用或报错 → 切换到**脚本模式**

**脚本模式前置条件：**

1. 确认环境变量 `XSKILL_API_KEY` 已设置（Shell 执行 `echo $XSKILL_API_KEY | head -c 10`）
2. 如果未设置，提示用户：
   ```
   export XSKILL_API_KEY=sk-your-api-key
   获取 API Key: https://www.xskill.ai/#/v2/api-keys
   ```
3. 确认 `requests` 已安装（`pip install requests`）

**脚本路径：** 本 Skill 目录下的 `scripts/seedance_api.py`，定位方式：
```bash
# 通过 Glob 工具搜索
glob: .cursor/skills/seedance2-api/scripts/seedance_api.py
```

> 后续步骤中，每个 API 调用都同时给出 **MCP 方式** 和 **脚本方式**，根据 Step 0 的判断选择其一执行。

## Step 1: 理解用户想法

收集以下信息（缺失的主动询问）：

- **故事核心**：一句话概括要拍什么
- **时长**：4-15 秒
- **画面比例**：16:9 / 9:16 / 1:1 / 21:9 / 4:3 / 3:4
- **视觉风格**：写实/动画/水墨/科幻/赛博朋克等
- **素材情况**：是否有现成图片/视频/音频，还是需要 AI 生成
- **功能模式**：是否需要首尾帧控制（first_last_frames），否则默认全能模式（omni_reference）

## Step 2: 深入挖掘（5 个维度）

针对每个维度引导用户补充细节：

1. **内容** - 主角是谁？做什么？在哪里？
2. **视觉** - 光影、色调、质感、氛围
3. **镜头** - 推/拉/摇/移/跟/环绕/升降
4. **动作** - 主体的具体动作和节奏
5. **声音** - 配乐风格、音效、对白

## Step 3: 构建分镜结构

按时间轴拆分镜头，使用以下公式：

```
【风格】_____风格，_____秒，_____比例，_____氛围

0-X秒：[镜头运动] + [画面内容] + [动作描述]
X-Y秒：[镜头运动] + [画面内容] + [动作描述]
...

【声音】_____配乐 + _____音效 + _____对白
【参考】@image_file_1 _____，@video_file_1 _____
```

详细模板和示例见 [reference.md](reference.md)。

## Step 4: 生成参考图（如需要）

若用户没有现成素材，使用 Seedream 4.5 生成角色图、场景图、首帧/尾帧等。

### 文生图

<details>
<summary><b>MCP 方式</b></summary>

调用 `submit_task` 工具：
- model_id: `fal-ai/bytedance/seedream/v4.5/text-to-image`
- parameters:
  - prompt: 详细的图片描述（英文效果更佳）
  - image_size: 根据视频比例选择
  - num_images: 需要的数量（1-6）

</details>

<details>
<summary><b>脚本方式</b></summary>

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "fal-ai/bytedance/seedream/v4.5/text-to-image" \
  --params '{"prompt":"An astronaut in a white spacesuit...","image_size":"landscape_16_9","num_images":1}'
```

</details>

### 图像编辑（基于现有图片修改）

<details>
<summary><b>MCP 方式</b></summary>

调用 `submit_task` 工具：
- model_id: `fal-ai/bytedance/seedream/v4.5/edit`
- parameters:
  - prompt: 编辑指令（用 Figure 1/2/3 引用图片）
  - image_urls: 输入图片 URL 数组
  - image_size: 输出尺寸

</details>

<details>
<summary><b>脚本方式</b></summary>

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "fal-ai/bytedance/seedream/v4.5/edit" \
  --params '{"prompt":"Change the background to a forest","image_urls":["https://..."],"image_size":"landscape_16_9"}'
```

</details>

### 轮询图片结果

图片约 1-2 分钟完成。

<details>
<summary><b>MCP 方式</b></summary>

调用 `get_task` 工具查询状态：
- 首次 30 秒后查询
- 之后每 30 秒查询一次
- 状态为 `completed` 时提取图片 URL

</details>

<details>
<summary><b>脚本方式</b></summary>

**单次查询：**
```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py query \
  --task-id "TASK_ID_HERE"
```

**自动轮询（推荐用于图片，间隔 10s，超时 180s）：**
```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py poll \
  --task-id "TASK_ID_HERE" --interval 10 --timeout 180
```

</details>

### image_size 对照表

| 视频比例 | 推荐 image_size | 说明 |
|---------|----------------|------|
| 16:9 | landscape_16_9 | 横屏 |
| 9:16 | portrait_16_9 | 竖屏 |
| 4:3 | landscape_4_3 | 横屏 |
| 3:4 | portrait_4_3 | 竖屏 |
| 1:1 | square_hd | 方形 |
| 21:9 | landscape_16_9 | 近似超宽屏 |

## Step 5: 生成专业提示词

将分镜结构和参考图整合为最终提示词：

- 用 `@image_file_1`、`@image_file_2` 等引用 image_files 数组中的图片
- 用 `@video_file_1` 等引用 video_files 数组中的视频
- 用 `@audio_file_1` 等引用 audio_files 数组中的音频
- 也兼容旧版 `@图片1`、`@视频1`、`@音频1` 语法

**引用语法示例：**

```
@image_file_1 作为角色形象参考，参考 @video_file_1 的运镜方式，配合 @audio_file_1 的配乐
```

**重要：** `image_files` 数组中第 N 个 URL 对应 `@image_file_N`，`video_files` 和 `audio_files` 分别独立编号。

## Step 6: 提交视频任务

**处理素材 URL：**
- Seedream 生成的图片：已有 URL，直接使用
- 用户提供的网络图片：直接使用
- 用户提供的本地图片：先上传获取 URL（见下方上传方式）

### 上传本地图片

<details>
<summary><b>MCP 方式</b></summary>

调用 `upload_image` 工具：image_url 或 image_data

</details>

<details>
<summary><b>脚本方式</b></summary>

```bash
# 上传网络图片
python .cursor/skills/seedance2-api/scripts/seedance_api.py upload \
  --image-url "https://example.com/image.png"

# 上传本地图片
python .cursor/skills/seedance2-api/scripts/seedance_api.py upload \
  --image-path "/path/to/local/image.png"
```

</details>

### 提交 Seedance 2.0 任务（全能模式 omni_reference）

<details>
<summary><b>MCP 方式</b></summary>

调用 `submit_task` 工具：
- model_id: `st-ai/super-seed2`
- parameters:
  - prompt: Step 5 生成的完整提示词
  - functionMode: `omni_reference`（默认，可省略）
  - image_files: 参考图片 URL 数组（最多 9 张，顺序对应 @image_file_1/2/3...）
  - video_files: 参考视频 URL 数组（最多 3 个，总时长 ≤ 15s）
  - audio_files: 参考音频 URL 数组（最多 3 个）
  - ratio: 画面比例（`16:9` / `9:16` / `1:1` / `21:9` / `4:3` / `3:4`）
  - duration: 时长整数（`4` - `15`）
  - model: `seedance_2.0_fast`（默认快速）或 `seedance_2.0`（标准质量）

</details>

<details>
<summary><b>脚本方式</b></summary>

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "st-ai/super-seed2" \
  --params '{
    "prompt": "电影级写实科幻风格，15秒，16:9...",
    "functionMode": "omni_reference",
    "image_files": ["https://img1.png", "https://img2.png"],
    "ratio": "16:9",
    "duration": 15,
    "model": "seedance_2.0_fast"
  }'
```

</details>

### 提交 Seedance 2.0 任务（首尾帧模式 first_last_frames）

<details>
<summary><b>MCP 方式</b></summary>

调用 `submit_task` 工具：
- model_id: `st-ai/super-seed2`
- parameters:
  - prompt: 视频描述提示词
  - functionMode: `first_last_frames`
  - filePaths: 图片 URL 数组（0 张=文生视频，1 张=首帧图生视频，2 张=首尾帧视频）
  - ratio: 画面比例
  - duration: 时长整数
  - model: `seedance_2.0_fast` 或 `seedance_2.0`

</details>

<details>
<summary><b>脚本方式</b></summary>

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "st-ai/super-seed2" \
  --params '{
    "prompt": "镜头从首帧缓缓过渡到尾帧，画面流畅自然",
    "functionMode": "first_last_frames",
    "filePaths": ["https://first-frame.png", "https://last-frame.png"],
    "ratio": "16:9",
    "duration": 5,
    "model": "seedance_2.0_fast"
  }'
```

</details>

## Step 7: 轮询等待视频结果

视频生成约需 10 分钟。

<details>
<summary><b>MCP 方式</b></summary>

轮询策略：
1. 提交后告知用户"视频正在生成，预计 10 分钟"
2. 首次 **60 秒**后调用 `get_task` 查询
3. 之后每 **90 秒**查询一次
4. 每次查询后向用户报告状态

</details>

<details>
<summary><b>脚本方式</b></summary>

**推荐：使用 poll 自动轮询（后台运行，间隔 30s，超时 600s）：**

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py poll \
  --task-id "TASK_ID_HERE" --interval 30 --timeout 600
```

脚本会在 stderr 打印轮询进度，完成后在 stdout 输出 JSON 结果。

**手动分次查询：**

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py query \
  --task-id "TASK_ID_HERE"
```

</details>

状态说明：
- `pending` → "排队中..."
- `processing` → "生成中..."
- `completed` → 提取视频 URL 并展示给用户
- `failed` → 告知失败原因，建议调整提示词重试

## 完整流程示例

用户说："帮我做一个宇航员在火星行走的视频"

### MCP 可用时

```
1. 收集信息 → 15秒，16:9，电影级科幻风格，无现成素材

2. 用 Seedream 4.5 生成宇航员图 + 火星场景图
   submit_task("fal-ai/bytedance/seedream/v4.5/text-to-image", {...})
   → 轮询 get_task → 获得图片 URL

3. 编写提示词 → 提交视频任务
   submit_task("st-ai/super-seed2", {...})

4. 轮询 get_task，~10分钟后获得视频 URL
```

### MCP 不可用时（脚本模式）

```
1. 收集信息 → 15秒，16:9，电影级科幻风格

2. 生成参考图：
   python scripts/seedance_api.py submit \
     --model "fal-ai/bytedance/seedream/v4.5/text-to-image" \
     --params '{"prompt":"An astronaut in white spacesuit on Mars...","image_size":"landscape_16_9"}'
   → 拿到 task_id

3. 轮询图片结果：
   python scripts/seedance_api.py poll --task-id "xxx" --interval 10 --timeout 180
   → 拿到图片 URL

4. 提交视频任务：
   python scripts/seedance_api.py submit \
     --model "st-ai/super-seed2" \
     --params '{"prompt":"...分镜提示词...","functionMode":"omni_reference","image_files":["图片URL"],"ratio":"16:9","duration":15,"model":"seedance_2.0_fast"}'
   → 拿到 task_id

5. 轮询视频结果：
   python scripts/seedance_api.py poll --task-id "xxx" --interval 30 --timeout 600
   → 拿到视频 URL
```

## 模型参数速查

### Seedream 4.5 文生图

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 图片描述 |
| image_size | string | 否 | auto_2K / auto_4K / square_hd / portrait_4_3 / portrait_16_9 / landscape_4_3 / landscape_16_9 |
| num_images | int | 否 | 1-6，默认 1 |

### Seedream 4.5 图像编辑

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 编辑指令，用 Figure 1/2/3 引用 |
| image_urls | array | 是 | 输入图片 URL 列表 |
| image_size | string | 否 | 同上 |
| num_images | int | 否 | 1-6，默认 1 |

### Seedance 2.0 视频（全能模式 omni_reference）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 分镜提示词，用 @image_file_N/@video_file_N/@audio_file_N 引用 |
| functionMode | string | 否 | `omni_reference`（默认） |
| image_files | array | 否 | 参考图片 URL 数组（最多 9 张） |
| video_files | array | 否 | 参考视频 URL 数组（最多 3 个，总时长 ≤ 15s） |
| audio_files | array | 否 | 参考音频 URL 数组（最多 3 个） |
| ratio | string | 否 | 21:9 / 16:9 / 4:3 / 1:1 / 3:4 / 9:16 |
| duration | integer | 否 | 4-15 整数，默认 5 |
| model | string | 否 | seedance_2.0_fast（默认）/ seedance_2.0 |

### Seedance 2.0 视频（首尾帧模式 first_last_frames）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 视频描述提示词 |
| functionMode | string | 是 | `first_last_frames` |
| filePaths | array | 否 | 图片 URL 数组（0张=文生视频，1张=首帧，2张=首尾帧） |
| ratio | string | 否 | 21:9 / 16:9 / 4:3 / 1:1 / 3:4 / 9:16 |
| duration | integer | 否 | 4-15 整数，默认 5 |
| model | string | 否 | seedance_2.0_fast（默认）/ seedance_2.0 |

## 工具速查

### MCP 工具

| 操作 | 工具 | 关键参数 |
|------|------|---------|
| 提交任务 | submit_task | model_id, parameters |
| 查询结果 | get_task | task_id |
| 上传图片 | upload_image | image_url 或 image_data |
| 查询余额 | get_balance | 无 |

### 脚本命令（MCP 不可用时）

| 操作 | 命令 | 说明 |
|------|------|------|
| 提交任务 | `python scripts/seedance_api.py submit --model MODEL --params '{...}'` | 返回 task_id |
| 单次查询 | `python scripts/seedance_api.py query --task-id ID` | 返回当前状态 |
| 自动轮询 | `python scripts/seedance_api.py poll --task-id ID --interval N --timeout N` | 阻塞直到完成 |
| 查询余额 | `python scripts/seedance_api.py balance` | 返回账户余额 |
| 上传图片 | `python scripts/seedance_api.py upload --image-url URL` 或 `--image-path PATH` | 返回图片 URL |

> **脚本路径说明：** 以上命令中的 `scripts/seedance_api.py` 是相对于 `.cursor/skills/seedance2-api/` 目录的路径。实际执行时使用完整路径 `.cursor/skills/seedance2-api/scripts/seedance_api.py`，或先 cd 到 skill 目录。

## Seedance 2.0 限制

- 不支持上传写实真人脸部素材
- 最多 12 个文件：图片 ≤ 9 + 视频 ≤ 3 + 音频 ≤ 3
- 视频/音频参考总时长 ≤ 15 秒
- 含视频参考会消耗更多积分

## 更多资源

详细分镜模板、完整示例和镜头词汇表见 [reference.md](reference.md)。
