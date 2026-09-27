import { useAuth } from '../context/AuthContext'
import EntrepreneurDashboard from './entrepreneur/EntrepreneurDashboard'
import OfficerDashboard from './officer/OfficerDashboard'
import AdminDashboard from './admin/AdminDashboard'

export default function DashboardPage() {
  const { user } = useAuth()

  if (user?.role === 'officer') return <OfficerDashboard />
  if (user?.role === 'admin') return <AdminDashboard />
  return <EntrepreneurDashboard />
}
