# Prove the code that will ship

Before writing a parity script, put this short wiring record in the conversion plan (after approval): the original callable/request builder, the converted public callable, the decisions evaluator/gate, and how the validation process imports or loads each. List the transport adaptation and authorization. These must be actual source symbols, not newly written substitutes.

## One policy, one inference per row

- All Jev model IDs, questions, criteria and thresholds remain in the single decisions module. Validation code imports that module. Do not copy the policy into a Python script for a TypeScript project, duplicate a raw Jev HTTP client, or import a function and then bypass it. Use the project's loader/compiler or a small bridge that executes the actual module.
- Run the actual decisions evaluator once per input, capture its sanitized real response, and replay that same response through the actual public wrapper/gate while counting fallback calls. Alternatively capture the response while the actual wrapper executes live. The row's raw answer, confidence and fallback result must come from that ONE inference. A second simultaneous Jev call can give a different result and cannot establish the first call's gate behavior.
- Assert the wrapper returns the accepted Jev result or the actual original result, with zero/one fallback calls respectively. Also assert the unchanged downstream fields, diagnostics, return types and exception identity. Do not substitute the fallback answer for the raw Jev answer in the parity row.
- Save the real response body or enough sanitized evidence to reproduce parsing, model, request ID, probabilities, usage and cost. Never save authorization headers.

## Execute the original path

Preserve the original callable, or load its pre-conversion source from git into the validation process. Assert source/AST identity (allowing only a function rename), or capture the request from the unchanged source and retain an equality assertion for all original request options and parsing. Execute its actual prompt builder and parser for every case.

When a baseline gateway route is authorized, adapt only transport/authentication and the same model's provider namespace. Do not manually reconstruct the prompt, add a new system message, alter the output schema, remove prefill/stop settings, or replace the SDK parser with new parsing. For a top-level SDK example, load the original entrypoint with a recording SDK boundary to obtain its real options, then call the real SDK with those options and a gateway transport. Replace only the fixture input when collecting more cases. Record any dependency-version or gateway differences as limitations.

A hand-written classifier that happens to use the same model is a different baseline. If executing/capturing the original is blocked, report parity as incomplete; do not present a proxy comparison as proof.

## Execute four distinct failure branches

Use the actual public wrapper, a counting fallback sentinel, and transport injection:

1. Low confidence: replay a genuinely captured response with the gate forced to reject, or change only its confidence as an explicitly labeled injected fault. Assert the actual fallback call count and return value. A pure predicate assertion alone does not establish wrapper fallback.
2. Generic error: inject a transport exception and assert exactly one original call.
3. Timeout: inject the transport's timeout/abort exception (or exercise its real timer) and assert exactly one original call.
4. Rate limit: inject an actual HTTP **429** response/error at the transport boundary and assert exactly one original call. A 401 auth error or a generic error whose message contains “429” is NOT a rate-limit test.

Never invent an HTTP-200 Jev answer, usage, probability distribution, or request ID. Accepted-path tests replay genuine live responses. Mutation of a captured response is fault injection, not measured inference, and must be labeled separately. No-key runs may test errors and predicates, but cannot claim accepted-path Jev verification without a genuine capture.

Run the assertions; a boolean in JSON is not evidence. Retain the script and execution output. In the report, distinguish passed, failed, skipped and incomplete checks.

## Review before declaring success

Read the entire validation script beside the decisions module. Search executable validation files for copied Jev model literals, questions, criteria, thresholds, duplicate evaluators and manually written baseline prompts. Replace them with calls/imports/source capture. Verify the report's selected threshold is exactly the deployed value; confirmation did not influence its choice; every fault flag has its own executed assertion; prices are provider-reported or sourced; and the artifact checker passes. Do not conceal a failed confirmation or retune against it without collecting fresh confirmation evidence.
