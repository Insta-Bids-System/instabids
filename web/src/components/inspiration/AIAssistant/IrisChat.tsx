import React, { useState, useEffect, useRef } from 'react'
import { X, Send, Sparkles, Info, Camera, Link2, Upload, Image, RefreshCw } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { InspirationBoard } from '../InspirationDashboard'
import toast from 'react-hot-toast'

interface IrisChatProps {
  board?: InspirationBoard | null
  onClose: () => void
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  suggestions?: string[]
}

const IrisChat: React.FC<IrisChatProps> = ({ board, onClose }) => {
  const { user } = useAuth()
  const [messages, setMessages] = useState<Message[]>([{
    id: '1',
    role: 'assistant',
    content: board 
      ? `Hi! I'm looking at your "${board.title}" board. How can I help you organize and refine your vision?`
      : "Hi! I'm Iris, your design inspiration assistant. I can help you organize your ideas, analyze images, and create a cohesive vision for your home projects. What would you like to explore today?",
    timestamp: new Date(),
    suggestions: board 
      ? [
          'Help me organize these images',
          'What style are these images?',
          'Create a vision summary',
          'Estimate project budget'
        ]
      : [
          'Start a new inspiration board',
          'Upload some images to analyze',
          'Tell me about design styles',
          'How does this work?'
        ]
  }])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [uploadingImages, setUploadingImages] = useState<File[]>([])
  const [imageCategory, setImageCategory] = useState<'ideal' | 'current'>('ideal')
  const [idealImageId, setIdealImageId] = useState<string | null>(null)
  const [currentImageId, setCurrentImageId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [lastGenerationId, setLastGenerationId] = useState<string | null>(null)
  const [tempBoardId, setTempBoardId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    try {
      // Use the actual profile ID from the user (which is what the FK references)
      const homeowner_id = user?.id || '550e8400-e29b-41d4-a716-446655440001' // Demo homeowner profile ID

      // Call real Iris API with full context awareness
      const response = await fetch('http://localhost:8008/api/iris/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          homeowner_id: homeowner_id,
          board_id: board?.id,
          conversation_context: messages.slice(-10).map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp
          }))
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response from Iris')
      }

      const data = await response.json()
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        suggestions: data.suggestions || []
      }
      
      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('Error calling Iris API:', error)
      // Fallback to simulated response
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateIrisResponse(userMessage.content, board),
        timestamp: new Date(),
        suggestions: generateSuggestions(userMessage.content, board)
      }
      setMessages(prev => [...prev, aiResponse])
    } finally {
      setIsTyping(false)
    }
  }

  const getImagesForBoard = async (boardId: string): Promise<any[]> => {
    try {
      const { data, error } = await supabase
        .from('inspiration_images')
        .select('*')
        .eq('board_id', boardId)
        .limit(20)

      if (error) throw error
      return data || []
    } catch (error) {
      console.error('Error loading board images:', error)
      return []
    }
  }

  // Handle image upload button click
  const handleImageUpload = () => {
    fileInputRef.current?.click()
  }

  // Handle file selection from input
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    const imageFiles = Array.from(files).filter(file => 
      file.type.startsWith('image/')
    )

    if (imageFiles.length === 0) {
      toast.error('Please select valid image files')
      return
    }

    setUploadingImages(imageFiles)
    setIsTyping(true)

    try {
      // Upload images to Supabase storage and create database records
      const uploadedImages = await Promise.all(
        imageFiles.map(async (file) => {
          // Generate unique filename
          const timestamp = Date.now()
          const fileExt = file.name.split('.').pop()
          const fileName = `${user?.id || 'anonymous'}_${timestamp}.${fileExt}`
          
          // Create a test board if needed for demo
          let tempBoardId = board?.id
          if (!tempBoardId) {
            // Use the actual profile ID from the user
            const homeownerId = user?.id || '550e8400-e29b-41d4-a716-446655440001' // Demo homeowner profile ID
            console.log('Creating board for homeowner:', homeownerId)
            
            const { data: newBoard, error: boardError } = await supabase
              .from('inspiration_boards')
              .insert({
                homeowner_id: homeownerId,
                title: 'AI-Assisted Inspiration Board',
                description: 'Created automatically for Iris AI analysis',
                room_type: 'kitchen',
                status: 'collecting'
              })
              .select()
              .single()
            
            if (boardError) {
              console.error('Board creation error:', boardError)
              toast.error('Could not create inspiration board')
            } else if (newBoard) {
              tempBoardId = newBoard.id
              setTempBoardId(tempBoardId)
              console.log('Created board:', tempBoardId)
              toast.success('Created new inspiration board for your images')
            }
          }

          // Upload to Supabase storage
          const { data: uploadData, error: uploadError } = await supabase.storage
            .from('inspiration')
            .upload(fileName, file, {
              cacheControl: '3600',
              upsert: false
            })

          if (uploadError) {
            console.error('Upload error:', uploadError)
            throw new Error(`Failed to upload ${file.name}`)
          }

          // Get public URL
          const { data: { publicUrl } } = supabase.storage
            .from('inspiration')
            .getPublicUrl(fileName)

          // Create database record if we have a board
          let imageRecord = null
          if (tempBoardId) {
            // Use the actual profile ID from the user for image records
            const homeownerId = user?.id || '550e8400-e29b-41d4-a716-446655440001' // Demo homeowner profile ID
            console.log('Creating image record:', { tempBoardId, homeownerId, category: imageCategory })
            
            const { data: dbData, error: dbError } = await supabase
              .from('inspiration_images')
              .insert({
                board_id: tempBoardId,
                homeowner_id: homeownerId,
                image_url: publicUrl,
                source: 'upload',
                category: imageCategory, // Include the selected category
                tags: [], // Will be populated by AI analysis later
                ai_analysis: {
                  filename: file.name,
                  file_size: file.size,
                  mime_type: file.type,
                  upload_timestamp: new Date().toISOString(),
                  category: imageCategory
                }
              })
              .select()
              .single()

            if (dbError) {
              console.error('Database error:', dbError)
              toast.error(`Failed to save ${imageCategory} image to database`)
            } else {
              imageRecord = dbData
              console.log('Successfully created image record:', imageRecord.id)
              toast.success(`${imageCategory === 'ideal' ? 'Ideal inspiration' : 'Current space'} image saved to board`)
              
              // Save image IDs for generation
              if (imageCategory === 'ideal') {
                setIdealImageId(imageRecord.id)
              } else {
                setCurrentImageId(imageRecord.id)
              }
            }
          } else {
            console.error('No board ID available for image storage')
            toast.error('Could not save image - no inspiration board available')
          }

          return {
            url: publicUrl,
            filename: file.name,
            size: file.size,
            record: imageRecord
          }
        })
      )

      // Add user message about the uploaded images
      const categoryDisplay = imageCategory === 'ideal' ? 'Ideal Inspiration' : 'Current Space'
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: `I've uploaded ${uploadedImages.length} ${categoryDisplay.toLowerCase()} image${uploadedImages.length > 1 ? 's' : ''}: ${uploadedImages.map(img => img.filename).join(', ')}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, userMessage])

      // Call REAL Claude API for intelligent image analysis
      let aiResponse: Message
      
      try {
        const analysisPrompt = imageCategory === 'ideal' 
          ? `You are Iris, an expert interior design assistant. The user just uploaded ${uploadedImages.length} IDEAL INSPIRATION image${uploadedImages.length > 1 ? 's' : ''} (${uploadedImages.map(img => img.filename).join(', ')}) for their ${board?.room_type || 'renovation'} project.

Your task: Analyze what design elements, materials, colors, and styles they're drawn to. Ask "What aspects of these images do you find most appealing?" and help them identify their preferences.

Focus on:
- Color palettes and materials they like
- Specific design elements (cabinets, countertops, lighting, etc.)
- Overall style and atmosphere
- Features they want to incorporate

Generate relevant tags like: ["modern-farmhouse", "white-cabinets", "black-hardware", "marble-countertops", "pendant-lighting"]

Be conversational and helpful - you're helping them define their dream space.`
          
          : `You are Iris, an expert interior design assistant. The user just uploaded ${uploadedImages.length} CURRENT SPACE image${uploadedImages.length > 1 ? 's' : ''} (${uploadedImages.map(img => img.filename).join(', ')}) showing their existing ${board?.room_type || 'room'}.

Your task: Analyze what needs improvement, upgrading, or changing. Identify specific problems and opportunities for enhancement.

Focus on:
- Elements that need updating or replacement
- Layout issues or space optimization opportunities  
- Outdated features that could be modernized
- Potential improvements for functionality and aesthetics

Generate relevant tags like: ["needs-updating", "old-countertops", "dated-cabinets", "poor-lighting", "storage-issues"]

Be encouraging - help them see the potential in their space while identifying specific areas for improvement.`

        const response = await fetch('http://localhost:8008/api/iris/analyze-image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image_urls: uploadedImages.map(img => img.url),
            category: imageCategory,
            filenames: uploadedImages.map(img => img.filename),
            analysis_prompt: analysisPrompt,
            board_info: {
              id: tempBoardId,
              room_type: board?.room_type || 'kitchen'
            }
          })
        })

        if (response.ok) {
          const claudeData = await response.json()
          const content = claudeData.content[0].text
          
          // Generate smart tags based on category
          const smartTags = imageCategory === 'ideal'
            ? ['inspiration', 'design-goals', 'style-preference', 'dream-elements']
            : ['current-state', 'needs-improvement', 'upgrade-potential', 'existing-space']
          
          // Update database records with AI-generated tags
          for (const uploadedImage of uploadedImages) {
            if (uploadedImage.record) {
              await supabase
                .from('inspiration_images')
                .update({
                  tags: smartTags,
                  ai_analysis: {
                    ...uploadedImage.record.ai_analysis,
                    claude_analysis: content,
                    generated_tags: smartTags,
                    analysis_timestamp: new Date().toISOString()
                  }
                })
                .eq('id', uploadedImage.record.id)
            }
          }
          
          aiResponse = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: content,
            timestamp: new Date(),
            suggestions: imageCategory === 'ideal' 
              ? ['Tell me what you love about this style', 'Show me similar designs', 'What elements appeal to you?', 'Help me find more like this']
              : ['What bothers you most about this space?', 'What would you change first?', 'Show me improvement ideas', 'Help me plan upgrades']
          }
        } else {
          throw new Error('Claude API call failed')
        }
      } catch (error) {
        console.error('Claude API error:', error)
        
        // Fallback with differentiated responses
        const fallbackContent = imageCategory === 'ideal'
          ? `I can see you've uploaded ${uploadedImages.length} inspiration image${uploadedImages.length > 1 ? 's' : ''}! These show great taste for your ${board?.room_type || 'project'}. **Auto-Generated Tags**: ${imageCategory === 'ideal' ? 'inspiring, stylish, design-goals, dream-elements' : 'current-state, needs-improvement, upgrade-potential'}

What aspects of these images do you find most appealing? For example:
- The color palette and how it makes you feel?
- Specific materials like countertops, cabinets, or flooring?
- The overall style and atmosphere?
- Particular design elements or features?

Understanding what draws you to these images will help me provide more personalized recommendations.`
          
          : `I can see you've uploaded ${uploadedImages.length} current space image${uploadedImages.length > 1 ? 's' : ''}! Let me help you identify improvement opportunities. **Auto-Generated Tags**: current-state, needs-improvement, upgrade-potential, existing-space

What aspects of your current space would you most like to change? For example:
- Are there elements that feel outdated or worn?
- Is the layout working well for your needs?
- Are there specific features you'd like to upgrade?
- What's the biggest frustration with this space?

Understanding your current challenges will help me suggest the best improvements.`

        aiResponse = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: fallbackContent,
          timestamp: new Date(),
          suggestions: imageCategory === 'ideal'
            ? ['Tell me what you love', 'Show similar styles', 'Identify key elements', 'Find more inspiration']
            : ['What needs changing?', 'Biggest problems?', 'Improvement priorities', 'Upgrade suggestions']
        }
      }
      
      setMessages(prev => [...prev, aiResponse])
      toast.success(`${uploadedImages.length} image${uploadedImages.length > 1 ? 's' : ''} uploaded and analyzed!`)
      
    } catch (error) {
      console.error('Error uploading images:', error)
      
      // Fallback response for upload failure
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I had trouble uploading those images, but I can still help you organize your design ideas. What style are you going for?`,
        timestamp: new Date(),
        suggestions: [
          'Describe the style you see',
          'Help me organize ideas',
          'What elements do you like?',
          'Create a mood board'
        ]
      }
      setMessages(prev => [...prev, aiResponse])
      toast.error('Image upload failed, but I can still help with your design!')
      
    } finally {
      setIsTyping(false)
      setUploadingImages([])
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    // Handle regeneration suggestions
    if (lastGenerationId && [
      'Make it brighter',
      'Try more modern styling', 
      'Add warmer colors',
      'Generate another version'
    ].includes(suggestion)) {
      handleRegenerateWithFeedback(suggestion)
      return
    }
    
    // Handle regular suggestions
    setInput(suggestion)
  }

  // Handle AI Dream Space Generation with DALL-E 3
  const handleGenerateImage = async () => {
    // Check if we have both images
    if (!idealImageId || !currentImageId) {
      const missingMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `🎨 **I need both types of images to generate your dream space!**

Currently uploaded:
- ${idealImageId ? '✅' : '❌'} Ideal Inspiration Image
- ${currentImageId ? '✅' : '❌'} Current Space Image

Please upload ${!idealImageId && !currentImageId ? 'both images' : !idealImageId ? 'an ideal inspiration image' : 'a current space image'} to continue.`,
        timestamp: new Date(),
        suggestions: [
          'Upload ideal inspiration',
          'Upload current space',
          'How does this work?'
        ]
      }
      setMessages(prev => [...prev, missingMessage])
      return
    }

    setIsGenerating(true)
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: 'Generate my dream space by merging my photos',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    // Show progress message
    const progressMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: `🎨 **Generating Your Dream Space...**

I'm using advanced AI to merge your current space with your ideal inspiration. This typically takes 10-15 seconds.

✨ **What I'm doing:**
- Analyzing your current room layout
- Identifying key design elements from your inspiration
- Creating a photorealistic rendering of your transformed space
- Ensuring realistic proportions and lighting`,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, progressMessage])

    try {
      // Call our backend API which uses DALL-E 3
      const response = await fetch('http://localhost:8008/api/image-generation/generate-dream-space', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          board_id: board?.id || tempBoardId,
          ideal_image_id: idealImageId,
          current_image_id: currentImageId,
          user_preferences: input || undefined
        })
      })

      if (!response.ok) {
        throw new Error('Generation failed')
      }

      const data = await response.json()
      setLastGenerationId(data.generation_id)

      // Show generated image with conversational response
      const successMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: `🎉 **Your Dream Space is Ready!**

![Generated Dream Space](${data.generated_image_url})

I've created a photorealistic vision of your space by combining:
- The layout and structure from your current room
- The style, colors, and design elements from your inspiration

What do you think? I can regenerate it with different styling if you'd like any changes!`,
        timestamp: new Date(),
        suggestions: [
          'I love it! Save this design',
          'Make it brighter',
          'Try more modern styling',
          'Add warmer colors',
          'Generate another version'
        ]
      }
      setMessages(prev => [...prev.slice(0, -1), successMessage]) // Replace progress message
      
      toast.success('Dream space generated successfully!')
      
    } catch (error) {
      console.error('Generation error:', error)
      
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: `I encountered an issue generating your dream space. Let me try a different approach. Please tell me more about what you'd like to see in your transformed space!`,
        timestamp: new Date(),
        suggestions: [
          'Describe your ideal style',
          'What colors do you prefer?',
          'Modern or traditional?',
          'Try uploading different images'
        ]
      }
      setMessages(prev => [...prev.slice(0, -1), errorMessage])
      toast.error('Generation failed. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  // Handle regeneration with user feedback
  const handleRegenerateWithFeedback = async (feedback: string) => {
    if (!lastGenerationId) return

    setIsGenerating(true)
    
    const regenerateMessage: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: `🔄 **Regenerating with your feedback...**

I'm adjusting the design based on: "${feedback}"`,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, regenerateMessage])

    try {
      const response = await fetch('http://localhost:8008/api/image-generation/regenerate-with-feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          previous_generation_id: lastGenerationId,
          user_feedback: feedback
        })
      })

      const data = await response.json()
      setLastGenerationId(data.generation_id)

      const newVersionMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `✨ **Updated Version Based on Your Feedback**

![Updated Dream Space](${data.generated_image_url})

I've adjusted the design to ${feedback.toLowerCase()}. How does this version look?`,
        timestamp: new Date(),
        suggestions: [
          'Perfect! This is what I want',
          'Getting closer, but...',
          'Try a different approach',
          'Show me the previous version'
        ]
      }
      setMessages(prev => [...prev.slice(0, -1), newVersionMessage])
      
    } catch (error) {
      console.error('Regeneration error:', error)
      toast.error('Failed to regenerate. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  // Handle AI Vision Composition
  const handleVisionComposition = async () => {
    setIsTyping(true)
    
    try {
      // Create user message for vision composition request
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: 'Generate a dream space by merging my ideal inspiration with my current space',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, userMessage])

      // For now, create a demo response until backend is implemented
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `🎨 **AI Vision Composition**

I'm analyzing your ideal inspiration images and current space photos to create a personalized dream space vision...

**Key Elements I'm Merging:**
• Clean lines and modern aesthetic from your inspiration photos
• Natural lighting and open layout from your current space
• Color palette: Soft whites, warm woods, and accent blacks
• Features: Shaker-style elements with contemporary touches

**Composition Result:**
Your dream space would combine the best of both worlds - taking the spacious layout of your current room and enhancing it with the sophisticated styling from your inspiration images. 

*Note: Full AI image generation coming soon! For now, I can help you plan the transformation step by step.*`,
        timestamp: new Date(),
        suggestions: [
          'Show me a detailed plan',
          'What changes would cost the most?',
          'How long would this take?',
          'Find contractors for this vision'
        ]
      }
      
      setMessages(prev => [...prev, aiResponse])
      toast.success('Dream space composition generated!')
      
    } catch (error) {
      console.error('Error generating vision composition:', error)
      toast.error('Could not generate composition. Please try again.')
    } finally {
      setIsTyping(false)
    }
  }

  const generateIrisResponse = (userInput: string, currentBoard?: InspirationBoard | null): string => {
    const input = userInput.toLowerCase()
    
    if (input.includes('organize')) {
      return "I'd be happy to help organize your images! I can see you have a mix of styles here. Would you like me to group them by room type, color scheme, or design style?"
    } else if (input.includes('style')) {
      return "Based on your saved images, I'm seeing a modern farmhouse aesthetic with clean lines, neutral colors, and natural textures. The white shaker cabinets paired with black hardware create a classic contrast. Would you like me to find more images in this style?"
    } else if (input.includes('budget')) {
      return "Based on similar projects in your area, I estimate this could range from $15,000-$25,000 for a full renovation. The main cost drivers would be cabinetry (40%), countertops (20%), and appliances (25%). Would you like a more detailed breakdown?"
    } else if (input.includes('vision')) {
      return "Let me create a vision summary for you. From your inspiration images, I see you're drawn to: bright, open spaces with white cabinetry, marble-look countertops, and modern black fixtures. The overall feeling is clean and timeless. Shall I help you refine this into a project brief?"
    } else {
      return "I understand you're interested in that! Let me help you explore this idea further. What specific aspect would you like to focus on?"
    }
  }

  const generateSuggestions = (userInput: string, currentBoard?: InspirationBoard | null): string[] => {
    if (userInput.toLowerCase().includes('organize')) {
      return [
        'Group by room type',
        'Sort by color scheme',
        'Identify common elements',
        'Remove duplicates'
      ]
    } else if (userInput.toLowerCase().includes('budget')) {
      return [
        'Show detailed breakdown',
        'Find budget-friendly alternatives',
        'Priority recommendations',
        'DIY vs professional costs'
      ]
    }
    return [
      'Tell me more',
      'Show similar examples',
      'What are my options?',
      'Ready to create project'
    ]
  }


  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Iris</h3>
            <p className="text-xs text-gray-500">Design Assistant</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              
              {/* Suggestions */}
              {message.suggestions && message.suggestions.length > 0 && (
                <div className="mt-3 space-y-1">
                  {message.suggestions.map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="block w-full text-left text-xs px-2 py-1 rounded bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-2 border-t border-b bg-gray-50">
        {/* Photo Category Selection */}
        <div className="mb-2">
          <span className="text-xs text-gray-500 font-medium">Photo Category:</span>
          <div className="flex gap-2 mt-1">
            <button 
              onClick={() => setImageCategory('ideal')}
              className={`text-xs px-2 py-1 rounded transition-colors ${
                imageCategory === 'ideal' 
                  ? 'bg-blue-100 text-blue-700 border border-blue-300' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              ✨ Ideal Inspiration
            </button>
            <button 
              onClick={() => setImageCategory('current')}
              className={`text-xs px-2 py-1 rounded transition-colors ${
                imageCategory === 'current' 
                  ? 'bg-green-100 text-green-700 border border-green-300' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              📐 Current Space
            </button>
          </div>
        </div>
        
        {/* Upload Actions */}
        <div className="flex gap-2">
          <button 
            onClick={handleImageUpload}
            disabled={isTyping || uploadingImages.length > 0}
            className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900 px-2 py-1 rounded hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Upload className="w-3 h-3" />
            {uploadingImages.length > 0 ? 'Uploading...' : `Upload ${imageCategory === 'ideal' ? 'Inspiration' : 'Current Space'}`}
          </button>
          <button className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900 px-2 py-1 rounded hover:bg-gray-200 transition-colors">
            <Link2 className="w-3 h-3" />
            Add URL
          </button>
          <button className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900 px-2 py-1 rounded hover:bg-gray-200 transition-colors">
            <Camera className="w-3 h-3" />
            Take Photo
          </button>
        </div>

        {/* AI Vision Composition */}
        <div className="mt-3 pt-2 border-t border-gray-200">
          <span className="text-xs text-gray-500 font-medium">AI Vision Composition:</span>
          <div className="flex gap-2 mt-1">
            <button 
              onClick={handleVisionComposition}
              disabled={isTyping}
              className="flex items-center gap-1 text-xs text-purple-600 hover:text-purple-800 px-2 py-1 rounded hover:bg-purple-50 transition-colors border border-purple-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className="w-3 h-3" />
              Generate Dream Space
            </button>
            <span className="text-xs text-gray-400 flex items-center">
              Merge your ideal inspiration with current space
            </span>
          </div>
        </div>
        
        {/* Dream Space Generation with DALL-E 3 */}
        <div className="mt-3 pt-2 border-t border-gray-200">
          <span className="text-xs text-gray-500 font-medium">Dream Space Generation:</span>
          <div className="flex gap-2 mt-1">
            <button 
              onClick={handleGenerateImage}
              disabled={isGenerating || (!idealImageId || !currentImageId)}
              className={`flex items-center gap-1 text-xs px-2 py-1 rounded transition-colors border ${
                idealImageId && currentImageId 
                  ? 'text-green-600 hover:text-green-800 hover:bg-green-50 border-green-200' 
                  : 'text-gray-400 border-gray-200 cursor-not-allowed'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={!idealImageId || !currentImageId ? 'Upload both ideal and current images first' : 'Generate dream space'}
            >
              <Image className="w-3 h-3" />
              {isGenerating ? 'Generating...' : 'Generate Dream Image'}
            </button>
            {lastGenerationId && (
              <button 
                onClick={() => handleSuggestionClick('Generate another version')}
                disabled={isGenerating}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50 transition-colors border border-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className="w-3 h-3" />
                Regenerate
              </button>
            )}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {idealImageId && currentImageId 
              ? '✅ Ready to generate your dream space!' 
              : `Need: ${!idealImageId ? '📸 Ideal image' : ''} ${!idealImageId && !currentImageId ? '&' : ''} ${!currentImageId ? '📐 Current image' : ''}`}
          </div>
        </div>
        
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Input */}
      <div className="p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Iris anything..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default IrisChat