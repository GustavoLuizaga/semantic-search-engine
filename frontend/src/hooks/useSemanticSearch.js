import { useState, useRef, useEffect } from "react";
import { searchQuery, checkOfflineStatus } from "../services/search-service";
import { translations } from "../utils/translations";

export function useSemanticSearch() {
  const inputRef = useRef(null);
  
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [source, setSource] = useState("local");
  const [language, setLanguage] = useState("es");
  
  // Nuevos estados para el modo offline
  const [mode, setMode] = useState("online");
  const [offlineAvailable, setOfflineAvailable] = useState(false);

  // Verificamos si Fuseki está disponible al cargar la app
  useEffect(() => {
    const verifyOffline = async () => {
      const isAvailable = await checkOfflineStatus();
      setOfflineAvailable(isAvailable);
      // Si no está disponible, forzamos el modo online por seguridad
      if (!isAvailable) setMode("online");
    };
    verifyOffline();
  }, []);

  const handleSearch = async (e) => {
    const t = translations[language] || translations.es;
    e.preventDefault();

    const query = inputRef.current?.value?.trim();

    if (!query) return;

    setIsLoading(true);
    setError(null);

    try {
      // Pasamos el mode a la petición
      const searchResults = await searchQuery(query, source, language, mode);
      setResults(searchResults);
    } catch (err) {
      console.error(err);
      setResults(null);

      if (err.name === "TypeError") {
        setError(t.errorBackend);
      } else {
        setError(t.errorGeneric);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
    inputRef,
    results,
    isLoading,
    error,
    handleSearch,
    source,
    setSource,
    language,
    setLanguage,
    // Exportamos las nuevas propiedades
    mode,
    setMode,
    offlineAvailable
  };
}