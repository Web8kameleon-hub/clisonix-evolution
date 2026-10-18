'use client';

/**
 * 🚀 WEB8 ULTRA MOTION SYSTEM v9.0
 * - Framer Motion advanced suite  
 * - Real-world presets (A11y, perf, SSR-safe)
 * - 3D Parallax, Scroll, Gestures, FLIP, Morphing
 * - Advanced Physics & Real-time Animations
 * 
 * @version 9.0.0 ULTRA MOTION
 * @author UltraWebThinking Team
 */

import React, {
  createContext, useCallback, useContext, useEffect,
  useLayoutEffect, useMemo, useRef, useState
} from 'react';
import {
  motion, AnimatePresence, useAnimationControls, useMotionValue,
  useSpring, useTransform, useVelocity, useScroll, useInView,
  useMotionTemplate, useAnimate, Variants, Transition, PanInfo
} from 'framer-motion';

/* ----------------------------- A11y / Context ----------------------------- */

interface MotionContextValue {
  reducedMotion: boolean;
  spring: Transition;
  bouncy: Transition;
  smooth: Transition;
  ultra: Transition;
}

const MotionCtx = createContext<MotionContextValue | null>(null);

export const Web8MotionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const apply = () => setReducedMotion(mq.matches);
    apply();
    mq.addEventListener?.('change', apply);
    return () => mq.removeEventListener?.('change', apply);
  }, []);

  const value = useMemo<MotionContextValue>(() => ({
    reducedMotion,
    spring: { type: 'spring', stiffness: 300, damping: 28 },
    bouncy: { type: 'spring', stiffness: 520, damping: 18 },
    smooth: { duration: 0.32, ease: [0.22, 0.61, 0.36, 1] },
    ultra:  { type: 'spring', stiffness: 800, damping: 24 }
  }), [reducedMotion]);

  return React.createElement(MotionCtx.Provider, { value }, children);
};

export const useWeb8Motion = () => {
  const ctx = useContext(MotionCtx);
  if (!ctx) throw new Error('Wrap tree with <Web8MotionProvider>');
  return ctx;
};

/* --------------------------------- Utils ---------------------------------- */

export const raf = (fn: () => void) => {
  let a = 0;
  const tick = () => { fn(); a = requestAnimationFrame(tick); };
  a = requestAnimationFrame(tick);
  return () => cancelAnimationFrame(a);
};

export const useSSRLayoutEffect = typeof window !== 'undefined' ? useLayoutEffect : useEffect;

export function clamp(n: number, min: number, max: number) {
  return Math.min(max, Math.max(min, n));
}

/* ------------------------------- Variants --------------------------------- */

export const V: Record<string, Variants> = {
  fade: {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 0.25 } }
  },
  rise: {
    hidden: { opacity: 0, y: 24 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.32, ease: [0.22, 0.61, 0.36, 1] } }
  },
  scale: {
    hidden: { opacity: 0, scale: 0.9 },
    visible: { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 420, damping: 28 } }
  },
  flipItem: {
    hidden: { opacity: 0, rotateX: -12, y: 10 },
    visible: { opacity: 1, rotateX: 0, y: 0, transition: { type: 'spring', stiffness: 520, damping: 30 } },
    exit:   { opacity: 0, rotateX: 8, y: -10, transition: { duration: 0.18 } }
  },
  route: {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.26 } },
    exit:    { opacity: 0, y: -8, transition: { duration: 0.2 } }
  }
};

/* ----------------------------- Parallax3D Card ---------------------------- */

interface Parallax3DProps extends React.HTMLAttributes<HTMLDivElement> {
  depth?: number; // deg max tilt
  glare?: boolean;
  hoverScale?: number;
}

