---
name: seedance2-api
description: End-to-end AI video generation from storyboard concept to final output. Supports both MCP and standalone Python script modes; automatically detects availability and switches gracefully if MCP is unavailable. Generates reference images with Seedream 4.5 (text-to-image and image editing), then submits video tasks to Seedance 2.0 with configurable aspect ratios and durations.
license: MIT
---

# Seedance 2.0 Storyboard & Video Generation

End-to-end workflow from concept to final video: Storyboard → Reference images → Submit video task → Get results.

## Step 0: Determine Execution Mode (MCP or Script)

**Check MCP availability first:**

- Check `xskill-ai` MCP service status (read `mcps/user-xskill-ai/STATUS.md`)
- If MCP is available → use `submit_task` / `get_task` and other MCP tools
- If MCP is unavailable or returns errors → switch to Script Mode

**Script mode prerequisites:**

- Verify `XSKILL_API_KEY` environment variable is set (run `echo $XSKILL_API_KEY | head -c 10`)
- If not set, prompt the user:
  ```
  export XSKILL_API_KEY=sk-your-api-key
  ```
  Get your API Key: https://www.xskill.ai/#/v2/api-keys
- Verify `requests` is installed (`pip install requests`)

**Script path:** Located under this skill's directory at `scripts/seedance_api.py`:

```
# Find via Glob tool
glob: .cursor/skills/seedance2-api/scripts/seedance_api.py
```

In the following steps, each API call provides both MCP method and Script method. Choose one based on the Step 0 result.

## Step 1: Understand the User's Idea

Collect the following information (proactively ask if anything is missing):

- **Story concept**: one-sentence summary of the video
- **Duration**: 4–15 seconds
- **Aspect ratio**: 16:9 / 9:16 / 1:1 / 21:9 / 4:3 / 3:4
- **Visual style**: realistic / animation / ink wash / sci-fi / cyberpunk, etc.
- **Assets**: existing images/videos/audio, or need AI generation
- **Function mode**: first & last frame control (`first_last_frames`) or default omni mode (`omni_reference`)

## Step 2: Deep Dive (5 Dimensions)

Guide the user through each dimension for richer detail:

- **Content** – Who is the subject? What are they doing? Where?
- **Visuals** – Lighting, color palette, texture, mood
- **Camera** – Push in / pull out / pan / tilt / track / orbit / crane
- **Motion** – Subject actions and pacing
- **Audio** – Music style, sound effects, dialogue

## Step 3: Build Storyboard Structure

Break down shots along the timeline using this formula:

```
[Style] _____ style, _____ seconds, _____ ratio, _____ mood

0-Xs: [Camera movement] + [Visual content] + [Action description]
X-Ys: [Camera movement] + [Visual content] + [Action description]
...

[Audio] _____ music + _____ SFX + _____ dialogue
[References] @image_file_1 _____, @video_file_1 _____
```

See `reference.md` for detailed templates and examples.

## Step 4: Generate Reference Images (If Needed)

If the user has no existing assets, use Seedream 4.5 to generate character art, scenes, first/last frames, etc.

### Text-to-Image

Call `submit_task` tool:

- `model_id`: `fal-ai/bytedance/seedream/v4.5/text-to-image`
- `parameters`:
  - `prompt`: detailed image description (English works best)
  - `image_size`: choose based on video aspect ratio
  - `num_images`: number needed (1–6)

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "fal-ai/bytedance/seedream/v4.5/text-to-image" \
  --params '{"prompt":"An astronaut in a white spacesuit...","image_size":"landscape_16_9","num_images":1}'
```

### Image Editing (Modify Existing Images)

Call `submit_task` tool:

- `model_id`: `fal-ai/bytedance/seedream/v4.5/edit`
- `parameters`:
  - `prompt`: editing instructions (use Figure 1/2/3 to reference images)
  - `image_urls`: array of input image URLs
  - `image_size`: output size

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "fal-ai/bytedance/seedream/v4.5/edit" \
  --params '{"prompt":"Change the background to a forest","image_urls":["https://..."],"image_size":"landscape_16_9"}'
```

### Poll Image Results

Images typically complete in 1–2 minutes.

Call `get_task` tool to check status:

- First query after 30 seconds
- Then every 30 seconds
- Extract image URL when status is `completed`

Single query:

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py query \
  --task-id "TASK_ID_HERE"
```

Auto-poll (recommended for images, interval 10s, timeout 180s):

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py poll \
  --task-id "TASK_ID_HERE" --interval 10 --timeout 180
```

### `image_size` Reference

