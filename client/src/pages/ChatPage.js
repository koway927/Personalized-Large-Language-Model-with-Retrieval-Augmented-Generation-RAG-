// import React, { useState } from "react";
// import QueryInput from "../components/QueryInput";
// import ChatWindow from "../components/ChatWindow";
// import Sidebar from "../components/Sidebar";
// import { extractInfoFromQuery, insertInfoToDB} from "../utils/extractInfo";

// function ChatPage() {
//   const [input, setInput] = useState("");
//   const [activeId, setActiveId] = useState(null);
//   const [messages, setMessages] = useState([]);
//   const [history, setHistory] = useState([]);
//   const [showSidebar, setShowSidebar] = useState(true);

//   // tempopary mock function, replace this later with real LLM API call
//   const handleSubmit = async () => {
//     if (input.trim() === "") return;

//     const userMsg = { role: "user", content: input };
//     setMessages((prev) => [...prev, userMsg]);
//     setInput("");

//     try {
//       // Send POST request to Flask backend
//       const res = await fetch("http://localhost:5000/query-llm", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//           body: JSON.stringify({
//           user_id: "1",
//           session_id: 1,
//           query: input,
//         }),
//       });

//       const data = await res.json();

//       const aiMsg = {
//         role: "assistant",
//         content: data.response || "No response received.",
//       };

//       const newMessages = [...messages, userMsg, aiMsg];
//       setMessages(newMessages);

//       // Optional: Extract info for DB
//       const extracted = await extractInfoFromQuery(input);
//       if (extracted) {
//         console.log("Extracted info", extracted);
//         // await insertInfoToDB(extracted);
//       }

//       if (newMessages.length === 2) {
//         const newConversation = {
//           id: Date.now(),
//           title: userMsg.content.slice(0, 15) + "...",
//           messages: newMessages,
//         };
//         setHistory((prev) => [newConversation, ...prev]);
//         setActiveId(newConversation.id);
//       } else {
//         setHistory((prev) =>
//           prev.map((conv) =>
//             conv.id === activeId ? { ...conv, messages: newMessages } : conv
//           )
//         );
//       }
//     } catch (err) {
//       console.error("Failed to fetch LLM response:", err);
//       const errorMsg = {
//         role: "assistant",
//         content: "An error occurred while contacting the server.",
//       };
//       setMessages((prev) => [...prev, errorMsg]);
//     }
//   };

//   // Load Conversations
//   const handleHistoryClick = (conversation) => {
//     setMessages(conversation.messages);
//     setActiveId(conversation.id);

//   };

//   return (
//     <div className="min-h-screen bg-gray-100 flex"> 
//       {/* Sidebar */}
//       <Sidebar
//         history={history}
//         activeId={activeId}
//         onHistoryClick={handleHistoryClick}
//         showSidebar={showSidebar}
//         setShowSidebar={setShowSidebar}
//       />
      
//       {/* Main content */}
//       <div className="flex-1 flex justify-center p-6">
//         <div className="w-full max-w-2xl flex flex-col items-center">
//           <h1 className="text-3xl font-bold mb-4">Chat</h1>
//           <button
//             className="mb-4 px-4 py-2 bg-black text-white rounded hover:bg-gray"
//             onClick={() => {
//               setMessages([]);
//               setActiveId(null);
//               setInput("");
//             }}
//           >
//             + New Conversation
//           </button>

//           {/* Chat window */}
//           <ChatWindow messages={messages} />

//           {/* Input box */}
//           <QueryInput input={input} setInput={setInput} handleSubmit={handleSubmit} />

//         </div>
//       </div>
//     </div>
//   );
// }

// export default ChatPage;
import React, { useState } from "react";
import QueryInput from "../components/QueryInput";
import ChatWindow from "../components/ChatWindow";
import Sidebar from "../components/Sidebar";
import ReactMarkdown from "react-markdown";

function ChatPage() {
  const [input, setInput] = useState("");
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);

  const user_id = "6";         // Replace with actual user ID logic
  const session_id = 17908;   // Replace with actual session ID logic

  const handleSubmit = async () => {
    if (input.trim() === "") return;

    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:5000/query-llm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: user_id,
          session_id: session_id,
          query: input,
        }),
      });

      const data = await res.json();
      const aiMsg = {
        role: "assistant",
        content: data.response || "No response received.",
      };

      const newMessages = [...messages, userMsg, aiMsg];
      setMessages(newMessages);

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
    } catch (err) {
      console.error("Failed to fetch LLM response:", err);
      const errorMsg = {
        role: "assistant",
        content: "An error occurred while contacting the server.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleHistoryClick = (conversation) => {
    setMessages(conversation.messages);
    setActiveId(conversation.id);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar
        history={history}
        activeId={activeId}
        onHistoryClick={handleHistoryClick}
        showSidebar={showSidebar}
        setShowSidebar={setShowSidebar}
      />

      <div className="flex-1 flex justify-center p-6">
        <div className="w-full max-w-4xl flex flex-col items-center">
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
          <div className="w-full h-[600px] overflow-y-scroll bg-white p-4 rounded shadow mb-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-4 ${
                  msg.role === "user" ? "text-right" : "text-left"
                }`}
              >
                <div
                  className={`inline-block p-3 rounded-xl ${
                    msg.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-black"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    <p>{msg.content}</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Input box */}
          <QueryInput input={input} setInput={setInput} handleSubmit={handleSubmit} />
        </div>
      </div>
    </div>
  );
}

export default ChatPage;