export const Parallax3D: React.FC<Parallax3DProps> = ({
  depth = 10, glare = true, hoverScale = 1.02, children, style, ...rest
}) => {
  const { reducedMotion } = useWeb8Motion();
  const ref = useRef<HTMLDivElement>(null);
  const rx = useMotionValue(0);
  const ry = useMotionValue(0);
  const s  = useSpring(1, { stiffness: 320, damping: 26 });

  const glow = useMotionTemplate`radial-gradient(600px 200px at ${useTransform(ry, v => 50 + v*2)}% ${useTransform(rx, v => 50 - v*2)}%, rgba(255,255,255,0.25), transparent 60%)`;

  const onMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left, y = e.clientY - rect.top;
    const px = x / rect.width, py = y / rect.height;
    rx.set((py - 0.5) * depth);
    ry.set((px - 0.5) * depth);
  };
  const onLeave = () => { rx.set(0); ry.set(0); s.set(1); };
  const onEnter = () => { s.set(hoverScale); };

  return React.createElement(motion.div, {
    ref,
    onMouseMove: reducedMotion ? undefined : onMove,
    onMouseLeave: onLeave,
    onMouseEnter: onEnter,
    style: {
      perspective: 1000,
      transformStyle: 'preserve-3d',
      ...style
    },
    ...rest
  }, React.createElement(motion.div, {
    style: {
      rotateX: reducedMotion ? 0 : rx,
      rotateY: reducedMotion ? 0 : ry,
      scale: s,
      willChange: 'transform'
    },
    className: 'web8-parallax3d'
  }, [
    glare && !reducedMotion && React.createElement(motion.div, {
      key: 'glare',
      'aria-hidden': true,
      style: {
        pointerEvents: 'none',
        position: 'absolute',
        inset: 0,
        borderRadius: 12,
        backgroundImage: glow,
        mixBlendMode: 'soft-light'
      }
    }),
    children
  ].filter(Boolean)));
};

/* --------------------------- Magnetic / Drag Card ------------------------- */

interface MagneticButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  strength?: number; // px attraction
}

export const MagneticButton: React.FC<MagneticButtonProps> = ({ 
  strength = 30, children, style, ...rest 
}) => {
  const { bouncy, reducedMotion } = useWeb8Motion();
  const x = useSpring(0, { stiffness: 400, damping: 22 });
  const y = useSpring(0, { stiffness: 400, damping: 22 });

  const ref = useRef<HTMLButtonElement>(null);
  const onMove = (e: React.MouseEvent) => {
    if (reducedMotion || !ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const dx = e.clientX - (r.left + r.width / 2);
    const dy = e.clientY - (r.top + r.height / 2);
    x.set(clamp(dx, -strength, strength));
    y.set(clamp(dy, -strength, strength));
  };
  const reset = () => { x.set(0); y.set(0); };

  return React.createElement(motion.button, {
    ref,
    onMouseMove: onMove,
    onMouseLeave: reset,
    onFocus: reset,
    whileTap: { scale: reducedMotion ? 1 : 0.96 },
    transition: bouncy,
    style: { x, y, ...style },
    ...rest
  }, children);
};

/* ----------------------------- Scroll Animations -------------------------- */

interface RevealOnScrollProps extends React.HTMLAttributes<HTMLDivElement> {
  once?: boolean;
  variant?: Variants;
  threshold?: number;
}

export const RevealOnScroll: React.FC<RevealOnScrollProps> = ({
  once = true, variant = V.rise, threshold = 0.2, children, ...rest
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { margin: '0px 0px -10% 0px', amount: threshold, once });
  
  return React.createElement(motion.div, {
    ref,
    variants: variant,
    initial: 'hidden',
    animate: inView ? 'visible' : 'hidden',
    ...rest
  }, children);
};

export const ScrollLinkedHero: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ 
  children, style, ...rest 
}) => {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, 120]);
  const blur = useTransform(scrollYProgress, [0, 1], [0, 8]);
  const opacity = useTransform(scrollYProgress, [0, 1], [1, 0.65]);
  
  return React.createElement(motion.section, {
    style: { 
      y, 
      filter: useMotionTemplate`blur(${blur}px)`, 
      opacity, 
      ...style 
    },
    ...rest
  }, children);
};

/* ------------------------------ FLIP / Layout ----------------------------- */

