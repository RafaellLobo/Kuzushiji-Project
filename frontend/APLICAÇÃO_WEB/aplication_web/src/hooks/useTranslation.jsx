import { useState } from "react";

export const useTranslation = () => {
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState(null);

  const translateImage = async (file) => {
    if (!file) return null;

    setIsTranslating(true);
    setError(null);

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch("http://localhost:8000/translate", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setIsTranslating(false);
        return data.data; // Retorna os dados prontinhos (kanji, jp, en)
      } else {
        setError("Ocorreu um erro ao analisar a imagem na API.");
        setIsTranslating(false);
        return null;
      }
    } catch (err) {
      console.error("Erro de conexão:", err);
      setError("Não foi possível conectar ao servidor. O back-end está rodando?");
      setIsTranslating(false);
      return null;
    }
  };

  return { translateImage, isTranslating, error };
};