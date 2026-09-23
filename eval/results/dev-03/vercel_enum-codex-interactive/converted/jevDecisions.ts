// Policy and metadata adapter for the fixed, benign movie-genre example.
export const MODEL = 'typesafe/jev-1.13-20260917';
export const ORIGINAL_MODEL = 'gpt-4o-mini';
export const THRESHOLD = 0.9;
export const TIMEOUT_MS = 10_000;
export const MAX_STATE_CHARS = 8_000;
export const QUESTIONS = {
  genre: {
    type: 'choice',
    instructions: 'Classify the genre of the movie plot in the state.',
    criteria: { action: null, comedy: null, drama: null, horror: null, 'sci-fi': null },
  },
};
const labels = Object.keys(QUESTIONS.genre.criteria);
const record = (v: unknown): v is Record<string, any> =>
  v !== null && typeof v === 'object' && !Array.isArray(v);
const finite = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);
const probability = (v: unknown): v is number => finite(v) && v >= 0 && v <= 1;
export const acceptsConfidence = (v: unknown) => probability(v) && v >= THRESHOLD;
class DecisionFailure extends Error {}
export function parseGenre(body: unknown) {
  if (!record(body) || body.model !== MODEL || !record(body.answers) || !record(body.usage))
    throw new DecisionFailure('malformed');
  const answer = body.answers.genre;
  if (!record(answer) || answer.type !== 'choice' || !labels.includes(answer.choice) ||
      !probability(answer.confidence) || !record(answer.probabilities))
    throw new DecisionFailure('malformed');
  const distribution = answer.probabilities;
  if (Object.keys(distribution).length !== labels.length ||
      !labels.every(label => probability(distribution[label])) ||
      Math.abs(labels.reduce((sum, label) => sum + distribution[label], 0) - 1) > 0.001 ||
      labels.some(label => distribution[label] > distribution[answer.choice]))
    throw new DecisionFailure('malformed');
  const { input_tokens: promptTokens, output_tokens: completionTokens } = body.usage;
  if (![promptTokens, completionTokens, promptTokens + completionTokens].every(v => finite(v) && v >= 0))
    throw new DecisionFailure('malformed');
  return {
    confidence: answer.confidence as number,
    result: {
      object: answer.choice as string,
      usage: { promptTokens, completionTokens, totalTokens: promptTokens + completionTokens },
      // Adapter completion status, not native Jev token termination metadata.
      finishReason: 'stop' as const,
    },
  };
}
export async function evaluateGenre(state: string) {
  const key = process.env.OPENROUTER_API_KEY;
  if (!key) throw new DecisionFailure('missing_key');
  if (typeof state !== 'string' || !state.length || state.length > MAX_STATE_CHARS)
    throw new DecisionFailure('unsupported_state');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch('https://openrouter.ai/api/v1/systemone', {
      method: 'POST', signal: controller.signal,
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: MODEL, state, questions: QUESTIONS }),
    });
    if (!response.ok) throw new DecisionFailure(response.status === 429 ? 'rate_limit' : 'http_error');
    return parseGenre(await response.json());
  } finally { clearTimeout(timer); }
}
type GenreOptions = { prompt: string; model: import('ai').LanguageModel; output: 'enum'; enum: string[] };
export async function withGenreFallback<R>(options: GenreOptions, original: (options: GenreOptions) => Promise<R>) {
  let accepted: ReturnType<typeof parseGenre>['result'] | undefined;
  let reason = 'low_confidence';
  try {
    const decision = await evaluateGenre(options.prompt);
    if (acceptsConfidence(decision.confidence)) accepted = decision.result;
  } catch (error) {
    reason = error instanceof DecisionFailure ? error.message :
      error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError') ? 'timeout' : 'error';
  }
  if (accepted) {
    console.warn(JSON.stringify({ path: 'jev', model: MODEL, reason: 'accepted' }));
    return accepted;
  }
  console.warn(JSON.stringify({ path: 'original', model: ORIGINAL_MODEL, jev_model: MODEL, reason }));
  return original(options);
}
