import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../../api/client'
import type { Application, RulesMeta } from '../../api/types'

export default function NewApplicationPage() {
  const [meta, setMeta] = useState<RulesMeta | null>(null)
  const [projectName, setProjectName] = useState('')
  const [sector, setSector] = useState('')
  const [location, setLocation] = useState('')
  const [size, setSize] = useState('Micro')
  const [stage, setStage] = useState('New')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    client.get<RulesMeta>('/rules/meta').then(({ data }) => {
      setMeta(data)
      setSector(data.sectors[0])
      setLocation(data.locations[0])
    })
  }, [])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const { data } = await client.post<Application>('/applications', {
        project_name: projectName,
        sector,
        location,
        size,
        stage,
      })
      navigate(`/applications/${data.id}`)
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Could not create application.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold text-slate-800">New Application</h1>
      <p className="mt-1 text-sm text-slate-500">
        Tell us about your project and UdyogSetu will auto-generate your approvals checklist.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <label className="text-sm font-medium text-slate-600">Project name</label>
          <input
            required
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="e.g. Shree Foods Processing Unit"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-slate-600">Sector</label>
            <select
              value={sector}
              onChange={(e) => setSector(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            >
              {meta?.sectors.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Location</label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            >
              {meta?.locations.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-slate-600">Unit size</label>
            <select
              value={size}
              onChange={(e) => setSize(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            >
              {meta?.sizes.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Stage</label>
            <select
              value={stage}
              onChange={(e) => setStage(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            >
              <option value="New">New</option>
              <option value="Expansion">Expansion</option>
              <option value="Existing">Existing</option>
            </select>
          </div>
        </div>

        {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting || !meta}
          className="w-full rounded-lg bg-brand-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-800 disabled:opacity-60"
        >
          {submitting ? 'Generating checklist…' : 'Generate Approvals Checklist'}
        </button>
      </form>
    </div>
  )
}
