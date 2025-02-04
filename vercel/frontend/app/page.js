"use client";
import { useState } from "react";
import Sidebar from "./components/Sidebar";
import SearchForm from "./components/SearchForm";
import SearchResultCard from "./components/SearchResultCard";

export default function HomePage() {
  // We'll store the entire "chat" or "history" in state:
  // Each entry will be { id, query, selectedCountry, summaryLang, results, summary, timestamp }
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);

  // Handler when a new search is performed
  const handleNewSearch = (newChat) => {
    // newChat is an object: { id, query, selectedCountry, summaryLang, results, summary, timestamp }
    setChatHistory((prev) => [newChat, ...prev]);
    setSelectedChatId(newChat.id);
  };

  // If we have a selected chat, find it in the array
  const activeChat = chatHistory.find((c) => c.id === selectedChatId);

  // Handler to create a brand new chat (clears UI state)
  const handleCreateNewChat = () => {
    setSelectedChatId(null);
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar for chat history */}
      <Sidebar
        chatHistory={chatHistory}
        onSelectChat={setSelectedChatId}
        onNewChat={handleCreateNewChat}
        selectedChatId={selectedChatId}
      />

      {/* Main content area */}
      <div className="flex-1 p-4 overflow-auto">
        {/* Search form always visible at top (or you can hide if there's an active chat) */}
        <SearchForm onNewSearch={handleNewSearch} />

        {/* Display results if we have an active chat */}
        {activeChat ? (
          <div className="mt-4">
            <h2 className="text-xl font-bold mb-2">Search Results:</h2>
            {activeChat.results && activeChat.results.length > 0 ? (
              <div className="space-y-4">
                {activeChat.results.map((result, idx) => (
                  <SearchResultCard key={idx} result={result} />
                ))}
              </div>
            ) : (
              <p>No results yet.</p>
            )}

            {activeChat.summary && (
              <div className="mt-6 bg-gray-100 dark:bg-gray-800 p-4 rounded">
                <h3 className="text-lg font-semibold mb-2">Summary</h3>
                <p>{activeChat.summary}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="mt-4">
            <p className="text-gray-500">Start a new search or select a chat from the sidebar.</p>
          </div>
        )}
      </div>
    </div>
  );
}
