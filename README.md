# Service Call Recording Analysis

Complete analysis pipeline for evaluating service call quality, compliance, and sales opportunities.

## 🌐 Live Demo

**👉 [View Live Analysis Demo](https://muhanzhang10.github.io/service_call_recording_analysis/webapp2/)**

Experience the interactive web application showcasing a complete service call analysis with:
- Comprehensive technician performance critique
- Client insights for advertising and sales
- Compliance analysis with letter grades
- Sales evaluation metrics
- Product-client alignment assessment
- Full annotated transcript

---

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

**Step 1: Transcribe Audio**
```bash
python -m transcribe.transcribe
```
Output: `data/transcription.json`, `data/transcription.txt`

**Step 2: Run Comprehensive Analysis (16 Steps)**
```bash
python -m analysis2.analyze
```
Output: `data/comprehensive_analysis.json` (FINAL)

This will execute all 16 analysis steps including:
- Speaker identification and compliance analysis
- Client insights extraction and product research
- Sales evaluation and technician critique
- Product-client alignment assessment
- Executive summary with recommendations

**Step 3: View Web Application**
```bash
python3 -m http.server 8000
```
Then open: http://localhost:8000/webapp2/

**Optional: Run Selective Steps**
```bash
# Run specific steps only
python -m analysis2.analyze --steps 14 11 15

# Run from step 10 onwards
python -m analysis2.analyze --from 10

# List all available steps
python -m analysis2.analyze --list
```

## 📁 Project Structure

```
Takehome/
├── transcribe/
│   └── transcribe.py                 # Audio transcription with AssemblyAI
│
├── analysis2/                        # ⭐ MAIN ANALYSIS PIPELINE
│   ├── analyze.py                    # 16-step comprehensive analysis
│   ├── openai_agent.py               # OpenAI LLM interface
│   ├── perplexity_agent.py           # Perplexity AI research interface
│   ├── USAGE_GUIDE.md                # Detailed usage instructions
│   └── README.md                     # Pipeline documentation
│
├── analysis/                         # (Legacy pipeline - replaced by analysis2)
│   ├── utterance_labeling_phase1.py  # Stage labeling
│   ├── stage_analysis_phase2.py      # Compliance analysis
│   └── annotate_utterances_phase3.py # Annotations
│
├── data/
│   ├── transcription.json            # Raw transcription from AssemblyAI
│   ├── transcription.txt             # Human-readable transcript
│   ├── comprehensive_analysis.json   # ⭐ FINAL OUTPUT (from analysis2)
│   └── .analysis_cache/              # Checkpoint files for resuming
│
├── webapp2/                          # ⭐ CURRENT WEB APPLICATION
│   ├── index.html                    # Interactive viewer
│   ├── styles.css                    # Modern styling
│   ├── app.js                        # Application logic
│   └── README.md                     # Deployment guide
│
├── webapp/                           # (Legacy viewer)
│   └── ...
│
├── requirements.txt                  # Python dependencies
├── .env                              # API keys (OPENAI_API_KEY, ASSEMBLYAI_API_KEY)
└── README.md                         # This file
```

## 🎯 Analysis Pipeline

### Overview: What This Analysis Incorporates

The comprehensive analysis evaluates service calls across three critical dimensions:

#### **Technician Performance Critique**
1. **Compliance Performance** - Adherence to service call standards and protocols
2. **Sales & Product Presentation** - Quality of product demonstrations and sales techniques
3. **Product-Client Alignment** - Match between recommended products and customer needs

#### **Client Insights for Advertising & Sales**
- Customer demographics, lifestyle, and preferences
- Pain points, motivations, and decision-making patterns
- Targeted messaging recommendations
- Personalized sales strategies

---

### 16-Step Analysis Process (analysis2/)

**Step 0: Speaker Identification**
- Automatically identifies Customer vs Technician roles
- Relabels transcript for clarity

**Step 1: Location & Context Extraction**
- Extracts address, city, state, region
- Identifies climate notes and environmental context

**Step 2: Pricing Extraction**
- Uses regex and LLM to extract all pricing mentions
- Structured analysis of product costs and financial details

**Step 3: Overall Summary**
- Comprehensive 3-5 paragraph summary of the call
- Identifies participants, purpose, discussion points, and outcomes

**Step 4: Compliance Analysis**
- Evaluates 8 compliance categories with letter grades (A-F):
  - Introduction quality
  - Problem diagnosis approach
  - Solution explanation clarity
  - Upsell attempts and techniques
  - Maintenance plan offerings
  - Closing professionalism
  - Call type identification
  - Sales insights and opportunities
- Provides detailed answers with direct transcript citations
- Assigns letter grades with explanations

**Step 5: Structured Analysis (Client & Products)**
- Extracts client situation (problem, equipment, details)
- Identifies all products and plans presented
- Documents features, pricing, special terms
- Records client response and interest level

**Step 6: Customer Objections Analysis**
- Catalogs all objections, concerns, and hesitations
- Identifies pain points and buying signals
- Evaluates objection severity and handling quality
- Assesses overall customer sentiment and readiness to buy

**Step 7: Product Interest Analysis**
- Deep analysis of WHY customer is/isn't interested in each product
- Supporting quotes and timestamp citations
- Interest explanations with hypotheses

**Step 8: Perplexity Research (AI-Enhanced)**
- Real-time research on mentioned products (pricing, specs, reviews)
- California-specific rebates and incentives
- Alternative product suggestions with market data
- Sourced citations for all information

**Step 9: Speaking Time Analysis**
- Calculates technician vs. customer speaking time ratio
- Evaluates adherence to 70/30 rule (customer speaks 70%)
- Identifies time spent on products vs. listening

**Step 10: Sales Evaluation (4 Graded Metrics)**
- **Building Rapport**: Introduction, name usage, active listening, comfort level
- **Handling Objections**: Acknowledgment, clarification, response quality
- **Speaking Time (70/30 Rule)**: Balance analysis and recommendations
- **Upselling Performance**: Success assessment and missed opportunities

**Step 11: Overall Technician Critique**
- Comprehensive performance evaluation across compliance, sales, and product alignment
- Individual grades for:
  - Compliance performance
  - Sales effectiveness
  - **Product-Client Alignment** (critical assessment)
- Strengths and areas for improvement
- Actionable recommendations

**Step 12: Product Comparison & Winner Selection**
- Evaluates all products (mentioned + alternatives) against customer needs
- Selects best-fit product with detailed reasoning
- Critiques technician's recommendations
- Assesses upsell approach and budget flexibility

**Step 13: [Reserved for future use]**

**Step 14: Client Insights Extraction** 🎯
Comprehensive profiling for advertising and sales:
- **Demographic Profile**: Family status, home details, work situation, age indicators
- **Lifestyle Preferences**: Comfort needs, environmental consciousness, tech-savviness, budget sensitivity
- **Pain Points & Motivations**: Primary/secondary concerns with severity ratings
- **Communication Profile**: Decision style, information preferences, trust level
- **Purchase Behavior**: Budget range, financing interest, decision timeline
- **Advertising Insights**: Resonant messaging, recommended channels, value propositions
- **Sales Strategy**: Best approach, follow-up emphasis, personalization opportunities
- **Client Archetype**: Summary classification for targeting

**Step 15: Executive Summary**
- Overall grade (A-F) incorporating compliance, sales, AND product alignment
- Grade distribution and key findings
- Customer readiness and sentiment
- Technician performance summary with product alignment assessment
- Sales evaluation summary (all 4 metrics)
- Client insights summary for advertising/sales teams
- Critical concerns and top recommendations

---

### Command-Line Execution

**Run all steps:**
```bash
python -m analysis2.analyze
```

**Run specific steps:**
```bash
python -m analysis2.analyze --steps 10 11 15  # Sales Eval + Critique + Summary
python -m analysis2.analyze --steps 14 11 15  # Client Insights + Critique + Summary
```

**Run from a step onwards:**
```bash
python -m analysis2.analyze --from 10  # Run steps 10-15
```

**Clear cache and restart:**
```bash
python -m analysis2.analyze --clear
```

**List all available steps:**
```bash
python -m analysis2.analyze --list
```

---

## 📊 Analysis Output

**Output File:** `data/comprehensive_analysis.json`

The final output includes:
- Full transcript with speaker identification
- Location and pricing information
- Compliance analysis with 8 graded evaluations
- Structured client situation and product data
- Customer objections with severity ratings
- AI-enhanced product research with citations
- Sales evaluation (4 graded metrics)
- Overall technician critique with product alignment assessment
- Product comparison and winner recommendation
- **Client insights for advertising/sales teams**
- Executive summary with actionable recommendations

**Key Metrics:**
- Overall Performance Grade (A-F)
- Compliance Grade
- Sales Grade
- **Product-Client Alignment Grade** ⭐
- Speaking Time Ratio
- Customer Readiness Score
- Buying Signals vs. Objections Count
