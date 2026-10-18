# Ocean Helpers - Deterministic Question Routing Engine

A modular, type-safe TypeScript/Node.js helper system that routes questions to specialized engines before falling back to Ocean-core reasoning. Prevents hallucinations by handling math, science, and factual questions deterministically.

## Overview

```
┌─────────────────────────────────────┐
│         User Question               │
└────────────┬────────────────────────┘
             │
             ▼
        ┌────────────────────┐
        │ Validation Layer   │  (Security checks, length validation)
        │ validateQuestion() │
        └────────┬───────────┘
                 │
        ┌────────▼──────────────────────┐
        │   Ocean Router                 │
        │ handleQuestion(q, options)     │
        └────────┬──────────────────────┘
                 │
          ___________▼____________
         │                       │
         ▼                       ▼
    ┌─────────────┐         ┌──────────────┐
    │ MathHelper  │         │ ScienceHelper│
    │ "27 + 56?"  │         │ "What= DNA?" │
    └──────┬──────┘         └────────┬─────┘
           │ OK                      │ OK
           └───────────┬─────────────┘
                       │
                       ▼
            ┌───────────────────────┐
            │ ReasoningHelper       │
            │ (Fallback to Ocean)   │
            └───────────────────────┘
                       │
                       ▼
            ┌────────────────────────┐
            │  HelperResult          │
            │ {domain, ok, answer}   │
            └────────────────────────┘
```

## Architecture

### File Structure

```
apps/web/lib/helpers/
├── types.ts                 # TypeScript interfaces & types
├── mathHelper.ts            # Arithmetic & basic algebra
├── scienceHelper.ts         # Factual science knowledge base
├── reasoningHelper.ts       # Complex reasoning fallback
├── oceanRouter.ts           # Main routing orchestrator
├── index.ts                 # Re-exports & public API
└── demo.ts                  # Usage examples

apps/web/app/api/ocean/
└── helpers/
    └── route.ts             # HTTP API endpoint (GET/POST)

apps/web/components/
└── OceanHelpersUI.tsx       # React chat interface component
```

### Core Types

```typescript
export type Domain = 'math' | 'science' | 'reasoning' | 'language';

export interface HelperResult {
  domain: Domain;
  ok: boolean;
  answer: string;
  notes?: string;
  confidence?: 'high' | 'medium' | 'low';
}

export interface Helper {
  name: string;
  canHandle: (question: string) => boolean;
  handle: (question: string) => Promise<HelperResult>;
}
```

## Helper Engines

### 1. **MathHelper** (`mathHelper.ts`)

Handles deterministic mathematics without hallucinations.

**Capabilities:**
- ✅ Basic arithmetic: `27 + 56`, `100 * 5`, `1000 / 8`
- ✅ Pattern detection: `Sa është 27 + 56?` (Albanian)
- ✅ Safe evaluation: sandboxed arithmetic using Function constructor
- ⚠️ Not yet: complex equations, calculus

**Example:**
```typescript
const result = await MathHelper.handle('27 + 56');
// { domain: 'math', ok: true, answer: '27 + 56 = 83', confidence: 'high' }
```

### 2. **ScienceHelper** (`scienceHelper.ts`)

Provides factual scientific definitions from curated knowledge base.

**Supported Terms (English + Albanian):**
- atom, molecule, electron, proton, neutron
- water (ujë), hydrogen, oxygen
- gravity, planets, orbits
- photosynthesis (fotosinteza)
- DNA (adn), genes, chromosomes
- electricity, magnetism, heat
- entropy, thermodynamics

**Example:**
```typescript
const result = await ScienceHelper.handle('What is an atom?');
// { domain: 'science', ok: true, answer: 'Atomi është...', confidence: 'high' }
```

### 3. **ReasoningHelper** (`reasoningHelper.ts`)

Catch-all for complex reasoning questions. Routes to Ocean-core LLM.

**Triggers:**
- Philosophical questions: `vetëdije`, `kestetim`, `morale`
- Complex multi-step: `si`, `pse`, `kur`, `ku`
- Creative/open-ended: `shkruaj`, `imagjino`, `ide`

**Example:**
```typescript
const result = await ReasoningHelper.handle('A mund të ketë vetëdije një AI?');
// { domain: 'reasoning', ok: true, answer: 'ReasoningHelper → Ocean-core...', confidence: 'medium' }
```

## Usage

### 1. **Basic Single Question**

```typescript
import { handleQuestion } from '@/lib/helpers';

const result = await handleQuestion('27 + 56?');
console.log(result.answer); // "27 + 56 = 83"
```

### 2. **Batch Processing**

```typescript
import { handleBatch } from '@/lib/helpers';

const results = await handleBatch([
  '100 * 5?',
  'What is DNA?',
  'Why is the sky blue?'
]);
```

### 3. **Streaming Results**

```typescript
import { handleQuestionStream } from '@/lib/helpers';

for await (const chunk of handleQuestionStream('What is photosynthesis?')) {
  console.log(chunk.answer);
}
```

### 4. **Security Validation**

```typescript
import { validateQuestion } from '@/lib/helpers';

const { safe, reason } = validateQuestion(userInput);
if (!safe) {
  console.log(`Blocked: ${reason}`);
}
```

### 5. **Helper Registry**

```typescript
import { getHelperRegistry } from '@/lib/helpers';

const registry = getHelperRegistry();
console.log(registry.helpers); // List all registered helpers
```

## HTTP API Endpoint

### Endpoint: `POST /api/ocean/helpers`

