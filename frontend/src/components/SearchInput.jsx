import SourceSelector from "./SourceSelector";
import LanguageSelector from "./LanguageSelector";

export default function SearchInput({
  onSubmit,
  isLoading,
  source,
  setSource,
  language,
  setLanguage,
  inputRef,
}) {
  return (
    <section className="w-full sticky bottom-6">
      <form
        onSubmit={onSubmit}
        className="flex gap-3 w-full bg-white dark:bg-zinc-800 p-2 rounded-2xl shadow-lg border border-zinc-200 dark:border-zinc-700"
      >
        <div className="flex items-center gap-2 flex-1">
          <SourceSelector source={source} setSource={setSource} />
          <LanguageSelector language={language} setLanguage={setLanguage} />
          <div className="relative flex-1">
            <input
              type="text"
              ref={inputRef}
              disabled={isLoading}
              placeholder="Escribe tu pregunta..."
              className="w-full bg-transparent py-3 px-4 text-sm
                         text-zinc-800 dark:text-zinc-100
                         placeholder-zinc-400 dark:placeholder-zinc-500
                         focus:outline-none disabled:opacity-50"
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 text-sm font-medium py-3 px-6 rounded-xl
                     transition-all duration-200
                     hover:bg-zinc-800 dark:hover:bg-zinc-200
                     disabled:bg-zinc-400 dark:disabled:bg-zinc-700
                     disabled:cursor-not-allowed"
        >
          {isLoading ? "..." : "Enviar"}
        </button>
      </form>
    </section>
  );
}