| Aspect Ratio | Recommended `image_size` | Note |
|---|---|---|
| 16:9 | `landscape_16_9` | Landscape |
| 9:16 | `portrait_16_9` | Portrait |
| 4:3 | `landscape_4_3` | Landscape |
| 3:4 | `portrait_4_3` | Portrait |
| 1:1 | `square_hd` | Square |
| 21:9 | `landscape_16_9` | Approximate ultrawide |

## Step 5: Compose the Final Prompt

Merge the storyboard structure and reference images into the final prompt:

- Use `@image_file_1`, `@image_file_2`, etc. to reference images in the `image_files` array
- Use `@video_file_1`, etc. to reference videos in the `video_files` array
- Use `@audio_file_1`, etc. to reference audio in the `audio_files` array

Reference syntax example:

```
@image_file_1 as character reference, follow @video_file_1 camera movement, with @audio_file_1 as background music
```

**Important:** The Nth URL in `image_files` maps to `@image_file_N`. `video_files` and `audio_files` are independently numbered.

## Step 6: Submit Video Task

**Handle asset URLs:**

- Seedream-generated images: URL already available, use directly
- User-provided web images: use directly
- User-provided local images: upload first to get URL (see upload methods below)

### Upload Local Images

Call `upload_image` tool: `image_url` or `image_data`

```bash
# Upload from URL
python .cursor/skills/seedance2-api/scripts/seedance_api.py upload \
  --image-url "https://example.com/image.png"

# Upload local file
python .cursor/skills/seedance2-api/scripts/seedance_api.py upload \
  --image-path "/path/to/local/image.png"
```

### Submit Seedance 2.0 Task (Omni Reference Mode)

Call `submit_task` tool:

- `model_id`: `st-ai/super-seed2`
- `parameters`:
  - `prompt`: the full prompt from Step 5
  - `functionMode`: `omni_reference` (default, can be omitted)
  - `image_files`: reference image URL array (up to 9, order matches `@image_file_1/2/3...`)
  - `video_files`: reference video URL array (up to 3, total duration ≤ 15s)
  - `audio_files`: reference audio URL array (up to 3)
  - `ratio`: aspect ratio (`16:9` / `9:16` / `1:1` / `21:9` / `4:3` / `3:4`)
  - `duration`: integer length (4–15)
  - `model`: `seedance_2.0_fast` (default, faster) or `seedance_2.0` (standard quality)

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "st-ai/super-seed2" \
  --params '{
    "prompt": "Cinematic realistic sci-fi style, 15 seconds, 16:9...",
    "functionMode": "omni_reference",
    "image_files": ["https://img1.png", "https://img2.png"],
    "ratio": "16:9",
    "duration": 15,
    "model": "seedance_2.0_fast"
  }'
```

### Submit Seedance 2.0 Task (First & Last Frames Mode)

Call `submit_task` tool:

- `model_id`: `st-ai/super-seed2`
- `parameters`:
  - `prompt`: video description prompt
  - `functionMode`: `first_last_frames`
  - `filePaths`: image URL array (0 = text-to-video, 1 = first frame, 2 = first & last frames)
  - `ratio`: aspect ratio
  - `duration`: integer length
  - `model`: `seedance_2.0_fast` or `seedance_2.0`

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "st-ai/super-seed2" \
  --params '{
    "prompt": "Camera smoothly transitions from first frame to last frame, fluid motion",
    "functionMode": "first_last_frames",
    "filePaths": ["https://first-frame.png", "https://last-frame.png"],
    "ratio": "16:9",
    "duration": 5,
    "model": "seedance_2.0_fast"
  }'
```

## Step 7: Poll for Video Results

Video generation takes approximately 10 minutes.

**Polling strategy:**

- After submission, inform the user: "Video is generating, estimated ~10 minutes"
- First query after 60 seconds via `get_task`
- Then every 90 seconds
- Report status to the user after each query

Recommended: auto-poll (runs in foreground, interval 30s, timeout 600s):

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py poll \
  --task-id "TASK_ID_HERE" --interval 30 --timeout 600
```

Progress is printed to stderr; final JSON result is printed to stdout when complete.

Manual single query:

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py query \
  --task-id "TASK_ID_HERE"
```

**Status reference:**

- `pending` → "Queued..."
- `processing` → "Generating..."
- `completed` → Extract the video URL and present to the user
- `failed` → Report the error; suggest adjusting the prompt and retrying

## Full Workflow Example

User says: *"Make a video of an astronaut walking on Mars"*

### When MCP Is Available

```
1. Gather info → 15s, 16:9, cinematic sci-fi style, no existing assets

2. Generate astronaut + Mars scene images with Seedream 4.5
   submit_task("fal-ai/bytedance/seedream/v4.5/text-to-image", {...})
   → poll get_task → get image URLs

3. Compose prompt → submit video task
   submit_task("st-ai/super-seed2", {...})

4. Poll get_task, ~10 min later → get video URL
```

