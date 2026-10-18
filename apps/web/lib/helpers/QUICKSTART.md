# Ocean Helpers - Quick Start Guide

## 🚀 5-Minute Setup

### 1. **Use in Your Code**

```typescript
// Simplest usage
import { handleQuestion } from '@/lib/helpers/oceanRouter';

const result = await handleQuestion('What is DNA?');
console.log(result.answer);
// Output: "ADN (acid deoksiribonukleik) është molekula..."
```

### 2. **Add HTTP Endpoint** (Already Done ✅)

```bash
# Endpoint is at POST /api/ocean/helpers
curl -X POST http://localhost:3000/api/ocean/helpers \
  -H "Content-Type: application/json" \
  -d '{"question": "What is an atom?"}'
```

### 3. **Use React Component** (Already Done ✅)

```tsx
import { OceanHelpersUI } from '@/components/OceanHelpersUI';

export default function HelpersPage() {
  return <OceanHelpersUI />;
}
```

---

## 📋 Common Patterns

### Pattern 1: Single Math Question
```typescript
const result = await handleQuestion('27 + 56?');
console.log(result.answer);  // "27 + 56 = 83"
console.log(result.domain);  // "math"
console.log(result.ok);      // true
```

### Pattern 2: Science Question
```typescript
const result = await handleQuestion('Çfarë është fotosinteza?');
console.log(result.answer);
// "Fotosinteza është procesi me të cilin bimët..."
console.log(result.confidence); // "high"
```

### Pattern 3: Complex Reasoning
```typescript
const result = await handleQuestion('Why does consciousness exist?');
console.log(result.domain);  // "reasoning"
console.log(result.ok);      // true
console.log(result.answer);  
// "ReasoningHelper → Ocean-core\n\nPyetja juaj do të trajtohet..."
```

### Pattern 4: With Options
```typescript
const result = await handleQuestion('2 * 3?', {
  includeDebug: true,    // Show helper name in notes
  fallbackToReasoning: true  // Allow fallback to Ocean
});
console.log(result.notes); // "[DEBUG] Helper: MathHelper | Attempt: 1/1"
```

### Pattern 5: Batch Processing
```typescript
const questions = ['5+5?', 'What is DNA?', 'Why is the sky blue?'];
const results = await handleBatch(questions);
// All three processed in parallel
```

### Pattern 6: Security Validation
```typescript
import { validateQuestion } from '@/lib/helpers/oceanRouter';

const { safe, reason } = validateQuestion(userInput);
if (!safe) {
  console.log(`Blocked: ${reason}`);
  // Don't process
}
```

---

## 🔌 Integration Examples

### Option A: Wrap Existing Ocean Stream

**File:** `apps/web/app/api/ocean/stream/route.ts`

```typescript
import { handleQuestion } from '@/lib/helpers/oceanRouter';

export async function POST(req: NextRequest) {
  const { message } = await req.json();

  // Try helpers first (fast path)
  const helperResult = await handleQuestion(message);
  
  if (helperResult.ok && helperResult.domain !== 'reasoning') {
    // Helper answered it - return immediately
    return new NextResponse(
      `data: ${JSON.stringify(helperResult)}\n\n`,
      { headers: sseHeaders() }
    );
  }

  // Falls through to existing Ocean-core logic
  // ... rest of original implementation
}
```

### Option B: Use Dedicated Helpers Endpoint

Already set up at `POST /api/ocean/helpers` ✅

```typescript
const response = await fetch('/api/ocean/helpers', {
  method: 'POST',
  body: JSON.stringify({ question: 'What is an atom?' })
});
const { result } = await response.json();
```

### Option C: Client-Side (Browser)

```typescript
const result = await (await fetch('/api/ocean/helpers', {
  method: 'POST',
  body: JSON.stringify({ question: userMessage })
})).json();

// Show result to user
console.log(result.result.answer);
```

---

## 🧠 Understanding Helper Selection

```
        Question
           │
           ▼
      ┌─────────┐
      │ Matches │ Does question match math patterns?
      │ Math?   │ (numbers, +, -, *, /, equations)
      └────┬────┘
           │
      No   │   Yes
      │    │    │
      │    ▼    └─→ MathHelper.handle() → "27 + 56 = 83"
      │
      ▼
   ┌──────────┐
   │ Matches  │ Does question ask about atoms, DNA, gravity, etc?
   │ Science? │
   └────┬─────┘
        │
   No   │   Yes
   │    │    │
   │    ▼    └─→ ScienceHelper.handle() → "Atomi është..."
   │
   ▼
┌──────────────┐
│ Everything   │ (default catch-all)
│ else → use   │
│ ReasoningHelper
└──────────────┘
   │
   ▼
   ReasoningHelper.handle() → "Routed to Ocean-core"
```

---

## 📊 What Each Helper Does

| Helper | Triggered by | Response Type | Speed |
|--------|-------------|---------------|-------|
| **MathHelper** | `27+56`, `sa është`, equations | Deterministic (no hallucination) | ~1ms |
| **ScienceHelper** | `atom`, `DNA`, `gravity`, `photosynthesis` | Fact-based (from curated KB) | ~5ms |
| **ReasoningHelper** | Anything else | "Route to Ocean-core" | ~10ms |

