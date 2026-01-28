---
name: openai-image-generation
description: Generate images from text prompts by calling the OpenAI Images API (gpt-image-1 by default) and saving the resulting files to the current working directory. Use this when the user asks to create, render, or generate images (mockups, diagrams, icons, banners, marketing visuals, etc.).
metadata:
  author: Chris + Copilot (template skill)
  version: "1.0.0"
license: MIT
compatibility: Requires outbound HTTPS access to api.openai.com and an OPENAI_API_KEY environment variable. Uses Python 3.10+ or PowerShell 7+ helper scripts.
---

# OpenAI Image Generation Skill (Copilot CLI)

This skill enables Copilot CLI to generate images by calling the OpenAI **Images API** and saving the results into the **current directory**.

## When to use this skill

Use this skill when the user asks to:
- generate an image from a text description
- create a diagram, icon, logo concept, banner, mockup, UI concept, marketing visual
- iterate on an image prompt with variations

## Security & secrets

- **Never** hardcode secrets.
- Read the API key from environment variables only:
  - `OPENAI_API_KEY` (required)
  - `OPENAI_BASE_URL` (optional; defaults to `https://api.openai.com`)
- Do not print the full key in logs. If you must confirm, print only the last 4 characters.

## Defaults

If the user doesn't specify:
- model: `gpt-image-1`
- size: `auto` (or `1024x1024` if needed for compatibility)
- number of images: `1`
- output format: `png`
- output naming: `generated-<timestamp>-<index>.png`

## Workflow

1) Gather minimal requirements
- Ask only if necessary: aspect ratio, style, and target use (social banner vs icon vs photo).
- If unclear, assume: modern, clean style; 1 image; square format.

2) Write an API-ready prompt
- Include subject, setting, style, composition, lighting, and constraints.
- Avoid ambiguous references like “make it nice”.

3) Generate the image via script (preferred)
- Prefer the helper scripts in `scripts/`:
  - `python3 scripts/generate_image.py --prompt "..."`
  - `pwsh scripts/generate_image.ps1 -Prompt "..."`

4) Save outputs to the current directory
- Return the filenames and suggest 2–4 prompt tweaks.

## Helper scripts

### Python (recommended)
Examples:
- `python3 scripts/generate_image.py --prompt "Minimalist cloud icon, flat vector, blue and white"`
- `python3 scripts/generate_image.py --prompt "Wide LinkedIn banner, abstract AI network pattern, modern professional" --size 1536x1024`

### PowerShell
Examples:
- `pwsh scripts/generate_image.ps1 -Prompt "3D render of a modern smart home rack, studio lighting" -Size 1024x1024`

## Output format (what you should respond with)

When you complete an image request, respond with:

1) Final prompt (exact string sent)
2) Command executed (Python or PowerShell)
3) Saved files (relative paths)
4) Suggested prompt variations (2–4 bullets)

## Policy guardrails (practical)

If user requests:
- copyrighted characters/logos/brand marks: warn about IP and offer an original alternative
- disallowed sexual content, violence, or illegal activity: refuse and offer safe alternatives
