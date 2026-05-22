import { useEffect, useState } from 'react';
import { api } from '../../services/api';

function Reports() {
  const [report, setReport] = useState(null);

  useEffect(() => {
    api.reportsDaily().then((r) => setReport(r.data));
  }, []);

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Reports</h2>
      <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
        {report ? (
          <>
            <p className="text-sm text-slate-400">Period: {report.period}</p>
            <p className="mt-3">Completed: {report.statistics?.completed_plans || 0}</p>
            <p>Failed: {report.statistics?.failed_plans || 0}</p>
            <p>Score: {report.statistics?.total_score || 0}</p>
          </>
        ) : (
          <p className="text-slate-400">Report is loading...</p>
        )}
      </div>
    </section>
  );
}

export default Reports;
