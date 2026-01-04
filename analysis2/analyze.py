#!/usr/bin/env python3
"""
Comprehensive Service Call Analysis Script
Analyzes the transcription using LLM to answer compliance and sales questions
with citations from the original transcript.
"""

import json
import os
import re
import time
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Import agent modules
from analysis2.openai_agent import OpenAIAgent, call_llm
from analysis2.perplexity_agent import PerplexityAgent, call_perplexity

# Load environment variables
load_dotenv()

# Initialize agents
openai_agent = OpenAIAgent(default_model="gpt-4o-mini")
perplexity_agent = PerplexityAgent(model="sonar")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TRANSCRIPT_TXT = PROJECT_ROOT / "data" / "transcription.txt"
TRANSCRIPT_JSON = PROJECT_ROOT / "data" / "transcription.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "comprehensive_analysis.json"
CACHE_DIR = PROJECT_ROOT / "data" / ".analysis_cache"
CACHE_DIR.mkdir(exist_ok=True)


# Progress tracking
class ProgressTracker:
    """Simple progress tracker for analysis steps."""
    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
    
    def step(self, step_name: str):
        """Mark completion of a step."""
        self.current_step += 1
        elapsed = time.time() - self.start_time
        percent = (self.current_step / self.total_steps) * 100
        print(f"\n{'='*80}")
        print(f"[{self.current_step}/{self.total_steps}] ({percent:.0f}%) - {step_name}")
        print(f"Elapsed time: {elapsed:.1f}s")
        print(f"{'='*80}")


def save_checkpoint(step_name: str, data: Any):
    """Save intermediate results as checkpoint."""
    checkpoint_file = CACHE_DIR / f"{step_name}_checkpoint.pkl"
    try:
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(data, f)
        print(f"  ✓ Checkpoint saved: {step_name}")
    except Exception as e:
        print(f"  ⚠️  Could not save checkpoint: {e}")


def load_checkpoint(step_name: str) -> Optional[Any]:
    """Load checkpoint if it exists."""
    checkpoint_file = CACHE_DIR / f"{step_name}_checkpoint.pkl"
    if checkpoint_file.exists():
        try:
            with open(checkpoint_file, 'rb') as f:
                data = pickle.load(f)
            print(f"  ✓ Loaded checkpoint: {step_name}")
            return data
        except Exception as e:
            print(f"  ⚠️  Could not load checkpoint: {e}")
    return None


def clear_checkpoints():
    """Clear all cached checkpoints."""
    try:
        for file in CACHE_DIR.glob("*_checkpoint.pkl"):
            file.unlink()
        print("  ✓ Cleared all checkpoints")
    except Exception as e:
        print(f"  ⚠️  Could not clear checkpoints: {e}")


def load_transcription() -> tuple[str, List[Dict]]:
    """Load both text and JSON transcription formats."""
    with open(TRANSCRIPT_TXT, 'r') as f:
        transcript_text = f.read()
    
    with open(TRANSCRIPT_JSON, 'r') as f:
        transcript_json = json.load(f)
    
    return transcript_text, transcript_json['utterances']


def identify_speakers(transcript_text: str) -> Dict[str, str]:
    """Identify which speaker is the customer and which is the technician."""
    system_prompt = """You are an expert at analyzing conversations to identify participants.
Determine which speaker is the customer and which is the technician/service provider."""
    
    prompt = f"""Analyze this service call transcript and determine which speaker is the customer 
and which is the technician.

TRANSCRIPT:
{transcript_text[:2000]}

Return ONLY a JSON object in this exact format:
{{
  "Speaker A": "Customer" or "Technician",
  "Speaker B": "Customer" or "Technician"
}}"""
    
    response = call_llm(prompt, system_prompt, model="gpt-4o")
    
    try:
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        mapping = json.loads(cleaned_response)
        return mapping
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        print(f"  Warning: Could not parse speaker identification: {e}")
        # Default mapping based on typical service call patterns
        return {"Speaker A": "Customer", "Speaker B": "Technician"}


def relabel_transcript(transcript_text: str, speaker_mapping: Dict[str, str]) -> str:
    """Replace Speaker A/B with Customer/Technician in transcript."""
    labeled_text = transcript_text
    for old_label, new_label in speaker_mapping.items():
        labeled_text = labeled_text.replace(f"{old_label}:", f"{new_label}:")
    return labeled_text


