// Single decisions module for all Jev model IDs, questions, thresholds and gate logic.
// Imported by workflow.ts and validation scripts.

// --- Model and provider configuration ---

export const JEV_MODEL = 'typesafe/jev-1.13-20260917';
export const JEV_BASE_URL = 'https://openrouter.ai/api/v1/systemone';
export const JEV_TIMEOUT_MS = 5000;
export const CONFIDENCE_THRESHOLD = 0.7;

// --- Genre classification question ---

export const GENRE_OPTIONS = ['action', 'comedy', 'drama', 'horror', 'sci-fi'] as const;
export type Genre = (typeof GENRE_OPTIONS)[number];

export const GENRE_QUESTION = {
  genre: {
    type: 'choice' as const,
    instructions: 'Classify the genre of this movie plot.',
    criteria: {
      action: 'Action-oriented plots with physical conflict, chases, or combat',
      comedy: 'Humorous plots focused on jokes, misunderstandings, or absurd situations',
      drama: 'Serious character-driven plots exploring emotional or social themes',
      horror: 'Plots designed to frighten, involving threats, monsters, or supernatural terror',
      'sci-fi': 'Science fiction plots involving futuristic technology, space, or speculative science',
    },
  },
};

// --- Confidence gate ---

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

export function isConfident(answer: JevChoiceAnswer): boolean {
  if (typeof answer.confidence !== 'number' || !isFinite(answer.confidence)) return false;
  if (answer.confidence < 0 || answer.confidence > 1) return false;
  return answer.confidence >= CONFIDENCE_THRESHOLD;
}

export function isKnownGenre(label: string): label is Genre {
  return (GENRE_OPTIONS as readonly string[]).includes(label);
}

// --- Usage adapter ---
// Maps Jev usage to the Vercel AI SDK usage shape for stdout compatibility.
// finishReason: "stop" is an adapter-owned status indicating a successful completed decision.
// This is NOT a native Jev field or a claim that tokens were generated until a stop sequence.

export function adaptUsage(jevUsage: { input_tokens: number; output_tokens: number }) {
  const promptTokens = typeof jevUsage.input_tokens === 'number' && isFinite(jevUsage.input_tokens) && jevUsage.input_tokens >= 0
    ? jevUsage.input_tokens : undefined;
  const completionTokens = typeof jevUsage.output_tokens === 'number' && isFinite(jevUsage.output_tokens) && jevUsage.output_tokens >= 0
    ? jevUsage.output_tokens : undefined;
  if (promptTokens === undefined || completionTokens === undefined) return undefined;
  return {
    promptTokens,
    completionTokens,
    totalTokens: promptTokens + completionTokens,
  };
}

export const ADAPTED_FINISH_REASON = 'stop';

// --- Diagnostic logging (stderr, not console, to avoid test harness interception) ---

function logJev(message: string): void {
  try { process.stderr.write(message + '\n'); } catch { /* ignore */ }
}

// --- Jev HTTP call ---

export async function classifyGenre(
  moviePlot: string,
): Promise<{ genre: Genre; usage: { promptTokens: number; completionTokens: number; totalTokens: number }; model: string } | null> {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    logJev('[jev] path=original reason=OPENROUTER_API_KEY not set');
    return null;
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), JEV_TIMEOUT_MS);

  try {
    const response = await fetch(JEV_BASE_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: JEV_MODEL,
        state: moviePlot,
        questions: GENRE_QUESTION,
      }),
      signal: controller.signal,
    });

    if (response.status === 429 || response.status >= 500) {
      logJev(`[jev] path=original reason=HTTP ${response.status}`);
      return null;
    }

    if (!response.ok) {
      logJev(`[jev] path=original reason=HTTP ${response.status}`);
      return null;
    }

    const body: JevResponse = await response.json();

    const answer = body.answers?.genre;
    if (!answer || answer.type !== 'choice') {
      logJev('[jev] path=original reason=malformed response');
      return null;
    }

    if (!isKnownGenre(answer.choice)) {
      logJev(`[jev] path=original reason=unknown genre label "${answer.choice}"`);
      return null;
    }

    if (!isConfident(answer)) {
      logJev(`[jev] path=original reason=low confidence ${answer.confidence}`);
      return null;
    }

    const adapted = adaptUsage(body.usage);
    if (!adapted) {
      logJev('[jev] path=original reason=invalid usage data');
      return null;
    }

    logJev(`[jev] path=jev model=${body.model} genre=${answer.choice} confidence=${answer.confidence}`);
    return { genre: answer.choice, usage: adapted, model: body.model };
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    logJev(`[jev] path=original reason=error: ${msg}`);
    return null;
  } finally {
    clearTimeout(timeout);
  }
}
