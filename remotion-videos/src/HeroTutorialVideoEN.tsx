import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();
const FONT = `${fontFamily}, -apple-system, BlinkMacSystemFont, sans-serif`;

const COLORS = {
  bg: "#0a0a1a",
  card: "#16162a",
  border: "rgba(255,255,255,0.1)",
  text: "#FFFFFF",
  muted: "#94A3B8",
  accent: "#0090FF",
  accentDark: "#0070C9",
  green: "#22C55E",
  greenBg: "rgba(34,197,94,0.1)",
};

/* ------------------------------------------------------------------ */
/*  SCENE 1: "Tell us about your business" - Chat message (0-4s)      */
/* ------------------------------------------------------------------ */
const Scene1_ContactUs: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame: frame - 5, fps, config: { damping: 14, stiffness: 90 } });
  const subtitleEnter = spring({ frame: frame - 15, fps, config: { damping: 14, stiffness: 90 } });

  const bubble1Enter = spring({ frame: frame - Math.round(1.2 * fps), fps, config: { damping: 12, stiffness: 100 } });
  const bubble2Enter = spring({ frame: frame - Math.round(1.8 * fps), fps, config: { damping: 12, stiffness: 100 } });
  const bubble3Enter = spring({ frame: frame - Math.round(2.4 * fps), fps, config: { damping: 12, stiffness: 100 } });

  const messages = [
    { text: "I have a restaurant in Rome, traditional cuisine", delay: bubble1Enter },
    { text: "I'd like a modern site with online reservations", delay: bubble2Enter },
    { text: "My logo is red and gold", delay: bubble3Enter },
  ];

  return (
    <AbsoluteFill style={{ background: COLORS.bg, fontFamily: FONT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{
        opacity: interpolate(titleEnter, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
        fontSize: 52, fontWeight: 800, color: COLORS.text, marginBottom: 8, textAlign: "center",
      }}>
        1. Tell us about your business
      </div>
      <div style={{
        opacity: interpolate(subtitleEnter, [0, 1], [0, 1]),
        fontSize: 24, color: COLORS.muted, marginBottom: 48, textAlign: "center",
      }}>
        Just 3 details. No commitment.
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 16, width: 700 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            opacity: interpolate(msg.delay, [0, 1], [0, 1]),
            transform: `translateX(${interpolate(msg.delay, [0, 1], [40, 0])}px)`,
            padding: "18px 28px",
            borderRadius: 20,
            borderTopRightRadius: 6,
            background: COLORS.accent,
            alignSelf: "flex-end",
            maxWidth: "85%",
          }}>
            <span style={{ fontSize: 22, color: COLORS.text, fontWeight: 500 }}>{msg.text}</span>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 2: "Our team works for you" - Design process (4-8s)         */
/* ------------------------------------------------------------------ */
const Scene2_WeWork: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame: frame - 5, fps, config: { damping: 14, stiffness: 90 } });

  const el1 = spring({ frame: frame - Math.round(0.8 * fps), fps, config: { damping: 12 } });
  const el2 = spring({ frame: frame - Math.round(1.2 * fps), fps, config: { damping: 12 } });
  const el3 = spring({ frame: frame - Math.round(1.6 * fps), fps, config: { damping: 12 } });
  const el4 = spring({ frame: frame - Math.round(2.0 * fps), fps, config: { damping: 12 } });

  const pulse = Math.sin(frame * 0.08) * 0.3 + 0.7;

  const steps = [
    { label: "Design", icon: "\uD83C\uDFA8", progress: el1 },
    { label: "Copy", icon: "\u270D\uFE0F", progress: el2 },
    { label: "Photos", icon: "\uD83D\uDCF8", progress: el3 },
    { label: "Animations", icon: "\u2728", progress: el4 },
  ];

  return (
    <AbsoluteFill style={{ background: COLORS.bg, fontFamily: FONT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{
        opacity: interpolate(titleEnter, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
        fontSize: 52, fontWeight: 800, color: COLORS.text, marginBottom: 12, textAlign: "center",
      }}>
        2. Our team works for you
      </div>
      <div style={{
        opacity: interpolate(titleEnter, [0, 1], [0, 1]),
        fontSize: 24, color: COLORS.muted, marginBottom: 60, textAlign: "center",
      }}>
        We build your custom site. You don't have to do anything.
      </div>

      <div style={{ display: "flex", gap: 32 }}>
        {steps.map((step, i) => (
          <div key={i} style={{
            opacity: interpolate(step.progress, [0, 1], [0, 1]),
            transform: `scale(${interpolate(step.progress, [0, 1], [0.5, 1])})`,
            width: 180, height: 180,
            borderRadius: 24,
            background: COLORS.card,
            border: `1px solid ${COLORS.border}`,
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12,
            boxShadow: `0 0 ${30 * pulse}px ${COLORS.accent}20`,
          }}>
            <span style={{ fontSize: 48 }}>{step.icon}</span>
            <span style={{ fontSize: 18, fontWeight: 700, color: COLORS.text }}>{step.label}</span>
            <div style={{ width: 100, height: 6, borderRadius: 3, background: "rgba(255,255,255,0.1)", overflow: "hidden" }}>
              <div style={{
                width: `${interpolate(step.progress, [0, 1], [0, 100])}%`,
                height: "100%", borderRadius: 3,
                background: `linear-gradient(90deg, ${COLORS.accent}, ${COLORS.accentDark})`,
              }} />
            </div>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 3: "Here's your site!" - Browser reveal (8-12.5s)           */
/* ------------------------------------------------------------------ */
const Scene3_SiteReady: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame: frame - 5, fps, config: { damping: 14 } });
  const browserEnter = spring({ frame: frame - 15, fps, config: { damping: 14, stiffness: 80 } });
  const nav = spring({ frame: frame - 25, fps, config: { damping: 14 } });
  const hero = spring({ frame: frame - 35, fps, config: { damping: 14 } });
  const cards = spring({ frame: frame - 50, fps, config: { damping: 14 } });
  const badgeEnter = spring({ frame: frame - Math.round(2.5 * fps), fps, config: { damping: 10, stiffness: 100 } });

  return (
    <AbsoluteFill style={{ background: COLORS.bg, fontFamily: FONT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{
        opacity: interpolate(titleEnter, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
        fontSize: 42, fontWeight: 800, color: COLORS.text, marginBottom: 32, textAlign: "center",
      }}>
        3. Here's your site!
      </div>

      <div style={{
        opacity: interpolate(browserEnter, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(browserEnter, [0, 1], [50, 0])}px)`,
        width: 900, borderRadius: 16, overflow: "hidden",
        border: `1px solid ${COLORS.border}`,
        boxShadow: "0 25px 80px rgba(0,144,255,0.15)",
      }}>
        <div style={{ height: 44, background: "#12122a", display: "flex", alignItems: "center", padding: "0 16px", gap: 10, borderBottom: `1px solid ${COLORS.border}` }}>
          <div style={{ display: "flex", gap: 7 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F57" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FFBD2E" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28C840" }} />
          </div>
          <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
            <div style={{ padding: "5px 20px", borderRadius: 8, background: "rgba(255,255,255,0.05)", border: `1px solid ${COLORS.border}`, color: COLORS.muted, fontSize: 13, fontFamily: "monospace" }}>
              damarco-restaurant.com
            </div>
          </div>
        </div>

        <div style={{ background: COLORS.card, padding: 20 }}>
          <div style={{
            opacity: interpolate(nav, [0, 1], [0, 1]),
            height: 40, borderRadius: 10, background: "rgba(255,255,255,0.03)", marginBottom: 14,
            display: "flex", alignItems: "center", padding: "0 16px", justifyContent: "space-between",
          }}>
            <div style={{ width: 90, height: 12, borderRadius: 4, background: COLORS.accent }} />
            <div style={{ display: "flex", gap: 12 }}>
              {[55, 45, 60, 50].map((w, i) => (
                <div key={i} style={{ width: w, height: 8, borderRadius: 3, background: "rgba(255,255,255,0.15)" }} />
              ))}
            </div>
          </div>

          <div style={{
            opacity: interpolate(hero, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(hero, [0, 1], [15, 0])}px)`,
            height: 180, borderRadius: 12,
            background: "linear-gradient(135deg, #B91C1C 0%, #DC2626 50%, #F59E0B 100%)",
            marginBottom: 14, padding: 28,
            display: "flex", flexDirection: "column", justifyContent: "center", gap: 10,
          }}>
            <div style={{ width: 280, height: 20, borderRadius: 5, background: "rgba(255,255,255,0.4)" }} />
            <div style={{ width: 200, height: 12, borderRadius: 3, background: "rgba(255,255,255,0.2)" }} />
            <div style={{ width: 120, height: 34, borderRadius: 8, background: "rgba(255,255,255,0.9)", marginTop: 6 }} />
          </div>

          <div style={{
            opacity: interpolate(cards, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(cards, [0, 1], [15, 0])}px)`,
            display: "flex", gap: 10,
          }}>
            {[1, 2, 3].map((_, i) => (
              <div key={i} style={{
                flex: 1, height: 80, borderRadius: 10, background: "rgba(255,255,255,0.03)",
                border: `1px solid ${COLORS.border}`, padding: 12,
                display: "flex", flexDirection: "column", gap: 6,
              }}>
                <div style={{ width: "50%", height: 10, borderRadius: 3, background: `${COLORS.accent}50` }} />
                <div style={{ width: "70%", height: 7, borderRadius: 2, background: "rgba(255,255,255,0.1)" }} />
                <div style={{ width: "40%", height: 7, borderRadius: 2, background: "rgba(255,255,255,0.06)" }} />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{
        position: "absolute", bottom: 140, right: 300,
        opacity: interpolate(badgeEnter, [0, 1], [0, 1]),
        transform: `scale(${interpolate(badgeEnter, [0, 1], [0.5, 1])})`,
        display: "flex", alignItems: "center", gap: 10,
        padding: "12px 24px", borderRadius: 50,
        background: COLORS.greenBg, border: `2px solid ${COLORS.green}`,
        boxShadow: "0 8px 30px rgba(34,197,94,0.2)",
      }}>
        <svg width={24} height={24} viewBox="0 0 24 24">
          <circle cx={12} cy={12} r={12} fill={COLORS.green} />
          <path d="M 7 12 L 10 15 L 17 8" fill="none" stroke="#FFFFFF" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span style={{ fontSize: 20, fontWeight: 700, color: COLORS.green }}>Ready in 48h</span>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 4: "Like it? Pay." Decision (12.5-16s)                      */
/* ------------------------------------------------------------------ */
const Scene4_Decision: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame: frame - 5, fps, config: { damping: 14, stiffness: 90 } });
  const leftCard = spring({ frame: frame - Math.round(0.8 * fps), fps, config: { damping: 12 } });
  const rightCard = spring({ frame: frame - Math.round(1.2 * fps), fps, config: { damping: 12 } });
  const bottomText = spring({ frame: frame - Math.round(2.2 * fps), fps, config: { damping: 14 } });

  return (
    <AbsoluteFill style={{ background: COLORS.bg, fontFamily: FONT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{
        opacity: interpolate(titleEnter, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
        fontSize: 52, fontWeight: 800, color: COLORS.text, marginBottom: 16, textAlign: "center",
      }}>
        4. You decide.
      </div>
      <div style={{
        opacity: interpolate(titleEnter, [0, 1], [0, 1]),
        fontSize: 26, color: COLORS.muted, marginBottom: 60, textAlign: "center",
      }}>
        See the result before spending a penny.
      </div>

      <div style={{ display: "flex", gap: 40 }}>
        <div style={{
          opacity: interpolate(leftCard, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(leftCard, [0, 1], [30, 0])}px)`,
          width: 360, padding: "40px 36px", borderRadius: 24,
          background: "rgba(34,197,94,0.08)", border: `2px solid ${COLORS.green}`,
          boxShadow: "0 0 40px rgba(34,197,94,0.15)",
          display: "flex", flexDirection: "column", alignItems: "center", gap: 16,
        }}>
          <svg width={56} height={56} viewBox="0 0 56 56">
            <circle cx={28} cy={28} r={28} fill={COLORS.green} />
            <path d="M 16 28 L 24 36 L 40 20" fill="none" stroke="#FFFFFF" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span style={{ fontSize: 28, fontWeight: 800, color: COLORS.green }}>Like it?</span>
          <span style={{ fontSize: 20, color: COLORS.muted, textAlign: "center" }}>We put it online.</span>
        </div>

        <div style={{
          opacity: interpolate(rightCard, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(rightCard, [0, 1], [30, 0])}px)`,
          width: 360, padding: "40px 36px", borderRadius: 24,
          background: "rgba(0,144,255,0.08)", border: `2px solid ${COLORS.accent}`,
          boxShadow: "0 0 40px rgba(0,144,255,0.15)",
          display: "flex", flexDirection: "column", alignItems: "center", gap: 16,
        }}>
          <svg width={56} height={56} viewBox="0 0 56 56">
            <circle cx={28} cy={28} r={28} fill={COLORS.accent} />
            <path d="M 18 18 L 38 38 M 38 18 L 18 38" fill="none" stroke="#FFFFFF" strokeWidth={4} strokeLinecap="round" />
          </svg>
          <span style={{ fontSize: 28, fontWeight: 800, color: COLORS.accent }}>Don't like it?</span>
          <span style={{ fontSize: 20, color: COLORS.muted, textAlign: "center" }}>You pay nothing. Zero.</span>
        </div>
      </div>

      <div style={{
        opacity: interpolate(bottomText, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(bottomText, [0, 1], [20, 0])}px)`,
        marginTop: 50, fontSize: 22, color: COLORS.muted, textAlign: "center",
        fontWeight: 600,
      }}>
        Zero risks. Zero obligations. Always.
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  Fade wrapper                                                       */
/* ------------------------------------------------------------------ */
const FadeWrapper: React.FC<{ children: React.ReactNode; durationInFrames: number }> = ({ children, durationInFrames }) => {
  const frame = useCurrentFrame();
  const FADE = 12;
  const fadeIn = interpolate(frame, [0, FADE], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - FADE, durationInFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: Math.min(fadeIn, fadeOut) }}>
      {children}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  MAIN COMPOSITION: 18 seconds, 540 frames at 30fps                 */
/* ------------------------------------------------------------------ */
export const HeroTutorialVideoENComposition: React.FC = () => {
  const S1 = 120;
  const S2 = 120;
  const S3 = 135;
  const S4 = 120;

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <Sequence from={0} durationInFrames={S1} premountFor={30}>
        <FadeWrapper durationInFrames={S1}>
          <Scene1_ContactUs />
        </FadeWrapper>
      </Sequence>
      <Sequence from={S1} durationInFrames={S2} premountFor={30}>
        <FadeWrapper durationInFrames={S2}>
          <Scene2_WeWork />
        </FadeWrapper>
      </Sequence>
      <Sequence from={S1 + S2} durationInFrames={S3} premountFor={30}>
        <FadeWrapper durationInFrames={S3}>
          <Scene3_SiteReady />
        </FadeWrapper>
      </Sequence>
      <Sequence from={S1 + S2 + S3} durationInFrames={S4} premountFor={30}>
        <FadeWrapper durationInFrames={S4}>
          <Scene4_Decision />
        </FadeWrapper>
      </Sequence>
    </AbsoluteFill>
  );
};

export const HERO_TUTORIAL_VIDEO_EN_CONFIG = {
  id: "HeroTutorialVideoEN",
  fps: 30,
  durationInFrames: 540,
  width: 1920,
  height: 1080,
};
