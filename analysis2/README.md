# Analysis2 - Modular Service Call Analysis

A modular, agent-based system for comprehensive HVAC service call transcript analysis.

## Architecture

The analysis system is now modularized into specialized agents:

```
analysis2/
├── __init__.py              # Package initialization
├── analyze.py               # Main analysis orchestrator
├── openai_agent.py          # OpenAI API agent
├── perplexity_agent.py      # Perplexity AI agent
└── README.md                # This file
```

## Modules

### 1. OpenAI Agent (`openai_agent.py`)

Handles all OpenAI API interactions for transcript analysis.

**Key Features:**
- Automatic retry logic with exponential backoff
- JSON response parsing with error handling
- Citation extraction and grading support
- Structured data extraction
- Text summarization

**Usage:**
```python
from analysis2.openai_agent import OpenAIAgent

# Initialize agent
agent = OpenAIAgent(default_model="gpt-4o-mini")

# Simple query
response = agent.query("Analyze this transcript...", system_prompt="You are an expert...")

# Query with citations and grading
result = agent.analyze_with_citations(transcript, "Did the technician greet properly?")
# Returns: {"answer": "...", "grade": "A", "citations": [...]}

# Extract structured data
schema = {"client_situation": {"problem": "...", "equipment": "..."}}
data = agent.extract_structured_data(transcript, schema)

# Summarize text
summary = agent.summarize(transcript, max_length=500)
```

**Methods:**
- `query()` - Basic query with retry logic
- `parse_json_response()` - Parse JSON with code block handling
- `analyze_with_citations()` - Analysis with grading and citations
- `extract_structured_data()` - Schema-based data extraction
- `summarize()` - Text summarization

### 2. Perplexity Agent (`perplexity_agent.py`)

Handles all Perplexity AI interactions for real-time product research.

**Key Features:**
- Web search with source citations
- California-specific HVAC expertise
- Automatic retry logic
- Rate limit handling
- Product research templates

**Usage:**
```python
from analysis2.perplexity_agent import PerplexityAgent

# Initialize agent
agent = PerplexityAgent(model="sonar")

# Simple query
result = agent.query("What is the price of a heat pump in California?")
# Returns: {"content": "...", "citations": ["https://...", ...], "error": False}

# Research specific product
customer_context = "Working from home, needs quiet system, Budget: $20k-30k"
result = agent.research_product(
    product_name="Daikin Heat Pump",
    product_description="High efficiency heat pump",
    customer_context=customer_context,
    location="Bay Area, California"
)

# Suggest alternative products
result = agent.suggest_alternatives(
    customer_context=customer_context,
    location="California"
)
```

**Methods:**
- `query()` - Basic query with citations
- `research_product()` - Deep dive on specific HVAC product
- `suggest_alternatives()` - Get alternative product recommendations

### 3. Main Orchestrator (`analyze.py`)

Coordinates the complete analysis pipeline using both agents.

**Features:**
- 12-step analysis pipeline
- Progress tracking
- Checkpoint/caching system
- Location and pricing extraction
- Customer objections analysis
- Executive summary generation

## Installation

```bash
# Ensure you're in the project directory
cd /path/to/Takehome

# Activate virtual environment
source takehome/bin/activate

# Install dependencies (already installed)
pip install openai python-dotenv requests
```

## Configuration

Set up your `.env` file:

```bash
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
```

## Running Analysis

```bash
# Run full analysis
python -m analysis2.analyze

# Or directly
cd analysis2
python analyze.py
```

## Agent Configuration

### OpenAI Agent Options

```python
agent = OpenAIAgent(
    api_key="sk-...",           # Optional, uses env var if not provided
    default_model="gpt-4o-mini"  # Default model for queries
)

# Override model per query
response = agent.query(prompt, model="gpt-4o")
```

### Perplexity Agent Options

```python
agent = PerplexityAgent(
    api_key="pplx-...",  # Optional, uses env var if not provided
    model="sonar"        # Model to use for queries
)

# Custom system prompt
result = agent.query(
    prompt="Research HVAC pricing...",
    system_prompt="You are a California HVAC expert..."
)
```

## Error Handling

Both agents include comprehensive error handling:

- **Rate Limits**: Automatic exponential backoff retry
- **Timeouts**: Configurable timeout with retry
- **API Errors**: Graceful degradation with error reporting
- **JSON Parsing**: Robust parsing with fallback

## Backwards Compatibility

Convenience functions are provided for backwards compatibility:

```python
from analysis2 import call_llm, call_perplexity

# Old-style usage still works
response = call_llm(prompt, system_prompt, model="gpt-4o-mini")
result = call_perplexity(prompt, model="sonar")
```

## Caching System

Analysis results are cached in `data/.analysis_cache/`:

```python
# Load checkpoint for specific step
from analysis2.analyze import load_checkpoint
data = load_checkpoint("step3")

# Save checkpoint
from analysis2.analyze import save_checkpoint
save_checkpoint("step3", my_data)

# Clear all checkpoints
from analysis2.analyze import clear_checkpoints
clear_checkpoints()
```

## Output Structure

Complete analysis is saved to `data/comprehensive_analysis.json`:

```json
{
  "metadata": {
    "analysis_timestamp": "2026-01-04T...",
    "speaker_mapping": {...}
  },
  "executive_summary": {
    "overall_grade": "B",
    "customer_readiness": "high",
    "buying_signals_count": 5,
    ...
  },
  "location_info": {...},
  "pricing_info": {...},
  "customer_objections_analysis": {...},
  "step1_overall_summary": "...",
  "step2_compliance_analysis": {...},
  "step3_structured_analysis": {...},
  "step4_enhanced_products": [...],
  "step5_perplexity_research": {
    "mentioned_products_research": [
      {
        "product_name": "...",
        "additional_info": "...",
        "citations": ["https://...", ...]
      }
    ],
    "alternative_products_info": "...",
    "alternative_citations": [...]
  },
  "step6_overall_critique": {...},
  "step7_product_comparison": {...}
}
```

## Testing

Test individual agents:

```python
# Test OpenAI agent
from analysis2.openai_agent import OpenAIAgent
agent = OpenAIAgent()
response = agent.query("Hello, world!")
print(response)

# Test Perplexity agent
from analysis2.perplexity_agent import PerplexityAgent
agent = PerplexityAgent()
result = agent.query("What is the best heat pump in California?")
print(result['content'])
print(f"Sources: {result['citations']}")
```

## Benefits of Modular Architecture

1. **Separation of Concerns**: Each agent handles one API
2. **Reusability**: Agents can be used independently
3. **Testability**: Easy to test agents in isolation
4. **Maintainability**: Changes to one agent don't affect others
5. **Extensibility**: Easy to add new agents (e.g., Claude, Gemini)

## Future Enhancements

Potential additions:
- `anthropic_agent.py` - Claude integration
- `google_agent.py` - Gemini integration
- `validation_agent.py` - Cross-validation between sources
- `storage_agent.py` - Database persistence
- `report_agent.py` - PDF/HTML report generation

## License

See main project LICENSE file.

## Support

For issues or questions, refer to the main project documentation:
- `QUICKSTART_ANALYSIS2.md` - Quick start guide
- `README_ANALYSIS2.md` - Detailed documentation
- `IMPROVEMENTS_LOG.md` - Recent enhancements
