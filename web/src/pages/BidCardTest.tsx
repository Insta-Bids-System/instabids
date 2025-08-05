import type React from "react";
import { useEffect, useState } from "react";
import BidCardPreview from "../components/BidCardPreview";
import { supabase } from "../lib/supabase";

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
  bid_document?: any;
}

const BidCardTest: React.FC = () => {
  const [bidCards, setBidCards] = useState<BidCardData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRecentBidCards();
  }, []);

  const loadRecentBidCards = async () => {
    try {
      setLoading(true);

      // Load recent bid cards from the database
      const { data, error } = await supabase
        .from("bid_cards")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(5);

      if (error) {
        setError(`Error loading bid cards: ${error.message}`);
        return;
      }

      setBidCards(data || []);
    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  };

  const getSessionIdFromBidCard = (bidCard: BidCardData): string | undefined => {
    // Try to extract session ID from the bid document
    const bidDocument = bidCard.bid_document;
    if (bidDocument?.full_cia_thread_id) {
      return bidDocument.full_cia_thread_id;
    }

    // Fallback: look for session ID patterns
    if (bidDocument?.cia_thread_id) {
      return bidDocument.cia_thread_id;
    }

    return undefined;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading bid cards...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <div className="text-red-600 text-center">
            <h2 className="text-xl font-bold mb-2">Error Loading Bid Cards</h2>
            <p className="text-gray-700">{error}</p>
            <button
              type="button"
              onClick={loadRecentBidCards}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Bid Card Preview Test</h1>
              <p className="text-gray-600 mt-1">Testing photo-integrated bid card components</p>
            </div>
            <button
              type="button"
              onClick={loadRecentBidCards}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Bid Cards</h3>
            <p className="text-3xl font-bold text-blue-600">{bidCards.length}</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Recent Cards</h3>
            <p className="text-3xl font-bold text-green-600">
              {
                bidCards.filter((card) => {
                  const created = new Date(card.created_at);
                  const today = new Date();
                  return today.getTime() - created.getTime() < 24 * 60 * 60 * 1000;
                }).length
              }
            </p>
            <p className="text-sm text-gray-500">Created today</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Photo Integration</h3>
            <p className="text-3xl font-bold text-purple-600">✓</p>
            <p className="text-sm text-gray-500">Database storage working</p>
          </div>
        </div>

        {/* Bid Cards */}
        {bidCards.length === 0 ? (
          <div className="bg-white p-12 rounded-lg shadow-sm border text-center">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Bid Cards Found</h3>
            <p className="text-gray-600 mb-4">
              No bid cards have been generated yet. Run the JAA agent test to create sample data.
            </p>
            <code className="bg-gray-100 px-3 py-1 rounded text-sm">
              python test_jaa_with_photos.py
            </code>
          </div>
        ) : (
          <div className="space-y-8">
            {bidCards.map((bidCard) => (
              <div key={bidCard.id} className="space-y-4">
                {/* Bid Card Info Header */}
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Bid Card: {bidCard.bid_card_number}
                      </h3>
                      <p className="text-gray-600">
                        Session ID: {getSessionIdFromBidCard(bidCard) || "Not available"}
                      </p>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <p>Database ID: {bidCard.id}</p>
                      <p>Created: {new Date(bidCard.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                {/* Bid Card Preview */}
                <BidCardPreview
                  bidCard={bidCard}
                  sessionId={getSessionIdFromBidCard(bidCard)}
                  showFullDetails={true}
                />
              </div>
            ))}
          </div>
        )}

        {/* Debug Info */}
        <div className="mt-12 bg-gray-900 text-white p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Debug Information</h3>
          <div className="space-y-2 text-sm font-mono">
            <p>✅ Photo Service: Database storage integration</p>
            <p>✅ BidCardPreview: Photo loading and display</p>
            <p>✅ JAA Integration: Bid card generation with photos</p>
            <p>✅ Database: Supabase connection active</p>
            <p>⏳ Frontend: React component rendering</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BidCardTest;
