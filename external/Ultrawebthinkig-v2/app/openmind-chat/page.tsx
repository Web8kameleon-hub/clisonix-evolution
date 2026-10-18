'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import OpenMindChat from '../../components/OpenMindChat';

export default function OpenMindChatPage() {
  return (
    <div className="openmind-page">
      <motion.header 
        className="page-header"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="header-content">
          <Link href="/" className="back-link">
            <span>← Back to Dashboard</span>
          </Link>
          <h1 className="page-title">
            🧠 OpenMind AI Chat Platform
          </h1>
          <p className="page-subtitle">
            Multi-Provider AI Chat Interface - Connect with Leading AI Models
          </p>
        </div>
      </motion.header>

      <motion.main 
        className="page-main"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <div className="chat-container">
          <OpenMindChat />
        </div>

        <div className="features-grid">
          <motion.div 
            className="feature-card"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <h3>🤖 Multiple AI Providers</h3>
            <p>Connect with OpenMind AI, Claude, GPT-4, and more leading AI models</p>
          </motion.div>

          <motion.div 
            className="feature-card"
            initial={{ opacity: 0, x: 0 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <h3>⚡ Real-time Responses</h3>
            <p>Get instant responses with sub-second latency and streaming support</p>
          </motion.div>

          <motion.div 
            className="feature-card"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <h3>🔒 Secure & Private</h3>
            <p>Enterprise-grade security with end-to-end encryption</p>
          </motion.div>
        </div>
      </motion.main>

      <style jsx global>{`
        .openmind-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #0a0f1c 0%, #1a2332 50%, #0d1117 100%);
          color: #ffffff;
          font-family: 'JetBrains Mono', monospace;
        }

        .page-header {
          padding: 40px 20px;
          text-align: center;
          background: rgba(0, 255, 255, 0.05);
          border-bottom: 1px solid #00ffff22;
        }

        .header-content {
          max-width: 1200px;
          margin: 0 auto;
        }

        .back-link {
          display: inline-flex;
          align-items: center;
          color: #00ffff;
          text-decoration: none;
          margin-bottom: 20px;
          padding: 8px 16px;
          border: 1px solid #00ffff44;
          border-radius: 20px;
          transition: all 0.3s ease;
        }

        .back-link:hover {
          background: rgba(0, 255, 255, 0.1);
          box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        }

        .page-title {
          font-size: 3rem;
          margin: 20px 0;
          background: linear-gradient(135deg, #00ffff, #0099cc);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          text-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
        }

        .page-subtitle {
          font-size: 1.2rem;
          color: #cccccc;
          margin-bottom: 30px;
          max-width: 600px;
          margin-left: auto;
          margin-right: auto;
          line-height: 1.5;
        }

        .page-main {
          padding: 40px 20px;
        }

        .chat-container {
          max-width: 1200px;
          margin: 0 auto 60px auto;
        }

        .features-grid {
          max-width: 1000px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 30px;
          padding: 20px;
        }

        .feature-card {
          padding: 30px;
          background: rgba(0, 255, 255, 0.05);
          border: 1px solid #00ffff22;
          border-radius: 15px;
          text-align: center;
          transition: all 0.3s ease;
        }

        .feature-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 30px rgba(0, 255, 255, 0.15);
          border-color: #00ffff44;
        }

        .feature-card h3 {
          color: #00ffff;
          margin-bottom: 15px;
          font-size: 1.4rem;
        }

        .feature-card p {
          color: #cccccc;
          line-height: 1.6;
          margin: 0;
        }

        @media (max-width: 768px) {
          .page-title {
            font-size: 2rem;
          }
          
          .page-subtitle {
            font-size: 1rem;
          }
          
          .features-grid {
            grid-template-columns: 1fr;
            gap: 20px;
          }
          
          .feature-card {
            padding: 20px;
          }
        }
      `}</style>
    </div>
  );
}
