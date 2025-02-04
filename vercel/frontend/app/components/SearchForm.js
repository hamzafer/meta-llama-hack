import { useState } from "react";
import { v4 as uuidv4 } from "uuid";

export default function SearchForm({ onNewSearch }) {
  const [query, setQuery] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("no"); // default
  const [summaryLang, setSummaryLang] = useState("en"); // default
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const countries = [
    { code: "us", name: "United States" },
    { code: "no", name: "Norway" },
    { code: "jp", name: "Japan" },
    { code: "fr", name: "France" },
    { code: "de", name: "Germany" },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:5000/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          country: selectedCountry,
          summary_lang: summaryLang,
        }),
      });
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      const data = await response.json();
      // Data includes: { query, selected_country, summary_lang, results, summary }
      const newChat = {
        id: uuidv4(),
        query: data.query,
        selectedCountry: data.selected_country,
        summaryLang: data.summary_lang,
        results: data.results,
        summary: data.summary,
        timestamp: Date.now(),
      };
      onNewSearch(newChat);
      setQuery(""); // clear input
    } catch (err) {
      console.error(err);
      setError(err.message || "Error calling backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col md:flex-row items-center gap-2"
    >
      <input
        type="text"
        className="flex-1 p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
        placeholder="Enter your query..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        required
      />

      <select
        value={selectedCountry}
        onChange={(e) => setSelectedCountry(e.target.value)}
        className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
      >
        {countries.map((c) => (
          <option key={c.code} value={c.code}>
            {c.name}
          </option>
        ))}
      </select>

      <select
        value={summaryLang}
        onChange={(e) => setSummaryLang(e.target.value)}
        className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
      >
        {/* Provide your desired summary language options */}
        <option value="en">English</option>
        <option value="no">Norwegian</option>
        <option value="jp">Japanese</option>
        <option value="fr">French</option>
        <option value="de">German</option>
      </select>

      <button
        type="submit"
        className="p-2 bg-blue-500 hover:bg-blue-600 text-white rounded"
        disabled={loading}
      >
        {loading ? "Searching..." : "Search"}
      </button>

      {error && <p className="text-red-500 ml-2">{error}</p>}
    </form>
  );
}
