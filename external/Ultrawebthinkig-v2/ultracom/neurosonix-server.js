/**
 * UltraCom Backend - NeuroSonix Integration Server
 * Enhanced cognitive processing with neural frequency modulation
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0 NeuroSonix Enhanced
 */

const express = require('express');
const cors = require('cors');
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// NeuroSonix Neural Frequency Database
const NEURAL_FREQUENCIES = {
  'gamma': { range: '30-100Hz', optimal: 40, function: 'Focus & Concentration' },
  'beta': { range: '13-30Hz', optimal: 15, function: 'Active Thinking & Analysis' },
  'alpha': { range: '8-13Hz', optimal: 10, function: 'Creativity & Relaxation' },
  'theta': { range: '4-8Hz', optimal: 6, function: 'Memory & Deep Processing' },
  'delta': { range: '0.5-4Hz', optimal: 2, function: 'Deep Sleep & Regeneration' }
};

// NeuroSonix Sonic Patterns
const SONIC_PATTERNS = {
  'neural-sync': 'Synchronized brainwave entrainment',
  'cognitive-boost': 'Enhanced cognitive performance',
  'creative-flow': 'Creative thinking amplification',
  'focus-lock': 'Deep concentration enhancement',
  'memory-enhance': 'Memory consolidation support'
};

// Enhanced Chat Endpoint with NeuroSonix
app.post('/api/chat', (req, res) => {
  try {
    const { message, history, neurosonix } = req.body;
    
    // Extract NeuroSonix parameters
    const frequency = neurosonix?.frequency || 40;
    const pattern = neurosonix?.pattern || 'neural-sync';
    
    // Simulate ASI AGI processing with NeuroSonix enhancement
    const enhancedResponse = processWithNeuroSonix(message, frequency, pattern);
    
    res.json({
      success: true,
      response: enhancedResponse,
      metadata: {
        provider: 'asi-ultracom-neurosonix',
        frequency: `${frequency}Hz`,
        pattern: pattern,
        enhancement: 'cognitive-amplified',
        timestamp: new Date().toISOString()
      }
    });
    
  } catch (error) {
    console.error('NeuroSonix Enhanced Chat Error:', error);
    res.status(500).json({
      success: false,
      error: 'NeuroSonix enhancement temporarily unavailable'
    });
  }
});

// NeuroSonix Processing Function
function processWithNeuroSonix(message, frequency, pattern) {
  // Determine optimal cognitive state based on frequency
  let cognitiveState = 'standard';
  if (frequency >= 30) cognitiveState = 'hyper-focused';
  else if (frequency >= 13) cognitiveState = 'analytical';
  else if (frequency >= 8) cognitiveState = 'creative';
  else if (frequency >= 4) cognitiveState = 'deep-processing';
  
  const responses = {
    'hyper-focused': [
      `🧠⚡ **NeuroSonix Gamma Enhancement (${frequency}Hz)**: ${message}\n\nOperating at peak cognitive performance with gamma wave synchronization. Advanced pattern recognition and rapid information processing enabled. Delivering ultra-precise analysis with enhanced focus and concentration.`,
      `🎯🔥 **Hyper-Focus Mode Active**: Processing "${message}" with ${frequency}Hz gamma wave entrainment. Neural pathways optimized for maximum clarity, rapid decision-making, and peak mental performance.`
    ],
    'analytical': [
      `🔬📊 **NeuroSonix Beta Analysis (${frequency}Hz)**: ${message}\n\nEngaging analytical processing with beta wave optimization. Enhanced logical reasoning, systematic thinking, and structured problem-solving capabilities activated.`,
      `⚡🧮 **Analytical Enhancement**: Your query "${message}" processed through ${frequency}Hz beta wave modulation for superior analytical thinking and detailed examination.`
    ],
    'creative': [
      `🎨✨ **NeuroSonix Alpha Creativity (${frequency}Hz)**: ${message}\n\nCreative flow state activated with alpha wave synchronization. Enhanced imagination, innovative thinking, and artistic insight generation enabled.`,
      `🌟💡 **Creative Flow Mode**: Processing "${message}" with ${frequency}Hz alpha wave enhancement for breakthrough creative solutions and innovative perspectives.`
    ],
    'deep-processing': [
      `🌊🧠 **NeuroSonix Theta Deep-Processing (${frequency}Hz)**: ${message}\n\nEngaging deep memory processing and subconscious pattern recognition. Enhanced learning, memory consolidation, and profound insight generation activated.`,
      `🔮💭 **Deep Processing Mode**: Your query "${message}" analyzed through ${frequency}Hz theta wave modulation for deep understanding and memory integration.`
    ]
  };
  
  const stateResponses = responses[cognitiveState] || responses['analytical'];
  const selectedResponse = stateResponses[Math.floor(Math.random() * stateResponses.length)];
  
  return selectedResponse + `\n\n🎵 **Sonic Pattern**: ${pattern} | **Frequency**: ${frequency}Hz | **State**: ${cognitiveState}`;
}

// NeuroSonix Direct Processing Endpoint
app.post('/api/neurosonix/process', (req, res) => {
  try {
    const { message, frequency, pattern, cognitiveMode } = req.body;
    
    const enhancedResponse = processWithNeuroSonix(message, frequency || 40, pattern || 'neural-sync');
    
    res.json({
      success: true,
      enhancedResponse,
      neurosonix: {
        frequency: frequency || 40,
        pattern: pattern || 'neural-sync',
        mode: cognitiveMode || 'enhanced',
        optimalState: frequency >= 30 ? 'gamma' : frequency >= 13 ? 'beta' : frequency >= 8 ? 'alpha' : 'theta'
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('NeuroSonix Processing Error:', error);
    res.status(500).json({
      success: false,
      error: 'NeuroSonix processing failed'
    });
  }
});

// NeuroSonix Enhancement Endpoint
app.post('/api/neurosonix/enhance', (req, res) => {
  try {
    const { message, frequency, pattern } = req.body;
    
    const enhancedContent = processWithNeuroSonix(message, frequency || 40, pattern || 'neural-sync');
    
    res.json({
      success: true,
      content: enhancedContent,
      enhancedResponse: enhancedContent,
      neurosonix: {
        frequency: frequency || 40,
        pattern: pattern || 'neural-sync',
        enhancement: 'cognitive-amplified'
      }
    });
    
  } catch (error) {
    res.status(500).json({ success: false, error: 'Enhancement failed' });
  }
});

// NeuroSonix Info Endpoint
app.get('/api/neurosonix/info', (req, res) => {
  res.json({
    service: 'NeuroSonix Cognitive Enhancement API',
    version: '8.0.0',
    status: 'active',
    frequencies: NEURAL_FREQUENCIES,
    patterns: SONIC_PATTERNS,
    features: [
      'Neural frequency modulation',
      'Cognitive state optimization',
      'Brainwave entrainment',
      'Enhanced processing capabilities'
    ]
  });
});

// Health Check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'UltraCom NeuroSonix Backend',
    timestamp: new Date().toISOString(),
    neurosonix: 'active'
  });
});

const PORT = process.env.PORT || 8081;

app.listen(PORT, () => {
  console.log(`🧠🎵 UltraCom NeuroSonix Backend started on port ${PORT}`);
  console.log(`🎯 Neural frequency enhancement active`);
  console.log(`🔊 Cognitive amplification system ready`);
});

module.exports = app;