**Request:**
```json
{
  "question": "What is an atom?",
  "debug": false,
  "stream": false
}
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "domain": "science",
    "ok": true,
    "answer": "Atomi është njësia më e vogël...",
    "confidence": "high"
  },
  "timestamp": "2024-03-27T10:30:00.000Z"
}
```

### Streaming: `POST /api/ocean/helpers?stream=true`

Returns Server-Sent Events (SSE):
```
data: {"event":"start","message":"Helper routing question..."}
data: {"event":"result","data":{...},"timestamp":"..."}
data: {"event":"done"}
```

### GET `/api/ocean/helpers`

Returns helper registry:
```json
{
  "status": "ok",
  "registry": {
    "count": 3,
    "helpers": [
      {"name": "MathHelper", "type": "math"},
      {"name": "ScienceHelper", "type": "science"},
      {"name": "ReasoningHelper", "type": "reasoning"}
    ],
    "supportedDomains": ["math", "science", "reasoning", "language"]
  }
}
```

## React Component

### `<OceanHelpersUI />`

Full-featured chat component with streaming support.

**Features:**
- ✅ Single & streaming responses
- ✅ Domain-colored messages (blue=math, green=science, purple=reasoning)
- ✅ Auto-scroll, timestamps
- ✅ Error handling
- ✅ Keyboard disabled during loading

**Usage:**
```typescript
import { OceanHelpersUI } from '@/components/OceanHelpersUI';

export default function HelpersPage() {
  return <OceanHelpersUI />;
}
```

## Integration with Ocean-Core

When a question reaches `ReasoningHelper`, it can be forwarded to Ocean-core for rich LLM reasoning:

```typescript
// In oceaRouter.ts or custom logic
const result = await handleQuestion(question);

if (result.domain === 'reasoning' && result.ok) {
  // Stream from Ocean-core
  const oceanResponse = await fetch('/api/ocean/stream', {
    method: 'POST',
    body: JSON.stringify({ message: question })
  });
  
  // Relay SSE chunks to user
}
```

## Configuration & Customization

### Extend MathHelper

```typescript
// mathHelper.ts - add new patterns
const MATH_PATTERNS = [
  // ... existing patterns ...
  /quadratic|ax\^2\+bx\+c/i,  // New: quadratic
  /matrix|determinant/i,       // New: linear algebra
];
```

### Expand ScienceHelper KB

```typescript
// scienceHelper.ts - add facts
const SCIENCE_KB = {
  // ... existing ...
  'relativity': {
    definition: 'Einstein\'s theory of how space and time are relative...',
  },
};
```

### Add New Helper

```typescript
import { Helper, HelperResult } from './types';

export const MyHelper: Helper = {
  name: 'MyHelper',
  canHandle(question: string) {
    return /keyword/i.test(question);
  },
  async handle(question: string): Promise<HelperResult> {
    return {
      domain: 'language',  // Or custom domain
      ok: true,
      answer: 'My custom response',
      confidence: 'high',
    };
  },
};

// Register in oceanRouter.ts
const HELPERS: Helper[] = [
  MathHelper,
  ScienceHelper,
  MyHelper,  // Add here
  ReasoningHelper,
];
```

## Demo & Testing

Run the included demo:

```bash
cd apps/web
npx ts-node lib/helpers/demo.ts
```

Or in Node.js REPL:

```javascript
const { runAllDemos } = require('./lib/helpers/demo');
await runAllDemos();
```

## Security

### Guarded Features

✅ **Injection Prevention:** SQL, script, eval patterns blocked by `validateQuestion()`
✅ **Length Limits:** Max 2000 chars per question
✅ **Code Sandbox:** Math evaluation uses `Function()` constructor, no `eval()`
✅ **Pattern Whitelisting:** Only recognized domains/keywords matched

### Safe by Default

- Science KB is curated (no LLM generation)
- Math only supports sandboxed arithmetic
- Reasoning falls back to Ocean with full context

## Performance & Caching

### Current

- MathHelper: ~1ms per arithmetic
- ScienceHelper: ~5ms per lookup (Object.entries iteration)
- ReasoningHelper: ~10ms to detect fallback

### Future Optimizations

- Memoize regex patterns (compilation cost)
- IndexedDB for Science KB (remove iteration)
- Redis cache for frequent questions
- Parallel helper evaluation (Promise.race)

## Monitoring & Debugging

### Enable Debug Mode

```typescript
const result = await handleQuestion(question, { includeDebug: true });
console.log(result.notes); // Shows helper name, attempt number, etc.
```

### Sample Logs

```
[DEBUG] Helper: MathHelper | Attempt: 1/1
[DEBUG] Helper: ScienceHelper | Attempt: 1/1
[DEBUG] ScienceHelper: Njoh këtë lloj pyetjeje shkencore, por nuk kam përkufizim...
```

## Roadmap

- [ ] **Advanced Math:** Symbolic solver (sympy API), graphing
- [ ] **Extended Science:** Multi-language KB, citations/sources
- [ ] **Learning:** Feedback loop to update helpers from user corrections
- [ ] **Async Streaming:** Full Ocean-core response relay in SSE
- [ ] **Monitoring:** Prometheus metrics (helper hit rates, latencies)
- [ ] **Testing:** Unit tests for each helper, integration tests with Ocean

## License & Attribution

Part of **Clisonix Cloud** architecture. Designed to coexist with Ocean-core and prevent hallucinations in deterministic domains.

---

**Questions?** Check [demo.ts](./demo.ts) or contact the team.
