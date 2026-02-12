"use client";

import { AuthProvider } from "@/lib/auth-context";
import { LanguageContext, useLanguageState } from "@/lib/i18n";

function LanguageProvider({ children }: { children: React.ReactNode }) {
  const value = useLanguageState("it");
  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <LanguageProvider>{children}</LanguageProvider>
    </AuthProvider>
  );
}
