import React from "react";

function Sidebar({ history, activeId, onHistoryClick, showSidebar, setShowSidebar }) {
  return (
    <div
      className={`transition-all duration-300 ${
        showSidebar ? "w-56" : "w-4"
      } bg-white shadow-md overflow-hidden`}
    >
      <div className="flex items-center justify-between px-2 py-2 border-b">
        {showSidebar && <span className="font-bold text-sm">Recent Searches</span>}
        <button
          className="text-sm text-black ml-auto"
          onClick={() => setShowSidebar(!showSidebar)}
          title={showSidebar ? "Collapse" : "Expand"}
        >
          {showSidebar ? "⟨" : "⟩"}
        </button>
      </div>

      {showSidebar && (
        <ul className="p-3 space-y-2 text-sm">
          {history.map((conv) => (
            <li
              key={conv.id}
              className={`cursor-pointer text-black hover:text-gray-700 font-light truncate`}
              onClick={() => onHistoryClick(conv)}
            >
              {conv.title}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Sidebar;
