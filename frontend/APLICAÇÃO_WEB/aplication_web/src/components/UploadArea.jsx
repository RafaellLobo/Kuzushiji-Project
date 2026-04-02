import { useState, useRef, useCallback } from "react";

// HOOKS
import { useCamera } from "../hooks/useCamera";
import { useTranslation } from "../hooks/useTranslation";

// VIEWS
import CameraView from "./CameraView";
import DropzoneView from "./DropzoneView";
import ResultsView from "./ResultsView";

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
    setState("loading"); 
    const data = await translateImage(selectedFile);
    if (data) {
      setTranslationData(data);
      setState("results_jp"); 
    } else {
      alert("Erro ao traduzir. Verifique se a API está rodando.");
      setState("preview"); 
    }
  };

  const handleRevealEnglish = () => setState("results_en");

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
            <ResultsView 
              state={state}
              previewUrl={previewUrl}
              translationData={translationData}
              onStartTranslation={handleStartTranslation}
              onRevealEnglish={handleRevealEnglish}
              onReset={reset}
            />
          ) : isCameraOpen ? (
            <CameraView 
              videoRef={videoRef} 
              onCapture={capturePhoto} 
              onCancel={stopCamera} 
            />
          ) : (
            <DropzoneView 
              state={state}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              fileInputRef={fileInputRef}
              onFileChange={handleFileChange}
              onStartCamera={startCamera}
            />
          )}
        </div>
        <div className="h-3 bg-gradient-to-r from-gold/40 via-gold/70 to-gold/40 border-t border-border/50" />
      </div>
    </div>
  );
};

export default UploadArea;