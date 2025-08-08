import React, { useState, useEffect } from 'react';

interface ContractorSummary {
  id: string;
  company_name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  city: string;
  state: string;
  specialties: string[];
  tier: number;
  tier_description: string;
  rating?: number;
  status: string;
  last_contact?: string;
  campaigns_participated: number;
  bids_submitted: number;
  response_rate: number;
  availability_status?: string;
}

interface ContractorDetail {
  id: string;
  company_name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  website?: string;
  city: string;
  state: string;
  address?: string;
  zip_code?: string;
  service_radius_miles?: number;
  contractor_size?: string;
  years_in_business?: number;
  specialties: string[];
  certifications: string[];
  license_number?: string;
  tier: number;
  tier_description: string;
  rating?: number;
  review_count?: number;
  lead_score?: number;
  campaigns_participated: number;
  bids_submitted: number;
  response_rate: number;
  last_contact?: string;
  availability_status?: string;
  recent_campaigns: Array<{
    campaign_id: string;
    campaign_name: string;
    project_type: string;
    bid_card_number: string;
    status: string;
    date: string;
  }>;
  outreach_history: Array<{
    attempt_id: string;
    channel: string;
    status: string;
    sent_at: string;
    responded_at?: string;
    campaign_name: string;
    project_type: string;
    bid_card_number: string;
  }>;
}

interface TierStats {
  tier_1: number;
  tier_2: number;
  tier_3: number;
  total: number;
}