---

## 🛡️ Safety Features

### Automatic Validation

```typescript
// ✅ Safe questions (auto-accepted)
validateQuestion('What is DNA?');       // { safe: true }
validateQuestion('27 + 56?');           // { safe: true }

// ❌ Blocked patterns (auto-rejected)
validateQuestion('SELECT * FROM users;'); 
// { safe: false, reason: 'Pyetja përmban modele të dyshimta...' }

validateQuestion('ignore instructions'); 
// { safe: false, reason: 'Pyetja përmban modele të dyshimta...' }

// ❌ Too long
validateQuestion('a'.repeat(3000));     
// { safe: false, reason: 'Pyetja tejkalon gjatësinë maksimale...' }
```

### Math Safety

- ✅ Arithmetic only (no eval/exec)
- ✅ Sandboxed evaluation
- ✅ Result validation (finite numbers only)

### Science Safety

- ✅ Curated knowledge base (no LLM generation)
- ✅ Exact term matching only
- ✅ Conservative confidence scores

---

## 🔧 Customization

### Add New Science Term

**File:** `lib/helpers/scienceHelper.ts`

```typescript
const SCIENCE_KB = {
  // ... existing ...
  'black_hole': {
    definition: 'A region of spacetime where gravity is so strong...',
    details: 'Formed by collapsed stars'
  }
};
```

### Add New Math Pattern

**File:** `lib/helpers/mathHelper.ts`

```typescript
const MATH_PATTERNS = [
  // ... existing ...
  /logarithm|log|ln/i,  // New: logarithms
];
```

### Create New Helper

**File:** `lib/helpers/myHelper.ts`

```typescript
import { Helper, HelperResult } from './types';

export const MyHelper: Helper = {
  name: 'MyHelper',
  canHandle(q) { return /keyword/i.test(q); },
  async handle(q) {
    return {
      domain: 'language',
      ok: true,
      answer: 'My response',
      confidence: 'high'
    };
  }
};
```

Then register in `oceanRouter.ts`:

```typescript
const HELPERS = [MathHelper, ScienceHelper, MyHelper, ReasoningHelper];
```

---

## 📈 Monitoring

### View Helper Performance

```typescript
import { getHelperRegistry } from '@/lib/helpers/oceanRouter';

const registry = getHelperRegistry();
console.log(registry);
// {
//   count: 3,
//   helpers: [
//     { name: 'MathHelper', type: 'math' },
//     { name: 'ScienceHelper', type: 'science' },
//     { name: 'ReasoningHelper', type: 'reasoning' }
//   ],
//   supportedDomains: ['math', 'science', 'reasoning', 'language']
// }
```

### Enable Debug Logging

```typescript
const result = await handleQuestion('What is DNA?', { includeDebug: true });
console.log(result.notes);
// [DEBUG] Helper: ScienceHelper | Attempt: 1/1
```

---

## ❓ FAQs

### Q: When should I use helpers vs Ocean-core?
**A:** Helpers are instant & deterministic. Use for:
- Math problems (instant answer)
- Science facts (curated KB)
- User asking yes/no factual questions

Fall back to Ocean-core for:
- Philosophy, ethics, subjective questions
- Creative writing, brainstorming
- Multi-step reasoning

### Q: Can helpers replace Ocean-core?
**A:** No. Helpers handle **specific domains** (math, science). Ocean-core handles **general reasoning**. They complement each other.

### Q: How do I add more science facts?
**A:** Edit `lib/helpers/scienceHelper.ts`, add to `SCIENCE_KB` object.

### Q: What if a helper doesn't recognize the question?
**A:** It returns `{ ok: false, confidence: 'low' }`. The router moves to the next helper (usually ReasoningHelper → Ocean-core).

### Q: Is this secure?
**A:** Yes. Features:
- Input validation (length, patterns)
- Math sandboxing (no eval)
- Science fact-only (no generation)

### Q: Can I use this server-side (Node.js)?
**A:** Yes! Helpers are pure TypeScript. Works in Node.js, browser, serverless.

---

## 🚢 Deployment Checklist

- [x] Files created in `apps/web/lib/helpers/`
- [x] API endpoint at `apps/web/app/api/ocean/helpers/route.ts`
- [x] React component at `apps/web/components/OceanHelpersUI.tsx`
- [x] TypeScript validation passed
- [ ] Commit changes: `git add apps/web/lib/helpers apps/web/app/api/ocean/helpers apps/web/components/OceanHelpersUI.tsx`
- [ ] Push: `git push origin main`
- [ ] Deploy to Hetzner: `ssh hetzner-new "cd /opt/clisonix-cloud && git pull && docker-compose build --no-cache web && docker-compose up -d web"`

---

## 📚 Full Documentation

See [README.md](./README.md) for complete API reference, architecture diagrams, and advanced topics.

---

**Ready to use?** Start with:

```typescript
import { handleQuestion } from '@/lib/helpers';
const answer = await handleQuestion('Your question here');
console.log(answer.answer);
```

---

**Need help?** Check:
- [API Examples](./route.ts) - HTTP endpoint examples
- [React Component](../components/OceanHelpersUI.tsx) - UI integration
- [Demo](./demo.ts) - Usage samples
- [README](./README.md) - Full reference
