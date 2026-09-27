interface StatCardProps {
  label: string
  value: string | number
  accent?: 'brand' | 'emerald' | 'rose' | 'amber'
  hint?: string
}

const ACCENTS: Record<string, string> = {
  brand: 'text-brand-700 bg-brand-50',
  emerald: 'text-emerald-700 bg-emerald-50',
  rose: 'text-rose-700 bg-rose-50',
  amber: 'text-amber-700 bg-amber-50',
}

export default function StatCard({ label, value, accent = 'brand', hint }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className={`mt-2 inline-flex rounded-lg px-2 py-1 text-3xl font-semibold ${ACCENTS[accent]}`}>{value}</p>
      {hint && <p className="mt-2 text-xs text-slate-400">{hint}</p>}
    </div>
  )
}
