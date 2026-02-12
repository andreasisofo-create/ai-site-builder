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

const StarIcon = ({ filled }: { filled: boolean }) => (
  <svg width={24} height={24} viewBox="0 0 24 24">
    <path
      d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
      fill={filled ? "#f59e0b" : "#e2e8f0"}
    />
  </svg>
);

export const TestimonialsVideoComposition = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });

  const testimonials = [
    {
      quote: "Il sito del mio ristorante e stato pronto in meno di un minuto. Incredibile!",
      author: "Marco Rossi",
      role: "Ristorante Da Mario",
      stars: 5,
      delay: 20,
    },
    {
      quote: "Finalmente un tool che capisce davvero il design. I miei clienti sono entusiasti.",
      author: "Laura Bianchi",
      role: "Agenzia Creativa",
      stars: 5,
      delay: 60,
    },
    {
      quote: "Ho risparmiato settimane di lavoro. Le animazioni GSAP sono professionali.",
      author: "Alessandro Verdi",
      role: "Startup SaaS",
      stars: 5,
      delay: 100,
    },
    {
      quote: "Il miglior investimento per la mia attivita. Sito elegante e veloce.",
      author: "Giulia Moretti",
      role: "E-commerce Fashion",
      stars: 4,
      delay: 140,
    },
    {
      quote: "Dall'idea al sito online in 3 minuti. Non potevo chiedere di meglio.",
      author: "Francesco Conti",
      role: "Consulente Freelance",
      stars: 5,
      delay: 180,
    },
  ];

  // Determine which testimonial is currently "active" (centered)
  const activeIndex = interpolate(frame, [0, 280], [0, testimonials.length - 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "#ffffff",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
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

      <GradientOrb color="rgba(59,130,246,0.06)" size={500} x="5%" y="15%" phaseOffset={0} />
      <GradientOrb color="rgba(124,58,237,0.05)" size={400} x="75%" y="55%" phaseOffset={50} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 48,
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
          }}
        >
          <div
            style={{
              display: "inline-flex",
              padding: "6px 16px",
              borderRadius: 20,
              background: "rgba(245,158,11,0.08)",
              border: "1px solid rgba(245,158,11,0.15)",
              color: "#d97706",
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: 1.5,
              marginBottom: 16,
            }}
          >
            TESTIMONIANZE
          </div>
          <h2
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: "#0c1222",
              lineHeight: 1.2,
            }}
          >
            Cosa dicono i{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              nostri clienti
            </span>
          </h2>
        </div>

        {/* Testimonial cards sliding from sides */}
        <div style={{ width: "100%", position: "relative", height: 320 }}>
          {testimonials.map((t, i) => {
            const cardEnter = spring({
              frame: frame - t.delay,
              fps,
              config: { damping: 14, stiffness: 80 },
            });

            // Slide from left for even, right for odd
            const slideDirection = i % 2 === 0 ? -1 : 1;
            const slideX = interpolate(cardEnter, [0, 1], [slideDirection * 400, 0]);
            const cardOpacity = interpolate(cardEnter, [0, 1], [0, 1]);

            // Scale down when not active
            const distFromActive = Math.abs(activeIndex - i);
            const scale = interpolate(distFromActive, [0, 1, 2], [1, 0.92, 0.85], {
              extrapolateRight: "clamp",
            });
            const cardZIndex = 10 - Math.round(distFromActive);

            // Position cards in a staggered layout
            const xOffset = (i - activeIndex) * 280;
            const yOffset = Math.abs(i - activeIndex) * 20;

            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: "50%",
                  top: "50%",
                  width: 420,
                  transform: `translate(calc(-50% + ${xOffset + slideX}px), calc(-50% + ${yOffset}px)) scale(${scale * interpolate(cardEnter, [0, 1], [0.8, 1])})`,
                  opacity: cardOpacity * interpolate(distFromActive, [0, 2, 3], [1, 0.5, 0], { extrapolateRight: "clamp" }),
                  zIndex: cardZIndex,
                  padding: "32px 28px",
                  borderRadius: 20,
                  background: "#ffffff",
                  border: "1px solid #e2e8f0",
                  boxShadow: distFromActive < 1
                    ? "0 20px 60px rgba(0,0,0,0.08), 0 0 20px rgba(99,102,241,0.06)"
                    : "0 8px 30px rgba(0,0,0,0.04)",
                }}
              >
                {/* Stars */}
                <div style={{ display: "flex", gap: 4, marginBottom: 20 }}>
                  {Array.from({ length: 5 }, (_, si) => (
                    <StarIcon key={si} filled={si < t.stars} />
                  ))}
                </div>

                {/* Quote */}
                <p
                  style={{
                    fontSize: 18,
                    color: "#1e293b",
                    lineHeight: 1.6,
                    marginBottom: 24,
                    fontStyle: "italic",
                  }}
                >
                  "{t.quote}"
                </p>

                {/* Author */}
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: "50%",
                      background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "white",
                      fontSize: 18,
                      fontWeight: 700,
                    }}
                  >
                    {t.author.charAt(0)}
                  </div>
                  <div>
                    <div style={{ fontSize: 16, fontWeight: 700, color: "#3b82f6" }}>
                      {t.author}
                    </div>
                    <div style={{ fontSize: 13, color: "#94a3b8" }}>
                      {t.role}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const TESTIMONIALS_VIDEO_CONFIG = {
  id: "TestimonialsVideo",
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
};
