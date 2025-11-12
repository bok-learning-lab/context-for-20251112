# Building Voice Agents

## Audio Handling

Some transport layers like the default `OpenAIRealtimeWebRTC` handle audio input and output for you. Others, such as `OpenAIRealtimeWebSocket`, require manual audio management:

```ts
import {
  RealtimeAgent,
  RealtimeSession,
  TransportLayerAudio,
} from '@openai/agents/realtime';

const agent = new RealtimeAgent({ name: 'My agent' });
const session = new RealtimeSession(agent);
const newlyRecordedAudio = new ArrayBuffer(0);

session.on('audio', (event: TransportLayerAudio) => {
  // play your audio
});

// send new audio to the agent
session.sendAudio(newlyRecordedAudio);
```

## Session Configuration

Configure a session by passing options to `RealtimeSession` or when calling `connect(...)`:

```ts
import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'Greeter',
  instructions: 'Greet the user with cheer and answer questions.',
});

const session = new RealtimeSession(agent, {
  model: 'gpt-realtime',
  config: {
    inputAudioFormat: 'pcm16',
    outputAudioFormat: 'pcm16',
    inputAudioTranscription: {
      model: 'gpt-4o-mini-transcribe',
    },
  },
});
```

Transport layers accept any parameter that matches `session`. For new parameters without a matching `RealtimeSessionConfig` property, use `providerData`; it is passed verbatim in the session object.

## Handoffs

Just like regular agents, handoffs help orchestrate multiple specialists:

```ts
import { RealtimeAgent } from '@openai/agents/realtime';

const mathTutorAgent = new RealtimeAgent({
  name: 'Math Tutor',
  handoffDescription: 'Specialist agent for math questions',
  instructions:
    'You provide help with math problems. Explain your reasoning at each step and include examples',
});

const agent = new RealtimeAgent({
  name: 'Greeter',
  instructions: 'Greet the user with cheer and answer questions.',
  handoffs: [mathTutorAgent],
});
```

Realtime handoffs update the ongoing session with the new configuration, so the new agent inherits conversation history. Voice/model settings remain locked, and only other Realtime Agents can be targeted. Use tool delegation when you need a different model (for example, `gpt-5-mini`).

## Tools

Realtime Agents call tools defined with the standard `tool()` helper:

```ts
import { tool, RealtimeAgent } from '@openai/agents/realtime';
import { z } from 'zod';

const getWeather = tool({
  name: 'get_weather',
  description: 'Return the weather for a city.',
  parameters: z.object({ city: z.string() }),
  async execute({ city }) {
    return `The weather in ${city} is sunny.`;
  },
});

const weatherAgent = new RealtimeAgent({
  name: 'Weather assistant',
  instructions: 'Answer weather questions.',
  tools: [getWeather],
});
```

Only function tools are supported, and they execute wherever the session runs (browser or server). For sensitive actions, have the tool call your backend over HTTP.

While a tool runs the agent cannot process additional user input. Consider prompting the agent to announce the tool call so the user understands the delay.

### Accessing Conversation History

Tools receive the arguments passed by the agent and can also access a snapshot of the conversation:

```ts
import {
  tool,
  RealtimeContextData,
  RealtimeItem,
} from '@openai/agents/realtime';
import { z } from 'zod';

const parameters = z.object({
  request: z.string(),
});

const refundTool = tool<typeof parameters, RealtimeContextData>({
  name: 'Refund Expert',
  description: 'Evaluate a refund',
  parameters,
  execute: async ({ request }, details) => {
    const history: RealtimeItem[] = details?.context?.history ?? [];
    // process the refund request using `history`
  },
});
```

> **Note**  
> The history snapshot reflects the state when the tool was invoked. The most recent utterance may still be transcribing.

### Approval Before Tool Execution

Tools defined with `needsApproval: true` emit `tool_approval_requested`. Use it to prompt the user:

```ts
import { session } from './agent';

session.on('tool_approval_requested', (_context, _agent, request) => {
  // show approval UI
  session.approve(request.approvalItem); // or session.reject(request.rawItem);
});
```

> **Note**  
> While waiting for approval the agent cannot process new user requests.

## Guardrails

Guardrails monitor responses for policy violations based on transcripts (text output must stay enabled). They run asynchronously as the model streams tokens and emit `guardrail_tripped` with the triggering `itemId`.

```ts
import {
  RealtimeOutputGuardrail,
  RealtimeAgent,
  RealtimeSession,
} from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'Greeter',
  instructions: 'Greet the user with cheer and answer questions.',
});

const guardrails: RealtimeOutputGuardrail[] = [
  {
    name: 'No mention of Dom',
    async execute({ agentOutput }) {
      const domInOutput = agentOutput.includes('Dom');
      return {
        tripwireTriggered: domInOutput,
        outputInfo: { domInOutput },
      };
    },
  },
];

const guardedSession = new RealtimeSession(agent, {
  outputGuardrails: guardrails,
});
```

