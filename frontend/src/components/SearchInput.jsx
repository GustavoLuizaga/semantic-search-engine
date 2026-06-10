import React, { useState, useEffect } from "react";
import SourceSelector from "./SourceSelector";
import LanguageSelector from "./LanguageSelector";
import DBpediaModal from "./DBpediaModal";
import SettingsSheet from "./SettingsSheet";
import { translations } from "../utils/translations";

const GearIcon = () => (
  <svg
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
);

export default function SearchInput({
  onSubmit,
  isLoading,
  source,
  setSource,
  language,
  setLanguage,
  inputRef,
  mode,
  setMode,
  offlineAvailable,
}) {
  const t = translations[language] || translations.es;
  const [isFocused, setIsFocused] = useState(false);

  // Modal de DBpedia (desktop)
  const [showModal, setShowModal] = useState(false);
  const [tempMode, setTempMode] = useState(mode);

  // Bottom sheet (móvil)
  const [showSheet, setShowSheet] = useState(false);

  useEffect(() => {
    if (source === "dbpedia") {
      setTempMode(mode);
      setShowModal(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source]);

  const handleAccept = () => {
    setMode(tempMode);
    setShowModal(false);
  };

  return (
    <>
      {/* ── Modal DBpedia (solo desktop) ── */}
      <div className="hidden sm:block">
        <DBpediaModal
          show={showModal}
          tempMode={tempMode}
          setTempMode={setTempMode}
          offlineAvailable={offlineAvailable}
          onAccept={handleAccept}
        />
      </div>

      {/* ── Bottom Sheet (móvil) ── */}
      <div className="sm:hidden">
        <SettingsSheet
          show={showSheet}
          onClose={() => setShowSheet(false)}
          source={source}
          setSource={setSource}
          language={language}
          setLanguage={setLanguage}
          mode={mode}
          setMode={setMode}
          offlineAvailable={offlineAvailable}
        />
      </div>

      {/* ── BARRA DE BÚSQUEDA ── */}
      <section className="fixed bottom-0 left-0 right-0 z-20 bg-linear-to-t from-zinc-50 via-zinc-50/90 to-transparent dark:from-zinc-900 dark:via-zinc-900/90 pt-12 pb-6">
        <div className="max-w-3xl mx-auto px-6 w-full">
          <form
            onSubmit={onSubmit}
            className="flex items-center gap-2 sm:gap-3 w-full bg-white dark:bg-zinc-800 p-2 rounded-2xl shadow-xl border border-zinc-200 dark:border-zinc-700"
          >
            {/* ── Botón engranaje (solo móvil) ── */}
            <button
              type="button"
              onClick={() => setShowSheet(true)}
              className="sm:hidden flex items-center justify-center w-10 h-10 rounded-xl text-zinc-500 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-700 hover:text-zinc-800 dark:hover:text-zinc-200 transition-colors shrink-0"
            >
              <GearIcon />
            </button>

            <div className="flex items-center flex-1">
              {/* ── Selectores inline (solo desktop) ── */}
              <div
                className={`
                  hidden sm:flex items-center
                  transition-all duration-300 ease-in-out
                  ${
                    isFocused
                      ? "max-w-0 opacity-0 overflow-hidden pointer-events-none"
                      : "max-w-xs opacity-100 pr-2"
                  }
                `}
              >
                <div className="flex items-center gap-1 shrink-0 whitespace-nowrap">
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
                  {source === "dbpedia" && (
                    <>
                      <div className="h-5 w-px bg-zinc-200 dark:bg-zinc-700 mx-1 shrink-0" />
                      <button
                        type="button"
                        onClick={() => setShowModal(true)}
                        className="px-2 py-1.5 text-sm font-medium text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-700"
                      >
                        {mode === "online" ? "Online" : "Offline"}
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* ── Input de texto ── */}
              <div className="relative flex-1">
                <input
                  type="text"
                  ref={inputRef}
                  disabled={isLoading}
                  placeholder={t.placeholder}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  className="w-full bg-transparent py-3 px-1 sm:px-2 text-sm text-zinc-800 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none disabled:opacity-50"
                />
              </div>
            </div>

            {/* ── Botón enviar ── */}
            <button
              type="submit"
              disabled={isLoading}
              className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 text-sm font-medium py-3 px-4 sm:px-6 rounded-xl transition-all duration-200 hover:bg-zinc-800 dark:hover:bg-zinc-200 disabled:bg-zinc-400 dark:disabled:bg-zinc-700 disabled:cursor-not-allowed shrink-0"
            >
              {isLoading ? t.loading : t.send}
            </button>
          </form>
        </div>
      </section>
    </>
  );
}