def extract_location_info(transcript_text: str) -> Dict[str, Any]:
    """Extract location information from transcript."""
    print("\nExtracting location information...")
    
    system_prompt = """You are an expert at extracting location information from conversations."""
    
    prompt = f"""Extract location information from this service call transcript:

TRANSCRIPT:
{transcript_text[:3000]}

Return JSON format:
{{
  "street_address": "Full street address if mentioned, or null",
  "city": "City name if mentioned, or null",
  "state": "State if mentioned (e.g., 'California'), or null",
  "region": "Region/area if mentioned (e.g., 'Bay Area', 'Northern California'), or null",
  "climate_notes": "Any mentions of local climate/weather"
}}"""
    
    response = call_llm(prompt, system_prompt, model="gpt-4o-mini")
    
    try:
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  Warning: Could not parse location info: {e}")
        return {
            "street_address": None,
            "city": None,
            "state": "California",  # Default assumption
            "region": None,
            "climate_notes": ""
        }


def extract_pricing_mentions(transcript_text: str) -> List[Dict[str, Any]]:
    """Extract all pricing mentions from transcript using regex and LLM."""
    print("\nExtracting pricing mentions...")
    
    # Regex patterns for dollar amounts
    price_pattern = r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:to|-)\s*\$[\d,]+(?:\.\d{2})?)?'
    pricing_mentions = []
    
    for match in re.finditer(price_pattern, transcript_text):
        pricing_mentions.append({
            "raw_text": match.group(),
            "position": match.start()
        })
    
    print(f"  Found {len(pricing_mentions)} pricing mentions via regex")
    
    # Use LLM for structured extraction
    system_prompt = """You are an expert at extracting pricing information from sales conversations."""
    
    prompt = f"""Extract ALL pricing mentions from this transcript. For each price mentioned, identify what it's for.

TRANSCRIPT:
{transcript_text}

Return JSON array:
[
  {{
    "amount": "Price (e.g., '$20,000' or '$15,000-$20,000')",
    "product_or_service": "What this price is for",
    "context": "Brief context around the mention"
  }}
]"""
    
    response = call_llm(prompt, system_prompt, model="gpt-4o-mini")
    
    try:
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        structured_prices = json.loads(cleaned_response)
        return {
            "regex_matches": pricing_mentions,
            "structured_pricing": structured_prices
        }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  Warning: Could not parse pricing info: {e}")
        return {
            "regex_matches": pricing_mentions,
            "structured_pricing": []
        }


def extract_customer_context(client_situation: Dict[str, Any], location_info: Dict[str, Any]) -> str:
    """Build customer context string from extracted information for Perplexity prompts."""
    context_parts = [
        f"Location: {location_info.get('region', '')} {location_info.get('city', '')}, {location_info.get('state', 'California')}".strip()
    ]
    
    if client_situation.get('problem_description'):
        context_parts.append(f"Problem: {client_situation['problem_description']}")
    
    if client_situation.get('current_equipment'):
        context_parts.append(f"Current Equipment: {client_situation['current_equipment']}")
    
    if client_situation.get('other_relevant_details'):
        context_parts.append(f"Other Details: {client_situation['other_relevant_details']}")
    
    if location_info.get('climate_notes'):
        context_parts.append(f"Climate: {location_info['climate_notes']}")
    
    return "\n- ".join(context_parts)


# Perplexity API calls now handled by perplexity_agent module


def deduplicate_products(products_list: List[Dict]) -> List[Dict]:
    """Deduplicate product names that might be variations of the same product."""
    if not products_list:
        return []
    
    seen_products = {}
    unique_products = []
    
    for product in products_list:
        name = product.get('name', '').lower().strip()
        # Simple normalization
        normalized = re.sub(r'[^\w\s]', '', name)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        if normalized and normalized not in seen_products:
            seen_products[normalized] = True
            unique_products.append(product)
        else:
            print(f"  Skipping duplicate product: {name}")
    
    return unique_products


def analyze_customer_objections(transcript_text: str) -> Dict[str, Any]:
    """Analyze customer objections, concerns, and hesitations."""
    print("\nAnalyzing customer objections and concerns...")
    
    system_prompt = """You are an expert at analyzing sales conversations to identify customer objections and concerns."""
    
    prompt = f"""Analyze this service call transcript and identify ALL customer objections, concerns, or hesitations.

TRANSCRIPT:
{transcript_text}

Return JSON format:
{{
  "objections": [
    {{
      "timestamp": "[XXs - YYs]",
      "quote": "Customer's exact words",
      "concern_type": "price/quality/trust/timing/need/other",
      "severity": "high/medium/low",
      "addressed_by_technician": "yes/no/partially",
      "how_addressed": "How technician responded"
    }}
  ],
  "pain_points": [
    {{
      "pain_point": "Description of customer pain point",
      "quote": "Supporting quote if available"
    }}
  ],
  "buying_signals": [
    {{
      "signal": "Positive buying signal observed",
      "quote": "Supporting quote"
    }}
  ],
  "overall_sentiment": "positive/neutral/negative/mixed",
  "readiness_to_buy": "high/medium/low with explanation"
}}"""
    
    response = call_llm(prompt, system_prompt, model="gpt-4o")
    
    try:
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  Warning: Could not parse objections analysis: {e}")
        return {
            "objections": [],
            "pain_points": [],
            "buying_signals": [],
            "overall_sentiment": "unknown",
            "readiness_to_buy": "unknown"
        }


