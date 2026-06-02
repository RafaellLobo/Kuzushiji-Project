import { useState, useRef, useEffect, useCallback } from "react";

export const useCamera = (onCapture) => {
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const startCamera = useCallback(() => {
    setCameraError(null);
    setIsCameraOpen(true);
  }, []); 

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraError(null);
    setIsCameraOpen(false);
  }, []);

  const capturePhoto = useCallback(() => {
    if (videoRef.current) {
      const { videoWidth, videoHeight } = videoRef.current;
      if (!videoWidth || !videoHeight) return;

      const canvas = document.createElement("canvas");
      canvas.width = videoWidth;
      canvas.height = videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
          stopCamera();
          if (onCapture) onCapture(file);
        }
      }, "image/jpeg", 0.95);
    }
  }, [onCapture, stopCamera]);

  useEffect(() => {
    const enableVideoStream = async () => {
      if (isCameraOpen && videoRef.current) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: {
              facingMode: { ideal: "environment" },
              width: { ideal: 1280 },
              height: { ideal: 720 },
            },
          });

          streamRef.current = stream;
          videoRef.current.srcObject = stream;

          videoRef.current.onloadedmetadata = () => {
            videoRef.current.play().catch((e) => console.error("Video playback error:", e));
          };
        } catch (err) {
          console.error("Camera connection error:", err);
          setCameraError("Could not start the camera. Check browser permission or whether another app is already using it.");
          setIsCameraOpen(false);
        }
      }
    };

    enableVideoStream();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, [isCameraOpen]);

  return {
    isCameraOpen,
    cameraError,
    videoRef,
    startCamera,
    stopCamera,
    capturePhoto,
  };
};
