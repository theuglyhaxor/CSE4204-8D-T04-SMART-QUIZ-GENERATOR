import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { auth as authApi, tokens } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => tokens.user());
  // "loading" until we've confirmed a stored token is still valid.
  const [loading, setLoading] = useState(() => Boolean(tokens.access()));

  const signOut = useCallback(async () => {
    const refresh = tokens.refresh();
    if (refresh) {
      // Best-effort blacklist; a failure here must not trap the user in the app.
      try {
        await authApi.logout(refresh);
      } catch {
        /* already expired or offline */
      }
    }
    tokens.clear();
    setUser(null);
  }, []);

  // Revalidate a stored session on boot: a token in localStorage may be expired
  // or blacklisted, and we should not render the app as if it were logged in.
  useEffect(() => {
    if (!tokens.access()) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    authApi
      .me()
      .then((me) => {
        if (cancelled) return;
        tokens.save({ user: me });
        setUser(me);
      })
      .catch(() => {
        if (cancelled) return;
        tokens.clear();
        setUser(null);
      })
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, []);

  // The API client raises this when a refresh fails — drop the session.
  useEffect(() => {
    const onExpired = () => setUser(null);
    window.addEventListener("sqg:session-expired", onExpired);
    return () => window.removeEventListener("sqg:session-expired", onExpired);
  }, []);

  const signIn = useCallback(async (username, password) => {
    const data = await authApi.login(username, password);
    tokens.save(data);
    setUser(data.user);
    return data.user;
  }, []);

  const signUp = useCallback(async (payload) => {
    const data = await authApi.register(payload);
    tokens.save(data);
    setUser(data.user);
    return data.user;
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      signIn,
      signUp,
      signOut,
      isAuthenticated: Boolean(user),
      isTeacher: user?.role === "teacher",
      isStudent: user?.role === "student",
    }),
    [user, loading, signIn, signUp, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside an <AuthProvider>.");
  return context;
}
