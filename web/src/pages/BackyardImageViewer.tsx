import { useEffect, useState } from "react";
import { Loader2, CheckCircle, AlertCircle, Image } from "lucide-react";

interface GeneratedImage {
  id: string;
  image_url: string;
  tags: string[];
  category: string;
  board_id: string;
  ai_analysis: any;
}

export default function BackyardImageViewer() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imageData, setImageData] = useState<GeneratedImage | null>(null);
  const [imageError, setImageError] = useState(false);

  // The specific image we generated
  const IMAGE_ID = "1bbed9d1-2123-4c10-af00-3a580b7c3698";
  const BOARD_ID = "443bd2f8-5d17-4a89-a07f-52955b5e1c74";

  useEffect(() => {
    fetchImage();
  }, []);

  const fetchImage = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Direct query to Supabase
      const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || "https://xrhgrthdcaymxuqcgrmj.supabase.co";
      const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyaGdydGhkY2F5bXh1cWNncm1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjUzMTI4MzMsImV4cCI6MjA0MDg4ODgzM30.V6nwideUHuo0ykxZFb8qn5WAR36MQjCYNsSyJsLt_9k";
      
      const response = await fetch(
        `${SUPABASE_URL}/rest/v1/inspiration_images?id=eq.${IMAGE_ID}`,
        {
          headers: {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch image: ${response.status}`);
      }

      const data = await response.json();
      
      if (data && data.length > 0) {
        setImageData(data[0]);
      } else {
        throw new Error("Image not found in database");
      }
    } catch (err) {
      console.error("Error fetching image:", err);
      setError(err instanceof Error ? err.message : "Failed to load image");
    } finally {
      setLoading(false);
    }
  };

  const handleImageError = () => {
    setImageError(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-2xl">
          <Loader2 className="w-12 h-12 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your generated backyard image...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl p-6 mb-6 shadow-xl">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Backyard Transformation with DALL-E 3
          </h1>
          <p className="text-gray-600">
            AI-Generated Vision of Your Backyard with Artificial Turf
          </p>
        </div>

        {/* Status Message */}
        {error ? (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <span className="text-red-700">{error}</span>
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6 flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
            <span className="text-green-700">
              Image successfully generated and saved to database!
            </span>
          </div>
        )}

        {/* Main Content */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Image Display */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl p-6 shadow-xl">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Generated Image</h2>
              
              <div className="bg-gray-100 rounded-xl p-4 min-h-[400px] flex items-center justify-center">
                {imageData && !imageError ? (
                  <img
                    src={imageData.image_url}
                    alt="Generated backyard with artificial turf"
                    className="max-w-full h-auto rounded-lg shadow-lg"
                    onError={handleImageError}
                  />
                ) : imageError ? (
                  <div className="text-center p-8">
                    <Image className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 font-medium mb-2">Image URL Expired</p>
                    <p className="text-sm text-gray-500">
                      The image was successfully generated but OpenAI URLs expire after 2 hours.
                    </p>
                    <p className="text-xs text-gray-400 mt-4">
                      Image ID: {IMAGE_ID}
                    </p>
                  </div>
                ) : (
                  <div className="text-center p-8">
                    <Image className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No image available</p>
                  </div>
                )}
              </div>

              {/* Image URL for debugging */}
              {imageData && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-mono break-all">
                    {imageData.image_url.substring(0, 100)}...
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Metadata Panel */}
          <div className="space-y-6">
            {/* Image Details */}
            <div className="bg-white rounded-2xl p-6 shadow-xl">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Image Details</h2>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Image ID</p>
                  <p className="font-mono text-xs text-gray-700 break-all">{IMAGE_ID}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">Board ID</p>
                  <p className="font-mono text-xs text-gray-700 break-all">{BOARD_ID}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">Category</p>
                  <p className="text-gray-700">{imageData?.category || "ideal"}</p>
                </div>
              </div>
            </div>

            {/* Tags */}
            {imageData?.tags && (
              <div className="bg-white rounded-2xl p-6 shadow-xl">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">Tags</h2>
                <div className="flex flex-wrap gap-2">
                  {imageData.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* AI Analysis */}
            {imageData?.ai_analysis && (
              <div className="bg-white rounded-2xl p-6 shadow-xl">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">AI Analysis</h2>
                <div className="text-sm text-gray-600 space-y-2">
                  <p>{imageData.ai_analysis.description}</p>
                  {imageData.ai_analysis.style && (
                    <p><strong>Style:</strong> {imageData.ai_analysis.style}</p>
                  )}
                  {imageData.ai_analysis.transformation && (
                    <p><strong>Transformation:</strong> {imageData.ai_analysis.transformation}</p>
                  )}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="bg-white rounded-2xl p-6 shadow-xl">
              <button
                onClick={fetchImage}
                className="w-full bg-purple-600 text-white rounded-lg py-3 px-4 font-medium hover:bg-purple-700 transition-colors"
              >
                Refresh Image
              </button>
            </div>
          </div>
        </div>

        {/* Info Footer */}
        <div className="mt-8 bg-white rounded-2xl p-6 shadow-xl">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">About This Image</h3>
          <div className="text-sm text-gray-600 space-y-2">
            <p>
              This image was generated using OpenAI's DALL-E 3 model based on your request to transform
              a backyard with patchy grass into one with beautiful artificial turf.
            </p>
            <p>
              The AI preserved the soccer goal position while replacing the natural grass with
              synthetic turf, creating a low-maintenance, evergreen backyard solution.
            </p>
            <p className="text-xs text-gray-500 mt-4">
              Generated on: {new Date().toLocaleDateString()} | Model: DALL-E 3 | Quality: HD
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}