Guardrails run every 100 characters (or at response completion). Since speech output lags text, violations usually trigger before users hear them. Customize the cadence via `outputGuardrailSettings`:

```ts
import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'Greeter',
  instructions: 'Greet the user with cheer and answer questions.',
});

const guardedSession = new RealtimeSession(agent, {
  outputGuardrails: [
    /* ... */
  ],
  outputGuardrailSettings: {
    debounceTextLength: 500, // run every 500 characters (-1 = only at end)
  },
});
```

## Turn Detection / Voice Activity Detection

Realtime Sessions automatically detect speech and trigger turns using built-in VAD. Override settings via `turnDetection`:

```ts
import { RealtimeSession } from '@openai/agents/realtime';
import { agent } from './agent';

const session = new RealtimeSession(agent, {
  model: 'gpt-realtime',
  config: {
    turnDetection: {
      type: 'semantic_vad',
      eagerness: 'medium',
      createResponse: true,
      interruptResponse: true,
    },
  },
});
```

Fine-tune these settings to balance interruptions versus silence handling. Refer to the Realtime API docs for detailed options.

## Interruptions

With automatic VAD, speaking over the agent triggers `audio_interrupted`, which you can use to stop playback (WebSocket transport only):

```ts
import { session } from './agent';

session.on('audio_interrupted', () => {
  // stop local playback
});
```

Offer manual interruption via `interrupt()`:

```ts
import { session } from './agent';

session.interrupt();
// emits `audio_interrupted` so you can halt playback
```

Sessions handle truncating generated text, updating history, and—in WebRTC—clearing outgoing audio. For WebSocket, manually stop any queued audio.

## Text Input

Send text alongside voice by calling `sendMessage`:

```ts
import { RealtimeSession, RealtimeAgent } from '@openai/agents/realtime';

const agent = new RealtimeAgent({ name: 'Assistant' });

const session = new RealtimeSession(agent, {
  model: 'gpt-realtime',
});

session.sendMessage('Hello, how are you?');
```

This enables multimodal interactions or injection of supplemental context.

## Conversation History Management

`RealtimeSession.history` tracks the conversation. Listen for `history_updated` to react to changes, or mutate it via `updateHistory`:

```ts
import { RealtimeSession, RealtimeAgent } from '@openai/agents/realtime';

const agent = new RealtimeAgent({ name: 'Assistant' });

const session = new RealtimeSession(agent, {
  model: 'gpt-realtime',
});

await session.connect({ apiKey: '<client-api-key>' });

session.on('history_updated', (history) => {
  console.log(history);
});

// Option 1: set explicitly
session.updateHistory([
  /* specific history */
]);

// Option 2: transform current history
session.updateHistory((currentHistory) => {
  return currentHistory.filter(
    (item) => !(item.type === 'message' && item.role === 'assistant'),
  );
});
```

## Limitations

- Function tool calls cannot be edited after execution.  
- Text output in history requires transcripts and text modalities.  
- Interrupted responses do not include transcripts.

## Delegation Through Tools

Combine conversation history with a tool call to escalate a complex task to a backend agent:

```ts
import {
  RealtimeAgent,
  RealtimeContextData,
  tool,
} from '@openai/agents/realtime';
import { handleRefundRequest } from './serverAgent';
import z from 'zod';

const refundSupervisorParameters = z.object({
  request: z.string(),
});

const refundSupervisor = tool<
  typeof refundSupervisorParameters,
  RealtimeContextData
>({
  name: 'escalateToRefundSupervisor',
  description: 'Escalate a refund request to the refund supervisor',
  parameters: refundSupervisorParameters,
  execute: async ({ request }, details) => {
    return handleRefundRequest(request, details?.context?.history ?? []);
  },
});

const agent = new RealtimeAgent({
  name: 'Customer Support',
  instructions:
    'You are a customer support agent. If you receive any requests for refunds, you need to delegate to your supervisor.',
  tools: [refundSupervisor],
});
```

Run the heavy lifting on the server (Next.js Server Action example):

```ts
// runs on the server
import 'server-only';

import { Agent, run } from '@openai/agents';
import type { RealtimeItem } from '@openai/agents/realtime';
import z from 'zod';

const agent = new Agent({
  name: 'Refund Expert',
  instructions:
    'You are a refund expert. You are given a request to process a refund and you need to determine if the request is valid.',
  model: 'gpt-5-mini',
  outputType: z.object({
    reasong: z.string(),
    refundApproved: z.boolean(),
  }),
});

export async function handleRefundRequest(
  request: string,
  history: RealtimeItem[],
) {
  const input = `
The user has requested a refund.

The request is: ${request}

Current conversation history:
${JSON.stringify(history, null, 2)}
`.trim();

  const result = await run(agent, input);

  return JSON.stringify(result.finalOutput, null, 2);
}
```
