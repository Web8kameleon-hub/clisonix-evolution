// AGI Tunnel Component - Pure TypeScript + Framer Motion - Industrial Grade
import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './AGITunnel.module.css';

interface TunnelNode {
  id: string;
  x: number;
  y: number;
  z: number;
  type: 'input' | 'processing' | 'output' | 'relay';
  intensity: number;
  connections: string[];
}

interface DataFlow {
  from: string;
  to: string;
  data: unknown;
  timestamp: number;
  speed: number;
}

interface AGITunnelProps {
  width?: number;
  height?: number;
  theme?: 'light' | 'dark' | 'agi';
  showDataFlow?: boolean;
  onNodeClick?: (node: TunnelNode) => void;
  onDataFlow?: (flow: DataFlow) => void;
}

const AGITunnel: React.FC<AGITunnelProps> = ({
  width = 800,
  height = 600,
  theme = 'agi',
  showDataFlow = true,
  onNodeClick,
  onDataFlow
}) => {
  // State management with React hooks
  const [nodes, setNodes] = React.useState<TunnelNode[]>([]);
  const [dataFlows, setDataFlows] = React.useState<DataFlow[]>([]);
  const [selectedNode, setSelectedNode] = React.useState<TunnelNode | null>(null);

  // Theme configurations
  const themeConfigs = {
    light: {
      backgroundColor: '#f8f9fa',
      nodeColor: '#6c757d',
      connectionColor: '#adb5bd',
      dataFlowColor: '#007bff',
      textColor: '#212529'
    },
    dark: {
      backgroundColor: '#212529',
      nodeColor: '#6c757d',
      connectionColor: '#495057',
      dataFlowColor: '#0dcaf0',
      textColor: '#f8f9fa'
    },
    agi: {
      backgroundColor: 'rgba(0, 0, 0, 0.95)',
      nodeColor: '#8a2be2',
      connectionColor: '#dda0dd',
      dataFlowColor: '#00ff7f',
      textColor: '#ffffff'
    }
  };

  const config = themeConfigs[theme];

  // Initialize nodes
  const initializeNodes = () => {
    const newNodes: TunnelNode[] = [
      // Input layer
      { id: 'input-1', x: 10, y: 30, z: 0, type: 'input', intensity: 80, connections: ['proc-1', 'proc-2'] },
      { id: 'input-2', x: 10, y: 50, z: 0, type: 'input', intensity: 65, connections: ['proc-1', 'proc-3'] },
      { id: 'input-3', x: 10, y: 70, z: 0, type: 'input', intensity: 90, connections: ['proc-2', 'proc-3'] },
      
      // Processing layer
      { id: 'proc-1', x: 35, y: 25, z: 1, type: 'processing', intensity: 75, connections: ['relay-1', 'output-1'] },
      { id: 'proc-2', x: 35, y: 50, z: 1, type: 'processing', intensity: 85, connections: ['relay-1', 'output-2'] },
      { id: 'proc-3', x: 35, y: 75, z: 1, type: 'processing', intensity: 70, connections: ['relay-2', 'output-2'] },
      
      // Relay layer
      { id: 'relay-1', x: 60, y: 35, z: 2, type: 'relay', intensity: 60, connections: ['output-1', 'output-3'] },
      { id: 'relay-2', x: 60, y: 65, z: 2, type: 'relay', intensity: 55, connections: ['output-2', 'output-3'] },
      
      // Output layer
      { id: 'output-1', x: 85, y: 25, z: 3, type: 'output', intensity: 95, connections: [] },
      { id: 'output-2', x: 85, y: 50, z: 3, type: 'output', intensity: 88, connections: [] },
      { id: 'output-3', x: 85, y: 75, z: 3, type: 'output', intensity: 92, connections: [] }
    ];
    
    setNodes(newNodes);
    return newNodes;
  };

  // Generate data flows
  const generateDataFlows = () => {
    const newFlows: DataFlow[] = [];
    
    nodes.forEach(node => {
      node.connections.forEach(targetId => {
        if (Math.random() > 0.7) { // 30% chance of data flow
          newFlows.push({
            from: node.id,
            to: targetId,
            data: { value: Math.random() * 100, type: 'neural_signal' },
            timestamp: Date.now(),
            speed: 0.5 + Math.random() * 1.5
          });
        }
      });
    });
    
    setDataFlows(newFlows);
    return newFlows;
  };

  // Handle node click
  const handleNodeClick = (node: TunnelNode) => {
    setSelectedNode(node);
    onNodeClick?.(node);
  };

  // Node type styles
  const getNodeStyle = (node: TunnelNode) => {
    const baseSize = 16 + (node.intensity / 100) * 8;
    const colors = {
      input: '#00ff7f',
      processing: '#ffff00',
      relay: '#ff69b4',
      output: '#ff1493'
    };

    return {
      width: `${baseSize}px`,
      height: `${baseSize}px`,
      backgroundColor: colors[node.type],
      borderRadius: '50%',
      boxShadow: `0 0 ${node.intensity / 10}px ${colors[node.type]}`,
      position: 'absolute' as const,
      left: `${node.x}%`,
      top: `${node.y}%`,
      transform: `translate(-50%, -50%) translateZ(${node.z * 20}px)`,
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      border: selectedNode?.id === node.id ? `2px solid ${config.textColor}` : 'none'
    };
  };

  // Initialize nodes on mount
  React.useEffect(() => {
    const initialNodes = initializeNodes();

    if (showDataFlow) {
      const interval = setInterval(() => {
        generateDataFlows();
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [showDataFlow]);

  // Update data flows when nodes change
  React.useEffect(() => {
    if (showDataFlow && nodes.length > 0) {
      generateDataFlows();
    }
  }, [nodes, showDataFlow]);

  return (
    <motion.div
      className={`${styles.tunnelContainer} ${styles[theme]}`}
      style={{
        width: `${width}px`,
        height: `${height}px`,
        backgroundColor: config.backgroundColor
      }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* SVG for connections */}
      <svg
        className={styles.connectionsSvg}
      >
        <defs>
          <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={config.connectionColor} stopOpacity="0.3" />
            <stop offset="100%" stopColor={config.connectionColor} stopOpacity="1" />
          </linearGradient>
        </defs>

        {/* Render connections */}
        {nodes.map(node =>
          node.connections.map(targetId => {
            const targetNode = nodes.find(n => n.id === targetId);
            if (!targetNode) return null;

            return (
              <line
                key={`${node.id}-${targetId}`}
                x1={`${node.x}%`}
                y1={`${node.y}%`}
                x2={`${targetNode.x}%`}
                y2={`${targetNode.y}%`}
                stroke="url(#connectionGradient)"
                strokeWidth="2"
                strokeDasharray="5,5"
              />
            );
          })
        )}

        {/* Render data flows */}
        <AnimatePresence>
          {showDataFlow && dataFlows.map((flow, index) => {
            const fromNode = nodes.find(n => n.id === flow.from);
            const toNode = nodes.find(n => n.id === flow.to);
            if (!fromNode || !toNode) return null;

            return (
              <motion.circle
                key={`flow-${index}`}
                r="3"
                fill={config.dataFlowColor}
                initial={{
                  cx: `${fromNode.x}%`,
                  cy: `${fromNode.y}%`
                }}
                animate={{
                  cx: `${toNode.x}%`,
                  cy: `${toNode.y}%`
                }}
                transition={{
                  duration: flow.speed,
                  ease: "linear",
                  repeat: Infinity,
                  repeatDelay: 1
                }}
                exit={{ opacity: 0 }}
              />
            );
          })}
        </AnimatePresence>
      </svg>

      {/* Render nodes */}
      {nodes.map(node => (
        <motion.div
          key={node.id}
          className={styles.nodeContainer}
          style={getNodeStyle(node)}
          onClick={() => handleNodeClick(node)}
          whileHover={{ scale: 1.2 }}
          whileTap={{ scale: 0.9 }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3, delay: node.z * 0.1 }}
        >
          <div
            className={styles.nodeLabel}
          >
            {node.id} ({node.intensity}%)
          </div>
        </motion.div>
      ))}

      {/* Selected node info */}
      {selectedNode && (
        <motion.div
          className={styles.selectedNodeInfo}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <strong>{selectedNode.id}</strong><br />
          Type: {selectedNode.type}<br />
          Intensity: {selectedNode.intensity}%<br />
          Connections: {selectedNode.connections.length}
        </motion.div>
      )}
    </motion.div>
  );
};

export default AGITunnel;