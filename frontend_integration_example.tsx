/**
 * Frontend Integration Example for Pre-loaded Opening Message
 * This shows how to integrate the opening message into the chat UI
 */

import React, { useState, useEffect } from 'react';
import { MessageCircle } from 'lucide-react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const CIAChatWithOpeningMessage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [inputValue, setInputValue] = useState('');

  // Fetch and display opening message when chat loads
  useEffect(() => {
    fetchOpeningMessage();
  }, []);

  const fetchOpeningMessage = async () => {
    try {
      const response = await fetch('http://localhost:8008/api/cia/opening-message');
      const data = await response.json();
      
      if (data.success && data.message) {
        // Add opening message as first message in chat
        const openingMessage: ChatMessage = {
          id: 'opening-message',
          role: 'assistant',
          content: data.message,
          timestamp: data.timestamp
        };
        
        setMessages([openingMessage]);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Failed to fetch opening message:', error);
      // Fallback to default message if API fails
      setMessages([{
        id: 'fallback',
        role: 'assistant',
        content: 'Welcome to InstaBids! Tell me about your home improvement project.',
        timestamp: new Date().toISOString()
      }]);
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Call CIA streaming endpoint
    // ... existing streaming logic ...
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center gap-3">
          <MessageCircle className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-semibold">InstaBids AI Assistant</h1>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-pulse text-gray-500">Loading your AI assistant...</div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-200'
                  }`}
                >
                  {/* Special formatting for opening message */}
                  {message.id === 'opening-message' ? (
                    <div className="space-y-3">
                      {message.content.split('\n\n').map((paragraph, idx) => (
                        <div key={idx}>
                          {paragraph.includes('**') ? (
                            // Parse bold text and emojis
                            <div dangerouslySetInnerHTML={{
                              __html: paragraph
                                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                .replace(/\n/g, '<br>')
                            }} />
                          ) : (
                            <p>{paragraph}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t bg-white px-6 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Tell me about your project or upload a photo..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSendMessage}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default CIAChatWithOpeningMessage;

/**
 * INTEGRATION NOTES:
 * 
 * 1. The opening message is fetched from /api/cia/opening-message when chat loads
 * 2. It's displayed as the first message in the conversation
 * 3. The message contains markdown formatting that should be rendered properly
 * 4. Pain points are highlighted with emojis and bold text
 * 5. The message sets the tone for the entire conversation
 * 
 * KEY IMPROVEMENTS:
 * - Users immediately see value proposition
 * - Pain points are front and center
 * - Photo upload is encouraged from the start
 * - Group bidding opportunity is highlighted
 * - Privacy protection is emphasized
 * 
 * BACKEND CHANGES:
 * - Updated agents/cia/prompts.py with new SYSTEM_PROMPT
 * - Added OPENING_MESSAGE constant
 * - Created /api/cia/opening-message endpoint
 * - Internal quality assessment (never asks "basic or premium?")
 */