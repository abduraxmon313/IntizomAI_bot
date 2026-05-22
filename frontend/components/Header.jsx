import { Brain, Moon, Sun } from 'lucide-react';
import { useEffect } from 'react';
import useStore from '../store/useStore';

function Header() {
  const { darkMode, toggleTheme, profile, authenticate, bootstrap } = useStore();

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    authenticate().then(bootstrap);
  }, [authenticate, bootstrap, darkMode]);

  return (
    <header className="sticky top-0 z-10 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between p-4 lg:px-6">
        <div className="flex items-center gap-2 text-lg font-semibold">
          <Brain className="text-cyan-400" size={20} /> IntizomAI Second Brain
        </div>
        <div className="flex items-center gap-3 text-sm text-slate-300">
          <span>{profile?.full_name || 'Telegram User'}</span>
          <button onClick={toggleTheme} className="rounded-lg border border-slate-700 p-2 hover:bg-slate-800" type="button">
            {darkMode ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
