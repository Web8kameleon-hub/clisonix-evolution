"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cva } from "class-variance-authority";
import { cn } from "../lib/motion-utils";
import { 
  fadeInUp, 
  scaleIn, 
  staggerContainer, 
  staggerItem, 
  albaGlow, 
  jonaGlow,
  buttonVariants 
} from "../lib/motion-utils";

// Demo komponent që përdor të gjitha pakot e instaluara
interface AnimatedDemoProps {
  theme?: "albi" | "jona" | "harmony";
}

const AnimatedDemo: React.FC<AnimatedDemoProps> = ({ theme = "albi" }) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const [counter, setCounter] = React.useState(0);

  React.useEffect(() => {
    setIsVisible(true);
  }, []);

  const stats = [
    { label: "Network Health", value: "94.3%", status: "excellent" },
    { label: "Active Connections", value: "18/20", status: "good" },
    { label: "Avg Latency", value: "12.5ms", status: "excellent" },
    { label: "Uptime", value: "99.8%", status: "excellent" },
  ];

  return (
    <div className={cn(
      "min-h-screen p-6",
      theme === "albi" && "bg-gradient-to-br from-neutral-900 via-neutral-900 to-neutral-900",
      theme === "jona" && "bg-gradient-to-br from-neutral-900 via-red-900 to-neutral-900", 
      theme === "harmony" && "bg-gradient-to-br from-neutral-900 via-purple-900 to-neutral-900"
    )}>
      <motion.div
        initial="initial"
        animate={isVisible ? "animate" : "initial"}
        variants={staggerContainer}
        className="max-w-6xl mx-auto"
      >
        {/* Header */}
        <motion.div
          variants={fadeInUp}
          className="text-center mb-12"
        >
          <motion.h1 
            className={cn(
              "text-4xl font-bold mb-4",
              theme === "albi" && "text-violet-100",
              theme === "jona" && "text-red-100",
              theme === "harmony" && "text-purple-100"
            )}
            variants={scaleIn}
          >
            {theme === "albi" && "💙 Creative Motion Demo"}
            {theme === "jona" && "❤️ Coordinator Motion Demo"}  
            {theme === "harmony" && "🌟 Harmony Motion Demo"}
          </motion.h1>
          
          <motion.p 
            variants={fadeInUp}
            className="text-lg opacity-80"
          >
            Demonstrimi i framer-motion, CVA dhe vanilla-extract
          </motion.p>
        </motion.div>

        {/* Theme Selector */}
        <motion.div
          variants={staggerItem}
          className="flex justify-center gap-4 mb-12"
        >
          <motion.button
            className={buttonVariants({ variant: "alba", size: "lg" })}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            animate={theme === "albi" ? {
              boxShadow: [
                "0 0 20px rgba(59, 130, 246, 0.5)",
                "0 0 30px rgba(59, 130, 246, 0.8)",
                "0 0 20px rgba(59, 130, 246, 0.5)",
              ],
              transition: {
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut",
              },
            } : {}}
          >
            💙 Albi Theme
          </motion.button>
          
          <motion.button
            className={buttonVariants({ variant: "jona", size: "lg" })}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            animate={theme === "jona" ? {
              boxShadow: [
                "0 0 20px rgba(239, 68, 68, 0.5)",
                "0 0 30px rgba(239, 68, 68, 0.8)",
                "0 0 20px rgba(239, 68, 68, 0.5)",
              ],
              transition: {
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut",
              },
            } : {}}
          >
            ❤️ Jona Theme
          </motion.button>
          
          <motion.button
            className={buttonVariants({ variant: "harmony", size: "lg" })}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🌟 Harmony Theme
          </motion.button>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          variants={staggerContainer}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              variants={staggerItem}
              whileHover={{ 
                scale: 1.05,
                rotateY: 5,
                transition: { duration: 0.2 }
              }}
              className={cn(
                "bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10",
                "hover:bg-white/10 transition-all duration-300"
              )}
            >
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="text-sm opacity-70 mb-2">{stat.label}</div>
                <div className={cn(
                  "text-2xl font-bold mb-2",
                  stat.status === "excellent" && "text-green-400",
                  stat.status === "good" && "text-yellow-400",
                  stat.status === "fair" && "text-orange-400",
                  stat.status === "poor" && "text-red-400"
                )}>
                  {stat.value}
                </div>
                <motion.div
                  className={cn(
                    "w-2 h-2 rounded-full",
                    stat.status === "excellent" && "bg-green-400",
                    stat.status === "good" && "bg-yellow-400",
                    stat.status === "fair" && "bg-orange-400",
                    stat.status === "poor" && "bg-red-400"
                  )}
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [1, 0.7, 1],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                />
              </motion.div>
            </motion.div>
          ))}
        </motion.div>

        {/* Interactive Counter */}
        <motion.div
          variants={scaleIn}
          className="bg-white/5 backdrop-blur-lg rounded-xl p-8 text-center mb-12 border border-white/10"
        >
          <motion.h3 
            className="text-2xl font-bold mb-6"
            animate={{
              color: theme === "albi" ? "#3b82f6" : theme === "jona" ? "#ef4444" : "#8b5cf6"
            }}
          >
            Interactive Counter
          </motion.h3>
          
          <motion.div
            key={counter}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-6xl font-bold mb-6"
          >
            {counter}
          </motion.div>
          
          <div className="flex justify-center gap-4">
            <motion.button
              className={buttonVariants({ variant: "secondary" })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCounter(counter - 1)}
            >
              Decrement
            </motion.button>
            
            <motion.button
              className={buttonVariants({ 
                variant: theme === "albi" ? "alba" : theme === "jona" ? "jona" : "default" 
              })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCounter(counter + 1)}
            >
              Increment
            </motion.button>
          </div>
        </motion.div>

        {/* Animated List */}
        <motion.div
          variants={staggerContainer}
          className="bg-white/5 backdrop-blur-lg rounded-xl p-8 border border-white/10"
        >
          <motion.h3 
            variants={fadeInUp}
            className="text-2xl font-bold mb-6"
          >
            Animated Features
          </motion.h3>
          
          <motion.ul
            variants={staggerContainer}
            className="space-y-4"
          >
            {[
              "✅ Framer Motion Animations",
              "✨ Class Variance Authority (CVA)",
              "🎨 Vanilla Extract CSS-in-JS", 
              "🔄 Conditional Classes with clsx",
              "🎯 Type-safe Variants",
              "🌊 Smooth Transitions"
            ].map((feature, index) => (
              <motion.li
                key={feature}
                variants={staggerItem}
                whileHover={{ x: 10, color: theme === "albi" ? "#3b82f6" : theme === "jona" ? "#ef4444" : "#8b5cf6" }}
                className="text-lg cursor-pointer flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors"
              >
                <motion.span
                  animate={{
                    rotate: [0, 360],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "linear",
                    delay: index * 0.2,
                  }}
                >
                  {feature.split(" ")[0]}
                </motion.span>
                {feature.substring(feature.indexOf(" ") + 1)}
              </motion.li>
            ))}
          </motion.ul>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default AnimatedDemo;

