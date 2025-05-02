import { useState, useRef, useEffect } from "react";

interface DropdownProps {
  items: {
    label: string;
    onClick: () => void;
  }[];
  isDarkMode: boolean;
}

const DropdownMenu = ({ items, isDarkMode }: DropdownProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const [selectedItem, setSelectedItem] = useState<string>(items[0].label);
  const handleItemClick = (item: string) => {
    setSelectedItem(item);
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close dropdown on ESC key press
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="relative z-50" ref={dropdownRef}>
      <button
        type="button"
        className="inline-flex justify-center w-full px-4 py-2 text-sm font-medium text-[#21B8CD] rounded-md shadow-sm"
        id="menu-button"
        aria-expanded={isOpen}
        aria-haspopup="true"
        onClick={() => setIsOpen(!isOpen)}
      >
        {selectedItem}
        <svg
          className={`w-5 h-5 ml-2 -mr-1 ${isDarkMode ? "text-white" : "text-black"}`}
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {isOpen && (
        <div
          className={`absolute left-0 w-30 mt-2 origin-top-right border ${
            isDarkMode
              ? "bg-[#222222] text-white border-[#343636]"
              : "bg-[#F1F1F1] text-[#1E3D43] border-[#C3C3C1]"
          }
          rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none`}
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="menu-button"
        >
          <div className="py-1" role="none">
            {items.map((item, index) => (
              <button
                key={index}
                className={`block w-full px-4 py-2 text-sm text-left ${
                  isDarkMode
                    ? "hover:bg-gray-600 border-[#343636]"
                    : "hover:bg-gray-300 border-[#C3C3C1]"
                }`}
                role="menuitem"
                onClick={() => {
                  item.onClick();
                  handleItemClick(item.label);
                  setIsOpen(false);
                }}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DropdownMenu;
