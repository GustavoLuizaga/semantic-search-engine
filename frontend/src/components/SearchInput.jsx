import React, { useState } from "react";
import SourceSelector from "./SourceSelector";
import LanguageSelector from "./LanguageSelector";
import { translations } from "../utils/translations";

export default function SearchInput({
  onSubmit,
  isLoading,
  source,
  setSource,
  language,
  setLanguage,
  inputRef,
}) {
  const t = translations[language] || translations.es;
  const [isFocused, setIsFocused] = useState(false);

  return (
    <section className="fixed bottom-0 left-0 right-0 z-20 bg-linear-to-t from-zinc-50 via-zinc-50/90 to-transparent dark:from-zinc-900 dark:via-zinc-900/90 pt-12 pb-6">
      <div className="max-w-3xl mx-auto px-6 w-full">
        <form
          onSubmit={onSubmit}
          className="flex items-center gap-2 sm:gap-3 w-full bg-white dark:bg-zinc-800 p-2 rounded-2xl shadow-xl border border-zinc-200 dark:border-zinc-700"
        >
          <div className="flex items-center flex-1">
            <div
              className={`
                transition-all duration-300 ease-in-out flex items-center
                ${
                  isFocused
                    ? // ENFOQUE (Móvil se oculta cortando el exceso / PC se queda visible)
                      "max-w-0 opacity-0 overflow-hidden sm:max-w-62.5 sm:opacity-100 sm:mr-2 sm:overflow-visible"
                    : // SIN ENFOQUE (Visible en todos lados, con overflow libre para que salgan los menús)
                      "max-w-62.5 opacity-100 mr-2 overflow-visible"
                }
              `}
            >
              <div className="flex items-center gap-1 shrink-0 min-w-max">
                <SourceSelector
                  source={source}
                  setSource={setSource}
                  language={language}
                />
                <div className="h-5 w-px bg-zinc-200 dark:bg-zinc-700 mx-1 shrink-0" />
                <LanguageSelector
                  language={language}
                  setLanguage={setLanguage}
                />
              </div>
            </div>

            {/* Input de Texto */}
            <div className="relative flex-1">
              <input
                type="text"
                ref={inputRef}
                disabled={isLoading}
                placeholder={t.placeholder}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                className="w-full bg-transparent py-3 px-1 sm:px-2 text-sm
                           text-zinc-800 dark:text-zinc-100
                           placeholder-zinc-400 dark:placeholder-zinc-500
                           focus:outline-none disabled:opacity-50"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 text-sm font-medium py-3 px-4 sm:px-6 rounded-xl
                       transition-all duration-200
                       hover:bg-zinc-800 dark:hover:bg-zinc-200
                       disabled:bg-zinc-400 dark:disabled:bg-zinc-700
                       disabled:cursor-not-allowed shrink-0"
          >
            {isLoading ? t.loading : t.send}
          </button>
        </form>
      </div>
    </section>
  );
}
