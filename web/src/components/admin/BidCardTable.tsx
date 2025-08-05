import React, { useEffect, useState } from "react";
import { useAdminAuth } from "../../hooks/useAdminAuth";
import LoadingSpinner from "../ui/LoadingSpinner";

interface BidCard {
  id?: string;
  bid_card_number?: string;
  title?: string;
  project_type: string;
  status: string;
  contractor_count_needed?: number;
  bid_count?: number;
  created_at: string;
  budget_min?: number | null;
  budget_max?: number | null;
  budget_range?: {
    min: number;
    max: number;
  };
  urgency_level?: string;
  location_city?: string | null;
  location_state?: string | null;
  location?: {
    city: string;
    state: string;
    zip_code: string;
  };
}

const BidCardTable: React.FC = () => {
  const { session } = useAdminAuth();
  const [bidCards, setBidCards] = useState<BidCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBidCards();
  }, [session]);

  const fetchBidCards = async () => {
    try {
      // Try direct Supabase query first
      const response = await fetch("http://localhost:8008/api/bid-cards/search", {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        // Handle the search API response format
        setBidCards(data.bid_cards || data);
      } else {
        setError("Failed to load bid cards");
      }
    } catch (err) {
      setError("Error connecting to backend");
    } finally {
      setLoading(false);
    }
  };

  const formatBudget = (bidCard: BidCard): string => {
    // Handle budget_range format from search API
    if (bidCard.budget_range) {
      const { min, max } = bidCard.budget_range;
      return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    }
    
    // Handle individual min/max format
    const min = bidCard.budget_min;
    const max = bidCard.budget_max;
    if (!min && !max) return "Budget not set";
    if (!min) return `Up to $${max?.toLocaleString()}`;
    if (!max) return `From $${min.toLocaleString()}`;
    return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
  };

  const formatProjectType = (type: string): string => {
    return type.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case "generated": return "bg-blue-100 text-blue-800";
      case "collecting_bids": return "bg-yellow-100 text-yellow-800";
      case "bids_complete": return "bg-green-100 text-green-800";
      case "cancelled": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getUrgencyColor = (bidCard: BidCard): string => {
    const urgency = bidCard.urgency_level;
    if (!urgency) return "text-gray-600";
    switch (urgency) {
      case "emergency": return "text-red-600 font-bold";
      case "urgent": return "text-orange-600 font-semibold";
      case "week": return "text-yellow-600";
      case "month": return "text-green-600";
      default: return "text-gray-600";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" />
        <span className="ml-3 text-gray-600">Loading bid cards...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex">
          <div className="text-red-400 text-xl mr-3">⚠️</div>
          <div>
            <h3 className="text-red-800 font-medium">Error Loading Bid Cards</h3>
            <p className="text-red-600 mt-1">{error}</p>
            <button
              onClick={fetchBidCards}
              className="mt-3 text-sm bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (bidCards.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 text-4xl mb-4">📋</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Bid Cards Found</h3>
        <p className="text-gray-600">No bid cards have been created yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">
          Bid Cards ({bidCards.length})
        </h2>
        <p className="text-sm text-gray-600">
          All bid cards in the system, showing latest first
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Bid Card
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Project
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Budget
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Urgency
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {bidCards.map((bidCard) => (
              <tr key={bidCard.bid_card_number} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {bidCard.bid_card_number}
                  </div>
                  <div className="text-sm text-gray-500">
                    Needs {bidCard.contractor_count_needed || bidCard.bid_count || 0} contractors
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {formatProjectType(bidCard.project_type)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(bidCard.status)}`}>
                    {bidCard.status.replace(/_/g, " ").toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatBudget(bidCard)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {bidCard.location 
                    ? `${bidCard.location.city}, ${bidCard.location.state}`
                    : bidCard.location_city && bidCard.location_state 
                    ? `${bidCard.location_city}, ${bidCard.location_state}`
                    : "Location not set"
                  }
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`text-sm ${getUrgencyColor(bidCard)}`}>
                    {bidCard.urgency_level ? bidCard.urgency_level.toUpperCase() : "NOT SET"}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(bidCard.created_at).toLocaleDateString()}
                  <div className="text-xs text-gray-400">
                    {new Date(bidCard.created_at).toLocaleTimeString()}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BidCardTable;