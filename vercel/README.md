# Local Llama Search

Local Llama Search is an AI-powered answer engine running fully on local hardware.

## 🛠️ Tech Stack

- **Frontend:** Next.js, Tailwind CSS
- **Backend:** FastAPI
- **LLMs:** Local models via Ollama
- **Search:** SearxNG
- **Memory:** Redis
- **Deployment:** Docker

## 🏃‍♂️ Running Locally

### Setup

1. Prepare the backend environment:
    ```bash
    cd local_llama_search/backend/
    mv .env.development.example .env.development
    ```
   Edit `.env.development` as needed. Ensure you have a capable GPU for running models.

2. No setup required for the frontend.

3. Start the app:
    ```bash
    cd local_llama_search/
    docker compose up
    ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

