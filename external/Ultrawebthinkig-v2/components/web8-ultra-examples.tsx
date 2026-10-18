'use client';

/**
 * 🎬 Web8 Ultra Motion v9 - Usage Examples
 * Complete implementation guide for production use
 */

import React, { useState } from 'react';
import {
  Web8MotionProvider,
  Parallax3D,
  MagneticButton,
  ScrollLinkedHero,
  Web8StatCard,
  FlipList,
  MorphIcon,
  PhysicsCard,
  RevealOnScroll,
  SmartReveal,
  RoutePresence,
  Presets,
  V
} from '@/lib/web8-ultra-motion-v9';

// Example 1: Hero Section with Parallax
export const UltraHeroSection: React.FC = () => {
  return (
    <ScrollLinkedHero style={{ 
      padding: '4rem 2rem', 
      textAlign: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center'
    }}>
      <SmartReveal>
        <h1 style={{ fontSize: '4rem', fontWeight: 900, marginBottom: '1rem' }}>
          UltraWebThinking
        </h1>
        <p style={{ fontSize: '1.5rem', opacity: 0.9, marginBottom: '2rem' }}>
          Next-generation AGI Mesh Platform
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <MagneticButton 
            style={{ 
              padding: '1rem 2rem',
              backgroundColor: 'white',
              color: '#667eea',
              border: 'none',
              borderRadius: '12px',
              fontSize: '1.1rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Start Building
          </MagneticButton>
          <MagneticButton 
            strength={50}
            style={{ 
              padding: '1rem 2rem',
              backgroundColor: 'transparent',
              color: 'white',
              border: '2px solid white',
              borderRadius: '12px',
              fontSize: '1.1rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Learn More
          </MagneticButton>
        </div>
      </SmartReveal>
    </ScrollLinkedHero>
  );
};

// Example 2: Stats Dashboard
export const StatsGrid: React.FC = () => {
  return (
    <section style={{ 
      padding: '3rem 2rem',
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '1.5rem',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      <Web8StatCard 
        title="System Health"
        value="99.7%"
        hint="ALBA/ASI Production Ready"
        className="stat-card"
      />
      <Web8StatCard 
        title="Real-time Processing"
        value="18,429/s"
        hint="IoT Data Points"
        className="stat-card"
      />
      <Web8StatCard 
        title="AI Efficiency"
        value="97.2%"
        hint="Neural Network Optimization"
        className="stat-card"
      />
      <Web8StatCard 
        title="Global Reach"
        value="156 Countries"
        hint="Active Deployments"
        className="stat-card"
      />
    </section>
  );
};

// Example 3: Interactive Navigation
export const NavigationToggle: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const hamburgerPaths = [
    "M4 6h16M4 12h16M4 18h16", // hamburger
    "M6 6l12 12M18 6l-12 12"  // close
  ];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <MagneticButton
        onClick={() => setIsOpen(!isOpen)}
        style={{
          padding: '0.75rem',
          backgroundColor: '#f3f4f6',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer'
        }}
      >
        <MorphIcon 
          paths={hamburgerPaths}
          activeIndex={isOpen ? 1 : 0}
          size={24}
          stroke="#374151"
          strokeWidth={2}
        />
      </MagneticButton>
      <span style={{ fontSize: '1.1rem', fontWeight: 500 }}>
        {isOpen ? 'Close Menu' : 'Open Menu'}
      </span>
    </div>
  );
};

// Example 4: Dynamic Task List
export const TaskManager: React.FC = () => {
  const [tasks, setTasks] = useState([
    { id: 1, title: 'Deploy AGI System', status: 'completed' },
    { id: 2, title: 'Optimize Neural Networks', status: 'in-progress' },
    { id: 3, title: 'Setup IoT Monitoring', status: 'pending' },
    { id: 4, title: 'Configure Security Layer', status: 'pending' }
  ]);

  const addTask = () => {
    const newTask = {
      id: Date.now(),
      title: `New Task ${tasks.length + 1}`,
      status: 'pending'
    };
    setTasks(prev => [newTask, ...prev]);
  };

  const removeTask = (id: number) => {
    setTasks(prev => prev.filter(task => task.id !== id));
  };

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '0 1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Task Manager</h2>
        <MagneticButton
          onClick={addTask}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '0.9rem',
            fontWeight: 500,
            cursor: 'pointer'
          }}
        >
          Add Task
        </MagneticButton>
      </div>

      <FlipList
        items={tasks}
        getKey={task => task.id}
        render={task => (
          <div style={{
            padding: '1rem',
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            marginBottom: '0.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0 }}>
                {task.title}
              </h3>
              <span style={{
                fontSize: '0.85rem',
                padding: '0.25rem 0.5rem',
                borderRadius: '4px',
                backgroundColor: task.status === 'completed' ? '#dcfce7' : 
                               task.status === 'in-progress' ? '#fef3c7' : '#f3f4f6',
                color: task.status === 'completed' ? '#166534' :
                       task.status === 'in-progress' ? '#92400e' : '#374151'
              }}>
                {task.status}
              </span>
            </div>
            <MagneticButton
              onClick={() => removeTask(task.id)}
              style={{
                padding: '0.5rem',
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.8rem',
                cursor: 'pointer'
              }}
            >
              Remove
            </MagneticButton>
          </div>
        )}
      />
    </div>
  );
};

// Example 5: Physics Playground
export const PhysicsDemo: React.FC = () => {
  return (
    <section style={{ padding: '3rem 2rem', textAlign: 'center' }}>
      <RevealOnScroll>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '2rem' }}>
          Interactive Physics Cards
        </h2>
        <p style={{ fontSize: '1.2rem', color: '#6b7280', marginBottom: '3rem' }}>
          Drag these cards around and watch the physics simulation!
        </p>
      </RevealOnScroll>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '2rem',
        maxWidth: '800px',
        margin: '0 auto'
      }}>
        <PhysicsCard style={{
          padding: '2rem',
          backgroundColor: '#f0f9ff',
          border: '2px solid #0ea5e9',
          borderRadius: '16px',
          cursor: 'grab'
        }}>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 600, color: '#0c4a6e' }}>
            Drag Me!
          </h3>
          <p style={{ color: '#075985', marginTop: '0.5rem' }}>
            Physics-based interaction
          </p>
        </PhysicsCard>

        <PhysicsCard bounce={0.1} style={{
          padding: '2rem',
          backgroundColor: '#fef7ff',
          border: '2px solid #d946ef',
          borderRadius: '16px',
          cursor: 'grab'
        }}>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 600, color: '#86198f' }}>
            Less Bounce
          </h3>
          <p style={{ color: '#a21caf', marginTop: '0.5rem' }}>
            Configurable physics
          </p>
        </PhysicsCard>

        <PhysicsCard bounce={0.8} style={{
          padding: '2rem',
          backgroundColor: '#f0fdf4',
          border: '2px solid #22c55e',
          borderRadius: '16px',
          cursor: 'grab'
        }}>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 600, color: '#15803d' }}>
            Super Bouncy!
          </h3>
          <p style={{ color: '#16a34a', marginTop: '0.5rem' }}>
            High bounce factor
          </p>
        </PhysicsCard>
      </div>
    </section>
  );
};

// Main App Example
export const Web8UltraMotionApp: React.FC = () => {
  return (
    <Web8MotionProvider>
      <RoutePresence>
        <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
          <UltraHeroSection />
          <StatsGrid />
          
          <section style={{ padding: '3rem 2rem', maxWidth: '1200px', margin: '0 auto' }}>
            <RevealOnScroll>
              <h2 style={{ fontSize: '2.5rem', fontWeight: 700, textAlign: 'center', marginBottom: '3rem' }}>
                Interactive Components
              </h2>
            </RevealOnScroll>
            
            <div style={{ display: 'grid', gap: '3rem' }}>
              <Parallax3D style={{ 
                padding: '2rem', 
                backgroundColor: 'white', 
                borderRadius: '16px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}>
                <NavigationToggle />
              </Parallax3D>
              
              <TaskManager />
            </div>
          </section>

          <PhysicsDemo />
        </div>
      </RoutePresence>
    </Web8MotionProvider>
  );
};

export default Web8UltraMotionApp;
