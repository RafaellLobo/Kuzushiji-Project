import SakuraAnimation from "./components/SakuraAnimation";
import UploadArea from "./components/UploadArea";

import washiTexture from "./assets/washi-texture.jpg"; 

function App() {
  return (
    <div
      className="relative min-h-screen flex flex-col bg-stone-200"
      style={{

        backgroundImage: `url(${washiTexture})`, 
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div className="absolute inset-0 bg-background/20"></div>
      
      <SakuraAnimation />

      
      <header className="relative z-10 text-center pt-12 sm:pt-16 pb-6 px-4">
        <h1 className="font-display text-4xl sm:text-5xl md:text-6xl text-foreground tracking-wide mb-2">
          <span className="text-primary">崩</span>し字認識
        </h1>

        <h2 className="font-display text-2xl sm:text-3xl text-foreground/90 mb-3">
          Kuzushiji Recognition
        </h2>

        <p className="text-muted-foreground text-sm sm:text-base max-w-md mx-auto">
          Upload or capture ancient Japanese text from the Edo period
        </p>

        <div className="mt-6 flex justify-center">
          <svg width="200" height="20" viewBox="0 0 200 20" className="opacity-30">
            {[0, 25, 50, 75, 100, 125, 150, 175].map((x) => (
              <path
                key={x}
                d={`M${x},20 Q${x + 12.5},0 ${x + 25},20`}
                fill="none"
                stroke="hsl(var(--gold))"
                strokeWidth="1.5"
              />
            ))}
          </svg>
        </div>
      </header>

      
      <main className="relative z-10 flex-1 flex items-start justify-center pb-12 sm:pb-16">
        <UploadArea />
      </main>

      <footer className="relative z-10 text-center py-6 px-4 border-t border-border/40">
        <p className="text-xs text-muted-foreground font-display">
          古文書 · Kuzushiji Recognition · Edo Period Script Analysis
        </p>
      </footer>
    </div>
  );
}

export default App;