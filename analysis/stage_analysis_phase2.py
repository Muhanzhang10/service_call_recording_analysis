"""
Phase 2: Stage-by-Stage Compliance Analysis
Analyze each stage against compliance questions and criteria
"""

import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Compliance questions for each stage
COMPLIANCE_CRITERIA = {
    "introduction": {
        "stage_name": "Introduction & Greeting",
        "questions": [
            {
                "id": "intro_greeting",
                "question": "Did the technician greet the customer in a professional and cordial manner?",
                "criteria": "Professional and friendly greeting that acknowledges the customer. If they've already met, the greeting should still be warm and professional.",
                "weight": 2
            },
            {
                "id": "intro_name_company",
                "question": "Did the technician appropriately introduce themselves/company (if needed given the context)?",
                "criteria": "If this is first contact, technician should introduce name and company. If they've already met (common in service calls), this is not required - cordial acknowledgment is sufficient. Consider whether a formal introduction would be natural given the context.",
                "weight": 2
            },
            {
                "id": "intro_rapport",
                "question": "Did the technician establish or maintain good rapport with the customer?",
                "criteria": "Friendly, respectful tone that builds trust. Uses customer's name if appropriate. Creates a positive start to the interaction.",
                "weight": 1
            }
        ]
    },
    "problem_diagnosis": {
        "stage_name": "Problem Diagnosis",
        "questions": [
            {
                "id": "diag_relevance",
                "question": "Was problem diagnosis relevant and appropriate for this call?",
                "criteria": "Consider: Did the customer express concerns or ask questions that warrant diagnosis? Is this a repair/troubleshooting call or routine service? May have already been discussed before recording. If no customer concerns or questions, brief responses are sufficient.",
                "weight": 1
            },
            {
                "id": "diag_customer_needs",
                "question": "Did the technician appropriately address any customer questions or concerns?",
                "criteria": "If customer asked questions or expressed concerns, technician should respond thoughtfully. If customer didn't raise issues, no probing is needed.",
                "weight": 2
            },
            {
                "id": "diag_communication",
                "question": "Was communication about the work clear and appropriate?",
                "criteria": "Technician explains what they're doing/found in a way that's appropriate for the context. Active listening if customer has concerns. May be brief if straightforward work.",
                "weight": 2
            }
        ]
    },
    "solution_explanation": {
        "stage_name": "Solution Explanation",
        "questions": [
            {
                "id": "soln_clarity",
                "question": "Did the technician clearly explain the solution or service performed?",
                "criteria": "Clear explanation of what was done, how it was fixed",
                "weight": 2
            },
            {
                "id": "soln_understanding",
                "question": "Did the customer appear to understand the explanation?",
                "criteria": "Customer responses indicate comprehension, technician checked for understanding",
                "weight": 1
            },
            {
                "id": "soln_details",
                "question": "Were technical details communicated in an accessible way?",
                "criteria": "Avoided excessive jargon or explained technical terms clearly",
                "weight": 1
            }
        ]
    },
    "upsell_attempts": {
        "stage_name": "Upsell Attempts",
        "questions": [
            {
                "id": "upsell_present",
                "question": "Did the technician attempt to upsell additional services or products?",
                "criteria": "Mentioned additional services, upgrades, or products",
                "weight": 2
            },
            {
                "id": "upsell_approach",
                "question": "Was the upsell approach natural and customer-focused?",
                "criteria": "Professional approach that considers customer needs, not pushy",
                "weight": 2
            },
            {
                "id": "upsell_value",
                "question": "Did the technician explain the value/benefits?",
                "criteria": "Clear explanation of why customer would benefit",
                "weight": 1
            }
        ]
    },
    "maintenance_plan": {
        "stage_name": "Maintenance Plan Offer",
        "questions": [
            {
                "id": "maint_offered",
                "question": "Did the technician offer a maintenance plan or service agreement?",
                "criteria": "Mentioned maintenance plans, service agreements, or ongoing support",
                "weight": 3
            },
            {
                "id": "maint_details",
                "question": "Were the plan details clearly explained?",
                "criteria": "Explained what the plan includes, benefits, and terms",
                "weight": 1
            },
            {
                "id": "maint_customer_response",
                "question": "Was the customer's response addressed appropriately?",
                "criteria": "Handled objections or interest professionally",
                "weight": 1
            }
        ]
    },
    "closing": {
        "stage_name": "Closing & Thank You",
        "questions": [
            {
                "id": "close_thankyou",
                "question": "Did the technician thank the customer?",
                "criteria": "Expressed gratitude for customer's business or time",
                "weight": 2
            },
            {
                "id": "close_professional",
                "question": "Was the closing professional and courteous?",
                "criteria": "Polite, professional tone in wrapping up",
                "weight": 1
            },
            {
                "id": "close_nextsteps",
                "question": "Were next steps or follow-up information provided if needed?",
                "criteria": "Confirmed any follow-up actions or left customer with necessary information",
                "weight": 1
            }
        ]
    }
}


