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
