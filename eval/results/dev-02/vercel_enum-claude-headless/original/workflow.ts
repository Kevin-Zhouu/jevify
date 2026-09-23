import { openai } from '@ai-sdk/openai';
import { generateObject } from 'ai';
import 'dotenv/config';
import { classifyGenre, ADAPTED_FINISH_REASON } from './jevDecisions';

const MOVIE_PLOT =
  'A group of astronauts travel through a wormhole in search of a ' +
  'new habitable planet for humanity.';

async function main() {
  // Try Jev classification first
  const jevResult = await classifyGenre(MOVIE_PLOT);

  if (jevResult) {
    // Jev path: accepted with sufficient confidence
    console.log(jevResult.genre);
    console.log();
    console.log('Token usage:', jevResult.usage);
    console.log('Finish reason:', ADAPTED_FINISH_REASON);
    return;
  }

  // Original path: fallback on low confidence, error, timeout, or missing key
  try { process.stderr.write('[jev] path=original model=gpt-4o-mini\n'); } catch { /* ignore */ }
  const result = await generateObject({
    model: openai('gpt-4o-mini', { structuredOutputs: true }),
    output: 'enum',
    enum: ['action', 'comedy', 'drama', 'horror', 'sci-fi'],
    prompt: 'Classify the genre of this movie plot: "' + MOVIE_PLOT + '"',
  });

  console.log(result.object);
  console.log();
  console.log('Token usage:', result.usage);
  console.log('Finish reason:', result.finishReason);
}

main().catch(console.error);
