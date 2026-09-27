import { useEffect, useState, type FormEvent } from 'react'
import client from '../api/client'
import type { Scheme } from '../api/types'
import { useAuth } from '../context/AuthContext'

const EMPTY_FORM = { name: '', sector: 'All', description: '', benefits: '', active: true }

export default function SchemesPage() {
  const { user } = useAuth()
  const [schemes, setSchemes] = useState<Scheme[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [error, setError] = useState<string | null>(null)

  const load = () => {
    client.get<Scheme[]>('/schemes').then(({ data }) => {
      setSchemes(data)
      setLoading(false)
    })
  }

  useEffect(load, [])

  const startEdit = (scheme: Scheme) => {
    setEditingId(scheme.id)
    setForm({ name: scheme.name, sector: scheme.sector, description: scheme.description, benefits: scheme.benefits, active: scheme.active })
    setShowForm(true)
  }

  const resetForm = () => {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setShowForm(false)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      if (editingId) {
        await client.put(`/schemes/${editingId}`, form)
      } else {
        await client.post('/schemes', form)
      }
      resetForm()
      load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Could not save scheme.')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this scheme?')) return
    await client.delete(`/schemes/${id}`)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">Government Schemes</h1>
          <p className="mt-1 text-sm text-slate-500">Incentives and support programs relevant to your sector.</p>
        </div>
        {user?.role === 'admin' && (
          <button
            onClick={() => (showForm ? resetForm() : setShowForm(true))}
            className="rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-800"
          >
            {showForm ? 'Close' : '+ Add Scheme'}
          </button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-xs font-medium text-slate-500">Scheme name</label>
              <input
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-500">Sector</label>
              <input
                value={form.sector}
                onChange={(e) => setForm({ ...form, sector: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500">Description</label>
            <textarea
              required
              rows={2}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500">Benefits</label>
            <textarea
              required
              rows={2}
              value={form.benefits}
              onChange={(e) => setForm({ ...form, benefits: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}
          <button type="submit" className="rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-800">
            {editingId ? 'Update Scheme' : 'Save Scheme'}
          </button>
        </form>
      )}

      {loading ? (
        <p className="text-sm text-slate-400">Loading schemes…</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {schemes.map((scheme) => (
            <div key={scheme.id} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700">{scheme.sector}</span>
                  <h3 className="mt-2 text-base font-semibold text-slate-800">{scheme.name}</h3>
                </div>
                {user?.role === 'admin' && (
                  <div className="flex gap-2 text-xs">
                    <button onClick={() => startEdit(scheme)} className="font-medium text-brand-700 hover:underline">Edit</button>
                    <button onClick={() => handleDelete(scheme.id)} className="font-medium text-rose-600 hover:underline">Delete</button>
                  </div>
                )}
              </div>
              <p className="mt-2 text-sm text-slate-500">{scheme.description}</p>
              <p className="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-600">
                <span className="font-medium text-slate-700">Benefits: </span>
                {scheme.benefits}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
