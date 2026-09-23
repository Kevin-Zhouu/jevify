import { openai } from '@ai-sdk/openai';
import { generateObject } from 'ai';
import 'dotenv/config';
import { genreClassification, classifyGenre } from './jevDecisions';

function jevLog(msg: string) {
  process.stderr.write(`[jev] ${msg}\n`);
}

async function main() {
  const moviePlot =
    'A group of astronauts travel through a wormhole in search of a ' +
    'new habitable planet for humanity.';

  // Try Jev Choice first
  const jev = await classifyGenre(moviePlot);

  if (jev && jev.confidence >= genreClassification.threshold) {
    jevLog(`path=jev model=${jev.model} confidence=${jev.confidence}`);

    console.log(jev.choice);
    console.log();
    console.log('Token usage:', {
      promptTokens: jev.usage.input_tokens,
      completionTokens: jev.usage.output_tokens,
      totalTokens: jev.usage.input_tokens + jev.usage.output_tokens,
    });
    console.log('Finish reason:', 'stop');
    return;
  }

  // Fallback to original
  if (jev) {
    jevLog(
      `path=original model=${jev.model} reason=low-confidence confidence=${jev.confidence}`,
    );
  } else {
    jevLog('path=original reason=jev-unavailable');
  }

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
