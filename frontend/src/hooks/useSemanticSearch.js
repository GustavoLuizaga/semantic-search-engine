import { useState, useRef } from "react";
import { searchQuery } from "../services/search-service";

export function useSemanticSearch() {
  const inputRef = useRef(null);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    const query = inputRef.current?.value?.trim();
    
    if (!query) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const searchResults = await searchQuery(query);
      setResults(searchResults);
    } catch (err) {
      setError("Hubo un error al realizar la búsqueda. Inténtalo de nuevo.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return { inputRef, results, isLoading, error, handleSearch };
}