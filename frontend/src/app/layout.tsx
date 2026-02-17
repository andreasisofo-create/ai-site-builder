import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
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
      <head>
        <script
          type="text/javascript"
          data-cmp-ab="1"
          src="https://cdn.consentmanager.net/delivery/autoblocking/130b896a62e17.js"
          data-cmp-host="c.delivery.consentmanager.net"
          data-cmp-cdn="cdn.consentmanager.net"
          data-cmp-codesrc="0"
        />
      </head>
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
