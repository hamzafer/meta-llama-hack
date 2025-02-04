export async function POST(req: Request) {
    try {
        const { query, country, summary_lang } = await req.json();

        const response = await fetch("http://127.0.0.1:5000/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                query, 
                country: country || "no",  // Default to Norway if not provided
                summary_lang: summary_lang || "en"  // Default to English if not provided
            }),
        });

        const data = await response.json();
        return new Response(JSON.stringify(data), { status: 200 });
    } catch (error) {
        return new Response(JSON.stringify({ error: "Failed to fetch from backend" }), { status: 500 });
    }
}
