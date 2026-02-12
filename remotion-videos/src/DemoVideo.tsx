import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Inter";

// Load Inter font
const { fontFamily } = loadFont();

/* ------------------------------------------------------------------ */
/*  SHARED HELPERS                                                     */
/* ------------------------------------------------------------------ */

const FONT = `${fontFamily}, -apple-system, BlinkMacSystemFont, sans-serif`;

/** Seeded pseudo-random for deterministic rendering */
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

/* ------------------------------------------------------------------ */
/*  DARK CINEMATIC BACKGROUND (shared across Hero scenes)              */
/* ------------------------------------------------------------------ */

const DarkBackground = () => {
  const frame = useCurrentFrame();

  // Particle dots
  const particles = Array.from({ length: 40 }, (_, i) => ({
    x: seededRandom(i * 4 + 1) * 1920,
    y: seededRandom(i * 4 + 2) * 1080,
    size: 2 + seededRandom(i * 4 + 3) * 3,
    phase: seededRandom(i * 4 + 4) * Math.PI * 2,
    speed: 0.3 + seededRandom(i * 4 + 5) * 0.8,
  }));

  return (
    <>
      {/* Base dark background */}
      <AbsoluteFill style={{ background: "#0a0a0f" }} />

      {/* Animated gradient mesh — purple/blue nebula */}
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 900,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(88,28,135,0.35) 0%, transparent 70%)",
          filter: "blur(120px)",
          left: "10%",
          top: "-20%",
          transform: `translate(${Math.sin(frame * 0.015) * 30}px, ${Math.cos(frame * 0.012) * 20}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(30,64,175,0.3) 0%, transparent 70%)",
          filter: "blur(100px)",
          right: "-5%",
          bottom: "-10%",
          transform: `translate(${Math.cos(frame * 0.018) * 25}px, ${Math.sin(frame * 0.014) * 18}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 500,
          height: 500,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 70%)",
          filter: "blur(80px)",
          left: "50%",
          top: "40%",
          transform: `translate(-50%, -50%) translate(${Math.sin(frame * 0.02 + 1) * 20}px, ${Math.cos(frame * 0.016 + 1) * 15}px)`,
        }}
      />

      {/* Floating particle dots */}
      {particles.map((p, i) => {
        const px = p.x + Math.sin(frame * 0.02 * p.speed + p.phase) * 30;
        const py = p.y + Math.cos(frame * 0.018 * p.speed + p.phase) * 25;
        const pOpacity = interpolate(
          Math.sin(frame * 0.04 + p.phase),
          [-1, 1],
          [0.05, 0.25]
        );
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: px,
              top: py,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              background: "rgba(255,255,255,0.8)",
              opacity: pOpacity,
            }}
          />
        );
      })}
    </>
  );
};

/* ------------------------------------------------------------------ */
/*  HERO VIDEO COMPOSITION — 12 seconds, 360 frames (Dark Cinematic)  */
/* ------------------------------------------------------------------ */

