import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import { query } from "@/lib/db";
import bcrypt from "bcryptjs";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const authOptions: NextAuthOptions = {
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
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Email e Password richiesti");
        }

        try {
          // Chiamata diretta al backend FastAPI per login
          const formData = new URLSearchParams();
          formData.append("username", credentials.email);
          formData.append("password", credentials.password);

          const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
          });

          if (!res.ok) {
            const error = await res.json().catch(() => ({}));
            throw new Error(error.detail || "Credenziali non valide");
          }

          const data = await res.json();
          
          return {
            id: data.user.id.toString(),
            name: data.user.full_name,
            email: data.user.email,
            image: data.user.avatar_url,
            accessToken: data.access_token,
          };
        } catch (error: any) {
          console.error("Authorize Error:", error.message);
          throw new Error(error.message || "Errore di autenticazione");
        }
      },
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }: any) {
      if (account?.provider === "google") {
        try {
          console.log('[AUTH] Tentativo signIn Google per:', user.email);

          // Prima: sincronizza utente nel nostro DB
          const existingUser = await query(
            'SELECT id FROM users WHERE oauth_id = $1',
            [account.providerAccountId]
          );

          let userId: string;

          if (existingUser.rows.length > 0) {
            console.log('[AUTH] Utente Google trovato');
            userId = existingUser.rows[0].id.toString();
          } else {
            // Check per email
            const existingEmail = await query(
              'SELECT id FROM users WHERE email = $1',
              [user.email]
            );

            if (existingEmail.rows.length > 0) {
              console.log('[AUTH] Utente trovato per EMAIL. Aggiorno OAuth.');
              const dbUser = existingEmail.rows[0];
              await query(
                `UPDATE users SET oauth_provider = $1, oauth_id = $2, avatar_url = COALESCE($3, avatar_url), updated_at = NOW() WHERE id = $4`,
                ['google', account.providerAccountId, user.image, dbUser.id]
              );
              userId = dbUser.id.toString();
            } else {
              // Crea nuovo utente
              console.log('[AUTH] Creazione NUOVO utente Google');
              const newUser = await query(
                `INSERT INTO users (email, full_name, avatar_url, oauth_provider, oauth_id, is_active, is_superuser, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                   RETURNING id`,
                [user.email, user.name, user.image, 'google', account.providerAccountId, true, false]
              );
              userId = newUser.rows[0].id.toString();
            }
          }

          // Ora ottieni il JWT dal backend chiamando l'endpoint OAuth
          const oauthRes = await fetch(`${API_BASE}/api/auth/oauth`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              provider: "google",
              id_token: account.id_token,
            }),
          });

          if (oauthRes.ok) {
            const oauthData = await oauthRes.json();
            user.accessToken = oauthData.access_token;
          }

          user.id = userId;
          return true;

        } catch (error: any) {
          console.error('[AUTH FAIL]', {
            step: 'signIn callback Google',
            error: error.message,
          });
          return false;
        }
      }
      return true;
    },
    async jwt({ token, user, account }: any) {
      // Salva i dati utente nel token JWT
      if (user) {
        token.id = user.id;
        token.accessToken = user.accessToken;
      }
      return token;
    },
    async session({ session, token }: any) {
      // Espone i dati nella sessione client-side
      if (session.user) {
        session.user.id = token.id;
        session.accessToken = token.accessToken;
      }
      return session;
    },
  },
  pages: {
    signIn: '/auth',
    error: '/auth',
  },
  debug: process.env.NODE_ENV === "development",
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
