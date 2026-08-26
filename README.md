# Seedance 2.0 API

> Out-of-the-box Seedance 2.0 API skill — just one API key to generate AI videos.

## Install

```bash
npx skills add https://github.com/hexiaochun/seedance2-api --skill seedance2-api
```

For Claude Code, Cursor, Codex, Gemini CLI, and other compatible agents.

## Skills in this package

| Skill | Description |
|---|---|
| `seedance2-api` | Core Seedance 2.0 video generation — text-to-video, image-to-video, multi-scene storyboards |
| `seedance-storyboard` | Storyboard generation from natural-language prompts |
| `publish-to-marketplaces` | Publish generated videos to external marketplaces |

## Usage

Once installed, simply ask your AI agent to generate a video:

> *"Generate a 5-second video of a cat walking through a city at sunset."*

The skill handles the API call, polling for completion, and returning the
video URL.

## Configuration

Set your Seedance 2.0 API key as an environment variable:

```bash
export SEEDANCE_API_KEY="your-api-key-here"
```

An optional Atlas Cloud provider is also included for direct text-to-video and
image-to-video generation. Set `ATLASCLOUD_API_KEY` and use
`.cursor/skills/seedance2-api/scripts/atlas_seedance.py`; the existing provider
remains the default. See the skill instructions for submit and poll examples.

## License

MIT
