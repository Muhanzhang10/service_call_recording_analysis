#!/usr/bin/env python3
"""
OpenAI Agent Module
Handles all interactions with OpenAI API for transcript analysis.
"""

import os
import time
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from openai import RateLimitError, APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class OpenAIAgent:
    """Agent for interacting with OpenAI API."""
    
    def __init__(self, api_key: str = None, default_model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI agent.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            default_model: Default model to use (default: "gpt-4o-mini")
        """
        self.client = OpenAI(api_key=api_key) if api_key else client
        self.default_model = default_model
    
    def query(self, prompt: str, system_prompt: str = None, 
             model: str = None, temperature: float = 0.3, 
             max_retries: int = 5) -> str:
        """
        Make a query to OpenAI API with retry logic.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            model: Model to use (uses default if not specified)
            temperature: Temperature for response randomness (default: 0.3)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response text from the model
        """
        model = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                return response.choices[0].message.content
                
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    print(f"\n⚠️  Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    print(f"\n❌ Rate limit error after {max_retries} attempts: {e}")
                    return f"Error: Rate limit exceeded after {max_retries} retries"
                    
            except APIError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    print(f"\n⚠️  API error. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    print(f"\n❌ API error after {max_retries} attempts: {e}")
                    return f"Error: API error after {max_retries} retries"
                    
            except Exception as e:
                print(f"\n❌ Unexpected error calling OpenAI: {e}")
                return f"Error: {str(e)}"
        
        return "Error: Maximum retries exceeded"
    
    def parse_json_response(self, response: str) -> Optional[Dict]:
        """
        Parse JSON response from LLM, handling code blocks.
        
        Args:
            response: Raw response string from LLM
            
        Returns:
            Parsed dict or None if parsing fails
        """
        try:
            cleaned = response.strip()
            
            # Remove markdown code blocks
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Warning: Could not parse JSON response: {e}")
            return None
    
    def analyze_with_citations(self, transcript: str, question: str, 
                               model: str = "gpt-4o") -> Dict[str, Any]:
        """
        Analyze transcript with citations and grading.
        
        Args:
            transcript: Full transcript text
            question: Question to analyze
            model: Model to use (default: gpt-4o for better reasoning)
            
        Returns:
            Dict with answer, grade, citations
        """
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
        
        prompt = f"""Analyze this service call transcript and answer the following question with 
detailed citations from the transcript:

QUESTION: {question}

TRANSCRIPT:
{transcript}

Provide your answer in JSON format with the answer and specific citations (timestamps, speaker, quotes).
Be thorough and include multiple citations if they support your analysis."""
        
        response = self.query(prompt, system_prompt, model=model)
        parsed = self.parse_json_response(response)
        
        if parsed:
            return {
                "question": question,
                "answer": parsed.get("answer", ""),
                "grade": parsed.get("grade", "N/A"),
                "grade_explanation": parsed.get("grade_explanation", ""),
                "citations": parsed.get("citations", [])
            }
        else:
            return {
                "question": question,
                "answer": response,
                "grade": "N/A",
                "grade_explanation": "",
                "citations": []
            }
    
    def extract_structured_data(self, transcript: str, schema: Dict[str, Any], 
                               model: str = "gpt-4o") -> Dict[str, Any]:
        """
        Extract structured data from transcript based on schema.
        
        Args:
            transcript: Full transcript text
            schema: Dict describing the expected structure
            model: Model to use
            
        Returns:
            Extracted structured data
        """
        system_prompt = """You are an expert at extracting structured information from conversations.
Extract the requested information accurately and format it as specified."""
        
        prompt = f"""Extract information from this transcript and format it according to the schema below.

TRANSCRIPT:
{transcript}

SCHEMA:
{json.dumps(schema, indent=2)}

Return your response as valid JSON matching the schema."""
        
        response = self.query(prompt, system_prompt, model=model)
        parsed = self.parse_json_response(response)
        
        return parsed if parsed else {"error": "Could not parse response", "raw": response}
    
    def summarize(self, text: str, max_length: int = None, 
                 model: str = "gpt-4o") -> str:
        """
        Generate a summary of the given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length hint (optional)
            model: Model to use
            
        Returns:
            Summary text
        """
        system_prompt = """You are an expert service call analyst. Your task is to provide 
comprehensive summaries of service call conversations, identifying key themes, participants, 
and outcomes."""
        
        length_instruction = f" Keep the summary under {max_length} words." if max_length else ""
        
        prompt = f"""Please provide a comprehensive summary of this service call conversation.{length_instruction}
Include:
- Who the participants are (their roles)
- What was the main purpose of the call
- What was discussed
- What was the outcome
- Any notable details

TRANSCRIPT:
{text}

Please provide a well-structured summary (3-5 paragraphs)."""
        
        return self.query(prompt, system_prompt, model=model)


# Convenience function for backwards compatibility
def call_llm(prompt: str, system_prompt: str = None, 
            model: str = "gpt-4o-mini", max_retries: int = 5) -> str:
    """
    Convenience function to make an OpenAI query.
    
    Args:
        prompt: User prompt
        system_prompt: System prompt (optional)
        model: Model to use
        max_retries: Maximum retry attempts
        
    Returns:
        Response text from the model
    """
    agent = OpenAIAgent(default_model=model)
    return agent.query(prompt, system_prompt, model=model, max_retries=max_retries)

