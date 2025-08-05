import type React from "react";
import { useEffect, useState } from "react";
import type {
  BidCard,
  DiscoveryRun,
  ContractorLead,
  OutreachCampaign,
  ContractorOutreachAttempt,
  BidCardView,
  EngagementEvent,
  SubmittedBid,
  ApiResponse
} from "../../types";

interface DiscoveryCache {
  id: string;
  bid_card_id: string;
  search_criteria: Record<string, unknown>;
  contractors_found: number;
  cached_at: string;
}

interface ChannelBreakdown {
  email: number;
  form: number;
  sms: number;
  phone: number;
}

interface SuccessRates {
  email: { sent: number; delivered: number; opened: number; clicked: number; percentage: number };
  form: { sent: number; submitted: number; percentage: number };
  sms: { sent: number; delivered: number; percentage: number };
  phone: { attempted: number; connected: number; percentage: number };
}

interface ResponseTracking {
  id: string;
  contractor_id: string;
  response_type: string;
  response_time: string;
  message: string;
}

interface TimelineEvent {
  id: string;
  event_type: string;
  description: string;
  timestamp: string;
  details?: Record<string, unknown>;
}

interface LifecycleMetrics {
  completion: {
    bids_received: number;
    bids_needed: number;
    completion_percentage: number;
    is_complete: boolean;
  };
  discovery: {
    contractors_discovered: number;
    discovery_runs: number;
  };
  outreach: {
    total_attempts: number;
    channels_used: number;
    channel_breakdown: ChannelBreakdown;
    success_rates: SuccessRates;
  };
  engagement: {
    total_views: number;
    total_engagements: number;
    engagement_rate: number;
  };
  bids: {
    average_bid: number;
    minimum_bid: number;
    maximum_bid: number;
    bid_spread: number;
    bid_range_percentage: number;
  };
  timeline: {
    age_hours: number;
    age_days: number;
    is_recent: boolean;
    created_at: string;
  };
}

interface LifecycleData {
  bid_card: BidCard;
  discovery: {
    discovery_runs: DiscoveryRun[];
    discovery_cache: DiscoveryCache | null;
    potential_contractors: ContractorLead[];
    contractor_leads: ContractorLead[];
  };
  campaigns: OutreachCampaign[];
  outreach: {
    outreach_attempts: ContractorOutreachAttempt[];
    channel_breakdown: ChannelBreakdown;
    success_rates: SuccessRates;
    response_tracking: ResponseTracking[];
  };
  engagement: {
    views: BidCardView[];
    engagement_events: EngagementEvent[];
    email_tracking: EngagementEvent[];
    contractor_responses: ResponseTracking[];
  };
  bids: EnhancedSubmittedBid[];
  timeline: TimelineEvent[];
  metrics: LifecycleMetrics;
}

interface EnhancedSubmittedBid extends SubmittedBid {
  is_lowest?: boolean;
  is_highest?: boolean;
  timeline_days?: number;
  start_date?: string;
  bid_content?: string;
  contractor_email?: string;
  contractor_phone?: string;
}

interface BidCardLifecycleViewProps {
  bidCardId: string;
  onClose: () => void;
}

