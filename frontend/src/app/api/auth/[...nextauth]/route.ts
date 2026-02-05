import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// @ts-ignore - NextAuth types issue
const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
        },
      },
    }),
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const res = await fetch(`${API_URL}/api/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({
            username: credentials?.email || "",
            password: credentials?.password || "",
          }),
        });

        if (!res.ok) return null;

        const data = await res.json();
        return {
          id: String(data.user.id),
          email: data.user.email,
          name: data.user.full_name,
          // @ts-ignore
          backendToken: data.access_token,
        };
      },
    }),
  ],
  pages: {
    signIn: "/auth",
  },
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async signIn({ user, account, profile }: any) {
      if (account?.provider === "google") {
        try {
          const res = await fetch(`${API_URL}/api/auth/oauth`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              provider: "google",
              id_token: account.id_token,
              access_token: account.access_token,
            }),
          });

          if (!res.ok) {
            console.error("Backend OAuth error:", await res.text());
            return false;
          }

          const data = await res.json();
          // @ts-ignore
          user.backendToken = data.access_token;
          user.id = String(data.user.id);
          return true;
        } catch (error) {
          console.error("OAuth backend error:", error);
          return false;
        }
      }
      return true;
    },
    async jwt({ token, user, account }: any) {
      if (user?.backendToken) {
        token.backendToken = user.backendToken;
      }
      return token;
    },
    async session({ session, token }: any) {
      session.backendToken = token.backendToken;
      return session;
    },
  },
});

export { handler as GET, handler as POST };
