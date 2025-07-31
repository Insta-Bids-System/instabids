import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { supabase, Project } from '@/lib/supabase'
import { Plus, Home, Clock, CheckCircle, XCircle, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'
import InspirationDashboard from '@/components/inspiration/InspirationDashboard'
import InternalBidCard from '@/components/InternalBidCard'
import { apiService } from '@/services/api'

const DashboardPage: React.FC = () => {
  const { user, profile, signOut } = useAuth()
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [bidCards, setBidCards] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'projects' | 'inspiration'>('projects')

  useEffect(() => {
    loadProjects()
    loadBidCards()
  }, [user])

  const loadProjects = async () => {
    if (!user) return

    try {
      const { data, error } = await supabase
        .from('projects')
        .select('*')
        .eq('homeowner_id', user.id)
        .order('created_at', { ascending: false })

      if (error) throw error
      setProjects(data || [])
    } catch (error) {
      console.error('Error loading projects:', error)
      toast.error('Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  const loadBidCards = async () => {
    if (!user) return

    try {
      // Load bid cards from the backend API using the API service
      const response = await fetch(`http://localhost:8008/api/bid-cards/homeowner/${user.id}`)
      if (response.ok) {
        const data = await response.json()
        console.log('[Dashboard] Loaded bid cards:', data)
        setBidCards(data || [])
      } else {
        console.log('[Dashboard] API call failed, trying fallback to Supabase')
        // Fallback to direct Supabase query
        const { data, error } = await supabase
          .from('bid_cards')
          .select('*')
          .eq('homeowner_id', user.id)
          .order('created_at', { ascending: false })

        if (error) throw error
        setBidCards(data || [])
      }
    } catch (error) {
      console.error('[Dashboard] Error loading bid cards:', error)
      // Don't show error toast for bid cards since they might not exist yet
    }
  }

  const getStatusIcon = (status: Project['status']) => {
    switch (status) {
      case 'draft':
        return <Clock className="w-5 h-5 text-gray-500" />
      case 'posted':
      case 'in_bidding':
        return <Clock className="w-5 h-5 text-blue-500" />
      case 'awarded':
      case 'in_progress':
        return <Clock className="w-5 h-5 text-yellow-500" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return null
    }
  }

  const getStatusText = (status: Project['status']) => {
    switch (status) {
      case 'draft':
        return 'Draft'
      case 'posted':
        return 'Posted'
      case 'in_bidding':
        return 'Receiving Bids'
      case 'awarded':
        return 'Awarded'
      case 'in_progress':
        return 'In Progress'
      case 'completed':
        return 'Completed'
      case 'cancelled':
        return 'Cancelled'
      default:
        return status
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="text-2xl font-bold text-primary-600">
              Instabids
            </Link>
            <div className="flex items-center gap-4">
              <span className="text-gray-600">
                {profile?.full_name || user?.email}
              </span>
              <button
                onClick={() => signOut()}
                className="text-gray-700 hover:text-primary-600"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('projects')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'projects'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              My Projects
            </button>
            <button
              onClick={() => setActiveTab('inspiration')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'inspiration'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Inspiration Board
            </button>
          </nav>
        </div>

        {/* Conditional Content */}
        {activeTab === 'projects' ? (
          <>
            <div className="mb-8 flex justify-between items-center">
              <h1 className="text-3xl font-bold text-gray-900">My Projects</h1>
              <Link
                to="/chat"
                className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Plus className="w-5 h-5" />
                New Project
              </Link>
            </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : projects.length === 0 && bidCards.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Home className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              No projects yet
            </h2>
            <p className="text-gray-600 mb-6">
              Start by describing your first project to our AI assistant
            </p>
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
              Create Your First Project
            </Link>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Bid Cards Section */}
            {bidCards.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-semibold text-gray-900">AI-Generated Bid Cards</h2>
                  <span className="text-sm text-gray-500">{bidCards.length} active</span>
                </div>
                <div className="grid gap-6 lg:grid-cols-2">
                  {bidCards.map((bidCard) => (
                    <InternalBidCard
                      key={bidCard.id}
                      bidCard={bidCard}
                      onContinueChat={() => navigate('/chat')}
                      onViewAnalytics={() => {
                        toast.success('Analytics coming soon!')
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Regular Projects Section */}
            {projects.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-semibold text-gray-900">Regular Projects</h2>
                  <span className="text-sm text-gray-500">{projects.length} projects</span>
                </div>
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {projects.map((project) => (
                    <div
                      key={project.id}
                      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => navigate(`/projects/${project.id}`)}
                    >
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
                            {project.title}
                          </h3>
                          {getStatusIcon(project.status)}
                        </div>
                        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                          {project.description}
                        </p>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">
                            {project.category}
                          </span>
                          <span className={`font-medium ${
                            project.status === 'completed' ? 'text-green-600' :
                            project.status === 'cancelled' ? 'text-red-600' :
                            'text-blue-600'
                          }`}>
                            {getStatusText(project.status)}
                          </span>
                        </div>
                        {project.budget_range && (
                          <div className="mt-3 text-sm text-gray-600">
                            Budget: ${project.budget_range.min.toLocaleString()} - ${project.budget_range.max.toLocaleString()}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
          </>
        ) : (
          <InspirationDashboard />
        )}
      </main>
    </div>
  )
}

export default DashboardPage