# OpenAI API calls now handled by openai_agent module


def step1_overall_summary(transcript_text: str) -> str:
    """Step 1: Get overall summary of the conversation."""
    print("\n" + "="*80)
    print("STEP 1: Overall Summary")
    print("="*80)
    
    system_prompt = """You are an expert service call analyst. Your task is to provide a 
comprehensive summary of service call conversations, identifying key themes, participants, 
and outcomes."""
    
    prompt = f"""Please provide a comprehensive overall summary of this service call conversation. 
Include:
- Who the participants are (their roles)
- What was the main purpose of the call
- What was discussed
- What was the outcome
- Any notable details

TRANSCRIPT:
{transcript_text}

Please provide a well-structured summary (3-5 paragraphs)."""
    
    summary = call_llm(prompt, system_prompt, model="gpt-4o")
    print(f"\nSummary generated ({len(summary)} characters)")
    return summary


def step2_compliance_questions(transcript_text: str) -> Dict[str, Dict[str, Any]]:
    """Step 2: Answer compliance questions with citations and letter grades."""
    print("\n" + "="*80)
    print("STEP 2: Compliance Questions with Citations and Grades")
    print("="*80)
    
    questions = {
        "introduction": "Did the technician properly greet the customer and introduce themselves/company?",
        "problem_diagnosis": "How did the technician inquire about and understand the customer's issue?",
        "solution_explanation": "Did the technician clearly explain the solution or service performed?",
        "upsell_attempts": "Note if and how the technician attempted to upsell additional services or products.",
        "maintenance_plan": "Did the technician offer any maintenance plans or long-term service agreements?",
        "closing": "How did the technician conclude the call? Did they thank the customer and finish courteously?",
        "call_type": "Identify what kind of service call this is (for example, a repair call, maintenance visit, installation, etc.) based on the conversation.",
        "sales_insights": "Highlight any sales signals or opportunities in the call. For instance, was the customer interested in additional services or did the technician miss cues for an upsell? Provide insights into what was done well or what was missed regarding sales opportunities."
    }
    
    system_prompt = """You are an expert service call compliance analyst. Your job is to analyze 
service call transcripts and answer specific questions about compliance and performance. 

CRITICAL: You must provide SPECIFIC CITATIONS from the transcript. Citations should be:
1. Direct quotes from the transcript (use exact timestamps in format [XXs - YYs])
2. Multiple citations if relevant to fully support your answer
3. Accurate and verifiable against the original transcript

GRADING: Assign a letter grade (A, B, C, D, or F) assessing the technician's performance:
- A (90-100%): Excellent - Exceeds expectations, professional, thorough
- B (80-89%): Good - Meets expectations with minor areas for improvement
- C (70-79%): Satisfactory - Adequate but needs improvement
- D (60-69%): Below expectations - Significant issues present
- F (0-59%): Failing - Critical failures, unprofessional

Format your response as JSON with:
{
  "answer": "Your detailed analysis here",
  "grade": "A, B, C, D, or F",
  "grade_explanation": "Brief explanation of why this grade was assigned",
  "citations": [
    {
      "timestamp": "[12.16s - 12.48s]",
      "speaker": "Customer or Technician",
      "quote": "Exact quote from transcript",
      "relevance": "Why this quote supports the answer"
    }
  ]
}"""
    
    results = {}
    
    for q_key, question in questions.items():
        print(f"\nProcessing: {q_key}")
        
        # Small delay to avoid rate limits
        time.sleep(1)
        
        prompt = f"""Analyze this service call transcript and answer the following question with 
detailed citations from the transcript:

QUESTION: {question}

TRANSCRIPT:
{transcript_text}

Provide your answer in JSON format with the answer and specific citations (timestamps, speaker, quotes).
Be thorough and include multiple citations if they support your analysis."""
        
        response = call_llm(prompt, system_prompt, model="gpt-4o")
        
        # Parse JSON response
        try:
            # Clean up response if it contains markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            parsed = json.loads(cleaned_response)
            results[q_key] = {
                "question": question,
                "answer": parsed.get("answer", ""),
                "grade": parsed.get("grade", "N/A"),
                "grade_explanation": parsed.get("grade_explanation", ""),
                "citations": parsed.get("citations", [])
            }
        except json.JSONDecodeError as e:
            print(f"  Warning: Could not parse JSON response for {q_key}: {e}")
            results[q_key] = {
                "question": question,
                "answer": response,
                "grade": "N/A",
                "grade_explanation": "",
                "citations": []
            }
    
    return results


