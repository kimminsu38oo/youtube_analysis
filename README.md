# 📺 AlgoView analysis server

A FastAPI-based API that analyzes a user's YouTube watch history, likes, and subscriptions to provide hourly statistics, keyword frequency, and behavioral insights.

## Features

* Hourly view counts and top 3 channels per time slot
* Keyword frequency analysis
* LLM-generated summary of user behavior

## Prerequisites

* Python 3.11.8 (tested)
* history.json
* liked_videos.json
* subscriptions.json

## Installation

1. **Clone the Repository**
```bash
git clone https://github.com/kimminsu38oo/youtube_analysis.git
cd youtube_analysis_server
```

2. **Set Up a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
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

3. **Example Request**
   * Endpoint: POST /analyze
   * Body:
```json
{
  "history_data": {...},
  "likes_data": {...},
  "subscriptions_data": {...}
}
```
   * Response:
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