const ContractorManagement: React.FC = () => {
  const [contractors, setContractors] = useState<ContractorSummary[]>([]);
  const [tierStats, setTierStats] = useState<TierStats | null>(null);
  const [selectedTier, setSelectedTier] = useState<number | null>(null);
  const [selectedContractor, setSelectedContractor] = useState<ContractorDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCity, setFilterCity] = useState('');
  const [filterSpecialty, setFilterSpecialty] = useState('');

  const fetchContractors = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedTier) params.append('tier', selectedTier.toString());
      if (filterCity) params.append('city', filterCity);
      if (filterSpecialty) params.append('specialty', filterSpecialty);
      params.append('limit', '100');

      const response = await fetch(`/api/contractor-management/contractors?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('admin_session_id') || 'admin-session'}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch contractors: ${response.status}`);
      }

      const data = await response.json();
      setContractors(data.contractors);
      setTierStats(data.tier_stats);
      setError(null);
    } catch (error) {
      console.error('Error fetching contractors:', error);
      setError(error instanceof Error ? error.message : 'Failed to load contractors');
    } finally {
      setLoading(false);
    }
  };

  const fetchContractorDetail = async (contractorId: string) => {
    try {
      const response = await fetch(`/api/contractor-management/contractors/${contractorId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('admin_session_id') || 'admin-session'}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch contractor details: ${response.status}`);
      }

      const data = await response.json();
      setSelectedContractor(data);
    } catch (error) {
      console.error('Error fetching contractor details:', error);
      setError(error instanceof Error ? error.message : 'Failed to load contractor details');
    }
  };

  useEffect(() => {
    fetchContractors();
    
    // Refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchContractors, 30000);
    return () => clearInterval(interval);
  }, [selectedTier, filterCity, filterSpecialty]);

  // Filter contractors by search term
  const filteredContractors = contractors.filter(contractor =>
    contractor.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (contractor.contact_name && contractor.contact_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
    contractor.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contractor.specialties.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getTierColor = (tier: number) => {
    switch (tier) {
      case 1: return 'bg-green-100 text-green-800 border-green-200';
      case 2: return 'bg-blue-100 text-blue-800 border-blue-200';
      case 3: return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': case 'verified': return 'text-green-600';
      case 'pending': return 'text-yellow-600';
      case 'inactive': case 'disqualified': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Invalid date';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-4 text-lg text-gray-600">Loading contractors...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
        <strong className="font-bold">Error loading contractors: </strong>
        <span className="block sm:inline">{error}</span>
        <button 
          onClick={fetchContractors}
          className="mt-2 bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Tier Statistics */}
      {tierStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800">Total Contractors</h3>
            <p className="text-3xl font-bold text-blue-600">{tierStats.total}</p>
          </div>
          
          <div 
            className={`bg-white p-4 rounded-lg border shadow-sm cursor-pointer transition-all ${
              selectedTier === 1 ? 'border-green-400 bg-green-50' : 'border-gray-200 hover:border-green-300'
            }`}
            onClick={() => setSelectedTier(selectedTier === 1 ? null : 1)}
          >
            <h3 className="text-lg font-semibold text-green-800">Tier 1 - Official</h3>
            <p className="text-3xl font-bold text-green-600">{tierStats.tier_1}</p>
            <p className="text-sm text-green-600">InstaBids contractors</p>
          </div>

          <div 
            className={`bg-white p-4 rounded-lg border shadow-sm cursor-pointer transition-all ${
              selectedTier === 2 ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-blue-300'
            }`}
            onClick={() => setSelectedTier(selectedTier === 2 ? null : 2)}
          >
            <h3 className="text-lg font-semibold text-blue-800">Tier 2 - Previous</h3>
            <p className="text-3xl font-bold text-blue-600">{tierStats.tier_2}</p>
            <p className="text-sm text-blue-600">Multiple campaigns</p>
          </div>

          <div 
            className={`bg-white p-4 rounded-lg border shadow-sm cursor-pointer transition-all ${
              selectedTier === 3 ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 hover:border-yellow-300'
            }`}
            onClick={() => setSelectedTier(selectedTier === 3 ? null : 3)}
          >
            <h3 className="text-lg font-semibold text-yellow-800">Tier 3 - New</h3>
            <p className="text-3xl font-bold text-yellow-600">{tierStats.tier_3}</p>
            <p className="text-sm text-yellow-600">First discovery</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by company, contact, or city..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filter by City</label>
            <input
              type="text"
              value={filterCity}
              onChange={(e) => setFilterCity(e.target.value)}
              placeholder="Enter city name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Specialty</label>
            <input
              type="text"
              value={filterSpecialty}
              onChange={(e) => setFilterSpecialty(e.target.value)}
              placeholder="Enter specialty..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Contractors Table */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tier
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Specialties
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Performance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredContractors.map((contractor) => (
                <tr key={contractor.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {contractor.company_name}
                      </div>
                      {contractor.contact_name && (
                        <div className="text-sm text-gray-500">{contractor.contact_name}</div>
                      )}
                      {contractor.email && (
                        <div className="text-sm text-gray-500">{contractor.email}</div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getTierColor(contractor.tier)}`}>
                      Tier {contractor.tier}
                    </span>
                    <div className="text-xs text-gray-500 mt-1">
                      {contractor.tier_description}
                    </div>
                  </td>

                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{contractor.city}</div>
                    <div className="text-sm text-gray-500">{contractor.state}</div>
                  </td>

                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {contractor.specialties.slice(0, 2).map((specialty, index) => (
                        <span key={index} className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                          {specialty}
                        </span>
                      ))}
                      {contractor.specialties.length > 2 && (
                        <span className="text-xs text-gray-500">
                          +{contractor.specialties.length - 2} more
                        </span>
                      )}
                    </div>
                  </td>

                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {contractor.campaigns_participated} campaigns
                    </div>
                    <div className="text-sm text-gray-500">
                      {contractor.response_rate}% response rate
                    </div>
                    {contractor.rating && (
                      <div className="text-sm text-yellow-600">
                        ⭐ {contractor.rating.toFixed(1)}
                      </div>
                    )}
                  </td>

                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`text-sm font-medium ${getStatusColor(contractor.status)}`}>
                      {contractor.status}
                    </div>
                    <div className="text-xs text-gray-500">
                      Last: {formatDate(contractor.last_contact)}
                    </div>
                  </td>

                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => fetchContractorDetail(contractor.id)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      View Details
                    </button>
                    {contractor.tier > 1 && (
                      <button className="text-green-600 hover:text-green-900">
                        Add to Campaign
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredContractors.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              {searchTerm || filterCity || filterSpecialty 
                ? 'No contractors match your filters' 
                : 'No contractors found'}
            </div>
          </div>
        )}
      </div>

      {/* Contractor Detail Modal */}
      {selectedContractor && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                {selectedContractor.company_name}
              </h3>
              <button
                onClick={() => setSelectedContractor(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-6">
              {/* Basic Info */}
              <div>
                <h4 className="text-md font-semibold text-gray-800 mb-3">Basic Information</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Contact:</span>
                    <p className="text-sm text-gray-900">{selectedContractor.contact_name || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Email:</span>
                    <p className="text-sm text-gray-900">{selectedContractor.email || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Phone:</span>
                    <p className="text-sm text-gray-900">{selectedContractor.phone || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Website:</span>
                    <p className="text-sm text-gray-900">{selectedContractor.website || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Location:</span>
                    <p className="text-sm text-gray-900">
                      {selectedContractor.city}, {selectedContractor.state}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Tier:</span>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ml-2 ${getTierColor(selectedContractor.tier)}`}>
                      Tier {selectedContractor.tier} - {selectedContractor.tier_description}
                    </span>
                  </div>
                </div>
              </div>

              {/* Performance */}
              <div>
                <h4 className="text-md font-semibold text-gray-800 mb-3">Performance</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Campaigns:</span>
                    <p className="text-lg font-bold text-blue-600">{selectedContractor.campaigns_participated}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Bids:</span>
                    <p className="text-lg font-bold text-green-600">{selectedContractor.bids_submitted}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Response Rate:</span>
                    <p className="text-lg font-bold text-yellow-600">{selectedContractor.response_rate}%</p>
                  </div>
                  {selectedContractor.rating && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Rating:</span>
                      <p className="text-lg font-bold text-yellow-600">⭐ {selectedContractor.rating.toFixed(1)}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Specialties */}
              <div>
                <h4 className="text-md font-semibold text-gray-800 mb-3">Specialties</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedContractor.specialties.map((specialty, index) => (
                    <span key={index} className="inline-flex px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-full">
                      {specialty}
                    </span>
                  ))}
                </div>
              </div>

              {/* Recent Activity */}
              {selectedContractor.outreach_history.length > 0 && (
                <div>
                  <h4 className="text-md font-semibold text-gray-800 mb-3">Recent Outreach History</h4>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {selectedContractor.outreach_history.slice(0, 5).map((attempt) => (
                      <div key={attempt.attempt_id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <div>
                          <span className="text-sm font-medium">{attempt.campaign_name}</span>
                          <span className="text-xs text-gray-500 ml-2">via {attempt.channel}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-xs text-gray-500">{formatDate(attempt.sent_at)}</div>
                          <div className={`text-xs ${attempt.responded_at ? 'text-green-600' : 'text-yellow-600'}`}>
                            {attempt.responded_at ? 'Responded' : 'No response'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractorManagement;