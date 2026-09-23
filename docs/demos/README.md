# Claude vs Jev: long structured JSON

[Watch the video](claude-vs-jev.mp4)

The same 12 support tickets and Choice questions go to Claude Haiku 4.5 and Jev. Claude writes the JSON progressively; Jev returns the decision object in one response. The video shows 136 lines of structured JSON, large timers, and the actual arrival of Claude's stream.

| Fresh paired capture | Time to full response |
| --- | ---: |
| Jev `typesafe/jev-1.13-20260917` | 0.441 seconds |
| Claude `anthropic/claude-haiku-4.5` | 5.108 seconds |

All **12/12 category choices match**. Probability distributions and confidence values differ. The observed completion-time ratio is **11.6×** for this one synthetic example.

## What the task asks for

For each synthetic ticket, choose billing, technical, sales, or account. Each result has the same fields: `type`, `choice`, `probabilities`, and `confidence`. Both models receive identical ticket text, questions, and criteria. Claude additionally receives JSON-format instructions and an example output shape; Jev uses its native Choice API. Claude's confidence is a self-estimate, not a claim of equivalent calibration to Jev's confidence.

This is **long structured decision output**, not arbitrary JSON generation. Jev does not write free-form text. The JSON envelopes and pretty-printing are application serialization, not prose generation by Jev.

## Recording and playback

Both calls were launched concurrently from the same local Python process through OpenRouter. Each duration begins immediately before its HTTP request. The Jev timer stops after its JSON body is received and decoded; Claude's stops at the stream's completion. There is no artificial delay, reasoning-mode inflation, or replay-speed adjustment.

Claude's **152 recorded content deltas** include their arrival timestamps. The video replays those events at **1×** after a two-second intro. Jev's entire answer object appears at its measured completion time. Claude's code panel follows the newest lines while streaming and returns to the top on completion; Jev's panel is complete from arrival. Mini-maps indicate how much JSON is available. At 30 fps, visible state transitions are quantized to video frames.

Claude included a markdown code fence despite instructions to return bare JSON. Only that wrapper is stripped for parsing and display; the raw stream is retained. Before publishing, both outputs were checked for all question IDs, allowed labels, probability keys, bounded values, and probability sums. Matching categories do not establish ground-truth accuracy or identical probability estimates.

The first recording attempt failed at local JSON parsing before a capture was saved. The recorder was fixed to preserve raw outputs and tolerate the markdown wrapper, then the paired run was repeated once. The displayed run is that second attempt; it was not selected from repeated speed trials. No first-attempt timing claim is made.

## Inspect or reproduce

- [Exact requests and synthetic inputs](json-data/requests.json)
- [Complete paired capture and stream events](json-data/capture.json)
- [Unmodified Claude text and timestamps](json-data/claude-stream-raw.json)
- [Raw Jev response and elapsed time](json-data/jev-raw.json)
- [Rendering manifest and source hash](manifest.json)
- [Recorder](../../tools/record_json_demo.py)
- [Renderer](../../tools/render_demos.py)

Record a new pair using an OpenRouter key passed through the hidden-input launcher (no credentials are written to the captures):

```sh
python3 tools/with_jev_key.py --provider openrouter -- python3 tools/record_json_demo.py
```

This overwrites the local capture files and makes two paid API calls. Check the resulting measurements before publishing a newly rendered video. The frozen corpus and skill evaluator are separate and unchanged.

Render without making API calls:

```sh
python3 -m venv /tmp/jevify-demo-render
/tmp/jevify-demo-render/bin/pip install pillow imageio-ffmpeg
/tmp/jevify-demo-render/bin/python tools/render_demos.py
```

Video: 1280 × 720, 30 fps, H.264, silent. Defaults use macOS Arial and Menlo. For other systems, set `JEVIFY_DEMO_FONTS` to a directory with `Arial.ttf` and `Arial Bold.ttf`, and `JEVIFY_DEMO_MONO` to an equivalent monospace font. Rendering dependencies are separate from the skill runtime.

## Limits

One small synthetic batch, one gateway route, one machine, no warmup or statistical latency study. This demo does not prove general speed, quality, calibrated Claude confidence, production reliability, or skill conversion correctness. The Claude model comparison is separate from Claude Code's coding-agent evaluation. See the [full skill report](../../REPORT.md), including remaining failures and unopened HELD-OUT.

TypeSafe also publishes [official structured-decision, Doom, and Wikiracing demos](https://typesafe.ai/blog/introducing-system-one-models-and-jev). Those remain attributed to TypeSafe and are not represented as Jevify results.

## Minecraft community preview

`minecraft-preview.gif` is an animated preview of [Ronak Malde’s original demo](https://x.com/rronak_/status/2101544156757950697), linked to the original hosted video in the root README. It preserves the full 39.1-second clip at its published speed, resized to 560px and sampled at 8 fps for GitHub. It is a community showcase, not a Jevify conversion or an unaccelerated recording of the full Minecraft run.
