import React, { useState } from "react";
import UltraInteractiveCIAChat from "@/components/chat/UltraInteractiveCIAChat";

export default function TestPage() {
  const [apiStatus, setApiStatus] = useState<"checking" | "connected" | "error">("checking");
  const [apiMessage, setApiMessage] = useState("");

  React.useEffect(() => {
    // Check API connection
    fetch("http://localhost:8008/test")
      .then((res) => res.json())
      .then((data) => {
        setApiStatus("connected");
        setApiMessage(data.message);
      })
      .catch((_err) => {
        setApiStatus("error");
        setApiMessage("Failed to connect to API");
      });
  }, []);

  const handleSendMessage = async (message: string, images: string[]) => {
    try {
      const response = await fetch("http://localhost:8008/api/cia/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          images,
          userId: "test_user",
          sessionId: "test_session",
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to send message");
      }

      const data = await response.json();
      return {
        response: data.response || data.message,
        phase: data.phase,
        extractedData: data.extractedData,
      };
    } catch (error) {
      console.error("Error calling CIA API:", error);
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">Instabids CIA Test Page</h1>

        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h2 className="text-xl font-semibold mb-2">API Status</h2>
          <div className="flex items-center space-x-2">
            <div
              className={`w-3 h-3 rounded-full ${
                apiStatus === "connected"
                  ? "bg-green-500"
                  : apiStatus === "error"
                    ? "bg-red-500"
                    : "bg-yellow-500 animate-pulse"
              }`}
            />
            <span className="text-sm">
              {apiStatus === "checking" ? "Checking API..." : apiMessage}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-2">Backend URL: http://localhost:8008</p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-4">Ultra Interactive CIA Agent</h2>
          <UltraInteractiveCIAChat
            onSendMessage={apiStatus === "connected" ? handleSendMessage : undefined}
          />
        </div>
      </div>
    </div>
  );
}
