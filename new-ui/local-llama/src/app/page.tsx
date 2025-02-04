"use client";
import { useState } from "react";

export default function Home() {
    const [query, setQuery] = useState("");
    const [country, setCountry] = useState("no");
    const [summaryLang, setSummaryLang] = useState("en");
    const [results, setResults] = useState([]);
    const [summary, setSummary] = useState("");
    const [loading, setLoading] = useState(false);

    const sendQuery = async () => {
        setLoading(true);
        const res = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, country, summary_lang: summaryLang }),
        });

        const data = await res.json();
        setResults(data.results);
        setSummary(data.summary);
        setLoading(false);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-6">
            <h2 className="text-2xl font-bold mb-4">Search with Llama & Google</h2>

            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your search query..."
                className="border rounded p-2 mb-2 w-full max-w-md"
            />

            <div className="flex space-x-4 mb-2">
                <select
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="border rounded p-2"
                >
                    <option value="no">Norway</option>
                    <option value="us">United States</option>
                    <option value="fr">France</option>
                    <option value="de">Germany</option>
                    <option value="jp">Japan</option>
                </select>

                <select
                    value={summaryLang}
                    onChange={(e) => setSummaryLang(e.target.value)}
                    className="border rounded p-2"
                >
                    <option value="en">English</option>
                    <option value="no">Norwegian</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="jp">Japanese</option>
                </select>
            </div>

            <button
                onClick={sendQuery}
                className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
                disabled={loading}
            >
                {loading ? "Searching..." : "Search"}
            </button>

            {summary && (
                <div className="mt-6 p-4 bg-gray-100 rounded w-full max-w-lg">
                    <h3 className="font-bold">Summary:</h3>
                    <p>{summary}</p>
                </div>
            )}

            {results.length > 0 && (
                <div className="mt-6 w-full max-w-lg">
                    <h3 className="font-bold">Results:</h3>
                    <ul className="list-disc pl-5">
                        {results.map((item, index) => (
                            <li key={index} className="mb-2">
                                <a href={item.link} target="_blank" className="text-blue-500">
                                    {item.title}
                                </a>
                                <p className="text-sm">{item.snippet}</p>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
