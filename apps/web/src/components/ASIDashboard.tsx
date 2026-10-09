/**
 * ASI Frontend Components
 * ======================
 * 
 * React components for the ASI (Artificial Superintelligence) system interface
 * using framer-motion, class-variance-authority (cva), and vanilla-extract.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import { cva } from 'class-variance-authority';
import { style, globalStyle, styleVariants } from '@vanilla-extract/css';

// Global styles
globalStyle('*', {
  margin: 0,
  padding: 0,
  boxSizing: 'border-box',
});

globalStyle('body', {
  fontFamily: '"Inter", system-ui, sans-serif',
  backgroundColor: '#0a0a0a',
  color: '#ffffff',
  lineHeight: 1.6,
});

// Styled components with vanilla-extract
const asiContainer = style({
  minHeight: '100vh',
  background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
  padding: '2rem',
  position: 'relative',
  overflow: 'hidden',
});

const headerStyle = style({
  textAlign: 'center',
  marginBottom: '3rem',
  position: 'relative',
  zIndex: 2,
});

const titleStyle = style({
  fontSize: '3.5rem',
  fontWeight: 'bold',
  background: 'linear-gradient(45deg, #00f5ff, #0080ff, #8000ff)',
  backgroundClip: 'text',
  WebkitBackgroundClip: 'text',
  color: 'transparent',
  marginBottom: '1rem',
  textShadow: '0 0 30px rgba(0, 245, 255, 0.3)',
});

const subtitleStyle = style({
  fontSize: '1.2rem',
  color: '#b0b0b0',
  marginBottom: '2rem',
});

const agentGridStyle = style({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
  gap: '2rem',
  marginBottom: '3rem',
  zIndex: 2,
  position: 'relative',
});

const terminalStyle = style({
  backgroundColor: 'rgba(0, 0, 0, 0.8)',
  border: '1px solid #333',
  borderRadius: '12px',
  padding: '1.5rem',
  fontFamily: '"Fira Code", monospace',
  minHeight: '400px',
  backdropFilter: 'blur(10px)',
  position: 'relative',
  zIndex: 2,
});

const backgroundParticle = style({
  position: 'absolute',
  borderRadius: '50%',
  background: 'radial-gradient(circle, rgba(0, 245, 255, 0.1) 0%, transparent 70%)',
  pointerEvents: 'none',
});

const particlePositionVariants = styleVariants({
  p0: { left: '5%', top: '12%', width: '80px', height: '80px' },
  p1: { left: '22%', top: '28%', width: '120px', height: '120px' },
  p2: { left: '45%', top: '18%', width: '100px', height: '100px' },
  p3: { left: '68%', top: '8%', width: '90px', height: '90px' },
  p4: { left: '82%', top: '24%', width: '110px', height: '110px' },
  p5: { left: '12%', top: '55%', width: '130px', height: '130px' },
  p6: { left: '36%', top: '62%', width: '95px', height: '95px' },
  p7: { left: '58%', top: '48%', width: '140px', height: '140px' },
  p8: { left: '78%', top: '60%', width: '105px', height: '105px' },
  p9: { left: '30%', top: '82%', width: '120px', height: '120px' },
} as const);

// CVA button variants
const buttonVariants = cva(
  'px-6 py-3 rounded-lg font-semibold transition-all duration-300 border',
  {
    variants: {
      variant: {
        alba: 'bg-violet-600 hover:bg-violet-700 border-violet-500 text-white',
        albi: 'bg-green-600 hover:bg-green-700 border-green-500 text-white',
        jona: 'bg-purple-600 hover:bg-purple-700 border-purple-500 text-white',
        asi: 'bg-gradient-to-r from-violet-600 via-purple-600 to-green-600 hover:from-violet-700 hover:via-purple-700 hover:to-green-700 border-violet-400 text-white',
        danger: 'bg-red-600 hover:bg-red-700 border-red-500 text-white',
        ghost: 'bg-transparent hover:bg-white/10 border-gray-600 text-gray-300',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-6 py-3 text-base',
        lg: 'px-8 py-4 text-lg',
      },
      disabled: {
        true: 'opacity-50 cursor-not-allowed pointer-events-none',
      },
    },
    defaultVariants: {
      variant: 'asi',
      size: 'md',
    },
  }
);

// Animation variants
const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: 0.3,
      staggerChildren: 0.2,
    },
  },
};

const itemVariants: Variants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 100,
    },
  },
};

const agentCardVariants: Variants = {
  hidden: { scale: 0.8, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 15,
    },
  },
  hover: {
    scale: 1.05,
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 10,
    },
  },
};

type AgentVariant = 'alba' | 'albi' | 'jona';
type AgentStatus = 'active' | 'inactive' | 'processing';

// Style variants
const agentBorderVariants = styleVariants({
  alba: { borderColor: '#00aaff' },
  albi: { borderColor: '#00ff88' },
  jona: { borderColor: '#aa00ff' },
});

const agentTitleVariants = styleVariants({
  alba: { color: '#00aaff' },
  albi: { color: '#00ff88' },
  jona: { color: '#aa00ff' },
});

const agentAccentVariants = styleVariants({
  alba: { backgroundColor: '#00aaff' },
  albi: { backgroundColor: '#00ff88' },
  jona: { backgroundColor: '#aa00ff' },
});

const statusDotVariants = styleVariants({
  active: { backgroundColor: '#00ff88' },
  processing: { backgroundColor: '#ffaa00' },
  inactive: { backgroundColor: '#ff4444' },
});

const statusTextVariants = styleVariants({
  active: { color: '#00ff88' },
  processing: { color: '#ffaa00' },
  inactive: { color: '#ff4444' },
});

// Types
interface Agent {
  name: string;
  role: string;
  status: AgentStatus;
  health: number;
  variant: AgentVariant;
}

interface ASITerminalProps {
  commands: string[];
  onCommand: (command: string) => void;
}

interface AgentCardProps {
  agent: Agent;
  onClick: () => void;
}

// Components
const AgentCard: React.FC<AgentCardProps> = ({ agent, onClick }) => {
  return (
    <motion.div
      className={`bg-gray-900/50 backdrop-blur-sm border rounded-xl p-6 cursor-pointer ${agentBorderVariants[agent.variant]}`}
      variants={agentCardVariants}
      whileHover="hover"
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-xl font-bold ${agentTitleVariants[agent.variant]}`}>
          {agent.name}
        </h3>
        <div 
          className={`w-3 h-3 rounded-full ${statusDotVariants[agent.status]}`}
        />
      </div>
      
      <p className="text-gray-400 mb-4">{agent.role}</p>
      
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Status:</span>
          <span className={statusTextVariants[agent.status]}>
            {agent.status.toUpperCase()}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Health:</span>
          <span className={agent.health > 80 ? 'text-green-400' : agent.health > 50 ? 'text-yellow-400' : 'text-red-400'}>
            {agent.health}%
          </span>
        </div>
      </div>
      
      {/* Health bar */}
      <div className="mt-4 bg-gray-700 rounded-full h-2">
        <motion.div
          className={`h-2 rounded-full ${agentAccentVariants[agent.variant]}`}
          initial={{ width: 0 }}
          animate={{ width: `${agent.health}%` }}
          transition={{ duration: 1, delay: 0.5 }}
        />
      </div>
    </motion.div>
  );
};

