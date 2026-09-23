// Jev decisions module — single source of truth for all Jev model IDs,
// questions, criteria, thresholds, and gate policy.

export const JEV_MODEL = 'typesafe/jev-1.13-20260917';
export const JEV_CONFIDENCE_THRESHOLD = 0.7;
export const JEV_TIMEOUT_MS = 5000;

const JEV_ENDPOINT = 'https://openrouter.ai/api/v1/systemone';

export const GENRE_OPTIONS = ['action', 'comedy', 'drama', 'horror', 'sci-fi'] as const;
export type Genre = typeof GENRE_OPTIONS[number];

export const GENRE_QUESTION = {
  genre: {
    type: 'choice' as const,
    instructions: 'Classify the genre of this movie plot',
    criteria: {
      action: 'Action-oriented plot with physical conflict, chases, or combat',
      comedy: 'Humorous plot meant to amuse and entertain',
      drama: 'Serious emotional narrative about human experiences',
      horror: 'Plot designed to frighten, with supernatural or violent threats',
      'sci-fi':
        'Plot involving science fiction concepts like space travel, future technology, or alien worlds',
    },
  },
};

export interface JevChoiceAnswer {
  type: 'choice';
  choice: string;
  confidence: number;
  probabilities: Record<string, number>;
}

export interface JevResponse {
  model: string;
  answers: Record<string, JevChoiceAnswer>;
  usage: { input_tokens: number; output_tokens: number };
}

export interface JevGateResult {
  accepted: true;
  genre: Genre;
  confidence: number;
  probabilities: Record<string, number>;
  model: string;
  usage: { input_tokens: number; output_tokens: number };
}

/**
 * Pure confidence gate predicate. Exported for testing.
 */
export function shouldAccept(confidence: number): boolean {
  return (
    typeof confidence === 'number' &&
    Number.isFinite(confidence) &&
    confidence >= 0 &&
    confidence <= 1 &&
    confidence >= JEV_CONFIDENCE_THRESHOLD
  );
}

/**
 * Validate a raw Jev response body. Returns a typed result or null.
 */
function validateResponse(body: unknown): JevGateResult | null {
  if (body === null || typeof body !== 'object' || Array.isArray(body)) return null;
  const resp = body as Record<string, unknown>;

  // Validate model matches pin
  if (typeof resp.model !== 'string') return null;

  // Validate answers container
  if (resp.answers === null || typeof resp.answers !== 'object' || Array.isArray(resp.answers))
    return null;
  const answers = resp.answers as Record<string, unknown>;
  const genreAnswer = answers.genre;
  if (genreAnswer === null || typeof genreAnswer !== 'object' || Array.isArray(genreAnswer))
    return null;
  const ga = genreAnswer as Record<string, unknown>;

  // Validate type
  if (ga.type !== 'choice') return null;

  // Validate choice is a known genre
  if (typeof ga.choice !== 'string') return null;
  if (!(GENRE_OPTIONS as readonly string[]).includes(ga.choice)) return null;

  // Validate confidence — must be finite number in [0,1], not boolean
  if (typeof ga.confidence === 'boolean') return null;
  if (typeof ga.confidence !== 'number') return null;
  if (!Number.isFinite(ga.confidence)) return null;
  if (ga.confidence < 0 || ga.confidence > 1) return null;

  // Validate probabilities
  if (ga.probabilities === null || typeof ga.probabilities !== 'object' || Array.isArray(ga.probabilities))
    return null;

  // Validate usage
  if (resp.usage === null || typeof resp.usage !== 'object' || Array.isArray(resp.usage))
    return null;
  const usage = resp.usage as Record<string, unknown>;
  if (typeof usage.input_tokens !== 'number' || !Number.isFinite(usage.input_tokens) || usage.input_tokens < 0)
    return null;
  if (typeof usage.output_tokens !== 'number' || !Number.isFinite(usage.output_tokens) || usage.output_tokens < 0)
    return null;

  if (!shouldAccept(ga.confidence)) return null;

  return {
    accepted: true,
    genre: ga.choice as Genre,
    confidence: ga.confidence,
    probabilities: ga.probabilities as Record<string, number>,
    model: resp.model as string,
    usage: { input_tokens: usage.input_tokens, output_tokens: usage.output_tokens },
  };
}

/**
 * Attempt a Jev Choice evaluation. Returns a gate result on acceptance, or null
 * on rejection / error / timeout / missing key.
 */
export async function evaluateGenre(moviePlot: string): Promise<JevGateResult | null> {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    process.stderr.write(
      JSON.stringify({ path: 'original', reason: 'missing_key', model: 'gpt-4o-mini' }) + '\n',
    );
    return null;
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), JEV_TIMEOUT_MS);

  try {
    const response = await fetch(JEV_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        state: moviePlot,
        model: JEV_MODEL,
        questions: GENRE_QUESTION,
      }),
      signal: controller.signal,
    });

    if (response.status === 429) {
      process.stderr.write(
        JSON.stringify({ path: 'original', reason: 'rate_limit', jev_model: JEV_MODEL, model: 'gpt-4o-mini' }) + '\n',
      );
      return null;
    }

    if (!response.ok) {
      process.stderr.write(
        JSON.stringify({ path: 'original', reason: 'http_error', status: response.status, jev_model: JEV_MODEL, model: 'gpt-4o-mini' }) + '\n',
      );
      return null;
    }

    const body: unknown = await response.json();
    const result = validateResponse(body);

    if (result === null) {
      process.stderr.write(
        JSON.stringify({ path: 'original', reason: 'low_confidence_or_invalid', jev_model: JEV_MODEL, model: 'gpt-4o-mini' }) + '\n',
      );
      return null;
    }

    process.stderr.write(
      JSON.stringify({ path: 'jev', jev_model: JEV_MODEL, model: result.model, confidence: result.confidence }) + '\n',
    );
    return result;
  } catch (err: unknown) {
    const reason =
      err instanceof Error && err.name === 'AbortError' ? 'timeout' : 'error';
    process.stderr.write(
      JSON.stringify({ path: 'original', reason, jev_model: JEV_MODEL, model: 'gpt-4o-mini' }) + '\n',
    );
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Adapter: map Jev finishReason for a successfully completed decision.
 * This is an adapter-owned status, not a native Jev field.
 */
export const JEV_FINISH_REASON = 'stop';
