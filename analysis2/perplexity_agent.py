#!/usr/bin/env python3
"""
Perplexity AI Agent Module
Handles all interactions with Perplexity API for HVAC product research.
"""

import os
import time
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Perplexity API key
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')


class PerplexityAgent:
    """Agent for interacting with Perplexity API."""
    
    def __init__(self, api_key: str = None, model: str = "sonar"):
        """
        Initialize Perplexity agent.
        
        Args:
            api_key: Perplexity API key (uses env var if not provided)
            model: Model to use for queries (default: "sonar")
        """
        self.api_key = api_key or PERPLEXITY_API_KEY
        self.model = model
        self.url = "https://api.perplexity.ai/chat/completions"
        
        if not self.api_key:
            print("⚠️  Warning: PERPLEXITY_API_KEY not found in environment")
    
    def query(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        Make a query to Perplexity API with retry logic.
        
        Args:
            prompt: User prompt/question
            system_prompt: System prompt (optional, uses default HVAC expert if not provided)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict with 'content', 'citations', and 'error' keys
        """
        if not self.api_key:
            return {
                "content": "Error: PERPLEXITY_API_KEY not found in environment",
                "citations": [],
                "error": True
            }
        
        # Default system prompt for HVAC expertise
        if system_prompt is None:
            system_prompt = (
                "You are a helpful HVAC industry expert specializing in California markets. "
                "Provide accurate product information, pricing specific to California/Bay Area "
                "when available, and cite reliable sources."
            )
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "search_recency_filter": "month",
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                # Extract content and citations
                content = result['choices'][0]['message']['content']
                citations = result.get('citations', [])
                
                return {
                    "content": content,
                    "citations": citations,
                    "error": False
                }
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        wait_time = 2 ** (attempt + 1)
                        print(f"\n⚠️  Perplexity rate limit hit. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        print(f"\n❌ Perplexity rate limit error after {max_retries} attempts")
                        return {"content": f"Error: Rate limit exceeded", "citations": [], "error": True}
                else:
                    print(f"\n❌ Perplexity HTTP error: {e}")
                    return {"content": f"Error: {str(e)}", "citations": [], "error": True}
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"\n⚠️  Perplexity timeout. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"\n❌ Perplexity timeout after {max_retries} attempts")
                    return {"content": "Error: Request timeout", "citations": [], "error": True}
                    
            except Exception as e:
                print(f"\n❌ Error calling Perplexity: {e}")
                return {"content": f"Error: {str(e)}", "citations": [], "error": True}
        
        return {"content": "Error: Maximum retries exceeded", "citations": [], "error": True}
    
    def research_product(self, product_name: str, product_description: str, 
                        customer_context: str, location: str = "California") -> Dict[str, Any]:
        """
        Research an HVAC product with California-specific context.
        
        Args:
            product_name: Name of the product
            product_description: Description from sales call
            customer_context: Customer situation and requirements
            location: Location string (default: "California")
            
        Returns:
            Dict with research results, citations, and error status
        """
        prompt = f"""Research this HVAC product for a {location} customer and provide additional information NOT mentioned in the sales call:

PRODUCT: {product_name}
DESCRIPTION FROM CALL: {product_description}

CUSTOMER CONTEXT:
{customer_context}

Please provide:
1. Current market pricing in {location} (include installation costs if available, with SOURCE URL)
2. Additional technical specifications not mentioned (SEER, EER, AFUE, capacity, with SOURCE URL)
3. Customer reviews or ratings (with SOURCE URL)
4. Energy efficiency certifications (ENERGY STAR, AHRI, California-specific certifications, with SOURCE URL)
5. Warranty details (with SOURCE URL)
6. California rebates or incentives available (TECH Clean California, utility rebates, with SOURCE URL)

Format your response as:
- [Information point] - Source: [URL]

Focus on factual, verifiable information with sources. Prioritize California-specific pricing and incentives."""
        
        return self.query(prompt)
    
    def suggest_alternatives(self, customer_context: str, location: str = "California") -> Dict[str, Any]:
        """
        Suggest alternative HVAC products based on customer needs.
        
        Args:
            customer_context: Customer situation and requirements
            location: Location string (default: "California")
            
        Returns:
            Dict with alternative product suggestions, citations, and error status
        """
        prompt = f"""Based on this HVAC service call in {location}, suggest 1-2 alternative heat pump or HVAC 
system products that the technician did NOT mention but might be suitable for this customer.

CUSTOMER CONTEXT:
{customer_context}

For each alternative product (1-2 total), provide:
1. Product name and manufacturer (specific model if possible, with SOURCE URL)
2. Approximate pricing in {location} including installation costs (with SOURCE URL)
3. Key features (noise levels in dB, efficiency ratings, special features, with SOURCE URL)
4. Noise level specifications in decibels (with SOURCE URL)
5. Energy efficiency ratings (SEER2, EER2, HSPF2, ENERGY STAR status, with SOURCE URL)
6. California rebates or incentives available (TECH Clean California, utility rebates, with SOURCE URL)
7. Why it would be suitable for THIS customer

Format with sources:
- [Information] - Source: [URL]

Provide 1-2 products with current, verifiable information and California-specific pricing."""
        
        return self.query(prompt)


# Convenience function for backwards compatibility
def call_perplexity(prompt: str, model: str = "sonar", max_retries: int = 3) -> Dict[str, Any]:
    """
    Convenience function to make a Perplexity query.
    
    Args:
        prompt: User prompt/question
        model: Model to use (default: "sonar")
        max_retries: Maximum retry attempts
        
    Returns:
        Dict with 'content', 'citations', and 'error' keys
    """
    agent = PerplexityAgent(model=model)
    return agent.query(prompt, max_retries=max_retries)

