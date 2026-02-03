import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ],
  pages: {
    signIn: "/auth",
  },
  callbacks: {
    async signIn({ account, profile }) {
      return true;
    },
    async redirect({ url, baseUrl }) {
      return "/dashboard";
    },
  },
});

export { handler as GET, handler as POST };
