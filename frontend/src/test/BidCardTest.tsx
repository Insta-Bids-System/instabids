import React from 'react';
import BidCard from '../components/BidCard';

// Test page to verify bid card component variants
const BidCardTest: React.FC = () => {
  // Sample bid card data
  const testBidCard = {
    id: "test_12345",
    project_type: "kitchen_remodel",
    timeline: "Within 1 month",
    urgency: "emergency",
    budget_display: "$35,000 - $45,000",
    budget_range: { min: 35000, max: 45000 },
    location: {
      city: "Orlando",
      state: "FL",
      neighborhood: "Winter Park"
    },
    project_details: {
      scope_of_work: [
        "Remove existing cabinets and countertops",
        "Install new custom cabinetry",
        "Install quartz countertops",
        "Update all appliances to stainless steel",
        "Add tile backsplash"
      ],
      special_requirements: [
        "Must maintain access to kitchen during renovation",
        "Eco-friendly materials preferred"
      ],
      property_details: {
        size: "225 sq ft",
        year_built: "1985",
        style: "Traditional"
      }
    },
    photo_urls: [
      "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800",
      "https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=800",
      "https://images.unsplash.com/photo-1556909212-d5b604d0c90d?w=800"
    ],
    hero_image_url: "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800",
    contractor_count: 5,
    created_at: new Date().toISOString(),
    homeowner_ready: true,
    views: 42
  };

  const handleViewDetails = () => {
    console.log('View details clicked');
  };

  const handleExpressInterest = () => {
    console.log('Express interest clicked');
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Bid Card Component Test</h1>
        
        {/* Full Variant */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Full Variant (Web Display)</h2>
          <div className="bg-white rounded-lg shadow-lg p-4">
            <BidCard 
              bidCard={testBidCard} 
              variant="full"
              onViewDetails={handleViewDetails}
              onExpressInterest={handleExpressInterest}
            />
          </div>
        </section>

        {/* Preview Variant */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Preview Variant (List Display)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <BidCard 
              bidCard={testBidCard} 
              variant="preview"
              onViewDetails={handleViewDetails}
            />
            <BidCard 
              bidCard={{...testBidCard, urgency: "week", id: "test_67890"}} 
              variant="preview"
              onViewDetails={handleViewDetails}
            />
            <BidCard 
              bidCard={{...testBidCard, urgency: "month", id: "test_11111"}} 
              variant="preview"
              onViewDetails={handleViewDetails}
            />
          </div>
        </section>

        {/* Email Variant */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Email Variant</h2>
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl">
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-600 mb-4">Email Preview:</p>
              <BidCard 
                bidCard={testBidCard} 
                variant="email"
              />
            </div>
          </div>
        </section>

        {/* Mobile Responsive Test */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Mobile Responsive Test</h2>
          <div className="bg-white rounded-lg shadow-lg p-4 max-w-sm mx-auto">
            <BidCard 
              bidCard={testBidCard} 
              variant="full"
              onViewDetails={handleViewDetails}
              onExpressInterest={handleExpressInterest}
            />
          </div>
        </section>
      </div>
    </div>
  );
};

export default BidCardTest;