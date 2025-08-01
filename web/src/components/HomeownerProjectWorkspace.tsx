import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  MessageSquare,
  FileText,
  Users,
  Calendar,
  DollarSign,
  Settings,
  Camera,
  Upload,
  Eye,
  Edit3,
  Send,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  MapPin,
  Home,
  Wrench,
  Package,
  Shield,
  Zap,
  Building,
  Star
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface BidCardData {
  id: string;
  bid_card_number: string;
  project_type: string;
  urgency_level: string;
  budget_min: number;
  budget_max: number;
  contractor_count_needed: number;
  created_at: string;
  status: string;
  complexity_score?: number;
  bid_document?: {
    all_extracted_data?: {
      location?: {
        city?: string;
        state?: string;
        address?: string;
        zip_code?: string;
        full_location?: string;
      };
      project_description?: string;
      service_type?: string;
      timeline_urgency?: string;
      material_preferences?: string[];
      special_requirements?: string[];
      contractor_requirements?: {
        contractor_count?: number;
        equipment_needed?: string[];
        licenses_required?: string[];
        specialties_required?: string[];
      };
      property_details?: {
        type?: string;
      };
      images?: string[];
      intention_score?: number;
      group_bidding_potential?: boolean;
    };
  };
  view_count?: number;
  click_count?: number;
  contractor_signups?: number;
}

interface HomeownerProjectWorkspaceProps {
  bidCardId?: string;
}

