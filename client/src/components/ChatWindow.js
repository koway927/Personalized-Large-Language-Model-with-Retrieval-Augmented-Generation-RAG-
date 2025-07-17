import React from "react";

function ChatWindow({ messages }) {
  return (
    <div className="p-4 bg-white rounded shadow max-w-xl w-full space-y-3 overflow-y-auto min-h-[300px]">
      <div className="flex flex-col space-y-2">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`text-sm px-4 py-2 rounded break-words inline-block max-w-xs ${
              msg.role === "user"
                ? "bg-blue-100 self-end text-right"
                : "bg-gray-100 self-start text-left"
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChatWindow;