interface FlipListProps<T> {
  items: T[];
  getKey: (t: T) => React.Key;
  render: (t: T) => React.ReactNode;
}

export function FlipList<T>({ items, getKey, render }: FlipListProps<T>) {
  return React.createElement(motion.ul, {
    layout: true,
    style: { listStyle: 'none', margin: 0, padding: 0 }
  }, React.createElement(AnimatePresence, { initial: false },
    items.map(item => 
      React.createElement(motion.li, {
        key: getKey(item),
        layout: true,
        variants: V.flipItem,
        initial: 'hidden',
        animate: 'visible',
        exit: 'exit',
        style: { borderRadius: 12, overflow: 'hidden' }
      }, render(item))
    )
  ));
}

/* ------------------------------ Path Morphing ----------------------------- */

interface MorphIconProps {
  paths: string[];          // lista e d-attributes
  activeIndex: number;      // cili path është aktiv
  size?: number;
  stroke?: string;
  strokeWidth?: number;
}

export const MorphIcon: React.FC<MorphIconProps> = ({
  paths, activeIndex, size = 24, stroke = 'currentColor', strokeWidth = 2
}) => {
  const { spring } = useWeb8Motion();
  const d = useMotionValue(paths[0] || '');
  
  useEffect(() => { 
    d.set(paths[activeIndex] || paths[0] || ''); 
  }, [activeIndex, paths, d]);

  return React.createElement(motion.svg, {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke,
    strokeWidth
  }, React.createElement(motion.path, {
    d: d as unknown as string,
    transition: spring,
    strokeLinecap: 'round',
    strokeLinejoin: 'round'
  }));
};

/* --------------------------- Gesture Physics Card ------------------------- */

interface PhysicsCardProps extends React.HTMLAttributes<HTMLDivElement> {
  bounce?: number; // 0..1
}

export const PhysicsCard: React.FC<PhysicsCardProps> = ({ 
  bounce = 0.25, children, style, ...rest 
}) => {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const vx = useVelocity(x);
  const vy = useVelocity(y);

  const onDragEnd = (_: any, info: PanInfo) => {
    // Fling inertial based on velocity
    const flingX = clamp(info.velocity.x / 4, -500, 500);
    const flingY = clamp(info.velocity.y / 4, -500, 500);
    x.set(flingX); y.set(flingY);
    const stop = raf(() => {
      x.set(x.get() * (1 - bounce));
      y.set(y.get() * (1 - bounce));
      if (Math.hypot(vx.get(), vy.get()) < 5 && Math.hypot(x.get(), y.get()) < 1) stop();
    });
  };

  return React.createElement(motion.div, {
    drag: true,
    dragConstraints: { left: -80, right: 80, top: -60, bottom: 60 },
    onDragEnd,
    style: { x, y, ...style },
    whileTap: { scale: 0.98 },
    transition: { type: 'spring', stiffness: 380, damping: 30 },
    ...rest
  }, children);
};

/* ------------------------- Route / Section Orchestration ------------------ */

export const RoutePresence: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  React.createElement(AnimatePresence, { mode: 'wait' },
    React.createElement(motion.div, {
      key: (typeof window !== 'undefined') ? location.pathname : 'route',
      variants: V.route,
      initial: 'initial',
      animate: 'animate',
      exit: 'exit'
    }, children)
  )
);

/* -------------------------- Smart Reveal (Real) --------------------------- */

interface SmartRevealProps extends React.HTMLAttributes<HTMLDivElement> {
  delayPerChild?: number;
  stagger?: number;
}

export const SmartReveal: React.FC<SmartRevealProps> = ({ 
  children, delayPerChild = 0.06, stagger = 0.06, ...rest 
}) => {
  const { reducedMotion } = useWeb8Motion();
  const [scope, animate] = useAnimate();
  
  useEffect(() => {
    if (reducedMotion) return;
    const els = Array.from(scope.current?.children || []);
    els.forEach((el, i) => {
      animate(el, 
        { opacity: [0, 1], y: [8, 0] }, 
        { duration: 0.32, delay: i * delayPerChild, ease: [0.22, 0.61, 0.36, 1] }
      );
    });
  }, [animate, delayPerChild, reducedMotion, scope]);
  
  return React.createElement('div', { ref: scope, ...rest }, children);
};

