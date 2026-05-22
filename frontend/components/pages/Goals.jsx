import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import ProgressBar from '../common/ProgressBar';

function Goals() {
  const [goals, setGoals] = useState([]);

  useEffect(() => {
    api.goalsList().then((r) => setGoals(r.data.items || []));
  }, []);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Goals</h2>
      <div className="space-y-3">
        {goals.length ? goals.map((goal) => (
          <div key={goal.id} className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="font-medium">{goal.title}</p>
            <p className="text-xs text-slate-400">{goal.goal_type}</p>
            <div className="mt-3"><ProgressBar value={goal.progress} /></div>
            <p className="mt-2 text-xs text-slate-400">{goal.current_value}/{goal.target_value} ({goal.progress}%)</p>
          </div>
        )) : <p className="text-slate-400">No goals yet.</p>}
      </div>
    </section>
  );
}

export default Goals;
