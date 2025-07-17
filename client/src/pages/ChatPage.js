import React, { useState } from "react";
import QueryInput from "../components/QueryInput";
import ChatWindow from "../components/ChatWindow";
import Sidebar from "../components/Sidebar";
import { extractInfoFromQuery, insertInfoToDB} from "../utils/extractInfo";

function ChatPage() {
  const [input, setInput] = useState("");
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);

  // tempopary mock function, replace this later with real LLM API call
  const handleSubmit = async () => {
    if (input.trim() === "") return;

    const userMsg = { role: "user", content: input };
    const aiMsg = {
      role: "assistant",
      content: `Your question: ${input}`, // TODO: Replace with actual call to LLM API
    };

    const newMessages = [...messages, userMsg, aiMsg];
    setMessages(newMessages);
    setInput("");

    // use Gemini to extract info
    const extracted = await extractInfoFromQuery(input);
    //if (!isDatabaseFull && extracted)
    if (extracted) {
        console.log("Extracted info", extracted);

        // TODO: insert to DB 
        // await insertInfoToDB(extracted);
    }


    if (newMessages.length === 2) {
      const newConversation = {
        id: Date.now(),
        title: userMsg.content.slice(0, 15) + "...",
        messages: newMessages,
      };
      setHistory((prev) => [newConversation, ...prev]);
      setActiveId(newConversation.id);
    } else {
      setHistory((prev) =>
        prev.map((conv) =>
          conv.id === activeId ? { ...conv, messages: newMessages } : conv
        )
      );
    }
  };

  // Load Conversations
  const handleHistoryClick = (conversation) => {
    setMessages(conversation.messages);
    setActiveId(conversation.id);

  };

  return (
    <div className="min-h-screen bg-gray-100 flex"> 
      {/* Sidebar */}
      <Sidebar
        history={history}
        activeId={activeId}
        onHistoryClick={handleHistoryClick}
        showSidebar={showSidebar}
        setShowSidebar={setShowSidebar}
      />
      
      {/* Main content */}
      <div className="flex-1 flex justify-center p-6">
        <div className="w-full max-w-2xl flex flex-col items-center">
          <h1 className="text-3xl font-bold mb-4">Chat</h1>
          <button
            className="mb-4 px-4 py-2 bg-black text-white rounded hover:bg-gray"
            onClick={() => {
              setMessages([]);
              setActiveId(null);
              setInput("");
            }}
          >
            + New Conversation
          </button>

          {/* Chat window */}
          <ChatWindow messages={messages} />

          {/* Input box */}
          <QueryInput input={input} setInput={setInput} handleSubmit={handleSubmit} />

        </div>
      </div>
    </div>
  );
}

export default ChatPage;