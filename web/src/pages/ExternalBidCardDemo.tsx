import React from 'react';
import ExternalBidCard from '../../../frontend/src/components/ExternalBidCard';

const ExternalBidCardDemo: React.FC = () => {
  // Sample bid card data with photos
  const sampleBidCard = {
    id: "demo-123",
    public_token: "BC0730123456",
    project_type: "kitchen_remodel",
    urgency: "month",
    budget_display: "$15,000 - $25,000",
    location: {
      city: "Melbourne",
      state: "FL"
    },
    contractor_count: 4,
    created_at: "2024-01-30T10:00:00Z",
    photo_urls: [
      "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80", // Kitchen before
      "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80", // Kitchen counter
      "https://images.unsplash.com/photo-1556909195-4057a517d54a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  // Kitchen space
    ],
    project_details: {
      scope_of_work: [
        "Complete kitchen cabinet replacement with modern white shaker style",
        "Install new granite countertops with undermount sink",
        "Update all appliances to stainless steel Energy Star models", 
        "Replace flooring with luxury vinyl plank throughout kitchen",
        "Install under-cabinet LED lighting and pendant lights over island",
        "Paint walls and ceiling, add tile backsplash"
      ]
    }
  };

  const bathBidCard = {
    id: "demo-456",
    public_token: "BC0730654321", 
    project_type: "bathroom_renovation",
    urgency: "week",
    budget_display: "$8,000 - $12,000",
    location: {
      city: "Orlando",
      state: "FL"
    },
    contractor_count: 3,
    created_at: "2024-01-30T14:30:00Z",
    photo_urls: [
      "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2087&q=80", // Bathroom before
      "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  // Bathroom space
    ],
    project_details: {
      scope_of_work: [
        "Complete master bathroom renovation with walk-in shower",
        "Install new vanity with double sinks and quartz countertop",
        "Replace all plumbing fixtures and faucets",
        "Install luxury vinyl tile flooring",
        "Paint walls and install new lighting fixtures"
      ]
    }
  };

  const roofBidCard = {
    id: "demo-789",
    public_token: "BC0730987654",
    project_type: "roof_replacement",
    urgency: "emergency", 
    budget_display: "$18,000 - $28,000",
    location: {
      city: "Tampa",
      state: "FL"
    },
    contractor_count: 5,
    created_at: "2024-01-30T09:15:00Z",
    photo_urls: [
      "https://images.unsplash.com/photo-1558618047-3c2c0c8056dd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80", // Roof damage
      "https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2073&q=80", // House exterior
      "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"  // Roof detail
    ],
    project_details: {
      scope_of_work: [
        "Complete roof replacement after storm damage",
        "Remove existing shingles and inspect decking",
        "Install new architectural shingles with 30-year warranty",
        "Replace gutters and downspouts",
        "Install new ridge vents for proper ventilation"
      ]
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            External Bid Card Examples
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            These are the bid cards contractors see in emails, SMS, and website embeds
          </p>
          <div className="text-sm text-gray-500 bg-yellow-50 rounded-lg p-4 max-w-2xl mx-auto">
            <strong>Note:</strong> Clicking these will take you to the dynamic landing page with animations and full signup flow
          </div>
        </div>

        {/* Grid of Examples */}
        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-900">Kitchen Remodel</h2>
            <p className="text-gray-600">High-value project with multiple photos</p>
            <ExternalBidCard 
              bidCard={sampleBidCard} 
              variant="web_embed"
              source="demo_web"
            />
          </div>

          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-900">Bathroom Renovation</h2>
            <p className="text-gray-600">Mid-range project with urgency</p>
            <ExternalBidCard 
              bidCard={bathBidCard} 
              variant="web_embed"
              source="demo_web"
            />
          </div>

          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-900">Emergency Roof</h2>
            <p className="text-gray-600">Urgent project with storm damage</p>
            <ExternalBidCard 
              bidCard={roofBidCard} 
              variant="web_embed"
              source="demo_web"
            />
          </div>
        </div>

        {/* Email Version Demo */}
        <div className="mb-16">
          <h2 className="text-3xl font-semibold text-gray-900 mb-6 text-center">Email Version</h2>
          <p className="text-center text-gray-600 mb-8">
            This is how the bid card appears in contractor acquisition emails
          </p>
          <div className="max-w-2xl mx-auto bg-gray-100 p-8 rounded-lg">
            <ExternalBidCard 
              bidCard={sampleBidCard} 
              variant="email"
              source="demo_email"
            />
          </div>
        </div>

        {/* SMS Version Demo */}
        <div className="mb-16">
          <h2 className="text-3xl font-semibold text-gray-900 mb-6 text-center">SMS Version</h2>
          <p className="text-center text-gray-600 mb-8">
            Compact version for text message distribution
          </p>
          <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-lg border">
            <div className="bg-blue-500 text-white p-3 rounded-t-lg text-center font-semibold">
              SMS from InstaBids
            </div>
            <div className="p-4 bg-gray-50 rounded-b-lg">
              <ExternalBidCard 
                bidCard={bathBidCard} 
                variant="sms"
                source="demo_sms"
              />
            </div>
          </div> 
        </div>

        {/* Features */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-3xl font-semibold text-gray-900 mb-6 text-center">
            External Bid Card Features
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📸</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Photo Carousel</h3>
              <p className="text-sm text-gray-600">Auto-rotating project photos with manual navigation</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Smart Tracking</h3>
              <p className="text-sm text-gray-600">Full attribution from view to contractor signup</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📱</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Multi-Channel</h3>
              <p className="text-sm text-gray-600">Optimized for email, SMS, and web embeds</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🚀</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">High Converting</h3>
              <p className="text-sm text-gray-600">Designed to maximize contractor signups</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExternalBidCardDemo;