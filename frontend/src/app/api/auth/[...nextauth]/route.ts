import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials"; // Added
import { query } from "@/lib/db";
import bcrypt from "bcryptjs"; // Added

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
    // Added CredentialsProvider
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
          // Check if user exists
          const result = await query(
            "SELECT * FROM users WHERE email = $1",
            [credentials.email]
          );

          if (result.rows.length === 0) {
            throw new Error("Nessun utente trovato con questa email");
          }

          const user = result.rows[0];

          // If user exists but only has OAuth (no password hash)
          if (!user.hashed_password) {
            throw new Error("Account creato con Google. Usa il login con Google.");
          }

          // Check password
          const isValid = await bcrypt.compare(
            credentials.password,
            user.hashed_password
          );

          if (!isValid) {
            throw new Error("Password non corretta");
          }

          return {
            id: user.id.toString(),
            name: user.full_name,
            email: user.email,
            image: user.avatar_url,
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
          console.log('[AUTH] Tentativo signIn per:', user.email);

          // Prima logica: Check esistenza per oauth_id
          const existingUser = await query(
            'SELECT id FROM users WHERE oauth_id = $1',
            [account.providerAccountId]
          );

          if (existingUser.rows.length > 0) {
            console.log('[AUTH] Utente trovato per OAUTH_ID');
            user.id = existingUser.rows[0].id.toString();
            return true;
          }

          // Seconda logica: Check esistenza per email
          const existingEmail = await query(
            'SELECT id FROM users WHERE email = $1',
            [user.email]
          );

          if (existingEmail.rows.length > 0) {
            console.log('[AUTH] Utente trovato per EMAIL. Aggiorno OAuth info.');
            const dbUser = existingEmail.rows[0];
            await query(
              `UPDATE users SET oauth_provider = $1, oauth_id = $2, avatar_url = COALESCE($3, avatar_url), updated_at = NOW() WHERE id = $4`,
              ['google', account.providerAccountId, user.image, dbUser.id]
            );
            user.id = dbUser.id.toString();
            return true;
          }

          // Terza logica: Creazione nuovo utente
          console.log('[AUTH] Creazione NUOVO utente');
          const newUser = await query(
            `INSERT INTO users (email, full_name, avatar_url, oauth_provider, oauth_id, is_active, is_superuser, created_at, updated_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
               RETURNING id`,
            [user.email, user.name, user.image, 'google', account.providerAccountId, true, false]
          );

          user.id = newUser.rows[0].id.toString();
          return true;

        } catch (error: any) {
          console.error('[AUTH FAIL]', {
            step: 'signIn callback',
            user: user.email,
            error: error.message,
            code: error.code,
            detail: error.detail,
          });
          return false;
        }
      }
      return true; // Credentials provider allows sign in by default if authorize returns user
    },
    async jwt({ token, user }: any) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }: any) {
      if (session.user) {
        // @ts-ignore
        session.user.id = token.id;
      }
      return session;
    },
  },
  pages: {
    signIn: '/auth',
    error: '/auth/error',
  },
  debug: true,
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
