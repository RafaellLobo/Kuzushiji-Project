import { useState, useRef, useEffect, useCallback } from "react";

export const useCamera = (onCapture) => {
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const startCamera = useCallback(() => {
    setIsCameraOpen(true);
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsCameraOpen(false);
  }, []);

  const capturePhoto = useCallback(() => {
    if (videoRef.current) {
      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
          stopCamera();
          if (onCapture) onCapture(file); // Devolve a foto pronta pro componente pai
        }
      }, "image/jpeg", 0.9);
    }
  }, [onCapture, stopCamera]);

  useEffect(() => {
    const enableVideoStream = async () => {
      if (isCameraOpen && videoRef.current) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 1280 }, height: { ideal: 720 } }
          });
          
          streamRef.current = stream;
          videoRef.current.srcObject = stream;
          
          videoRef.current.onloadedmetadata = () => {
            videoRef.current.play().catch(e => console.error("Erro ao dar play:", e));
          };
        } catch (err) {
          console.error("Erro ao conectar câmera:", err);
          alert("Erro ao ligar a câmera. Verifique se outro app está usando ela.");
        }
      }
    };

    enableVideoStream();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, [isCameraOpen]);

  // Retornamos apenas o que o componente visual vai precisar usar
  return {
    isCameraOpen,
    videoRef,
    startCamera,
    stopCamera,
    capturePhoto
  };
};