const ASITerminal: React.FC<ASITerminalProps> = ({ commands, onCommand }) => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([
    '🤖 ASI Terminal initialized...',
    '🔐 Safety sandbox active',
    '🌐 Network monitoring online',
    '✅ All agents operational',
    '',
    'Type "help" for available commands',
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      setHistory(prev => [...prev, `> ${input}`, '']);
      onCommand(input);
      setInput('');
    }
  };

  useEffect(() => {
    if (commands.length > 0) {
      const latestCommand = commands[commands.length - 1];
      setHistory(prev => [...prev, `✓ ${latestCommand}`, '']);
    }
  }, [commands]);

  return (
    <div className={terminalStyle}>
      <div className="flex items-center mb-4 pb-2 border-b border-gray-700">
        <div className="flex space-x-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
        </div>
        <span className="ml-4 text-gray-400 text-sm">ASI Terminal v1.0</span>
      </div>
      
      <div className="text-sm text-green-400 mb-4 h-64 overflow-y-auto">
        {history.map((line, index) => (
          <div key={index} className="mb-1">
            {line}
          </div>
        ))}
      </div>
      
      <form onSubmit={handleSubmit} className="flex">
        <span className="text-violet-400 mr-2">ASI&gt;</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 bg-transparent text-white outline-none"
          placeholder="Enter command..."
          autoFocus
        />
      </form>
    </div>
  );
};