def step3_structured_analysis(transcript_text: str) -> Dict[str, Any]:
    """Step 3: Provide structured responses about client situation, products, and responses."""
    print("\n" + "="*80)
    print("STEP 3: Structured Analysis (Client Situation, Products, Responses)")
    print("="*80)
    
    system_prompt = """You are an expert sales and service analyst. Analyze service calls to 
extract structured information about the client's situation, products/services presented, 
and client responses."""
    
    prompt = f"""Analyze this service call transcript and provide a structured analysis in JSON format:

1. Client's Situation: What was the problem or need? What were the relevant details about their current equipment/setup?

2. Products and Plans Presented: List each product/plan/option that was presented to the client with:
   - Name/description of the product/plan
   - Key features mentioned
   - Pricing information (if mentioned)
   - Any special terms (rebates, financing, etc.)

3. Client's Response: For each product/plan, what was the client's response? Were they interested, 
   hesitant, declined, or agreed?

TRANSCRIPT:
{transcript_text}

Return JSON in this exact format:
{{
  "client_situation": {{
    "problem_description": "...",
    "current_equipment": "...",
    "other_relevant_details": "..."
  }},
  "products_and_plans": [
    {{
      "name": "...",
      "description": "...",
      "features": ["...", "..."],
      "pricing": "...",
      "special_terms": ["...", "..."],
      "client_response": "...",
      "client_interest_level": "high/medium/low"
    }}
  ],
  "overall_outcome": "..."
}}"""
    
    response = call_llm(prompt, system_prompt, model="gpt-4o")
    
    # Parse JSON response
    try:
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        parsed = json.loads(cleaned_response)
        return parsed
    except json.JSONDecodeError as e:
        print(f"  Warning: Could not parse JSON response: {e}")
        return {
            "client_situation": {"error": "Could not parse response"},
            "products_and_plans": [],
            "overall_outcome": response
        }


def step4_integrated_product_analysis(transcript_text: str, products_list: List[Dict]) -> List[Dict]:
    """Step 4: Analyze interest for mentioned products (integrated into product data)."""
    print("\n" + "="*80)
    print("STEP 4: Product Interest Analysis (Integrated)")
    print("="*80)
    
    system_prompt = """You are an expert at analyzing customer interest in products during sales calls.
Your job is to identify specific reasons why the customer is interested or not interested in each product,
using direct quotes from the conversation when possible."""
    
    enhanced_products = []
    
    for product in products_list:
        product_name = product.get('name', 'Unknown Product')
        print(f"\nAnalyzing interest for: {product_name}")
        
        # Small delay to avoid rate limits
        time.sleep(1)
        
        prompt = f"""Analyze this service call transcript and explain WHY the client is interested or 
not interested in the following product:

PRODUCT: {product_name}
DESCRIPTION: {product.get('description', 'N/A')}
FEATURES: {', '.join(product.get('features', []))}
PRICING: {product.get('pricing', 'N/A')}

TRANSCRIPT:
{transcript_text}

Provide a detailed explanation with:
1. Direct quotes from the customer showing interest or hesitation
2. If no direct quotes exist, provide a hypothesis based on the conversation context
3. Be specific about what factors influenced their interest level

Return JSON format:
{{
  "interest_explanation": "Detailed explanation here",
  "supporting_quotes": [
    {{
      "timestamp": "[XXs - YYs]",
      "quote": "Direct quote",
      "indicates": "interest/disinterest/concern"
    }}
  ],
  "hypothesis": "If no direct quotes, explain hypothesis here"
}}"""
        
        response = call_llm(prompt, system_prompt, model="gpt-4o")
        
        # Create enhanced product with interest analysis integrated
        enhanced_product = product.copy()
        
        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            parsed = json.loads(cleaned_response)
            enhanced_product['interest_analysis'] = parsed
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Warning: Could not parse interest analysis: {e}")
            enhanced_product['interest_analysis'] = {
                "interest_explanation": response,
                "supporting_quotes": [],
                "hypothesis": ""
            }
        
        enhanced_products.append(enhanced_product)
    
    return enhanced_products


def step5b_alternative_product_interest(transcript_text: str, alternative_products_text: str) -> str:
    """Analyze why client might be interested in alternative products."""
    print("\nAnalyzing client interest in alternative products...")
    
    time.sleep(1)
    
    system_prompt = """You are an expert at analyzing customer needs and matching products to those needs."""
    
    prompt = f"""Based on this service call transcript, analyze why the client MIGHT be interested in 
the following alternative products:

ALTERNATIVE PRODUCTS:
{alternative_products_text}

TRANSCRIPT (Customer situation and preferences):
{transcript_text[:3000]}

For each alternative product mentioned above, explain:
1. Which customer needs/concerns it addresses
2. How it compares to what the customer is currently considering
3. Specific features that align with customer's stated preferences (quiet, efficient, etc.)
4. Potential objections or concerns the customer might have

Provide a clear, detailed analysis of potential interest."""
    
    response = call_llm(prompt, system_prompt, model="gpt-4o")
    return response


