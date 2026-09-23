# Jev conversion plan

No good Jev opportunities here. All three sites produce displayed text.

Source revision: `dcb356deb748674782849bfd635f53e59688e275` on `main`.
Output mode: branch, `jev-convert/evaluation`.
Output repository: `/Users/bigsoup/Downloads/Jev Converter/eval/runs/dev-02/openai_demo-codex-interactive/original`.
The inactive clone_path is ignored; no clone is created.

## Approval resolution

The user's only approved action is fallback for pure DECISION sites with enumerated outputs, preserving all externally observable fields. This predicate matches zero sites. All other conversion options are declined. No code, dependency, environment or provider changes are selected. The generation sites remain unchanged as explicitly required by the approval scope. Prior recommendations are recorded below, not treated as permission for additional work.

| Original site | Provider | Classification / fit | Downstream and reason | Option, benefit and risk |
| --- | --- | --- | --- | --- |
| workflow.py:10 | OpenAI SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | Prints completion.choices[0].message.content at workflow.py:19. The prompt requests generated text, not an enumerated decision. | leave; primitive none. Preserve the complete standard request and printed response. No cost or latency change; no speculative savings. Existing generation behavior retained; Jev substitution would alter the public contract. |
| workflow.py:23 | OpenAI SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | Iterates streamed chunks, skips empty choices, prints delta content at workflow.py:33–38. Python advice/code requires free-form generation and observable streaming behavior. | leave; primitive none. Preserve streaming, empty-choice handling and output exactly. No cost or latency change; no speculative savings. Existing generation behavior retained; Jev substitution would alter the public contract. |
| workflow.py:42 | OpenAI SDK / OpenAI / gpt-5.5 | GENERATION / NOT A FIT | Parses raw response at workflow.py:51; prints response.request_id and generated content at lines 52–53. Requires generated text and truthful transport request-ID diagnostics. | leave; primitive none. Preserve raw-response parsing, request ID and generated content. No cost or latency change; no speculative savings. Existing generation behavior retained; Jev substitution would alter the public contract. |

## Inventory and preflight

One shared OpenAI client at workflow.py:6 serves these three calls; no additional application wrappers or decision consumers were found. All inputs are short hardcoded text. No external-input mitigation exists or is necessary for these fixtures; this is not an adversarial robustness claim.

Read-only preflight passed: clean repository, valid unused requested branch, git available, OPENROUTER_API_KEY present (value neither printed nor saved). Setup uses OpenRouter and the requested Jev pin `typesafe/jev-1.13-20260917`, conservative risk. Neither is added to production because no sites qualify. Explicit conversational setup and approval govern; the config was not read.

## Validation plan

Run the user-provided independent behavior smoke with Python 3.14 against the output repository. Compare workflow.py byte-for-byte with the source revision. Run the skill artifact checker. No project test command exists. No converted sites means no live parity calls, thresholds or new fallback fault tests are applicable. Authorized isolated baseline routing is unnecessary and unused.
