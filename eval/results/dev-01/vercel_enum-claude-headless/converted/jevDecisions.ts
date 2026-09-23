// Jev decisions module — all model IDs, questions, criteria, and thresholds in one place.
// Provider: OpenRouter. Model: typesafe/jev-1.13-20260917 (pinned).

export const JEV_MODEL = 'typesafe/jev-1.13-20260917';
const JEV_ENDPOINT = 'https://openrouter.ai/api/v1/systemone';
const JEV_TIMEOUT_MS = 10_000;

export const genreClassification = {
  model: JEV_MODEL,
  threshold: 0.7,
  question: {
    type: 'choice' as const,
    instructions: 'Classify the genre of this movie plot.',
    criteria: {
      action: null,
      comedy: null,
      drama: null,
      horror: null,
      'sci-fi': null,
    } as Record<string, null>,
  },
};

export interface JevGenreResult {
  choice: string;
  confidence: number;
  probabilities: Record<string, number>;
  usage: { input_tokens: number; output_tokens: number };
  model: string;
}

/**
 * Attempt genre classification via Jev Choice.
 * Returns null on missing key, network error, timeout, non-OK response,
 * or malformed/unexpected response shape.
 */
export async function classifyGenre(
  moviePlot: string,
): Promise<JevGenreResult | null> {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) return null;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), JEV_TIMEOUT_MS);

  try {
    const res = await fetch(JEV_ENDPOINT, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: genreClassification.model,
        state: moviePlot,
        questions: {
          genre: genreClassification.question,
        },
      }),
      signal: controller.signal,
    });

    if (!res.ok) return null;

    const data = await res.json();
    const answer = data.answers?.genre;
    if (!answer || answer.type !== 'choice' || typeof answer.choice !== 'string') {
      return null;
    }
    if (typeof answer.confidence !== 'number' || !isFinite(answer.confidence)) {
      return null;
    }
    // Reject unknown labels
    if (!(answer.choice in genreClassification.question.criteria)) {
      return null;
    }

    return {
      choice: answer.choice,
      confidence: answer.confidence,
      probabilities: answer.probabilities ?? {},
      usage: data.usage ?? { input_tokens: 0, output_tokens: 0 },
      model: data.model ?? genreClassification.model,
    };
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
}