def load_labeled_transcript():
    """Load the labeled transcript from Phase 1"""
    transcript_path = PROJECT_ROOT / "data" / "transcript_labeled.json"
    with open(transcript_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_stage_utterances(labeled_transcript, stage_key):
    """Extract utterances for a specific stage"""
    stage_info = labeled_transcript["stage_summary"].get(stage_key, {})
    utterance_indices = stage_info.get("utterance_indices", [])
    
    utterances = []
    for idx in utterance_indices:
        if idx < len(labeled_transcript["utterances"]):
            utterances.append(labeled_transcript["utterances"][idx])
    
    return utterances, stage_info


def format_utterances_for_analysis(utterances, speaker_map):
    """Format utterances for GPT analysis"""
    formatted = []
    for utt in utterances:
        speaker_label = speaker_map.get(utt["speaker"], utt["speaker"])
        formatted.append({
            "speaker": speaker_label,
            "timestamp": f"[{utt['start']:.2f}s - {utt['end']:.2f}s]",
            "text": utt["text"]
        })
    return formatted


def analyze_stage_with_gpt(stage_key, utterances, speaker_map):
    """
    Analyze a specific stage against its compliance questions
    """
    if not utterances:
        # Stage not present
        return {
            "status": "absent",
            "overall_compliance": "NON-COMPLIANT",
            "compliance_score": 0,
            "quality_rating": "N/A",
            "analysis": f"The {COMPLIANCE_CRITERIA[stage_key]['stage_name']} stage was not identified in this call.",
            "questions": [],
            "key_strengths": [],
            "critical_gaps": [f"{COMPLIANCE_CRITERIA[stage_key]['stage_name']} stage missing entirely"],
            "recommendations": [f"Include a proper {COMPLIANCE_CRITERIA[stage_key]['stage_name']} in future calls"]
        }
    
    criteria = COMPLIANCE_CRITERIA[stage_key]
    formatted_utterances = format_utterances_for_analysis(utterances, speaker_map)
    
    prompt = f"""You are analyzing the **{criteria['stage_name']}** stage of a service call.

STAGE UTTERANCES:
{json.dumps(formatted_utterances, indent=2)}

COMPLIANCE QUESTIONS TO EVALUATE:
{json.dumps(criteria['questions'], indent=2)}

Your task: Evaluate this stage against each compliance question.

IMPORTANT CONTEXT CONSIDERATIONS:
- Consider the CONTEXT of the conversation. For example, in service calls, the technician often arrives at a location where they've already met the customer, so a formal name/company introduction may not be needed.
- Evaluate what is APPROPRIATE for the situation, not just a checklist. A cordial greeting in a follow-up context is just as good as a formal introduction in a first-contact scenario.
- For PROBLEM DIAGNOSIS: Not all calls require extensive diagnosis. If the customer has no questions/concerns, brief responses are perfectly fine. Diagnostic discussions may have occurred before the recording. Evaluate based on whether the technician appropriately addressed the customer's actual needs, not whether they probed for problems that don't exist.
- Focus on the quality and professionalism of the interaction within its context, not rigid adherence to formalities that may be unnecessary.

For EACH question, provide:
1. answer: "YES" (compliant), "PARTIAL" (somewhat compliant), or "NO" (non-compliant)
2. score: 0-100 (0=completely missing, 50=partially present, 100=excellently done)
3. evidence: Specific quote(s) from the utterances with timestamps
4. explanation: Why you gave this answer and score, considering the context
5. what_was_good: Positive aspects (if any)
6. what_was_missing: Gaps or issues (if any)

Then provide an OVERALL ASSESSMENT:

- overall_compliance: "COMPLIANT" (most questions YES), "PARTIAL" (mixed), or "NON-COMPLIANT" (most NO)
- compliance_score: 0-100 (weighted average based on question weights)
- quality_rating: Rate based on these criteria:

  **Excellent (90-100):**
  - All or nearly all compliance questions answered YES
  - Strong execution across all key elements of this stage
  - Professional, clear, and effective communication
  - No significant gaps or issues
  - Best practices consistently followed
  
  **Good (70-89):**
  - Most compliance questions answered YES, some PARTIAL
  - Solid execution with minor room for improvement
  - Generally professional and clear communication
  - Minor gaps that don't significantly impact quality
  - Most best practices followed
  
  **Fair (50-69):**
  - Mixed compliance results (YES/PARTIAL/NO)
  - Inconsistent execution with notable gaps
  - Some communication issues or unclear elements
  - Several important aspects missing or weak
  - Best practices partially followed
  
  **Poor (<50):**
  - Most questions answered NO or PARTIAL
  - Weak or incomplete execution
  - Significant communication problems
  - Critical elements missing
  - Best practices not followed

- analysis: 2-3 sentences summarizing the stage quality
- key_strengths: Array of 2-3 main strengths
- critical_gaps: Array of 2-3 main issues or missing elements
- recommendations: Array of 3-5 specific, actionable recommendations

OUTPUT FORMAT (JSON):
{{
  "status": "present",
  "questions": [
    {{
      "id": "intro_greeting",
      "question": "Did the technician properly greet the customer?",
      "answer": "PARTIAL",
      "score": 60,
      "evidence": [
        {{
          "quote": "Hey, Luis",
          "timestamp": "[12.80s - 19.36s]",
          "speaker": "Technician"
        }}
      ],
      "explanation": "Greeting was present but informal...",
      "what_was_good": "Used customer's name",
      "what_was_missing": "Lacked professional greeting structure"
    }}
  ],
  "overall_compliance": "PARTIAL",
  "compliance_score": 45,
  "quality_rating": "Poor",
  "analysis": "The introduction stage was present but incomplete...",
  "key_strengths": ["Used customer name", "Friendly tone"],
  "critical_gaps": ["No name introduction", "No company mention"],
  "recommendations": [
    "Add formal greeting with name and company",
    "Practice professional introduction script",
    "Establish credibility early"
  ]
}}

IMPORTANT:
- Return ONLY valid JSON
- Be specific with evidence - include actual quotes
- Consider the weight of each question when calculating overall score
- Be fair but thorough in evaluation
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert service call quality analyst. You evaluate technician performance against established compliance criteria with precision and fairness."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"❌ Error analyzing {stage_key}: {e}")
        raise


def calculate_overall_compliance_score(stage_analyses):
    """Calculate overall compliance across all stages"""
    total_score = 0
    total_weight = 0
    stages_evaluated = 0
    
    for stage_key, analysis in stage_analyses.items():
        if analysis.get("status") == "present":
            score = analysis.get("compliance_score", 0)
            # Each stage has equal weight
            total_score += score
            total_weight += 100
            stages_evaluated += 1
    
    if total_weight > 0:
        overall_score = total_score / stages_evaluated
    else:
        overall_score = 0
    
    return round(overall_score, 1)


def generate_overall_rating(overall_score):
    """Convert score to rating"""
    if overall_score >= 90:
        return "Excellent"
    elif overall_score >= 70:
        return "Good"
    elif overall_score >= 50:
        return "Fair"
    else:
        return "Poor"


def save_stage_analyses(labeled_transcript, stage_analyses, overall_score, overall_rating):
    """Save the analyzed transcript with stage analyses"""
    
    # Add stage analyses to the transcript
    labeled_transcript["stage_analyses"] = stage_analyses
    labeled_transcript["overall_compliance"] = {
        "score": overall_score,
        "rating": overall_rating,
        "stages_evaluated": len([a for a in stage_analyses.values() if a.get("status") == "present"]),
        "stages_missing": len([a for a in stage_analyses.values() if a.get("status") == "absent"])
    }
    
    # Save to file
    output_path = PROJECT_ROOT / "data" / "transcript_analyzed.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(labeled_transcript, f, indent=2)
    
    print(f"\n✓ Analyzed transcript saved to: {output_path}")
    
    return output_path


def print_stage_summary(stage_key, analysis):
    """Print a summary of stage analysis"""
    stage_name = COMPLIANCE_CRITERIA[stage_key]["stage_name"]
    
    if analysis["status"] == "absent":
        print(f"\n❌ {stage_name}: ABSENT")
        return
    
    compliance = analysis["overall_compliance"]
    score = analysis["compliance_score"]
    rating = analysis["quality_rating"]
    
    # Icon based on compliance
    if compliance == "COMPLIANT":
        icon = "✓"
    elif compliance == "PARTIAL":
        icon = "⚠"
    else:
        icon = "✗"
    
    print(f"\n{icon} {stage_name}: {compliance}")
    print(f"   Score: {score}/100 | Rating: {rating}")
    print(f"   Questions answered: {len(analysis['questions'])}")
    
    # Quick summary of questions
    yes_count = sum(1 for q in analysis["questions"] if q["answer"] == "YES")
    partial_count = sum(1 for q in analysis["questions"] if q["answer"] == "PARTIAL")
    no_count = sum(1 for q in analysis["questions"] if q["answer"] == "NO")
    
    print(f"   ✓ {yes_count} YES | ⚠ {partial_count} PARTIAL | ✗ {no_count} NO")


def main():
    print("="*60)
    print("PHASE 2: STAGE-BY-STAGE COMPLIANCE ANALYSIS")
    print("="*60)
    
    # Step 1: Load labeled transcript
    print("\nStep 1: Loading labeled transcript from Phase 1...")
    labeled_transcript = load_labeled_transcript()
    speaker_map = labeled_transcript.get("speaker_identification", {})
    print(f"✓ Loaded transcript with {len(labeled_transcript['utterances'])} utterances")
    print(f"   Speakers: {speaker_map}")
    
    # Step 2: Analyze each stage
    print("\nStep 2: Analyzing each stage for compliance...")
    stage_analyses = {}
    
    for i, stage_key in enumerate(COMPLIANCE_CRITERIA.keys(), 1):
        stage_name = COMPLIANCE_CRITERIA[stage_key]["stage_name"]
        print(f"\n[{i}/6] Analyzing {stage_name}...")
        
        # Get utterances for this stage
        utterances, stage_info = get_stage_utterances(labeled_transcript, stage_key)
        
        if utterances:
            print(f"   Found {len(utterances)} utterances for this stage")
        else:
            print(f"   ⚠️  Stage not found in transcript")
        
        # Analyze with GPT
        analysis = analyze_stage_with_gpt(stage_key, utterances, speaker_map)
        stage_analyses[stage_key] = analysis
        
        print(f"   ✓ Analysis complete")
    
    # Step 3: Calculate overall compliance
    print("\nStep 3: Calculating overall compliance score...")
    overall_score = calculate_overall_compliance_score(stage_analyses)
    overall_rating = generate_overall_rating(overall_score)
    print(f"✓ Overall Compliance Score: {overall_score}/100 ({overall_rating})")
    
    # Step 4: Save results
    print("\nStep 4: Saving results...")
    output_path = save_stage_analyses(labeled_transcript, stage_analyses, overall_score, overall_rating)
    
    # Step 5: Print summary
    print("\n" + "="*60)
    print("STAGE ANALYSIS SUMMARY")
    print("="*60)
    
    for stage_key in COMPLIANCE_CRITERIA.keys():
        print_stage_summary(stage_key, stage_analyses[stage_key])
    
    print("\n" + "="*60)
    print(f"OVERALL COMPLIANCE: {overall_score}/100 ({overall_rating})")
    print("="*60)
    
    print("\n" + "="*60)
    print("✓ PHASE 2 COMPLETE!")
    print("="*60)
    print(f"\nNext step: Run Phase 3 to add detailed annotations")
    print(f"Output file ready: {output_path}")


if __name__ == "__main__":
    main()

