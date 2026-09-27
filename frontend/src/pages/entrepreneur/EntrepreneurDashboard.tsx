import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../../api/client'
import type { Application, DashboardStats } from '../../api/types'
import StatCard from '../../components/StatCard'
import StatusBadge from '../../components/StatusBadge'
import SlaBadge from '../../components/SlaBadge'
import { formatDate } from '../../utils/date'

function nextDueItem(app: Application) {
  const open = app.checklist_items.filter((i) => i.status !== 'approved' && i.status !== 'rejected')
  if (open.length === 0) return null
  return open.sort((a, b) => new Date(a.due_at).getTime() - new Date(b.due_at).getTime())[0]
}

export default function EntrepreneurDashboard() {
  const [applications, setApplications] = useState<Application[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([client.get<Application[]>('/applications'), client.get<DashboardStats>('/dashboard/stats')])
      .then(([apps, s]) => {
        setApplications(apps.data)
        setStats(s.data)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">My Applications</h1>
          <p className="mt-1 text-sm text-slate-500">Track approvals across every department in one place.</p>
        </div>
        <Link
          to="/applications/new"
          className="rounded-lg bg-accent-500 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-accent-600"
        >
          + New Application
        </Link>
      </div>

      {stats && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard label="Total Applications" value={stats.total_applications} accent="brand" />
          <StatCard label="Approved" value={stats.approved} accent="emerald" />
          <StatCard label="In Progress" value={stats.in_progress} accent="amber" />
          <StatCard label="Overdue Items" value={stats.overdue_items} accent="rose" />
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        {loading ? (
          <p className="p-8 text-center text-sm text-slate-400">Loading applications…</p>
        ) : applications.length === 0 ? (
          <div className="p-10 text-center">
            <p className="text-sm text-slate-500">You haven't filed any applications yet.</p>
            <Link to="/applications/new" className="mt-3 inline-block text-sm font-medium text-brand-700 hover:underline">
              Start your first application →
            </Link>
          </div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-5 py-3">Project</th>
                <th className="px-5 py-3">Sector / Location</th>
                <th className="px-5 py-3">Checklist</th>
                <th className="px-5 py-3">Next Due</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Filed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {applications.map((app) => {
                const due = nextDueItem(app)
                const approvedCount = app.checklist_items.filter((i) => i.status === 'approved').length
                return (
                  <tr key={app.id} className="transition hover:bg-brand-50/40">
                    <td className="px-5 py-4">
                      <Link to={`/applications/${app.id}`} className="font-medium text-brand-700 hover:underline">
                        {app.project_name}
                      </Link>
                      <p className="text-xs text-slate-400">{app.size} · {app.stage}</p>
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {app.sector}
                      <p className="text-xs text-slate-400">{app.location}</p>
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {approvedCount} / {app.checklist_items.length} cleared
                    </td>
                    <td className="px-5 py-4">
                      {due ? (
                        <div>
                          <p className="text-xs text-slate-500">{due.approval_name}</p>
                          <SlaBadge dueAt={due.due_at} resolved={false} />
                        </div>
                      ) : (
                        <span className="text-xs text-slate-400">All cleared</span>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={app.status} />
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-400">{formatDate(app.created_at)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
