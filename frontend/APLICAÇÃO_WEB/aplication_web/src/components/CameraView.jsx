import { Camera, X } from "lucide-react";

// O componente recebe as funções e a referência do vídeo como "props" (parâmetros)
const CameraView = ({ videoRef, onCapture, onCancel }) => {
  return (
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
          onClick={onCapture} 
          className="flex items-center justify-center gap-2 px-6 py-3 bg-deepCrimson text-white font-display rounded-none hover:bg-deepCrimson/90 shadow-md"
        >
          <Camera className="w-5 h-5" />
          Capture image
        </button>
        <button 
          onClick={onCancel} 
          className="flex items-center justify-center gap-2 px-6 py-3 bg-transparent text-foreground border-2 border-border font-display rounded-none hover:bg-black/5 shadow-md"
        >
          <X className="w-5 h-5" />
          Cancel
        </button>
      </div>
    </div>
  );
};

export default CameraView;