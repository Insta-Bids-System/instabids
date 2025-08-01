import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Plus, Image as ImageIcon, Sparkles, Grid3X3, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'
import BoardCreator from './BoardCreator'
import BoardView from './BoardView'
import IrisChat from './AIAssistant/IrisChat'

export interface InspirationBoard {
  id: string
  homeowner_id: string
  title: string
  description?: string
  room_type?: string
  status: 'collecting' | 'organizing' | 'refining' | 'ready'
  cover_image_id?: string
  ai_insights?: any
  created_at: string
  updated_at: string
  image_count?: number
}

const InspirationDashboard: React.FC = () => {
  const { user } = useAuth()
  const [boards, setBoards] = useState<InspirationBoard[]>([])
  const [loading, setLoading] = useState(true)
  const [showBoardCreator, setShowBoardCreator] = useState(false)
  const [showIrisChat, setShowIrisChat] = useState(false)
  const [selectedBoard, setSelectedBoard] = useState<InspirationBoard | null>(null)

  useEffect(() => {
    console.log('🔍 useEffect triggered, user:', user)
    const demoUser = localStorage.getItem('DEMO_USER')
    console.log('🔍 useEffect demo user check:', demoUser)
    if (user || demoUser) {
      console.log('🔍 Calling loadBoards from useEffect')
      loadBoards()
    } else {
      console.log('🔍 No user or demo user found, not loading boards')
    }
  }, [user])

  const loadBoards = async () => {
    try {
      setLoading(true)
      console.log('🔍 loadBoards called')
      
      // Check for demo user
      const demoUser = localStorage.getItem('DEMO_USER')
      console.log('🔍 Demo user from localStorage:', demoUser)
      if (demoUser) {
        const demoData = JSON.parse(demoUser)
        console.log('🔍 Demo data parsed:', demoData)
        console.log('🔍 Making API call to:', `http://localhost:8008/api/demo/inspiration/boards?homeowner_id=${encodeURIComponent(demoData.id)}`)
        // Load demo boards from backend API
        try {
          const response = await fetch(`http://localhost:8008/api/demo/inspiration/boards?homeowner_id=${encodeURIComponent(demoData.id)}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json'
            }
          })

          console.log('🔍 API response status:', response.status)
          if (!response.ok) {
            throw new Error('Failed to load demo boards')
          }

          const boardsData = await response.json()
          console.log('🔍 Boards data received:', boardsData)
          setBoards(boardsData)
          console.log('🔍 Boards state updated with', boardsData?.length, 'boards')
          
          // Force update to test rendering
          if (boardsData && boardsData.length > 0) {
            console.log('🔍 Successfully set boards, should render now')
          }
        } catch (error) {
          console.error('Error loading demo boards:', error)
          // Fallback to empty state
          setBoards([])
        }
        setLoading(false)
        return
      }
      
      // Load boards with image count
      const { data: boardsData, error: boardsError } = await supabase
        .from('inspiration_boards')
        .select(`
          *,
          inspiration_images(count)
        `)
        .eq('homeowner_id', user?.id)
        .order('created_at', { ascending: false })

      if (boardsError) throw boardsError

      // Transform the data to include image count
      const boardsWithCount = boardsData?.map(board => ({
        ...board,
        image_count: board.inspiration_images?.[0]?.count || 0
      })) || []

      setBoards(boardsWithCount)
    } catch (error) {
      console.error('Error loading boards:', error)
      toast.error('Failed to load inspiration boards')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateBoard = async (boardData: Partial<InspirationBoard>) => {
    try {
      // Check for demo user
      const demoUser = localStorage.getItem('DEMO_USER')
      
      if (demoUser) {
        // For demo users, use the backend API which has service-level permissions
        const demoData = JSON.parse(demoUser)
        const response = await fetch('http://localhost:8008/api/demo/inspiration/boards', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: boardData.title || 'New Inspiration Board',
            description: boardData.description,
            room_type: boardData.room_type,
            homeowner_id: demoData.id,
            status: 'collecting',
            is_demo: true
          })
        })

        if (!response.ok) {
          throw new Error('Failed to create demo board')
        }

        const data = await response.json()
        
        toast.success('Board created successfully!')
        setBoards([data, ...boards])
        setShowBoardCreator(false)
      } else {
        // For authenticated users, use direct Supabase access
        const { data, error } = await supabase
          .from('inspiration_boards')
          .insert({
            ...boardData,
            homeowner_id: user?.id,
            status: 'collecting'
          })
          .select()
          .single()

        if (error) throw error

        toast.success('Board created successfully!')
        setBoards([data, ...boards])
        setShowBoardCreator(false)
      }
    } catch (error) {
      console.error('Error creating board:', error)
      toast.error('Failed to create board')
    }
  }

  const handleBoardClick = (board: InspirationBoard) => {
    setSelectedBoard(board)
  }

  const getStatusColor = (status: InspirationBoard['status']) => {
    switch (status) {
      case 'collecting':
        return 'bg-blue-100 text-blue-800'
      case 'organizing':
        return 'bg-yellow-100 text-yellow-800'
      case 'refining':
        return 'bg-purple-100 text-purple-800'
      case 'ready':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusLabel = (status: InspirationBoard['status']) => {
    switch (status) {
      case 'collecting':
        return '🌱 Collecting Ideas'
      case 'organizing':
        return '🏗️ Organizing'
      case 'refining':
        return '🎯 Refining Vision'
      case 'ready':
        return '🚀 Ready for Bids'
      default:
        return status
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (selectedBoard) {
    return (
      <>
        <BoardView 
          board={selectedBoard}
          onBack={() => setSelectedBoard(null)}
          onBoardUpdate={(updatedBoard) => {
            setBoards(prev => prev.map(b => b.id === updatedBoard.id ? updatedBoard : b))
            setSelectedBoard(updatedBoard)
          }}
        />
        
        {/* Iris Chat Assistant */}
        {showIrisChat && (
          <IrisChat
            board={selectedBoard}
            onClose={() => setShowIrisChat(false)}
          />
        )}
      </>
    )
  }

  return (
    <div className="relative">
      {/* Header */}
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Inspiration Boards</h1>
          <p className="text-gray-600">Collect and organize your home improvement ideas</p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => setShowIrisChat(!showIrisChat)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <MessageSquare className="w-5 h-5" />
            Chat with Iris
          </button>
          <button
            onClick={() => setShowBoardCreator(true)}
            className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Board
          </button>
        </div>
      </div>

      {/* Empty State */}
      {boards.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="mx-auto w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mb-6">
            <Sparkles className="w-12 h-12 text-primary-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Start Your First Inspiration Board
          </h2>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Collect images from anywhere, organize your ideas, and turn your dream into reality with AI assistance.
          </p>
          <button
            onClick={() => setShowBoardCreator(true)}
            className="inline-flex items-center gap-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Create Your First Board
          </button>
        </div>
      ) : (
        /* Board Grid */
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {boards.map((board) => (
            <div
              key={board.id}
              onClick={() => handleBoardClick(board)}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer overflow-hidden group"
            >
              {/* Cover Image or Placeholder */}
              <div className="aspect-video bg-gray-100 relative overflow-hidden">
                {board.cover_image_id ? (
                  <img 
                    src={`/api/placeholder/400/225`} 
                    alt={board.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Grid3X3 className="w-12 h-12 text-gray-400" />
                  </div>
                )}
                
                {/* Status Badge */}
                <div className="absolute top-2 right-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(board.status)}`}>
                    {getStatusLabel(board.status)}
                  </span>
                </div>

                {/* Image Count */}
                {board.image_count > 0 && (
                  <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1">
                    <ImageIcon className="w-3 h-3" />
                    {board.image_count}
                  </div>
                )}
              </div>

              {/* Board Info */}
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
                  {board.title}
                </h3>
                {board.description && (
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {board.description}
                  </p>
                )}
                {board.room_type && (
                  <div className="mt-2">
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {board.room_type}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Board Creator Modal */}
      {showBoardCreator && (
        <BoardCreator
          onClose={() => setShowBoardCreator(false)}
          onCreate={handleCreateBoard}
        />
      )}

      {/* Iris Chat Assistant */}
      {showIrisChat && (
        <IrisChat
          board={selectedBoard}
          onClose={() => setShowIrisChat(false)}
        />
      )}
    </div>
  )
}

export default InspirationDashboard