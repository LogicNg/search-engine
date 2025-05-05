// App.tsx
import React, { useState, useEffect } from "react";
import SearchResultCard from "./components/SearchResultCard";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import { useQueryHistory } from "./hooks/useQueryHistory";

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
  const [searchResult, setSearchResult] = useState<ContentCardData[]>([]);

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  const [searched, setSearched] = useState(false);
  const [isSuggestionClicked, setIsSuggestionClicked] = useState(false);

  const [isSearching, setIsSearching] = useState(false);

  const [history, setHistory] = useState<[]>([]);
  const {
    queryHistory,
    addQueryHistory,
    deleteQueryHistory,
    clearQueryHistory,
  } = useQueryHistory();

  const [stemmedWords, setStemmedWords] = useState<string[]>([]);
  const [viewStemmedWords, setViewStemmedWords] = useState(false);

  //Get history
  useEffect(() => {
    fetch("/history")
      .then((res) => res.json())
      .then((data) => {
        data.sort(
          (a: { timestamp: string }, b: { timestamp: string }) =>
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        setHistory(data);
        //console.log("History:", data);
      })
      .catch((err) => console.error("Error fetching history:", err));
  }, []);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setQuery(value);
    setIsSuggestionClicked(false);

    if (value) {
      fetch(`/suggestions?query=${encodeURIComponent(value)}`)
        .then((res) => res.json())
        .then((data) => {
          setSuggestions(data);
          //console.log("Suggestions:", data);
        })
        .catch((err) => console.error("Error fetching suggestions:", err));
    } else {
      setSuggestions([]);
      //setSearchResult([]);
    }
  };

  const handleSearch = (searchQuery?: string) => {
    const queryToSearch = searchQuery ? searchQuery : query;
    //console.log("Searching for:", queryToSearch);

    if (!queryToSearch) {
      alert("Please enter a query");
      return;
    }

    setViewStemmedWords(false);

    setIsSearching(true);

    addQueryHistory(queryToSearch);

    fetch(`/search?query=${encodeURIComponent(queryToSearch)}`)
      .then((res) => res.json())
      .then((data) => {
        //data.sort((a: ContentCardData, b: ContentCardData) => b.score - a.score);
        setSearchResult(data);
        setIsSearching(false);
      })
      .catch((err) => console.error("Error fetching search result:", err));
  };

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  const [isHistorySelected, setIsHistorySelected] = useState<boolean[]>(() =>
    Array(queryHistory.length).fill(false)
  );

  useEffect(() => {
    if (queryHistory.length > isHistorySelected.length) {
      setIsHistorySelected((prev) => [
        ...prev,
        ...Array(queryHistory.length - prev.length).fill(false),
      ]);
    }
    //console.log("History selected:", isHistorySelected);
  }, [queryHistory]);

  //Voice input

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser doesn't support speech recognition.</span>;
  }

  useEffect(() => {
    setQuery(transcript); // Update query whenever transcript changes
  }, [transcript]);

  // Handler get similar page
  const handleGetSimilarPage = (index: number) => () => {
    // Get the keywords of the selected search result
    const selectedResult = searchResult[index];
    const keywords = selectedResult.keywords;
    //sort the keywords by score in descending order
    const sortedKeywords = Object.entries(keywords).sort(
      ([, scoreA], [, scoreB]) => {
        return parseFloat(scoreB) - parseFloat(scoreA);
      }
    );
    // Convert the sorted keywords to a string
    const keywordsString = sortedKeywords
      .map(([keyword, _]) => `${keyword}`)
      .join(" ");

    setQuery(keywordsString);
    //console.log("Searching for similar pages with keywords:", query);
    handleSearch(keywordsString);
    setSearched(true);
  };

  // Handle display and select stemmed words from db
  const handleStemmedWords = () => {
    fetch(`/get_stemmed_word`)
      .then((res) => res.json())
      .then((data) => {
        //console.log("Stemmed words:", data);
        setStemmedWords(data);
      })
      .catch((err) => console.error("Error fetching stemmed words:", err));
  };

  return (
    <div
      className={`${
        isDarkMode ? "bg-[#191A1A] text-white" : "bg-[#F1F1F1] text-[#1E3D43]"
      } min-h-screen flex`}
    >
      {/* Sidebar */}
      <div
        className={`${isSidebarOpen ? "w-64" : "w-20"} ${
          isDarkMode ? "bg-[#222222] text-white" : "bg-[#f6f6f6] text-[#1E3D43]"
        } transition-all duration-300 flex flex-col p-3`}
      >
        <button className="p-4" onClick={toggleSidebar}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            className="size-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
            />
          </svg>
        </button>
        {isSidebarOpen && (
          <div className="flex-1">
            <div className="flex items-center justify-between px-4 py-4 ">
              <h2 className="text-lg font-medium mt-5">History</h2>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                className="size-5 hover: cursor-pointer translate-y-2"
                onClick={clearQueryHistory}
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                />
              </svg>
            </div>
            <ul className="mt-5 overflow-y-auto max-h-[60vh]">
              {queryHistory.map((history_query, index) => (
                <li
                  onClick={() => {
                    const willBeSelected = !isHistorySelected[index];
                    setIsHistorySelected((prev) => {
                      //only one history can be selected at a time
                      const newState = Array(history.length).fill(false);
                      newState[index] = willBeSelected;
                      return newState;
                    });

                    // update if willBeSelected or the query dont have history_query

                    if (willBeSelected) {
                      setQuery(history_query);

                      handleSearch(history_query);
                      setSearched(true);
                    }
                  }}
                  onDoubleClick={() => {
                    deleteQueryHistory(history_query);
                    setIsHistorySelected((prev) => {
                      const newState = [...prev];
                      newState[index] = false;
                      return newState;
                    });
                  }}
                  key={index}
                  className={`flex justify-between items-center px-4 py-3 ${
                    isDarkMode
                      ? isHistorySelected[index]
                        ? "hover:bg-gray-700 bg-gray-700"
                        : "hover:bg-gray-700"
                      : isHistorySelected[index]
                      ? "hover:bg-gray-300 bg-gray-300"
                      : "hover:bg-gray-300"
                  } overflow-y-auto hover: cursor-pointer`}
                >
                  <p>{history_query}</p>
                  {/*}
                  <svg width="14" height="4" viewBox="0 0 14 4" fill="none" xmlns="http://www.w3.org/2000/svg" className="hover: cursor-pointer" stroke={isDarkMode ? "white" : "black"}>
                    <path d="M2 3.5C1.60218 3.5 1.22064 3.34196 0.93934 3.06066C0.658035 2.77936 0.5 2.39782 0.5 2C0.5 1.60218 0.658035 1.22064 0.93934 0.93934C1.22064 0.658035 1.60218 0.5 2 0.5C2.39782 0.5 2.77936 0.658035 3.06066 0.93934C3.34196 1.22064 3.5 1.60218 3.5 2C3.5 2.39782 3.34196 2.77936 3.06066 3.06066C2.77936 3.34196 2.39782 3.5 2 3.5ZM7 3.5C6.60218 3.5 6.22064 3.34196 5.93934 3.06066C5.65804 2.77936 5.5 2.39782 5.5 2C5.5 1.60218 5.65804 1.22064 5.93934 0.93934C6.22064 0.658035 6.60218 0.5 7 0.5C7.39782 0.5 7.77936 0.658035 8.06066 0.93934C8.34196 1.22064 8.5 1.60218 8.5 2C8.5 2.39782 8.34196 2.77936 8.06066 3.06066C7.77936 3.34196 7.39782 3.5 7 3.5ZM12 3.5C11.6022 3.5 11.2206 3.34196 10.9393 3.06066C10.658 2.77936 10.5 2.39782 10.5 2C10.5 1.60218 10.658 1.22064 10.9393 0.93934C11.2206 0.658035 11.6022 0.5 12 0.5C12.3978 0.5 12.7794 0.658035 13.0607 0.93934C13.342 1.22064 13.5 1.60218 13.5 2C13.5 2.39782 13.342 2.77936 13.0607 3.06066C12.7794 3.34196 12.3978 3.5 12 3.5Z" fill="white"/>
                  </svg>
                  
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="0.5"
                    className="size-6 hover: cursor-pointer"
                    stroke={isDarkMode ? "white" : "black"}
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3"
                    />
                  </svg>*/}
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
      <div
        className={`flex-1 flex flex-col items-center justify-start px-4 ${
          searched ? "mt-[5vh]" : "mt-[30vh]"
        }`}
      >
        {!searched && (
          <h1 className="text-2xl md:text-4xl mb-10">Not Deep Search</h1>
        )}
        {/* Search Bar */}
        <div className="relative flex-1">
          <div className="flex items-center justify-center gap-1">
            <div
              className={`flex items-center ${
                isDarkMode
                  ? "bg-[#222222] text-white"
                  : "bg-[#F1F1F1] text-[#1E3D43]"
              } px-4 py-2 h-[60px] w-[700px] rounded-tl-2xl rounded-tr-2xl ${
                suggestions.length > 0 && !isSuggestionClicked
                  ? ""
                  : "rounded-bl-2xl rounded-br-2xl"
              } border ${
                isDarkMode ? "border-[#343636]" : "border-[#C3C3C1]"
              } shadow hover: cursor-pointer`}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="#21B8CD"
                className="size-6 mr-5"
                onClick={() => {
                  setIsSuggestionClicked(true);
                  if (query) {
                    handleSearch();
                    setSearched(true);
                  } else {
                    setSearchResult([]);
                    setSearched(false);
                  }
                }}
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
                />
              </svg>

              <input
                className="flex-1 bg-transparent outline-none px-2"
                type="text"
                placeholder="Search..."
                value={query}
                onChange={handleSearchChange}
                onKeyDown={(event) => {
                  setIsSuggestionClicked(true);
                  if (event.key === "Enter") {
                    if (query) {
                      handleSearch();
                      setSearched(true);
                    } else {
                      setSearchResult([]);
                      setSearched(false);
                    }
                  }
                }}
              />
              {/* Mic Button */}
              <div className="bg-[#21B8CD] rounded-lg p-2 hover: cursor-pointer">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke={
                    isDarkMode
                      ? listening
                        ? "white"
                        : "black"
                      : listening
                      ? "black"
                      : "white"
                  }
                  className="size-6"
                  onClick={() => {
                    if (listening) {
                      //console.log("Stopping listening");
                      SpeechRecognition.stopListening();
                    } else {
                      resetTranscript();
                      //console.log("Starting listening");
                      setQuery("");
                      SpeechRecognition.startListening({
                        continuous: true,
                        language: "en-US",
                      });
                    }
                  }}
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && !isSuggestionClicked && (
            <ul
              className={` z-50  ${
                isDarkMode
                  ? "bg-[#222222] text-white"
                  : "bg-[#F1F1F1] text-[#1E3D43]"
              } rounded-bl-2xl rounded-br-2xl shadow overflow-y-auto max-h-60`}
            >
              {suggestions.map((suggestion, index) => (
                <li
                  key={index}
                  className={`px-4 py-2 cursor-pointer border ${
                    isDarkMode
                      ? "hover:bg-gray-600 border-[#343636]"
                      : "hover:bg-gray-300 border-[#C3C3C1]"
                  }`}
                  onClick={() => {
                    setQuery(suggestion);
                    setIsSuggestionClicked(true);
                  }}
                >
                  {suggestion}
                </li>
              ))}
            </ul>
          )}

          {/* Get all stemmed word */}
          {!searched && (
            <div>
              <div
                className={`${
                  isDarkMode ? "text-white" : "text-[#1E3D43]"
                } flex items-center justify-center mt-5 transition-colors transform hover:scale-105 active:scale-95 hover:cursor-pointer underline`}
                onClick={() => {
                  handleStemmedWords();
                  setViewStemmedWords(!viewStemmedWords);
                  
                }}
              >
                <h2 className="text-sm">
                  {viewStemmedWords ? "Close" : "Get All Stemmed Words"}
                </h2>
              </div>

              {viewStemmedWords &&
                stemmedWords.length > 0 &&
                searchResult.length === 0 &&
                !isSearching && (
                  <div className="relative w-full h-[85vh] overflow-y-auto">
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-10 gap-2 p-4">
                      {stemmedWords.map((item, index) => (
                        <button
                          key={`stemmed-word-${index}`}
                          onClick={() => {
                            // Add to query, preserve previous query
                            const newQuery = query ? `${query} ${item}` : item;
                            setQuery(newQuery);
                          }}
                          className={`
                        ${isDarkMode ? "text-white" : "text-black"}
                         text-sm px-2 py-1 rounded-md 
                        hover:bg-[#1DBBD1] transition-all 
                        transform hover:scale-105 active:scale-95
                        whitespace-nowrap overflow-hidden text-ellipsis
                      `}
                          title={item} // Show full word on hover
                        >
                          {item}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
            </div>
          )}
          {/* Circular loader while waiting for search result */}
          {isSearching && (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <svg
                className="animate-spin h-10 w-10 text-[#21B8CD]"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path
                  fill="currentColor"
                  d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8.009,8.009,0,0,1,12,20Z"
                />
                <path fill="currentColor" d="M12.5,6h-1V12h5v-1H12.5Z" />
              </svg>
            </div>
          )}

          {/* Have Search Results*/} 
          {searchResult.length > 0 && !isSearching && (
            <div className="relative w-full h-[85vh] overflow-y-auto scroll-mr-3">
              {searchResult.map((item, index) => (
                <div className="py-2 mt-3" key={index}>
                  <SearchResultCard
                    {...item}
                    isDarkMode={isDarkMode}
                    onClick={handleGetSimilarPage(index)}
                  />
                </div>
              ))}
            </div>
          )}

          {/* No Search Results */}
          {searchResult.length === 0 && !isSearching && searched && (
            <div className="flex flex-col items-center justify-center mt-[30vh] gap-y-4">
              <h2 className="text-lg ">
                No results containing all your search terms were found.
              </h2>
              <h2 className="text-sm">
                Try different keywords or remove some filters.
              </h2>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
