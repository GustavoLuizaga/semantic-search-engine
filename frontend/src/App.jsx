import { useState, useRef } from "react";
import { searchQuery } from "./services/search-service";

function App() {
  const inputRef = useRef();
  const [results, setResults] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const query = inputRef.current.value;
    const searchResults = await searchQuery(query);
    setResults(searchResults);
    console.log(searchResults.answer);
  }

  return (
    <div className="flex flex-col justify-center items-center">
      <h1 className="mt-8 text-3xl text-center font-bold">
        Buscador Semantico 
      </h1>
      <section className="mt-8">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            ref={inputRef}
            className="border border-gray-300 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500s"
            placeholder="Escribe tu pregunta .."
          />
          <button 
            type="submit"
            className="ml-2 bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Buscar
          </button>
        </form>
        <section className="mt-4">
          {
            results.answer && (
              <p>{results.answer}</p>
            )
          }
        </section>
      </section>
    </div>
  );
}

export default App;
