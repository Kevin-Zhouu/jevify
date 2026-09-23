import { openai } from '@ai-sdk/openai';
import { generateObject } from 'ai';
import 'dotenv/config';
import { evaluateGenre, JEV_FINISH_REASON } from './jevDecisions';

async function main() {
  const moviePlot =
    'A group of astronauts travel through a wormhole in search of a ' +
    'new habitable planet for humanity.';

  // Attempt Jev Choice gate; null means rejected/error/missing-key
  let jevResult: Awaited<ReturnType<typeof evaluateGenre>> = null;
  try {
    jevResult = await evaluateGenre(moviePlot);
  } catch {
    // evaluateGenre handles its own errors; this is a defensive catch
  }

  if (jevResult !== null) {
    // Jev accepted — use the Jev answer
    console.log(jevResult.genre);
    console.log();
    console.log('Token usage:', {
      promptTokens: jevResult.usage.input_tokens,
      completionTokens: jevResult.usage.output_tokens,
      totalTokens: jevResult.usage.input_tokens + jevResult.usage.output_tokens,
    });
    console.log('Finish reason:', JEV_FINISH_REASON);
    return;
  }

  // Original path — Jev rejected, errored, timed out, or key missing
  const result = await generateObject({
    model: openai('gpt-4o-mini', { structuredOutputs: true }),
    output: 'enum',
    enum: ['action', 'comedy', 'drama', 'horror', 'sci-fi'],
    prompt: 'Classify the genre of this movie plot: "' + moviePlot + '"',
  });

  console.log(result.object);
  console.log();
  console.log('Token usage:', result.usage);
  console.log('Finish reason:', result.finishReason);
}

main().catch(console.error);