def step5_perplexity_enhanced_research(transcript_text: str, mentioned_products: List[Dict], 
                                        customer_context: str, location_info: Dict[str, Any]) -> Dict[str, Any]:
    """Step 5: Use Perplexity to research mentioned products AND suggest alternatives."""
    print("\n" + "="*80)
    print("STEP 5: Perplexity Enhanced Product Research")
    print("="*80)
    
    # Build location string
    location_str = f"{location_info.get('region', '')} {location_info.get('city', '')}, {location_info.get('state', 'California')}".strip()
    
    # Deduplicate products first
    unique_products = deduplicate_products(mentioned_products)
    print(f"\nResearching {len(unique_products)} unique products...")
    
    # Research mentioned products
    mentioned_research = []
    for product in unique_products:
        product_name = product.get('name', 'Unknown Product')
        print(f"\nResearching additional info for: {product_name}")
        
        time.sleep(2)  # Delay to avoid rate limits
        
        prompt = f"""Research this HVAC product for a California customer and provide additional information NOT mentioned in the sales call:

PRODUCT: {product_name}
DESCRIPTION FROM CALL: {product.get('description', 'N/A')}
FEATURES MENTIONED: {', '.join(product.get('features', []))}
PRICING MENTIONED: {product.get('pricing', 'Not specified')}

CUSTOMER CONTEXT:
{customer_context}

Please provide:
1. Current market pricing in {location_str} (include installation costs if available, with SOURCE URL)
2. Additional technical specifications not mentioned (SEER, EER, AFUE, capacity, with SOURCE URL)
3. Customer reviews or ratings (with SOURCE URL)
4. Energy efficiency certifications (ENERGY STAR, AHRI, California-specific certifications, with SOURCE URL)
5. Warranty details (with SOURCE URL)
6. California rebates or incentives available (TECH Clean California, utility rebates, with SOURCE URL)

Format your response as:
- [Information point] - Source: [URL]

Focus on factual, verifiable information with sources. Prioritize California-specific pricing and incentives."""
        
        perplexity_result = call_perplexity(prompt)
        
        mentioned_research.append({
            "product_name": product_name,
            "additional_info": perplexity_result.get("content", ""),
            "citations": perplexity_result.get("citations", []),
            "error": perplexity_result.get("error", False)
        })
    
    # Suggest alternative products using dynamic context
    print("\nResearching alternative products...")
    time.sleep(2)
    
    prompt = f"""Based on this HVAC service call in {location_str}, suggest 1-2 alternative heat pump or HVAC 
system products that the technician did NOT mention but might be suitable for this customer.

CUSTOMER CONTEXT:
{customer_context}

For each alternative product (1-2 total), provide:
1. Product name and manufacturer (specific model if possible, with SOURCE URL)
2. Approximate pricing in {location_str} including installation costs (with SOURCE URL)
3. Key features (noise levels in dB, efficiency ratings, special features, with SOURCE URL)
4. Noise level specifications in decibels (with SOURCE URL)
5. Energy efficiency ratings (SEER2, EER2, HSPF2, ENERGY STAR status, with SOURCE URL)
6. California rebates or incentives available (TECH Clean California, utility rebates, with SOURCE URL)
7. Why it would be suitable for THIS customer

Format with sources:
- [Information] - Source: [URL]

Provide 1-2 products with current, verifiable information and California-specific pricing."""
    
    alternative_result = call_perplexity(prompt)
    
    return {
        "mentioned_products_research": mentioned_research,
        "alternative_products_info": alternative_result.get("content", ""),
        "alternative_citations": alternative_result.get("citations", []),
        "error": alternative_result.get("error", False)
    }


def step6_overall_technician_critique(compliance_analysis: Dict, products_analysis: List[Dict]) -> Dict[str, Any]:
    """Generate overall technician performance critique."""
    print("\n" + "="*80)
    print("STEP 6A: Overall Technician Critique")
    print("="*80)
    
    # Extract grades
    grades = {}
    for key, item in compliance_analysis.items():
        if 'grade' in item:
            grades[key] = {
                'grade': item.get('grade', 'N/A'),
                'question': item.get('question', '')
            }
    
    system_prompt = """You are a senior service call quality analyst. Provide a comprehensive 
critique of technician performance across compliance and sales."""
    
    prompt = f"""Based on the following analysis, provide an OVERALL CRITIQUE of the technician's performance:

COMPLIANCE GRADES:
{json.dumps(grades, indent=2)}

NUMBER OF PRODUCTS PRESENTED: {len(products_analysis)}

Provide a comprehensive critique covering:
1. Overall compliance performance (summary of grades)
2. Strengths demonstrated
3. Areas needing improvement
4. Product presentation quality
5. Sales effectiveness
6. Customer rapport and professionalism
7. Key recommendations for improvement

Return JSON format:
{{
  "overall_grade": "A/B/C/D/F based on compliance average",
  "compliance_summary": "Summary of compliance performance",
  "sales_summary": "Summary of sales/product presentation",
  "strengths": ["strength 1", "strength 2", ...],
  "areas_for_improvement": ["area 1", "area 2", ...],
  "key_recommendations": ["recommendation 1", "recommendation 2", ...],
  "overall_assessment": "Comprehensive final assessment"
}}"""
    
    response = call_llm(prompt, system_prompt, model="gpt-4o")
    
    try:
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  Warning: Could not parse critique: {e}")
        return {
            "overall_grade": "N/A",
            "compliance_summary": response,
            "sales_summary": "",
            "strengths": [],
            "areas_for_improvement": [],
            "key_recommendations": [],
            "overall_assessment": ""
        }


