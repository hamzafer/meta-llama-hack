"use client";
import { useState, useEffect } from "react";
import "../app/globals.css"; // Tailwind + global styles

export default function RootLayout({ children }) {
  const [darkMode, setDarkMode] = useState(false);

  // If you want to persist dark mode across sessions, you can save to localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      setDarkMode(true);
    }
  }, []);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [darkMode]);

  return (
    <html lang="en">
      <head>
        <title>My Next.js + Flask Search App</title>
      </head>
      <body className="bg-white text-black dark:bg-gray-900 dark:text-gray-100 transition-colors">
        {/* Dark mode toggle in a small fixed corner or anywhere you like */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="absolute top-4 right-4 px-4 py-2 bg-gray-200 dark:bg-gray-800 rounded"
        >
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>

        {children}
      </body>
    </html>
  );
}
