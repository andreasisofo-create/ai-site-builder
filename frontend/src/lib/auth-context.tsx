"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

// Usa path relativi per sfruttare il proxy Next.js -> Backend
// In sviluppo: localhost:3000/api -> localhost:8000/api
// In produzione: vercel.app/api -> render.com/api
const API_BASE = "";  // Path relativi, es: "/api/auth/login"

export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (email: string, password: string, fullName: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  googleLogin: () => void;
  microsoftLogin: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Load token from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    const userStr = localStorage.getItem("user");

    if (token && userStr) {
      try {
        setState({
          token,
          user: JSON.parse(userStr),
          isLoading: false,
          isAuthenticated: true,
        });
      } catch {
        // user JSON corrotto, prova a recuperare dal backend
        fetchUser(token).then((user) => {
          if (user) {
            localStorage.setItem("user", JSON.stringify(user));
            setState({ token, user, isLoading: false, isAuthenticated: true });
          } else {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            setState((prev) => ({ ...prev, isLoading: false }));
          }
        });
      }
    } else if (token) {
      // Token presente ma user mancante - prova a recuperare
      fetchUser(token).then((user) => {
        if (user) {
          localStorage.setItem("user", JSON.stringify(user));
          setState({ token, user, isLoading: false, isAuthenticated: true });
        } else {
          localStorage.removeItem("token");
          setState((prev) => ({ ...prev, isLoading: false }));
        }
      });
    } else {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  }, []);

  // Fetch user data with token
  const fetchUser = useCallback(async (token: string): Promise<User | null> => {
    try {
      const res = await fetch(`/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) return null;
      return await res.json();
    } catch (error) {
      console.error("Error fetching user:", error);
      return null;
    }
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await fetch(`/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        return { success: false, error: error.detail || "Credenziali non valide" };
      }

      const data = await res.json();
      const { access_token, user } = data;

      // Save to localStorage
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      setState({
        token: access_token,
        user,
        isLoading: false,
        isAuthenticated: true,
      });

      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message || "Errore di connessione" };
    }
  };

  const register = async (email: string, password: string, fullName: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const res = await fetch(`/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });

      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        return { success: false, error: error.detail || "Errore durante la registrazione" };
      }

      // Auto login after registration
      return await login(email, password);
    } catch (error: any) {
      return { success: false, error: error.message || "Errore di connessione" };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setState({
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,
    });
    window.location.href = "/auth";
  };

  const googleLogin = () => {
    const backendUrl = "https://ai-site-builder-jz2g.onrender.com";
    window.location.href = `${backendUrl}/api/auth/oauth/google?redirect_to=${encodeURIComponent(window.location.origin + "/auth/callback")}`;
  };

  const microsoftLogin = () => {
    const backendUrl = "https://ai-site-builder-jz2g.onrender.com";
    window.location.href = `${backendUrl}/api/auth/oauth/microsoft?redirect_to=${encodeURIComponent(window.location.origin + "/auth/callback")}`;
  };

  const refreshUser = async () => {
    if (!state.token) return;

    const user = await fetchUser(state.token);
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
      setState((prev) => ({ ...prev, user }));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        googleLogin,
        microsoftLogin,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

// Hook for protected routes
export function useRequireAuth(redirectUrl = "/auth") {
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      window.location.href = redirectUrl;
    }
  }, [isLoading, isAuthenticated, redirectUrl]);

  return { isLoading, isAuthenticated };
}
