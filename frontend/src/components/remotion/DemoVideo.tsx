"use client";

import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Easing,
} from "remotion";

/* ------------------------------------------------------------------ */
/*  HERO VIDEO — Plays in the hero section, shows the AI builder UX   */
/* ------------------------------------------------------------------ */

const GradientOrb = ({
  color,
  size,
  x,
  y,
  phaseOffset,
}: {
  color: string;
  size: number;
  x: string;
  y: string;
  phaseOffset: number;
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const breathe = interpolate(
    frame,
    [0, durationInFrames / 2, durationInFrames],
    [1, 1.3, 1],
    { extrapolateRight: "clamp" }
  );
  const drift = Math.sin((frame + phaseOffset) * 0.02) * 15;

  return (
    <div
      style={{
        position: "absolute",
        width: size,
        height: size,
        borderRadius: "50%",
        background: color,
        filter: `blur(${size * 0.4}px)`,
        left: x,
        top: y,
        transform: `scale(${breathe}) translate(${drift}px, ${drift * 0.6}px)`,
      }}
    />
  );
};

const TypewriterText = ({ text, startFrame }: { text: string; startFrame: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const elapsed = frame - startFrame;
  if (elapsed < 0) return null;
  const charsPerFrame = 1.2;
  const visible = Math.min(Math.floor(elapsed * charsPerFrame), text.length);
  return (
    <span>
      {text.slice(0, visible)}
      {visible < text.length && (
        <span
          style={{
            opacity: Math.sin(frame * 0.3) > 0 ? 1 : 0,
            borderRight: "2px solid #818cf8",
            marginLeft: 2,
          }}
        />
      )}
    </span>
  );
};

const MockBrowser = ({ children, url }: { children: React.ReactNode; url: string }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 18, stiffness: 80 } });
  const scale = interpolate(enter, [0, 1], [0.85, 1]);
  const opacity = interpolate(enter, [0, 1], [0, 1]);

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        opacity,
        borderRadius: 16,
        overflow: "hidden",
        border: "1px solid rgba(255,255,255,0.08)",
        boxShadow: "0 25px 80px rgba(0,0,0,0.6), 0 0 60px rgba(99,102,241,0.15)",
      }}
    >
      <div
        style={{
          height: 44,
          background: "#161616",
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 8,
        }}
      >
        <div style={{ display: "flex", gap: 6 }}>
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ff5f57" }} />
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ffbd2e" }} />
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28c840" }} />
        </div>
        <div
          style={{
            flex: 1,
            display: "flex",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              padding: "4px 20px",
              borderRadius: 6,
              background: "rgba(255,255,255,0.05)",
              color: "#94a3b8",
              fontSize: 13,
              fontFamily: "monospace",
            }}
          >
            {url}
          </div>
        </div>
      </div>
      <div style={{ background: "#0a0a0a", position: "relative" }}>{children}</div>
    </div>
  );
};

const ProgressRing = ({
  progress,
  size,
  stroke,
}: {
  progress: number;
  size: number;
  stroke: number;
}) => {
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - progress);
  return (
    <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="url(#grad)"
        strokeWidth={stroke}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
      />
      <defs>
        <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#3b82f6" />
          <stop offset="100%" stopColor="#8b5cf6" />
        </linearGradient>
      </defs>
    </svg>
  );
};

