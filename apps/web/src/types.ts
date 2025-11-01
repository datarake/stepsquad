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
