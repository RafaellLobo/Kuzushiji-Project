import { useEffect, useState } from "react";

const SakuraAnimation = () => {
  const [petals, setPetals] = useState([]);

  useEffect(() => {
    const generated = Array.from({ length: 18 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      size: 8 + Math.random() * 14,
      duration: 8 + Math.random() * 12,
      delay: Math.random() * 15,
      opacity: 0.15 + Math.random() * 0.25,
    }));
    setPetals(generated);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {petals.map((p) => (
        <div
          key={p.id}
          className="absolute animate-sakura-fall"
          style={{
            left: `${p.left}%`,
            top: "-20px",
            width: p.size,
            height: p.size,
            animationDuration: `${p.duration}s`,
            animationDelay: `${p.delay}s`,
            opacity: p.opacity,
          }}
        >
          <svg viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="15" cy="10" rx="6" ry="10" fill="hsl(350, 60%, 75%)" transform="rotate(0 15 15)" />
            <ellipse cx="15" cy="10" rx="6" ry="10" fill="hsl(350, 55%, 80%)" transform="rotate(72 15 15)" />
            <ellipse cx="15" cy="10" rx="6" ry="10" fill="hsl(350, 60%, 75%)" transform="rotate(144 15 15)" />
            <ellipse cx="15" cy="10" rx="6" ry="10" fill="hsl(350, 55%, 80%)" transform="rotate(216 15 15)" />
            <ellipse cx="15" cy="10" rx="6" ry="10" fill="hsl(350, 60%, 75%)" transform="rotate(288 15 15)" />
            <circle cx="15" cy="15" r="3" fill="hsl(40, 60%, 70%)" />
          </svg>
        </div>
      ))}
    </div>
  );
};

export default SakuraAnimation;