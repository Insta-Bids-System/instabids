'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, Image as ImageIcon, X } from 'lucide-react';
import { StorageService } from '@/lib/storage';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  images?: string[];
  timestamp: Date;
}

interface CIAChatProps {
  onSendMessage?: (message: string, images: string[]) => Promise<string>;
}

export default function CIAChat({ onSendMessage }: CIAChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm Alex, your project assistant at InstaBids. Here's what makes us different: We eliminate the expensive lead fees and wasted sales meetings that drive up costs on other platforms. Instead, contractors and homeowners interact directly through our app using photos and conversations to create solid quotes - no sales meetings needed. This keeps all the money savings between you and your contractor, not going to corporations. Contractors save on lead costs and sales time, so they can offer you better prices.\n\nWhat kind of home project brings you here today?",
      timestamp: new Date(),
    },
  ]);
  
  const [inputMessage, setInputMessage] = useState('');
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [imagePreview, setImagePreview] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fix hydration error
  useEffect(() => {
    setMounted(true);
  }, []);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length + selectedImages.length > 5) {
      toast.error('You can upload a maximum of 5 images');
      return;
    }

    // Validate each file
    for (const file of files) {
      const error = StorageService.validateImage(file);
      if (error) {
        toast.error(error);
        return;
      }
    }

    setSelectedImages([...selectedImages, ...files]);
    
    // Create preview URLs
    const newPreviews = files.map(file => URL.createObjectURL(file));
    setImagePreview([...imagePreview, ...newPreviews]);
  };

  const removeImage = (index: number) => {
    const newImages = selectedImages.filter((_, i) => i !== index);
    const newPreviews = imagePreview.filter((_, i) => i !== index);
    
    // Revoke the URL to prevent memory leaks
    URL.revokeObjectURL(imagePreview[index]);
    
    setSelectedImages(newImages);
    setImagePreview(newPreviews);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && selectedImages.length === 0) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      images: imagePreview.length > 0 ? [...imagePreview] : undefined,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Convert images to base64 for sending
      const imageDataUrls: string[] = [];
      for (const file of selectedImages) {
        const dataUrl = await StorageService.fileToBase64(file);
        imageDataUrls.push(dataUrl);
      }

      // Call the message handler - use default mock if not provided
      let response: string;
      
      if (onSendMessage) {
        console.log('Sending message to API...');
        response = await onSendMessage(inputMessage, imageDataUrls);
      } else {
        // Fallback mock response
        console.log('No API handler provided, using mock response');
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
        response = generateMockResponse(inputMessage);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please make sure the backend is running (cd backend && python main.py).",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setSelectedImages([]);
      setImagePreview([]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Generate mock responses when API is not connected
  const generateMockResponse = (message: string): string => {
    const lower = message.toLowerCase();
    
    if (lower.includes('kitchen')) {
      return "A kitchen renovation - great choice! Kitchen updates offer excellent ROI. Are you planning a full remodel or focusing on specific areas like cabinets, countertops, or appliances?";
    } else if (lower.includes('bathroom')) {
      return "Bathroom renovations can really transform your daily routine! What's motivating this project - is it updating the style, fixing issues, or adding functionality?";
    } else if (lower.includes('budget')) {
      return "Budget planning is smart! Kitchen remodels typically range from $15,000-$60,000, while bathrooms run $8,000-$25,000. What range feels comfortable for your project?";
    } else {
      return "I'd be happy to help with your project! Could you tell me more about what type of work you're considering?";
    }
  };

  return (
    <div className="flex flex-col h-[600px] max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg">
        <h2 className="text-xl font-semibold">Chat with Alex</h2>
        <p className="text-sm opacity-90">Your Instabids Project Assistant</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              
              {/* Display images if any */}
              {message.images && message.images.length > 0 && (
                <div className="mt-2 grid grid-cols-2 gap-2">
                  {message.images.map((img, idx) => (
                    <img
                      key={idx}
                      src={img}
                      alt={`Upload ${idx + 1}`}
                      className="rounded-md w-full h-32 object-cover"
                    />
                  ))}
                </div>
              )}
              
              {/* Only show timestamp on client to avoid hydration error */}
              {mounted && (
                <p className="text-xs mt-1 opacity-70">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Image Preview Area */}
      {imagePreview.length > 0 && (
        <div className="px-4 py-2 border-t">
          <div className="flex gap-2 overflow-x-auto">
            {imagePreview.map((preview, index) => (
              <div key={index} className="relative flex-shrink-0">
                <img
                  src={preview}
                  alt={`Preview ${index + 1}`}
                  className="w-20 h-20 object-cover rounded-md"
                />
                <button
                  onClick={() => removeImage(index)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
          />
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
            title="Upload images"
          >
            <ImageIcon size={24} />
          </button>
          
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your project or ask a question..."
            className="flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={1}
          />
          
          <button
            onClick={handleSendMessage}
            disabled={isLoading || (!inputMessage.trim() && selectedImages.length === 0)}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={24} />
          </button>
        </div>
        
        <p className="text-xs text-gray-500 mt-2">
          You can upload up to 5 images. Press Enter to send or Shift+Enter for new line.
        </p>
      </div>
    </div>
  );
}