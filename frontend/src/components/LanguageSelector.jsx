import React, { useState, useRef, useEffect } from "react";

const CheckIcon = () => (
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
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const ChevronDownIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="6 9 12 15 18 9"></polyline>
  </svg>
);

const SpanishIcon = () => (
  <svg width="20" height="14" viewBox="0 0 20 14" fill="none" aria-hidden="true">
    <rect width="20" height="14" rx="3" fill="#D52B1E" />
    <rect y="4.67" width="20" height="4.66" fill="#F9D616" />
    <rect y="9.34" width="20" height="4.66" fill="#007A33" />
  </svg>
);

const EnglishIcon = () => (
  <svg width="20" height="14" viewBox="0 0 20 14" fill="none" aria-hidden="true">
    <rect width="20" height="14" rx="3" fill="#B22234" />
    <path d="M0 2H20M0 4H20M0 6H20M0 8H20M0 10H20M0 12H20" stroke="#FFFFFF" strokeWidth="1" />
    <rect width="8.6" height="7.6" rx="2.4" fill="#3C3B6E" />
  </svg>
);

const FrenchIcon = () => (
  <svg width="20" height="14" viewBox="0 0 20 14" fill="none" aria-hidden="true">
    <rect width="20" height="14" rx="3" fill="#FFFFFF" />
    <rect width="6.67" height="14" rx="3" fill="#0055A4" />
    <rect x="13.33" width="6.67" height="14" rx="3" fill="#EF4135" />
  </svg>
);

const LanguageIcon = ({ value }) => {
  if (value === "en") return <EnglishIcon />;
  if (value === "fr") return <FrenchIcon />;
  return <SpanishIcon />;
};

export default function LanguageSelector({ language, setLanguage }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const options = [
    { value: "es", title: "Español (Bolivia)" },
    { value: "en", title: "Inglés (EE. UU.)" },
    { value: "fr", title: "Francés" },
  ];

  const selectedOption =
    options.find((option) => option.value === language) || options[0];

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="
          flex items-center gap-1.5
          bg-transparent
          px-2 py-2
          text-zinc-500 dark:text-zinc-400
          text-sm font-medium
          hover:text-zinc-800 dark:hover:text-zinc-100
          transition-colors duration-200
          outline-none cursor-pointer
        "
      >
        <LanguageIcon value={selectedOption.value} />
        <span>{selectedOption.title}</span>
        <div
          className={`transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
        >
          <ChevronDownIcon />
        </div>
      </button>

      {isOpen && (
        <div
          className="
          absolute z-10 bottom-full mb-2 w-56 origin-bottom-left
          bg-white dark:bg-[#1e1e20]
          rounded-2xl shadow-xl
          border border-zinc-200 dark:border-zinc-700
          p-2 flex flex-col gap-1
        "
        >
          {options.map((option) => {
            const isSelected = language === option.value;

            return (
              <div
                key={option.value}
                onClick={() => {
                  setLanguage(option.value);
                  setIsOpen(false);
                }}
                className={`
                  flex items-center gap-3 p-3 rounded-xl cursor-pointer
                  transition-colors duration-150
                  hover:bg-zinc-100 dark:hover:bg-[#2a2a2c]
                  ${isSelected ? "bg-zinc-50 dark:bg-[#2a2a2c]" : ""}
                `}
              >
                <div className="w-5 shrink-0 text-zinc-800 dark:text-zinc-200">
                  {isSelected && <CheckIcon />}
                </div>

                <div className="shrink-0">
                  <LanguageIcon value={option.value} />
                </div>

                <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                  {option.title}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}