/** Scene 1: "E-QUIPE" brand intro — huge text with glow */
const HeroScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({
    frame: frame - 10,
    fps,
    config: { damping: 12, stiffness: 80 },
  });
  const subtitleEnter = spring({
    frame: frame - 30,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Glow pulse
  const glowSize = interpolate(
    Math.sin(frame * 0.08),
    [-1, 1],
    [40, 80]
  );

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <DarkBackground />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
        }}
      >
        {/* Brand name */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `scale(${interpolate(titleEnter, [0, 1], [0.7, 1])})`,
          }}
        >
          <h1
            style={{
              fontSize: 140,
              fontWeight: 900,
              color: "#ffffff",
              textAlign: "center",
              letterSpacing: 12,
              lineHeight: 1,
              textShadow: `0 0 ${glowSize}px rgba(139,92,246,0.6), 0 0 ${glowSize * 2}px rgba(59,130,246,0.3)`,
            }}
          >
            E-QUIPE
          </h1>
        </div>

        {/* Subtitle */}
        <div
          style={{
            opacity: interpolate(subtitleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(subtitleEnter, [0, 1], [30, 0])}px)`,
            marginTop: 32,
          }}
        >
          <div
            style={{
              fontSize: 52,
              fontWeight: 600,
              background: "linear-gradient(135deg, #818cf8, #38bdf8)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              textAlign: "center",
              letterSpacing: 4,
            }}
          >
            Site Builder AI
          </div>
        </div>

        {/* Decorative line */}
        <div
          style={{
            marginTop: 40,
            width: interpolate(titleEnter, [0, 1], [0, 200]),
            height: 2,
            background: "linear-gradient(90deg, transparent, rgba(139,92,246,0.8), transparent)",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 2: "L'AI GENERA IL TUO SITO" — spinning orb + progress */
const HeroScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Progress counter
  const progress = interpolate(frame, [15, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });
  const percentage = Math.round(progress * 100);

  // Orb animation
  const orbScale = interpolate(
    Math.sin(frame * 0.08),
    [-1, 1],
    [0.9, 1.1]
  );
  const orbRotation = frame * 2;
  const orbGlow = interpolate(
    Math.sin(frame * 0.06),
    [-1, 1],
    [30, 70]
  );

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <DarkBackground />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          gap: 40,
        }}
      >
        {/* Title */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [40, 0])}px)`,
          }}
        >
          <h1
            style={{
              fontSize: 72,
              fontWeight: 800,
              color: "#ffffff",
              textAlign: "center",
              lineHeight: 1.15,
              textShadow: "0 0 30px rgba(139,92,246,0.4)",
            }}
          >
            {"L'AI GENERA"}
            <br />
            <span
              style={{
                background: "linear-gradient(135deg, #818cf8, #38bdf8)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              IL TUO SITO
            </span>
          </h1>
        </div>

        {/* Spinning orb */}
        <div
          style={{
            position: "relative",
            width: 200,
            height: 200,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* Outer ring */}
          <div
            style={{
              position: "absolute",
              width: 200,
              height: 200,
              borderRadius: "50%",
              border: "2px solid rgba(139,92,246,0.3)",
              transform: `rotate(${orbRotation}deg)`,
              borderTopColor: "#818cf8",
              borderRightColor: "rgba(56,189,248,0.6)",
            }}
          />
          {/* Inner orb */}
          <div
            style={{
              width: 120,
              height: 120,
              borderRadius: "50%",
              background: "radial-gradient(circle at 35% 35%, #818cf8, #4f46e5, #1e1b4b)",
              transform: `scale(${orbScale})`,
              boxShadow: `0 0 ${orbGlow}px rgba(129,140,248,0.5), 0 0 ${orbGlow * 2}px rgba(59,130,246,0.2)`,
            }}
          />
          {/* Percentage overlay */}
          <div
            style={{
              position: "absolute",
              fontSize: 48,
              fontWeight: 800,
              color: "#ffffff",
              fontVariantNumeric: "tabular-nums",
              textShadow: "0 0 20px rgba(139,92,246,0.8)",
            }}
          >
            {percentage}%
          </div>
        </div>

        {/* Progress bar */}
        <div
          style={{
            width: 400,
            height: 6,
            borderRadius: 3,
            background: "rgba(255,255,255,0.1)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${percentage}%`,
              height: "100%",
              borderRadius: 3,
              background: "linear-gradient(90deg, #818cf8, #38bdf8)",
              boxShadow: "0 0 20px rgba(129,140,248,0.5)",
            }}
          />
        </div>

        {/* Status text */}
        <div
          style={{
            fontSize: 48,
            fontWeight: 600,
            color: percentage < 100 ? "rgba(255,255,255,0.6)" : "#38bdf8",
            textShadow: percentage >= 100 ? "0 0 20px rgba(56,189,248,0.5)" : "none",
          }}
        >
          {percentage < 100 ? "Generazione..." : "Completato!"}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 3: "IL RISULTATO" — simplified website mockup */
const HeroScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90 },
  });
  const mockupEnter = spring({
    frame: frame - 15,
    fps,
    config: { damping: 12, stiffness: 70 },
  });

  // Staggered blocks
  const block1 = spring({ frame: frame - 25, fps, config: { damping: 14 } });
  const block2 = spring({ frame: frame - 35, fps, config: { damping: 14 } });
  const block3 = spring({ frame: frame - 45, fps, config: { damping: 14 } });

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <DarkBackground />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          gap: 40,
        }}
      >
        {/* Title */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
          }}
        >
          <h1
            style={{
              fontSize: 80,
              fontWeight: 800,
              color: "#ffffff",
              textAlign: "center",
              textShadow: "0 0 30px rgba(139,92,246,0.4)",
            }}
          >
            IL RISULTATO
          </h1>
        </div>

        {/* Simplified browser mockup */}
        <div
          style={{
            opacity: interpolate(mockupEnter, [0, 1], [0, 1]),
            transform: `scale(${interpolate(mockupEnter, [0, 1], [0.85, 1])})`,
            width: 900,
            borderRadius: 16,
            overflow: "hidden",
            border: "1px solid rgba(139,92,246,0.3)",
            boxShadow: "0 0 60px rgba(139,92,246,0.15), 0 25px 80px rgba(0,0,0,0.4)",
          }}
        >
          {/* Browser bar */}
          <div
            style={{
              height: 44,
              background: "rgba(255,255,255,0.05)",
              display: "flex",
              alignItems: "center",
              padding: "0 16px",
              gap: 8,
              borderBottom: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <div style={{ display: "flex", gap: 6 }}>
              <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ff5f57" }} />
              <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ffbd2e" }} />
              <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28c840" }} />
            </div>
            <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
              <div
                style={{
                  padding: "4px 24px",
                  borderRadius: 8,
                  background: "rgba(255,255,255,0.08)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  color: "rgba(255,255,255,0.5)",
                  fontSize: 13,
                  fontFamily: "monospace",
                }}
              >
                il-tuo-sito.e-quipe.app
              </div>
            </div>
          </div>

          {/* Site content — colored blocks */}
          <div style={{ background: "#0f0f18", padding: 24 }}>
            {/* Nav bar block */}
            <div
              style={{
                opacity: interpolate(block1, [0, 1], [0, 1]),
                height: 40,
                borderRadius: 8,
                background: "rgba(255,255,255,0.06)",
                marginBottom: 16,
                display: "flex",
                alignItems: "center",
                padding: "0 16px",
                justifyContent: "space-between",
              }}
            >
              <div style={{ width: 80, height: 14, borderRadius: 4, background: "rgba(129,140,248,0.4)" }} />
              <div style={{ display: "flex", gap: 12 }}>
                {[60, 50, 70, 55].map((w, i) => (
                  <div key={i} style={{ width: w, height: 10, borderRadius: 3, background: "rgba(255,255,255,0.15)" }} />
                ))}
              </div>
            </div>

            {/* Hero block */}
            <div
              style={{
                opacity: interpolate(block2, [0, 1], [0, 1]),
                transform: `translateY(${interpolate(block2, [0, 1], [20, 0])}px)`,
                height: 220,
                borderRadius: 12,
                background: "linear-gradient(135deg, rgba(88,28,135,0.4), rgba(30,64,175,0.3))",
                marginBottom: 16,
                padding: 32,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                gap: 12,
              }}
            >
              <div style={{ width: 350, height: 28, borderRadius: 6, background: "rgba(255,255,255,0.25)" }} />
              <div style={{ width: 250, height: 16, borderRadius: 4, background: "rgba(255,255,255,0.12)" }} />
              <div
                style={{
                  width: 140,
                  height: 40,
                  borderRadius: 8,
                  background: "linear-gradient(135deg, #818cf8, #38bdf8)",
                  marginTop: 8,
                  boxShadow: "0 0 20px rgba(129,140,248,0.3)",
                }}
              />
            </div>

            {/* Section blocks row */}
            <div
              style={{
                opacity: interpolate(block3, [0, 1], [0, 1]),
                transform: `translateY(${interpolate(block3, [0, 1], [20, 0])}px)`,
                display: "flex",
                gap: 12,
              }}
            >
              {[1, 2, 3].map((_, i) => (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    height: 100,
                    borderRadius: 10,
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid rgba(255,255,255,0.06)",
                    padding: 16,
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                  }}
                >
                  <div style={{ width: "60%", height: 12, borderRadius: 3, background: "rgba(129,140,248,0.3)" }} />
                  <div style={{ width: "80%", height: 8, borderRadius: 2, background: "rgba(255,255,255,0.1)" }} />
                  <div style={{ width: "50%", height: 8, borderRadius: 2, background: "rgba(255,255,255,0.07)" }} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 4: "INIZIA ORA" — big CTA with glow pulse + Gratis badge */
const HeroScene4 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 10, stiffness: 100 },
  });
  const ctaEnter = spring({
    frame: frame - 25,
    fps,
    config: { damping: 12, stiffness: 90 },
  });
  const badgeEnter = spring({
    frame: frame - 40,
    fps,
    config: { damping: 14, stiffness: 100 },
  });
  const brandEnter = spring({
    frame: frame - 55,
    fps,
    config: { damping: 14 },
  });

  // CTA glow pulse
  const ctaGlow = interpolate(
    Math.sin(frame * 0.1),
    [-1, 1],
    [20, 50]
  );

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <DarkBackground />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          gap: 40,
        }}
      >
        {/* Main CTA text */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `scale(${interpolate(titleEnter, [0, 1], [0.6, 1])})`,
          }}
        >
          <h1
            style={{
              fontSize: 120,
              fontWeight: 900,
              color: "#ffffff",
              textAlign: "center",
              lineHeight: 1.1,
              textShadow: `0 0 ${ctaGlow}px rgba(139,92,246,0.5), 0 0 ${ctaGlow * 2}px rgba(59,130,246,0.3)`,
            }}
          >
            INIZIA ORA
          </h1>
        </div>

        {/* CTA button */}
        <div
          style={{
            opacity: interpolate(ctaEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(ctaEnter, [0, 1], [30, 0])}px)`,
          }}
        >
          <div
            style={{
              padding: "24px 80px",
              borderRadius: 16,
              background: "linear-gradient(135deg, #7c3aed, #3b82f6)",
              fontSize: 52,
              fontWeight: 800,
              color: "#ffffff",
              textAlign: "center",
              boxShadow: `0 0 ${ctaGlow}px rgba(124,58,237,0.5), 0 15px 50px rgba(0,0,0,0.4)`,
              letterSpacing: 2,
            }}
          >
            CREA IL TUO SITO
          </div>
        </div>

        {/* Gratis badge */}
        <div
          style={{
            opacity: interpolate(badgeEnter, [0, 1], [0, 1]),
            transform: `scale(${interpolate(badgeEnter, [0, 1], [0.5, 1])})`,
          }}
        >
          <div
            style={{
              padding: "14px 40px",
              borderRadius: 30,
              background: "rgba(34,197,94,0.15)",
              border: "2px solid rgba(34,197,94,0.4)",
              fontSize: 48,
              fontWeight: 700,
              color: "#4ade80",
              textAlign: "center",
              boxShadow: "0 0 30px rgba(34,197,94,0.2)",
              letterSpacing: 4,
            }}
          >
            GRATIS
          </div>
        </div>

        {/* Brand footer */}
        <div
          style={{
            opacity: interpolate(brandEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(brandEnter, [0, 1], [15, 0])}px)`,
            marginTop: 20,
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              background: "linear-gradient(135deg, #7c3aed, #3b82f6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 20,
              fontWeight: 900,
              color: "white",
              boxShadow: "0 0 20px rgba(124,58,237,0.4)",
            }}
          >
            E
          </div>
          <span
            style={{
              fontSize: 48,
              fontWeight: 700,
              color: "rgba(255,255,255,0.7)",
              letterSpacing: 2,
            }}
          >
            e-quipe.app
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const HeroVideoComposition = () => {
  const frame = useCurrentFrame();

  // Simple scene switching with fade transitions
  const scene = frame < 90 ? 1 : frame < 180 ? 2 : frame < 270 ? 3 : 4;

  const fadeOut1 = interpolate(frame, [80, 90], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeIn2 = interpolate(frame, [90, 100], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut2 = interpolate(frame, [170, 180], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeIn3 = interpolate(frame, [180, 190], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut3 = interpolate(frame, [260, 270], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeIn4 = interpolate(frame, [270, 280], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: "#0a0a0f" }}>
      {scene === 1 && (
        <AbsoluteFill style={{ opacity: fadeOut1 }}>
          <HeroScene1 />
        </AbsoluteFill>
      )}
      {scene === 2 && (
        <AbsoluteFill style={{ opacity: Math.min(fadeIn2, fadeOut2) }}>
          <HeroScene2 />
        </AbsoluteFill>
      )}
      {scene === 3 && (
        <AbsoluteFill style={{ opacity: Math.min(fadeIn3, fadeOut3) }}>
          <HeroScene3 />
        </AbsoluteFill>
      )}
      {scene === 4 && (
        <AbsoluteFill style={{ opacity: fadeIn4 }}>
          <HeroScene4 />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

export const HERO_VIDEO_CONFIG = {
  id: "HeroVideo",
  fps: 30,
  durationInFrames: 360, // 12 seconds
  width: 1920,
  height: 1080,
};

/* ------------------------------------------------------------------ */
/*  ADS VIDEO COMPOSITION — 10 seconds, 300 frames                    */
/*  STYLE: Neon Data Dashboard                                         */
/* ------------------------------------------------------------------ */

const NEON = {
  bg: "#05050a",
  pink: "#ff006e",
  cyan: "#00f5d4",
  yellow: "#fee440",
  gridDot: "rgba(255,255,255,0.06)",
};

const neonGlow = (color: string, spread = 20) =>
  `0 0 ${spread}px ${color}, 0 0 ${spread * 2}px ${color}`;

/** Shared dark background with grid dots */
const NeonBackground = () => (
  <>
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: NEON.bg,
      }}
    />
    {/* Grid dot pattern */}
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `radial-gradient(circle, ${NEON.gridDot} 1px, transparent 1px)`,
        backgroundSize: "40px 40px",
      }}
    />
  </>
);

/** Scene 1: "GESTIONE ADS" - Neon title + animated bar chart */
const AdsScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  const barData = [
    { label: "Lun", value: 65, color: NEON.pink },
    { label: "Mar", value: 90, color: NEON.cyan },
    { label: "Mer", value: 55, color: NEON.yellow },
    { label: "Gio", value: 105, color: NEON.pink },
    { label: "Ven", value: 120, color: NEON.cyan },
  ];
  const maxValue = 130;

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <NeonBackground />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          gap: 48,
        }}
      >
        {/* Neon Title */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [40, 0])}px)`,
            textAlign: "center",
          }}
        >
          <h1
            style={{
              fontSize: 72,
              fontWeight: 900,
              color: NEON.pink,
              textShadow: neonGlow(NEON.pink, 15),
              letterSpacing: 6,
              lineHeight: 1.1,
            }}
          >
            GESTIONE ADS
          </h1>
          <p
            style={{
              fontSize: 28,
              color: "rgba(255,255,255,0.5)",
              marginTop: 12,
              fontWeight: 500,
              letterSpacing: 3,
            }}
          >
            PERFORMANCE SETTIMANALE
          </p>
        </div>

        {/* Bar Chart */}
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            gap: 40,
            height: 360,
            padding: "0 80px",
          }}
        >
          {barData.map((bar, i) => {
            const barEnter = spring({
              frame: frame - (20 + i * 8),
              fps,
              config: { damping: 12, stiffness: 80 },
            });
            const barHeight = (bar.value / maxValue) * 300;

            return (
              <div
                key={bar.label}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 16,
                }}
              >
                {/* Value */}
                <span
                  style={{
                    fontSize: 24,
                    fontWeight: 800,
                    color: bar.color,
                    textShadow: neonGlow(bar.color, 8),
                    opacity: interpolate(barEnter, [0, 1], [0, 1]),
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {Math.round(bar.value * interpolate(barEnter, [0, 1], [0, 1]))}
                </span>
                {/* Bar */}
                <div
                  style={{
                    width: 70,
                    height: barHeight * interpolate(barEnter, [0, 1], [0, 1]),
                    borderRadius: "8px 8px 4px 4px",
                    background: `linear-gradient(180deg, ${bar.color}, ${bar.color}88)`,
                    boxShadow: neonGlow(bar.color, 12),
                  }}
                />
                {/* Label */}
                <span
                  style={{
                    fontSize: 18,
                    color: "rgba(255,255,255,0.5)",
                    fontWeight: 600,
                    letterSpacing: 1,
                  }}
                >
                  {bar.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 2: "RISULTATI" - 3 large neon metric cards */
const AdsScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame: frame - 5, fps, config: { damping: 15 } });

  const metrics = [
    { label: "ROI", value: "+340%", color: NEON.cyan, target: 340, suffix: "%", prefix: "+", delay: 15 },
    { label: "Impressioni", value: "45K+", color: NEON.yellow, target: 45, suffix: "K+", prefix: "", delay: 25 },
    { label: "Conversioni", value: "2.8K", color: NEON.pink, target: 2.8, suffix: "K", prefix: "", delay: 35 },
  ];

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <NeonBackground />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          gap: 56,
        }}
      >
        {/* Title */}
        <h1
          style={{
            fontSize: 64,
            fontWeight: 900,
            color: "#ffffff",
            textShadow: neonGlow("rgba(255,255,255,0.3)", 10),
            letterSpacing: 8,
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
          }}
        >
          RISULTATI
        </h1>

        {/* Metric Cards */}
        <div style={{ display: "flex", gap: 40 }}>
          {metrics.map((m) => {
            const cardEnter = spring({
              frame: frame - m.delay,
              fps,
              config: { damping: 12, stiffness: 90 },
            });
            const counterProgress = interpolate(
              frame,
              [m.delay + 5, m.delay + 55],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            const currentVal = m.target === 2.8
              ? (counterProgress * m.target).toFixed(1)
              : Math.round(counterProgress * m.target);

            return (
              <div
                key={m.label}
                style={{
                  width: 340,
                  padding: "48px 40px",
                  borderRadius: 20,
                  background: "rgba(255,255,255,0.03)",
                  border: `1px solid ${m.color}55`,
                  boxShadow: neonGlow(m.color, 15),
                  textAlign: "center",
                  opacity: interpolate(cardEnter, [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(cardEnter, [0, 1], [40, 0])}px) scale(${interpolate(cardEnter, [0, 1], [0.9, 1])})`,
                }}
              >
                <div
                  style={{
                    fontSize: 88,
                    fontWeight: 900,
                    color: m.color,
                    textShadow: neonGlow(m.color, 12),
                    lineHeight: 1,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {m.prefix}{currentVal}{m.suffix}
                </div>
                <div
                  style={{
                    fontSize: 22,
                    color: "rgba(255,255,255,0.55)",
                    marginTop: 16,
                    fontWeight: 600,
                    letterSpacing: 3,
                    textTransform: "uppercase",
                  }}
                >
                  {m.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 3: "META + GOOGLE ADS" - Two badges, subtitle, CTA */
const AdsScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame: frame - 5, fps, config: { damping: 14 } });
  const metaEnter = spring({ frame: frame - 15, fps, config: { damping: 12, stiffness: 90 } });
  const googleEnter = spring({ frame: frame - 25, fps, config: { damping: 12, stiffness: 90 } });
  const subtitleEnter = spring({ frame: frame - 40, fps, config: { damping: 14 } });
  const ctaEnter = spring({ frame: frame - 55, fps, config: { damping: 10, stiffness: 100 } });

  // CTA glow pulse
  const ctaPulse = interpolate(
    Math.sin(frame * 0.1),
    [-1, 1],
    [15, 35]
  );

  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <NeonBackground />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          gap: 48,
        }}
      >
        {/* Title */}
        <h1
          style={{
            fontSize: 68,
            fontWeight: 900,
            color: "#ffffff",
            letterSpacing: 4,
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
          }}
        >
          <span style={{ color: NEON.pink, textShadow: neonGlow(NEON.pink, 12) }}>META</span>
          <span style={{ color: "rgba(255,255,255,0.3)", margin: "0 20px" }}>+</span>
          <span style={{ color: NEON.cyan, textShadow: neonGlow(NEON.cyan, 12) }}>GOOGLE ADS</span>
        </h1>

        {/* Two Badge Rectangles */}
        <div style={{ display: "flex", gap: 48 }}>
          {/* Meta Badge */}
          <div
            style={{
              width: 420,
              height: 200,
              borderRadius: 24,
              background: "rgba(255,255,255,0.03)",
              border: `2px solid ${NEON.pink}88`,
              boxShadow: neonGlow(NEON.pink, 20),
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 16,
              opacity: interpolate(metaEnter, [0, 1], [0, 1]),
              transform: `translateX(${interpolate(metaEnter, [0, 1], [-60, 0])}px) scale(${interpolate(metaEnter, [0, 1], [0.85, 1])})`,
            }}
          >
            <span
              style={{
                fontSize: 52,
                fontWeight: 900,
                color: NEON.pink,
                textShadow: neonGlow(NEON.pink, 10),
                letterSpacing: 3,
              }}
            >
              META
            </span>
            <span
              style={{
                fontSize: 20,
                color: "rgba(255,255,255,0.45)",
                fontWeight: 600,
                letterSpacing: 2,
              }}
            >
              FACEBOOK & INSTAGRAM
            </span>
          </div>

          {/* Google Badge */}
          <div
            style={{
              width: 420,
              height: 200,
              borderRadius: 24,
              background: "rgba(255,255,255,0.03)",
              border: `2px solid ${NEON.cyan}88`,
              boxShadow: neonGlow(NEON.cyan, 20),
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 16,
              opacity: interpolate(googleEnter, [0, 1], [0, 1]),
              transform: `translateX(${interpolate(googleEnter, [0, 1], [60, 0])}px) scale(${interpolate(googleEnter, [0, 1], [0.85, 1])})`,
            }}
          >
            <span
              style={{
                fontSize: 52,
                fontWeight: 900,
                color: NEON.cyan,
                textShadow: neonGlow(NEON.cyan, 10),
                letterSpacing: 3,
              }}
            >
              GOOGLE
            </span>
            <span
              style={{
                fontSize: 20,
                color: "rgba(255,255,255,0.45)",
                fontWeight: 600,
                letterSpacing: 2,
              }}
            >
              SEARCH & DISPLAY
            </span>
          </div>
        </div>

        {/* Subtitle */}
        <p
          style={{
            fontSize: 32,
            color: "rgba(255,255,255,0.6)",
            fontWeight: 600,
            letterSpacing: 2,
            opacity: interpolate(subtitleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(subtitleEnter, [0, 1], [20, 0])}px)`,
          }}
        >
          Esperti Dedicati
        </p>

        {/* CTA with glow pulse */}
        <div
          style={{
            opacity: interpolate(ctaEnter, [0, 1], [0, 1]),
            transform: `scale(${interpolate(ctaEnter, [0, 1], [0.7, 1])})`,
          }}
        >
          <div
            style={{
              padding: "22px 64px",
              borderRadius: 16,
              background: `linear-gradient(135deg, ${NEON.pink}, ${NEON.cyan})`,
              boxShadow: `0 0 ${ctaPulse}px ${NEON.pink}, 0 0 ${ctaPulse}px ${NEON.cyan}`,
              fontSize: 28,
              fontWeight: 900,
              color: "#05050a",
              letterSpacing: 4,
            }}
          >
            INIZIA ORA
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const AdsVideoComposition = () => {
  const frame = useCurrentFrame();

  // Simple scene switching based on frame ranges
  // Scene 1: 0-99, Scene 2: 100-199, Scene 3: 200-299
  const scene = frame < 100 ? 1 : frame < 200 ? 2 : 3;

  // Fade transition between scenes
  const fadeOut1 = interpolate(frame, [90, 100], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeIn2 = interpolate(frame, [100, 110], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut2 = interpolate(frame, [190, 200], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeIn3 = interpolate(frame, [200, 210], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: NEON.bg }}>
      {scene === 1 && (
        <AbsoluteFill style={{ opacity: fadeOut1 }}>
          <AdsScene1 />
        </AbsoluteFill>
      )}
      {scene === 2 && (
        <AbsoluteFill style={{ opacity: Math.min(fadeIn2, fadeOut2) }}>
          <AdsScene2 />
        </AbsoluteFill>
      )}
      {scene === 3 && (
        <AbsoluteFill style={{ opacity: fadeIn3 }}>
          <AdsScene3 />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

export const ADS_VIDEO_CONFIG = {
  id: "AdsVideo",
  fps: 30,
  durationInFrames: 300, // 10 seconds
  width: 1920,
  height: 1080,
};

/* ------------------------------------------------------------------ */
/*  EXPORTS (backward compatible)                                      */
/* ------------------------------------------------------------------ */

export const DemoVideoComposition = HeroVideoComposition;
export const DEMO_VIDEO_CONFIG = HERO_VIDEO_CONFIG;
