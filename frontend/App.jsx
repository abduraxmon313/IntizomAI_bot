import { Navigate, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Dashboard from './components/pages/Dashboard';
import Statistics from './components/pages/Statistics';
import Goals from './components/pages/Goals';
import Plans from './components/pages/Plans';
import Reports from './components/pages/Reports';
import Settings from './components/pages/Settings';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      <Header />
      <div className="mx-auto flex w-full max-w-7xl gap-4 p-4 lg:p-6">
        <Navigation />
        <main className="w-full rounded-2xl border border-slate-800/70 bg-slate-900/60 p-4 shadow-2xl backdrop-blur sm:p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/statistics" element={<Statistics />} />
            <Route path="/goals" element={<Goals />} />
            <Route path="/plans" element={<Plans />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
