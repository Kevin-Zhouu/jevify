import { openai } from '@ai-sdk/openai';
import { generateObject } from 'ai';
import 'dotenv/config';
import {
  callJevGenreClassification,
  JEV_MODEL,
} from './jevDecisions';

const MOVIE_PLOT =
  'A group of astronauts travel through a wormhole in search of a ' +
  'new habitable planet for humanity.';

async function main() {
  // Try Jev Choice first; fall back to original generateObject on low
  // confidence, errors, timeouts, missing credentials, or unknown labels.
  const jevResult = await callJevGenreClassification(MOVIE_PLOT);

  if (jevResult) {
    // Jev path — use real Jev answer and usage
    const { genre, jevResponse } = jevResult;
    process.stderr.write(
      `[jev] answered: path=jev model=${jevResponse.model}\n`,
    );

    console.log(genre);
    console.log();
    console.log('Token usage:', {
      promptTokens: jevResponse.usage.input_tokens,
      completionTokens: jevResponse.usage.output_tokens,
      totalTokens:
        jevResponse.usage.input_tokens + jevResponse.usage.output_tokens,
    });
    console.log('Finish reason:', 'stop');
  } else {
    // Original path — unchanged generateObject call
    const result = await generateObject({
      model: openai('gpt-4o-mini', { structuredOutputs: true }),
      output: 'enum',
      enum: ['action', 'comedy', 'drama', 'horror', 'sci-fi'],
      prompt: 'Classify the genre of this movie plot: "' + MOVIE_PLOT + '"',
    });

    process.stderr.write('[jev] answered: path=original model=gpt-4o-mini\n');

    console.log(result.object);
    console.log();
    console.log('Token usage:', result.usage);
    console.log('Finish reason:', result.finishReason);
  }
}

main().catch(console.error);
