import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import UltraInteractiveCIAChat from '@/components/chat/UltraInteractiveCIAChat';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';

export default function ChatPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [apiConnected, setApiConnected] = useState(false);

  // Test API connection on component mount
  useEffect(() => {
    const testConnection = async () => {
      try {
        const isConnected = await apiService.testConnection();
        setApiConnected(isConnected);
        console.log('[ChatPage] API connection status:', isConnected);
      } catch (error) {
        console.error('[ChatPage] Failed to test API connection:', error);
        setApiConnected(false);
      }
    };

    testConnection();
  }, []);

  const handleSendMessage = async (message: string, images: string[]) => {
    try {
      // Get or create session ID
      let sessionId = localStorage.getItem('cia_session_id');
      if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('cia_session_id', sessionId);
      }

      const userId = user?.id || 'anonymous_user';
      const result = await apiService.sendChatMessage(message, images, userId, sessionId);
      
      if (result.success && result.data) {
        return {
          response: result.data.response,
          phase: result.data.phase,
          extractedData: result.data.extractedData
        };
      } else {
        throw new Error(result.error || 'Failed to send message');
      }
    } catch (error) {
      console.error('[ChatPage] Error sending message:', error);
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="mr-4 p-2 rounded-lg hover:bg-gray-100"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-semibold">New Project</h1>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="flex items-center">
                <div
                  className={`w-2 h-2 rounded-full mr-2 ${
                    apiConnected ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                />
                <span className="text-sm text-gray-600">
                  {apiConnected ? 'API Connected' : 'Using Mock Mode'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="py-8">
        <UltraInteractiveCIAChat onSendMessage={apiConnected ? handleSendMessage : undefined} />
      </div>
    </div>
  );
}