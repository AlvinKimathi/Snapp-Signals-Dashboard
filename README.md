# Snapp Signals Dashboard

The **Snapp Signals Dashboard** is an interactive web app for exploring economic and operational indicators for Kenya. Built with **Streamlit** for the front-end and **FastAPI** & **Python** for the back-end, it brings together cleaned data, charts, and a conversational assistant into one user-friendly interface.

---

## What it does

At its core, this project combines multiple datasets and turns them into a coherent set of signals for easier monitoring and interpretation.

### Features

- **Interactive charts and metrics**  
  Visualise exchange rates, inflation, energy prices, compliance pressure indices. Each chart supports hover tooltips, zooming, and filtering so users can explore trends more naturally.

- **Contextual insights**  
  The dashboard highlights important observations such as **Data Lag**, **Insight of the Day**, and other summary notes that help users quickly understand what matters.

- **Conversational assistant**  
  A built-in chatbot powered by OpenAI can answer questions about the dashboard’s data. It uses the current dashboard context to generate grounded, relevant responses.

- **Modular architecture**  
  The front-end, API server, and data ingestion workflows are separated into distinct modules, making the project easier to maintain and extend.

---

## Repository structure

The project is organised into the following top-level folders:

| Path | Purpose |
|------|---------|
| `Dashboard/` | Streamlit front-end and FastAPI server. Contains `App.py` (Streamlit entry point), `api_server.py` (FastAPI entry point), and supporting modules. |
| `Clean_Data/` | Pre-processed CSV files used directly by the dashboard. Each file represents a specific indicator. |
| `Raw_Data/` | Original source datasets before cleaning and transformation. Useful for traceability and reproducibility. |
| `Registry/` | Contains the data catalogue (`Data Source Registry.xlsx`) and (`insight_registry.csv`) which track data sources, update frequency and usage. |
| `Notebook/` | Jupyter notebooks used for exploration, cleaning, and transformation of raw datasets. |
| `Output/` | Generated artefacts such as pre-rendered charts and other outputs. |

---

## Conversational assistant

The dashboard includes a built-in assistant that helps users interact with the data and easier understanding for non-technical viewers.

### How it works

- The Streamlit dashboard captures the current context from the visible charts, filters, and metrics
- That context is sent to the FastAPI back-end
- The back-end builds a grounded prompt using the dashboard state
- OpenAI’s API generates a response based on the current data context
- The assistant returns an answer designed to stay relevant to the dashboard instead of giving generic responses

### Bot requirements

To use the assistant properly:

- `OPENAI_API_KEY` must be set
- The FastAPI server must be running
- The Streamlit app must be able to reach the API using `SNAPP_BOT_API_URL`

If the key is missing or the API server is unavailable, the bot should return a helpful fallback message instead of failing silently.

---

## Data workflow

The project separates raw data, cleaned data, and presentation logic so the workflow remains easy to follow.

### General flow

1. Raw datasets are stored in `Raw_Data/`
2. Cleaning and transformation are done in notebooks or scripts
3. Processed files are saved into `Clean_Data/`
4. The dashboard reads from `Clean_Data/`
5. Source tracking and update notes are stored in `Registry/`

This structure makes it easier to refresh indicators without constantly changing dashboard logic.

---

## Example indicators included

Depending on the current data files available, the dashboard includes indicators such as:

- Central Bank of Kenya rates
- Inflation and CPI measures
- Exchange rates
- Fuel and energy-related indicators
- Compliance pressure indices
- Road accident statistics
- Other macroeconomic and operational signals relevant to Kenya

---

## Acknowledgements

- The design and early implementation were shaped by the needs of analysts tracking macroeconomic conditions in Kenya
- Data comes from a range of official and public sources including:
  - Central Bank of Kenya
  - Kenya National Bureau of Statistics
  - EPRA
  - World Bank
- Prompt logic for the assistant is defined in `bot/bot_prompts.py`
- Full source and update details are tracked in the `Registry/` folder

---

## License

This repository is provided for **Internal use**.

If you plan to deploy it publicly or build on it commercially, make sure you:

- have permission to use all included datasets
- comply with third-party data usage terms
- comply with the terms of any APIs or external services used

---

## Notes

- This dashboard is intended to simplify the monitoring of signals that would otherwise remain spread across multiple datasets and reporting sources.
- The architecture is designed so that the data layer, dashboard layer, and assistant layer can evolve independently.
- For best performance, keep cleaned datasets consistent in structure and naming so the loader functions continue working without code changes.

---