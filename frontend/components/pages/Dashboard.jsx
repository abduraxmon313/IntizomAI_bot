import useStore from '../../store/useStore';

function Dashboard() {
  const { stats, plans, loading } = useStore();

  const cards = [
    ['Daily plans', stats?.total_plans || 0],
    ['Completed', stats?.completed_plans || 0],
    ['Success', `${stats?.success_rate || 0}%`],
    ['Score', stats?.total_score || 0],
  ];

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Dashboard</h2>
      {loading && <p className="text-slate-400">Loading...</p>}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map(([label, value]) => (
          <div key={label} className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="text-xs text-slate-400">{label}</p>
            <p className="mt-2 text-2xl font-semibold">{value}</p>
          </div>
        ))}
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
        <h3 className="text-lg font-medium">Today plans</h3>
        <ul className="mt-3 space-y-2">
          {plans.length ? plans.map((plan) => (
            <li key={plan.id} className="rounded-lg border border-slate-800 px-3 py-2">
              <p className="font-medium">{plan.title}</p>
              <p className="text-xs text-slate-400">{plan.scheduled_time || 'No time'} • {plan.status}</p>
            </li>
          )) : <li className="text-sm text-slate-400">No plans yet.</li>}
        </ul>
      </div>
    </section>
  );
}

export default Dashboard;
