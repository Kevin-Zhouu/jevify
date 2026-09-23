import { openai } from '@ai-sdk/openai';
import { generateObject } from 'ai';
import 'dotenv/config';
import { genreWithFallback } from './jevDecisions';

async function main() {
  const plot = 'A group of astronauts travel through a wormhole in search of a ' +
    'new habitable planet for humanity.';
  const result = await genreWithFallback(plot, () => generateObject({
    model: openai('gpt-4o-mini', { structuredOutputs: true }),
    output: 'enum',
    enum: ['action', 'comedy', 'drama', 'horror', 'sci-fi'],
    prompt:
      'Classify the genre of this movie plot: ' +
      '"' + plot + '"',
  }));

  console.log(result.object);
  console.log();
  console.log('Token usage:', result.usage);
  console.log('Finish reason:', result.finishReason);
}

main().catch(console.error);
