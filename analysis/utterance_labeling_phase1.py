"""
Phase 1: Utterance Labeling
Label each utterance in the transcript with stage tags
"""

import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Get project root directory (parent of analysis folder)
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from project root
load_dotenv(PROJECT_ROOT / ".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Stage definitions
STAGE_DEFINITIONS = {
    "introduction": {
        "name": "Introduction & Greeting",
        "description": "Technician greets customer and introduces themselves/company",
        "keywords": ["hello", "hi", "my name", "calling from", "this is"],
        "key_elements": ["greeting", "technician name", "company name"]
    },
    "problem_diagnosis": {
        "name": "Problem Diagnosis",
        "description": "Technician inquires about and understands the customer's issue",
        "keywords": ["problem", "issue", "what's wrong", "tell me about", "happening"],
        "key_elements": ["asking questions", "understanding issue", "diagnostic inquiry"]
    },
    "solution_explanation": {
        "name": "Solution Explanation",
        "description": "Technician explains the solution, work performed, or service provided",
        "keywords": ["fixed", "repaired", "replaced", "installed", "adjusted", "done"],
        "key_elements": ["what was done", "how it was fixed", "technical details"]
    },
    "upsell_attempts": {
        "name": "Upsell Attempts",
        "description": "Technician offers additional services, products, or upgrades",
        "keywords": ["also", "additional", "upgrade", "recommend", "options", "equipment"],
        "key_elements": ["additional services", "product recommendations", "upgrades"]
    },
    "maintenance_plan": {
        "name": "Maintenance Plan Offer",
        "description": "Technician offers maintenance plans or long-term service agreements",
        "keywords": ["maintenance", "plan", "agreement", "service plan", "warranty", "protection"],
        "key_elements": ["maintenance plan", "service agreement", "ongoing support"]
    },
    "closing": {
        "name": "Closing & Thank You",
        "description": "Technician wraps up the call and thanks the customer",
        "keywords": ["thank", "thanks", "appreciate", "have a", "take care", "goodbye"],
        "key_elements": ["thank you", "closing remarks", "goodbye"]
    }
}


def load_transcription():
    """Load the transcription JSON file"""
    transcript_path = PROJECT_ROOT / "data" / "transcription.json"
    with open(transcript_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_labeling_prompt(utterances):
    """
    Create a prompt for GPT-4 to label all utterances with stage tags
    """
    
    # Simplify utterances for the prompt (remove unnecessary fields)
    simplified_utterances = []
    for i, utt in enumerate(utterances):
        simplified_utterances.append({
            "index": i,
            "speaker": utt["speaker"],
            "text": utt["text"],
            "start": utt["start"],
            "end": utt["end"]
        })
    
    prompt = f"""You are analyzing a service call transcript between a technician and a customer.

Your task: Label EACH utterance with the appropriate service call stage(s).

STAGES (in typical order):
1. **introduction** - Greeting, technician introduces name/company
2. **problem_diagnosis** - Understanding what the issue is/was
3. **solution_explanation** - Explaining work done, repairs made, technical details
4. **upsell_attempts** - Offering additional services, products, or upgrades
5. **maintenance_plan** - Offering maintenance plans or service agreements
6. **closing** - Thank you, wrapping up, goodbye

STAGE DETAILS:
{json.dumps(STAGE_DEFINITIONS, indent=2)}

INSTRUCTIONS:
- Each utterance can have ONE primary_stage and potentially multiple stage_tags
- primary_stage = the main stage this utterance belongs to
- stage_tags = array of all relevant stages (usually includes primary_stage)
- An utterance can span multiple stages if it covers multiple topics
- Use "other" as primary_stage only if it doesn't fit any category (small talk, off-topic)
- Consider context from previous utterances
- Speaker B is likely the Technician, Speaker A is likely the Customer

TRANSCRIPT UTTERANCES:
{json.dumps(simplified_utterances, indent=2)}

OUTPUT FORMAT (JSON):
Return a JSON object with a "labels" array containing one entry per utterance:

{{
  "labels": [
    {{
      "index": 0,
      "primary_stage": "introduction",
      "stage_tags": ["introduction"],
      "confidence": 0.9,
      "reasoning": "Brief explanation of why this stage was chosen"
    }},
    {{
      "index": 1,
      "primary_stage": "introduction",
      "stage_tags": ["introduction", "solution_explanation"],
      "confidence": 0.7,
      "reasoning": "Technician mentions work done but hasn't properly introduced themselves - mixed content"
    }}
  ],
  "speaker_identification": {{
    "A": "Customer",
    "B": "Technician"
  }},
  "overall_notes": "Any observations about the call flow or stage progression"
}}

IMPORTANT: 
- Return ONLY valid JSON, no markdown code blocks
- Include ALL {len(utterances)} utterances in order
- Be consistent with stage naming (use exact stage keys listed above)
"""
    
    return prompt


def label_utterances_with_gpt(utterances):
    """
    Send utterances to GPT-4 and get stage labels back
    """
    print(f"Sending {len(utterances)} utterances to GPT-4 for labeling...")
    
    prompt = create_labeling_prompt(utterances)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert service call analyst. You analyze call transcripts and identify different stages of service calls with high accuracy. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}  # Ensures JSON output
        )
        
        result = json.loads(response.choices[0].message.content)
        
        print(f"✓ Received labels for {len(result['labels'])} utterances")
        
        return result
        
    except Exception as e:
        print(f"❌ Error calling GPT-4: {e}")
        raise


