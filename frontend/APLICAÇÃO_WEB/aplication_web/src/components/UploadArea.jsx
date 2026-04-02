import { useCamera } from "../hooks/useCamera";
import { useTranslation } from "../hooks/useTranslation";
import { useState, useRef, useCallback, useEffect } from "react";
import { Upload, Camera, Image as ImageIcon, RotateCcw, ArrowRight, Languages, X } from "lucide-react";
import brushStroke from "../assets/brush-stroke.png";

const UploadArea = () => {
  const [state, setState] = useState("idle"); 
  const [previewUrl, setPreviewUrl] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [translationData, setTranslationData] = useState(null);
  
  const fileInputRef = useRef(null);

  const handleFile = useCallback((file) => {
    if (!file.type.startsWith("image/")) return;
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setSelectedFile(file);
    setState("preview");
  }, []);

  const { isCameraOpen, videoRef, startCamera, stopCamera, capturePhoto } = useCamera(handleFile);
  const { translateImage } = useTranslation();

  const handleStartTranslation = async () => {
    if (!selectedFile) return;
    
    setState("loading"); // Mostra a tela de tinta carregando
    
    // Manda a foto pro hook e espera a mágica acontecer
    const data = await translateImage(selectedFile);

    if (data) {
      setTranslationData(data);
      setState("results_jp"); // Se deu certo, mostra o Japonês
    } else {
      alert("Erro ao traduzir. Verifique se a API está rodando.");
      setState("preview"); // Se deu erro, volta pra tela de espera
    }
  };

  const handleRevealEnglish = () => {
    setState("results_en");
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    if (state === "idle" && !isCameraOpen) setState("dragging");
  }, [state, isCameraOpen]);

  const handleDragLeave = useCallback(() => {
    if (state === "dragging") setState("idle");
  }, [state]);

  const handleFileChange = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const reset = () => {
    setPreviewUrl(null);
    setSelectedFile(null);
    setTranslationData(null);
    setState("idle");
    stopCamera();
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
          ) : state !== "idle" && state !== "dragging" ? (
            <div className="animate-fade-in">
              <div className="flex flex-col md:flex-row gap-6 md:gap-8">
                
                {/* Left: Imagem Original */}
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
                  
                  <div className="flex-1 bg-background/60 border border-border rounded-none p-5 mb-5 min-h-[200px] shadow-inner flex flex-col justify-center">
                    
                    {state === "preview" && (
                      <div className="text-center opacity-60">
                        <p className="font-display text-lg mb-2">Ready for analysis.</p>
                        <p className="text-sm">Click "Iniciar Tradução" to begin.</p>
                      </div>
                    )}

                    {(state === "results_jp" || state === "results_en") && translationData && (
                      <div className="space-y-4 animate-fade-in w-full">
                        <div>
                          <h4 className="text-sm font-bold text-deepCrimson mb-1">Kanji Detected:</h4>
                          <p className="font-display text-lg tracking-widest text-foreground">
                            {translationData.characters.map(c => c.old_kanji).join("  ")}
                          </p>
                        </div>
                        
                        <div className="pt-2 border-t border-border/50">
                          <h4 className="text-sm font-bold text-deepCrimson mb-1">Modern Japanese:</h4>
                          <p className="font-display text-foreground leading-relaxed">
                            {translationData.japanese_text}
                          </p>
                        </div>

                        {state === "results_en" && (
                          <div className="pt-2 border-t border-border/50 animate-fade-in">
                            <h4 className="text-sm font-bold text-deepCrimson mb-1">Translation (English):</h4>
                            <p className="font-display text-foreground leading-relaxed italic">
                              {translationData.english_translation}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3">
                    {state === "preview" ? (
                      <button 
                        onClick={handleStartTranslation}
                        className="w-full flex items-center justify-center gap-2 px-5 py-3 bg-deepCrimson text-white font-display text-sm rounded-none hover:bg-deepCrimson/90 transition-all shadow-md"
                      >
                        Iniciar Tradução <ArrowRight className="w-4 h-4" />
                      </button>
                    ) : (
                      <button 
                        onClick={handleRevealEnglish}
                        disabled={state === "results_en"}
                        className={`w-full flex items-center justify-center gap-2 px-5 py-3 font-display text-sm rounded-none transition-all shadow-md
                          ${state === "results_en" 
                            ? "bg-muted text-muted-foreground cursor-not-allowed border border-border" 
                            : "bg-transparent text-foreground border border-gold hover:bg-gold/10"
                          }`}
                      >
                        <Languages className="w-4 h-4" />
                        {state === "results_en" ? "Translated to English" : "Translate to English"}
                      </button>
                    )}
                  </div>

                </div>
              </div>

              <div className="flex justify-center mt-8 pt-5 border-t border-border/50">
                <button
                  onClick={reset}
                  className="flex items-center gap-2 px-5 py-2 text-muted-foreground hover:text-foreground font-display text-sm transition-colors duration-300"
                >
                  <RotateCcw className="w-4 h-4" />
                  Upload Another Document
                </button>
              </div>
            </div>
          ) : isCameraOpen ? (
            <div className="flex flex-col items-center justify-center animate-fade-in py-8">
              <h3 className="font-display text-xl mb-4 text-foreground">Capture Document</h3>
              <div className="relative w-full max-w-lg aspect-[4/3] bg-black rounded-none overflow-hidden border-4 border-border mb-6 shadow-lg">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover scale-x-[-1]" 
                />
                <div className="absolute inset-0 pointer-events-none border-[40px] border-black/30"></div>
                <div className="absolute inset-1/4 pointer-events-none border-2 border-white/50 border-dashed"></div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md justify-center">
                <button 
                  onClick={capturePhoto} 
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-deepCrimson text-white font-display rounded-none hover:bg-deepCrimson/90 shadow-md"
                >
                  <Camera className="w-5 h-5" />
                  Capture image
                </button>
                <button 
                  onClick={stopCamera} 
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-transparent text-foreground border-2 border-border font-display rounded-none hover:bg-black/5 shadow-md"
                >
                  <X className="w-5 h-5" />
                  Cancel
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
                <img src={brushStroke} alt="" className="w-48 h-auto opacity-20 animate-brush-write" loading="lazy" />
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center justify-center gap-3 px-6 py-3 bg-deepCrimson text-white font-display rounded-none hover:bg-deepCrimson/90 transition-all duration-300 shadow-md"
                >
                  <Upload className="w-5 h-5" /> Upload Image
                </button>

                <button
                  onClick={startCamera}
                  className="flex items-center justify-center gap-3 px-6 py-3 bg-transparent text-foreground border border-gold font-display rounded-none hover:bg-gold/10 transition-all duration-300 shadow-md"
                >
                  <Camera className="w-5 h-5" /> Use Camera
                </button>
              </div>

              <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/jpg" className="hidden" onChange={handleFileChange} />
            </>
          )}
        </div>
        <div className="h-3 bg-gradient-to-r from-gold/40 via-gold/70 to-gold/40 border-t border-border/50" />
      </div>
    </div>
  );
};

export default UploadArea;