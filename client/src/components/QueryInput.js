import React from "react";

function QueryInput({ input, setInput, handleSubmit }) {
  return (
    <div className="mt-4 w-full max-w-xl flex">
      <input
        type="text"
        className="flex-1 px-4 py-2 rounded-l border border-gray-300 focus:outline-none"
        value={input}
        placeholder="Enter your query..."
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            handleSubmit();
          }
        }}
      />
      <button
        onClick={handleSubmit}
        className="px-4 py-2 bg-black text-white rounded-r hover:bg-gray-800"
      >
        Send
      </button>
    </div>
  );
}

export default QueryInput;
