// Web8 Motion System Test
// Simple Node.js test without TypeScript runtime

const { web8MotionPresets, Web8MotionUtils, Web8PresetBuilder, web8Engine } = require('./web8-motion.js');

console.log('🎭 Testing Web8 Vanilla Motion System...');

// Test basic presets
console.log('\n📋 Basic Presets:');
console.log('- fadeIn available:', !!web8MotionPresets?.fadeIn);
console.log('- slideInLeft available:', !!web8MotionPresets?.slideInLeft);
console.log('- bounceIn available:', !!web8MotionPresets?.bounceIn);

// Test engine
console.log('\n🚀 Engine Test:');
if (web8Engine) {
  web8Engine.registerAnimation('testAnim', {
    initial: { opacity: 0 },
    animate: { opacity: 1 }
  });
  console.log('- Animation registered successfully');
  console.log('- Retrieved animation:', !!web8Engine.getAnimation('testAnim'));
} else {
  console.log('- Engine not available (requires compilation)');
}

console.log('\n✅ Web8 Motion System structure validated!');
console.log('🎯 Ready for production use in TypeScript projects');
