// App.tsx
import React, { useState, useEffect } from "react";
import SearchResultCard from "./components/SearchResultCard";

interface ContentCardData {
  score: number;
  title: string;
  link: string;
  last_modification_date: string;
  file_size: string;
  keywords: { [keyword: string]: string };
  children_links: string[];
  parent_links: string[];
}

const App: React.FC = () => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [history, setHistory] = useState<string[]>([]);
  const [searchResult, setSearchResult] = useState<ContentCardData[]>([]);

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  //Get search history
  useEffect(() => {
    const dummyHistory = ["Movie", "Move", "Movement", "Movvvy", "Move", "Movement", "Movvvy"];
    setHistory(dummyHistory);
  }, []);

  // Get search results
  useEffect(() => {
    fetch("/search")
      .then((res) => res.json())
      .then((data) => { 
        data.sort((a: ContentCardData, b: ContentCardData) => b.score - a.score);
        setSearchResult(data);
        console.log(data); 
      })
      .catch((err) => console.error("Error fetching data:", err));
  }, [query]); 

  
  
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setQuery(value);

    // Dummy suggestions for demonstration
    if (value) {
      setSuggestions(["Movie", "Move", "Movement", "Movvvy", "Move", "Movement", "Movvvy"]);
    } else {
      setSuggestions([]);
    }
  };

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  return (
    <div className={`${isDarkMode ? "bg-[#191A1A] text-white" : "bg-[#F1F1F1] text-[#1E3D43]"} min-h-screen flex`}>
      {/* Sidebar */}
      <div
        className={`${isSidebarOpen ? "w-64" : "w-20"} ${isDarkMode ? "bg-[#222222] text-white" : "bg-[#f6f6f6] text-[#1E3D43]"} transition-all duration-300 flex flex-col p-3`}
      >
        <button className="p-4" onClick={toggleSidebar}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>

        </button>
        {isSidebarOpen && (
          <div className="flex-1 overflow-y-auto">
            <h2 className="px-4 py-4 text-lg font-medium mt-5">History</h2>
            <ul className="mt-5">
              {history.map((query, index) => (
                <li className={`flex justify-between items-center px-4 py-3 ${isDarkMode ? "hover:bg-gray-700" : "hover:bg-gray-300"} overflow-y-auto hover: cursor-pointer`}>
                  <span>{query}</span>
                  <svg width="14" height="4" viewBox="0 0 14 4" fill="none" xmlns="http://www.w3.org/2000/svg" className="hover: cursor-pointer" stroke={isDarkMode ? "white" : "black"}>
                    <path d="M2 3.5C1.60218 3.5 1.22064 3.34196 0.93934 3.06066C0.658035 2.77936 0.5 2.39782 0.5 2C0.5 1.60218 0.658035 1.22064 0.93934 0.93934C1.22064 0.658035 1.60218 0.5 2 0.5C2.39782 0.5 2.77936 0.658035 3.06066 0.93934C3.34196 1.22064 3.5 1.60218 3.5 2C3.5 2.39782 3.34196 2.77936 3.06066 3.06066C2.77936 3.34196 2.39782 3.5 2 3.5ZM7 3.5C6.60218 3.5 6.22064 3.34196 5.93934 3.06066C5.65804 2.77936 5.5 2.39782 5.5 2C5.5 1.60218 5.65804 1.22064 5.93934 0.93934C6.22064 0.658035 6.60218 0.5 7 0.5C7.39782 0.5 7.77936 0.658035 8.06066 0.93934C8.34196 1.22064 8.5 1.60218 8.5 2C8.5 2.39782 8.34196 2.77936 8.06066 3.06066C7.77936 3.34196 7.39782 3.5 7 3.5ZM12 3.5C11.6022 3.5 11.2206 3.34196 10.9393 3.06066C10.658 2.77936 10.5 2.39782 10.5 2C10.5 1.60218 10.658 1.22064 10.9393 0.93934C11.2206 0.658035 11.6022 0.5 12 0.5C12.3978 0.5 12.7794 0.658035 13.0607 0.93934C13.342 1.22064 13.5 1.60218 13.5 2C13.5 2.39782 13.342 2.77936 13.0607 3.06066C12.7794 3.34196 12.3978 3.5 12 3.5Z" fill="white"/>
                  </svg>

                </li>
              ))} 
            </ul>
          </div>
        )}
        {isSidebarOpen && (
          <div className="p-4 flex items-center justify-between"> 
              <span className="mr-2">Dark Mode</span>
              <input
                type="checkbox"
                checked={isDarkMode}
                onChange={toggleTheme}
                className="toggle-checkbox"
              /> 
          </div>
        )}
      </div>

      {/* Main */}
      <div className={`flex-1 flex flex-col items-center justify-start px-4 ${searchResult.length > 0 ? "mt-[5vh]" : "mt-[30vh]"}`}>
        
        {!searchResult.length && (<h1 className="text-2xl md:text-4xl mb-10">Not Deep Search</h1>)}
        {/* Search Bar */}
        <div className="relative">
          <div className={`flex items-center ${isDarkMode ? "bg-[#222222] text-white" : "bg-[#F1F1F1] text-[#1E3D43]"} px-4 py-2 h-[60px] w-[700px] rounded-tl-2xl rounded-tr-2xl ${suggestions.length > 0 ? "" : "rounded-bl-2xl rounded-br-2xl"} border ${isDarkMode ? "border-[#343636]" : "border-[#C3C3C1]"} shadow hover: cursor-pointer`}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="#21B8CD" className="size-6 mr-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
            </svg>

            <input
              className="flex-1 bg-transparent outline-none px-2"
              type="text"
              placeholder="Search..."
              value={query}
              onChange={handleSearchChange}
            />

            <div className="bg-[#21B8CD] rounded-lg p-2 hover: cursor-pointer">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke={isDarkMode ? "black" : "white"}
                className="size-6"
              >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z"
              />
              </svg>
            </div>
            

          </div>

          <div className="relative w-full h-[85vh] overflow-y-auto">
          {searchResult.map((item, index) => (
            <div className="py-2 mt-3" key={index}>
              <SearchResultCard {...item} />
            </div>
          ))}
        </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <ul className={`absolute top-full w-full ${isDarkMode ? "bg-[#222222] text-white" : "bg-[#F1F1F1] text-[#1E3D43]"} rounded-bl-2xl rounded-br-2xl shadow overflow-y-auto max-h-60`}>
              {suggestions.map((suggestion, index) => (
                <li
                  key={index}
                  className={`px-4 py-2 hover:bg-gray-600 cursor-pointer border ${isDarkMode ? "border-[#343636]" : "border-[#C3C3C1]"}`}
                  onClick={() => setQuery(suggestion)}
                >
                  {suggestion}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;