# 📺 AlgoView Analysis Server

A FastAPI-based API that analyzes a user's YouTube watch history, likes, and subscriptions to provide hourly statistics, keyword frequency, and behavioral insights. Now featuring real-time streaming analysis!

## Features

* Hourly view counts and top 3 channels per time slot
* Keyword frequency analysis
* LLM-generated summary of user behavior
* Real-time streaming analysis with incremental results

## Prerequisites

* Python 3.12.3 (tested)
* history.json and subscriptions.json from your YouTube data
* OpenAI API key

## Installation

1. **Clone the Repository**
```bash
git clone https://github.com/kimminsu38oo/youtube_analysis.git
cd youtube_analysis
```

2. **Set Up a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate # On macOS/Linux
venv\Scripts\activate # On Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Set Up Environment Variables**
```bash
# Create a .env file in the project root
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

## Usage

1. **Run the API**
```bash
cd analysis
uvicorn app.main:app --reload
```
* The API will be available at http://127.0.0.1:8000.

2. **Access the Interactive Docs**
   * Open your browser and go to http://127.0.0.1:8000/docs for the Swagger UI.

## API Endpoints

### Traditional Analysis Endpoint
**Endpoint**: `POST /api/v1/analysis/{analysis_id}`
**Request**: Upload two files - `history_file` and `subscriptions_file`
**Response**: Returns a complete analysis in a single response

```json
{
  "status": "success",
  "data": {
    "hourlyStats": [...],
    "keywordFrequency": [...],
    "llmAnalysis": "User tends to watch entertainment content in the evening."
  }
}
```

### Streaming Analysis Endpoint
**Endpoint**: `POST /api/v1/analysis-stream/{analysis_id}`
**Request**: Upload two files - `history_file` and `subscriptions_file`
**Response**: Streams analysis results incrementally as they're processed

1. **Hourly Statistics Analysis**
```json
{
  "function": "hourly_stats",
  "status": "success",
  "data": [
    {
      "hour": 0,
      "totalViews": 0,
      "categories": []
    },
    {
      "hour": 18,
      "totalViews": 200,
      "categories": [
        {"name": "Entertainment", "views": 121},
        {"name": "Education", "views": 79}
      ]
    }
  ]
}
```

2. **Keyword Analysis**
```json
{
  "function": "keyword_frequency",
  "status": "success",
  "data": [
    {"keyword": "Music", "frequency": 150},
    {"keyword": "Gaming", "frequency": 100},
    {"keyword": "Entertainment", "frequency": 80},
    {"keyword": "Education", "frequency": 60},
    {"keyword": "Sports", "frequency": 40}
  ]
}
```

3. **LLM Analysis**
```json
{
  "function": "llm_analysis",
  "status": "success",
  "data": "The user tends to watch YouTube mainly during evening hours (18-20), with a preference for entertainment and educational content. Key interests include music and gaming. The viewing pattern suggests YouTube is primarily used for relaxation after work hours."
}
```

4. **Completion Message**
```json
{
  "function": "completion",
  "status": "success",
  "message": "Analysis completed successfully."
}
```

## Testing the Streaming API
You can test the streaming functionality using the included `test.html` file:
1. Open the `test.html` file in your web browser
2. Enter the server URL (default: http://localhost:8000)
3. Upload your history.json and subscriptions.json files
4. Click "Start Analysis" to see the real-time streaming results
5. Each analysis component will update as soon as it's processed by the server

The test page includes a visualization of hourly statistics, keyword frequency tags, and the LLM analysis, all updating in real-time as data is received from the server.

## Client Implementation
To consume the streaming endpoint, clients should process each JSON response as it arrives. The test.html file provides a reference implementation for handling the streamed responses.