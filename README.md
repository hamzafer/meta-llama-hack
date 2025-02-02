*Innovating with AI and Llama Models to Solve Real-World Problems*

---

## 👥 Team Members

- **Oliver Sanchez** - AI & Machine Learning Specialist
- **Adi Singh** - Robotics Engineer & Backend Developer
- **Hamza Zafar** - Data Scientist & NLP Expert
- **Putri Azizah** - Computer Vision Expert

We are a passionate team of developers and researchers dedicated to leveraging AI for impactful solutions. Our focus is
on building **cutting-edge applications** that integrate **Llama models, NLP, and AI-driven automation** to tackle
real-world challenges.

# Local Search & Summarization Demo

This project is a demo application that:

- Accepts a search query in a user’s language.
- Translates the query to the local language (using a Llama-based API).
- Uses the Google Custom Search API to retrieve localized search results.
- Summarizes the results via Llama.
- Displays the top 10 results with images (if available) in a clean front-end.

## Setup

1. **Clone the repository and navigate to the project folder:**

   ```bash
   git clone https://github.com/yourusername/my_search_app.git
   cd my_search_app
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**

   Create a `.env` file in the project root (see the provided example) and insert your API keys and configuration
   values.

4. **Run the application:**

   ```bash
   python app.py
   ```

5. **Visit the application:**

   Open your browser at [http://localhost:5000](http://localhost:5000).

## Notes

- Ensure your Llama API (or Ollama) is running and accessible at the URL specified in your `.env` file.
- Customize the supported countries and languages in `app.py` as needed.
- This is a demo. In a production setting, you may wish to add error handling, security enhancements, and further
  refinements to the UI.

Happy coding!
