/**
 * Jev decisions module — owns all Jev model IDs, question definitions,
 * confidence thresholds, and the fallback wrapper for this project.
 */

// ---------------------------------------------------------------------------
// Model and provider configuration
// ---------------------------------------------------------------------------

export const JEV_MODEL = 'typesafe/jev-1.13-20260917';
export const JEV_ENDPOINT = 'https://openrouter.ai/api/v1/systemone';
export const JEV_TIMEOUT_MS = 5000;
export const CONFIDENCE_THRESHOLD = 0.7;

// ---------------------------------------------------------------------------
// Genre classification question
// ---------------------------------------------------------------------------

export const GENRE_QUESTION = {
  type: 'choice' as const,
  instructions: 'What is the genre of this movie based on its plot?',
  criteria: {
    action: null,
    comedy: null,
    drama: null,
    horror: null,
    'sci-fi': null,
  },
};

// ---------------------------------------------------------------------------
// Jev HTTP adapter (dependency-free, uses Node 18+ fetch)
// ---------------------------------------------------------------------------

interface JevChoiceAnswer {
  choice: string;
  confidence: number;
  probabilities: Record<string, number>;
}

interface JevResponse {
  model: string;
  answers: Record<string, JevChoiceAnswer>;
  usage: { input_tokens: number; output_tokens: number };
}

export async function callJevGenreClassification(
  moviePlot: string,
): Promise<{ genre: string; jevResponse: JevResponse } | null> {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    process.stderr.write('[jev] missing OPENROUTER_API_KEY, taking original path\n');
    return null;
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), JEV_TIMEOUT_MS);

  try {
    const body = JSON.stringify({
      model: JEV_MODEL,
      state: moviePlot,
      questions: { genre: GENRE_QUESTION },
    });

    const res = await fetch(JEV_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body,
      signal: controller.signal,
    });

    if (!res.ok) {
      process.stderr.write(
        `[jev] HTTP ${res.status}, taking original path\n`,
      );
      return null;
    }

    const data: JevResponse = await res.json();
    const answer = data.answers?.genre;

    if (!answer || typeof answer.confidence !== 'number' || !isFinite(answer.confidence)) {
      process.stderr.write('[jev] malformed response, taking original path\n');
      return null;
    }

    if (answer.confidence < CONFIDENCE_THRESHOLD) {
      process.stderr.write(
        `[jev] confidence ${answer.confidence.toFixed(2)} < ${CONFIDENCE_THRESHOLD}, taking original path\n`,
      );
      return null;
    }

    const validOptions = Object.keys(GENRE_QUESTION.criteria);
    if (!validOptions.includes(answer.choice)) {
      process.stderr.write(
        `[jev] unknown label "${answer.choice}", taking original path\n`,
      );
      return null;
    }

    return { genre: answer.choice, jevResponse: data };
  } catch (err: unknown) {
    const reason =
      err instanceof Error && err.name === 'AbortError' ? 'timeout' : 'error';
    process.stderr.write(`[jev] ${reason}, taking original path\n`);
    return null;
  } finally {
    clearTimeout(timeout);
  }
}
