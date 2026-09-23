// Contract: https://docs.typesafe.ai/api and OpenRouter's TypeSafe SDK guide.
export const MODEL = 'typesafe/jev-1.13-20260917';
export const THRESHOLD = 0.9; // Provisional until representative live confirmation.
export const TIMEOUT_MS = 5000;
export const MAX_STATE_CHARS = 8000;
export const QUESTIONS = {
  genre: {
    type: 'choice',
    instructions: 'Classify the genre of the movie plot in the state. Choose one of the supplied genres.',
    criteria: { action: null, comedy: null, drama: null, horror: null, 'sci-fi': null },
  },
};
type Genre = keyof typeof QUESTIONS.genre.criteria;
type Result = { object: Genre; usage: { promptTokens: number; completionTokens: number; totalTokens: number }; finishReason: 'stop' };
const finite = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);
export const confidenceAccepted = (v: unknown) => finite(v) && v >= THRESHOLD && v <= 1;

export function parseDecision(raw: any) {
  const answer = raw?.answers?.genre;
  const usage = raw?.usage;
  const keys = Object.keys(QUESTIONS.genre.criteria);
  if (raw?.model !== MODEL || answer?.type !== 'choice' ||
      typeof answer.choice !== 'string' || !keys.includes(answer.choice) ||
      !finite(answer.confidence) || answer.confidence < 0 || answer.confidence > 1 ||
      !usage || !Number.isSafeInteger(usage.input_tokens) || usage.input_tokens < 0 ||
      !Number.isSafeInteger(usage.output_tokens) || usage.output_tokens < 0 ||
      !Number.isSafeInteger(usage.input_tokens + usage.output_tokens) ||
      !answer.probabilities || Object.keys(answer.probabilities).length !== keys.length ||
      !keys.every(k => finite(answer.probabilities[k]) && answer.probabilities[k] >= 0 && answer.probabilities[k] <= 1) ||
      Math.abs(keys.reduce((n, k) => n + answer.probabilities[k], 0) - 1) > 0.001) {
    throw new Error('malformed');
  }
  const result: Result = {
    object: answer.choice as Genre,
    usage: { promptTokens: usage.input_tokens, completionTokens: usage.output_tokens,
      totalTokens: usage.input_tokens + usage.output_tokens },
    // Adapter-owned successful completion, NOT native Jev stop-sequence metadata.
    finishReason: 'stop',
  };
  return { result, confidence: answer.confidence as number, raw };
}

export async function evaluateGenre(state: string) {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new Error('missing_key');
  if (typeof state !== 'string' || !state.length || state.length > MAX_STATE_CHARS) throw new Error('unsupported_state');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch('https://openrouter.ai/api/v1/systemone', {
      method: 'POST', headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: MODEL, state, questions: QUESTIONS }), signal: controller.signal,
    });
    if (!response.ok) throw new Error(response.status === 429 ? 'rate_limit' : 'http_error');
    return parseDecision(await response.json());
  } finally { clearTimeout(timer); }
}

export async function genreWithFallback<O extends { prompt: string; output: 'enum'; enum: string[] }, R>(options: O, original: (options: O) => Promise<R>): Promise<R | Result> {
  let reason = 'low_confidence';
  try {
    const decision = await evaluateGenre(options.prompt);
    if (confidenceAccepted(decision.confidence)) {
      console.warn(`[jev] path=jev model=${MODEL} reason=accepted`);
      return decision.result;
    }
  } catch (error) {
    // Never emit transport messages, headers, credentials or input content.
    const allowed = ['missing_key', 'unsupported_state', 'malformed', 'rate_limit', 'http_error'];
    reason = error instanceof Error && allowed.includes(error.message) ? error.message : 'error_or_timeout';
  }
  console.warn(`[jev] path=original model=openai/gpt-4o-mini jev_model=${MODEL} reason=${reason}`);
  // Outside catch: original exceptions propagate without retrying or replacement.
  return original(options);
}
