/**
 * EuroWeb Web8 - Simple Index Component
 * CSS Modules + CVA + Framer Motion Implementation
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.1 Industrial
 * @license MIT
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer } from '../lib/motion';
import styles from './IndexSimple.module.css';

// Pure TypeScript component - NO default export (forbidden)
const IndexSimple = (): React.ReactElement => {
  return (
    <motion.div
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      className={styles.container}
    >
      <motion.div
        variants={fadeInUp}
        className={styles.content}
      >
        <motion.h1
          variants={fadeInUp}
          className={styles.title}
        >
          Web8 UltraThinking
        </motion.h1>
        
        <motion.p
          variants={fadeInUp}
          className={styles.subtitle}
        >
          Kristal Engine Ready
        </motion.p>
        
        <motion.div
          variants={fadeInUp}
          className={styles.statusContainer}
        >
          <motion.div
            animate={{
              opacity: [1, 0.5, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
            className={styles.statusIndicator}
          />
          <span className={styles.statusText}>
            System Active
          </span>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

// Named export (required by EuroWeb Web8 standards)
export { IndexSimple };
