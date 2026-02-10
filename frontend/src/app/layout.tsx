import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import { Providers } from "@/components/Providers";
import HelpChatbot from "@/components/HelpChatbot";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "E-quipe Site Builder",
  description: "Crea siti web professionali in pochi minuti",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="it">
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster position="top-right" />
          <HelpChatbot />
        </Providers>
      </body>
    </html>
  );
}
