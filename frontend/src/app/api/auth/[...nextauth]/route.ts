import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import { Pool } from "pg";

// Configurazione Database Diretta (Bypass Backend Python)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

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
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        // Nota: Il login con password rimarrà limitato se non implementiamo 
        // anche l'hashing password qui. Per ora supportiamo Google.
        return null;
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
          const client = await pool.connect();
          try {
            // 1. Cerca utente per oauth_id
            const existingUser = await client.query(
              'SELECT * FROM users WHERE oauth_id = $1',
              [account.providerAccountId]
            );

            if (existingUser.rows.length > 0) {
              user.id = existingUser.rows[0].id.toString();
              return true;
            }

            // 2. Cerca utente per email
            const existingEmail = await client.query(
              'SELECT * FROM users WHERE email = $1',
              [user.email]
            );

            if (existingEmail.rows.length > 0) {
              // Aggiorna utente esistente con OAuth
              const dbUser = existingEmail.rows[0];
              await client.query(
                `UPDATE users SET oauth_provider = $1, oauth_id = $2, avatar_url = COALESCE($3, avatar_url) WHERE id = $4`,
                ['google', account.providerAccountId, user.image, dbUser.id]
              );
              user.id = dbUser.id.toString();
              return true;
            }

            // 3. Crea nuovo utente
            const newUser = await client.query(
              `INSERT INTO users (email, full_name, avatar_url, oauth_provider, oauth_id, is_active, is_superuser, created_at, updated_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
               RETURNING id`,
              [user.email, user.name, user.image, 'google', account.providerAccountId, true, false]
            );

            user.id = newUser.rows[0].id.toString();
            return true;

          } finally {
            client.release();
          }
        } catch (error) {
          console.error("Database connection error:", error);
          return false;
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
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
