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
      console.log("Translation response status:", response.status);
      console.log("Translation response body:", data);

      if (response.ok && data.success) {
        setIsTranslating(false);
        return data.data;
      }

      if (response.ok && data.success === false) {
        const errorCode = data?.error?.code ?? "TRANSLATION_ERROR";
        const errorMessage =
          errorCode === "NO_KANJI_FOUND"
            ? "Nenhum kanji foi detectado na imagem. Por favor, tente novamente."
            : data?.error?.message ?? "Ocorreu um erro ao analisar a imagem.";

        setError({
          code: errorCode,
          message: errorMessage,
        });
        setIsTranslating(false);
        return null;
      }

      setError({
        code: data?.error?.code ?? "API_ERROR",
        message: data?.error?.message ?? "Ocorreu um erro ao analisar a imagem.",
      });
      setIsTranslating(false);
      return null;
    } catch (err) {
      console.error("Erro de conexão:", err);
      setError({
        code: "CONNECTION_ERROR",
        message: "Não foi possível conectar ao servidor. Verifique se a API está rodando.",
      });
      setIsTranslating(false);
      return null;
    }
  };

  return { translateImage, isTranslating, error };
};
