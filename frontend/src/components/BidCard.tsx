import React, { useState } from 'react';
import { Calendar, Clock, MapPin, DollarSign, Home, Camera, ChevronLeft, ChevronRight, X, Users, AlertCircle } from 'lucide-react';

interface BidCardProps {
  bidCard: {
    id: string;
    public_token?: string;
    project_type: string;
    timeline: string;
    urgency: string;
    budget_display: string;
    budget_range?: {
      min: number;
      max: number;
    };
    location: {
      city: string;
      state: string;
      neighborhood?: string;
    };
    project_details: {
      scope_of_work?: string[];
      special_requirements?: string[];
      property_details?: {
        size?: string;
        year_built?: string;
        style?: string;
      };
    };
    photo_urls?: string[];
    hero_image_url?: string;
    contractor_count: number;
    created_at: string;
    homeowner_ready: boolean;
    views?: number;
  };
  variant?: 'full' | 'preview' | 'email';
  onViewDetails?: () => void;
  onExpressInterest?: () => void;
}

const BidCard: React.FC<BidCardProps> = ({ bidCard, variant = 'full', onViewDetails, onExpressInterest }) => {
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [showPhotoModal, setShowPhotoModal] = useState(false);

  const photos = bidCard.photo_urls || [];
  const hasPhotos = photos.length > 0;

  const formatProjectType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency?.toLowerCase()) {
      case 'emergency':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'week':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'month':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getUrgencyText = (urgency: string) => {
    switch (urgency?.toLowerCase()) {
      case 'emergency':
        return 'Urgent - ASAP';
      case 'week':
        return 'Within 7 Days';
      case 'month':
        return 'Within 30 Days';
      default:
        return 'Flexible Timeline';
    }
  };

  const getDaysAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const navigatePhoto = (direction: 'prev' | 'next') => {
    if (direction === 'prev') {
      setCurrentPhotoIndex((prev) => (prev > 0 ? prev - 1 : photos.length - 1));
    } else {
      setCurrentPhotoIndex((prev) => (prev < photos.length - 1 ? prev + 1 : 0));
    }
  };

  if (variant === 'email') {
    // Simplified version for email
    return (
      <div style={{ 
        border: '1px solid #e5e7eb', 
        borderRadius: '8px', 
        padding: '24px',
        backgroundColor: '#ffffff',
        fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif'
      }}>
        <h2 style={{ fontSize: '24px', marginBottom: '16px', color: '#111827' }}>
          {formatProjectType(bidCard.project_type)}
        </h2>
        <div style={{ marginBottom: '16px' }}>
          <span style={{ 
            backgroundColor: '#fef3c7', 
            color: '#92400e',
            padding: '4px 12px',
            borderRadius: '4px',
            fontSize: '14px'
          }}>
            {getUrgencyText(bidCard.urgency)}
          </span>
        </div>
        <p style={{ color: '#6b7280', marginBottom: '16px' }}>
          📍 {bidCard.location.city}, {bidCard.location.state} • 
          💰 {bidCard.budget_display} • 
          👥 {bidCard.contractor_count} contractors needed
        </p>
        <a href={`https://instabids.com/join?bid=${bidCard.public_token || bidCard.id}&src=email`} 
           style={{ 
             display: 'inline-block',
             backgroundColor: '#2563eb',
             color: '#ffffff',
             padding: '16px 32px',
             borderRadius: '6px',
             textDecoration: 'none',
             fontWeight: '600',
             fontSize: '16px'
           }}>
          Join InstaBids - Submit Quotes for Free
        </a>
        <p style={{ 
          color: '#6b7280', 
          fontSize: '14px', 
          textAlign: 'center', 
          marginTop: '12px' 
        }}>
          No longer pay for leads, only jobs
        </p>
      </div>
    );
  }

  if (variant === 'preview') {
    // Card preview for lists
    return (
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
           onClick={onViewDetails}>
        {hasPhotos && (
          <div className="relative h-48 bg-gray-100">
            <img 
              src={bidCard.hero_image_url || photos[0]} 
              alt={bidCard.project_type}
              className="w-full h-full object-cover"
            />
            {photos.length > 1 && (
              <div className="absolute bottom-2 right-2 bg-black bg-opacity-60 text-white px-2 py-1 rounded text-sm">
                <Camera className="w-4 h-4 inline mr-1" />
                {photos.length}
              </div>
            )}
            <div className={`absolute top-2 left-2 px-3 py-1 rounded-full text-xs font-medium ${getUrgencyColor(bidCard.urgency)}`}>
              {getUrgencyText(bidCard.urgency)}
            </div>
          </div>
        )}
        
        <div className="p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {formatProjectType(bidCard.project_type)}
          </h3>
          
          <div className="space-y-2 text-sm text-gray-600">
            <div className="flex items-center">
              <MapPin className="w-4 h-4 mr-2 text-gray-400" />
              {bidCard.location.neighborhood 
                ? `${bidCard.location.neighborhood}, ${bidCard.location.city}`
                : `${bidCard.location.city}, ${bidCard.location.state}`}
            </div>
            <div className="flex items-center">
              <DollarSign className="w-4 h-4 mr-2 text-gray-400" />
              {bidCard.budget_display}
            </div>
            <div className="flex items-center">
              <Users className="w-4 h-4 mr-2 text-gray-400" />
              Looking for {bidCard.contractor_count} contractors
            </div>
          </div>
          
          <div className="mt-4 flex items-center justify-between">
            <span className="text-xs text-gray-500">{getDaysAgo(bidCard.created_at)}</span>
            {bidCard.views && (
              <span className="text-xs text-gray-500">{bidCard.views} views</span>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Full bid card display
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Photo Gallery Section */}
      {hasPhotos && (
        <div className="relative">
          <div className="relative h-96 bg-gray-900">
            <img 
              src={photos[currentPhotoIndex]} 
              alt={`${bidCard.project_type} photo ${currentPhotoIndex + 1}`}
              className="w-full h-full object-contain cursor-pointer"
              onClick={() => setShowPhotoModal(true)}
            />
            
            {photos.length > 1 && (
              <>
                <button 
                  onClick={() => navigatePhoto('prev')}
                  className="absolute left-4 top-1/2 -translate-y-1/2 bg-white bg-opacity-80 hover:bg-opacity-100 rounded-full p-2 shadow-lg transition"
                >
                  <ChevronLeft className="w-6 h-6" />
                </button>
                <button 
                  onClick={() => navigatePhoto('next')}
                  className="absolute right-4 top-1/2 -translate-y-1/2 bg-white bg-opacity-80 hover:bg-opacity-100 rounded-full p-2 shadow-lg transition"
                >
                  <ChevronRight className="w-6 h-6" />
                </button>
                
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
                  {photos.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentPhotoIndex(index)}
                      className={`w-2 h-2 rounded-full transition ${
                        index === currentPhotoIndex ? 'bg-white' : 'bg-white bg-opacity-50'
                      }`}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
          
          {/* Photo thumbnails */}
          {photos.length > 1 && (
            <div className="bg-gray-100 p-2 flex space-x-2 overflow-x-auto">
              {photos.map((photo, index) => (
                <img
                  key={index}
                  src={photo}
                  alt={`Thumbnail ${index + 1}`}
                  className={`w-20 h-20 object-cover rounded cursor-pointer border-2 transition ${
                    index === currentPhotoIndex ? 'border-blue-500' : 'border-transparent'
                  }`}
                  onClick={() => setCurrentPhotoIndex(index)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Content Section */}
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {formatProjectType(bidCard.project_type)}
            </h2>
            <div className="flex items-center space-x-4 text-gray-600">
              <div className="flex items-center">
                <MapPin className="w-5 h-5 mr-1" />
                <span>{bidCard.location.city}, {bidCard.location.state}</span>
              </div>
              <div className="flex items-center">
                <Calendar className="w-5 h-5 mr-1" />
                <span>{getDaysAgo(bidCard.created_at)}</span>
              </div>
            </div>
          </div>
          
          <div className={`px-4 py-2 rounded-full text-sm font-medium border ${getUrgencyColor(bidCard.urgency)}`}>
            <Clock className="w-4 h-4 inline mr-1" />
            {getUrgencyText(bidCard.urgency)}
          </div>
        </div>

        {/* Budget Section */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Project Budget</p>
              <p className="text-2xl font-bold text-gray-900">{bidCard.budget_display}</p>
            </div>
            <DollarSign className="w-8 h-8 text-gray-400" />
          </div>
        </div>

        {/* Project Details */}
        {bidCard.project_details && (
          <div className="space-y-4 mb-6">
            {bidCard.project_details.scope_of_work && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Scope of Work</h3>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {bidCard.project_details.scope_of_work.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {bidCard.project_details.property_details && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Property Details</h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  {bidCard.project_details.property_details.size && (
                    <div>
                      <p className="text-gray-500">Size</p>
                      <p className="font-medium">{bidCard.project_details.property_details.size}</p>
                    </div>
                  )}
                  {bidCard.project_details.property_details.year_built && (
                    <div>
                      <p className="text-gray-500">Year Built</p>
                      <p className="font-medium">{bidCard.project_details.property_details.year_built}</p>
                    </div>
                  )}
                  {bidCard.project_details.property_details.style && (
                    <div>
                      <p className="text-gray-500">Style</p>
                      <p className="font-medium">{bidCard.project_details.property_details.style}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Homeowner Status */}
        {bidCard.homeowner_ready && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-center text-green-800">
              <AlertCircle className="w-5 h-5 mr-2" />
              <p className="font-medium">Homeowner is ready to review bids and start immediately</p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col space-y-4">
          <button
            onClick={onExpressInterest}
            className="w-full bg-blue-600 text-white py-4 px-6 rounded-lg font-semibold hover:bg-blue-700 transition text-lg"
          >
            Join InstaBids - Submit Quotes for Free
          </button>
          <p className="text-center text-gray-600 text-sm">
            No longer pay for leads, only jobs
          </p>
          {onViewDetails && (
            <button
              onClick={onViewDetails}
              className="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50 transition"
            >
              Share This Project
            </button>
          )}
        </div>

        {/* Stats */}
        <div className="mt-6 pt-6 border-t flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-4">
            <span>
              <Users className="w-4 h-4 inline mr-1" />
              {bidCard.contractor_count} contractors needed
            </span>
            {bidCard.views && (
              <span>{bidCard.views} views</span>
            )}
          </div>
          <span>Bid #{bidCard.id.slice(-6).toUpperCase()}</span>
        </div>
      </div>

      {/* Photo Modal */}
      {showPhotoModal && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center"
             onClick={() => setShowPhotoModal(false)}>
          <button
            onClick={() => setShowPhotoModal(false)}
            className="absolute top-4 right-4 text-white hover:text-gray-300"
          >
            <X className="w-8 h-8" />
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigatePhoto('prev');
            }}
            className="absolute left-4 text-white hover:text-gray-300"
          >
            <ChevronLeft className="w-12 h-12" />
          </button>
          
          <img
            src={photos[currentPhotoIndex]}
            alt={`Full size photo ${currentPhotoIndex + 1}`}
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigatePhoto('next');
            }}
            className="absolute right-4 text-white hover:text-gray-300"
          >
            <ChevronRight className="w-12 h-12" />
          </button>
          
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white">
            {currentPhotoIndex + 1} / {photos.length}
          </div>
        </div>
      )}
    </div>
  );
};

export default BidCard;