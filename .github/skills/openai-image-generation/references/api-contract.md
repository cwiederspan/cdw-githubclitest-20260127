# API Contract (OpenAI Images API)

This skill uses the OpenAI Images API endpoint:

- `POST https://api.openai.com/v1/images`

The helper scripts send a JSON payload with:
- `model` (default: `gpt-image-1`)
- `prompt` (required)
- `size` (default: `auto`)
- `n` (default: `1`)
- optional: `quality`, `style`

The response is expected to contain:
- `data`: array of images

For `gpt-image-*` models, images are returned as base64, typically in `data[i].b64_json`.
For `dall-e-3`, images may be returned as `url` or `b64_json` depending on `response_format`.

See OpenAI docs for current parameters and limits.
