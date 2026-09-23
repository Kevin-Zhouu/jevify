# Claude versus Jev: two decision demos

[Watch/download both comparisons in one video](claude-vs-jev.mp4) · [Confident decision](01-confident-decision.mp4) · [Confidence fallback](02-confidence-fallback.mp4)

Each 18-second demo puts the original Claude path on the left and the Jev path with Claude fallback on the right. The combined MP4 is 36 seconds, 1280 × 720, 24 fps, H.264, with no audio. The GIF is a smaller README preview.

## What was recorded

These videos are **rendered data replays**, not screen recordings or new inference runs. Labels, confidence values, costs, and request latencies come directly from the successful DEV03 Codex headless conversion of the public Anthropic insurance-ticket classification example.

- Original model: `anthropic/claude-haiku-4.5`, measured through the authorized OpenRouter baseline adapter.
- Jev model: `typesafe/jev-1.13-20260917`, through OpenRouter.
- Preset confidence threshold: **0.90**.
- Source: [JEV_PARITY.json](../../eval/results/dev-03/anthropic_classification-codex-headless/original/JEV_PARITY.json).
- Method and limits: [conversion report](../../eval/results/dev-03/anthropic_classification-codex-headless/original/JEV_CONVERSION_REPORT.md).
- Exact selected rows, request IDs, raw Jev responses, source hash, and selection rule: [manifest.json](manifest.json).

The first demo selects the first accepted repository fixture. The second selects the first rejected repository fixture where Jev and Claude's raw answers differ. Both are tickets from the **same workflow**, not two independently evaluated workflows. No answers were invented or substituted. Claude is a model baseline here; this does not imply the Claude Code coding-agent evaluation passed.

## How to interpret the animation

The ticket stays visible for four seconds before both panels begin. Request durations then replay at 1× speed, with final results held for readability. The source requests were measured separately, not concurrently in a filmed race. Encoding at 24 fps quantizes visual completion times; printed millisecond values come from the original measurements.

For the fallback example, the right panel shows a **modeled serial timeline**: measured Jev time plus measured Claude time. The displayed cascade cost similarly sums both recorded costs. Neither is a new end-to-end measurement. The actual conversion's fallback control flow was separately verified using genuine response captures through its public wrapper.

The full 36-input source set had 21/22 accepted matches and 14/36 fallbacks. One accepted answer disagreed with Claude. Confidence is not correctness, agreement is not ground-truth accuracy, and selected examples are not a general speed or cost guarantee.

## Rebuild the videos

The renderer needs Python, Pillow, and imageio-ffmpeg. These are **demo development dependencies**, not skill runtime dependencies. It reads the archived results and makes no API calls.

```sh
python3 -m venv /tmp/jevify-demo-render
/tmp/jevify-demo-render/bin/pip install pillow imageio-ffmpeg
/tmp/jevify-demo-render/bin/python tools/render_demos.py
```

The default fonts are macOS Arial and Arial Bold. Elsewhere, set `JEVIFY_DEMO_FONTS` to a directory containing equivalent licensed fonts named `Arial.ttf` and `Arial Bold.ttf`.

The renderer produces both MP4s, the combined MP4, PNG stills, the GIF, and the provenance manifest. Upstream inputs retain the license in the [vendored workflow](../../corpus/anthropic_classification/).