const HomeownerProjectWorkspace: React.FC<HomeownerProjectWorkspaceProps> = ({ bidCardId }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'chat' | 'contractors' | 'documents' | 'analytics'>('overview');
  const [bidCard, setBidCard] = useState<BidCardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatMessage, setChatMessage] = useState('');

  const projectId = bidCardId || id;

  useEffect(() => {
    if (projectId && user) {
      loadBidCard();
    }
  }, [projectId, user]);

  const loadBidCard = async () => {
    try {
      // Load all bid cards and find the one we need
      const response = await fetch(`http://localhost:8008/api/bid-cards/homeowner/${user?.id}`);
      if (response.ok) {
        const data = await response.json();
        const foundCard = data.find((card: BidCardData) => 
          card.id === projectId || card.bid_card_number === projectId
        );
        if (foundCard) {
          setBidCard(foundCard);
        } else {
          console.error('Bid card not found');
        }
      }
    } catch (error) {
      console.error('Error loading bid card:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContinueChat = () => {
    navigate('/chat', { 
      state: { 
        projectContext: bidCard,
        initialMessage: `I want to modify my ${bidCard?.project_type} project (${bidCard?.bid_card_number})`
      }
    });
  };

  const handleSendMessage = () => {
    if (chatMessage.trim()) {
      // For now, redirect to chat with the message
      navigate('/chat', {
        state: {
          projectContext: bidCard,
          initialMessage: chatMessage
        }
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!bidCard) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Project Not Found</h2>
          <p className="text-gray-600 mb-6">The project you're looking for doesn't exist or you don't have access to it.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const extractedData = bidCard.bid_document?.all_extracted_data || {};
  const photos = extractedData.images || [];

  const formatProjectType = (type: string) => {
    return type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Home Project';
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const TabButton = ({ 
    id, 
    label, 
    icon: Icon, 
    active 
  }: { 
    id: string; 
    label: string; 
    icon: React.ElementType; 
    active: boolean;
  }) => (
    <button
      onClick={() => setActiveTab(id as any)}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
        active 
          ? 'bg-blue-600 text-white' 
          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
      }`}
    >
      <Icon className="w-4 h-4" />
      {label}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </button>
              <div className="h-6 w-px bg-gray-300" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  {formatProjectType(bidCard.project_type)}
                </h1>
                <p className="text-sm text-gray-500">{bidCard.bid_card_number}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(bidCard.status)}`}>
                {bidCard.status?.toUpperCase()}
              </div>
              <button
                onClick={handleContinueChat}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Edit3 className="w-4 h-4" />
                Modify Project
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-1 py-3">
            <TabButton id="overview" label="Overview" icon={Home} active={activeTab === 'overview'} />
            <TabButton id="chat" label="Project Chat" icon={MessageSquare} active={activeTab === 'chat'} />
            <TabButton id="contractors" label="Contractors" icon={Users} active={activeTab === 'contractors'} />
            <TabButton id="documents" label="Documents" icon={FileText} active={activeTab === 'documents'} />
            <TabButton id="analytics" label="Analytics" icon={TrendingUp} active={activeTab === 'analytics'} />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Project Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  <span className="text-sm font-medium text-gray-600">Budget Range</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  ${bidCard.budget_min?.toLocaleString()} - ${bidCard.budget_max?.toLocaleString()}
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <Users className="w-5 h-5 text-blue-600" />
                  <span className="text-sm font-medium text-gray-600">Contractors Needed</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {bidCard.contractor_count_needed}
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <Clock className="w-5 h-5 text-orange-600" />
                  <span className="text-sm font-medium text-gray-600">Timeline</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {extractedData.timeline_urgency || bidCard.urgency_level}
                </div>
              </div>

            </div>

            {/* Project Details Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Project Description */}
              <div className="lg:col-span-2 space-y-6">
                {extractedData.project_description && (
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <FileText className="w-5 h-5" />
                      Project Description
                    </h3>
                    <p className="text-gray-700 leading-relaxed">
                      {extractedData.project_description}
                    </p>
                  </div>
                )}

                {/* Materials & Preferences */}
                {extractedData.material_preferences && extractedData.material_preferences.length > 0 && (
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Package className="w-5 h-5" />
                      Material Preferences
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {extractedData.material_preferences.map((material, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                          {material}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Special Requirements */}
                {extractedData.special_requirements && extractedData.special_requirements.length > 0 && (
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Zap className="w-5 h-5" />
                      Special Requirements
                    </h3>
                    <ul className="space-y-2">
                      {extractedData.special_requirements.map((req, index) => (
                        <li key={index} className="flex items-start gap-2 text-gray-700">
                          <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                          <span>{req}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Project Photos */}
                {photos.length > 0 && (
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Camera className="w-5 h-5" />
                      Project Photos ({photos.length})
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      {photos.slice(0, 4).map((photo, index) => (
                        <div key={index} className="relative">
                          <img
                            src={photo}
                            alt={`Project photo ${index + 1}`}
                            className="w-full h-24 object-cover rounded-lg"
                          />
                          {index === 3 && photos.length > 4 && (
                            <div className="absolute inset-0 bg-black bg-opacity-50 rounded-lg flex items-center justify-center">
                              <span className="text-white text-sm font-medium">
                                +{photos.length - 4} more
                              </span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Property Details */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Building className="w-5 h-5" />
                    Property Details
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="text-gray-900">{extractedData.property_details?.type || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Service:</span>
                      <span className="text-gray-900">{extractedData.service_type || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Location:</span>
                      <span className="text-gray-900">
                        {extractedData.location?.city || extractedData.location?.zip_code || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Project Stats
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Eye className="w-4 h-4" />
                        <span className="text-sm">Views</span>
                      </div>
                      <span className="font-semibold text-gray-900">{bidCard.view_count || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Users className="w-4 h-4" />
                        <span className="text-sm">Contractor Interest</span>
                      </div>
                      <span className="font-semibold text-green-600">{bidCard.contractor_signups || 0}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Project Modifications</h2>
              <p className="text-gray-600 mt-1">
                Make changes to your project requirements, budget, timeline, or other details.
              </p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What would you like to modify about your project?
                  </label>
                  <textarea
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    placeholder="I want to increase the budget to $50,000 and add premium appliances..."
                    className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleSendMessage}
                    disabled={!chatMessage.trim()}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Start Modification Chat
                  </button>
                  <button
                    onClick={handleContinueChat}
                    className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-200 flex items-center gap-2"
                  >
                    <MessageSquare className="w-4 h-4" />
                    Open Full Chat
                  </button>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-900 mb-4">Quick Modifications</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <button
                    onClick={() => setChatMessage("I want to increase my budget range for this project")}
                    className="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <DollarSign className="w-5 h-5 text-green-600 mb-2" />
                    <div className="text-sm font-medium">Adjust Budget</div>
                  </button>
                  <button
                    onClick={() => setChatMessage("I need to change the timeline for this project")}
                    className="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <Clock className="w-5 h-5 text-orange-600 mb-2" />
                    <div className="text-sm font-medium">Change Timeline</div>
                  </button>
                  <button
                    onClick={() => setChatMessage("I want to add more requirements to this project")}
                    className="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <Settings className="w-5 h-5 text-blue-600 mb-2" />
                    <div className="text-sm font-medium">Add Requirements</div>
                  </button>
                  <button
                    onClick={() => setChatMessage("I want to upload additional photos for this project")}
                    className="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <Upload className="w-5 h-5 text-purple-600 mb-2" />
                    <div className="text-sm font-medium">Add Photos</div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Other tabs would be implemented here */}
        {activeTab === 'contractors' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Contractor Communications</h2>
            <div className="text-center py-12">
              <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Coming Soon</h3>
              <p className="text-gray-600">
                Contractor communication features will be available in Phase 2 of development.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Project Documents</h2>
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Coming Soon</h3>
              <p className="text-gray-600">
                Document management features will be available in a future update.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Project Analytics</h2>
            <div className="text-center py-12">
              <TrendingUp className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Coming Soon</h3>
              <p className="text-gray-600">
                Advanced analytics and reporting features will be available in a future update.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomeownerProjectWorkspace;