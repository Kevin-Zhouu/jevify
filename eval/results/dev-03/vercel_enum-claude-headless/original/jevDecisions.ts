// Single decisions module: all Jev model IDs, questions, criteria, thresholds.
// Converted site: workflow.ts:6 (generateObject enum genre classification)

export const JEV_MODEL = 'typesafe/jev-1.13-20260917';
export const JEV_BASE_URL = 'https://openrouter.ai/api/v1/systemone';
export const JEV_TIMEOUT_MS = 5000;
export const GENRE_CONFIDENCE_THRESHOLD = 0.85;

export const GENRE_OPTIONS = ['action', 'comedy', 'drama', 'horror', 'sci-fi'] as const;
export type Genre = typeof GENRE_OPTIONS[number];

export function genreQuestion() {
  return {
    genre: {
      type: 'choice' as const,
      instructions: 'Classify the genre of this movie plot.',
      criteria: {
        'action': 'Action-oriented plots with physical conflict, chases, battles, or high-stakes missions',
        'comedy': 'Humorous plots intended to amuse through jokes, misunderstandings, or absurd situations',
        'drama': 'Serious plots focused on emotional themes, relationships, and character development',
        'horror': 'Plots designed to frighten, involving supernatural elements, monsters, or psychological terror',
        'sci-fi': 'Science fiction plots involving futuristic technology, space exploration, or scientific concepts',
      },
    },
  };
}

export function isAcceptedGenre(choice: string, confidence: number): choice is Genre {
  return (
    (GENRE_OPTIONS as readonly string[]).includes(choice) &&
    confidence >= GENRE_CONFIDENCE_THRESHOLD
  );
}

function logDecision(data: Record<string, unknown>): void {
  try { process.stderr.write(JSON.stringify(data) + '\n'); } catch {}
}

export async function classifyGenre(
  moviePlot: string,
  originalFn: () => Promise<{ object: string; usage: { promptTokens: number; completionTokens: number; totalTokens: number }; finishReason: string }>
): Promise<{ object: string; usage: { promptTokens: number; completionTokens: number; totalTokens: number }; finishReason: string }> {
  const apiKey = process.env.OPENROUTER_API_KEY;

  if (!apiKey) {
    logDecision({ path: 'original', reason: 'missing_key', model: 'gpt-4o-mini' });
    return originalFn();
  }

  let accepted: { genre: Genre; confidence: number; usage: { input_tokens: number; output_tokens: number }; model: string; requestId: string } | undefined;
  let fallbackReason: string | undefined;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), JEV_TIMEOUT_MS);

  try {
    const response = await fetch(JEV_BASE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: JEV_MODEL,
        state: moviePlot,
        questions: genreQuestion(),
      }),
      signal: controller.signal,
    });

    if (response.status === 429) {
      fallbackReason = 'rate_limit';
    } else if (!response.ok) {
      fallbackReason = `http_${response.status}`;
    } else {
      const body = await response.json();

      if (!body || typeof body !== 'object' || !body.answers?.genre) {
        fallbackReason = 'malformed_response';
      } else {
        const answer = body.answers.genre;
        const model = body.model;
        const usage = body.usage;
        const requestId = body.id ?? '';

        if (typeof model !== 'string' || !model.includes('jev-1.13')) {
          fallbackReason = 'model_mismatch';
        } else if (
          !usage || typeof usage !== 'object' || Array.isArray(usage) ||
          typeof usage.input_tokens !== 'number' || !Number.isFinite(usage.input_tokens) || usage.input_tokens < 0 ||
          typeof usage.output_tokens !== 'number' || !Number.isFinite(usage.output_tokens) || usage.output_tokens < 0
        ) {
          fallbackReason = 'invalid_usage';
        } else if (
          typeof answer.confidence === 'boolean' ||
          typeof answer.confidence !== 'number' ||
          !Number.isFinite(answer.confidence) ||
          answer.confidence < 0 || answer.confidence > 1
        ) {
          fallbackReason = 'invalid_confidence';
        } else if (!isAcceptedGenre(answer.choice, answer.confidence)) {
          fallbackReason = 'low_confidence';
        } else {
          accepted = {
            genre: answer.choice,
            confidence: answer.confidence,
            usage: { input_tokens: usage.input_tokens, output_tokens: usage.output_tokens },
            model,
            requestId,
          };
        }
      }
    }
  } catch (err: unknown) {
    const e = err as { name?: string };
    fallbackReason = e?.name === 'AbortError' ? 'timeout' : 'error';
  } finally {
    clearTimeout(timeoutId);
  }

  if (accepted) {
    logDecision({ path: 'jev', model: accepted.model, jev_model: JEV_MODEL, confidence: accepted.confidence });
    return {
      object: accepted.genre,
      usage: {
        promptTokens: accepted.usage.input_tokens,
        completionTokens: accepted.usage.output_tokens,
        totalTokens: accepted.usage.input_tokens + accepted.usage.output_tokens,
      },
      finishReason: 'stop',
    };
  }

  // Original call is OUTSIDE the try/catch — cannot be caught and retried.
  logDecision({ path: 'original', reason: fallbackReason, jev_model: JEV_MODEL, model: 'gpt-4o-mini' });
  return originalFn();
}
