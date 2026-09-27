const STYLES: Record<string, string> = {
  submitted: 'bg-slate-100 text-slate-700 ring-slate-300',
  under_review: 'bg-amber-50 text-amber-700 ring-amber-300',
  approved: 'bg-emerald-50 text-emerald-700 ring-emerald-300',
  rejected: 'bg-rose-50 text-rose-700 ring-rose-300',
  pending: 'bg-slate-100 text-slate-700 ring-slate-300',
  document_uploaded: 'bg-sky-50 text-sky-700 ring-sky-300',
}

const LABELS: Record<string, string> = {
  submitted: 'Submitted',
  under_review: 'Under Review',
  approved: 'Approved',
  rejected: 'Rejected',
  pending: 'Pending',
  document_uploaded: 'Document Uploaded',
}

export default function StatusBadge({ status }: { status: string }) {
  const style = STYLES[status] ?? 'bg-slate-100 text-slate-700 ring-slate-300'
  const label = LABELS[status] ?? status
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${style}`}>
      {label}
    </span>
  )
}
