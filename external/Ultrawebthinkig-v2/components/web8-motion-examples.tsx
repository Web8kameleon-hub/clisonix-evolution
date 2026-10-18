/**
 * 🎬 WEB8 MOTION - REACT INTEGRATION EXAMPLE
 * How to use the vanilla motion system with React + framer-motion
 */

import React from 'react';
import { motion } from 'framer-motion';
import { 
  web8MotionPresets, 
  motionVariants, 
  Web8PresetBuilder, 
  web8Engine,
  cn
} from '@/lib/web8-motion';

// Example 1: Using prebuilt presets
export const FadeInCard: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className 
}) => {
  return (
    <motion.div
      className={cn('p-6 rounded-lg bg-white shadow-lg', className)}
      {...web8MotionPresets.fadeIn}
    >
      {children}
    </motion.div>
  );
};

// Example 2: Using CSS classes with motion variants
export const AnimatedButton: React.FC<{ 
  children: React.ReactNode; 
  onClick?: () => void;
  variant?: 'fadeIn' | 'bounceIn' | 'scaleIn';
  speed?: 'slow' | 'normal' | 'fast';
}> = ({ 
  children, 
  onClick, 
  variant = 'fadeIn',
  speed = 'normal'
}) => {
  const animationClasses = motionVariants({ 
    animation: variant, 
    speed,
    easing: 'smooth' 
  });

  return (
    <motion.button
      className={cn(
        'px-4 py-2 bg-blue-500 text-white rounded-md',
        animationClasses
      )}
      onClick={onClick}
      {...web8MotionPresets.bounceIn}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {children}
    </motion.button>
  );
};

// Example 3: Using preset builder for custom animations
export const CustomHeroSection: React.FC<{ title: string; subtitle: string }> = ({ 
  title, 
  subtitle 
}) => {
  const heroAnimation = Web8PresetBuilder
    .fadeIn()
    .initial({ opacity: 0, y: 50, scale: 0.9 })
    .animate({ opacity: 1, y: 0, scale: 1 })
    .transition({ duration: 0.8, type: 'spring', stiffness: 100 })
    .build();

  const subtitleAnimation = Web8PresetBuilder
    .slideIn()
    .transition({ delay: 0.3 })
    .build();

  return (
    <section className="hero-section py-20 text-center">
      <motion.h1
        className="text-5xl font-bold mb-4"
        {...heroAnimation}
      >
        {title}
      </motion.h1>
      
      <motion.p
        className="text-xl text-gray-600"
        {...subtitleAnimation}
      >
        {subtitle}
      </motion.p>
    </section>
  );
};

// Example 4: Staggered list animation
export const StaggeredList: React.FC<{ items: string[] }> = ({ items }) => {
  return (
    <motion.ul
      className="space-y-4"
      {...web8MotionPresets.staggerContainer}
    >
      {items.map((item, index) => (
        <motion.li
          key={index}
          className="p-4 bg-gray-100 rounded-lg"
          {...web8MotionPresets.staggerItem}
        >
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
};

// Example 5: Advanced component with engine integration
export const InteractiveCard: React.FC<{ 
  title: string; 
  content: string;
  id: string; 
}> = ({ title, content, id }) => {
  React.useEffect(() => {
    // Register custom animation with engine
    web8Engine.registerAnimation(`card-${id}`, {
      initial: { opacity: 0, rotateY: -90 },
      animate: { opacity: 1, rotateY: 0 },
      exit: { opacity: 0, rotateY: 90 },
      transition: { duration: 0.6, type: 'spring' }
    });
  }, [id]);

  const cardAnimation = web8Engine.getAnimation(`card-${id}`) || web8MotionPresets.fadeIn;

  return (
    <motion.div
      className="card p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl shadow-md"
      {...cardAnimation}
      whileHover={{
        scale: 1.02,
        rotateY: 5,
        boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
      }}
      whileTap={{ scale: 0.98 }}
    >
      <motion.h3 
        className="text-2xl font-semibold mb-3"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        {title}
      </motion.h3>
      
      <motion.p 
        className="text-gray-700"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        {content}
      </motion.p>
    </motion.div>
  );
};

// Example 6: Page transitions wrapper
export const PageTransition: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{
        type: "spring",
        stiffness: 260,
        damping: 20
      }}
      className="page-transition"
    >
      {children}
    </motion.div>
  );
};

// Usage Example Component
export const MotionShowcase: React.FC = () => {
  const listItems = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];

  return (
    <PageTransition>
      <div className="space-y-8 p-8">
        <CustomHeroSection 
          title="Web8 Motion System"
          subtitle="Industrial-grade animations with TypeScript power"
        />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FadeInCard>
            <h3 className="text-lg font-semibold mb-2">Fade In Card</h3>
            <p>This card uses the fadeIn preset from Web8 Motion.</p>
          </FadeInCard>
          
          <InteractiveCard 
            id="demo-card"
            title="Interactive Card"
            content="This card has custom animations registered with the Web8 engine."
          />
        </div>
        
        <div className="flex gap-4">
          <AnimatedButton variant="fadeIn" speed="fast">
            Fade Button
          </AnimatedButton>
          <AnimatedButton variant="bounceIn" speed="normal">
            Bounce Button
          </AnimatedButton>
          <AnimatedButton variant="scaleIn" speed="slow">
            Scale Button
          </AnimatedButton>
        </div>
        
        <StaggeredList items={listItems} />
      </div>
    </PageTransition>
  );
};

export default MotionShowcase;

/**
 * 📝 USAGE NOTES:
 * 
 * 1. Import Web8 motion utilities from @/lib/web8-motion
 * 2. Use presets with framer-motion's motion components
 * 3. Combine CSS classes using motionVariants function
 * 4. Build custom animations with Web8PresetBuilder
 * 5. Register complex animations with web8Engine
 * 6. Mix and match with framer-motion's native props
 * 
 * 🎯 BENEFITS:
 * - Type-safe animation configurations
 * - Consistent motion design system
 * - Zero external dependencies beyond framer-motion
 * - Flexible and extensible architecture
 * - Production-ready performance
 */
