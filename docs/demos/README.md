# Claude vs Jev

[Watch the 20-second comparison](claude-vs-jev.mp4)

Two minimal side-by-side scenes: **route a ticket**, then **clear a six-ticket inbox**. Both show Claude Haiku 4.5 on the left and Jev 1.13 on the right, with large timers and visible completion states.

| Scene | Video | What it shows |
| --- | --- | --- |
| Route one ticket | [8 seconds](01-ticket-race.mp4) | A billing question, with the same category returned by both models |
| Clear the inbox | [12 seconds](02-inbox-race.mp4) | Six different categories, with tickets completing at their recorded request durations |

## Data, not invented speed

These are visual replays of previously recorded live requests. No new calls were made. Timers run at **1×** after a two-second introduction; completed results stay visible for readability. The source calls were measured separately, not filmed simultaneously.

- Claude: `anthropic/claude-haiku-4.5` through the authorized OpenRouter baseline adapter.
- Jev: `typesafe/jev-1.13-20260917` through OpenRouter.
- Source: [archived JEV_PARITY.json](../../eval/results/dev-03/anthropic_classification-codex-headless/original/JEV_PARITY.json).
- Exact selected rows, full inputs, raw responses, request IDs, source hash, and total durations: [manifest.json](manifest.json).
- Original validation method: [conversion report](../../eval/results/dev-03/anthropic_classification-codex-headless/original/JEV_CONVERSION_REPORT.md).

The queue selects the **first accepted, matching repository fixture for each of the first six distinct categories**, in source order. The single-ticket scene uses the billing-inquiry member. Selection is intended to illustrate speed on successful decisions, not to estimate overall accuracy or average savings. The billing ticket is a particularly favorable latency example; it is not the median request.

The queue animation assumes **one request in flight per model**. Queue totals are sums of the separately measured durations, not live batch throughput or a concurrency benchmark. The shortened ticket previews are human-written display captions; the models received the full original input strings retained in the manifest. All final categories are actual recorded answers.

The complete source set had **21/22 accepted matches and 14/36 fallbacks** at a preset 0.90 threshold. One accepted answer disagreed with Claude. The selected scenes do not show those disagreements or fallbacks. Agreement is not ground-truth accuracy, and these clips do not establish a production speed guarantee.

The Claude **model baseline** here is separate from the Claude Code **coding-agent evaluation**, which still has known failures. See [the full report](../../REPORT.md).

## Official Jev demos

TypeSafe's [launch article](https://typesafe.ai/blog/introducing-system-one-models-and-jev) includes a structured-decision comparison, Doom, and Wikiracing. Its structured-decision comparison uses GPT-5.6 Terra, so we link it with its original attribution rather than relabeling it as Claude. The Doom agent receives structured textual state, not game images. These are TypeSafe's demos, not Jevify conversion results.

## Rebuild

Outputs: two MP4s, the combined MP4, PNG stills, a README GIF, and the provenance manifest. Video: 1280 × 720, 30 fps, H.264, silent. The preview GIF uses 10 fps.

```sh
python3 -m venv /tmp/jevify-demo-render
/tmp/jevify-demo-render/bin/pip install pillow imageio-ffmpeg
/tmp/jevify-demo-render/bin/python tools/render_demos.py
```

The default fonts are macOS Arial and Arial Bold. Elsewhere, set `JEVIFY_DEMO_FONTS` to a directory containing equivalent licensed fonts named `Arial.ttf` and `Arial Bold.ttf`. Rendering dependencies are separate from skill runtime dependencies. The renderer makes no API calls. Upstream inputs retain the [vendored workflow license](../../corpus/anthropic_classification/LICENSE.upstream).
