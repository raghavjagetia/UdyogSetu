import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import ProtectedLayout from './components/ProtectedLayout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import NewApplicationPage from './pages/entrepreneur/NewApplicationPage'
import ApplicationDetailPage from './pages/ApplicationDetailPage'
import SchemesPage from './pages/SchemesPage'
import RulesManager from './pages/admin/RulesManager'

function RootRedirect() {
  const { isAuthenticated } = useAuth()
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route element={<ProtectedLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/applications/:id" element={<ApplicationDetailPage />} />
            <Route path="/schemes" element={<SchemesPage />} />
          </Route>

          <Route element={<ProtectedLayout roles={['entrepreneur']} />}>
            <Route path="/applications/new" element={<NewApplicationPage />} />
          </Route>

          <Route element={<ProtectedLayout roles={['admin']} />}>
            <Route path="/rules" element={<RulesManager />} />
          </Route>

          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
