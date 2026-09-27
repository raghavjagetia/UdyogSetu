export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

export interface SlaInfo {
  label: string
  overdue: boolean
  daysLeft: number
}

export function slaInfo(dueIso: string): SlaInfo {
  const due = new Date(dueIso).getTime()
  const now = Date.now()
  const diffDays = Math.ceil((due - now) / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return { label: `${Math.abs(diffDays)}d overdue`, overdue: true, daysLeft: diffDays }
  }
  if (diffDays === 0) {
    return { label: 'Due today', overdue: false, daysLeft: 0 }
  }
  return { label: `${diffDays}d left`, overdue: false, daysLeft: diffDays }
}
