import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import DataQuality from './pages/DataQuality';
import CoachDashboard from './pages/CoachDashboard';
import ScoutDashboard from './pages/ScoutDashboard';
import AnalystDashboard from './pages/AnalystDashboard';
import Players from './pages/Players';
import AIChat from './pages/AIChat';
import './App.css';

const navItems = [
  { section: 'Overview' },
  { path: '/data-quality', icon: '📊', label: 'Data Quality & EDA' },
  { path: '/players', icon: '👥', label: 'Player Database' },
  { section: 'Dashboards' },
  { path: '/coach', icon: '🧑‍🏫', label: 'Coach Dashboard' },
  { path: '/scout', icon: '🔍', label: 'Scout & Manager' },
  { path: '/analyst', icon: '📈', label: 'Match Analyst' },
  { section: 'AI' },
  { path: '/ai-chat', icon: '🤖', label: 'AI Coach Chat' },
];

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <aside className="sidebar">
          <div className="sidebar-logo">
            <h1>⚽ AthleteIQ</h1>
            <p>Performance Analytics</p>
          </div>
          <nav className="sidebar-nav">
            {navItems.map((item, i) =>
              item.section ? (
                <div key={i} className="sidebar-section-title">{item.section}</div>
              ) : (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {item.label}
                </NavLink>
              )
            )}
          </nav>
          <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)', fontSize: 11, color: 'var(--text-muted)' }}>
            <div>Powered by ML & GenAI</div>
            <div style={{ marginTop: 4 }}>11,060 Players · 25,979 Matches</div>
          </div>
        </aside>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/data-quality" replace />} />
            <Route path="/data-quality" element={<DataQuality />} />
            <Route path="/players" element={<Players />} />
            <Route path="/coach" element={<CoachDashboard />} />
            <Route path="/scout" element={<ScoutDashboard />} />
            <Route path="/analyst" element={<AnalystDashboard />} />
            <Route path="/ai-chat" element={<AIChat />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