### When MCP Is Unavailable (Script Mode)

```
1. Gather info → 15s, 16:9, cinematic sci-fi style

2. Generate reference images:
   python scripts/seedance_api.py submit \
     --model "fal-ai/bytedance/seedream/v4.5/text-to-image" \
     --params '{"prompt":"An astronaut in white spacesuit on Mars...","image_size":"landscape_16_9"}'
   → get task_id

3. Poll for image results:
   python scripts/seedance_api.py poll --task-id "xxx" --interval 10 --timeout 180
   → get image URL

4. Submit video task:
   python scripts/seedance_api.py submit \
     --model "st-ai/super-seed2" \
     --params '{"prompt":"...storyboard prompt...","functionMode":"omni_reference","image_files":["IMAGE_URL"],"ratio":"16:9","duration":15,"model":"seedance_2.0_fast"}'
   → get task_id

5. Poll for video results:
   python scripts/seedance_api.py poll --task-id "xxx" --interval 30 --timeout 600
   → get video URL
```

## Model Parameters Quick Reference

### Seedream 4.5 Text-to-Image

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | Yes | Image description |
| `image_size` | string | No | `auto_2K` / `auto_4K` / `square_hd` / `portrait_4_3` / `portrait_16_9` / `landscape_4_3` / `landscape_16_9` |
| `num_images` | int | No | 1–6, default 1 |

### Seedream 4.5 Image Editing

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | Yes | Editing instructions, reference images as Figure 1/2/3 |
| `image_urls` | array | Yes | Input image URL list |
| `image_size` | string | No | Same as above |
| `num_images` | int | No | 1–6, default 1 |

### Seedance 2.0 Video (Omni Reference Mode)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | Yes | Storyboard prompt, use `@image_file_N` / `@video_file_N` / `@audio_file_N` |
| `functionMode` | string | No | `omni_reference` (default) |
| `image_files` | array | No | Reference image URL array (up to 9) |
| `video_files` | array | No | Reference video URL array (up to 3, total ≤ 15s) |
| `audio_files` | array | No | Reference audio URL array (up to 3) |
| `ratio` | string | No | `21:9` / `16:9` / `4:3` / `1:1` / `3:4` / `9:16` |
| `duration` | integer | No | 4–15, default 5 |
| `model` | string | No | `seedance_2.0_fast` (default) / `seedance_2.0` |

### Seedance 2.0 Video (First & Last Frames Mode)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `prompt` | string | Yes | Video description prompt |
| `functionMode` | string | Yes | `first_last_frames` |
| `filePaths` | array | No | Image URL array (0 = text-to-video, 1 = first frame, 2 = first & last) |
| `ratio` | string | No | `21:9` / `16:9` / `4:3` / `1:1` / `3:4` / `9:16` |
| `duration` | integer | No | 4–15, default 5 |
| `model` | string | No | `seedance_2.0_fast` (default) / `seedance_2.0` |

## Tools Quick Reference

### MCP Tools

| Action | Tool | Key Parameters |
|---|---|---|
| Submit task | `submit_task` | `model_id`, `parameters` |
| Query result | `get_task` | `task_id` |
| Upload image | `upload_image` | `image_url` or `image_data` |
| Check balance | `get_balance` | (none) |

### Script Commands (When MCP Is Unavailable)

| Action | Command | Description |
|---|---|---|
| Submit task | `python scripts/seedance_api.py submit --model MODEL --params '{...}'` | Returns `task_id` |
| Single query | `python scripts/seedance_api.py query --task-id ID` | Returns current status |
| Auto-poll | `python scripts/seedance_api.py poll --task-id ID --interval N --timeout N` | Blocks until done |
| Check balance | `python scripts/seedance_api.py balance` | Returns account balance |
| Upload image | `python scripts/seedance_api.py upload --image-url URL or --image-path PATH` | Returns image URL |

**Script path note:** The `scripts/seedance_api.py` path above is relative to `.cursor/skills/seedance2-api/`. Use the full path `.cursor/skills/seedance2-api/scripts/seedance_api.py` when executing, or `cd` into the skill directory first.

## Seedance 2.0 Limitations

- Realistic human face uploads are not supported
- Maximum 12 files: images ≤ 9 + videos ≤ 3 + audio ≤ 3
- Total video/audio reference duration ≤ 15 seconds
- Video references consume more credits

## More Resources

See `reference.md` for detailed storyboard templates, full examples, and camera movement glossary.
