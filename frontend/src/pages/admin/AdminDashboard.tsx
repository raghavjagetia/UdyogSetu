import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import client from '../../api/client'
import type { DashboardStats } from '../../api/types'
import StatCard from '../../components/StatCard'

const INK = { primary: '#0b0b0b', secondary: '#52514e', muted: '#898781', grid: '#e1e0d9' }
const STATUS_COLOR: Record<string, string> = {
  submitted: '#2a78d6',
  under_review: '#fab219',
  approved: '#0ca30c',
  rejected: '#d03b3b',
}
const STATUS_LABEL: Record<string, string> = {
  submitted: 'Submitted',
  under_review: 'Under Review',
  approved: 'Approved',
  rejected: 'Rejected',
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client
      .get<DashboardStats>('/dashboard/stats')
      .then(({ data }) => setStats(data))
      .finally(() => setLoading(false))
  }, [])

  const handleExport = async () => {
    const response = await client.get('/dashboard/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = 'udyogsetu_compliance_report.csv'
    link.click()
    window.URL.revokeObjectURL(url)
  }

  if (loading || !stats) return <p className="text-sm text-slate-400">Loading analytics…</p>

  const statusData = stats.by_status.map((s) => ({ ...s, label: STATUS_LABEL[s.status] ?? s.status }))
  const sectorData = [...stats.by_sector].sort((a, b) => b.count - a.count)
  const deptData = [...stats.by_department].sort((a, b) => b.pending - a.pending)

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">Compliance Analytics</h1>
          <p className="mt-1 text-sm text-slate-500">State-wide view across every department and sector.</p>
        </div>
        <div className="flex gap-2">
          <Link to="/rules" className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:border-brand-300 hover:text-brand-700">
            Manage Rules
          </Link>
          <button onClick={handleExport} className="rounded-lg bg-accent-500 px-4 py-2 text-sm font-semibold text-white hover:bg-accent-600">
            Export CSV
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        <StatCard label="Total Applications" value={stats.total_applications} accent="brand" />
        <StatCard label="Approved" value={stats.approved} accent="emerald" />
        <StatCard label="Rejected" value={stats.rejected} accent="rose" />
        <StatCard label="In Progress" value={stats.in_progress} accent="amber" />
        <StatCard label="Overdue Items" value={stats.overdue_items} accent="rose" hint="Across all departments" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-700">Applications by Status</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusData} margin={{ left: -10 }}>
                <CartesianGrid stroke={INK.grid} vertical={false} />
                <XAxis dataKey="label" tick={{ fill: INK.muted, fontSize: 12 }} axisLine={{ stroke: INK.grid }} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fill: INK.muted, fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip
                  cursor={{ fill: '#f4f7f8' }}
                  contentStyle={{ borderRadius: 10, borderColor: INK.grid, fontSize: 12 }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={48}>
                  {statusData.map((entry) => (
                    <Cell key={entry.status} fill={STATUS_COLOR[entry.status] ?? '#2a78d6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-700">Applications by Sector</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectorData} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid stroke={INK.grid} horizontal={false} />
                <XAxis type="number" allowDecimals={false} tick={{ fill: INK.muted, fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis dataKey="sector" type="category" width={140} tick={{ fill: INK.secondary, fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: '#f4f7f8' }} contentStyle={{ borderRadius: 10, borderColor: INK.grid, fontSize: 12 }} />
                <Bar dataKey="count" fill="#2a78d6" radius={[0, 4, 4, 0]} maxBarSize={22} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-700">Department Workload — Pending vs Overdue</h2>
          <div className="flex items-center gap-4 text-xs font-medium text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: '#2a78d6' }} />
              Pending
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: '#d03b3b' }} />
              Overdue
            </span>
          </div>
        </div>
        <div className="mt-4 h-96">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={deptData} margin={{ left: -10, bottom: 90 }}>
              <CartesianGrid stroke={INK.grid} vertical={false} />
              <XAxis
                dataKey="department"
                tick={{ fill: INK.muted, fontSize: 11 }}
                axisLine={{ stroke: INK.grid }}
                tickLine={false}
                interval={0}
                angle={-40}
                textAnchor="end"
                height={110}
              />
              <YAxis allowDecimals={false} tick={{ fill: INK.muted, fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: '#f4f7f8' }} contentStyle={{ borderRadius: 10, borderColor: INK.grid, fontSize: 12 }} />
              <Bar dataKey="pending" name="Pending" fill="#2a78d6" radius={[4, 4, 0, 0]} maxBarSize={28} />
              <Bar dataKey="overdue" name="Overdue" fill="#d03b3b" radius={[4, 4, 0, 0]} maxBarSize={28} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
