import { User, Competition, CompetitionCreateRequest, CompetitionUpdateRequest, ApiError, Team, TeamCreateRequest, TeamJoinRequest, StepIngestRequest, StepIngestResponse, StepHistoryResponse, LeaderboardResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
const USE_DEV_AUTH = import.meta.env.VITE_USE_DEV_AUTH === 'true';

class ApiClient {
  private async getAuthHeaders(): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (USE_DEV_AUTH) {
      const devEmail = localStorage.getItem('devEmail');
      if (devEmail) {
        headers['X-Dev-User'] = devEmail;
      }
    } else {
      // Firebase auth token
      try {
        const { firebaseGetIdToken } = await import('./firebase');
        const token = await firebaseGetIdToken();
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
          localStorage.setItem('firebaseToken', token);
        } else {
          // Fallback to stored token if available
          const storedToken = localStorage.getItem('firebaseToken');
          if (storedToken) {
            headers['Authorization'] = `Bearer ${storedToken}`;
          }
        }
      } catch (error) {
        // Firebase not configured, use stored token
        const storedToken = localStorage.getItem('firebaseToken');
        if (storedToken) {
          headers['Authorization'] = `Bearer ${storedToken}`;
        }
      }
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      if (response.status === 401) {
        // Redirect to login
        localStorage.removeItem('devEmail');
        localStorage.removeItem('firebaseToken');
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }
      
      if (response.status === 403) {
        throw new Error('Not authorized');
      }

      if (response.status === 409) {
        try {
          const error: ApiError = await response.json();
          throw new Error(error.detail || 'Conflict: Resource already exists');
        } catch {
          throw new Error('Conflict: Resource already exists');
        }
      }

      try {
        const error: ApiError = await response.json();
        throw new Error(error.detail || 'An error occurred');
      } catch {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    }

    return response.json();
  }

  async getHealth(): Promise<{ ok: boolean }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return this.handleResponse(response);
  }

  async getMe(): Promise<User> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/me`, {
      headers,
    });
    return this.handleResponse(response);
  }

  async getCompetitions(params?: {
    status?: string;
    tz?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ rows: Competition[]; total: number; page: number; page_size: number; total_pages: number }> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.tz) queryParams.append('tz', params.tz);
    if (params?.search) queryParams.append('search', params.search);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    
    const url = `${API_BASE_URL}/competitions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const headers = await this.getAuthHeaders();
    const response = await fetch(url, {
      headers,
    });
    return this.handleResponse(response);
  }

  async getUsers(): Promise<{ rows: User[] }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/users`, {
      headers,
    });
    return this.handleResponse(response);
  }

  async getUser(uid: string): Promise<User> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/users/${uid}`, {
      headers,
    });
    return this.handleResponse(response);
  }

  async updateUserRole(uid: string, role: 'ADMIN' | 'MEMBER'): Promise<{ ok: boolean }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/users/${uid}?role=${role}`, {
      method: 'PATCH',
      headers,
    });
    return this.handleResponse(response);
  }

  async getCompetition(compId: string): Promise<Competition> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/competitions/${compId}`, {
      headers,
    });
    return this.handleResponse(response);
  }

  async createCompetition(data: CompetitionCreateRequest): Promise<{ ok: boolean; comp_id: string }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/competitions`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  async updateCompetition(compId: string, data: CompetitionUpdateRequest): Promise<{ ok: boolean }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/competitions/${compId}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  async deleteCompetition(compId: string): Promise<{ ok: boolean }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/competitions/${compId}`, {
      method: 'DELETE',
      headers,
    });
    return this.handleResponse(response);
  }

  // Team Management
  async getCompetitionTeams(compId: string): Promise<{ rows: Team[] }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/competitions/${compId}/teams`, {
      headers,
    });
    return this.handleResponse(response);
  }

  async getTeam(teamId: string): Promise<Team> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/teams/${teamId}`, {
      headers,
    });
    return this.handleResponse(response);
  }

  async createTeam(data: TeamCreateRequest): Promise<{ team_id: string; name: string; comp_id: string }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/teams`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  async joinTeam(data: TeamJoinRequest): Promise<{ ok: boolean; team_id: string }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/teams/join`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  async leaveTeam(teamId: string, uid: string): Promise<{ ok: boolean }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/teams/${teamId}/members/${uid}`, {
      method: 'DELETE',
      headers,
    });
    return this.handleResponse(response);
  }

  // Step Ingestion
  async submitSteps(data: StepIngestRequest): Promise<StepIngestResponse> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/ingest/steps`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  async getUserStepHistory(uid: string, compId?: string): Promise<StepHistoryResponse> {
    const headers = await this.getAuthHeaders();
    const url = compId 
      ? `${API_BASE_URL}/users/${uid}/steps?comp_id=${compId}`
      : `${API_BASE_URL}/users/${uid}/steps`;
    const response = await fetch(url, {
      headers,
    });
    return this.handleResponse(response);
  }

  // Leaderboards
  async getIndividualLeaderboard(params?: {
    comp_id?: string;
    date?: string;
    start_date?: string;
    end_date?: string;
    team_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<LeaderboardResponse> {
    const headers = await this.getAuthHeaders();
    const queryParams = new URLSearchParams();
    if (params?.comp_id) queryParams.append('comp_id', params.comp_id);
    if (params?.date) queryParams.append('date', params.date);
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    if (params?.team_id) queryParams.append('team_id', params.team_id);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    
    const url = `${API_BASE_URL}/leaderboard/individual${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    const response = await fetch(url, {
      headers,
    });
    return this.handleResponse(response);
  }

  async getTeamLeaderboard(params?: {
    comp_id?: string;
    date?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<LeaderboardResponse> {
    const headers = await this.getAuthHeaders();
    const queryParams = new URLSearchParams();
    if (params?.comp_id) queryParams.append('comp_id', params.comp_id);
    if (params?.date) queryParams.append('date', params.date);
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    
    const url = `${API_BASE_URL}/leaderboard/team${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    const response = await fetch(url, {
      headers,
    });
    return this.handleResponse(response);
  }
}

export const apiClient = new ApiClient();
