import React from 'react';
import ContractorCommunicationHub from '@/components/homeowner/ContractorCommunicationHub';

const TestCommunicationPage: React.FC = () => {
  const bidCardId = "4c9dfb00-ee77-41da-8b8d-2615dbd31d95";
  const homeownerId = "11111111-1111-1111-1111-111111111111";

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Test Contractor Communication Hub
        </h1>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <ContractorCommunicationHub 
            bidCardId={bidCardId}
            homeownerId={homeownerId}
          />
        </div>
      </div>
    </div>
  );
};

export default TestCommunicationPage;