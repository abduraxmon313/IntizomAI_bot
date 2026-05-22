import { useEffect, useState } from 'react';
import { api } from '../../services/api';

function Plans() {
  const [plans, setPlans] = useState([]);

  useEffect(() => {
    api.plansHistory().then((r) => setPlans(r.data.items || []));
  }, []);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Plans history</h2>
      <div className="space-y-2">
        {plans.length ? plans.map((plan) => (
          <article key={plan.id} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
            <p className="font-medium">{plan.title}</p>
            <p className="text-xs text-slate-400">{plan.plan_date} • {plan.status}</p>
          </article>
        )) : <p className="text-slate-400">No historical plans found.</p>}
      </div>
    </section>
  );
}

export default Plans;