const particleConfigs = [
  { id: 0, variant: 'p0', duration: 18 },
  { id: 1, variant: 'p1', duration: 22 },
  { id: 2, variant: 'p2', duration: 16 },
  { id: 3, variant: 'p3', duration: 24 },
  { id: 4, variant: 'p4', duration: 20 },
  { id: 5, variant: 'p5', duration: 26 },
  { id: 6, variant: 'p6', duration: 19 },
  { id: 7, variant: 'p7', duration: 23 },
  { id: 8, variant: 'p8', duration: 21 },
  { id: 9, variant: 'p9', duration: 25 },
] as const;

const BackgroundParticles: React.FC = () => (
  <>
    {particleConfigs.map((particle) => (
      <motion.div
        key={particle.id}
        className={`${backgroundParticle} ${particlePositionVariants[particle.variant]}`}
        animate={{
          x: [0, 100, -100, 0],
          y: [0, -100, 100, 0],
          opacity: [0.1, 0.3, 0.1],
        }}
        transition={{
          duration: particle.duration,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
    ))}
  </>
);

// Main ASI Dashboard Component
const ASIDashboard: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([
    {
      name: 'Analytical',
      role: 'Network Infrastructure Monitor',
      status: 'active',
      health: 94,
      variant: 'alba',
    },
    {
      name: 'Creative',
      role: 'Process Automation Engine',
      status: 'active',
      health: 87,
      variant: 'albi',
    },
    {
      name: 'Coordinator',
      role: 'Human-AI Communication Bridge',
      status: 'processing',
      health: 92,
      variant: 'jona',
    },
  ]);

  const [commands, setCommands] = useState<string[]>([]);

  const handleAgentClick = (agent: Agent) => {
    console.log(`Agent ${agent.name} clicked`);
    // Handle agent interaction
  };

  const handleCommand = (command: string) => {
    setCommands(prev => [...prev, command]);
    
    // Simulate command processing
    setTimeout(() => {
      // Update agent status based on command
      if (command.includes('status')) {
        console.log('Status check completed');
      }
    }, 1000);
  };

  return (
    <div className={asiContainer}>
      <BackgroundParticles />
      
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.header className={headerStyle} variants={itemVariants}>
          <h1 className={titleStyle}>ASI System</h1>
          <p className={subtitleStyle}>
            Artificial Superintelligence • Trinity Architecture
          </p>
          <div className="flex justify-center space-x-4">
            <motion.button
              className={buttonVariants({ variant: 'alba', size: 'sm' })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Network Status
            </motion.button>
            <motion.button
              className={buttonVariants({ variant: 'albi', size: 'sm' })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Process Monitor
            </motion.button>
            <motion.button
              className={buttonVariants({ variant: 'jona', size: 'sm' })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              AI Chat
            </motion.button>
          </div>
        </motion.header>

        <motion.div className={agentGridStyle} variants={itemVariants}>
          <AnimatePresence>
            {agents.map((agent) => (
              <AgentCard
                key={agent.name}
                agent={agent}
                onClick={() => handleAgentClick(agent)}
              />
            ))}
          </AnimatePresence>
        </motion.div>

        <motion.div variants={itemVariants}>
          <ASITerminal commands={commands} onCommand={handleCommand} />
        </motion.div>
      </motion.div>
    </div>
  );
};

export default ASIDashboard;

