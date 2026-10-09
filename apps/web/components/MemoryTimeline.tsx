"use client";

import React from "react";

/**
 * Memory Timeline Component
 * 
 * Displays a visual timeline of AI chat interactions with threading,
 * persona identification, and timestamps.
 * 
 * Based on Harmonic Trinity's MemoryTimeline.
 */

export interface TimelineMessage {
  type: "user" | "ai" | "system" | "debate";
  text: string;
  timestamp: number;
  persona?: string;
  emoji?: string;
}

interface MemoryTimelineProps {
  messages: TimelineMessage[];
  maxHeight?: string;
  showTimestamps?: boolean;
  onClear?: () => void;
}

const PERSONA_COLORS: Record<string, string> = {
  alba: "bg-amber-100 border-amber-400 text-amber-900",
  albi: "bg-blue-100 border-blue-400 text-blue-900",
  jona: "bg-red-100 border-red-400 text-red-900",
  blerina: "bg-green-100 border-green-400 text-green-900",
  asi: "bg-purple-100 border-purple-400 text-purple-900",
  system: "bg-gray-100 border-gray-400 text-gray-700",
  default: "bg-slate-100 border-slate-400 text-slate-900",
};

const PERSONA_EMOJIS: Record<string, string> = {
  alba: "🌅",
  albi: "🔧",
  jona: "🔍",
  blerina: "🌐",
  asi: "🧠",
  user: "👤",
  system: "⚙️",
};

function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatRelativeTime(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  
  if (diff < 60000) return "just now";
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return formatTime(timestamp);
}

export function MemoryTimeline({
  messages,
  maxHeight = "400px",
  showTimestamps = true,
  onClear,
}: MemoryTimelineProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  React.useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-lg">No messages yet</p>
        <p className="text-sm">Start a conversation to see the timeline</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center gap-2">
          <span className="text-lg">📜</span>
          <h3 className="font-semibold text-gray-800">Memory Timeline</h3>
          <span className="text-xs text-gray-500 bg-gray-200 px-2 py-0.5 rounded-full">
            {messages.length} messages
          </span>
        </div>
        {onClear && (
          <button
            onClick={onClear}
            className="text-xs text-red-500 hover:text-red-700 hover:bg-red-50 px-2 py-1 rounded transition-colors"
          >
            Clear
          </button>
        )}
      </div>

      {/* Timeline Container */}
      <div
        ref={containerRef}
        className="overflow-y-auto p-4"
        style={{ maxHeight }}
      >
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />

          {/* Messages */}
          <div className="space-y-4">
            {messages.map((msg, idx) => {
              const persona = msg.persona?.toLowerCase() || msg.type;
              const colorClass = PERSONA_COLORS[persona] || PERSONA_COLORS.default;
              const emoji = msg.emoji || PERSONA_EMOJIS[persona] || "💬";
              const isUser = msg.type === "user";

              return (
                <div key={idx} className="relative pl-10">
                  {/* Timeline dot */}
                  <div
                    className={`absolute left-2.5 w-3 h-3 rounded-full border-2 ${
                      isUser
                        ? "bg-blue-500 border-blue-600"
                        : "bg-white border-gray-400"
                    }`}
                  />

                  {/* Message card */}
                  <div
                    className={`p-3 rounded-lg border ${
                      isUser
                        ? "bg-blue-50 border-blue-200"
                        : colorClass
                    }`}
                  >
                    {/* Header */}
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm">{emoji}</span>
                        <span className="font-medium text-sm capitalize">
                          {isUser ? "You" : msg.persona || msg.type}
                        </span>
                        {msg.type === "debate" && (
                          <span className="text-xs bg-purple-200 text-purple-700 px-1.5 py-0.5 rounded">
                            Debate
                          </span>
                        )}
                      </div>
                      {showTimestamps && (
                        <span className="text-xs text-gray-400">
                          {formatRelativeTime(msg.timestamp)}
                        </span>
                      )}
                    </div>

                    {/* Content */}
                    <p className="text-sm whitespace-pre-wrap break-words">
                      {msg.text}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer with stats */}
      <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 rounded-b-lg">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {messages.filter((m) => m.type === "user").length} user messages •{" "}
            {messages.filter((m) => m.type === "ai" || m.type === "debate").length} AI responses
          </span>
          {messages.length > 0 && (
            <span>
              Started {formatTime(messages[0].timestamp)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Compact version for sidebars
 */
export function MemoryTimelineCompact({
  messages,
  maxMessages = 5,
}: {
  messages: TimelineMessage[];
  maxMessages?: number;
}) {
  const recentMessages = messages.slice(-maxMessages);

  return (
    <div className="space-y-2">
      {recentMessages.map((msg, idx) => {
        const emoji = msg.emoji || PERSONA_EMOJIS[msg.persona?.toLowerCase() || msg.type] || "💬";
        const isUser = msg.type === "user";

        return (
          <div
            key={idx}
            className={`flex items-start gap-2 p-2 rounded text-sm ${
              isUser ? "bg-blue-50" : "bg-gray-50"
            }`}
          >
            <span>{emoji}</span>
            <p className="flex-1 truncate">{msg.text}</p>
          </div>
        );
      })}
      {messages.length > maxMessages && (
        <p className="text-xs text-gray-400 text-center">
          +{messages.length - maxMessages} more messages
        </p>
      )}
    </div>
  );
}

/**
 * Clear Memory Button Component
 */
export function ClearMemoryButton({
  onClear,
  className = "",
}: {
  onClear: () => void;
  className?: string;
}) {
  const [confirming, setConfirming] = React.useState(false);

  const handleClick = () => {
    if (confirming) {
      onClear();
      setConfirming(false);
    } else {
      setConfirming(true);
      setTimeout(() => setConfirming(false), 3000);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
        confirming
          ? "bg-red-500 text-white hover:bg-red-600"
          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
      } ${className}`}
    >
      {confirming ? "Click to confirm" : "🗑️ Clear Memory"}
    </button>
  );
}

export default MemoryTimeline;
