# DocInsight-MCP

A document-driven query system that parses graduate application PDFs, stores 
the extracted data in a SQLite database, and lets users ask plain-English 
questions about the data — powered by Cohere's LLM API and a custom MCP 
(Model Context Protocol) layer.

Built as a university capstone project to demonstrate safe LLM-database 
integration without exposing raw SQL generation to the model.

## Features
- Parse structured PDF application forms into JSON
- Store and query application data in SQLite
- Batch ingest directories of PDFs with deduplication
- Natural language querying via Cohere LLM API
- Safe execution through a validated MCP tool call layer
- Supports filtering and aggregation queries

## How It Works
1. PDFs are parsed into structured Python dictionaries
2. Parsed data is staged as JSON then inserted into SQLite
3. User enters a natural language query
4. The LLM converts the query into a structured tool call
5. The MCP layer validates and executes the tool call safely
6. Results are returned to the user

## Tech Stack
- **Language:** Python
- **Database:** SQLite
- **LLM API:** Cohere
- **PDF Parsing:** pdfplumber
- **Protocol:** MCP (Model Context Protocol)

## Setup

### 1. Clone the repository
git clone https://github.com/CornellCodes/DocInsight-MCP.git
cd DocInsight-MCP

### 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set your Cohere API key

macOS / Linux:
export COHERE_API_KEY="your_api_key_here"

To persist across sessions:
echo 'export COHERE_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc

### 5. Run the app
cd MCP-DocInsight
./start.sh

## Example Queries
- "How many applicants are there?"
- "How many BIO applicants had at least a 3.5 GPA?"
- "Show CSC applicants above 3.2 GPA"
- "Show provisional admissions for Fall 2025"

## Authors
- Justin Cornell
- Ethan Scott
- Garrick Mills
