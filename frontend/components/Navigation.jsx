import { BarChart3, Gauge, Goal, ListTodo, Settings, Sheet } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: Gauge },
  { to: '/statistics', label: 'Statistics', icon: BarChart3 },
  { to: '/goals', label: 'Goals', icon: Goal },
  { to: '/plans', label: 'Plans', icon: ListTodo },
  { to: '/reports', label: 'Reports', icon: Sheet },
  { to: '/settings', label: 'Settings', icon: Settings },
];

function Navigation() {
  return (
    <aside className="hidden w-60 shrink-0 rounded-2xl border border-slate-800/70 bg-slate-900/60 p-3 lg:block">
      <nav className="space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-xl px-3 py-2 text-sm transition ${
                isActive ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-300 hover:bg-slate-800/70'
              }`
            }
          >
            <Icon size={16} /> {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Navigation;
