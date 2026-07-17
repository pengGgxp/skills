---
name: image2-api-generator
description: Generate raster images by calling an OpenAI-compatible images API directly with the fixed model gpt-image-2. Use when Codex needs to create an image from a text prompt, save API-generated image bytes or URL results locally, or use a custom image API configured through a .env file instead of the built-in image generation tool.
---

# Image2 API Generator

Generate one image from a text prompt with the bundled dependency-free Python CLI. Call the configured API directly at `<IMAGE_BASE_URL>/images/generations` and always use the model `gpt-image-2`.

## Configure

Use the skill-local `.env` file by default:

```dotenv
IMAGE_API_KEY=<secret>
IMAGE_BASE_URL=https://provider.example/v1
```

Keep `.env` private. Never print, quote, copy into source code, or include the API key in an answer. The CLI also loads a `.env` in the current working directory after the skill-local file, and accepts `--env-file` for an explicit location.

## Generate

Run:

```powershell
python "<skill-root>\scripts\generate_image.py" --prompt "A concise image prompt" --out "output\imagegen\result.png"
```

Use `--size 1024x1024` by default. Add `--quality <value>` or `--output-format png|jpeg|webp` only when the configured provider supports those OpenAI-compatible request fields. Use `--overwrite` only when the user explicitly requests replacement.

The CLI accepts API responses containing either `data[0].b64_json` or `data[0].url`. It downloads URL results without forwarding the API key to the download host.

## Workflow

1. Turn the user's request into a concise production prompt without changing explicit constraints or exact text.
2. Choose a descriptive output path in the current workspace. Prefer `output/imagegen/` when the user did not specify one.
3. Verify only that `IMAGE_API_KEY` and `IMAGE_BASE_URL` are non-empty; do not reveal their values.
4. Run `scripts/generate_image.py` and capture the final path printed by the CLI.
5. Inspect the saved image before reporting success. Check subject, composition, text accuracy, and explicit constraints.
6. Report the saved path and the final prompt. On API failure, report the sanitized error and do not expose credentials.

Do not silently change the model, endpoint family, or provider. The model is fixed to `gpt-image-2`.
