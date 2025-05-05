import React from "react";

interface ContentCardProps {
  score: number;
  title: string;
  link: string;
  last_modification_date: string;
  file_size: string;
  keywords: { [keyword: string]: string };
  children_links: string[];
  parent_links: string[];
  isDarkMode: boolean;
}

const SearchResultCard: React.FC<ContentCardProps> = ({
  score,
  title,
  link,
  last_modification_date,
  file_size,
  keywords,
  children_links,
  parent_links,
  isDarkMode,
}) => {
  //Sort the keywords by score in descending order
  const sortedKeywords = Object.entries(keywords).sort(([, scoreA], [, scoreB]) => {
    return parseFloat(scoreB) - parseFloat(scoreA);
  });

  //a list of color, indicating high, medium, low score.
  const scoreColor =
    score > 0.75
      ? "bg-[#56EAFF]"
      : score > 0.5
      ? "bg-[#1DBBD1]"
      : score > 0.25
      ? "bg-[#0D7280]"
      : "bg-[#084F59]";

  const [showChildrenLinks, setShowChildrenLinks] = React.useState(false);
  const [showParentLinks, setShowParentLinks] = React.useState(false);

  return (
    <div
      className={`border ${
        isDarkMode
          ? "bg-[#2D2E2E] hover:bg-[#373737] text-white border-[#343636]"
          : "bg-[#ffffff] hover:bg-[#ffffff] text-[#494949] border-[#C3C3C1]"
      } p-4 rounded-2xl shadow-md max-w-3xl`}
    >
      {/* Score and Title */}
      <div className="flex items-center mb-2">
        <div
          className={`${scoreColor} ${
            score > 0.5 ? "text-black" : "text-white"
          } px-2 py-1 rounded-md text-sm mr-4`}
        >
          {score}
        </div>
        <h2 className="text-lg font-semibold truncate">{title}</h2>
      </div>

      {/* Link */}
      <a
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-300 hover:underline break-all"
      >
        {link}
      </a>

      {/* Date & File Size */}
      <div className="text-gray-400 text-sm mt-2">
        {new Date(last_modification_date).toDateString()} | {file_size}
      </div>

      {/* Keywords */}
      <div className="flex flex-wrap gap-2 mt-4 hover:cursor-pointer">
        {sortedKeywords.map(([keyword, score], index) => (
          <div
            key={index}
            className={`${
              isDarkMode ? "bg-white" : "bg-[#dcdbdb]"
            } px-3 py-1 rounded-xl text-sm transition-transform transform hover:scale-105 active:scale-95`}
          >
            <span
              className={`mr-2 ${
                isDarkMode ? "text-[#21B8CD]" : "text-[#21B8CD]"
              }`}
            >
              {keyword}
            </span>
            <span className="text-black">{score}</span>
          </div>
        ))}
      </div>

      {/* Children Links */}
      {children_links.length > 0 && (
        <div className="mt-4">
          <div className="flex items-start justify-start">
            <h3 className="text-sm font-semibold mb-2 mr-6">Children Links</h3>
            <button
              onClick={() => setShowChildrenLinks(!showChildrenLinks)}
              className={`text-gray-400 ${
                isDarkMode ? "hover:text-white" : "hover:text-black"
              } transition-colors`}
            >
              {showChildrenLinks ? "▲" : "▼"}
            </button>
          </div>
          {showChildrenLinks && (
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-300 ml-5">
              {children_links.map((childLink, index) => (
                <li key={index}>
                  <a
                    href={childLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline text-blue-300"
                  >
                    {childLink}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {/* Parent Links */}
      {parent_links.length > 0 && (
        <div className="mt-4">
          <div className="flex items-start justify-start">
            <h3 className="text-sm font-semibold mb-2 mr-6">Parent Links</h3>
            <button
              onClick={() => setShowParentLinks(!showParentLinks)}
              className={`text-gray-400 ${
                isDarkMode ? "hover:text-white" : "hover:text-black"
              } transition-colors`}
            >
              {showParentLinks ? "▲" : "▼"}
            </button>
          </div>
          {showParentLinks && (
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-300 ml-5">
              {parent_links.map((parentLink, index) => (
                <li key={index}>
                  <a
                    href={parentLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline text-blue-300"
                  >
                    {parentLink}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchResultCard;
