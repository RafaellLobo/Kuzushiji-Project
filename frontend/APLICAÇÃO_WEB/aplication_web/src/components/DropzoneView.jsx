import { Upload, Camera, Image as ImageIcon } from "lucide-react";
import brushStroke from "../assets/brush-stroke.png";

const DropzoneView = ({
  state,
  onDrop,
  onDragOver,
  onDragLeave,
  fileInputRef,
  onFileChange,
  onStartCamera
}) => {
  return (
    <>
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
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
          onClick={onStartCamera}
          className="flex items-center justify-center gap-3 px-6 py-3 bg-transparent text-foreground border border-gold font-display rounded-none hover:bg-gold/10 transition-all duration-300 shadow-md"
        >
          <Camera className="w-5 h-5" /> Use Camera
        </button>
      </div>

      <input 
        ref={fileInputRef} 
        type="file" 
        accept="image/jpeg,image/png,image/jpg" 
        className="hidden" 
        onChange={onFileChange} 
      />
    </>
  );
};

export default DropzoneView;