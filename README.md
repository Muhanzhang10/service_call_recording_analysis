# Service Call Recording Analysis

Complete analysis pipeline for evaluating service call quality, compliance, and sales opportunities.

## 🚀 Quick Start

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory with:

```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run Complete Analysis Pipeline

**Phase 1: Transcribe Audio**
```bash
python -m transcribe.transcribe
```
Output: `data/transcription.json`, `data/transcription.txt`

**Phase 2: Label Utterances by Stage**
```bash
python -m analysis.utterance_labeling_phase1
```
Output: `data/transcript_labeled.json`

**Phase 3: Analyze Stage Compliance**
```bash
python -m analysis.stage_analysis_phase2
```
Output: `data/transcript_analyzed.json`

**Phase 4: Add Detailed Annotations**
```bash
python -m analysis.annotate_utterances_phase3
```
Output: `data/annotated_transcript.json` (FINAL)

**Phase 5: View Web Application**
```bash
python3 -m http.server 8000
```
Then open: http://localhost:8000/webapp/

## 📁 Project Structure

```
Takehome/
├── transcribe/
│   └── transcribe.py                 # Audio transcription with AssemblyAI
│
├── analysis/
│   ├── utterance_labeling_phase1.py  # Phase 1: Label utterances by stage
│   ├── stage_analysis_phase2.py      # Phase 2: Compliance analysis
│   └── annotate_utterances_phase3.py # Phase 3: Detailed annotations
│
├── data/
│   ├── 39472_N_Darner_Dr_2.m4a      # Original audio file
│   ├── transcription.json            # Raw transcription (Phase 1)
│   ├── transcript_labeled.json       # Labeled by stage (Phase 2)
│   ├── transcript_analyzed.json      # With compliance analysis (Phase 3)
│   └── annotated_transcript.json     # FINAL: Complete analysis (Phase 4)
│
├── webapp/
│   ├── index.html                    # Web UI
│   ├── styles.css                    # Styling
│   ├── app.js                        # Application logic
│   └── README.md                     # Deployment guide
│
├── requirements.txt                  # Python dependencies
├── .env                              # API keys (not committed)
└── README.md                         # This file
```

## 🎯 Analysis Pipeline

### Phase 1: Utterance Labeling
- Labels each utterance with stage tags (introduction, diagnosis, etc.)
- Identifies speaker roles (Technician vs Customer)
- Creates stage timeline summary

### Phase 2: Compliance Analysis
- Evaluates each stage against 3-5 compliance questions
- Provides YES/PARTIAL/NO answers with evidence
- Calculates compliance scores and quality ratings
- Identifies strengths, gaps, and recommendations

### Phase 3: Detailed Annotations
- Adds inline annotations to critical moments
- Identifies 20-30 key moments worth highlighting
- Categorizes annotations: Success, Warning, Opportunity, etc.
- Generates call type identification and sales insights

### Phase 4: Web Application
- Interactive transcript viewer with annotations
- Side-by-side stage analysis panel
- Color-coded compliance indicators
- Sales insights dashboard

## 📊 Analysis Coverage

The complete analysis includes:

**6 Call Stages:**
1. **Introduction** - Greeting, name, company identification
2. **Problem Diagnosis** - Understanding the customer's issue
3. **Solution Explanation** - Explaining work performed
4. **Upsell Attempts** - Additional services offered
5. **Maintenance Plan** - Long-term service agreements
6. **Closing** - Thank you and wrap-up

**18 Compliance Questions Total** (3 per stage)

**Additional Analysis:**
- Call Type Identification
- Sales Opportunities (captured & missed)
- Customer Buying Signals
- Overall Compliance Score
- Sales Performance Rating
