import { createContext, useContext, useState, useCallback } from 'react';

const AuthContext = createContext(null);

export const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('rem_user')); } catch { return null; }
  });

  const login = useCallback(async (email, password) => {
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.non_field_errors?.[0] || 'Credenciais inválidas.');
    }
    const data = await res.json();
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('rem_user', JSON.stringify(data.user));
    setToken(data.access);
    setUser(data.user);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('rem_user');
    setToken(null);
    setUser(null);
  }, []);

  const authFetch = useCallback(async (url, options = {}) => {
    const t = localStorage.getItem('access_token');
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (t) headers['Authorization'] = `Bearer ${t}`;
    let res;
    try {
      res = await fetch(url, { ...options, headers });
    } catch (networkErr) {
      throw new Error('Sem conexão com o servidor. Verifique sua rede.');
    }
    if (res.status === 401) {
      logout();
      window.location.href = '/login';
      return res;
    }
    if (!res.ok && options.method && options.method !== 'GET') {
      const body = await res.json().catch(() => ({}));
      const msg = Object.values(body).flat()[0] || `Erro ${res.status}`;
      throw new Error(String(msg));
    }
    return res;
  }, [logout]);

  return (
    <AuthContext.Provider value={{ token, user, login, logout, authFetch, API: API_BASE }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