const BidCardLifecycleView: React.FC<BidCardLifecycleViewProps> = ({ bidCardId, onClose }) => {
  const [lifecycleData, setLifecycleData] = useState<LifecycleData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadLifecycleData = async () => {
      try {
        setIsLoading(true);
        console.log("Loading lifecycle for bid card ID:", bidCardId);
        const response = await fetch(`http://localhost:8008/api/bid-cards/${bidCardId}/lifecycle`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("admin_session_id")}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          // Handle both wrapped and unwrapped responses
          if (data.success && data.data) {
            setLifecycleData(data.data);
          } else if (data.bid_card) {
            // Direct response from API
            setLifecycleData(data);
          } else {
            setError(data.error || data.detail || "Failed to load bid card lifecycle data");
          }
        } else {
          const errorData = await response.json().catch(() => ({}));
          setError(errorData.detail || `Failed to load bid card lifecycle data (${response.status})`);
        }
      } catch (err) {
        setError("Error loading lifecycle data");
        console.error("Error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    loadLifecycleData();
  }, [bidCardId]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "generated":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "collecting_bids":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "bids_complete":
        return "bg-green-100 text-green-800 border-green-200";
      case "expired":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "emergency":
        return "text-red-600 bg-red-50";
      case "urgent":
        return "text-orange-600 bg-orange-50";
      case "standard":
        return "text-blue-600 bg-blue-50";
      case "flexible":
        return "text-green-600 bg-green-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = (now.getTime() - time.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) return "Just now";
    if (diffInHours < 24) return `${Math.floor(diffInHours)}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  const renderOverviewTab = () => {
    if (!lifecycleData) return null;

    const { bid_card, metrics } = lifecycleData;
    const location = bid_card.bid_document?.location;

    return (
      <div className="space-y-6">
        {/* Header Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-4">
                <h2 className="text-2xl font-bold text-gray-900">
                  {bid_card.project_type.charAt(0).toUpperCase() + bid_card.project_type.slice(1)}{" "}
                  Project
                </h2>
                <span
                  className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(bid_card.status)}`}
                >
                  {bid_card.status.replace("_", " ")}
                </span>
                <span
                  className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getUrgencyColor(bid_card.urgency_level)}`}
                >
                  {bid_card.urgency_level}
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Bid Card:</span>
                  <div className="text-gray-900 font-mono">{bid_card.bid_card_number}</div>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Location:</span>
                  <div className="text-gray-900">
                    {location && 'city' in location && 'state' in location
                      ? `${location.city}, ${location.state}`
                      : `${bid_card.location_city || 'Unknown'}, ${bid_card.location_state || 'Unknown'}`
                    }
                  </div>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Budget Range:</span>
                  <div className="text-gray-900">
                    {bid_card.budget_min && bid_card.budget_max
                      ? `${formatCurrency(bid_card.budget_min)} - ${formatCurrency(bid_card.budget_max)}`
                      : "Not specified"
                    }
                  </div>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Created:</span>
                  <div className="text-gray-900">{formatTimeAgo(bid_card.created_at)}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Section */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Bid Collection Progress</span>
              <span className="text-sm text-gray-600">
                {metrics.completion.bids_received}/{metrics.completion.bids_needed} bids (
                {Math.round(metrics.completion.completion_percentage)}%)
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${
                  metrics.completion.is_complete
                    ? "bg-green-500"
                    : metrics.completion.completion_percentage > 75
                      ? "bg-blue-500"
                      : metrics.completion.completion_percentage > 50
                        ? "bg-yellow-500"
                        : "bg-red-500"
                }`}
                style={{ width: `${Math.min(metrics.completion.completion_percentage, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Discovery Metrics */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-blue-600 text-lg">🔍</span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Contractors Found</p>
                <p className="text-lg font-semibold text-gray-900">
                  {metrics.discovery.contractors_discovered}
                </p>
              </div>
            </div>
          </div>

          {/* Outreach Metrics */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <span className="text-yellow-600 text-lg">📧</span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Outreach Sent</p>
                <p className="text-lg font-semibold text-gray-900">
                  {metrics.outreach.total_attempts}
                </p>
              </div>
            </div>
          </div>

          {/* Engagement Metrics */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <span className="text-purple-600 text-lg">👁️</span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Bid Card Views</p>
                <p className="text-lg font-semibold text-gray-900">
                  {metrics.engagement.total_views}
                </p>
              </div>
            </div>
          </div>

          {/* Bid Metrics */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-green-600 text-lg">💰</span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Avg Bid Amount</p>
                <p className="text-lg font-semibold text-gray-900">
                  {metrics.bids.average_bid > 0
                    ? formatCurrency(metrics.bids.average_bid)
                    : "No bids"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Channel Breakdown */}
        {Object.keys(metrics.outreach.channel_breakdown).length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Outreach Channels</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(metrics.outreach.channel_breakdown).map(([channel, count]) => (
                <div key={channel} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-sm text-gray-500 capitalize">{channel}</div>
                  {metrics.outreach.success_rates[channel as keyof SuccessRates] && (
                    <div className="text-xs text-green-600">
                      {Math.round(metrics.outreach.success_rates[channel as keyof SuccessRates].percentage)}% success
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderBidsTab = () => {
    if (!lifecycleData?.bids.length) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">💰</div>
          <p className="text-gray-500">No bids submitted yet</p>
          <p className="text-sm text-gray-400 mt-1">
            Bids will appear here when contractors respond
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {lifecycleData.bids.map((bid, index) => (
          <div key={bid.id || index} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h4 className="text-lg font-medium text-gray-900">{bid.contractor_name}</h4>
                  {bid.is_lowest && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Lowest Bid
                    </span>
                  )}
                  {bid.is_highest && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Highest Bid
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                  <div>
                    <span className="font-medium text-gray-700">Bid Amount:</span>
                    <div className="text-lg font-bold text-gray-900">
                      {formatCurrency(bid.bid_amount)}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Timeline:</span>
                    <div className="text-gray-900">
                      {bid.timeline_days ? `${bid.timeline_days} days` : bid.timeline_estimate}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Start Date:</span>
                    <div className="text-gray-900">
                      {bid.start_date 
                        ? new Date(bid.start_date).toLocaleDateString()
                        : bid.start_date_available 
                          ? new Date(bid.start_date_available).toLocaleDateString()
                          : "Not specified"
                      }
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Submitted:</span>
                    <div className="text-gray-900">{formatTimeAgo(bid.submitted_at)}</div>
                  </div>
                </div>

                <div className="mb-4">
                  <span className="font-medium text-gray-700">Bid Details:</span>
                  <p className="text-gray-600 mt-1">
                    {bid.bid_content || bid.proposal_details}
                  </p>
                </div>

                <div className="flex items-center text-sm text-gray-500">
                  <span>📧 {bid.contractor_email || 'Email not provided'}</span>
                  <span className="mx-2">•</span>
                  <span>📞 {bid.contractor_phone || 'Phone not provided'}</span>
                  <span className="mx-2">•</span>
                  <span>Via {bid.submission_method}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderContractorsTab = () => {
    if (!lifecycleData) return null;

    // Get contractor data from contractor_leads table (primary source)
    // This is the authoritative source of all contractors that have been discovered for this bid card
    const contractorLeads = lifecycleData.discovery?.contractor_leads || [];
    
    // Map contractor leads to display format with outreach data
    const contractors = contractorLeads.map(lead => ({
      id: lead.id,
      name: lead.business_name || lead.company_name || "Unknown Contractor",
      email: lead.email || "No email",
      phone: lead.phone || "No phone",
      website: lead.website || "No website",
      // Determine tier based on data quality and engagement
      tier: lead.lead_status === "contacted" ? 1 : 
            lead.lead_status === "enriched" ? 2 : 3,
      tier_name: lead.lead_status === "contacted" ? "Internal" : 
                  lead.lead_status === "enriched" ? "Prospects" : "New/Cold",
      lead_score: lead.lead_score || 0,
      lead_status: lead.lead_status || "new",
      // Get all outreach attempts for this contractor
      outreach_attempts: lifecycleData.outreach.outreach_attempts.filter(
        attempt => attempt.contractor_lead_id === lead.id
      ),
      discovery_run_id: lead.discovery_run_id
    }));

    // Fallback: if no contractor_leads data, try to get from campaigns (legacy)
    const campaignContractors = lifecycleData.campaigns.flatMap(campaign => 
      campaign.campaign_contractors?.map(cc => ({
        id: cc.contractor_id,
        name: cc.contractor_name || cc.business_name || "Unknown Contractor",
        email: cc.email || "No email",
        phone: cc.phone || "No phone",
        website: "No website",
        tier: cc.tier || 3,
        tier_name: cc.tier === 1 ? "Internal" : cc.tier === 2 ? "Prospects" : "New/Cold",
        lead_score: 0,
        lead_status: "unknown",
        outreach_attempts: lifecycleData.outreach.outreach_attempts.filter(
          attempt => attempt.contractor_lead_id === cc.id
        ),
        discovery_run_id: null
      })) || []
    );

    // Use contractor_leads if available, otherwise fall back to campaign_contractors
    const allContractors = contractors.length > 0 ? contractors : campaignContractors;

    if (allContractors.length === 0) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">👥</div>
          <p className="text-gray-500">No contractors reached out to yet</p>
          <p className="text-sm text-gray-400 mt-1">
            Contractors will appear here once campaigns start outreach
          </p>
        </div>
      );
    }

    const getTierColor = (tier: number) => {
      switch (tier) {
        case 1: return "bg-green-100 text-green-800 border-green-200";
        case 2: return "bg-blue-100 text-blue-800 border-blue-200";
        case 3: return "bg-gray-100 text-gray-800 border-gray-200";
        default: return "bg-gray-100 text-gray-800 border-gray-200";
      }
    };

    const getOutreachStatus = (attempts: any[], channel: string) => {
      const channelAttempts = attempts.filter(a => a.channel === channel);
      if (channelAttempts.length === 0) return { attempted: false, success: false };
      
      const successful = channelAttempts.some(a => 
        a.status === 'delivered' || a.status === 'sent' || a.status === 'opened'
      );
      return { attempted: true, success: successful };
    };

    return (
      <div className="space-y-4">
        {/* Summary Stats */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <h4 className="text-lg font-medium text-gray-900 mb-3">Contractor Outreach Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {allContractors.filter(c => c.tier === 1).length}
              </div>
              <div className="text-sm text-gray-500">Tier 1 (Internal)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {allContractors.filter(c => c.tier === 2).length}
              </div>
              <div className="text-sm text-gray-500">Tier 2 (Prospects)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">
                {allContractors.filter(c => c.tier === 3).length}
              </div>
              <div className="text-sm text-gray-500">Tier 3 (New/Cold)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {allContractors.length}
              </div>
              <div className="text-sm text-gray-500">Total Contacted</div>
            </div>
          </div>
        </div>

        {/* Contractor List */}
        {allContractors.map((contractor, index) => {
          const formStatus = getOutreachStatus(contractor.outreach_attempts, 'form');
          const emailStatus = getOutreachStatus(contractor.outreach_attempts, 'email');
          const phoneStatus = getOutreachStatus(contractor.outreach_attempts, 'phone');
          
          return (
            <div key={contractor.id || index} className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <h4 className="text-lg font-medium text-gray-900">{contractor.name}</h4>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getTierColor(contractor.tier)}`}>
                      Tier {contractor.tier}: {contractor.tier_name}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-4">
                    <div>
                      <span className="font-medium text-gray-700">Email:</span>
                      <div className="text-gray-900">{contractor.email}</div>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Phone:</span>
                      <div className="text-gray-900">{contractor.phone}</div>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Website:</span>
                      <div className="text-gray-900">
                        {contractor.website && contractor.website !== "No website" ? (
                          <a href={contractor.website} target="_blank" rel="noopener noreferrer" 
                             className="text-blue-600 hover:text-blue-800 underline">
                            {contractor.website}
                          </a>
                        ) : (
                          "No website"
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Lead Score and Status (if available from contractor_leads) */}
                  {contractor.lead_score > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-4">
                      <div>
                        <span className="font-medium text-gray-700">Lead Score:</span>
                        <div className="flex items-center space-x-2">
                          <div className="text-gray-900">{contractor.lead_score}/100</div>
                          <div className={`h-2 w-16 rounded-full ${
                            contractor.lead_score >= 80 ? 'bg-green-200' : 
                            contractor.lead_score >= 60 ? 'bg-yellow-200' : 'bg-red-200'
                          }`}>
                            <div className={`h-2 rounded-full ${
                              contractor.lead_score >= 80 ? 'bg-green-500' : 
                              contractor.lead_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                            }`} style={{ width: `${contractor.lead_score}%` }}></div>
                          </div>
                        </div>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Lead Status:</span>
                        <div className="text-gray-900 capitalize">{contractor.lead_status}</div>
                      </div>
                    </div>
                  )}

                  {/* Outreach Methods Status */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="text-sm font-medium text-gray-700 mb-3">Outreach Methods</h5>
                    <div className="grid grid-cols-3 gap-4">
                      {/* Form Status */}
                      <div className="text-center">
                        <div className={`w-8 h-8 mx-auto mb-2 rounded-full flex items-center justify-center ${
                          formStatus.attempted 
                            ? formStatus.success 
                              ? 'bg-green-100 text-green-600' 
                              : 'bg-yellow-100 text-yellow-600'
                            : 'bg-gray-100 text-gray-400'
                        }`}>
                          {formStatus.attempted ? (formStatus.success ? '✓' : '?') : '○'}
                        </div>
                        <div className="text-xs font-medium text-gray-900">Form</div>
                        <div className="text-xs text-gray-500">
                          {formStatus.attempted ? (formStatus.success ? 'Sent' : 'Attempted') : 'Not sent'}
                        </div>
                      </div>

                      {/* Email Status */}
                      <div className="text-center">
                        <div className={`w-8 h-8 mx-auto mb-2 rounded-full flex items-center justify-center ${
                          emailStatus.attempted 
                            ? emailStatus.success 
                              ? 'bg-green-100 text-green-600' 
                              : 'bg-yellow-100 text-yellow-600'
                            : 'bg-gray-100 text-gray-400'
                        }`}>
                          {emailStatus.attempted ? (emailStatus.success ? '✓' : '?') : '○'}
                        </div>
                        <div className="text-xs font-medium text-gray-900">Email</div>
                        <div className="text-xs text-gray-500">
                          {emailStatus.attempted ? (emailStatus.success ? 'Delivered' : 'Attempted') : 'Not sent'}
                        </div>
                      </div>

                      {/* Phone Status */}
                      <div className="text-center">
                        <div className={`w-8 h-8 mx-auto mb-2 rounded-full flex items-center justify-center ${
                          phoneStatus.attempted 
                            ? phoneStatus.success 
                              ? 'bg-green-100 text-green-600' 
                              : 'bg-yellow-100 text-yellow-600'
                            : 'bg-gray-100 text-gray-400'
                        }`}>
                          {phoneStatus.attempted ? (phoneStatus.success ? '✓' : '?') : '○'}
                        </div>
                        <div className="text-xs font-medium text-gray-900">Phone</div>
                        <div className="text-xs text-gray-500">
                          {phoneStatus.attempted ? (phoneStatus.success ? 'Called' : 'Attempted') : 'Not called'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Outreach Attempts Details */}
                  {contractor.outreach_attempts.length > 0 && (
                    <div className="mt-4 bg-blue-50 rounded-lg p-3">
                      <h6 className="text-xs font-medium text-blue-900 mb-2">Outreach History</h6>
                      <div className="space-y-1">
                        {contractor.outreach_attempts.slice(0, 3).map((attempt, idx) => (
                          <div key={idx} className="flex items-center justify-between text-xs">
                            <span className="text-blue-700">
                              {attempt.channel}: {attempt.status}
                            </span>
                            <span className="text-blue-600">
                              {formatTimeAgo(attempt.sent_at)}
                            </span>
                          </div>
                        ))}
                        {contractor.outreach_attempts.length > 3 && (
                          <div className="text-xs text-blue-600">
                            +{contractor.outreach_attempts.length - 3} more attempts
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderTimelineTab = () => {
    if (!lifecycleData?.timeline.length) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">📅</div>
          <p className="text-gray-500">No timeline events</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {lifecycleData.timeline.map((event, index) => (
          <div key={event.id || index} className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-900">{event.description}</p>
                <p className="text-sm text-gray-500">{formatTimeAgo(event.timestamp)}</p>
              </div>
              {event.details && (
                <div className="mt-1 text-sm text-gray-600">
                  {Object.entries(event.details).map(([key, value]) => (
                    <span key={key} className="mr-4">
                      {key.replace(/_/g, " ")}: {String(value)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="text-red-400 text-4xl mb-4">⚠️</div>
            <p className="text-gray-900 font-medium mb-2">Error Loading Data</p>
            <p className="text-gray-600 text-sm mb-4">{error}</p>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Always render the modal structure, even while loading
  // This prevents the modal from disappearing

  const tabs = [
    { id: "overview", name: "Overview", icon: "📊" },
    { id: "contractors", name: "Contractors Reached Out", icon: "👥" },
    { id: "bids", name: "Submitted Bids", icon: "💰" },
    { id: "timeline", name: "Timeline", icon: "📅" },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-50 rounded-lg max-w-6xl w-full h-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">
            Bid Card Lifecycle{lifecycleData ? `: ${lifecycleData.bid_card.bid_card_number}` : ''}
          </h1>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <span className="text-2xl">×</span>
          </button>
        </div>

        {/* Tabs */}
        <div className="bg-white border-b border-gray-200 px-6">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                type="button"
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-pulse space-y-4">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3 mx-auto"></div>
                </div>
                <p className="text-gray-500 mt-4">Loading bid card data...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-red-400 text-4xl mb-4">⚠️</div>
                <p className="text-gray-900 font-medium mb-2">Error Loading Data</p>
                <p className="text-gray-600 text-sm">{error}</p>
              </div>
            </div>
          ) : lifecycleData ? (
            <>
              {activeTab === "overview" && renderOverviewTab()}
              {activeTab === "contractors" && renderContractorsTab()}
              {activeTab === "bids" && renderBidsTab()}
              {activeTab === "timeline" && renderTimelineTab()}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default BidCardLifecycleView;