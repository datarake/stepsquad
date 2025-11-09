export type Role = "ADMIN" | "MEMBER";

export type Status = "DRAFT" | "REGISTRATION" | "ACTIVE" | "ENDED" | "ARCHIVED";

export interface Competition {
  comp_id: string;
  name: string;
  status: Status;
  tz: string; // e.g., "Europe/Bucharest"
  registration_open_date: string; // YYYY-MM-DD
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
  max_teams: number;
  max_members_per_team: number;
  created_by: string;
  created_at: string; // ISO
  updated_at: string; // ISO
}

export interface User {
  uid: string;
  email: string;
  role: Role;
}

export interface ApiError {
  detail: string;
}

export interface CompetitionCreateRequest {
  comp_id: string;
  name: string;
  tz: string;
  registration_open_date: string;
  start_date: string;
  end_date: string;
  max_teams: number;
  max_members_per_team: number;
  status?: Status;
}

export interface CompetitionUpdateRequest {
  name?: string;
  tz?: string;
  registration_open_date?: string;
  start_date?: string;
  end_date?: string;
  max_teams?: number;
  max_members_per_team?: number;
  status?: Status;
}

export interface Team {
  team_id: string;
  name: string;
  comp_id: string;
  owner_uid: string;
  members: string[];
}

export interface TeamCreateRequest {
  name: string;
  comp_id: string;
  owner_uid: string;
}

export interface TeamJoinRequest {
  team_id: string;
  uid: string;
}

export interface StepIngestRequest {
  comp_id: string;
  date: string; // YYYY-MM-DD
  steps: number;
  provider?: string; // e.g., "manual", "garmin", "fitbit", "healthkit"
  tz?: string;
  source_ts?: string; // ISO8601
  idempotency_key?: string;
}

export interface StepEntry {
  user_id: string;
  date: string;
  steps: number;
}

export interface StepHistoryResponse {
  rows: StepEntry[];
}

export interface StepIngestResponse {
  status: string;
  stored: boolean;
  user_id: string;
  comp_id: string;
  date: string;
  steps: number;
}

export interface LeaderboardEntry {
  user_id?: string;
  team_id?: string;
  email?: string;
  name?: string;
  steps: number;
  rank: number;
  member_count?: number;
  comp_id?: string;
}

export interface LeaderboardResponse {
  rows: LeaderboardEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Device Integration Types
export interface Device {
  provider: "garmin" | "fitbit" | "virtual";
  linked_at: string;
  last_sync: string | null;
  sync_enabled: boolean;
}

export interface DeviceListResponse {
  devices: Device[];
  count: number;
}

export interface OAuthAuthorizeResponse {
  authorization_url: string;
  state: string;
  provider: "garmin" | "fitbit" | "virtual";
}

export interface OAuthCallbackResponse {
  status: "success" | "error";
  provider: "garmin" | "fitbit" | "virtual";
  message: string;
}

export interface DeviceSyncResponse {
  status: "success" | "error";
  provider: "garmin" | "fitbit" | "virtual";
  date: string;
  steps: number;
  competitions: Array<{
    comp_id: string;
    status: "submitted" | "error" | "skipped";
    steps?: number;
    error?: string;
    reason?: string;
  }>;
  submitted_count: number;
  message: string;
}

export interface DeviceUnlinkResponse {
  status: "success" | "error";
  provider: "garmin" | "fitbit" | "virtual";
  message: string;
}

export interface VirtualDeviceSyncRequest {
  steps: number;
  date?: string;
}
