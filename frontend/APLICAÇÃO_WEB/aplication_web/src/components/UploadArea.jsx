import { useState, useRef, useCallback } from "react";
import { Upload, Camera, Image as ImageIcon, RotateCcw } from "lucide-react";
import brushStroke from "../assets/brush-stroke.png";


const PLACEHOLDER_TRANSCRIPTION = `春の夜の夢ばかりなる手枕に
かひなく立たむ名こそ惜しけれ

花の色は移りにけりないたづらに
わが身世にふるながめせしまに

めぐり逢ひて見しやそれとも分かぬ間に
雲隠れにし夜半の月かな`;

const UploadArea = () => {
  const [state, setState] = useState("idle");
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleFile = useCallback((file) => {
    if (!file.type.startsWith("image/")) return;
    setState("loading");
    const url = URL.createObjectURL(file);
    setTimeout(() => {
      setPreviewUrl(url);
      setState("results");
    }, 2500);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setState("idle");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setState("dragging");
  }, []);

  const handleDragLeave = useCallback(() => {
    setState("idle");
  }, []);

  const handleFileChange = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const reset = () => {
    setPreviewUrl(null);
    setState("idle");
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4">

      <div className="relative bg-card backdrop-blur-sm border-4 border-border rounded-none shadow-xl overflow-hidden">

        <div className="h-3 bg-gradient-to-r from-gold/40 via-gold/70 to-gold/40 border-b border-border/50" />

        <div className="p-6 sm:p-10">
          {state === "loading" ? (
            <div className="flex flex-col items-center justify-center py-16 animate-fade-in">
              <div className="relative w-24 h-24 mb-6">
                <div className="absolute inset-0 rounded-full bg-deepCrimson/10 animate-ink-spread" />
                <div className="absolute inset-2 rounded-full bg-deepCrimson/15 animate-ink-spread" style={{ animationDelay: "0.5s" }} />
                <div className="absolute inset-4 rounded-full bg-deepCrimson/20 animate-ink-spread" style={{ animationDelay: "1s" }} />
              </div>
              <p className="font-display text-lg text-foreground">Analyzing ancient writing...</p>
              <p className="text-muted-foreground text-sm mt-2">墨跡を解読中</p>
            </div>
          ) : state === "results" && previewUrl ? (
            <div className="animate-fade-in">

              <div className="flex flex-col md:flex-row gap-6 md:gap-8">
                
                <div className="md:w-1/2 flex flex-col items-center">
                  <div className="w-full border-2 border-border rounded-none p-2 bg-background/50 shadow-md">
                    <img
                      src={previewUrl}
                      alt="Uploaded kuzushiji text"
                      className="w-full h-auto max-h-96 object-contain rounded-none"
                    />
                  </div>
                  <p className="font-display text-xs text-muted-foreground mt-3">原文画像 · Original Document</p>
                </div>

                <div className="md:w-1/2 flex flex-col">
                  <h3 className="font-display text-lg text-foreground mb-3 border-b border-border pb-2">
                    <span className="text-deepCrimson">解読</span>結果 · Transcription
                  </h3>
                  
                  <div className="flex-1 bg-background/60 border border-border rounded-none p-5 mb-5 min-h-[200px] shadow-inner overflow-auto">
                    <p className="font-display text-foreground leading-relaxed whitespace-pre-line text-sm sm:text-base">
                      {PLACEHOLDER_TRANSCRIPTION}
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3">
                    <button className="flex-1 px-5 py-2.5 bg-deepCrimson text-white font-display text-sm rounded-none hover:bg-deepCrimson/90 transition-all duration-300 hover:scale-105 shadow-md">
                      Translate to English
                    </button>
                    <button className="flex-1 px-5 py-2.5 bg-transparent text-foreground border border-gold font-display text-sm rounded-none hover:bg-gold/10 transition-all duration-300 hover:scale-105 shadow-md">
                      Botão de mandar para API
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex justify-center mt-8 pt-5 border-t border-border/50">
                <button
                  onClick={reset}
                  className="flex items-center gap-2 px-5 py-2 text-muted-foreground hover:text-foreground font-display text-sm transition-colors duration-300"
                >
                  <RotateCcw className="w-4 h-4" />
                  Upload Another
                </button>
              </div>
            </div>
          ) : (
            <>

              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                className={`border-2 border-dotted rounded-none p-8 sm:p-12 text-center transition-all duration-300 cursor-pointer group
                  ${state === "dragging"
                    ? "border-deepCrimson bg-deepCrimson/5 scale-[1.02]"
                    : "border-gold/50 hover:border-gold"
                  }`}
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="flex flex-col items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-border flex items-center justify-center group-hover:bg-gold/20 transition-colors duration-300">
                    <ImageIcon className="w-8 h-8 text-gold group-hover:text-gold/80 transition-colors" />
                  </div>
                  <div>
                    <p className="font-display text-lg text-foreground/80 mb-1">
                      Drop the image of the ancient document here.
                    </p>
                    <p className="text-sm text-muted-foreground/80">
                      古文書の画像をここにドロップ
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-center my-6">
                <img
                  src={brushStroke}
                  alt=""
                  className="w-48 h-auto opacity-20 animate-brush-write"
                  loading="lazy"
                />
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center justify-center gap-3 px-6 py-3 bg-deepCrimson text-white font-display rounded-none hover:bg-deepCrimson/90 transition-all duration-300 hover:scale-105 shadow-md"
                >
                  <Upload className="w-5 h-5" />
                  Upload Image
                </button>
                <button
                  onClick={() => cameraInputRef.current?.click()}
                  className="flex items-center justify-center gap-3 px-6 py-3 bg-transparent text-foreground border border-gold font-display rounded-none hover:bg-gold/10 transition-all duration-300 hover:scale-105 shadow-md"
                >
                  <Camera className="w-5 h-5" />
                  Use Camera
                </button>
              </div>

              <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/jpg" className="hidden" onChange={handleFileChange} />
              <input ref={cameraInputRef} type="file" accept="image/jpeg,image/png,image/jpg" capture="environment" className="hidden" onChange={handleFileChange} />
            </>
          )}
        </div>

        <div className="h-3 bg-gradient-to-r from-gold/40 via-gold/70 to-gold/40 border-t border-border/50" />
      </div>
    </div>
  );
};

export default UploadArea;