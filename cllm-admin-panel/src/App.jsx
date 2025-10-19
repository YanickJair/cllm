import { Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from './components/layout/AdminLayout';

// Pages
import Dashboard from './pages/Dashboard';
import NBA from './pages/NBA';
import CLLM from './pages/CLLM';
import SystemPrompts from './pages/SystemPrompts';
import Vocabulary from './pages/Vocabulary';
import Settings from './pages/Settings';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Main admin routes with layout */}
        <Route path="/" element={<AdminLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="nba/*" element={<NBA />} />
          <Route path="cllm" element={<CLLM />} />
          <Route path="prompts/*" element={<SystemPrompts />} />
          <Route path="vocabulary" element={<Vocabulary />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* 404 fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
}

export default App;