export const HeroVideoComposition = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Phase timeline (in frames at 30fps)
  const PHASE_INPUT = 0;       // 0-2s: user types description
  const PHASE_GENERATE = 60;   // 2-4.5s: AI generates
  const PHASE_RESULT = 135;    // 4.5-7s: result appears
  const PHASE_PUBLISH = 210;   // 7-8.5s: publish click
  const PHASE_LIVE = 255;      // 8.5-10s: site is live

  // Shared animations
  const generateProgress = interpolate(
    frame,
    [PHASE_GENERATE, PHASE_RESULT],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.25, 0.1, 0.25, 1) }
  );

  const resultEnter = spring({
    frame: frame - PHASE_RESULT,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  const publishPulse = frame >= PHASE_PUBLISH && frame < PHASE_LIVE
    ? Math.sin((frame - PHASE_PUBLISH) * 0.15) * 0.5 + 0.5
    : 0;

  const liveEnter = spring({
    frame: frame - PHASE_LIVE,
    fps,
    config: { damping: 12 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "#050508",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 60,
      }}
    >
      {/* Animated background */}
      <GradientOrb color="rgba(59,130,246,0.12)" size={700} x="5%" y="10%" phaseOffset={0} />
      <GradientOrb color="rgba(139,92,246,0.10)" size={550} x="65%" y="50%" phaseOffset={50} />
      <GradientOrb color="rgba(168,85,247,0.08)" size={400} x="30%" y="70%" phaseOffset={100} />

      <div style={{ position: "relative", zIndex: 1, width: "100%", maxWidth: 1400, display: "flex", gap: 60 }}>
        {/* Left side — process steps */}
        <div style={{ flex: "0 0 380px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <Sequence from={0}>
            <div>
              <div
                style={{
                  opacity: interpolate(spring({ frame, fps, config: { damping: 15 } }), [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(spring({ frame, fps }), [0, 1], [30, 0])}px)`,
                }}
              >
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "6px 16px",
                    borderRadius: 20,
                    background: "rgba(99,102,241,0.12)",
                    border: "1px solid rgba(99,102,241,0.2)",
                    marginBottom: 24,
                  }}
                >
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e", animation: "pulse 2s infinite" }} />
                  <span style={{ fontSize: 14, color: "#a5b4fc", letterSpacing: 1 }}>AI-POWERED</span>
                </div>

                <h2 style={{ fontSize: 44, fontWeight: 800, color: "white", lineHeight: 1.15, marginBottom: 16 }}>
                  Crea il tuo sito
                  <br />
                  <span style={{ background: "linear-gradient(135deg, #60a5fa, #a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                    in tempo reale
                  </span>
                </h2>
                <p style={{ fontSize: 18, color: "#94a3b8", lineHeight: 1.7 }}>
                  Guarda come l'AI genera un sito professionale completo mentre tu descrivi il tuo business.
                </p>
              </div>

              {/* Step indicators */}
              <div style={{ marginTop: 40, display: "flex", flexDirection: "column", gap: 16 }}>
                {[
                  { label: "Descrivi", active: frame >= PHASE_INPUT, done: frame >= PHASE_GENERATE },
                  { label: "Genera", active: frame >= PHASE_GENERATE, done: frame >= PHASE_RESULT },
                  { label: "Risultato", active: frame >= PHASE_RESULT, done: frame >= PHASE_PUBLISH },
                  { label: "Pubblica", active: frame >= PHASE_PUBLISH, done: frame >= PHASE_LIVE },
                ].map((step, i) => {
                  const stepEnter = spring({ frame: frame - (i * 30 + 15), fps, config: { damping: 15 } });
                  return (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 12,
                        opacity: interpolate(stepEnter, [0, 1], [0, 1]),
                        transform: `translateX(${interpolate(stepEnter, [0, 1], [-20, 0])}px)`,
                      }}
                    >
                      <div
                        style={{
                          width: 36,
                          height: 36,
                          borderRadius: 10,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: 14,
                          fontWeight: 700,
                          background: step.done
                            ? "linear-gradient(135deg, #3b82f6, #8b5cf6)"
                            : step.active
                              ? "rgba(99,102,241,0.2)"
                              : "rgba(255,255,255,0.04)",
                          border: step.active ? "1px solid rgba(99,102,241,0.4)" : "1px solid rgba(255,255,255,0.06)",
                          color: step.done ? "white" : step.active ? "#a5b4fc" : "#475569",
                          transition: "all 0.3s",
                        }}
                      >
                        {step.done ? "✓" : i + 1}
                      </div>
                      <span
                        style={{
                          fontSize: 16,
                          fontWeight: step.active ? 600 : 400,
                          color: step.active ? "white" : "#64748b",
                        }}
                      >
                        {step.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </Sequence>
        </div>

        {/* Right side — browser mockup */}
        <div style={{ flex: 1, display: "flex", alignItems: "center" }}>
          <MockBrowser url="e-quipe.app/dashboard">
            <div style={{ minHeight: 500, padding: 32, position: "relative" }}>
              {/* Phase 1: Input form */}
              {frame < PHASE_RESULT && (
                <div style={{ opacity: frame >= PHASE_RESULT ? 0 : 1 }}>
                  <div style={{ marginBottom: 24 }}>
                    <div style={{ fontSize: 13, color: "#64748b", marginBottom: 8, fontWeight: 500 }}>
                      NOME ATTIVITA
                    </div>
                    <div
                      style={{
                        padding: "12px 16px",
                        borderRadius: 10,
                        background: "rgba(255,255,255,0.04)",
                        border: "1px solid rgba(255,255,255,0.08)",
                        fontSize: 16,
                        color: "white",
                        minHeight: 44,
                      }}
                    >
                      <TypewriterText text="Ristorante Da Mario" startFrame={10} />
                    </div>
                  </div>

                  <div style={{ marginBottom: 24 }}>
                    <div style={{ fontSize: 13, color: "#64748b", marginBottom: 8, fontWeight: 500 }}>
                      DESCRIZIONE
                    </div>
                    <div
                      style={{
                        padding: "12px 16px",
                        borderRadius: 10,
                        background: "rgba(255,255,255,0.04)",
                        border: "1px solid rgba(255,255,255,0.08)",
                        fontSize: 15,
                        color: "#cbd5e1",
                        minHeight: 80,
                        lineHeight: 1.6,
                      }}
                    >
                      <TypewriterText
                        text="Cucina romana autentica dal 1985. Pasta fatta in casa, pizza al forno a legna..."
                        startFrame={35}
                      />
                    </div>
                  </div>

                  {/* Generate button */}
                  {frame >= PHASE_GENERATE - 10 && (
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 16,
                        marginTop: 32,
                      }}
                    >
                      <div
                        style={{
                          padding: "14px 28px",
                          borderRadius: 12,
                          background: frame >= PHASE_GENERATE
                            ? "linear-gradient(135deg, #3b82f6, #7c3aed)"
                            : "rgba(99,102,241,0.2)",
                          color: "white",
                          fontWeight: 600,
                          fontSize: 15,
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                          boxShadow: frame >= PHASE_GENERATE ? "0 8px 30px rgba(99,102,241,0.3)" : "none",
                        }}
                      >
                        {frame >= PHASE_GENERATE && frame < PHASE_RESULT ? (
                          <>
                            <ProgressRing progress={generateProgress} size={22} stroke={2.5} />
                            Generando...
                          </>
                        ) : (
                          "✨ Genera con AI"
                        )}
                      </div>

                      {frame >= PHASE_GENERATE && frame < PHASE_RESULT && (
                        <span style={{ fontSize: 14, color: "#64748b" }}>
                          {Math.round(generateProgress * 100)}%
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Phase 2: Generated result */}
              {frame >= PHASE_RESULT && (
                <div
                  style={{
                    opacity: interpolate(resultEnter, [0, 1], [0, 1]),
                    transform: `translateY(${interpolate(resultEnter, [0, 1], [20, 0])}px)`,
                  }}
                >
                  {/* Mini website preview */}
                  <div
                    style={{
                      borderRadius: 12,
                      overflow: "hidden",
                      border: "1px solid rgba(255,255,255,0.08)",
                      marginBottom: 20,
                    }}
                  >
                    {/* Hero section of generated site */}
                    <div
                      style={{
                        height: 220,
                        background: "linear-gradient(135deg, #1a0a0a, #2a1515)",
                        padding: 24,
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "flex-end",
                        position: "relative",
                      }}
                    >
                      <div style={{ position: "absolute", top: 16, right: 16, display: "flex", gap: 16, fontSize: 13, color: "rgba(255,255,255,0.7)" }}>
                        <span>Menu</span><span>Chi Siamo</span><span>Contatti</span>
                      </div>
                      <h3 style={{ fontSize: 28, fontWeight: 800, color: "white", marginBottom: 6 }}>
                        Ristorante Da Mario
                      </h3>
                      <p style={{ fontSize: 14, color: "rgba(255,255,255,0.7)", marginBottom: 12 }}>
                        Il vero gusto della tradizione romana
                      </p>
                      <div
                        style={{
                          display: "inline-flex",
                          padding: "8px 20px",
                          borderRadius: 8,
                          background: "#dc2626",
                          color: "white",
                          fontSize: 13,
                          fontWeight: 600,
                          width: "fit-content",
                        }}
                      >
                        Prenota un Tavolo
                      </div>
                    </div>

                    {/* Sections preview */}
                    <div style={{ display: "flex", gap: 1, background: "rgba(255,255,255,0.03)" }}>
                      {["Chi Siamo", "Il Menu", "Galleria", "Contatti"].map((s) => (
                        <div
                          key={s}
                          style={{
                            flex: 1,
                            padding: "12px 8px",
                            textAlign: "center",
                            fontSize: 11,
                            color: "#64748b",
                            borderRight: "1px solid rgba(255,255,255,0.04)",
                          }}
                        >
                          {s}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Success badge */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div
                        style={{
                          width: 32,
                          height: 32,
                          borderRadius: "50%",
                          background: "rgba(34,197,94,0.15)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: 16,
                        }}
                      >
                        ✓
                      </div>
                      <span style={{ color: "#22c55e", fontSize: 14, fontWeight: 600 }}>
                        Sito generato in 45 secondi
                      </span>
                    </div>

                    {/* Publish button */}
                    <div
                      style={{
                        padding: "10px 24px",
                        borderRadius: 10,
                        background: frame >= PHASE_PUBLISH
                          ? "linear-gradient(135deg, #22c55e, #16a34a)"
                          : "rgba(34,197,94,0.15)",
                        border: "1px solid rgba(34,197,94,0.3)",
                        color: frame >= PHASE_PUBLISH ? "white" : "#22c55e",
                        fontWeight: 600,
                        fontSize: 14,
                        boxShadow: publishPulse > 0 ? `0 0 ${publishPulse * 20}px rgba(34,197,94,0.3)` : "none",
                      }}
                    >
                      🚀 Pubblica
                    </div>
                  </div>

                  {/* Live notification */}
                  {frame >= PHASE_LIVE && (
                    <div
                      style={{
                        marginTop: 20,
                        padding: "14px 20px",
                        borderRadius: 12,
                        background: "rgba(34,197,94,0.08)",
                        border: "1px solid rgba(34,197,94,0.2)",
                        display: "flex",
                        alignItems: "center",
                        gap: 12,
                        opacity: interpolate(liveEnter, [0, 1], [0, 1]),
                        transform: `translateY(${interpolate(liveEnter, [0, 1], [10, 0])}px)`,
                      }}
                    >
                      <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#22c55e" }} />
                      <span style={{ color: "#86efac", fontSize: 14 }}>
                        Online su{" "}
                        <span style={{ color: "white", fontWeight: 600 }}>
                          ristorante-da-mario.e-quipe.app
                        </span>
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </MockBrowser>
        </div>
      </div>

      {/* Bottom progress */}
      <div
        style={{
          position: "absolute",
          bottom: 30,
          left: 60,
          right: 60,
          height: 3,
          borderRadius: 2,
          background: "rgba(255,255,255,0.04)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            borderRadius: 2,
            background: "linear-gradient(90deg, #3b82f6, #8b5cf6)",
            width: `${interpolate(frame, [0, durationInFrames], [0, 100], { extrapolateRight: "clamp" })}%`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const HERO_VIDEO_CONFIG = {
  id: "HeroVideo",
  fps: 30,
  durationInFrames: 300, // 10 seconds
  width: 1920,
  height: 1080,
};

/* ------------------------------------------------------------------ */
/*  ADS SERVICE VIDEO — Shows Meta + Google + AI content creation     */
/* ------------------------------------------------------------------ */

const MetricCard = ({
  label,
  value,
  change,
  delay,
}: {
  label: string;
  value: string;
  change: string;
  delay: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - delay, fps, config: { damping: 14 } });

  return (
    <div
      style={{
        padding: "20px 24px",
        borderRadius: 14,
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(255,255,255,0.06)",
        opacity: interpolate(enter, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(enter, [0, 1], [20, 0])}px) scale(${interpolate(enter, [0, 1], [0.95, 1])})`,
      }}
    >
      <div style={{ fontSize: 13, color: "#64748b", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 800, color: "white" }}>{value}</div>
      <div style={{ fontSize: 13, color: "#22c55e", marginTop: 4 }}>{change}</div>
    </div>
  );
};

export const AdsVideoComposition = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 14 } });

  // Channel tabs animation
  const tabFrame = interpolate(frame, [0, durationInFrames], [0, 3], { extrapolateRight: "clamp" });
  const activeTab = Math.floor(tabFrame) % 3;
  const tabs = ["Meta Ads", "Google Ads", "AI Content"];
  const tabColors = ["#1877f2", "#4285f4", "#8b5cf6"];

  return (
    <AbsoluteFill
      style={{
        background: "#050508",
        fontFamily: "'Inter', -apple-system, sans-serif",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 60,
      }}
    >
      <GradientOrb color="rgba(24,119,242,0.10)" size={600} x="10%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(66,133,244,0.08)" size={500} x="70%" y="60%" phaseOffset={80} />

      <div style={{ position: "relative", zIndex: 1, width: "100%", maxWidth: 1200 }}>
        {/* Header */}
        <div
          style={{
            textAlign: "center",
            marginBottom: 48,
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
          }}
        >
          <div
            style={{
              display: "inline-flex",
              padding: "6px 16px",
              borderRadius: 20,
              background: "rgba(34,197,94,0.1)",
              border: "1px solid rgba(34,197,94,0.2)",
              color: "#86efac",
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: 1,
              marginBottom: 20,
            }}
          >
            SERVIZIO ADS GESTITO
          </div>
          <h2 style={{ fontSize: 42, fontWeight: 800, color: "white", lineHeight: 1.2 }}>
            Porta clienti al tuo sito
            <br />
            <span style={{ background: "linear-gradient(135deg, #60a5fa, #a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              con Meta e Google Ads
            </span>
          </h2>
        </div>

        {/* Dashboard mockup */}
        <div
          style={{
            borderRadius: 16,
            overflow: "hidden",
            border: "1px solid rgba(255,255,255,0.06)",
            background: "rgba(255,255,255,0.02)",
          }}
        >
          {/* Tab bar */}
          <div style={{ display: "flex", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
            {tabs.map((tab, i) => (
              <div
                key={tab}
                style={{
                  flex: 1,
                  padding: "14px 20px",
                  textAlign: "center",
                  fontSize: 14,
                  fontWeight: activeTab === i ? 700 : 400,
                  color: activeTab === i ? "white" : "#64748b",
                  borderBottom: activeTab === i ? `2px solid ${tabColors[i]}` : "2px solid transparent",
                  background: activeTab === i ? "rgba(255,255,255,0.02)" : "transparent",
                  transition: "all 0.3s",
                }}
              >
                {tab}
              </div>
            ))}
          </div>

          {/* Metrics grid */}
          <div style={{ padding: 24 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
              <MetricCard label="Impressioni" value="24.5K" change="+18%" delay={30} />
              <MetricCard label="Click" value="1,847" change="+24%" delay={45} />
              <MetricCard label="Conversioni" value="156" change="+32%" delay={60} />
              <MetricCard label="ROI" value="3.8x" change="+0.5x" delay={75} />
            </div>

            {/* Chart placeholder */}
            <div
              style={{
                height: 180,
                borderRadius: 12,
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.04)",
                position: "relative",
                overflow: "hidden",
                display: "flex",
                alignItems: "flex-end",
                padding: "0 16px 16px",
                gap: 8,
              }}
            >
              {Array.from({ length: 14 }).map((_, i) => {
                const barDelay = 90 + i * 5;
                const barEnter = spring({ frame: frame - barDelay, fps, config: { damping: 12 } });
                const heights = [40, 55, 35, 65, 80, 70, 95, 85, 110, 100, 120, 130, 115, 140];
                return (
                  <div
                    key={i}
                    style={{
                      flex: 1,
                      height: heights[i] * interpolate(barEnter, [0, 1], [0, 1]),
                      borderRadius: "6px 6px 0 0",
                      background: `linear-gradient(180deg, ${tabColors[activeTab]}cc, ${tabColors[activeTab]}44)`,
                    }}
                  />
                );
              })}
            </div>
          </div>
        </div>

        {/* Bottom badges */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: 32,
            marginTop: 32,
          }}
        >
          {["IA prepara tutto", "Esperto approva", "Monitoraggio 24/7"].map((text, i) => {
            const badgeEnter = spring({ frame: frame - (180 + i * 15), fps, config: { damping: 15 } });
            return (
              <div
                key={text}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  opacity: interpolate(badgeEnter, [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(badgeEnter, [0, 1], [15, 0])}px)`,
                }}
              >
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e" }} />
                <span style={{ fontSize: 14, color: "#94a3b8" }}>{text}</span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const ADS_VIDEO_CONFIG = {
  id: "AdsVideo",
  fps: 30,
  durationInFrames: 240, // 8 seconds
  width: 1920,
  height: 1080,
};

// Re-export old name for backward compatibility
export const DemoVideoComposition = HeroVideoComposition;
export const DEMO_VIDEO_CONFIG = HERO_VIDEO_CONFIG;
