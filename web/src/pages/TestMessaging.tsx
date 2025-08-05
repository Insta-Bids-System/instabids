import type React from "react";
import { MessagingInterface } from "../components/messaging";

// Test page for messaging system
export const TestMessaging: React.FC = () => {
  // Mock user data for testing
  const mockHomeownerId = "123e4567-e89b-12d3-a456-426614174001";
  const mockContractorId = "123e4567-e89b-12d3-a456-426614174002";

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Messaging System Test</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Homeowner View */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="bg-blue-600 text-white p-4">
              <h2 className="text-xl font-semibold">Homeowner View</h2>
              <p className="text-sm opacity-90">ID: {mockHomeownerId}</p>
            </div>
            <div style={{ height: "600px" }}>
              <MessagingInterface userId={mockHomeownerId} userType="homeowner" />
            </div>
          </div>

          {/* Contractor View */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="bg-green-600 text-white p-4">
              <h2 className="text-xl font-semibold">Contractor View</h2>
              <p className="text-sm opacity-90">ID: {mockContractorId}</p>
            </div>
            <div style={{ height: "600px" }}>
              <MessagingInterface userId={mockContractorId} userType="contractor" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
