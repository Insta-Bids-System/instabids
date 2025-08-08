"use client";

import {
  AlertTriangle,
  Award,
  Building2,
  CheckCircle,
  LogOut,
  MapPin,
  MessageSquare,
  Plus,
  Bell,
  FileText,
} from "lucide-react";
import { useEffect, useState, useMemo } from "react";
import { BidCardMarketplace } from "@/components/bidcards/BidCardMarketplace";
import ContractorOnboardingChat from "@/components/chat/ContractorOnboardingChat";
import { useAuth } from "@/contexts/AuthContext";

interface ContractorDashboardProps {
  contractorId?: string;
}

interface ScopeChangeNotification {
  id: string;
  content: string;
  message_type: "scope_change_notification";
  created_at: string;
  is_read: boolean;
  metadata: {
    scope_changes: string[];
    scope_change_details: Record<string, any>;
  };
}

export default function ContractorDashboard({ contractorId }: ContractorDashboardProps) {
  const { signOut } = useAuth();
  const [contractorData, setContractorData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<"projects" | "marketplace" | "chat" | "profile" | "notifications">(
    "projects"
  );
  const [isLoading, setIsLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [sessionId] = useState(() => `contractor_${Date.now()}`);
  const [projects, setProjects] = useState<any[]>([]);
  const [bidCards, setBidCards] = useState<any[]>([]);
  const [scopeNotifications, setScopeNotifications] = useState<ScopeChangeNotification[]>([]);
  const [unreadNotifications, setUnreadNotifications] = useState(0);

  const loadContractorData = async () => {
    setIsLoading(true);
    try {
      // Load contractor data from unified contractors table (59 fields)
      const response = await fetch(`http://localhost:8008/contractors/${contractorId}/profile`);
      if (response.ok) {
        const data = await response.json();
        setContractorData(data);
        console.log(`Loaded contractor profile: ${data.profile_completeness}% complete with ${data.data_source}`);
      } else {
        // Try the fallback summary endpoint
        const summaryResponse = await fetch(`http://localhost:8008/contractors/${contractorId}/profile/summary`);
        if (summaryResponse.ok) {
          const summaryData = await summaryResponse.json();
          setContractorData({
            ...summaryData,
            display_name: summaryData.display_name,
            company_name: summaryData.display_name,
            phone: summaryData.phone,
            email: summaryData.email,
            website: summaryData.website,
            location: summaryData.location,
            rating: summaryData.rating,
            verified: summaryData.verified,
            years_in_business: summaryData.years_experience,
            license_number: summaryData.license_number,
            specialties: summaryData.specialties,
            emergency_services: summaryData.emergency_services,
            free_estimates: summaryData.free_estimates,
            profile_image_url: summaryData.profile_image,
            data_source: summaryData.data_source
          });
          console.log("Loaded contractor profile summary from unified table");
        } else {
          // Ultimate fallback for demo purposes
          console.log("API failed, using demo contractor data");
          setContractorData({
            company_name: "Demo Construction LLC",
            business_name: "Demo Construction LLC", 
            phone: "(555) 123-4567",
            business_phone: "(555) 123-4567",
            website_url: "https://democonstruction.com",
            business_address: "123 Demo St, Demo City, DC 12345",
            location_city: "Demo City",
            location_state: "DC",
            years_in_business: 15,
            license_number: "DC-12345",
            verified: true,
            rating: 4.8,
            google_rating: 4.8,
            google_reviews: 127,
            specialty_services: ["General Construction", "Kitchen Remodeling", "Bathroom Renovation"],
            emergency_services: true,
            free_estimates: true,
            crew_size: 8,
            insurance_info: "General Liability: $2M, Workers Comp: Current",
            bbb_rating: "A+",
            bbb_accredited: true,
            certifications: ["Licensed General Contractor", "EPA RRP Certified"],
            portfolio_images: ["/demo/portfolio1.jpg", "/demo/portfolio2.jpg"],
            data_source: "unified_contractors_table_demo",
            profile_completeness: 85
          });
        }
      }
    } catch (error) {
      console.error("Error loading contractor data:", error);
      // Provide fallback demo data
      setContractorData({
        company_name: "Demo Construction LLC",
        data_source: "fallback_demo",
        profile_completeness: 0
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadProjects = async () => {
    if (!contractorId) return;

    try {
      // Load projects and bid cards from the backend API
      const response = await fetch(`http://localhost:8008/contractors/${contractorId}/projects`);
      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects || []);
        setBidCards(data.bidCards || []);
      }
    } catch (error) {
      console.error("Error loading projects:", error);
      // Don't show error toast since projects might not exist yet
    }
  };

  const loadScopeNotifications = async () => {
    if (!contractorId) return;

    try {
      // Load scope change notifications from the intelligent messaging API
      const response = await fetch(`http://localhost:8008/api/intelligent-messages/scope-change-notifications/${contractorId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.notifications) {
          setScopeNotifications(data.notifications);
          // Count unread notifications
          const unreadCount = data.notifications.filter((notification: ScopeChangeNotification) => !notification.is_read).length;
          setUnreadNotifications(unreadCount);
          console.log(`Loaded ${data.notifications.length} scope change notifications, ${unreadCount} unread`);
        }
      }
    } catch (error) {
      console.error("Error loading scope notifications:", error);
      // Don't show error since notifications are optional
    }
  };

  useEffect(() => {
    setMounted(true);
    if (contractorId) {
      loadContractorData();
      loadProjects();
      loadScopeNotifications();
    }
  }, [contractorId]);

  const handleLogout = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  // Component for displaying scope change notifications
  const ScopeChangeMessage = ({ notification }: { notification: ScopeChangeNotification }) => {
    const handleReviewChanges = () => {
      // Navigate to updated project details - for now just log
      console.log("Review changes for notification:", notification.id);
      // TODO: Navigate to bid card details or updated project view
    };

    return (
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 my-4 rounded-r-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>
          <div className="ml-3 flex-grow">
            <p className="text-sm font-medium text-blue-800">
              Bid Card Updated
            </p>
            <p className="mt-1 text-sm text-blue-700">
              {notification.content}
            </p>
            {notification.metadata.scope_changes && notification.metadata.scope_changes.length > 0 && (
              <div className="mt-2 text-xs text-blue-600">
                Changes: {notification.metadata.scope_changes.join(", ")}
              </div>
            )}
            <div className="mt-2 text-xs text-gray-500">
              {new Date(notification.created_at).toLocaleDateString()} at{" "}
              {new Date(notification.created_at).toLocaleTimeString()}
            </div>
            <button 
              onClick={handleReviewChanges}
              className="mt-2 px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors"
            >
              Review Updated Project Details
            </button>
          </div>
          {!notification.is_read && (
            <div className="flex-shrink-0">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (!mounted) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - matching the main site design */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="text-2xl font-bold text-primary-600">Instabids</div>
            <div className="flex items-center gap-4">
              <span className="text-gray-600">
                {contractorData?.business_name || contractorData?.company_name || "Contractor Portal"}
              </span>
              {contractorData?.data_source === "unified_contractors_table" && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  ✨ Unified Profile ({contractorData?.profile_completeness || 0}% Complete)
                </span>
              )}
              {contractorData?.data_source?.includes("demo") && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  🏗️ Demo Profile
                </span>
              )}
              {contractorData?.verified && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ✅ Verified
                </span>
              )}
              {/* Notifications Indicator */}
              {unreadNotifications > 0 && (
                <div className="relative">
                  <Bell className="w-5 h-5 text-blue-600" />
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {unreadNotifications}
                  </span>
                </div>
              )}
              <button
                type="button"
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation - matching DashboardPage style */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            <button
              type="button"
              onClick={() => setActiveTab("projects")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "projects"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              My Projects
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("marketplace")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "marketplace"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Bid Marketplace
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("chat")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "chat"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              CoIA Assistant
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("profile")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "profile"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              My Profile
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("notifications")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "notifications"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              } flex items-center gap-1`}
            >
              Notifications
              {unreadNotifications > 0 && (
                <span className="bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {unreadNotifications}
                </span>
              )}
            </button>
          </nav>
        </div>

        {/* Projects Tab */}
        {activeTab === "projects" && (
          <>
            <div className="mb-8 flex justify-between items-center">
              <h1 className="text-3xl font-bold text-gray-900">My Projects</h1>
              <button
                type="button"
                onClick={() => setActiveTab("chat")}
                className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Plus className="w-5 h-5" />
                New Project Discussion
              </button>
            </div>

            {isLoading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              </div>
            ) : projects.length === 0 && bidCards.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">No projects yet</h2>
                <p className="text-gray-600 mb-6">
                  Connect with CoIA to start receiving project opportunities
                </p>
                <button
                  type="button"
                  onClick={() => setActiveTab("chat")}
                  className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <MessageSquare className="w-5 h-5" />
                  Start with CoIA Assistant
                </button>
              </div>
            ) : (
              <div className="space-y-8">
                {/* Bid Cards Section */}
                {bidCards.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-2xl font-semibold text-gray-900">Available Projects</h2>
                      <span className="text-sm text-gray-500">{bidCards.length} opportunities</span>
                    </div>
                    <div className="grid gap-6 lg:grid-cols-2">
                      {bidCards.map((bidCard) => {
                        // Check if bid card has recent scope changes
                        const hasRecentScopeChanges = bidCard.scope_last_updated && 
                          new Date(bidCard.scope_last_updated) > new Date(Date.now() - 24 * 60 * 60 * 1000);

                        return (
                          <div
                            key={bidCard.id}
                            className="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
                          >
                            <div className="p-6">
                              <div className="flex items-start justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {bidCard.project_type}
                                </h3>
                                <div className="flex items-center gap-2">
                                  <span className="text-sm text-gray-500">
                                    {bidCard.bid_card_number}
                                  </span>
                                  {hasRecentScopeChanges && (
                                    <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs font-medium">
                                      Updated
                                    </span>
                                  )}
                                </div>
                              </div>
                              <p className="text-gray-600 text-sm mb-4">{bidCard.description}</p>
                              <div className="flex items-center justify-between">
                                <span className="text-primary-600 font-medium">
                                  {bidCard.budget_range}
                                </span>
                                <span className="text-sm text-gray-500">{bidCard.timeline}</span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Regular Projects */}
                {projects.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-2xl font-semibold text-gray-900">Active Projects</h2>
                      <span className="text-sm text-gray-500">{projects.length} projects</span>
                    </div>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                      {projects.map((project) => (
                        <div
                          key={project.id}
                          className="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
                        >
                          <div className="p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                              {project.title}
                            </h3>
                            <p className="text-gray-600 text-sm mb-4">{project.description}</p>
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-500">{project.category}</span>
                              <span className="text-primary-600 font-medium">{project.status}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Marketplace Tab */}
        {activeTab === "marketplace" && (
          <div>
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Bid Marketplace</h1>
              <p className="text-gray-600">
                Browse and bid on available projects. Message homeowners to ask questions before
                submitting your bid.
              </p>
            </div>

            <BidCardMarketplace contractorId={contractorId} userType="contractor" />
          </div>
        )}

        {/* CoIA Chat Tab */}
        {activeTab === "chat" && (
          <div>
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">CoIA Assistant</h1>
              <p className="text-gray-600">
                Your Contractor Onboarding & Intelligence Agent with voice capabilities
              </p>
            </div>

            <div className="max-w-4xl mx-auto">
              <ContractorOnboardingChat
                sessionId={sessionId}
                onComplete={(contractorId) => {
                  console.log("Contractor onboarding completed:", contractorId);
                  // Optionally refresh contractor data or redirect
                  loadContractorData();
                }}
              />
            </div>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === "notifications" && (
          <div>
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Notifications</h1>
              <p className="text-gray-600">
                Project updates and scope changes from homeowners
              </p>
            </div>

            {scopeNotifications.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  No notifications yet
                </h2>
                <p className="text-gray-600">
                  You'll be notified when homeowners make changes to project scope
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {scopeNotifications.map((notification) => (
                  <ScopeChangeMessage key={notification.id} notification={notification} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === "profile" && (
          <div>
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">My Profile</h1>
              <p className="text-gray-600">
                AI-researched contractor profile and business information
              </p>
            </div>

            {isLoading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              </div>
            ) : contractorData ? (
              <div className="space-y-6">
                {/* Company Information */}
                <div className="bg-white rounded-lg shadow">
                  <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Building2 className="w-5 h-5 text-primary-600" />
                      Company Information
                    </h3>
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Business Name</label>
                        <p className="text-gray-900 font-medium">
                          {contractorData.business_name || contractorData.company_name}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Phone</label>
                        <p className="text-gray-900 font-medium">
                          {contractorData.business_phone || contractorData.phone}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Email</label>
                        <p className="text-gray-900 font-medium">
                          {contractorData.business_email || contractorData.email}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Website</label>
                        <a
                          href={contractorData.website_url || contractorData.website}
                          className="text-primary-600 hover:text-primary-700"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {contractorData.website_url || contractorData.website}
                        </a>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Address</label>
                        <p className="text-gray-900">
                          {contractorData.business_address || contractorData.address}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Location</label>
                        <p className="text-gray-900">
                          {contractorData.business_city || contractorData.location_city}, {contractorData.business_state || contractorData.location_state}
                        </p>
                      </div>
                      {contractorData.license_number && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">License Number</label>
                          <p className="text-gray-900 font-medium">{contractorData.license_number}</p>
                        </div>
                      )}
                      {contractorData.years_in_business && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Years in Business</label>
                          <p className="text-gray-900 font-medium">{contractorData.years_in_business} years</p>
                        </div>
                      )}
                      {contractorData.crew_size && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Crew Size</label>
                          <p className="text-gray-900 font-medium">{contractorData.crew_size} employees</p>
                        </div>
                      )}
                      {contractorData.insurance_info && (
                        <div className="md:col-span-2">
                          <label className="text-sm font-medium text-gray-500">Insurance</label>
                          <p className="text-gray-900">{contractorData.insurance_info}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Services & Specialties */}
                <div className="bg-white rounded-lg shadow">
                  <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Award className="w-5 h-5 text-primary-600" />
                      Services & Specialties
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Specializations</label>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {(contractorData.specialty_services || contractorData.specialties)?.map((specialty: string, index: number) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                            >
                              {specialty}
                            </span>
                          ))}
                        </div>
                      </div>
                      {(contractorData.service_areas || contractorData.certifications) && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">
                            {contractorData.service_areas ? "Service Areas" : "Certifications"}
                          </label>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {(contractorData.service_areas || contractorData.certifications)?.map((item: string, index: number) => (
                              <span
                                key={index}
                                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800"
                              >
                                {contractorData.service_areas && <MapPin className="w-3 h-3 mr-1" />}
                                {item}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {/* Service Options */}
                      <div>
                        <label className="text-sm font-medium text-gray-500">Service Options</label>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {contractorData.emergency_services && (
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                              🚨 Emergency Services
                            </span>
                          )}
                          {contractorData.free_estimates && (
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                              💰 Free Estimates
                            </span>
                          )}
                          {contractorData.financing_options && (
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                              💳 Financing Available
                            </span>
                          )}
                          {contractorData.warranty_offered && (
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                              🛡️ Warranty: {contractorData.warranty_offered}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Ratings & Reviews */}
                {(contractorData.google_rating || contractorData.rating || contractorData.bbb_rating) && (
                  <div className="bg-white rounded-lg shadow">
                    <div className="p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Ratings & Reviews</h3>
                      <div className="grid md:grid-cols-3 gap-6">
                        {contractorData.google_rating && (
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-900">{contractorData.google_rating}</div>
                            <div className="text-sm text-gray-500">Google Reviews</div>
                            {contractorData.google_reviews && (
                              <div className="text-xs text-gray-400">{contractorData.google_reviews} reviews</div>
                            )}
                          </div>
                        )}
                        {contractorData.bbb_rating && (
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-900">{contractorData.bbb_rating}</div>
                            <div className="text-sm text-gray-500">BBB Rating</div>
                            {contractorData.bbb_accredited && (
                              <div className="text-xs text-green-600">BBB Accredited</div>
                            )}
                          </div>
                        )}
                        {contractorData.angi_rating && (
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-900">{contractorData.angi_rating}</div>
                            <div className="text-sm text-gray-500">Angi Rating</div>
                            {contractorData.angi_reviews && (
                              <div className="text-xs text-gray-400">{contractorData.angi_reviews} reviews</div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Social Media & Online Presence */}
                {(contractorData.social_media || contractorData.facebook_url || contractorData.instagram_url || contractorData.linkedin_url) && (
                  <div className="bg-white rounded-lg shadow">
                    <div className="p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Online Presence</h3>
                      <div className="flex flex-wrap gap-4">
                        {(contractorData.social_media?.facebook || contractorData.facebook_url) && (
                          <a
                            href={contractorData.social_media?.facebook || contractorData.facebook_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                          >
                            Facebook
                          </a>
                        )}
                        {(contractorData.social_media?.instagram || contractorData.instagram_url) && (
                          <a
                            href={contractorData.social_media?.instagram || contractorData.instagram_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                          >
                            Instagram
                          </a>
                        )}
                        {contractorData.linkedin_url && (
                          <a
                            href={contractorData.linkedin_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                          >
                            LinkedIn
                          </a>
                        )}
                        {contractorData.youtube_url && (
                          <a
                            href={contractorData.youtube_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                          >
                            YouTube
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* AI Research Badge */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                    <div>
                      <p className="text-green-800 font-medium">AI Research Complete</p>
                      <p className="text-green-700 text-sm">
                        Profile data intelligently gathered from web research
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  No profile data available
                </h2>
                <p className="text-gray-600 mb-6">Complete your setup with CoIA Assistant</p>
                <button
                  type="button"
                  onClick={() => setActiveTab("chat")}
                  className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <MessageSquare className="w-5 h-5" />
                  Start Setup with CoIA
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
