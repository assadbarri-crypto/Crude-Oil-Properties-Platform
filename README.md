# 🛢️ Crude Oil Properties Platform

An interactive, AI-powered web application designed to explore, visualize, and compare the physicochemical properties of crude oils and their weathered fractions.

## 🌟 Features
*   **Interactive Dashboard:** Filter by origin, sample number (ESTS), and weathering fraction (W0-W4) to view over 20 different properties including Density, Viscosity, SARA fractions, and more.
*   **Dynamic Comparisons:** Generate bar charts to compare specific properties across multiple samples. Charts automatically sort from highest to lowest for easy analysis.
*   **AI Data Assistant:** A built-in chatbot powered by the Groq API (Llama 3). You can ask natural language questions (e.g., *"What is the viscosity of ESTS 0506?"*) or ask it to generate scatter plots (e.g., *"Plot density vs viscosity for Gulf of Mexico"*).

## 🛠️ Technology Stack
*   **Data Extraction:** `pdfplumber`, `pandas` (Custom Python script to parse 100+ PDF reports).
*   **Frontend:** `Streamlit`
*   **Visualization:** `Plotly Express`
*   **AI Integration:** `Groq` API (Tool Calling/Function Calling)

## 🚀 How to Run Locally
1. Clone the repository.
2. Install the requirements: `pip install -r requirements.txt`
3. Set up your Groq API key in a `.streamlit/secrets.toml` file:
   `GROQ_API_KEY = "your_api_key_here"`
4. Run the app: `streamlit run app.py`

## 📜 Data Attribution
Contains information licensed under the [Open Government Licence – Canada](https://open.canada.ca/en/open-government-licence-canada).
Original Data Source: Environment and Climate Change Canada (ECCC) Crude Oil and Petroleum Product Database.

## ⚖️ License
This project is licensed under the MIT License.
