import { create } from 'zustand';
import { api, setAuthToken } from '../services/api';

const getInitData = () => {
  if (window?.Telegram?.WebApp?.initData) {
    return window.Telegram.WebApp.initData;
  }
  return localStorage.getItem('initData') || '';
};

const useStore = create((set) => ({
  token: localStorage.getItem('token') || '',
  darkMode: localStorage.getItem('darkMode') !== 'light',
  profile: null,
  stats: null,
  plans: [],
  goals: [],
  loading: false,
  error: '',

  toggleTheme: () =>
    set((state) => {
      const darkMode = !state.darkMode;
      localStorage.setItem('darkMode', darkMode ? 'dark' : 'light');
      document.documentElement.classList.toggle('dark', darkMode);
      return { darkMode };
    }),

  authenticate: async () => {
    const initData = getInitData();
    if (!initData) return;
    set({ loading: true, error: '' });
    try {
      const { data } = await api.login(initData);
      localStorage.setItem('token', data.access_token);
      setAuthToken(data.access_token);
      set({ token: data.access_token, profile: data.user, loading: false });
    } catch (e) {
      set({ error: e?.response?.data?.detail || 'Authentication failed', loading: false });
    }
  },

  bootstrap: async () => {
    const token = localStorage.getItem('token') || '';
    setAuthToken(token);
    set({ token, loading: true, error: '' });
    try {
      const [profile, stats, plans, goals] = await Promise.all([
        api.profile(),
        api.dailyStats(),
        api.todayPlans(),
        api.goalsList(),
      ]);
      set({
        profile: profile.data,
        stats: stats.data,
        plans: plans.data.items || [],
        goals: goals.data.items || [],
        loading: false,
      });
    } catch {
      set({ loading: false });
    }
  },
}));

export default useStore;
