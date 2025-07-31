// API service for connecting to the Instabids backend
const API_BASE_URL = 'http://localhost:8008'; // Updated port to match actual API server
console.log('FORCED API_BASE_URL:', API_BASE_URL);

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  phase?: string;
  extractedData?: any;
}

export interface ChatMessage {
  message: string;
  images?: string[];
  user_id?: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  phase?: string;
  extractedData?: any;
  sessionId?: string;
  conversationState?: any;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      console.log(`[API] Making request to: ${url}`);
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(`[API] Response:`, data);
      
      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error(`[API] Error in ${endpoint}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Health check endpoint
  async healthCheck(): Promise<ApiResponse<{ status: string; agents: string[] }>> {
    return this.request('/');
  }

  // Chat with CIA agent
  async sendChatMessage(
    message: string,
    images: string[] = [],
    userId?: string,
    sessionId?: string
  ): Promise<ApiResponse<ChatResponse>> {
    const payload: ChatMessage = {
      message,
      images,
      user_id: userId,
      session_id: sessionId,
    };

    return this.request<ChatResponse>('/api/cia/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // Process conversation with JAA (Job Assessment Agent)
  async processWithJAA(
    conversationId: string
  ): Promise<ApiResponse<any>> {
    return this.request(`/api/jaa/process/${conversationId}`, {
      method: 'POST',
    });
  }

  // Get conversation history
  async getConversation(
    conversationId: string
  ): Promise<ApiResponse<any>> {
    return this.request(`/api/conversation/${conversationId}`);
  }

  // Get user's conversations
  async getUserConversations(
    userId: string
  ): Promise<ApiResponse<any[]>> {
    return this.request(`/api/user/${userId}/conversations`);
  }

  // Create new conversation
  async createConversation(
    userId: string,
    projectType?: string
  ): Promise<ApiResponse<{ conversationId: string }>> {
    return this.request('/api/conversation', {
      method: 'POST',
      body: JSON.stringify({
        userId,
        projectType,
      }),
    });
  }

  // Get project details from bid card
  async getProjectDetails(
    projectId: string
  ): Promise<ApiResponse<any>> {
    return this.request(`/api/project/${projectId}`);
  }

  // Contractor endpoints
  async getAvailableProjects(
    contractorId: string,
    filters?: {
      type?: string;
      location?: string;
      budgetMin?: number;
      budgetMax?: number;
      urgency?: string;
    }
  ): Promise<ApiResponse<any[]>> {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/api/contractor/${contractorId}/projects${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return this.request(endpoint);
  }

  // Submit bid for a project
  async submitBid(
    projectId: string,
    contractorId: string,
    bidData: {
      amount: number;
      timeline: string;
      description: string;
      materials?: string;
    }
  ): Promise<ApiResponse<any>> {
    return this.request(`/api/project/${projectId}/bid`, {
      method: 'POST',
      body: JSON.stringify({
        contractorId,
        ...bidData,
      }),
    });
  }

  // Get contractor stats and dashboard data
  async getContractorDashboard(
    contractorId: string
  ): Promise<ApiResponse<{
    stats: any;
    recentProjects: any[];
    activeBids: any[];
  }>> {
    return this.request(`/api/contractor/${contractorId}/dashboard`);
  }

  // File upload helper for images
  async uploadImages(
    files: File[]
  ): Promise<ApiResponse<string[]>> {
    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(`image_${index}`, file);
      });

      const response = await fetch(`${API_BASE_URL}/api/upload/images`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data.urls || [],
      };
    } catch (error) {
      console.error('[API] Upload error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      };
    }
  }

  // Test connection to backend
  async testConnection(): Promise<boolean> {
    try {
      const result = await this.healthCheck();
      return result.success;
    } catch (error) {
      console.error('[API] Connection test failed:', error);
      return false;
    }
  }
}

// Helper function for single file upload
export async function uploadFile(file: File): Promise<{ url: string; name: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/upload/file`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }

  const data = await response.json();
  return {
    url: data.url,
    name: file.name
  };
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;