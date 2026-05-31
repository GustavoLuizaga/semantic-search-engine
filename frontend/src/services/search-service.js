export const searchQuery = async (query, source = "local", language = "es") => {
  const endpoint =
    source === "dbpedia"
      ? "http://localhost:8000/search/dbpedia"
      : "http://localhost:8000/search";

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        query: query, 
        language: language
       }),
    });

    const result = await response.json();

    return {
      answer: result.answer,
      data: result.data,
    };
  } catch (error) {
    throw error;
  }
};