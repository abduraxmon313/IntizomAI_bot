import useStore from '../../store/useStore';

function Settings() {
  const { profile, darkMode, toggleTheme } = useStore();

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Settings</h2>
      <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
        <p className="font-medium">Profile</p>
        <p className="mt-2 text-sm text-slate-400">Name: {profile?.full_name || '-'}</p>
        <p className="text-sm text-slate-400">Username: @{profile?.username || '-'}</p>
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
        <p className="font-medium">Preferences</p>
        <button type="button" onClick={toggleTheme} className="mt-2 rounded-lg border border-slate-700 px-3 py-2 text-sm hover:bg-slate-800">
          Theme: {darkMode ? 'Dark' : 'Light'}
        </button>
      </div>
    </section>
  );
}

export default Settings;
