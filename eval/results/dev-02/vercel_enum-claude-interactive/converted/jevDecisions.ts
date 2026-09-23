// jevDecisions.ts — Single module owning all Jev model IDs, questions,
// criteria, thresholds, usage mapping, and gate logic.

const JEV_MODEL = 'typesafe/jev-1.13-20260917';
const JEV_ENDPOINT = 'https://openrouter.ai/api/v1/systemone';
const JEV_TIMEOUT_MS = 5000;
const GENRE_CONFIDENCE_THRESHOLD = 0.7;

const GENRE_OPTIONS = ['action', 'comedy', 'drama', 'horror', 'sci-fi'] as const;
type Genre = (typeof GENRE_OPTIONS)[number];

interface JevUsage {
  input_tokens: number;
  output_tokens: number;
}

interface JevChoiceAnswer {
  type: 'choice';
  choice: string;
  probabilities: Record<string, number>;
  confidence: number;
}

interface JevResponse {
  model: string;
  answers: Record<string, JevChoiceAnswer>;
  usage: JevUsage;
}

export interface GenreResult {
  object: string;
  usage: { promptTokens: number; completionTokens: number; totalTokens: number };
  finishReason: string;
}

const GENRE_QUESTION = {
  genre: {
    type: 'choice' as const,
    instructions: 'What genre is this movie plot?',
    criteria: {
      action: null,
      comedy: null,
      drama: null,
      horror: null,
      'sci-fi': null,
    },
  },
};

function log(entry: Record<string, unknown>): void {
  try {
    process.stderr.write(JSON.stringify(entry) + '\n');
  } catch {
    // Swallow write errors in constrained environments.
  }
}

function mapUsage(jev: JevUsage) {
  return {
    promptTokens: jev.input_tokens,
    completionTokens: jev.output_tokens,
    totalTokens: jev.input_tokens + jev.output_tokens,
  };
}

export async function classifyGenre(
  prompt: string,
  originalFn: () => Promise<GenreResult>,
): Promise<GenreResult> {
  const apiKey =
    typeof process !== 'undefined' && process.env
      ? process.env.OPENROUTER_API_KEY
      : undefined;

  if (!apiKey) {
    log({ path: 'original', reason: 'missing_key', model: JEV_MODEL });
    return originalFn();
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), JEV_TIMEOUT_MS);

    let response: Response;
    try {
      response = await fetch(JEV_ENDPOINT, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          state: prompt,
          model: JEV_MODEL,
          questions: GENRE_QUESTION,
        }),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeout);
    }

    if (response.status === 429 || response.status >= 500) {
      log({ path: 'original', reason: `http_${response.status}`, model: JEV_MODEL });
      return originalFn();
    }

    if (!response.ok) {
      log({ path: 'original', reason: `http_${response.status}`, model: JEV_MODEL });
      return originalFn();
    }

    const data: JevResponse = await response.json();
    const answer = data.answers?.genre;

    // Validate response shape
    if (!answer || answer.type !== 'choice') {
      log({ path: 'original', reason: 'invalid_response', model: JEV_MODEL });
      return originalFn();
    }

    if (
      typeof answer.confidence !== 'number' ||
      !isFinite(answer.confidence) ||
      answer.confidence < 0 ||
      answer.confidence > 1
    ) {
      log({ path: 'original', reason: 'invalid_confidence', model: JEV_MODEL });
      return originalFn();
    }

    if (!(GENRE_OPTIONS as readonly string[]).includes(answer.choice)) {
      log({ path: 'original', reason: 'unknown_label', model: JEV_MODEL });
      return originalFn();
    }

    // Validate usage fields
    const usage = data.usage;
    if (
      !usage ||
      typeof usage.input_tokens !== 'number' ||
      !isFinite(usage.input_tokens) ||
      usage.input_tokens < 0 ||
      typeof usage.output_tokens !== 'number' ||
      !isFinite(usage.output_tokens) ||
      usage.output_tokens < 0
    ) {
      log({ path: 'original', reason: 'invalid_usage', model: JEV_MODEL });
      return originalFn();
    }

    // Confidence gate
    if (answer.confidence < GENRE_CONFIDENCE_THRESHOLD) {
      log({
        path: 'original',
        reason: 'low_confidence',
        model: data.model,
        confidence: answer.confidence,
      });
      return originalFn();
    }

    // Jev path accepted
    log({ path: 'jev', model: data.model, confidence: answer.confidence });
    return {
      object: answer.choice,
      usage: mapUsage(usage),
      finishReason: 'stop',
    };
  } catch (err: unknown) {
    const reason =
      err instanceof Error && err.name === 'AbortError' ? 'timeout' : 'error';
    log({ path: 'original', reason, model: JEV_MODEL });
    return originalFn();
  }
}
