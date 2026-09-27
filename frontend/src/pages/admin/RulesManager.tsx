import { useEffect, useState, type FormEvent } from 'react'
import client from '../../api/client'
import type { Rule, RulesMeta } from '../../api/types'

const EMPTY_FORM = {
  sector: 'All',
  location: 'All',
  min_size: 'Micro',
  approval_name: '',
  department: '',
  clause_ref: '',
  sla_days: 15,
  mandatory: true,
  active: true,
}

export default function RulesManager() {
  const [rules, setRules] = useState<Rule[]>([])
  const [meta, setMeta] = useState<RulesMeta | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    Promise.all([client.get<Rule[]>('/rules'), client.get<RulesMeta>('/rules/meta')]).then(([r, m]) => {
      setRules(r.data)
      setMeta(m.data)
      setLoading(false)
    })
  }

  useEffect(load, [])

  const startEdit = (rule: Rule) => {
    setEditingId(rule.id)
    setForm({
      sector: rule.sector,
      location: rule.location,
      min_size: rule.min_size,
      approval_name: rule.approval_name,
      department: rule.department,
      clause_ref: rule.clause_ref,
      sla_days: rule.sla_days,
      mandatory: rule.mandatory,
      active: rule.active,
    })
  }

  const resetForm = () => {
    setEditingId(null)
    setForm(EMPTY_FORM)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      if (editingId) {
        await client.put(`/rules/${editingId}`, form)
      } else {
        await client.post('/rules', form)
      }
      resetForm()
      load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Could not save rule.')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this rule? Existing applications keep their generated checklist items.')) return
    await client.delete(`/rules/${id}`)
    load()
  }

  const toggleActive = async (rule: Rule) => {
    await client.put(`/rules/${rule.id}`, { active: !rule.active })
    load()
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-800">Rules Engine</h1>
        <p className="mt-1 text-sm text-slate-500">
          Rules-as-code: every entry here is matched against sector, location and unit size to build an
          applicant's checklist automatically.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-3">
        <div>
          <label className="text-xs font-medium text-slate-500">Sector</label>
          <select
            value={form.sector}
            onChange={(e) => setForm({ ...form, sector: e.target.value })}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option value="All">All sectors</option>
            {meta?.sectors.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">Location</label>
          <select
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option value="All">All locations</option>
            {meta?.locations.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">Applies from size</label>
          <select
            value={form.min_size}
            onChange={(e) => setForm({ ...form, min_size: e.target.value })}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            {meta?.sizes.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs font-medium text-slate-500">Approval name</label>
          <input
            required
            value={form.approval_name}
            onChange={(e) => setForm({ ...form, approval_name: e.target.value })}
            placeholder="e.g. Consent to Establish"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">Department</label>
          <input
            required
            value={form.department}
            onChange={(e) => setForm({ ...form, department: e.target.value })}
            placeholder="e.g. Maharashtra Pollution Control Board"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">SLA (days)</label>
          <input
            required
            type="number"
            min={1}
            value={form.sla_days}
            onChange={(e) => setForm({ ...form, sla_days: Number(e.target.value) })}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>

        <div className="md:col-span-2">
          <label className="text-xs font-medium text-slate-500">Clause / legal reference</label>
          <input
            required
            value={form.clause_ref}
            onChange={(e) => setForm({ ...form, clause_ref: e.target.value })}
            placeholder="e.g. Factories Act, 1948 - Sec 6"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>

        <div className="flex items-end gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={form.mandatory}
              onChange={(e) => setForm({ ...form, mandatory: e.target.checked })}
            />
            Mandatory
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={form.active}
              onChange={(e) => setForm({ ...form, active: e.target.checked })}
            />
            Active
          </label>
        </div>

        {error && <p className="md:col-span-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600">{error}</p>}

        <div className="flex gap-2 md:col-span-3">
          <button type="submit" className="rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-800">
            {editingId ? 'Update Rule' : 'Add Rule'}
          </button>
          {editingId && (
            <button type="button" onClick={resetForm} className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600">
              Cancel edit
            </button>
          )}
        </div>
      </form>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        {loading ? (
          <p className="p-8 text-center text-sm text-slate-400">Loading rules…</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Approval</th>
                <th className="px-4 py-3">Sector</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Min Size</th>
                <th className="px-4 py-3">Department</th>
                <th className="px-4 py-3">SLA</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rules.map((rule) => (
                <tr key={rule.id} className={!rule.active ? 'opacity-50' : ''}>
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-700">{rule.approval_name}</p>
                    <p className="text-xs text-slate-400">{rule.clause_ref}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{rule.sector}</td>
                  <td className="px-4 py-3 text-slate-600">{rule.location}</td>
                  <td className="px-4 py-3 text-slate-600">{rule.min_size}+</td>
                  <td className="px-4 py-3 text-slate-600">{rule.department}</td>
                  <td className="px-4 py-3 text-slate-600">{rule.sla_days}d</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggleActive(rule)}
                      className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                        rule.active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'
                      }`}
                    >
                      {rule.active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2 text-xs">
                      <button onClick={() => startEdit(rule)} className="font-medium text-brand-700 hover:underline">
                        Edit
                      </button>
                      <button onClick={() => handleDelete(rule.id)} className="font-medium text-rose-600 hover:underline">
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
