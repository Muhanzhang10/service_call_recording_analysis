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
        "description": "The FINAL closing of the call - technician thanks the customer and says goodbye. NOT 'wrapping up' a discussion or presentation (that's part of other stages like upsell/maintenance plan). This is the actual end of the conversation.",
        "keywords": ["thank", "thanks", "appreciate", "have a", "take care", "goodbye", "bye"],
        "key_elements": ["thank you", "final goodbye", "call ending"]
    }
}


def load_transcription():
    """Load the transcription JSON file"""
    transcript_path = PROJECT_ROOT / "data" / "transcription.json"
    with open(transcript_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_context_window(utterances, target_index, window_size=4):
    """
    Create a context window around a target utterance for better labeling
    
    Args:
        utterances: List of all utterances
        target_index: Index of the utterance to label
        window_size: Number of utterances to include before and after (default 4)
    
    Returns:
        List of utterances with context, marking the target
    """
    start_idx = max(0, target_index - window_size)
    end_idx = min(len(utterances), target_index + window_size + 1)
    
    context_utterances = []
    for i in range(start_idx, end_idx):
        utt = utterances[i]
        context_utterances.append({
            "index": i,
            "speaker": utt["speaker"],
            "text": utt["text"],
            "start": utt["start"],
            "end": utt["end"],
            "is_target": (i == target_index)  # Mark the utterance to be labeled
        })
    
    return context_utterances


def create_batch_labeling_prompt(utterance_batches):
    """
    Create a prompt for GPT-4 to label a batch of utterances with their context windows
    
    Args:
        utterance_batches: List of context windows, each containing utterances with one marked as target
    """
    
    prompt = f"""You are analyzing a service call transcript between a technician and a customer.

Your task: Label the TARGET utterances (marked with "is_target": true) with the appropriate service call stage(s).
For each target utterance, you are provided with surrounding utterances for CONTEXT ONLY.

STAGES (in typical order):
1. **introduction** - Greeting, technician introduces name/company
2. **problem_diagnosis** - Understanding what the issue is/was
3. **solution_explanation** - Explaining work done, repairs made, technical details
4. **upsell_attempts** - Offering additional services, products, or upgrades
5. **maintenance_plan** - Offering maintenance plans or service agreements
6. **closing** - FINAL thank you and goodbye (NOT "wrapping up" a presentation - that belongs to the stage being wrapped up)

STAGE DETAILS:
{json.dumps(STAGE_DEFINITIONS, indent=2)}

INSTRUCTIONS:
- Label ONLY the utterances marked with "is_target": true
- Use surrounding utterances for context to make better decisions
- Each utterance can have ONE primary_stage and potentially multiple stage_tags
- primary_stage = the main stage this utterance belongs to
- stage_tags = array of all relevant stages (usually includes primary_stage)
- An utterance can span multiple stages if it covers multiple topics
- Use "other" as primary_stage only if it doesn't fit any category (small talk, off-topic)
- Speaker B is likely the Technician, Speaker A is likely the Customer

IMPORTANT - CLOSING STAGE CLARIFICATION:
- "closing" stage is ONLY for the FINAL goodbye/thank you at the END of the call
- Phrases like "let me wrap up", "to wrap this up", "wrapping up here" are NOT closing - they're transitions within other stages (upsell, maintenance_plan, solution_explanation)
- Only label as "closing" if it's the actual farewell/goodbye at the end of the conversation
- Example: "Let me wrap up the pricing for you" = upsell_attempts (NOT closing)
- Example: "Thanks so much, have a great day!" = closing

CONTEXT CONSIDERATIONS:
- Look at what comes BEFORE the target utterance to understand the flow
- Look at what comes AFTER to see where the conversation is heading
- Short utterances like "Okay" or "Sure" should be labeled based on the stage they're part of
- Transitions like "Let me explain..." belong to the stage that follows, not closing

SPECIAL PATTERN - COMBINED GREETINGS:
- Technicians often combine greetings with status updates: "Hey John, I got you all fixed up"
- These should have BOTH "introduction" AND the other relevant stage in stage_tags
- If the FIRST technician utterance contains ANY greeting element (Hi, Hey, Hello, customer name), include "introduction" in stage_tags
- Example: "Hey Luis. Got you all done." → stage_tags: ["introduction", "solution_explanation"]
- The primary_stage can be the dominant topic, but introduction should be in stage_tags if greeting is present

UTTERANCES WITH CONTEXT:
{json.dumps(utterance_batches, indent=2)}

OUTPUT FORMAT (JSON):
Return a JSON object with a "labels" array containing one entry for EACH TARGET utterance:

{{
  "labels": [
    {{
      "index": 0,
      "primary_stage": "introduction",
      "stage_tags": ["introduction"],
      "confidence": 0.9,
      "reasoning": "Brief explanation considering the surrounding context"
    }}
  ]
}}

IMPORTANT: 
- Return ONLY valid JSON, no markdown code blocks
- Include labels for ALL target utterances in the batch
- Be consistent with stage naming (use exact stage keys listed above)
- Consider the FULL CONTEXT when making labeling decisions
"""
    
    return prompt


def label_utterances_with_gpt(utterances, batch_size=15):
    """
    Send utterances to GPT-4 with sliding window context for better labeling
    
    Args:
        utterances: List of all utterances to label
        batch_size: Number of context windows to process per API call
    """
    print(f"Labeling {len(utterances)} utterances using sliding window context...")
    print(f"Window size: 4 utterances before and after each target")
    
    all_labels = []
    total_batches = (len(utterances) + batch_size - 1) // batch_size
    
    # Process utterances in batches for efficiency
    for batch_num in range(0, len(utterances), batch_size):
        batch_end = min(batch_num + batch_size, len(utterances))
        current_batch_size = batch_end - batch_num
        
        print(f"Processing batch {batch_num // batch_size + 1}/{total_batches} ({current_batch_size} utterances)...")
        
        # Create context windows for this batch
        utterance_batches = []
        for i in range(batch_num, batch_end):
            context_window = create_context_window(utterances, i, window_size=4)
            utterance_batches.append({
                "target_index": i,
                "context": context_window
            })
        
        prompt = create_batch_labeling_prompt(utterance_batches)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert service call analyst. You analyze call transcripts and identify different stages of service calls with high accuracy. You use context effectively to make accurate stage classifications. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            batch_result = json.loads(response.choices[0].message.content)
            batch_labels = batch_result.get("labels", [])
            
            # Validate we got the right number of labels
            if len(batch_labels) != current_batch_size:
                print(f"⚠️  Warning: Expected {current_batch_size} labels, got {len(batch_labels)}")
            
            all_labels.extend(batch_labels)
            print(f"   ✓ Received {len(batch_labels)} labels")
            
        except Exception as e:
            print(f"❌ Error processing batch {batch_num // batch_size + 1}: {e}")
            raise
    
    print(f"✓ Successfully labeled all {len(all_labels)} utterances with context")
    
    # For first batch, try to identify speaker roles (do this once, not per batch)
    # Re-run a quick analysis on the first ~20 utterances to identify speakers
    speaker_identification = identify_speakers(utterances[:20])
    
    return {
        "labels": all_labels,
        "speaker_identification": speaker_identification,
        "overall_notes": f"Labeled with sliding window context (window_size=4). Processed in {total_batches} batches."
    }


def identify_speakers(initial_utterances):
    """
    Identify which speaker is the technician and which is the customer
    """
    try:
        prompt = f"""Based on these initial utterances from a service call, identify which speaker is the Technician and which is the Customer.

UTTERANCES:
{json.dumps([{"speaker": u["speaker"], "text": u["text"]} for u in initial_utterances], indent=2)}

OUTPUT FORMAT (JSON):
{{
  "A": "Customer" or "Technician",
  "B": "Customer" or "Technician"
}}

Return ONLY valid JSON."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You identify speakers in service call transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        print(f"⚠️  Could not identify speakers: {e}")
        return {"A": "Customer", "B": "Technician"}  # Default assumption


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
    
    # Group utterances by stage tags (not just primary stage)
    # This allows utterances with multiple stages to be analyzed in all relevant stages
    for i, utterance in enumerate(labeled_transcript["utterances"]):
        stage_tags = utterance.get("stage_tags", [])
        
        # Add this utterance to ALL stages it's tagged with
        for stage_tag in stage_tags:
            if stage_tag in stage_summary:
                # Avoid duplicates
                if i not in stage_summary[stage_tag]["utterance_indices"]:
                    stage_summary[stage_tag]["utterance_indices"].append(i)
                    stage_summary[stage_tag]["utterance_count"] += 1
                    stage_summary[stage_tag]["status"] = "present"
                    
                    # Update time range
                    if stage_summary[stage_tag]["start_time"] is None:
                        stage_summary[stage_tag]["start_time"] = utterance["start"]
                    stage_summary[stage_tag]["end_time"] = utterance["end"]
    
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

