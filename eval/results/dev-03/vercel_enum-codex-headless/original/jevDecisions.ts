// Policy and metadata adapter for the fixed, trusted movie-plot example.
export const MODEL = 'typesafe/jev-1.13-20260917';
export const ORIGINAL_MODEL = 'gpt-4o-mini';
export const THRESHOLD = 0.9; // Provisional; never remove the original fallback.
export const MAX_STATE_BYTES = 8000;
export const TIMEOUT_MS = 5000;
export const QUESTIONS = {
  genre: {
    type: 'choice',
    instructions: 'Classify the genre of the movie plot in `plot`. Select the best matching genre.',
    criteria: { action: null, comedy: null, drama: null, horror: null, 'sci-fi': null },
  },
};

type MovieResult = {
  object: string;
  usage: { promptTokens: number; completionTokens: number; totalTokens: number };
  finishReason: string;
};
type Transport = typeof fetch;
const record = (v: unknown): v is Record<string, any> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);
const finite = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);
const unit = (v: unknown): v is number => finite(v) && v >= 0 && v <= 1;
const tokens = (v: unknown): v is number => finite(v) && Number.isSafeInteger(v) && v >= 0;

export function confidenceAccepted(confidence: unknown) {
  return unit(confidence) && confidence >= THRESHOLD;
}

export function parseDecision(raw: unknown): { result: MovieResult; confidence: number } {
  if (!record(raw) || raw.model !== MODEL || !record(raw.answers) ||
      !record(raw.answers.genre) || !record(raw.usage)) throw new Error('malformed');
  const a = raw.answers.genre;
  const labels = Object.keys(QUESTIONS.genre.criteria);
  if (a.type !== 'choice' || typeof a.choice !== 'string' || !labels.includes(a.choice) ||
      !unit(a.confidence) || !record(a.probabilities) ||
      Object.keys(a.probabilities).length !== labels.length ||
      !labels.every(k => unit(a.probabilities[k])) ||
      Math.abs(labels.reduce((s, k) => s + a.probabilities[k], 0) - 1) > 0.001 ||
      !labels.every(k => a.probabilities[k] <= a.probabilities[a.choice]) ||
      !tokens(raw.usage.input_tokens) || !tokens(raw.usage.output_tokens) ||
      !tokens(raw.usage.input_tokens + raw.usage.output_tokens)) throw new Error('malformed');
  return {
    confidence: a.confidence,
    result: {
      object: a.choice,
      usage: {
        promptTokens: raw.usage.input_tokens,
        completionTokens: raw.usage.output_tokens,
        totalTokens: raw.usage.input_tokens + raw.usage.output_tokens,
      },
      // Adapter-owned completed-decision status, not a native token stop reason.
      finishReason: 'stop',
    },
  };
}

export async function evaluateGenre(plot: string, transport: Transport = fetch): Promise<unknown> {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error('missing_key');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await transport('https://openrouter.ai/api/v1/systemone', {
      method: 'POST', signal: controller.signal,
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: MODEL, state: { plot }, questions: QUESTIONS }),
    });
    if (!response.ok) throw new Error(response.status === 429 ? 'rate_limit' : 'http_error');
    return await response.json();
  } finally { clearTimeout(timer); }
}

export async function withGenreDecision<T extends MovieResult>(
  plot: string, original: () => Promise<T>, transport: Transport = fetch,
): Promise<T | MovieResult> {
  let accepted: MovieResult | undefined;
  let reason = 'unsupported_state';
  if (typeof plot === 'string' && plot.trim() && new TextEncoder().encode(plot).length <= MAX_STATE_BYTES) {
    reason = 'missing_key';
    if (process.env.OPENROUTER_API_KEY) {
      try {
        const decision = parseDecision(await evaluateGenre(plot, transport));
        reason = 'below_threshold';
        if (confidenceAccepted(decision.confidence)) accepted = decision.result;
      } catch (error) {
        const name = error instanceof Error ? error.name : '';
        const message = error instanceof Error ? error.message : '';
        reason = name === 'AbortError' || name === 'TimeoutError' ? 'timeout' :
          ['rate_limit', 'http_error', 'malformed'].includes(message) ? message : 'error';
      }
    }
  }
  console.warn(JSON.stringify({ path: accepted ? 'jev' : 'original',
    model: accepted ? MODEL : ORIGINAL_MODEL, jev_model: MODEL,
    reason: accepted ? 'accepted' : reason }));
  if (accepted) return accepted;
  // Outside the Jev catch: original failures propagate without a second call.
  return original();
}
