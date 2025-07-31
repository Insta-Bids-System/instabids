'use client';

import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  MapPin, 
  Clock, 
  DollarSign, 
  Eye, 
  MessageSquare, 
  Calendar,
  Star,
  TrendingUp,
  Users,
  CheckCircle,
  AlertTriangle,
  Filter,
  Search
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Project {
  id: string;
  title: string;
  type: string;
  location: string;
  budget: {
    min: number;
    max: number;
  };
  urgency: 'Emergency' | 'Week' | 'Month' | 'Flexible';
  description: string;
  requirements: string[];
  images: string[];
  postedDate: Date;
  deadline?: Date;
  homeowner: {
    name: string;
    rating: number;
    projectsCompleted: number;
  };
  bidsReceived: number;
  maxBids: number;
  status: 'Open' | 'In Review' | 'Awarded' | 'Closed';
}

interface ContractorStats {
  totalProjects: number;
  activeProjects: number;
  completedProjects: number;
  averageRating: number;
  totalEarnings: number;
  responseRate: number;
}

interface ContractorDashboardProps {
  contractorId?: string;
}

export default function ContractorDashboard({ contractorId }: ContractorDashboardProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<ContractorStats | null>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [filter, setFilter] = useState<{
    type: string;
    urgency: string;
    budgetRange: string;
    location: string;
  }>({
    type: 'all',
    urgency: 'all',
    budgetRange: 'all',
    location: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Mock data - replace with API calls
      const mockStats: ContractorStats = {
        totalProjects: 47,
        activeProjects: 3,
        completedProjects: 44,
        averageRating: 4.8,
        totalEarnings: 125000,
        responseRate: 95
      };

      const mockProjects: Project[] = [
        {
          id: '1',
          title: 'Kitchen Renovation - Modern Update',
          type: 'Kitchen',
          location: 'Downtown Seattle, WA',
          budget: { min: 25000, max: 40000 },
          urgency: 'Month',
          description: 'Complete kitchen renovation including new cabinets, countertops, appliances, and flooring. Looking for a modern, clean aesthetic.',
          requirements: ['Licensed', 'Insured', '5+ years experience', 'References required'],
          images: ['/api/placeholder/400/300', '/api/placeholder/400/300'],
          postedDate: new Date('2025-01-28'),
          deadline: new Date('2025-02-15'),
          homeowner: {
            name: 'Sarah Johnson',
            rating: 4.9,
            projectsCompleted: 3
          },
          bidsReceived: 7,
          maxBids: 12,
          status: 'Open'
        },
        {
          id: '2',
          title: 'Emergency Roof Repair',
          type: 'Roofing',
          location: 'Bellevue, WA',
          budget: { min: 3000, max: 8000 },
          urgency: 'Emergency',
          description: 'Urgent roof repair needed due to storm damage. Multiple shingles blown off, possible leak.',
          requirements: ['Emergency response', 'Licensed', 'Insurance claims experience'],
          images: ['/api/placeholder/400/300'],
          postedDate: new Date('2025-01-29'),
          homeowner: {
            name: 'Mike Chen',
            rating: 4.7,
            projectsCompleted: 1
          },
          bidsReceived: 3,
          maxBids: 8,
          status: 'Open'
        },
        {
          id: '3',
          title: 'Bathroom Remodel - Master Suite',
          type: 'Bathroom',
          location: 'Redmond, WA',
          budget: { min: 15000, max: 25000 },
          urgency: 'Week',
          description: 'Master bathroom complete remodel. Tile shower, new vanity, modern fixtures.',
          requirements: ['Plumbing experience', 'Tile work', 'Licensed'],
          images: ['/api/placeholder/400/300', '/api/placeholder/400/300'],
          postedDate: new Date('2025-01-27'),
          deadline: new Date('2025-02-10'),
          homeowner: {
            name: 'Jennifer Davis',
            rating: 5.0,
            projectsCompleted: 2
          },
          bidsReceived: 12,
          maxBids: 12,
          status: 'In Review'
        }
      ];

      setStats(mockStats);
      setProjects(mockProjects);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'Emergency': return 'bg-red-100 text-red-800 border-red-200';
      case 'Week': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Month': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Flexible': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const filteredProjects = projects.filter(project => {
    if (filter.type !== 'all' && project.type.toLowerCase() !== filter.type.toLowerCase()) return false;
    if (filter.urgency !== 'all' && project.urgency.toLowerCase() !== filter.urgency.toLowerCase()) return false;
    if (filter.location && !project.location.toLowerCase().includes(filter.location.toLowerCase())) return false;
    return true;
  });

  if (!mounted) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Contractor Dashboard</h1>
              <p className="text-gray-600">Find and bid on projects that match your expertise</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                My Bids
              </button>
              <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                Profile Settings
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Building2 className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Active Projects</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.activeProjects}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.completedProjects}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <Star className="w-5 h-5 text-yellow-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Rating</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.averageRating}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Response Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.responseRate}%</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <DollarSign className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Earnings</p>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalEarnings)}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Users className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Projects</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalProjects}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Projects</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Project Type</label>
              <select
                value={filter.type}
                onChange={(e) => setFilter(prev => ({ ...prev, type: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Types</option>
                <option value="kitchen">Kitchen</option>
                <option value="bathroom">Bathroom</option>
                <option value="roofing">Roofing</option>
                <option value="flooring">Flooring</option>
                <option value="electrical">Electrical</option>
                <option value="plumbing">Plumbing</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Urgency</label>
              <select
                value={filter.urgency}
                onChange={(e) => setFilter(prev => ({ ...prev, urgency: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Urgencies</option>
                <option value="emergency">Emergency</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="flexible">Flexible</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Budget Range</label>
              <select
                value={filter.budgetRange}
                onChange={(e) => setFilter(prev => ({ ...prev, budgetRange: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Budgets</option>
                <option value="0-5000">$0 - $5,000</option>
                <option value="5000-15000">$5,000 - $15,000</option>
                <option value="15000-30000">$15,000 - $30,000</option>
                <option value="30000+">$30,000+</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={filter.location}
                  onChange={(e) => setFilter(prev => ({ ...prev, location: e.target.value }))}
                  placeholder="City or ZIP code"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <div key={project.id} className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
              <div className="p-6">
                {/* Header */}
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{project.title}</h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <MapPin className="w-4 h-4" />
                      {project.location}
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getUrgencyColor(project.urgency)}`}>
                    {project.urgency}
                  </span>
                </div>

                {/* Budget */}
                <div className="flex items-center gap-2 mb-4">
                  <DollarSign className="w-4 h-4 text-green-600" />
                  <span className="text-lg font-semibold text-green-600">
                    {formatCurrency(project.budget.min)} - {formatCurrency(project.budget.max)}
                  </span>
                </div>

                {/* Description */}
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">{project.description}</p>

                {/* Requirements */}
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Requirements:</h4>
                  <div className="flex flex-wrap gap-1">
                    {project.requirements.slice(0, 3).map((req, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        {req}
                      </span>
                    ))}
                    {project.requirements.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        +{project.requirements.length - 3} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Images */}
                {project.images.length > 0 && (
                  <div className="flex gap-2 mb-4">
                    {project.images.slice(0, 2).map((image, index) => (
                      <img
                        key={index}
                        src={image}
                        alt={`Project ${index + 1}`}
                        className="w-16 h-16 object-cover rounded"
                      />
                    ))}
                    {project.images.length > 2 && (
                      <div className="w-16 h-16 bg-gray-100 rounded flex items-center justify-center text-xs text-gray-600">
                        +{project.images.length - 2}
                      </div>
                    )}
                  </div>
                )}

                {/* Homeowner Info */}
                <div className="flex items-center gap-3 mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{project.homeowner.name}</p>
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      {project.homeowner.rating} • {project.homeowner.projectsCompleted} projects
                    </div>
                  </div>
                </div>

                {/* Bids Progress */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Bids: {project.bidsReceived}/{project.maxBids}</span>
                    <span>{mounted && project.deadline && `Due: ${project.deadline.toLocaleDateString()}`}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(project.bidsReceived / project.maxBids) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedProject(project)}
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <Eye className="w-4 h-4" />
                    View Details
                  </button>
                  <button className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                    <MessageSquare className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredProjects.length === 0 && (
          <div className="text-center py-12">
            <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
            <p className="text-gray-600">Try adjusting your filters to see more projects.</p>
          </div>
        )}
      </div>

      {/* Project Detail Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-gray-900">{selectedProject.title}</h2>
                <button
                  onClick={() => setSelectedProject(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-3">Project Details</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Location</label>
                      <p className="text-gray-900">{selectedProject.location}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Budget Range</label>
                      <p className="text-green-600 font-semibold">
                        {formatCurrency(selectedProject.budget.min)} - {formatCurrency(selectedProject.budget.max)}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      <p className="text-gray-900">{selectedProject.description}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Requirements</label>
                      <ul className="list-disc list-inside text-gray-900">
                        {selectedProject.requirements.map((req, index) => (
                          <li key={index}>{req}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">Project Images</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {selectedProject.images.map((image, index) => (
                      <img
                        key={index}
                        src={image}
                        alt={`Project ${index + 1}`}
                        className="w-full h-48 object-cover rounded-lg"
                      />
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-4 mt-6 pt-6 border-t">
                <button
                  onClick={() => setSelectedProject(null)}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
                <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Submit Bid
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}