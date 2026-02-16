**[English](README.md)** | **中文**

# Seedance 2.0 API 使用指南

Seedance 2.0 全能模型 API 调用示例。基于 [速推AI](https://www.xskill.ai/#/v2/models?model=st-ai%2Fsuper-seed2) 平台接入字节跳动新一代 AI 视频生成模型。

## 模型简介

**Model ID:** `st-ai/super-seed2`

Seedance 2.0 是字节跳动推出的新一代 AI 视频生成模型，核心能力包括：

- **多模态混合输入** — 支持图片/视频/音频混合输入（最多 9 张图 + 3 段视频 + 3 段音频）
- **@引用语法** — 通过 `@image_file_1`、`@video_file_1`、`@audio_file_1` 精确控制每个素材的作用（也兼容旧版 `@图片1`、`@视频1`）
- **双功能模式** — 全能模式（Omni Reference）和首尾帧模式（First/Last Frames）
- **原生音画同步** — 支持音素级口型同步（8+ 种语言）
- **多镜头叙事** — 可从单条提示词生成多镜头连贯叙事
- **影院级画质** — 输出最高 2K 分辨率，时长 4-15 秒，生成约 60 秒完成

## 定价信息

| 模式 | 价格 |
|------|------|
| 基础价格 | 40 积分/次 |
| Fast 5秒（文生视频） | 50 积分 |
| Fast 5秒（含视频输入） | 100 积分 |
| 标准 5秒（含视频输入） | 200 积分 |

> 按秒计费：Fast 无视频 10/秒、含视频 20/秒；标准 无视频 20/秒、含视频 40/秒（4-15 秒）

## 前置准备

1. 前往 [速推AI](https://www.xskill.ai) 注册账号
2. 在 [API Key 页面](https://www.xskill.ai/#/v2/api-key) 创建 API Key
3. 获取积分用于调用

## API 调用

### 接口说明

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v3/tasks/create` | POST | 创建任务，返回 task_id |
| `/api/v3/tasks/query` | POST | 查询任务状态和结果 |

**Base URL:** `https://api.xskill.ai`

### 认证方式

在请求头中添加 API Key：

```
Authorization: Bearer sk-your-api-key
```

### 功能模式

Seedance 2.0 支持两种功能模式：

| 模式 | 说明 | 素材参数 |
|------|------|---------|
| `omni_reference` | **全能模式（默认）** — 多模态混合，分别传入图片/视频/音频数组 | `image_files`、`video_files`、`audio_files` |
| `first_last_frames` | **首尾帧模式** — 文/图生视频，通过首帧/尾帧图片控制 | `filePaths` |

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型 ID，固定为 `st-ai/super-seed2` |
| `params.model` | string | 否 | 速度模式：`seedance_2.0_fast`（快速，默认）/ `seedance_2.0`（标准） |
| `params.prompt` | string | 是 | 提示词。支持 `@image_file_1`、`@video_file_1`、`@audio_file_1` 引用素材（也兼容旧版 `@图片1`、`@视频1`、`@音频1`） |
| `params.functionMode` | string | 否 | 功能模式：`omni_reference`（全能模式，默认）/ `first_last_frames`（首尾帧模式） |
| `params.ratio` | string | 否 | 视频宽高比：`21:9` / `16:9` / `4:3` / `1:1` / `3:4` / `9:16` |
| `params.duration` | integer | 否 | 视频时长（秒），4-15 整数，默认 `5` |
| `params.image_files` | array | 否 | 参考图片 URL 数组（omni_reference 模式，最多 9 张）。数组中第 N 个元素对应 `@image_file_N` |
| `params.video_files` | array | 否 | 参考视频 URL 数组（omni_reference 模式，最多 3 个，总时长 ≤ 15 秒）。数组中第 N 个元素对应 `@video_file_N` |
| `params.audio_files` | array | 否 | 参考音频 URL 数组（omni_reference 模式，最多 3 个）。数组中第 N 个元素对应 `@audio_file_N` |
| `params.filePaths` | array | 否 | 图片 URL 数组（first_last_frames 模式）。0 张：文生视频；1 张：图生视频（首帧）；2 张：首尾帧视频 |

### cURL 示例

```bash
# 示例 1: 全能模式（图片 + 视频）
curl -X POST "https://api.xskill.ai/api/v3/tasks/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{
    "model": "st-ai/super-seed2",
    "params": {
      "model": "seedance_2.0_fast",
      "prompt": "@image_file_1 中的人物按照 @video_file_1 的动作和运镜风格进行表演，电影级光影",
      "functionMode": "omni_reference",
      "image_files": [
        "https://your-character-image.png"
      ],
      "video_files": [
        "https://your-reference-video.mp4"
      ],
      "ratio": "16:9",
      "duration": 5
    }
  }'

# 示例 2: 首尾帧模式
curl -X POST "https://api.xskill.ai/api/v3/tasks/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{
    "model": "st-ai/super-seed2",
    "params": {
      "model": "seedance_2.0_fast",
      "prompt": "镜头从首帧缓缓过渡到尾帧，画面流畅自然，电影级光影效果",
      "functionMode": "first_last_frames",
      "filePaths": [
        "https://your-first-frame.png",
        "https://your-last-frame.png"
      ],
      "ratio": "16:9",
      "duration": 5
    }
  }'

# 查询任务结果（使用返回的 task_id）
curl -X POST "https://api.xskill.ai/api/v3/tasks/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{"task_id": "your-task-id"}'
```

### Python 示例

```python
import requests
import time

url = "https://api.xskill.ai/api/v3/tasks/create"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-your-api-key"
}

# 全能模式：图片 + 视频
payload = {
    "model": "st-ai/super-seed2",
    "params": {
        "model": "seedance_2.0_fast",
        "prompt": "@image_file_1 中的人物按照 @video_file_1 的动作和运镜风格进行表演，电影级光影",
        "functionMode": "omni_reference",
        "image_files": [
            "https://your-character-image.png"
        ],
        "video_files": [
            "https://your-reference-video.mp4"
        ],
        "ratio": "16:9",
        "duration": 5
    }
}

# 创建任务
response = requests.post(url, json=payload, headers=headers)
result = response.json()
print("任务创建结果:", result)

# 获取 task_id
task_id = result["data"]["task_id"]

# 轮询查询任务结果
query_url = "https://api.xskill.ai/api/v3/tasks/query"
while True:
    query_response = requests.post(query_url, json={"task_id": task_id}, headers=headers)
    query_result = query_response.json()
    status = query_result["data"]["status"]
    print(f"任务状态: {status}")

    if status == "completed":
        video_url = query_result["data"]["result"]["output"]["images"][0]
        print(f"视频地址: {video_url}")
        break
    elif status == "failed":
        print("任务失败")
        break

    time.sleep(5)  # 每 5 秒查询一次
```

### JavaScript 示例

```javascript
const API_KEY = "sk-your-api-key";
const BASE_URL = "https://api.xskill.ai";

// 创建任务（全能模式）
async function createTask() {
  const response = await fetch(`${BASE_URL}/api/v3/tasks/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      model: "st-ai/super-seed2",
      params: {
        model: "seedance_2.0_fast",
        prompt: "@image_file_1 中的人物按照 @video_file_1 的动作和运镜风格进行表演，电影级光影",
        functionMode: "omni_reference",
        image_files: [
          "https://your-character-image.png"
        ],
        video_files: [
          "https://your-reference-video.mp4"
        ],
        ratio: "16:9",
        duration: 5
      }
    })
  });

  const result = await response.json();
  console.log("任务创建结果:", result);
  return result.data.task_id;
}

// 查询任务结果
async function queryTask(taskId) {
  const response = await fetch(`${BASE_URL}/api/v3/tasks/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`
    },
    body: JSON.stringify({ task_id: taskId })
  });

  return await response.json();
}

// 主流程：创建并轮询
async function main() {
  const taskId = await createTask();

  while (true) {
    const result = await queryTask(taskId);
    const status = result.data.status;
    console.log(`任务状态: ${status}`);

    if (status === "completed") {
      console.log("视频地址:", result.data.result.output.images[0]);
      break;
    } else if (status === "failed") {
      console.log("任务失败");
      break;
    }

    await new Promise(resolve => setTimeout(resolve, 5000)); // 每 5 秒查询
  }
}

main();
```

### 响应格式

**创建任务成功：**

```json
{
  "code": 200,
  "data": {
    "task_id": "task_xxx",
    "price": 10
  }
}
```

**任务查询结果：**

```json
{
  "code": 200,
  "data": {
    "status": "completed",
    "result": {
      "output": {
        "images": [
          "https://your-video-output-url.mp4"
        ]
      }
    }
  }
}
```

> **status 状态值：** `pending`（排队中）、`processing`（处理中）、`completed`（已完成）、`failed`（失败）

---

## MCP 调用

Seedance 2.0 支持通过 MCP（Model Context Protocol）在 AI 编辑器中直接调用，无需手动编写 API 代码。

### 方式一：一键安装

复制下方命令到终端执行，自动配置 MCP 环境：

**Mac / Linux：**

```bash
curl -fsSL https://api.xskill.ai/install-mcp.sh | bash -s -- YOUR_API_KEY
```

**Windows（PowerShell）：**

```powershell
irm https://api.xskill.ai/install-mcp.ps1 | iex
```

### 方式二：手动配置编辑器

#### Cursor 配置

1. 打开 Cursor 设置（`Cmd/Ctrl + ,`）
2. 搜索 "MCP" 并启用 MCP 功能
3. 在项目根目录创建 `.cursor/mcp.json` 文件
4. 粘贴以下配置：

```json
{
  "mcpServers": {
    "sutui-ai": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/mcp-client",
        "https://api.xskill.ai/api/v3/mcp-http"
      ],
      "env": {
        "SUTUI_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

#### Claude Desktop 配置

在 Claude Desktop 设置中添加相同的 MCP 服务器配置即可。

### MCP HTTP 端点

如需直接调用 MCP HTTP 接口：

```
GET https://api.xskill.ai/api/v3/mcp-http
Authorization: Bearer YOUR_API_KEY
```

### MCP 使用方式

配置完成后，在 AI 编辑器中直接对话即可使用：

> **用户：** 帮我用 st-ai/super-seed2 生成一个视频
>
> **Agent：** 好的，我来帮你调用 st-ai/super-seed2 生成视频...

**提示：**
- MCP 会自动识别模型能力并调用对应工具
- 无需手动传入参数，Agent 会智能提取
- 支持多轮对话持续优化结果

---

## MCP + Cursor Skills：AI 自动分镜创作

除了直接通过 MCP 调用 API，你还可以安装 **Cursor Skills**，让 AI Agent 自动完成从创意到成片的全流程——无需手动编写任何代码或参数。

### 什么是 Cursor Skills？

Cursor Skills 是 Cursor 编辑器中的可复用 AI 工作流模板。安装后，AI Agent 会自动识别你的意图，按照专业的分镜流程引导你完成视频创作：

```
用户创意 → 信息收集 → 分镜设计 → 生成参考图 → 构建提示词 → 提交视频任务 → 轮询结果 → 返回视频
```

### 安装 Skill

**方式一：克隆仓库**

```bash
# 克隆本仓库
git clone https://github.com/siliconflow/seedance2-api.git

# 复制 skill 到你的项目
cp -r seedance2-api/.cursor/skills/seedance-storyboard/ your-project/.cursor/skills/seedance-storyboard/
```

**方式二：手动创建**

在你的项目中创建 `.cursor/skills/seedance-storyboard/` 目录，将本仓库中的 `SKILL.md` 和 `reference.md` 放入其中。

> **前提条件：** 已安装 Cursor 编辑器，已配置 MCP（参考上方"MCP 调用"章节），速推AI 账号已有足够积分。

### 使用方式

配置完成后，在 Cursor 中直接用自然语言描述你的创意即可：

```
用户：帮我做一个宇航员在火星行走的 15 秒科幻短片

Agent 自动执行：
1. 收集信息（时长、比例、风格、素材情况）
2. 用 Seedream 4.5 生成宇航员和火星场景参考图
3. 构建专业分镜提示词（时间轴 + 镜头语言 + 声音设计）
4. 提交 Seedance 2.0 视频生成任务
5. 自动轮询并返回生成的视频
```

### 完整工作流

| 步骤 | 说明 | 使用的模型/工具 |
|------|------|----------------|
| 信息收集 | 收集时长、比例、风格、素材等 | Agent 对话引导 |
| 参考图生成 | 生成角色图、场景图、首帧/尾帧 | Seedream 4.5（文生图/图像编辑） |
| 分镜构建 | 按时间轴编写专业镜头语言 | 内置分镜模板 |
| 视频生成 | 提交最终提示词和素材 | Seedance 2.0 |
| 结果获取 | 自动轮询任务状态 | MCP get_task |

### 对话示例

```
用户：做一个咖啡品牌的 15 秒广告，高端商业风格

Agent：好的！需要确认几个信息：
  - 画面比例：推荐 16:9（横屏广告）
  - 是否有现成的产品图片？
  - 品牌名称和 slogan？

用户：16:9，没有现成图片，品牌叫 Lucky Coffee

Agent：
  1. 正在用 Seedream 4.5 生成咖啡杯特写图和品牌场景图...
  2. 图片生成完成，开始构建分镜：
     0-3秒：微距特写，咖啡液缓缓注入杯中，蒸汽升腾
     3-6秒：中景环绕，手握咖啡杯，阳光洒在桌面
     6-10秒：推镜头至咖啡豆，一粒咖啡豆飘落
     10-12秒：画面黑屏转场
     12-15秒：品牌文字渐显 "Lucky Coffee"
  3. 提交 Seedance 2.0 视频任务...
  4. 视频生成中，预计 10 分钟...
  5. 视频生成完成！[视频链接]
```

### 支持的创作场景

| 场景 | 说明 | 示例 |
|------|------|------|
| 叙事故事 | 情感短片、微电影 | "男人下班回家的温情故事" |
| 产品广告 | 品牌宣传、电商视频 | "咖啡品牌 15 秒广告" |
| 角色动作 | 武侠、科幻、舞蹈 | "武侠风格双人对打" |
| 风景旅拍 | 自然风光、城市街拍 | "日落海边漫步" |
| 视频延长 | 在已有视频基础上续拍 | "将这个视频延长 10 秒" |
| 剧情颠覆 | 修改已有视频的剧情 | "把结局改成反转" |
| 创意转场 | 多场景穿梭 | "科幻世界穿梭转场" |
| 首尾帧视频 | 控制起始和结束画面 | "日出到日落延时转场" |

> **提示：** Skill 内置了丰富的分镜模板（叙事类、产品类、动作类、风景类等）和镜头运动词汇表，Agent 会根据你的需求自动选择最合适的模板。

---

## 使用案例

### 案例 1：角色动作迁移（全能模式 — 图片+视频）

将图片中的角色按照视频的动作和运镜风格进行表演。

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "@image_file_1 中的人物按照 @video_file_1 的动作和运镜风格进行表演，电影级光影",
    "functionMode": "omni_reference",
    "image_files": ["https://your-character-image.png"],
    "video_files": ["https://your-reference-video.mp4"],
    "ratio": "16:9",
    "duration": 5
  }
}
```

### 案例 2：单图生成视频（全能模式）

从单张图片生成动态视频。

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "@image_file_1 角色在森林中缓步行走，阳光透过树叶洒下斑驳光影，微风吹动发丝",
    "functionMode": "omni_reference",
    "image_files": ["https://your-character-image.png"],
    "ratio": "9:16",
    "duration": 8
  }
}
```

### 案例 3：首尾帧视频

生成从首帧过渡到尾帧的视频。

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "镜头从首帧缓缓过渡到尾帧，画面流畅自然，电影级光影效果",
    "functionMode": "first_last_frames",
    "filePaths": [
      "https://your-first-frame.png",
      "https://your-last-frame.png"
    ],
    "ratio": "16:9",
    "duration": 5
  }
}
```

### 案例 4：音频驱动口型（全能模式 — 图片+音频）

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "@image_file_1 角色说话，配合 @audio_file_1 的内容，表情自然生动",
    "functionMode": "omni_reference",
    "image_files": ["https://your-character-image.png"],
    "audio_files": ["https://your-audio-file.mp3"],
    "ratio": "16:9",
    "duration": 5
  }
}
```

### 更多玩法

| 场景 | prompt 示例 | 功能模式 | 输入素材 |
|------|-------------|---------|----------|
| 角色动作迁移 | `@image_file_1 中的人物按照 @video_file_1 的动作进行表演` | omni_reference | image_files + video_files |
| 单图动态化 | `@image_file_1 角色缓缓转头微笑，微风吹动头发` | omni_reference | image_files |
| 多角色互动 | `@image_file_1 和 @image_file_2 两个角色面对面交谈` | omni_reference | image_files |
| 音频驱动口型 | `@image_file_1 角色说话，配合 @audio_file_1 的内容` | omni_reference | image_files + audio_files |
| 场景转换 | `从 @image_file_1 的场景平滑过渡到 @image_file_2 的场景` | omni_reference | image_files |
| 首尾帧视频 | `镜头从首帧缓缓过渡到尾帧` | first_last_frames | filePaths |
| 纯文本生视频 | `日落海边，波浪轻轻拍打沙滩` | first_last_frames | （无） |

---

## 相关链接

- [速推AI 官网](https://www.xskill.ai)
- [Seedance 2.0 模型页面](https://www.xskill.ai/#/v2/models?model=st-ai%2Fsuper-seed2)
- [API Key 管理](https://www.xskill.ai/#/v2/api-key)
- [任务列表](https://www.xskill.ai/#/v2/tasks)

## License

MIT
