import { useCallback, useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import client from '../api/client'
import type { Application, ChecklistItem } from '../api/types'
import StatusBadge from '../components/StatusBadge'
import SlaBadge from '../components/SlaBadge'
import { formatDate } from '../utils/date'
import { useAuth } from '../context/AuthContext'

function ChecklistRow({
  item,
  application,
  onChanged,
}: {
  item: ChecklistItem
  application: Application
  onChanged: () => void
}) {
  const { user } = useAuth()
  const [file, setFile] = useState<File | null>(null)
  const [remarks, setRemarks] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const resolved = item.status === 'approved' || item.status === 'rejected'
  const canUpload = user?.role === 'entrepreneur' && application.applicant_id === user.id && !resolved
  const canReview =
    (user?.role === 'admin' || (user?.role === 'officer' && user.department === item.department)) && !resolved

  const upload = async () => {
    if (!file) return
    setBusy(true)
    setError(null)
    const form = new FormData()
    form.append('file', file)
    try {
      await client.post(`/applications/${application.id}/checklist/${item.id}/document`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setFile(null)
      onChanged()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Upload failed.')
    } finally {
      setBusy(false)
    }
  }

  const review = async (action: 'approve' | 'reject') => {
    setBusy(true)
    setError(null)
    try {
      await client.post(`/applications/${application.id}/checklist/${item.id}/review`, { action, remarks })
      onChanged()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Action failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <tr className="border-t border-slate-100 align-top">
      <td className="px-5 py-4">
        <p className="font-medium text-slate-700">
          {item.approval_name}
          {!item.mandatory && (
            <span className="ml-2 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-500">
              Optional
            </span>
          )}
        </p>
        <p className="text-xs text-slate-400">{item.clause_ref}</p>
      </td>
      <td className="px-5 py-4 text-sm text-slate-600">{item.department}</td>
      <td className="px-5 py-4">
        <SlaBadge dueAt={item.due_at} resolved={resolved} />
      </td>
      <td className="px-5 py-4">
        <StatusBadge status={item.status} />
        {item.remarks && <p className="mt-1 max-w-[16rem] text-xs text-slate-400">"{item.remarks}"</p>}
      </td>
      <td className="px-5 py-4 text-xs text-slate-500">
        {item.documents.length === 0 ? (
          <span className="text-slate-300">No documents</span>
        ) : (
          <ul className="space-y-1">
            {item.documents.map((d) => (
              <li key={d.id}>📎 {d.original_filename}</li>
            ))}
          </ul>
        )}
      </td>
      <td className="px-5 py-4">
        {canUpload && (
          <div className="flex flex-col gap-2">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="text-xs text-slate-500 file:mr-2 file:rounded-md file:border-0 file:bg-brand-50 file:px-2 file:py-1 file:text-xs file:font-medium file:text-brand-700"
            />
            <button
              onClick={upload}
              disabled={!file || busy}
              className="rounded-md bg-brand-700 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-brand-800 disabled:opacity-50"
            >
              {busy ? 'Uploading…' : 'Upload'}
            </button>
          </div>
        )}
        {canReview && (
          <div className="flex flex-col gap-2">
            <textarea
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Remarks (optional)"
              rows={2}
              className="w-40 rounded-md border border-slate-200 px-2 py-1 text-xs focus:border-brand-500 focus:outline-none"
            />
            <div className="flex gap-2">
              <button
                onClick={() => review('approve')}
                disabled={busy}
                className="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
              >
                Approve
              </button>
              <button
                onClick={() => review('reject')}
                disabled={busy}
                className="rounded-md bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-rose-700 disabled:opacity-50"
              >
                Reject
              </button>
            </div>
          </div>
        )}
        {error && <p className="mt-1 text-xs text-rose-600">{error}</p>}
        {resolved && !canUpload && !canReview && <span className="text-xs text-slate-300">—</span>}
      </td>
    </tr>
  )
}

export default function ApplicationDetailPage() {
  const { id } = useParams()
  const [application, setApplication] = useState<Application | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    client
      .get<Application>(`/applications/${id}`)
      .then(({ data }) => setApplication(data))
      .catch((err) => setError(err?.response?.data?.detail ?? 'Could not load application.'))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  if (loading) return <p className="text-sm text-slate-400">Loading…</p>
  if (error) return <p className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-600">{error}</p>
  if (!application) return null

  const approvedCount = application.checklist_items.filter((i) => i.status === 'approved').length

  return (
    <div className="space-y-6">
      <Link to="/dashboard" className="text-sm text-brand-700 hover:underline">
        ← Back to dashboard
      </Link>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-800">{application.project_name}</h1>
            <p className="mt-1 text-sm text-slate-500">
              {application.sector} · {application.location} · {application.size} · {application.stage} stage
            </p>
            {application.applicant_name && (
              <p className="mt-1 text-xs text-slate-400">
                Filed by {application.applicant_name} ({application.applicant_email}) on{' '}
                {formatDate(application.created_at)}
              </p>
            )}
          </div>
          <div className="text-right">
            <StatusBadge status={application.status} />
            <p className="mt-2 text-xs text-slate-400">
              {approvedCount} / {application.checklist_items.length} approvals cleared
            </p>
          </div>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-5 py-3">Approval</th>
              <th className="px-5 py-3">Department</th>
              <th className="px-5 py-3">SLA</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3">Documents</th>
              <th className="px-5 py-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {application.checklist_items.map((item) => (
              <ChecklistRow key={item.id} item={item} application={application} onChanged={load} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
