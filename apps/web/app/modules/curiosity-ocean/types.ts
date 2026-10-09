export type CuriosityLevel = "curious" | "wild" | "chaos" | "genius";

export interface Message {
  id: string;
  type: "user" | "ai";
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  rabbitHoles?: string[];
  nextQuestions?: string[];
}
