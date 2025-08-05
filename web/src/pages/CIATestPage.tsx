import type React from "react";
import CIAChat from "@/components/chat/CIAChat";

const CIATestPage: React.FC = () => {
  const handleSendMessage = async (message: string, _images: string[]) => {
    // Mock response that includes account creation trigger
    await new Promise((resolve) => setTimeout(resolve, 1000));

    if (message.toLowerCase().includes("kitchen")) {
      return "Great! I understand you're planning a kitchen renovation. Based on what you've told me, I can connect you with 3-5 qualified contractors who specialize in kitchen projects. To get your professional bids and start the process, would you like to create your InstaBids account? It only takes a minute and you'll start receiving bids within hours.";
    }

    if (message.toLowerCase().includes("bathroom")) {
      return "Perfect! A bathroom renovation is a great investment. I can help you get competitive bids from experienced contractors. To receive your bid cards and get started, let's create an account so contractors can reach you with their quotes.";
    }

    return "Thanks for that information! I'm gathering all the details about your project. When you're ready to start receiving bids, I'll help you create your InstaBids account to connect with qualified contractors.";
  };

  const handleAccountCreated = (userData: { name: string; email: string; userId: string }) => {
    console.log("Account created:", userData);
    // Here you could redirect to dashboard, update global state, etc.
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-center mb-6">CIA Chat Test with Account Signup</h1>
        <div className="bg-white rounded-lg shadow-lg p-4">
          <CIAChat onSendMessage={handleSendMessage} onAccountCreated={handleAccountCreated} />
        </div>

        {/* Test Instructions */}
        <div className="mt-6 bg-blue-50 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Test Instructions:</h3>
          <ul className="space-y-1 text-blue-800 text-sm">
            <li>• Type "I want to renovate my kitchen" and send</li>
            <li>• The CIA should respond with an account creation prompt</li>
            <li>• The signup modal should automatically appear</li>
            <li>• Test the account creation flow</li>
            <li>• Check that the welcome message appears after signup</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CIATestPage;