/* ------------------------------- Presets API ------------------------------ */

export const Presets = {
  FadeIn: (p: React.HTMLAttributes<HTMLDivElement>) => 
    React.createElement(motion.div, {
      variants: V.fade,
      initial: 'hidden',
      whileInView: 'visible',
      viewport: { once: true, margin: '-10% 0px' },
      ...p
    }),
    
  Rise: (p: React.HTMLAttributes<HTMLDivElement>) => 
    React.createElement(motion.div, {
      variants: V.rise,
      initial: 'hidden',
      whileInView: 'visible',
      viewport: { once: true },
      ...p
    }),
    
  ScaleIn: (p: React.HTMLAttributes<HTMLDivElement>) => 
    React.createElement(motion.div, {
      variants: V.scale,
      initial: 'hidden',
      whileInView: 'visible',
      viewport: { once: true },
      ...p
    })
};

/* ------------------------------ Example Cards ----------------------------- */

export const Web8StatCard: React.FC<{ 
  title: string; 
  value: string | number; 
  hint?: string; 
  className?: string; 
}> = ({ title, value, hint, className }) => {
  const { smooth } = useWeb8Motion();
  
  return React.createElement(Parallax3D, {
    className,
    style: { position: 'relative' }
  }, React.createElement(motion.div, {
    className: 'card',
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0, transition: smooth },
    style: { 
      padding: 14, 
      borderRadius: 12, 
      border: '1px solid #e5e7eb', 
      background: '#fff' 
    }
  }, [
    React.createElement('div', {
      key: 'title',
      style: { fontSize: 12, color: '#6b7280' }
    }, title),
    React.createElement('div', {
      key: 'value',
      style: { fontSize: 28, fontWeight: 700 }
    }, value),
    hint && React.createElement('div', {
      key: 'hint',
      style: { fontSize: 12, color: '#6b7280' }
    }, hint)
  ].filter(Boolean)));
};

/* ------------------------------- Legacy Compatibility ----------------------- */

// Backward compatibility with v8 API
export const web8Variants = V;
export const web8Transitions = {
  smooth: { duration: 0.32, ease: [0.22, 0.61, 0.36, 1] },
  spring: { type: 'spring' as const, stiffness: 300, damping: 28 },
  bouncy: { type: 'spring' as const, stiffness: 520, damping: 18 },
  ultra: { type: 'spring' as const, stiffness: 800, damping: 24 }
};

export const Web8Motion = motion;
export const Web8AnimatePresence = AnimatePresence;
export const useWeb8Animation = useAnimationControls;
export const useWeb8Transform = useTransform;
export const useWeb8MotionValue = useMotionValue;

/* ------------------------------- Main Exports ------------------------------ */

export default {
  Provider: Web8MotionProvider,
  motion,
  AnimatePresence,
  variants: V,
  transitions: web8Transitions,
  components: {
    Parallax3D,
    MagneticButton,
    RevealOnScroll,
    ScrollLinkedHero,
    FlipList,
    MorphIcon,
    PhysicsCard,
    RoutePresence,
    SmartReveal,
    Web8StatCard
  },
  presets: Presets,
  hooks: {
    useWeb8Motion,
    useAnimationControls,
    useMotionValue,
    useSpring,
    useTransform,
    useVelocity,
    useScroll,
    useInView,
    useMotionTemplate,
    useAnimate
  },
  utils: { raf, useSSRLayoutEffect, clamp }
};

// Success logs
console.log('🚀 Web8 Ultra Motion System v9.0 - LOADED SUCCESSFULLY');
console.log('✨ Advanced Features: 3D Parallax, Physics, Morphing, FLIP');
console.log('🔥 Accessibility: Reduced motion support');
console.log('⚡ Performance: SSR-safe, optimized animations');
console.log('🎭 Real-world ready: Production-grade system');
