import axios from 'axios';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
});

export function setAuthToken(token) {
  if (token) {
    client.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete client.defaults.headers.common.Authorization;
  }
}

export const api = {
  login: (init_data) => client.post('/auth/login', { init_data }),
  profile: () => client.get('/user/profile'),
  todayPlans: () => client.get('/plans/today'),
  plansHistory: () => client.get('/plans/history'),
  createPlan: (payload) => client.post('/plans/create', payload),
  dailyStats: () => client.get('/statistics/daily'),
  weeklyStats: () => client.get('/statistics/weekly'),
  monthlyStats: () => client.get('/statistics/monthly'),
  yearlyStats: () => client.get('/statistics/yearly'),
  goalsList: () => client.get('/goals/list'),
  goalsProgress: () => client.get('/goals/progress'),
  createGoal: (payload) => client.post('/goals/create', payload),
  reportsDaily: () => client.get('/reports/daily'),
};
