import { createContext, useContext, useEffect, useState } from "react";
import { loginUser } from "../api/auth";
import { getCurrentUser } from "../api/users";

const AuthContext = createContext(null);

function getStoredUser() {
  try {
    const stored = localStorage.getItem("kazilink_user");
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("kazilink_token"));
  const [currentUser, setCurrentUser] = useState(() => getStoredUser());
  const [loading, setLoading] = useState(() => Boolean(token));

  useEffect(() => {
    if (!token) {
      localStorage.removeItem("kazilink_user");
      setCurrentUser(null);
      setLoading(false);
      return;
    }

    const storedUser = getStoredUser();
    if (storedUser) {
      setCurrentUser(storedUser);
    }

    setLoading(true);
    const start = Date.now();
    console.debug("Auth: validating current user...");

    let active = true;
    getCurrentUser()
      .then((u) => {
        if (!active) return;
        console.debug("Auth: getCurrentUser success", Date.now() - start);
        setCurrentUser(u);
        localStorage.setItem("kazilink_user", JSON.stringify(u));
      })
      .catch((err) => {
        if (!active) return;
        console.warn("Auth: getCurrentUser failed", err);
        localStorage.removeItem("kazilink_token");
        localStorage.removeItem("kazilink_user");
        setToken(null);
        setCurrentUser(null);
      })
      .finally(() => {
        if (!active) return;
        console.debug("Auth: finished getCurrentUser", Date.now() - start);
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [token]);

  const login = async (email, password) => {
    const t0 = Date.now();
    console.debug("Auth: login start", email);
    const data = await loginUser(email, password);
    console.debug("Auth: login token received", Date.now() - t0);
    localStorage.setItem("kazilink_token", data.access_token);
    setToken(data.access_token);

    try {
      const t1 = Date.now();
      const user = await getCurrentUser();
      console.debug("Auth: fetched user after login", Date.now() - t1);
      localStorage.setItem("kazilink_user", JSON.stringify(user));
      setCurrentUser(user);
      console.debug("Auth: login complete total", Date.now() - t0);
      return user;
    } catch (error) {
      console.warn("Auth: failed to fetch current user after login", error);
      localStorage.removeItem("kazilink_token");
      localStorage.removeItem("kazilink_user");
      setToken(null);
      setCurrentUser(null);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("kazilink_token");
    localStorage.removeItem("kazilink_user");
    setToken(null);
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        currentUser,
        loading,
        isAuthenticated: Boolean(token && currentUser),
        login,
        logout,
        refreshUser: async () => setCurrentUser(await getCurrentUser()),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
