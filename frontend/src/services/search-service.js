
export const searchQuery = async (query) => {
    try {
        const response = await fetch("http://localhost:8000/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query }),
        });
        const result = await response.json();
        return {answer: result.answer, data: result.data};
    } catch (error) {
      //  console.error("Error al realizar la búsqueda:", error);
        return response.json();
    }
};