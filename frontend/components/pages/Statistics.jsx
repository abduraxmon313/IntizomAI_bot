import { useEffect, useMemo, useState } from 'react';
import { api } from '../../services/api';
import { BarChart, Bar, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

function Statistics() {
  const [stats, setStats] = useState({});

  useEffect(() => {
    Promise.all([api.dailyStats(), api.weeklyStats(), api.monthlyStats(), api.yearlyStats()]).then(([d, w, m, y]) => {
      setStats({ daily: d.data, weekly: w.data, monthly: m.data, yearly: y.data });
    });
  }, []);

  const chartData = useMemo(
    () => ['daily', 'weekly', 'monthly', 'yearly'].map((k) => ({
      period: k,
      completed: stats[k]?.completed_plans || 0,
      total: stats[k]?.total_plans || 0,
    })),
    [stats]
  );

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Statistics</h2>
      <div className="h-72 rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="period" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="completed" fill="#06b6d4" radius={6} />
            <Bar dataKey="total" fill="#38bdf8" radius={6} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default Statistics;
