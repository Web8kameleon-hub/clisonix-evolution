# Clisonix TypeScript SDK

Official TypeScript SDK for Clisonix Cloud API - Neural harmonic processing, EEG analysis, and ASI Trinity integration.

## Installation

```bash
npm install @clisonix/sdk
# or
yarn add @clisonix/sdk
# or
pnpm add @clisonix/sdk
```

## Quick Start

```typescript
import Clisonix from '@clisonix/sdk';

const clisonix = new Clisonix({
  apiKey: 'your-api-key'
});

// Check system health
const health = await clisonix.core.health();
console.log(`System status: ${health.status}`);

// Get ASI Trinity status
const asiStatus = await clisonix.asi.getStatus();
console.log(`ASI Active: ${asiStatus.asi_active}`);
```

## API Modules

### Core API
System health and status endpoints.

```typescript
// Health check
const health = await clisonix.core.health();

// Detailed status
const status = await clisonix.core.status();

// Ping
const ping = await clisonix.core.ping();
```

### Brain API
Neural harmonic processing and analysis.

```typescript
// Analyze harmonics
const analysis = await clisonix.brain.analyzeHarmonics({
  frequencies: [8, 10, 12, 14],
  amplitudes: [0.5, 0.8, 0.6, 0.4]
});

// Get brain sync metrics
const sync = await clisonix.brain.getSync();

// Cortex analysis
const cortex = await clisonix.brain.analyzeCortex({
  pattern_data: [0.1, 0.5, 0.3, 0.8, 0.2],
  analysis_type: 'deep'
});

// Ask AI assistant
const response = await clisonix.brain.ask(
  "What does increased alpha wave activity indicate?"
);
```

### EEG API
EEG data collection and processing.

```typescript
// Start recording session
const session = await clisonix.eeg.startSession({
  channels: 8,
  sample_rate: 256
});

// Get session data
const data = await clisonix.eeg.getSessionData(session.session_id);

// Analyze frequencies
const frequencies = await clisonix.eeg.analyzeFrequencies(session.session_id);

// Stop session
await clisonix.eeg.stopSession(session.session_id);
```

### ASI API
ASI Trinity system interface (ALBA, ALBI, JONA).

```typescript
// Get ASI status
const status = await clisonix.asi.getStatus();

// Get component metrics
const albaMetrics = await clisonix.asi.getALBAMetrics();
const albiMetrics = await clisonix.asi.getALBIMetrics();
const jonaMetrics = await clisonix.asi.getJONAMetrics();

// Trigger sync
await clisonix.asi.triggerSync();
```

### Billing API
Payment and subscription management.

```typescript
// Get available plans
const plans = await clisonix.billing.getPlans();

// Get current subscription
const subscription = await clisonix.billing.getSubscription();

// Create checkout session
const checkout = await clisonix.billing.createCheckout('pro');

// Get usage stats
const usage = await clisonix.billing.getUsage();
```

### Reporting API (Port 8001)
Docker and system metrics.

```typescript
// Get Docker containers
const containers = await clisonix.reporting.getDockerContainers();
console.log(`${containers.total} containers, ${containers.healthy} healthy`);

// Get Docker stats
const stats = await clisonix.reporting.getDockerStats();

// Get system metrics
const metrics = await clisonix.reporting.getSystemMetrics();
```

### Excel API (Port 8002)
Excel and reporting operations.

```typescript
// Generate Excel report
const report = await clisonix.excel.generateReport({
  report_type: 'monthly_summary',
  format: 'xlsx'
});

// Get templates
const templates = await clisonix.excel.getTemplates();
```

## Configuration

```typescript
const clisonix = new Clisonix({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.clisonix.com', // Optional, defaults to production
  timeout: 30000, // Optional, request timeout in ms
  retries: 3 // Optional, number of retry attempts
});
```

## Error Handling

```typescript
import { Clisonix, ClisonixError } from '@clisonix/sdk';

try {
  const health = await clisonix.core.health();
} catch (error) {
  if (error instanceof ClisonixError) {
    console.error(`API Error: ${error.message}`);
    console.error(`Code: ${error.code}`);
    console.error(`Status: ${error.statusCode}`);
  }
}
```

## TypeScript Support

Full TypeScript support with all types exported:

```typescript
import {
  Clisonix,
  HealthResponse,
  ASIStatus,
  BrainSyncResult,
  EEGSession,
  BillingPlan
} from '@clisonix/sdk';
```

## Production Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Main API | https://api.clisonix.com | Core, Brain, EEG, ASI, Billing |
| Reporting | https://reporting.clisonix.com | Docker, System Metrics |
| Excel | https://excel.clisonix.com | Excel Reports |
| Frontend | https://clisonix.com | Web Dashboard |

## License

MIT © Clisonix Cloud
