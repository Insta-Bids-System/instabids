import React, { useState } from 'react';
import { OpenAIRealtimeWebRTC } from '@/services/openai-realtime-webrtc';

export default function WebRTCTestPage() {
  const [status, setStatus] = useState('Not connected');
  const [logs, setLogs] = useState<string[]>([]);
  const [apiKey, setApiKey] = useState(import.meta.env.VITE_OPENAI_API_KEY || '');
  const [client, setClient] = useState<OpenAIRealtimeWebRTC | null>(null);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testConnection = async () => {
    if (!apiKey) {
      addLog('❌ No API key provided');
      return;
    }

    addLog('🚀 Starting WebRTC test...');
    setStatus('Connecting...');

    try {
      const realtimeClient = new OpenAIRealtimeWebRTC({
        apiKey: apiKey,
        model: 'gpt-4o-realtime-preview-2024-12-17',
        voice: 'alloy',
        instructions: 'Test connection only'
      });

      // Listen to events
      realtimeClient.on('connected', () => {
        addLog('✅ Connected successfully!');
        setStatus('Connected');
      });

      realtimeClient.on('error', (error) => {
        addLog(`❌ Error: ${error.message}`);
        setStatus('Error');
      });

      realtimeClient.on('disconnected', () => {
        addLog('🔌 Disconnected');
        setStatus('Disconnected');
      });

      // Connect
      await realtimeClient.connect();
      setClient(realtimeClient);
      
    } catch (error) {
      addLog(`❌ Connection failed: ${error.message}`);
      setStatus('Failed');
      console.error('Full error:', error);
    }
  };

  const disconnect = () => {
    if (client) {
      client.disconnect();
      setClient(null);
      addLog('🔌 Manually disconnected');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">OpenAI WebRTC Test Page</h1>
        
        {/* Status */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Connection Status</h2>
          <div className={`text-lg font-medium ${
            status === 'Connected' ? 'text-green-600' : 
            status === 'Failed' || status === 'Error' ? 'text-red-600' : 
            'text-yellow-600'
          }`}>
            {status}
          </div>
        </div>

        {/* API Key */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">API Key</h2>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full px-4 py-2 border rounded-lg mb-4"
          />
          <div className="flex gap-4">
            <button
              onClick={testConnection}
              disabled={status === 'Connecting...'}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Test Connection
            </button>
            {client && (
              <button
                onClick={disconnect}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Disconnect
              </button>
            )}
          </div>
        </div>

        {/* Console Logs */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Console Logs</h2>
          <div className="bg-gray-900 text-gray-100 p-4 rounded-lg h-96 overflow-y-auto font-mono text-sm">
            {logs.length === 0 ? (
              <div className="text-gray-500">No logs yet...</div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="mb-1">{log}</div>
              ))
            )}
          </div>
          <button
            onClick={() => setLogs([])}
            className="mt-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Clear Logs
          </button>
        </div>

        {/* Instructions */}
        <div className="mt-6 text-gray-600 text-sm">
          <p>This page tests the OpenAI Realtime WebRTC connection without authentication.</p>
          <p>Check the browser console (F12) for detailed logs.</p>
        </div>
      </div>
    </div>
  );
}