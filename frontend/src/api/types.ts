export type Role = 'entrepreneur' | 'officer' | 'admin'

export interface User {
  id: number
  name: string
  email: string
  role: Role
  department: string | null
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export type ChecklistStatus = 'pending' | 'document_uploaded' | 'approved' | 'rejected'
export type ApplicationStatus = 'submitted' | 'under_review' | 'approved' | 'rejected'

export interface DocumentOut {
  id: number
  original_filename: string
  uploaded_at: string
}

export interface ChecklistItem {
  id: number
  application_id: number
  approval_name: string
  department: string
  clause_ref: string
  sla_days: number
  due_at: string
  mandatory: boolean
  status: ChecklistStatus
  remarks: string | null
  reviewed_by: number | null
  reviewed_at: string | null
  documents: DocumentOut[]
}

export interface Application {
  id: number
  applicant_id: number
  project_name: string
  sector: string
  location: string
  size: 'Micro' | 'Small' | 'Medium' | 'Large'
  stage: 'New' | 'Expansion' | 'Existing'
  status: ApplicationStatus
  created_at: string
  updated_at: string
  checklist_items: ChecklistItem[]
  applicant_name?: string
  applicant_email?: string
}

export interface Rule {
  id: number
  sector: string
  location: string
  min_size: string
  approval_name: string
  department: string
  clause_ref: string
  sla_days: number
  mandatory: boolean
  active: boolean
}

export interface Scheme {
  id: number
  name: string
  sector: string
  description: string
  benefits: string
  active: boolean
}

export interface DashboardStats {
  total_applications: number
  approved: number
  rejected: number
  in_progress: number
  overdue_items: number
  avg_turnaround_days: number | null
  by_status: { status: string; count: number }[]
  by_sector: { sector: string; count: number }[]
  by_department: { department: string; pending: number; overdue: number }[]
}

export interface RulesMeta {
  sectors: string[]
  locations: string[]
  sizes: string[]
}
