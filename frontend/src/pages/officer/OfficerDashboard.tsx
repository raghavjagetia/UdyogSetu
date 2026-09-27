import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../../api/client'
import type { Application, DashboardStats } from '../../api/types'
import StatCard from '../../components/StatCard'
import StatusBadge from '../../components/StatusBadge'
import SlaBadge from '../../components/SlaBadge'
import { useAuth } from '../../context/AuthContext'

export default function OfficerDashboard() {
  const { user } = useAuth()
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

  const myDeptStats = stats?.by_department.find((d) => d.department === user?.department)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-800">Review Queue</h1>
        <p className="mt-1 text-sm text-slate-500">{user?.department} · applications awaiting your department's action</p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Applications in Queue" value={applications.length} accent="brand" />
        <StatCard label="Pending Items" value={myDeptStats?.pending ?? 0} accent="amber" />
        <StatCard label="Overdue Items" value={myDeptStats?.overdue ?? 0} accent="rose" />
        <StatCard label="Avg. Turnaround" value={stats?.avg_turnaround_days ? `${stats.avg_turnaround_days}d` : '—'} accent="brand" />
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        {loading ? (
          <p className="p-8 text-center text-sm text-slate-400">Loading queue…</p>
        ) : applications.length === 0 ? (
          <p className="p-10 text-center text-sm text-slate-500">No applications require your department's review right now.</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-5 py-3">Project</th>
                <th className="px-5 py-3">Applicant</th>
                <th className="px-5 py-3">Sector / Location</th>
                <th className="px-5 py-3">Your Approval</th>
                <th className="px-5 py-3">SLA</th>
                <th className="px-5 py-3">Application Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {applications.map((app) => {
                const myItem = app.checklist_items.find((i) => i.department === user?.department)
                return (
                  <tr key={app.id} className="transition hover:bg-brand-50/40">
                    <td className="px-5 py-4">
                      <Link to={`/applications/${app.id}`} className="font-medium text-brand-700 hover:underline">
                        {app.project_name}
                      </Link>
                    </td>
                    <td className="px-5 py-4 text-slate-600">{app.applicant_name}</td>
                    <td className="px-5 py-4 text-slate-600">
                      {app.sector}
                      <p className="text-xs text-slate-400">{app.location}</p>
                    </td>
                    <td className="px-5 py-4">{myItem && <StatusBadge status={myItem.status} />}</td>
                    <td className="px-5 py-4">
                      {myItem && <SlaBadge dueAt={myItem.due_at} resolved={myItem.status === 'approved' || myItem.status === 'rejected'} />}
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={app.status} />
                    </td>
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