def merge_labels_with_transcript(transcript_data, labels_result):
    """
    Merge the stage labels back into the transcript data
    """
    print("Merging labels with transcript data...")
    
    labels = labels_result["labels"]
    speaker_identification = labels_result.get("speaker_identification", {})
    
    # Validate we have labels for all utterances
    if len(labels) != len(transcript_data["utterances"]):
        print(f"⚠️  Warning: Label count ({len(labels)}) doesn't match utterance count ({len(transcript_data['utterances'])})")
    
    # Add labels to each utterance
    for i, utterance in enumerate(transcript_data["utterances"]):
        if i < len(labels):
            label = labels[i]
            
            # Add new fields
            utterance["primary_stage"] = label["primary_stage"]
            utterance["stage_tags"] = label["stage_tags"]
            utterance["stage_confidence"] = label["confidence"]
            utterance["stage_reasoning"] = label["reasoning"]
            utterance["annotations"] = []  # Will be populated in later phases
    
    # Add metadata
    transcript_data["speaker_identification"] = speaker_identification
    transcript_data["labeling_metadata"] = {
        "phase": "phase1_utterance_labeling",
        "model": "gpt-4o",
        "total_utterances": len(labels),
        "stages_found": list(set(label["primary_stage"] for label in labels)),
        "overall_notes": labels_result.get("overall_notes", "")
    }
    
    print(f"✓ Labels merged successfully")
    print(f"  - Speaker identification: {speaker_identification}")
    print(f"  - Stages found: {transcript_data['labeling_metadata']['stages_found']}")
    
    return transcript_data


def generate_stage_summary(labeled_transcript):
    """
    Generate a summary of utterances per stage
    """
    print("Generating stage summary...")
    
    stage_summary = {}
    
    for stage_key in STAGE_DEFINITIONS.keys():
        stage_summary[stage_key] = {
            "name": STAGE_DEFINITIONS[stage_key]["name"],
            "utterance_indices": [],
            "utterance_count": 0,
            "start_time": None,
            "end_time": None,
            "status": "absent"
        }
    
    # Group utterances by primary stage
    for i, utterance in enumerate(labeled_transcript["utterances"]):
        primary_stage = utterance.get("primary_stage")
        
        if primary_stage and primary_stage in stage_summary:
            stage_summary[primary_stage]["utterance_indices"].append(i)
            stage_summary[primary_stage]["utterance_count"] += 1
            stage_summary[primary_stage]["status"] = "present"
            
            # Update time range
            if stage_summary[primary_stage]["start_time"] is None:
                stage_summary[primary_stage]["start_time"] = utterance["start"]
            stage_summary[primary_stage]["end_time"] = utterance["end"]
    
    labeled_transcript["stage_summary"] = stage_summary
    
    # Print summary
    print("\n" + "="*60)
    print("STAGE SUMMARY")
    print("="*60)
    for stage_key, summary in stage_summary.items():
        status_icon = "✓" if summary["status"] == "present" else "✗"
        print(f"{status_icon} {summary['name']}: {summary['utterance_count']} utterances")
        if summary["status"] == "present":
            print(f"   [{summary['start_time']:.2f}s - {summary['end_time']:.2f}s]")
    print("="*60)
    
    return labeled_transcript


def save_labeled_transcript(data, output_filename="transcript_labeled.json"):
    """Save the labeled transcript to file"""
    output_path = PROJECT_ROOT / "data" / output_filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Labeled transcript saved to: {output_path}")


def main():
    print("="*60)
    print("PHASE 1: UTTERANCE LABELING")
    print("="*60)
    
    # Step 1: Load transcript
    print("\nStep 1: Loading transcript...")
    transcript_data = load_transcription()
    print(f"✓ Loaded {len(transcript_data['utterances'])} utterances")
    
    # Step 2: Label utterances with GPT-4
    print("\nStep 2: Labeling utterances with GPT-4...")
    labels_result = label_utterances_with_gpt(transcript_data["utterances"])
    
    # Step 3: Merge labels back into transcript
    print("\nStep 3: Merging labels with transcript...")
    labeled_transcript = merge_labels_with_transcript(transcript_data, labels_result)
    
    # Step 4: Generate stage summary
    print("\nStep 4: Generating stage summary...")
    labeled_transcript = generate_stage_summary(labeled_transcript)
    
    # Step 5: Save results
    print("\nStep 5: Saving results...")
    save_labeled_transcript(labeled_transcript)
    
    print("\n" + "="*60)
    print("✓ PHASE 1 COMPLETE!")
    print("="*60)
    print(f"\nNext step: Run Phase 2 to analyze each stage for compliance")
    print(f"Output file ready: {PROJECT_ROOT / 'data' / 'transcript_labeled.json'}")


if __name__ == "__main__":
    main()

