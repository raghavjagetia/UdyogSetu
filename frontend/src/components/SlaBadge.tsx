import { slaInfo } from '../utils/date'

export default function SlaBadge({ dueAt, resolved }: { dueAt: string; resolved: boolean }) {
  if (resolved) {
    return <span className="text-xs text-slate-400">—</span>
  }

  const { label, overdue } = slaInfo(dueAt)
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${
        overdue ? 'bg-rose-50 text-rose-700 ring-rose-300' : 'bg-brand-50 text-brand-700 ring-brand-300'
      }`}
    >
      {overdue && '⚠ '}
      {label}
    </span>
  )
}
