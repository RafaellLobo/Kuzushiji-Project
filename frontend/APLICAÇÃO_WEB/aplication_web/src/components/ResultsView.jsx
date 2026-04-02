import { RotateCcw, ArrowRight, Languages } from "lucide-react";

const ResultsView = ({
  state,
  previewUrl,
  translationData,
  onStartTranslation,
  onRevealEnglish,
  onReset
}) => {
  return (
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

        {/* Right: Transcrição e Ações */}
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
                onClick={onStartTranslation}
                className="w-full flex items-center justify-center gap-2 px-5 py-3 bg-deepCrimson text-white font-display text-sm rounded-none hover:bg-deepCrimson/90 transition-all shadow-md"
              >
                Iniciar Tradução <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button 
                onClick={onRevealEnglish}
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
          onClick={onReset}
          className="flex items-center gap-2 px-5 py-2 text-muted-foreground hover:text-foreground font-display text-sm transition-colors duration-300"
        >
          <RotateCcw className="w-4 h-4" />
          Upload Another Document
        </button>
      </div>
    </div>
  );
};

export default ResultsView;