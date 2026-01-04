# Comprehensive Service Call Analysis - Web Application

This web application presents a comprehensive analysis of the service call recording, including:

## Features

### 📋 Overall Summary
- High-level overview of the entire conversation
- Key participants and their roles
- Main purpose and outcomes
- Quick statistics (duration, utterances, call type)

### ✓ Compliance Check
- Detailed evaluation of standard service call procedures:
  - Introduction
  - Problem Diagnosis
  - Solution Explanation
  - Upsell Attempts
  - Maintenance Plan Offer
  - Closing & Thank You
  - Call Type Identification
  - Sales Insights
- **Citations**: Each answer includes specific quotes from the transcript with timestamps

### 📊 Client Situation & Products
- Client's situation analysis
- All products and plans presented during the call
- Features, pricing, and special terms
- Client's response to each product/plan
- Interest level indicators

### 📝 Full Transcript
- Complete conversation with speaker labels
- Toggleable timestamps
- Easy-to-read format

## Running the Application

### Option 1: Using the deployment script
```bash
python run_webapp.py 2
```

Then open your browser to: http://localhost:8000/webapp2/

### Option 2: Manual setup
```bash
cd /path/to/Takehome
python -m http.server 8000
```

Then navigate to: http://localhost:8000/webapp2/

## Prerequisites

Before running the web application, you need to:

1. **Generate the analysis data** by running the analysis script:
   ```bash
   cd analysis2
   python analyze.py
   ```

2. This will create `data/comprehensive_analysis.json` which the web app reads.

3. Make sure you have your OpenAI API key set:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   Or create a `.env` file with:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## File Structure

```
webapp2/
├── index.html      # Main HTML structure
├── styles.css      # Styling and layout
├── app.js          # JavaScript for data loading and rendering
└── README.md       # This file
```

## Technology Stack

- **Frontend**: Pure HTML, CSS, JavaScript (no frameworks)
- **Analysis**: Python with OpenAI GPT-4
- **Data Format**: JSON

## Design Philosophy

This application focuses on **clarity and readability** rather than complex features:
- Clean, modern UI with intuitive navigation
- Tab-based organization for easy access to different analysis sections
- Citations with timestamps for transparency and verifiability
- Responsive design that works on desktop and mobile devices

## Analysis Model

The analysis is performed using OpenAI's GPT-4 model, which provides:
- Deep understanding of conversation context
- Accurate identification of compliance elements
- Detailed sales opportunity analysis
- Specific citations with timestamps

## Notes

- The analysis is generated automatically but should be reviewed for accuracy
- Citations link directly to specific moments in the transcript
- The client response analysis helps identify successful sales techniques and missed opportunities


