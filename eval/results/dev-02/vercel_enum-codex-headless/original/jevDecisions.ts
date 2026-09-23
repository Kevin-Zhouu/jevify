// Jev policy for the fixed, benign movie-plot example; not a public-input guardrail.
export const MODEL = 'typesafe/jev-1.13-20260917';
export const ORIGINAL_MODEL = 'gpt-4o-mini';
export const THRESHOLD = 0.9; // Provisional until measured on representative inputs.
export const TIMEOUT_MS = 5000;
export const MAX_STATE_BYTES = 8000;
export const QUESTIONS = {
  genre: {
    type: 'choice',
    instructions: 'Classify the genre of the movie plot in `plot`. Select one genre.',
    criteria: { action: null, comedy: null, drama: null, horror: null, 'sci-fi': null },
  },
};
type Genre = keyof typeof QUESTIONS.genre.criteria;
export type PrintedResult = {
  object: Genre;
  usage: { promptTokens: number; completionTokens: number; totalTokens: number };
  finishReason: string;
};
const record = (value: unknown): value is Record<string, any> =>
  value !== null && typeof value === 'object' && !Array.isArray(value);
const unit = (value: unknown): value is number =>
  typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1;
const tokens = (value: unknown): value is number =>
  typeof value === 'number' && Number.isSafeInteger(value) && value >= 0;

export function confident(confidence: unknown): boolean {
  return unit(confidence) && confidence >= THRESHOLD;
}

export function parseDecision(raw: unknown) {
  if (!record(raw) || raw.model !== MODEL || !record(raw.answers) || !record(raw.usage))
    throw new Error('invalid_response');
  const answer = raw.answers.genre;
  if (!record(answer) || answer.type !== 'choice' || typeof answer.choice !== 'string' ||
      !Object.hasOwn(QUESTIONS.genre.criteria, answer.choice) || !unit(answer.confidence) ||
      !record(answer.probabilities)) throw new Error('invalid_response');
  const labels = Object.keys(QUESTIONS.genre.criteria);
  if (Object.keys(answer.probabilities).length !== labels.length ||
      !labels.every(label => unit(answer.probabilities[label])) ||
      Math.abs(labels.reduce((sum, label) => sum + answer.probabilities[label], 0) - 1) > 0.02 ||
      labels.some(label => answer.probabilities[label] > answer.probabilities[answer.choice]))
    throw new Error('invalid_response');
  const { input_tokens, output_tokens } = raw.usage;
  if (!tokens(input_tokens) || !tokens(output_tokens) || !tokens(input_tokens + output_tokens))
    throw new Error('invalid_usage');
  return {
    confidence: answer.confidence as number,
    result: {
      object: answer.choice as Genre,
      usage: { promptTokens: input_tokens, completionTokens: output_tokens,
        totalTokens: input_tokens + output_tokens },
      // Adapter-owned generic completion status, not a native Jev stop sequence.
      finishReason: 'stop',
    } satisfies PrintedResult,
    raw,
  };
}

export async function evaluateGenre(plot: string) {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error('missing_key');
  if (typeof plot !== 'string' || !plot.trim() || new TextEncoder().encode(plot).length > MAX_STATE_BYTES)
    throw new Error('unsupported_state');
  const response = await fetch('https://openrouter.ai/api/v1/systemone', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: MODEL, state: { plot }, questions: QUESTIONS }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  if (!response.ok) throw new Error(response.status === 429 ? 'rate_limit' : `http_${response.status}`);
  return parseDecision(await response.json());
}

// Separate the pure gate from transport so fault tests need no simulated Jev inference.
export async function chooseAnswer<T>(decision: ReturnType<typeof parseDecision>, original: () => Promise<T>) {
  if (confident(decision.confidence)) {
    console.warn(`[jevify] path=jev model=${MODEL} reason=accepted`);
    return decision.result;
  }
  return answerOriginal(original, 'below_threshold');
}

async function answerOriginal<T>(original: () => Promise<T>, reason: string): Promise<T> {
  console.warn(`[jevify] path=original model=${ORIGINAL_MODEL} jev_model=${MODEL} reason=${reason}`);
  // Outside the Jev catch: original errors propagate unchanged, never trigger a retry.
  return original();
}

export async function genreWithFallback<T>(plot: string, original: () => Promise<T>): Promise<T | PrintedResult> {
  let decision: ReturnType<typeof parseDecision>;
  try {
    decision = await evaluateGenre(plot);
  } catch (error) {
    const message = error instanceof Error ? error.message : '';
    const reason = error instanceof Error && (error.name === 'TimeoutError' || error.name === 'AbortError')
      ? 'timeout' : /^(missing_key|unsupported_state|invalid_response|invalid_usage|rate_limit|http_\d{3})$/.test(message)
        ? message : 'error';
    return answerOriginal(original, reason);
  }
  return chooseAnswer(decision, original);
}
