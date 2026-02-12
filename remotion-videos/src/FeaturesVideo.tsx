import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";
import {
  TransitionSeries,
  linearTiming,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();
const FONT = `${fontFamily}, -apple-system, BlinkMacSystemFont, sans-serif`;

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

/* ------------------------------------------------------------------ */
/*  SCENE 1: Template Gallery                                          */
/* ------------------------------------------------------------------ */

const FeaturesScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });

  const templates = [
    { name: "Restaurant Elegant", color: "#dc2626", accent: "#fca5a5" },
    { name: "SaaS Gradient", color: "#3b82f6", accent: "#93c5fd" },
    { name: "Portfolio Minimal", color: "#7c3aed", accent: "#c4b5fd" },
    { name: "E-commerce Modern", color: "#22c55e", accent: "#86efac" },
    { name: "Business Corporate", color: "#0ea5e9", accent: "#7dd3fc" },
    { name: "Blog Editorial", color: "#f59e0b", accent: "#fcd34d" },
  ];

  const zoomProgress = interpolate(frame, [55, 75], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%)",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <GradientOrb color="rgba(139,92,246,0.07)" size={500} x="10%" y="15%" phaseOffset={0} />
      <GradientOrb color="rgba(59,130,246,0.06)" size={400} x="65%" y="55%" phaseOffset={60} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
          width: "100%",
          maxWidth: 1100,
          transform: `scale(${interpolate(zoomProgress, [0, 1], [1, 1.15])})`,
        }}
      >
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
            textAlign: "center",
          }}
        >
          <div
            style={{
              display: "inline-flex",
              padding: "6px 16px",
              borderRadius: 20,
              background: "rgba(139,92,246,0.08)",
              border: "1px solid rgba(139,92,246,0.15)",
              color: "#7c3aed",
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: 1.5,
              marginBottom: 16,
            }}
          >
            19 TEMPLATE PROFESSIONALI
          </div>
          <h2
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: "#0c1222",
              lineHeight: 1.2,
            }}
          >
            Scegli il tuo{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              template
            </span>
          </h2>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: 16,
            width: "100%",
          }}
        >
          {templates.map((tmpl, i) => {
            const cardEnter = spring({
              frame: frame - (10 + i * 4),
              fps,
              config: { damping: 14, stiffness: 100 },
            });
            const isSelected = i === 1;
            const selectedGlow = isSelected
              ? interpolate(frame, [60, 75], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                })
              : 0;

            return (
              <div
                key={tmpl.name}
                style={{
                  opacity: interpolate(cardEnter, [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(cardEnter, [0, 1], [40, 0])}px) scale(${interpolate(cardEnter, [0, 1], [0.9, 1])})`,
                  borderRadius: 14,
                  overflow: "hidden",
                  border: isSelected
                    ? `2px solid rgba(124,58,237,${interpolate(selectedGlow, [0, 1], [0.1, 0.6])})`
                    : "1px solid #e2e8f0",
                  background: "#ffffff",
                  boxShadow: isSelected
                    ? `0 0 ${selectedGlow * 30}px rgba(124,58,237,${selectedGlow * 0.2})`
                    : "0 2px 8px rgba(0,0,0,0.04)",
                }}
              >
                <div
                  style={{
                    height: 110,
                    background: `linear-gradient(135deg, ${tmpl.color}10, ${tmpl.color}05)`,
                    padding: 12,
                    display: "flex",
                    flexDirection: "column",
                    gap: 6,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ width: 40, height: 6, borderRadius: 3, background: tmpl.color, opacity: 0.6 }} />
                    <div style={{ display: "flex", gap: 4 }}>
                      {[1, 2, 3].map((n) => (
                        <div key={n} style={{ width: 16, height: 4, borderRadius: 2, background: "rgba(0,0,0,0.08)" }} />
                      ))}
                    </div>
                  </div>
                  <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", gap: 4 }}>
                    <div style={{ width: "70%", height: 8, borderRadius: 4, background: "rgba(0,0,0,0.1)" }} />
                    <div style={{ width: "50%", height: 6, borderRadius: 3, background: "rgba(0,0,0,0.06)" }} />
                    <div style={{ width: 50, height: 12, borderRadius: 4, background: tmpl.color, opacity: 0.8, marginTop: 4 }} />
                  </div>
                </div>
                <div style={{ padding: "10px 12px", display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: tmpl.color }} />
                  <span style={{ fontSize: 12, color: "#64748b", fontWeight: 500 }}>{tmpl.name}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 2: AI Code-to-Website                                        */
/* ------------------------------------------------------------------ */

const FeaturesScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  const codeLines = [
    '{ "business": "Ristorante Da Mario",',
    '  "style": "elegant",',
    '  "theme": { "primary": "#dc2626" },',
    '  "sections": ["hero", "menu",',
    '    "gallery", "contacts"] }',
  ];
  const allCode = codeLines.join("\n");
  const typeProgress = interpolate(frame, [15, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const visibleChars = Math.floor(typeProgress * allCode.length);

  const transformProgress = interpolate(frame, [55, 75], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });

  const siteEnter = spring({
    frame: frame - 60,
    fps,
    config: { damping: 14, stiffness: 80 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%)",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <GradientOrb color="rgba(59,130,246,0.07)" size={500} x="15%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(139,92,246,0.06)" size={400} x="70%" y="50%" phaseOffset={50} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 32,
          width: "100%",
          maxWidth: 1100,
        }}
      >
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
            textAlign: "center",
          }}
        >
          <h2 style={{ fontSize: 42, fontWeight: 800, color: "#0c1222" }}>
            Da JSON a{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              sito completo
            </span>
          </h2>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 32, width: "100%" }}>
          {/* Code panel */}
          <div
            style={{
              flex: 1,
              padding: "20px 24px",
              borderRadius: 14,
              background: "#1e293b",
              border: "1px solid #334155",
              fontFamily: "monospace",
              fontSize: 14,
              lineHeight: 1.6,
              color: "#94a3b8",
              whiteSpace: "pre",
              minHeight: 180,
              position: "relative",
              overflow: "hidden",
            }}
          >
            <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ff5f57" }} />
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ffbd2e" }} />
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#28c840" }} />
            </div>
            <span style={{ color: "#e2e8f0" }}>
              {allCode.slice(0, visibleChars)}
            </span>
            <span
              style={{
                opacity: Math.sin(frame * 0.3) > 0 ? 1 : 0,
                borderRight: "2px solid #818cf8",
                marginLeft: 1,
                display: "inline-block",
                height: 16,
              }}
            />
          </div>

          {/* Arrow */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              opacity: interpolate(transformProgress, [0, 0.3], [0, 1], { extrapolateRight: "clamp" }),
            }}
          >
            <svg width={60} height={60} viewBox="0 0 60 60">
              <defs>
                <linearGradient id="arrowGradF" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#7c3aed" />
                </linearGradient>
              </defs>
              <path
                d="M10 30 L40 30 M32 20 L44 30 L32 40"
                fill="none"
                stroke="url(#arrowGradF)"
                strokeWidth={3}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>

          {/* Website preview */}
          <div
            style={{
              flex: 1,
              borderRadius: 14,
              overflow: "hidden",
              border: "1px solid #e2e8f0",
              boxShadow: "0 20px 60px rgba(0,0,0,0.06)",
              opacity: interpolate(siteEnter, [0, 1], [0, 1]),
              transform: `scale(${interpolate(siteEnter, [0, 1], [0.9, 1])})`,
            }}
          >
            <div
              style={{
                height: 32,
                background: "#f8fafc",
                display: "flex",
                alignItems: "center",
                padding: "0 10px",
                gap: 6,
                borderBottom: "1px solid #e2e8f0",
              }}
            >
              <div style={{ display: "flex", gap: 4 }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#ff5f57" }} />
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#ffbd2e" }} />
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#28c840" }} />
              </div>
              <div style={{ flex: 1, textAlign: "center", fontSize: 10, color: "#64748b", fontFamily: "monospace" }}>
                ristorante-da-mario.e-quipe.app
              </div>
            </div>
            <div style={{ height: 180, background: "linear-gradient(135deg, #fef2f2, #fff1f2)", padding: 16 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
                <div style={{ width: 50, height: 6, borderRadius: 3, background: "rgba(0,0,0,0.15)" }} />
                <div style={{ display: "flex", gap: 8 }}>
                  {["Menu", "About", "Contatti"].map((t) => (
                    <span key={t} style={{ fontSize: 8, color: "#94a3b8" }}>{t}</span>
                  ))}
                </div>
              </div>
              <h3 style={{ fontSize: 18, fontWeight: 800, color: "#0c1222", marginBottom: 4 }}>
                Il vero gusto della tradizione
              </h3>
              <p style={{ fontSize: 9, color: "#64748b", marginBottom: 10 }}>
                Cucina romana autentica dal 1985
              </p>
              <div
                style={{
                  padding: "6px 14px",
                  borderRadius: 6,
                  background: "#dc2626",
                  color: "white",
                  fontSize: 10,
                  fontWeight: 600,
                  width: "fit-content",
                }}
              >
                Prenota
              </div>
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 3: GSAP Animation Showcase                                   */
/* ------------------------------------------------------------------ */

const FeaturesScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  const fadeUpProgress = interpolate(frame, [15, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scaleInProgress = interpolate(frame, [25, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),
  });
  const splitText = "Animazioni GSAP";
  const splitProgress = interpolate(frame, [20, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const magneticPhase = Math.sin(frame * 0.08) * 8;

  const effects = [
    { name: "fade-up", code: 'data-animate="fade-up"' },
    { name: "scale-in", code: 'data-animate="scale-in"' },
    { name: "text-split", code: 'data-animate="text-split"' },
    { name: "magnetic", code: 'data-animate="magnetic"' },
  ];

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%)",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <GradientOrb color="rgba(59,130,246,0.07)" size={500} x="20%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(168,85,247,0.06)" size={400} x="60%" y="60%" phaseOffset={40} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 36,
          width: "100%",
          maxWidth: 1100,
        }}
      >
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
            textAlign: "center",
          }}
        >
          <div
            style={{
              display: "inline-flex",
              padding: "6px 16px",
              borderRadius: 20,
              background: "rgba(59,130,246,0.08)",
              border: "1px solid rgba(59,130,246,0.15)",
              color: "#3b82f6",
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: 1.5,
              marginBottom: 16,
            }}
          >
            29 EFFETTI PROFESSIONALI
          </div>
          <h2 style={{ fontSize: 42, fontWeight: 800, color: "#0c1222" }}>
            Animazioni{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              cinematografiche
            </span>
          </h2>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 20, width: "100%" }}>
          {/* fade-up demo */}
          <div
            style={{
              padding: 24,
              borderRadius: 16,
              background: "#ffffff",
              border: "1px solid #e2e8f0",
              minHeight: 160,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
            }}
          >
            <span style={{ fontSize: 11, color: "#64748b", fontFamily: "monospace" }}>{effects[0].code}</span>
            <div
              style={{
                opacity: fadeUpProgress,
                transform: `translateY(${interpolate(fadeUpProgress, [0, 1], [30, 0])}px)`,
              }}
            >
              <div style={{ width: "80%", height: 10, borderRadius: 5, background: "rgba(59,130,246,0.25)", marginBottom: 8 }} />
              <div style={{ width: "60%", height: 8, borderRadius: 4, background: "rgba(59,130,246,0.15)" }} />
              <div style={{ marginTop: 12, width: 80, height: 28, borderRadius: 6, background: "rgba(59,130,246,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "#3b82f6" }}>
                CTA Button
              </div>
            </div>
            <span style={{ fontSize: 12, color: "#64748b", fontWeight: 600 }}>fade-up</span>
          </div>

          {/* scale-in demo */}
          <div
            style={{
              padding: 24,
              borderRadius: 16,
              background: "#ffffff",
              border: "1px solid #e2e8f0",
              minHeight: 160,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
            }}
          >
            <span style={{ fontSize: 11, color: "#64748b", fontFamily: "monospace" }}>{effects[1].code}</span>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flex: 1 }}>
              <div
                style={{
                  width: 80,
                  height: 80,
                  borderRadius: 16,
                  background: "linear-gradient(135deg, rgba(124,58,237,0.2), rgba(59,130,246,0.2))",
                  transform: `scale(${interpolate(scaleInProgress, [0, 1], [0, 1])})`,
                  opacity: scaleInProgress,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <svg width={32} height={32} viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="#7c3aed" />
                </svg>
              </div>
            </div>
            <span style={{ fontSize: 12, color: "#64748b", fontWeight: 600 }}>scale-in</span>
          </div>

          {/* text-split demo */}
          <div
            style={{
              padding: 24,
              borderRadius: 16,
              background: "#ffffff",
              border: "1px solid #e2e8f0",
              minHeight: 160,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
            }}
          >
            <span style={{ fontSize: 11, color: "#64748b", fontFamily: "monospace" }}>{effects[2].code}</span>
            <div style={{ display: "flex", gap: 3, flexWrap: "wrap", padding: "16px 0" }}>
              {splitText.split("").map((char, ci) => {
                const charProgress = interpolate(
                  splitProgress,
                  [ci / splitText.length, Math.min((ci + 1) / splitText.length + 0.05, 1)],
                  [0, 1],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                );
                return (
                  <span
                    key={ci}
                    style={{
                      fontSize: 28,
                      fontWeight: 800,
                      color: "#0c1222",
                      opacity: charProgress,
                      transform: `translateY(${interpolate(charProgress, [0, 1], [20, 0])}px)`,
                      display: "inline-block",
                      minWidth: char === " " ? 10 : undefined,
                    }}
                  >
                    {char}
                  </span>
                );
              })}
            </div>
            <span style={{ fontSize: 12, color: "#64748b", fontWeight: 600 }}>text-split</span>
          </div>

          {/* magnetic demo */}
          <div
            style={{
              padding: 24,
              borderRadius: 16,
              background: "#ffffff",
              border: "1px solid #e2e8f0",
              minHeight: 160,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
            }}
          >
            <span style={{ fontSize: 11, color: "#64748b", fontFamily: "monospace" }}>{effects[3].code}</span>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flex: 1 }}>
              <div
                style={{
                  padding: "12px 32px",
                  borderRadius: 12,
                  background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                  color: "white",
                  fontSize: 16,
                  fontWeight: 700,
                  transform: `translate(${magneticPhase}px, ${magneticPhase * 0.5}px)`,
                  boxShadow: "0 8px 30px rgba(99,102,241,0.25)",
                }}
              >
                Hover Me
              </div>
            </div>
            <span style={{ fontSize: 12, color: "#64748b", fontWeight: 600 }}>magnetic</span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 4: One-Click Publish                                         */
/* ------------------------------------------------------------------ */

const FeaturesScene4 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  const domainText = "mio-business.e-quipe.app";
  const typeProgress = interpolate(frame, [20, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const visibleChars = Math.floor(typeProgress * domainText.length);
  const cursorOpacity = visibleChars < domainText.length ? (Math.sin(frame * 0.3) > 0 ? 1 : 0) : 0;

  const globeRotation = frame * 1.2;

  const connectionLines = Array.from({ length: 8 }, (_, i) => {
    const angle = (i / 8) * Math.PI * 2 + globeRotation * 0.01;
    const radius = 80;
    return {
      x1: Math.cos(angle) * (radius * 0.5),
      y1: Math.sin(angle) * (radius * 0.5),
      x2: Math.cos(angle) * radius,
      y2: Math.sin(angle) * radius,
      opacity: interpolate(Math.sin(frame * 0.1 + i), [-1, 1], [0.2, 0.8]),
    };
  });

  const publishEnter = spring({
    frame: frame - 55,
    fps,
    config: { damping: 10, stiffness: 120 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%)",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <GradientOrb color="rgba(34,197,94,0.07)" size={500} x="40%" y="25%" phaseOffset={0} />
      <GradientOrb color="rgba(59,130,246,0.05)" size={400} x="20%" y="60%" phaseOffset={60} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
        }}
      >
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
            textAlign: "center",
          }}
        >
          <h2 style={{ fontSize: 48, fontWeight: 800, color: "#0c1222" }}>
            Pubblica con{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #22c55e, #3b82f6)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              1 click
            </span>
          </h2>
        </div>

        <div style={{ position: "relative", width: 200, height: 200 }}>
          <svg width={200} height={200} viewBox="-100 -100 200 200">
            {connectionLines.map((line, i) => (
              <line
                key={i}
                x1={line.x1}
                y1={line.y1}
                x2={line.x2}
                y2={line.y2}
                stroke="#3b82f6"
                strokeWidth={1.5}
                opacity={line.opacity}
                strokeLinecap="round"
              />
            ))}
            <circle
              cx={0}
              cy={0}
              r={55}
              fill="none"
              stroke="rgba(59,130,246,0.25)"
              strokeWidth={2}
            />
            <ellipse
              cx={0}
              cy={0}
              rx={55}
              ry={20}
              fill="none"
              stroke="rgba(59,130,246,0.12)"
              strokeWidth={1}
              transform={`rotate(${globeRotation * 0.3})`}
            />
            <ellipse
              cx={0}
              cy={0}
              rx={20}
              ry={55}
              fill="none"
              stroke="rgba(59,130,246,0.12)"
              strokeWidth={1}
            />
            <circle cx={0} cy={0} r={6} fill="#3b82f6" />
            {connectionLines.map((line, i) => (
              <circle
                key={`dot-${i}`}
                cx={line.x2}
                cy={line.y2}
                r={3}
                fill="#22c55e"
                opacity={line.opacity}
              />
            ))}
          </svg>
        </div>

        <div
          style={{
            padding: "14px 28px",
            borderRadius: 14,
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#22c55e",
              boxShadow: "0 0 8px rgba(34,197,94,0.5)",
            }}
          />
          <span style={{ fontSize: 20, color: "#1e293b", fontFamily: "monospace", fontWeight: 500 }}>
            https://{domainText.slice(0, visibleChars)}
            <span
              style={{
                opacity: cursorOpacity,
                borderRight: "2px solid #22c55e",
                marginLeft: 1,
                display: "inline-block",
                height: 20,
              }}
            />
          </span>
        </div>

        <div
          style={{
            opacity: interpolate(publishEnter, [0, 1], [0, 1]),
            transform: `scale(${interpolate(publishEnter, [0, 1], [0.5, 1])})`,
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "12px 24px",
            borderRadius: 16,
            background: "rgba(34,197,94,0.08)",
            border: "1px solid rgba(34,197,94,0.2)",
          }}
        >
          <svg width={20} height={20} viewBox="0 0 20 20">
            <circle cx={10} cy={10} r={10} fill="#22c55e" />
            <path
              d="M6 10 L9 13 L14 7"
              fill="none"
              stroke="white"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span style={{ fontSize: 16, fontWeight: 600, color: "#16a34a" }}>
            Sito online — SSL incluso
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  COMPOSITION                                                        */
/* ------------------------------------------------------------------ */

export const FeaturesVideoComposition = () => {
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={80}>
        <FeaturesScene1 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={85}>
        <FeaturesScene2 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={85}>
        <FeaturesScene3 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={wipe({ direction: "from-left" })}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={95}>
        <FeaturesScene4 />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};

export const FEATURES_VIDEO_CONFIG = {
  id: "FeaturesVideo",
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
};