def generate_executive_summary(all_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate executive summary with key findings and recommendations."""
    print("\n" + "="*80)
    print("GENERATING EXECUTIVE SUMMARY")
    print("="*80)
    
    # Extract key data
    compliance = all_results.get("step2_compliance_analysis", {})
    products = all_results.get("step4_enhanced_products", [])
    critique = all_results.get("step6_overall_critique", {})
    objections = all_results.get("customer_objections_analysis", {})
    winner = all_results.get("step7_product_comparison", {})
    
    # Count grades
    grades = {}
    for key, item in compliance.items():
        grade = item.get('grade', 'N/A')
        grades[grade] = grades.get(grade, 0) + 1
    
    # Calculate average grade (letter to number)
    grade_values = {'A': 90, 'B': 80, 'C': 70, 'D': 60, 'F': 50}
    total_grade = 0
    grade_count = 0
    for key, item in compliance.items():
        grade = item.get('grade', '')
        if grade in grade_values:
            total_grade += grade_values[grade]
            grade_count += 1
    
    avg_grade_num = total_grade / grade_count if grade_count > 0 else 0
    if avg_grade_num >= 90:
        avg_grade = 'A'
    elif avg_grade_num >= 80:
        avg_grade = 'B'
    elif avg_grade_num >= 70:
        avg_grade = 'C'
    elif avg_grade_num >= 60:
        avg_grade = 'D'
    else:
        avg_grade = 'F'
    
    # Build executive summary
    return {
        "call_outcome": winner.get("winner_product", "Unknown"),
        "overall_grade": avg_grade,
        "grade_distribution": grades,
        "total_products_presented": len(products),
        "customer_readiness": objections.get("readiness_to_buy", "unknown"),
        "customer_sentiment": objections.get("overall_sentiment", "unknown"),
        "key_findings": [
            f"Technician received overall grade of {avg_grade}",
            f"{len(products)} products presented to customer",
            f"Customer readiness to buy: {objections.get('readiness_to_buy', 'unknown')}",
            f"Recommended product: {winner.get('winner_product', 'Unknown')}"
        ],
        "top_recommendations": critique.get("key_recommendations", [])[:3],
        "critical_concerns": [
            obj for obj in objections.get("objections", [])
            if obj.get("severity") == "high"
        ],
        "buying_signals_count": len(objections.get("buying_signals", [])),
        "objections_count": len(objections.get("objections", [])),
        "generated_at": datetime.now().isoformat()
    }


def step7_product_comparison_and_winner(transcript_text: str, enhanced_products: List[Dict], 
                                        perplexity_research: Dict) -> Dict[str, Any]:
    """Step 7: Compare all products and pick a winner."""
    print("\n" + "="*80)
    print("STEP 7: Product Comparison and Winner Selection")
    print("="*80)
    
    system_prompt = """You are an expert HVAC consultant. Analyze all products (those mentioned by the 
technician, with additional research, and alternatives suggested) and determine which is the best fit 
for this specific customer."""
    
    # Prepare enhanced products summary
    mentioned_summary = "\n".join([
        f"- {p.get('name', 'Unknown')}: {p.get('pricing', 'N/A')}\n  Features: {', '.join(p.get('features', []))}\n  Client Interest: {p.get('interest_analysis', {}).get('interest_explanation', 'N/A')[:200]}"
        for p in enhanced_products
    ])
    
    # Get research info
    additional_research = "\n\n".join([
        f"ADDITIONAL RESEARCH FOR {r['product_name']}:\n{r['additional_info']}"
        for r in perplexity_research.get('mentioned_products_research', [])
    ])
    
    prompt = f"""Analyze this service call and determine which HVAC product is the BEST fit for the customer.

CUSTOMER SITUATION (from transcript):
{transcript_text[:3000]}

PRODUCTS MENTIONED BY TECHNICIAN (with client interest analysis):
{mentioned_summary}

ADDITIONAL RESEARCH ON MENTIONED PRODUCTS:
{additional_research}

ALTERNATIVE PRODUCTS FROM RESEARCH:
{perplexity_research.get('alternative_products_info', 'None available')}

ALTERNATIVE PRODUCT INTEREST ANALYSIS:
{perplexity_research.get('alternative_interest_analysis', 'Not available')}

CRITERIA TO EVALUATE:
1. Price range fit for customer's budget
2. Housing configuration compatibility
3. Noise level (customer works from home)
4. Efficiency and energy savings
5. California climate suitability
6. Customer's stated preferences
7. Long-term value

Return detailed JSON:
{{
  "winner_product": "Product name",
  "winner_reasoning": "Detailed explanation of why this is the best choice",
  "comparison_factors": [
    "Factor 1: Analysis",
    "Factor 2: Analysis",
    ...
  ],
  "technician_critique": {{
    "was_right_product": "yes/no/partially",
    "upsell_assessment": "maximum/moderate/minimal - explain",
    "customer_budget_flexibility": "Could customer go higher? Analysis based on conversation mood",
    "critique_bullets": [
      "Critique point 1",
      "Critique point 2",
      ...
    ],
    "overall_summary": "Summary of technician's product recommendations"
  }}
}}"""
    
    response = call_llm(prompt, system_prompt, model="gpt-4o")
    
    try:
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        parsed = json.loads(cleaned_response)
        return parsed
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  Warning: Could not parse comparison: {e}")
        return {
            "winner_product": "Analysis failed",
            "winner_reasoning": response,
            "comparison_factors": [],
            "technician_critique": {}
        }


def main():
    """Run the complete analysis pipeline with progress tracking and checkpointing."""
    print("\n" + "="*80)
    print("SERVICE CALL COMPREHENSIVE ANALYSIS (ENHANCED)")
    print("="*80)
    print(f"\nReading transcription from: {TRANSCRIPT_TXT}")
    print(f"Cache directory: {CACHE_DIR}")
    
    # Initialize progress tracker (11 total steps now)
    progress = ProgressTracker(total_steps=12)
    
    # Load transcription
    transcript_text, transcript_json = load_transcription()
    print(f"Loaded transcript with {len(transcript_json)} utterances")
    
    # Initialize results structure
    results = {
        "metadata": {
            "transcript_file": str(TRANSCRIPT_TXT),
            "total_utterances": len(transcript_json),
            "analysis_model": "gpt-4o",
            "analysis_timestamp": datetime.now().isoformat()
        }
    }
    
    # Step 0: Speaker Identification
    progress.step("Speaker Identification")
    cached = load_checkpoint("speakers")
    if cached:
        speaker_mapping = cached
    else:
        speaker_mapping = identify_speakers(transcript_text)
        save_checkpoint("speakers", speaker_mapping)
    
    labeled_transcript = relabel_transcript(transcript_text, speaker_mapping)
    results["metadata"]["speaker_mapping"] = speaker_mapping
    print(f"Speaker mapping: {speaker_mapping}")
    
    # Step 0.5: Location Extraction
    progress.step("Location & Context Extraction")
    cached = load_checkpoint("location")
    if cached:
        location_info = cached
    else:
        location_info = extract_location_info(labeled_transcript)
        save_checkpoint("location", location_info)
    results["location_info"] = location_info
    print(f"Location: {location_info}")
    
    # Step 0.6: Pricing Extraction
    progress.step("Pricing Extraction")
    cached = load_checkpoint("pricing")
    if cached:
        pricing_info = cached
    else:
        pricing_info = extract_pricing_mentions(labeled_transcript)
        save_checkpoint("pricing", pricing_info)
    results["pricing_info"] = pricing_info
    print(f"Found {len(pricing_info.get('structured_pricing', []))} pricing mentions")
    
    # Step 1: Overall Summary
    progress.step("Overall Summary")
    cached = load_checkpoint("step1")
    if cached:
        results["step1_overall_summary"] = cached
    else:
        results["step1_overall_summary"] = step1_overall_summary(labeled_transcript)
        save_checkpoint("step1", results["step1_overall_summary"])
    
    # Step 2: Compliance Questions with Grades
    progress.step("Compliance Analysis")
    cached = load_checkpoint("step2")
    if cached:
        results["step2_compliance_analysis"] = cached
    else:
        results["step2_compliance_analysis"] = step2_compliance_questions(labeled_transcript)
        save_checkpoint("step2", results["step2_compliance_analysis"])
    
    # Step 3: Structured Analysis
    progress.step("Structured Analysis")
    cached = load_checkpoint("step3")
    if cached:
        results["step3_structured_analysis"] = cached
    else:
        results["step3_structured_analysis"] = step3_structured_analysis(labeled_transcript)
        save_checkpoint("step3", results["step3_structured_analysis"])
    
    # Step 3.5: Customer Objections Analysis
    progress.step("Customer Objections Analysis")
    cached = load_checkpoint("objections")
    if cached:
        results["customer_objections_analysis"] = cached
    else:
        results["customer_objections_analysis"] = analyze_customer_objections(labeled_transcript)
        save_checkpoint("objections", results["customer_objections_analysis"])
    
    # Step 4: Enhanced Product Analysis (interest integrated)
    progress.step("Product Interest Analysis")
    products_list = results["step3_structured_analysis"].get("products_and_plans", [])
    
    if not products_list:
        print("⚠️  No products found in structured analysis. Skipping product-related steps.")
        results["step4_enhanced_products"] = []
    else:
        cached = load_checkpoint("step4")
        if cached:
            results["step4_enhanced_products"] = cached
        else:
            results["step4_enhanced_products"] = step4_integrated_product_analysis(labeled_transcript, products_list)
            save_checkpoint("step4", results["step4_enhanced_products"])
        # Update the structured analysis with enhanced products
        results["step3_structured_analysis"]["products_and_plans"] = results["step4_enhanced_products"]
    
    # Build dynamic customer context for Perplexity
    customer_context = extract_customer_context(
        results["step3_structured_analysis"].get("client_situation", {}),
        location_info
    )
    
    # Step 5: Perplexity Enhanced Research (mentioned + alternatives)
    if results.get("step4_enhanced_products"):
        progress.step("Perplexity Research")
        cached = load_checkpoint("step5")
        if cached:
            results["step5_perplexity_research"] = cached
        else:
            results["step5_perplexity_research"] = step5_perplexity_enhanced_research(
        labeled_transcript,
                results["step4_enhanced_products"],
                customer_context,
                location_info
            )
            save_checkpoint("step5", results["step5_perplexity_research"])
        
        # Step 5B: Alternative Product Interest Analysis
        if results["step5_perplexity_research"].get("alternative_products_info"):
            cached = load_checkpoint("step5b")
            if cached:
                results["step5_perplexity_research"]["alternative_interest_analysis"] = cached
            else:
                alt_interest = step5b_alternative_product_interest(
                    labeled_transcript,
                    results["step5_perplexity_research"]["alternative_products_info"]
                )
                results["step5_perplexity_research"]["alternative_interest_analysis"] = alt_interest
                save_checkpoint("step5b", alt_interest)
    else:
        print("⚠️  Skipping Perplexity research (no products found)")
        results["step5_perplexity_research"] = {}
    
    # Step 6: Overall Technician Critique
    progress.step("Technician Critique")
    cached = load_checkpoint("step6")
    if cached:
        results["step6_overall_critique"] = cached
    else:
        results["step6_overall_critique"] = step6_overall_technician_critique(
            results["step2_compliance_analysis"],
            results.get("step4_enhanced_products", [])
        )
        save_checkpoint("step6", results["step6_overall_critique"])
    
    # Step 7: Product Comparison and Winner
    if results.get("step4_enhanced_products"):
        progress.step("Product Comparison")
        cached = load_checkpoint("step7")
        if cached:
            results["step7_product_comparison"] = cached
        else:
            results["step7_product_comparison"] = step7_product_comparison_and_winner(
                labeled_transcript,
                results["step4_enhanced_products"],
                results.get("step5_perplexity_research", {})
            )
            save_checkpoint("step7", results["step7_product_comparison"])
    else:
        print("⚠️  Skipping product comparison (no products found)")
        results["step7_product_comparison"] = {}
    
    # Step 8: Executive Summary
    progress.step("Executive Summary")
    results["executive_summary"] = generate_executive_summary(results)
    
    # Save results
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    print(f"\nWriting analysis to: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Clear checkpoints after successful completion
    clear_checkpoints()
    
    print(f"\n{'='*80}")
    print(f"✓ ANALYSIS COMPLETE!")
    print(f"{'='*80}")
    print(f"\n📊 Results saved to: {OUTPUT_FILE}")
    print(f"\n📋 Summary:")
    print(f"  - Executive Summary: {results['executive_summary'].get('call_outcome', 'N/A')}")
    print(f"  - Overall Grade: {results['executive_summary'].get('overall_grade', 'N/A')}")
    print(f"  - Products Analyzed: {len(results.get('step4_enhanced_products', []))}")
    print(f"  - Customer Readiness: {results['executive_summary'].get('customer_readiness', 'N/A')}")
    print(f"  - Buying Signals: {results['executive_summary'].get('buying_signals_count', 0)}")
    print(f"  - Objections: {results['executive_summary'].get('objections_count', 0)}")
    print(f"  - Recommended Product: {results.get('step7_product_comparison', {}).get('winner_product', 'N/A')}")
    
    return 0


if __name__ == "__main__":
    exit(main())

