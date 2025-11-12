# Realtime Transport Layer

## Default Transport Layers

### Connecting Over WebRTC

The default transport layer uses WebRTC, recording microphone input and handling playback automatically. To plug in your own `MediaStream` or audio element, inject an `OpenAIRealtimeWebRTC` instance:

```ts
import {
  RealtimeAgent,
  RealtimeSession,
  OpenAIRealtimeWebRTC,
} from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'Greeter',
  instructions: 'Greet the user with cheer and answer questions.',
});

async function main() {
  const transport = new OpenAIRealtimeWebRTC({
    mediaStream: await navigator.mediaDevices.getUserMedia({ audio: true }),
    audioElement: document.createElement('audio'),
  });

  const customSession = new RealtimeSession(agent, { transport });
}
```

### Connecting Over WebSocket

Pass `transport: 'websocket'` (or provide an `OpenAIRealtimeWebSocket`) to use a WebSocket connection—ideal for server-side contexts such as Twilio phone agents:

```ts
import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'Greeter',
  instructions: 'Greet the user with cheer and answer questions.',
});

const myRecordedArrayBuffer = new ArrayBuffer(0);

const wsSession = new RealtimeSession(agent, {
  transport: 'websocket',
  model: 'gpt-realtime',
});
await wsSession.connect({ apiKey: process.env.OPENAI_API_KEY! });

wsSession.on('audio', (event) => {
  // event.data is a chunk of PCM16 audio
});

wsSession.sendAudio(myRecordedArrayBuffer);
```

Use any recording/playback library to handle the PCM16 payloads.

### Connecting Over SIP

Bridge SIP calls (Twilio, etc.) with `OpenAIRealtimeSIP`. It keeps the session synchronized with SIP events from your telephony provider.

1. Generate the initial session config via `OpenAIRealtimeSIP.buildInitialConfig()` to keep SIP invites and Realtime defaults aligned.  
2. Attach a `RealtimeSession` that uses the SIP transport and connect using the provider’s `callId`.  
3. Listen for session events for analytics, transcripts, or escalations.

```ts
import OpenAI from 'openai';
import {
  OpenAIRealtimeSIP,
  RealtimeAgent,
  RealtimeSession,
  type RealtimeSessionOptions,
} from '@openai/agents/realtime';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
  webhookSecret: process.env.OPENAI_WEBHOOK_SECRET!,
});

const agent = new RealtimeAgent({
  name: 'Receptionist',
  instructions:
    'Welcome the caller, answer scheduling questions, and hand off if the caller requests a human.',
});

const sessionOptions: Partial<RealtimeSessionOptions> = {
  model: 'gpt-realtime',
  config: {
    audio: {
      input: {
        turnDetection: { type: 'semantic_vad', interruptResponse: true },
      },
    },
  },
};

export async function acceptIncomingCall(callId: string): Promise<void> {
  const initialConfig = await OpenAIRealtimeSIP.buildInitialConfig(
    agent,
    sessionOptions,
  );
  await openai.realtime.calls.accept(callId, initialConfig);
}

export async function attachRealtimeSession(
  callId: string,
): Promise<RealtimeSession> {
  const session = new RealtimeSession(agent, {
    transport: new OpenAIRealtimeSIP(),
    ...sessionOptions,
  });

  session.on('history_added', (item) => {
    console.log('Realtime update:', item.type);
  });

  await session.connect({
    apiKey: process.env.OPENAI_API_KEY!,
    callId,
  });

  return session;
}
```

### Cloudflare Workers (workerd) Note

> Cloudflare Workers and other workerd runtimes cannot open outbound WebSockets with the global `WebSocket` constructor. Use the Cloudflare transport from the extensions package, which performs the `fetch()`-based upgrade internally.

```ts
import { CloudflareRealtimeTransportLayer } from '@openai/agents-extensions';
import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'My Agent',
});

const cfTransport = new CloudflareRealtimeTransportLayer({
  url: 'wss://api.openai.com/v1/realtime?model=gpt-realtime',
});

const session = new RealtimeSession(agent, {
  transport: cfTransport,
});
```

## Building Your Own Transport Mechanism

Implement the `RealtimeTransportLayer` interface and emit `RealtimeTransportEventTypes` events to integrate custom transports or third-party speech services.

## Interacting With the Realtime API More Directly

You can stay inside `RealtimeSession` or use the transport layer by itself, depending on how much automation you want.

### Option 1 — Accessing the Transport Layer

`session.transport` exposes the raw connection:

```ts
import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'Greeter',
  instructions: 'Greet the user with cheer and answer questions.',
});

const session = new RealtimeSession(agent, {
  model: 'gpt-realtime',
});

session.transport.on('*', (event) => {
  // JSON-parsed event received over the connection
});

session.transport.sendEvent({
  type: 'response.create',
  // ...
});
```

### Option 2 — Using Only the Transport Layer

Skip automatic tool execution, guardrails, etc., and use the transport client as a lightweight connector:

```ts
import { OpenAIRealtimeWebRTC } from '@openai/agents/realtime';

const client = new OpenAIRealtimeWebRTC();
const audioBuffer = new ArrayBuffer(0);

await client.connect({
  apiKey: '<api key>',
  model: 'gpt-4o-mini-realtime-preview',
  initialSessionConfig: {
    instructions: 'Speak like a pirate',
    voice: 'ash',
    modalities: ['text', 'audio'],
    inputAudioFormat: 'pcm16',
    outputAudioFormat: 'pcm16',
  },
});

client.on('audio', (newAudio) => {
  // handle PCM16 audio chunks
});

client.sendAudio(audioBuffer);
```
