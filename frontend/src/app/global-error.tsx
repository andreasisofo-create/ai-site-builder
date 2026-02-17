"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="it">
      <body style={{ backgroundColor: "#0a0a0a", color: "#fff", fontFamily: "system-ui, sans-serif" }}>
        <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ textAlign: "center", maxWidth: 400, padding: "0 16px" }}>
            <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 8 }}>Qualcosa e&apos; andato storto</h2>
            <p style={{ color: "#94a3b8", fontSize: 14, marginBottom: 24 }}>
              Si e&apos; verificato un errore imprevisto. Prova a ricaricare la pagina.
            </p>
            <button
              onClick={reset}
              style={{
                padding: "8px 20px",
                backgroundColor: "#2563eb",
                color: "#fff",
                border: "none",
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 500,
                cursor: "pointer",
              }}
            >
              Riprova
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
