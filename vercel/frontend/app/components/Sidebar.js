export default function Sidebar({
    chatHistory,
    onSelectChat,
    onNewChat,
    selectedChatId,
  }) {
    return (
      <div className="w-64 bg-gray-100 dark:bg-gray-800 text-black dark:text-gray-100 p-4 flex flex-col">
        <button
          onClick={onNewChat}
          className="mb-4 w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
        >
          New Chat
        </button>
  
        <div className="flex-1 overflow-auto space-y-2">
          {chatHistory.map((chat) => (
            <div
              key={chat.id}
              className={`p-2 rounded cursor-pointer ${
                selectedChatId === chat.id
                  ? "bg-blue-300 dark:bg-blue-700"
                  : "hover:bg-gray-200 dark:hover:bg-gray-700"
              }`}
              onClick={() => onSelectChat(chat.id)}
            >
              <div className="font-semibold">{chat.query}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {new Date(chat.timestamp).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  