"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Bot, Loader2, Send, TrendingUp, User } from "lucide-react";
import type React from "react";
import { useEffect, useRef, useState } from "react";

interface ContractorOnboardingChatProps {
  sessionId: string;
  onComplete: (contractorId: string) => void;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  profileData?: any;
  stage?: string;
  isStreaming?: boolean;
}

interface ProfileProgress {
  completeness: number;
  stage: string;
  collectedData: {
    primaryTrade?: string;
    yearsInBusiness?: number;
    serviceRadius?: number;
    businessName?: string;
    specializations?: string[];
    licenseInfo?: string;
    serviceAreas?: string[];
  };
  matchingProjects: number;
}

const ContractorOnboardingChat: React.FC<ContractorOnboardingChatProps> = ({
  sessionId,
  onComplete,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Welcome to InstaBids! I'm CoIA, your contractor success assistant. I'm here to help you get set up and start winning more projects.\n\nTo get started, what's your primary trade or specialty? (For example: General Contractor, Plumber, Electrician, HVAC, etc.)",
      timestamp: new Date(),
      stage: "welcome",
    },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [profileProgress, setProfileProgress] = useState<ProfileProgress>({
    completeness: 0,
    stage: "welcome",
    collectedData: {},
    matchingProjects: 0,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputMessage.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      // Create streaming assistant message
      const assistantMessageId = (Date.now() + 1).toString();
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingMessageId(assistantMessageId);

      // Call the real COIA backend endpoint
      const response = await fetch("http://localhost:8008/chat/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
          current_stage: profileProgress.stage,
          profile_data: profileProgress.collectedData,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update profile progress
      if (data.profile_progress) {
        setProfileProgress((prev) => ({
          ...prev,
          ...data.profile_progress,
        }));
      }

      // Simulate streaming response (in real implementation, use SSE or WebSocket)
      const fullResponse = data.response || "I understand. Let me help you with that.";
      let currentText = "";

      for (let i = 0; i <= fullResponse.length; i++) {
        currentText = fullResponse.slice(0, i);

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, content: currentText, stage: data.stage, profileData: data.profile_data }
              : msg
          )
        );

        await new Promise((resolve) => setTimeout(resolve, 20));
      }

      // Mark streaming as complete
      setMessages((prev) =>
        prev.map((msg) => (msg.id === assistantMessageId ? { ...msg, isStreaming: false } : msg))
      );

      setStreamingMessageId(null);

      // Check if onboarding is complete
      if (data.stage === "completed" && data.contractor_id) {
        setTimeout(() => {
          onComplete(data.contractor_id);
        }, 2000);
      }
    } catch (error) {
      console.error("Error sending message:", error);

      // Mock response for development (remove when backend is ready)
      const mockResponse = generateMockCoIAResponse(inputMessage, profileProgress);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: mockResponse.response,
                isStreaming: false,
                stage: mockResponse.stage,
              }
            : msg
        )
      );

      setProfileProgress((prev) => ({
        ...prev,
        ...mockResponse.profileUpdate,
      }));

      setStreamingMessageId(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Mock CoIA response generator (remove when real backend is ready)
  const generateMockCoIAResponse = (userInput: string, currentProgress: ProfileProgress) => {
    const input = userInput.toLowerCase();

    if (currentProgress.stage === "welcome") {
      if (input.includes("general") || input.includes("contractor")) {
        return {
          response:
            "Excellent! General contracting is a great field with lots of opportunities on InstaBids.\n\nHow many years have you been in the contracting business? This helps me understand your experience level and match you with appropriate projects.",
          stage: "experience",
          profileUpdate: {
            collectedData: { ...currentProgress.collectedData, primaryTrade: "General Contractor" },
            completeness: 0.2,
            stage: "experience",
          },
        };
      } else if (input.includes("plumb")) {
        return {
          response:
            "Perfect! Plumbing is always in high demand. We have plenty of plumbing projects from simple repairs to full bathroom renovations.\n\nHow many years of plumbing experience do you have?",
          stage: "experience",
          profileUpdate: {
            collectedData: { ...currentProgress.collectedData, primaryTrade: "Plumber" },
            completeness: 0.2,
            stage: "experience",
          },
        };
      }
    } else if (currentProgress.stage === "experience") {
      const years = parseInt(input) || 5;
      return {
        response: `Great! ${years} years of experience puts you in a strong position with homeowners.\n\nWhat's your service area? Please tell me the main city/zip code you work in and how far you're willing to travel for projects.`,
        stage: "service_area",
        profileUpdate: {
          collectedData: { ...currentProgress.collectedData, yearsInBusiness: years },
          completeness: 0.4,
          stage: "service_area",
        },
      };
    } else if (currentProgress.stage === "service_area") {
      return {
        response: `Perfect! I'll make sure to show you projects in that area.\n\nLast question: What makes your work stand out? For example:\n- Do you offer any warranties or guarantees?\n- Any special certifications or techniques?\n- What's your biggest competitive advantage?\n\nThis helps me write compelling project proposals for you.`,
        stage: "differentiators",
        profileUpdate: {
          collectedData: { ...currentProgress.collectedData, serviceAreas: [input] },
          completeness: 0.7,
          stage: "differentiators",
        },
      };
    } else if (currentProgress.stage === "differentiators") {
      return {
        response: `Excellent! Your profile is now complete. Based on what you've told me, I found **${Math.floor(Math.random() * 15) + 5} active projects** that match your expertise and service area.\n\nYou're all set to start browsing projects and submitting bids. Welcome to InstaBids! 🎉\n\nRedirecting you to your contractor dashboard...`,
        stage: "completed",
        profileUpdate: {
          collectedData: { ...currentProgress.collectedData, differentiators: input },
          completeness: 1.0,
          stage: "completed",
          matchingProjects: Math.floor(Math.random() * 15) + 5,
        },
      };
    }

    return {
      response: "I understand. Can you tell me more about that?",
      stage: currentProgress.stage,
      profileUpdate: {},
    };
  };

  return (
    <div className="flex flex-col h-[600px] bg-white/5 backdrop-blur-sm">
      {/* Profile Progress Bar */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-white/70">Profile Setup Progress</span>
          <span className="text-sm text-white/70">
            {Math.round(profileProgress.completeness * 100)}% Complete
          </span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${profileProgress.completeness * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        {profileProgress.matchingProjects > 0 && (
          <div className="flex items-center gap-2 mt-2 text-sm text-green-400">
            <TrendingUp className="w-4 h-4" />
            {profileProgress.matchingProjects} matching projects found
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === "user"
                    ? "bg-blue-600"
                    : "bg-gradient-to-r from-green-500 to-blue-500"
                }`}
              >
                {message.role === "user" ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-white" />
                )}
              </div>

              <div className={`flex-1 max-w-[80%] ${message.role === "user" ? "text-right" : ""}`}>
                <div
                  className={`rounded-2xl px-4 py-3 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white ml-auto"
                      : "bg-white/10 text-white"
                  } ${message.role === "user" ? "max-w-fit ml-auto" : ""}`}
                >
                  <div className="whitespace-pre-wrap">
                    {message.content}
                    {message.isStreaming && (
                      <motion.span
                        animate={{ opacity: [1, 0] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                        className="inline-block w-2 h-4 bg-current ml-1"
                      />
                    )}
                  </div>
                </div>

                <div className="text-xs text-white/50 mt-1">
                  {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && !streamingMessageId && (
          <motion.div
            className="flex gap-3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1">
              <div className="bg-white/10 rounded-2xl px-4 py-3 text-white">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>CoIA is thinking...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your response..."
              disabled={isLoading}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:opacity-50"
            />
          </div>

          <button
            type="button"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="flex-shrink-0 bg-gradient-to-r from-green-600 to-blue-600 text-white p-3 rounded-xl hover:from-green-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContractorOnboardingChat;
