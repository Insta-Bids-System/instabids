import React, { useState } from 'react'
import { Home, Sparkles, Target } from 'lucide-react'
import { supabase } from '@/lib/supabase'
import toast from 'react-hot-toast'

interface ImageCategorizerProps {
  imageId: string
  currentTags: string[]
  onTagsUpdate: (newTags: string[]) => void
}

const ImageCategorizer: React.FC<ImageCategorizerProps> = ({ 
  imageId, 
  currentTags, 
  onTagsUpdate 
}) => {
  const [updating, setUpdating] = useState(false)
  
  const getCategory = () => {
    if (currentTags.includes('current')) return 'current'
    if (currentTags.includes('vision')) return 'vision'
    return 'inspiration'
  }
  
  const [category, setCategory] = useState(getCategory())

  const updateCategory = async (newCategory: 'current' | 'inspiration' | 'vision') => {
    if (updating || newCategory === category) return
    
    setUpdating(true)
    
    try {
      // Remove old category tags and add new one
      let newTags = currentTags.filter(tag => !['current', 'vision'].includes(tag))
      
      if (newCategory === 'current') {
        newTags.push('current')
      } else if (newCategory === 'vision') {
        newTags.push('vision')
      }
      // 'inspiration' has no specific tag - it's the default
      
      const { error } = await supabase
        .from('inspiration_images')
        .update({ tags: newTags })
        .eq('id', imageId)
      
      if (error) throw error
      
      setCategory(newCategory)
      onTagsUpdate(newTags)
      toast.success(`Moved to ${newCategory === 'current' ? 'Current Space' : newCategory === 'vision' ? 'My Vision' : 'Inspiration'}`)
    } catch (error) {
      console.error('Error updating category:', error)
      toast.error('Failed to update category')
    } finally {
      setUpdating(false)
    }
  }

  return (
    <div className="flex gap-1 p-1 bg-white/90 rounded-lg">
      <button
        onClick={() => updateCategory('current')}
        disabled={updating}
        className={`p-1.5 rounded transition-all ${
          category === 'current' 
            ? 'bg-blue-500 text-white' 
            : 'hover:bg-gray-100 text-gray-600'
        }`}
        title="Current Space"
      >
        <Home className="w-4 h-4" />
      </button>
      
      <button
        onClick={() => updateCategory('inspiration')}
        disabled={updating}
        className={`p-1.5 rounded transition-all ${
          category === 'inspiration' 
            ? 'bg-purple-500 text-white' 
            : 'hover:bg-gray-100 text-gray-600'
        }`}
        title="Inspiration"
      >
        <Sparkles className="w-4 h-4" />
      </button>
      
      <button
        onClick={() => updateCategory('vision')}
        disabled={updating}
        className={`p-1.5 rounded transition-all ${
          category === 'vision' 
            ? 'bg-green-500 text-white' 
            : 'hover:bg-gray-100 text-gray-600'
        }`}
        title="My Vision"
      >
        <Target className="w-4 h-4" />
      </button>
    </div>
  )
}

export default ImageCategorizer