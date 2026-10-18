'use strict';

/**
 * 🎬 WEB8 MOTION DEMO
 * Showcase of vanilla motion system capabilities
 */

import { 
  web8MotionPresets, 
  Web8MotionUtils, 
  Web8PresetBuilder, 
  web8Engine,
  motionVariants,
  cn
} from './web8-motion';

// Demo: Basic Animation Presets
console.log('🎭 DEMO: Web8 Motion Presets');
console.log('fadeIn config:', web8MotionPresets.fadeIn);
console.log('slideInLeft config:', web8MotionPresets.slideInLeft);
console.log('bounceIn config:', web8MotionPresets.bounceIn);

// Demo: Custom Variant Classes
console.log('\n🎨 DEMO: Variant Class Generation');
const fadeInClasses = motionVariants({ animation: 'fadeIn', speed: 'fast', easing: 'smooth' });
const bounceInClasses = motionVariants({ animation: 'bounceIn', speed: 'slow', easing: 'bouncy' });
console.log('Fade in classes:', fadeInClasses);
console.log('Bounce in classes:', bounceInClasses);

// Demo: Utility Functions
console.log('\n🔧 DEMO: Motion Utilities');
const customVariant = Web8MotionUtils.createVariant('customFade', {
  initial: { opacity: 0, scale: 0.5 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: 0.5 }
});
console.log('Custom variant:', customVariant);

const staggeredAnimation = Web8MotionUtils.createStaggered(
  web8MotionPresets.fadeIn,
  0.2,
  0.1
);
console.log('Staggered animation:', staggeredAnimation);

// Demo: Preset Builder
console.log('\n🏗️ DEMO: Preset Builder');
const customAnimation = Web8PresetBuilder
  .fadeIn()
  .hover({ scale: 1.1, rotateZ: 5 })
  .tap({ scale: 0.9 })
  .transition({ duration: 0.4, type: 'spring' })
  .build();
console.log('Built custom animation:', customAnimation);

const slideAnimation = new Web8PresetBuilder()
  .initial({ x: -100, opacity: 0 })
  .animate({ x: 0, opacity: 1 })
  .exit({ x: 100, opacity: 0 })
  .transition({ duration: 0.6, ease: "easeInOut" })
  .hover({ y: -5 })
  .build();
console.log('Built slide animation:', slideAnimation);

// Demo: Animation Engine
console.log('\n🚀 DEMO: Animation Engine');
web8Engine.registerAnimation('heroEntrance', {
  initial: { opacity: 0, scale: 0.8, y: 50 },
  animate: { opacity: 1, scale: 1, y: 0 },
  transition: { duration: 0.8, type: 'spring', stiffness: 100 }
});

web8Engine.registerAnimation('cardHover', {
  whileHover: { scale: 1.05, y: -10, rotateY: 5 },
  transition: { duration: 0.3 }
});

console.log('Registered animations:', Array.from(web8Engine.getAllAnimations().keys()));
console.log('Hero entrance config:', web8Engine.getAnimation('heroEntrance'));

// Demo: Animation Sequences
web8Engine.playSequence('hero-section', ['heroEntrance', 'cardHover']);

// Demo: Class Name Utility
console.log('\n🎯 DEMO: Class Name Utilities');
const dynamicClasses = cn(
  'base-class',
  true && 'conditional-class',
  false && 'hidden-class',
  'final-class'
);
console.log('Dynamic classes:', dynamicClasses);

// Demo: Advanced Animation Combinations
console.log('\n⚡ DEMO: Advanced Combinations');
const complexVariants = Web8MotionUtils.combineVariants(
  customVariant,
  Web8MotionUtils.createVariant('withRotation', {
    animate: { rotate: 360 },
    transition: { duration: 2 } // Removed repeat for TypeScript compatibility
  })
);
console.log('Combined variants:', complexVariants);

const animationSequence = Web8MotionUtils.createSequence(
  { initial: { opacity: 0, scale: 0.5 }, animate: { opacity: 0.5, scale: 0.8 } },
  { initial: { opacity: 0.5, scale: 0.8 }, animate: { opacity: 1, scale: 1 } },
  { initial: { opacity: 1, scale: 1 }, animate: { opacity: 1, scale: 1 } }
);
console.log('Animation sequence:', animationSequence);

// Demo: CSS Class Integration
console.log('\n🎨 DEMO: CSS Integration Ready');
console.log('Motion variants function ready for use with className props');
console.log('CSS classes auto-injected for immediate styling');

// Export demo functions for testing
export const web8MotionDemo = {
  showBasicPresets: () => console.table(web8MotionPresets),
  testVariants: () => ({
    fadeIn: motionVariants({ animation: 'fadeIn' }),
    bounceIn: motionVariants({ animation: 'bounceIn', speed: 'fast' }),
    slideIn: motionVariants({ animation: 'slideIn', easing: 'smooth' })
  }),
  testEngine: () => {
    web8Engine.playSequence('demo-element', ['fadeIn', 'bounceIn']);
    return web8Engine.getActiveAnimations();
  },
  buildCustom: () => Web8PresetBuilder.scaleIn().hover({ rotate: 10 }).build()
};

console.log('\n✨ Web8 Vanilla Motion Demo Complete!');
console.log('🎯 Ready for production use with zero JSX dependencies');
console.log('🚀 Use with any framework: React, Vue, Svelte, or vanilla JS');
