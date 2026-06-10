export default function ToggleSwitch({ checked, onChange, disabled }) {
  return (
    <button
      type="button"
      onClick={() => !disabled && onChange(!checked)}
      className={`w-12 h-6 rounded-full relative transition-colors duration-300 outline-none ${
        checked ? "bg-green-500" : "bg-zinc-300 dark:bg-zinc-600"
      } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
    >
      <div
        className={`w-4 h-4 bg-white rounded-full absolute top-1 transition-transform duration-300 shadow-sm ${
          checked ? "translate-x-7" : "translate-x-1"
        }`}
      />
    </button>
  );
}
