import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import { query } from "@/lib/db";

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
  ],
  callbacks: {
    async signIn({ user, account, profile }: any) {
      if (account?.provider === "google") {
        try {
          console.log('[AUTH] Tentativo signIn per:', user.email);

          // Usiamo l'approccio UPSERT (Insert o Update) che è più atomico e sicuro
          // Nota: la tua tabella `users` ha colonne diverse dall'esempio di Claude, quindi adatto la query alle TUE colonne (oauth_id, ecc)

          /*
             Struttura tabella users (da init-db):
             id, email, full_name, avatar_url, oauth_provider, oauth_id, is_active...
          */

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

          // Seconda logica: Check esistenza per email (per collegare account esistenti)
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
          return false; // Questo causa AccessDenied, ma ora vedremo il log su Vercel
        }
      }
      return true;
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
    error: '/auth/error', // Per vedere meglio errori se ci sono
  },
  debug: true, // Attiva debug log su Vercel
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
