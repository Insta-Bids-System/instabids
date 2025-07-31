import React, { useState, useEffect } from 'react'
import { ArrowLeft, Plus, MoreVertical, Eye, Download, Trash2, Grid3X3, Image as ImageIcon } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { InspirationBoard } from './InspirationDashboard'
import { ImageUploader } from './ImageUploader'
import ImageCategorizer from './ImageCategorizer'
import AIAnalysisDisplay from './AIAnalysisDisplay'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/contexts/AuthContext'
import toast from 'react-hot-toast'

interface BoardViewProps {
  board: InspirationBoard
  onBack: () => void
  onBoardUpdate?: (board: InspirationBoard) => void
}

interface BoardImage {
  id: string
  board_id: string
  image_url: string
  thumbnail_url: string
  tags: string[]
  user_notes?: string
  position: number
  created_at: string
  ai_analysis?: any
}

const BoardView: React.FC<BoardViewProps> = ({ board, onBack, onBoardUpdate }) => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [images, setImages] = useState<BoardImage[]>([])
  const [loading, setLoading] = useState(true)
  const [showUploader, setShowUploader] = useState(false)
  const [selectedImage, setSelectedImage] = useState<BoardImage | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'columns'>('grid')

  useEffect(() => {
    loadImages()
  }, [board.id])

  const loadImages = async () => {
    try {
      setLoading(true)
      
      // Check for demo user - load from actual database
      const demoUser = localStorage.getItem('DEMO_USER')
      if (demoUser && board.homeowner_id === JSON.parse(demoUser).id) {
        // Load demo images from actual database  
        try {
          const { data, error } = await supabase
            .from('inspiration_images')
            .select('*')
            .eq('board_id', board.id)
            .order('position', { ascending: true })

          if (error) throw error
          setImages(data || [])
        } catch (error) {
          console.error('Error loading demo images:', error)
          setImages([])
        }
        setLoading(false)
        return
      }
      
      const { data, error } = await supabase
        .from('inspiration_images')
        .select('*')
        .eq('board_id', board.id)
        .order('position', { ascending: true })

      if (error) throw error
      setImages(data || [])
    } catch (error) {
      console.error('Error loading images:', error)
      toast.error('Failed to load images')
    } finally {
      setLoading(false)
    }
  }

  const handleUploadComplete = async (uploadedImages: any[]) => {
    // Reload images after upload
    await loadImages()
    setShowUploader(false)
    
    // Update board status if it was collecting
    if (board.status === 'collecting' && images.length + uploadedImages.length >= 5) {
      // Check if demo user
      const demoUser = localStorage.getItem('DEMO_USER')
      if (demoUser) {
        // For demo users, just update locally
        if (onBoardUpdate) {
          onBoardUpdate({ ...board, status: 'organizing' })
        }
      } else {
        try {
          const { error } = await supabase
            .from('inspiration_boards')
            .update({ status: 'organizing' })
            .eq('id', board.id)
          
          if (!error && onBoardUpdate) {
            onBoardUpdate({ ...board, status: 'organizing' })
          }
        } catch (error) {
          console.error('Error updating board status:', error)
        }
      }
    }
  }

  const handleDeleteImage = async (imageId: string) => {
    if (!confirm('Are you sure you want to delete this image?')) return

    try {
      const { error } = await supabase
        .from('inspiration_images')
        .delete()
        .eq('id', imageId)

      if (error) throw error

      setImages(prev => prev.filter(img => img.id !== imageId))
      toast.success('Image deleted')
    } catch (error) {
      console.error('Error deleting image:', error)
      toast.error('Failed to delete image')
    }
  }

  const handleStartProject = () => {
    // Prepare vision data for CIA
    const visionImages = images.filter(img => img.tags.includes('vision'))
    const currentImages = images.filter(img => img.tags.includes('current'))
    const inspirationImages = images.filter(img => !img.tags.includes('current') && !img.tags.includes('vision'))
    
    // Create context data to pass to CIA
    const visionData = {
      board_id: board.id,
      board_title: board.title,
      board_description: board.description,
      vision_images: visionImages.map(img => ({
        id: img.id,
        url: img.image_url,
        analysis: img.ai_analysis
      })),
      current_images: currentImages.map(img => ({
        id: img.id,
        url: img.image_url,
        analysis: img.ai_analysis
      })),
      inspiration_images: inspirationImages.map(img => ({
        id: img.id,
        url: img.image_url,
        analysis: img.ai_analysis
      }))
    }
    
    // Navigate to chat with vision context
    navigate('/chat', { 
      state: { 
        fromVision: true,
        visionData: visionData,
        message: `I've created a vision board called "${board.title}" and I'm ready to start this project. I have ${visionImages.length} vision images showing what I want to achieve.`
      }
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{board.title}</h2>
            {board.description && (
              <p className="text-sm text-gray-600">{board.description}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : ''}`}
            >
              <Grid3X3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('columns')}
              className={`p-1.5 rounded ${viewMode === 'columns' ? 'bg-white shadow-sm' : ''}`}
            >
              <ImageIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Add Images Button */}
          <button
            onClick={() => setShowUploader(!showUploader)}
            className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Images
          </button>
        </div>
      </div>

      {/* Uploader Section */}
      {showUploader && (
        <div className="p-4 bg-gray-50 border-b">
          <ImageUploader
            boardId={board.id}
            onUploadComplete={handleUploadComplete}
            onClose={() => setShowUploader(false)}
          />
        </div>
      )}

      {/* Images Section */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : images.length === 0 ? (
          <div className="text-center py-12">
            <ImageIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No images yet</h3>
            <p className="text-gray-600 mb-4">Start building your vision by adding inspiration images</p>
            <button
              onClick={() => setShowUploader(true)}
              className="inline-flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Your First Images
            </button>
          </div>
        ) : viewMode === 'grid' ? (
          /* Grid View */
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {images.map((image) => (
              <div
                key={image.id}
                className="group relative aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer"
                onClick={() => setSelectedImage(image)}
              >
                <img
                  src={image.thumbnail_url || image.image_url}
                  alt="Inspiration"
                  className="w-full h-full object-cover"
                />
                
                {/* Hover Overlay with AI Analysis */}
                {image.ai_analysis ? (
                  <AIAnalysisDisplay 
                    analysis={image.ai_analysis}
                    imageType={image.tags.includes('current') ? 'current' : image.tags.includes('vision') ? 'vision' : 'inspiration'}
                  />
                ) : (
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-opacity">
                    <div className="absolute inset-0 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity p-2">
                      {/* Category Selector */}
                      <div className="mb-2">
                        <ImageCategorizer
                          imageId={image.id}
                          currentTags={image.tags}
                          onTagsUpdate={(newTags) => {
                            setImages(prev => prev.map(img => 
                              img.id === image.id ? { ...img, tags: newTags } : img
                            ))
                          }}
                        />
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            window.open(image.image_url, '_blank')
                          }}
                          className="p-2 bg-white rounded-full hover:bg-gray-100"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteImage(image.id)
                          }}
                          className="p-2 bg-white rounded-full hover:bg-gray-100"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Tags */}
                {image.tags.length > 0 && (
                  <div className="absolute bottom-2 left-2 right-2">
                    <div className="flex flex-wrap gap-1">
                      {image.tags.slice(0, 2).map((tag, idx) => (
                        <span
                          key={idx}
                          className="text-xs bg-black bg-opacity-60 text-white px-2 py-0.5 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                      {image.tags.length > 2 && (
                        <span className="text-xs bg-black bg-opacity-60 text-white px-2 py-0.5 rounded">
                          +{image.tags.length - 2}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          /* Column View (Three Columns) */
          <div className="grid grid-cols-3 gap-6">
            {/* Current Space */}
            <div>
              <h3 className="font-medium text-gray-900 mb-4">Current Space</h3>
              <div className="space-y-4">
                {images.filter(img => img.tags.includes('current')).map((image) => (
                  <div key={image.id} className="group relative aspect-video bg-gray-100 rounded-lg overflow-hidden cursor-pointer">
                    <img
                      src={image.thumbnail_url || image.image_url}
                      alt="Current space"
                      className="w-full h-full object-cover"
                    />
                    {image.ai_analysis && (
                      <AIAnalysisDisplay 
                        analysis={image.ai_analysis}
                        imageType="current"
                      />
                    )}
                  </div>
                ))}
                {images.filter(img => img.tags.includes('current')).length === 0 && (
                  <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                    <p className="text-sm text-gray-500">No current space photos</p>
                  </div>
                )}
              </div>
            </div>

            {/* Inspiration */}
            <div>
              <h3 className="font-medium text-gray-900 mb-4">Inspiration</h3>
              <div className="space-y-4">
                {images.filter(img => !img.tags.includes('current') && !img.tags.includes('vision')).map((image) => (
                  <div key={image.id} className="group relative aspect-video bg-gray-100 rounded-lg overflow-hidden cursor-pointer">
                    <img
                      src={image.thumbnail_url || image.image_url}
                      alt="Inspiration"
                      className="w-full h-full object-cover"
                    />
                    {image.ai_analysis && (
                      <AIAnalysisDisplay 
                        analysis={image.ai_analysis}
                        imageType="inspiration"
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* My Vision */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-gray-900">My Vision</h3>
                {images.filter(img => img.tags.includes('vision')).length > 0 && (
                  <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full">
                    {images.filter(img => img.tags.includes('vision')).length} images
                  </span>
                )}
              </div>
              <div className="space-y-4">
                {images.filter(img => img.tags.includes('vision')).map((image) => (
                  <div key={image.id} className="group relative aspect-video bg-gray-100 rounded-lg overflow-hidden cursor-pointer">
                    <img
                      src={image.thumbnail_url || image.image_url}
                      alt="Vision"
                      className="w-full h-full object-cover"
                    />
                    {image.ai_analysis && (
                      <AIAnalysisDisplay 
                        analysis={image.ai_analysis}
                        imageType="vision"
                      />
                    )}
                  </div>
                ))}
                {images.filter(img => img.tags.includes('vision')).length === 0 && (
                  <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                    <p className="text-sm text-gray-500">Build your vision</p>
                  </div>
                )}
              </div>
              
              {/* CIA Handoff Button */}
              {images.filter(img => img.tags.includes('vision')).length > 0 && (
                <button
                  onClick={() => handleStartProject()}
                  className="w-full mt-4 bg-primary-600 text-white px-4 py-3 rounded-lg hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Start Project from Vision
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BoardView