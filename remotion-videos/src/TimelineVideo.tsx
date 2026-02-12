import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
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

const milestones = [
  {
    year: "2024",
    title: "Lancio Piattaforma",
    description: "Prima versione con 5 template e generazione AI base",
    icon: "rocket",
    delay: 20,
  },
  {
    year: "Q2 2024",
    title: "Motore GSAP",
    description: "29 animazioni professionali integrate automaticamente",
    icon: "sparkle",
    delay: 55,
  },
  {
    year: "Q4 2024",
    title: "19 Template Premium",
    description: "8 categorie: ristoranti, SaaS, portfolio, e-commerce e altro",
    icon: "grid",
    delay: 90,
  },
  {
    year: "Q1 2025",
    title: "AI Avanzata",
    description: "ChromaDB con 105 pattern creativi per design unico",
    icon: "brain",
    delay: 125,
  },
  {
    year: "2025",
    title: "2.800+ Siti Generati",
    description: "Community in crescita con valutazione 4.8/5 stelle",
    icon: "trophy",
    delay: 160,
  },
];

const MilestoneIcon = ({ icon }: { icon: string }) => {
  const iconPaths: Record<string, JSX.Element> = {
    rocket: (
      <path
        d="M6 15L3 12M6 15L9 12M6 15V3M6 3C6 3 8 5 12 5C16 5 18 3 18 3M18 3V15M18 15L21 12M18 15L15 12"
        fill="none"
        stroke="white"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
    sparkle: (
      <path
        d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z"
        fill="white"
      />
    ),
    grid: (
      <>
        <rect x={3} y={3} width={7} height={7} rx={1} fill="white" />
        <rect x={14} y={3} width={7} height={7} rx={1} fill="white" />
        <rect x={3} y={14} width={7} height={7} rx={1} fill="white" />
        <rect x={14} y={14} width={7} height={7} rx={1} fill="white" />
      </>
    ),
    brain: (
      <path
        d="M12 2C8 2 5 5 5 8C5 10 6 11.5 7.5 12.5L7 22H17L16.5 12.5C18 11.5 19 10 19 8C19 5 16 2 12 2Z"
        fill="white"
      />
    ),
    trophy: (
      <path
        d="M8 21H16M12 17V21M6 3H18V7C18 10.3 15.3 13 12 13C8.7 13 6 10.3 6 7V3ZM6 5H3V7C3 8.7 4.3 10 6 10V5ZM18 5H21V7C21 8.7 19.7 10 18 10V5Z"
        fill="none"
        stroke="white"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  };

  return (
    <svg width={24} height={24} viewBox="0 0 24 24">
      {iconPaths[icon] || iconPaths.sparkle}
    </svg>
  );
};

export const TimelineVideoComposition = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });

  // Timeline line draw progress
  const lineProgress = interpolate(frame, [15, 240], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const timelineTop = 340;
  const timelineHeight = 560;

  return (
    <AbsoluteFill
      style={{
        background: "#ffffff",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-start",
        paddingTop: 60,
      }}
    >
      {/* Grid background */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage:
            "linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <GradientOrb color="rgba(59,130,246,0.06)" size={500} x="5%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(124,58,237,0.05)" size={400} x="80%" y="50%" phaseOffset={50} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          width: "100%",
          maxWidth: 1200,
        }}
      >
        {/* Title */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
            textAlign: "center",
            marginBottom: 60,
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
            IL NOSTRO PERCORSO
          </div>
          <h2
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: "#0c1222",
              lineHeight: 1.2,
            }}
          >
            Come siamo{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              cresciuti
            </span>
          </h2>
        </div>

        {/* Timeline container */}
        <div
          style={{
            position: "relative",
            width: "100%",
            height: timelineHeight,
          }}
        >
          {/* Vertical timeline line */}
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: 0,
              width: 3,
              height: timelineHeight * lineProgress,
              background: "linear-gradient(180deg, #3b82f6, #7c3aed)",
              borderRadius: 2,
              transform: "translateX(-50%)",
              boxShadow: "0 0 12px rgba(59,130,246,0.3)",
            }}
          />

          {/* Milestones */}
          {milestones.map((milestone, i) => {
            const dotEnter = spring({
              frame: frame - milestone.delay,
              fps,
              config: { damping: 10, stiffness: 100 },
            });

            const cardEnter = spring({
              frame: frame - milestone.delay - 8,
              fps,
              config: { damping: 14, stiffness: 80 },
            });

            const isLeft = i % 2 === 0;
            const yPos = (i / (milestones.length - 1)) * (timelineHeight - 40);

            // Pulse effect on dot
            const pulse = interpolate(
              Math.sin((frame - milestone.delay) * 0.08),
              [-1, 1],
              [0.9, 1.1]
            );
            const dotScale = frame > milestone.delay ? pulse : 0;

            return (
              <div key={milestone.title}>
                {/* Center dot */}
                <div
                  style={{
                    position: "absolute",
                    left: "50%",
                    top: yPos,
                    transform: `translate(-50%, -50%) scale(${interpolate(dotEnter, [0, 1], [0, 1]) * dotScale})`,
                    width: 48,
                    height: 48,
                    borderRadius: "50%",
                    background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: "0 4px 20px rgba(59,130,246,0.3)",
                    zIndex: 2,
                  }}
                >
                  <MilestoneIcon icon={milestone.icon} />
                </div>

                {/* Card */}
                <div
                  style={{
                    position: "absolute",
                    top: yPos,
                    transform: `translateY(-50%) translateX(${interpolate(cardEnter, [0, 1], [isLeft ? -60 : 60, 0])}px)`,
                    opacity: interpolate(cardEnter, [0, 1], [0, 1]),
                    ...(isLeft
                      ? { right: "calc(50% + 48px)" }
                      : { left: "calc(50% + 48px)" }),
                    width: 400,
                    padding: "24px 28px",
                    borderRadius: 16,
                    background: "#ffffff",
                    border: "1px solid #e2e8f0",
                    boxShadow: "0 8px 30px rgba(0,0,0,0.06)",
                    textAlign: isLeft ? "right" : "left",
                  }}
                >
                  {/* Year badge */}
                  <div
                    style={{
                      display: "inline-flex",
                      padding: "3px 10px",
                      borderRadius: 8,
                      background: "rgba(59,130,246,0.08)",
                      color: "#3b82f6",
                      fontSize: 12,
                      fontWeight: 700,
                      marginBottom: 10,
                    }}
                  >
                    {milestone.year}
                  </div>

                  {/* Title */}
                  <div
                    style={{
                      fontSize: 20,
                      fontWeight: 800,
                      color: "#0c1222",
                      marginBottom: 6,
                      lineHeight: 1.3,
                    }}
                  >
                    {milestone.title}
                  </div>

                  {/* Description */}
                  <div
                    style={{
                      fontSize: 14,
                      color: "#64748b",
                      lineHeight: 1.5,
                    }}
                  >
                    {milestone.description}
                  </div>

                  {/* Connector line from card to dot */}
                  <div
                    style={{
                      position: "absolute",
                      top: "50%",
                      ...(isLeft
                        ? { right: -24, width: 24 }
                        : { left: -24, width: 24 }),
                      height: 2,
                      background: "linear-gradient(90deg, #e2e8f0, #3b82f6)",
                      transform: "translateY(-50%)",
                      opacity: interpolate(cardEnter, [0, 1], [0, 0.6]),
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const TIMELINE_VIDEO_CONFIG = {
  id: "TimelineVideo",
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
};
