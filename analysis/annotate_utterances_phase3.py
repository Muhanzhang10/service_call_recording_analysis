"""
Phase 3: Utterance-Level Annotations
Add detailed annotations to critical moments in each stage
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

# Stage-specific annotation guidelines
STAGE_ANNOTATION_GUIDELINES = {
    "introduction": {
        "focus_areas": [
            "Greeting quality - professional, cordial, and appropriate for the context",
            "Context awareness - recognize if this is first contact or if they've already met",
            "Rapport building - friendly tone, respectful acknowledgment",
            "Use of customer's name (when appropriate)",
            "If first contact: clear introduction of technician name and company",
            "If already met: warm acknowledgment and smooth transition to the work",
            "Overall professionalism and customer comfort"
        ],
        "common_issues": [
            "Cold or abrupt greeting regardless of context",
            "Missing formal introduction when it IS the first contact",
            "Overly formal introduction when they've clearly already met",
            "Lack of rapport or warmth",
            "Too casual or unprofessional tone"
        ],
        "what_to_highlight": [
            "Context-appropriate greetings (formal intro vs. warm acknowledgment)",
            "Effective rapport building and friendly tone",
            "Professional demeanor that puts customer at ease",
            "Good use of customer's name",
            "Missed opportunities for warmth or professionalism",
            "If already met: warm acknowledgment and smooth transition to the work",
        ]
    },
    "problem_diagnosis": {
        "focus_areas": [
            "Context awareness - Is extensive diagnosis relevant for this call type?",
            "Customer-driven inquiry - Did the customer ask questions or express concerns?",
            "Appropriate response depth - Match response to customer needs (brief if no concerns, detailed if issues raised)",
            "Prior discussions - May have already covered diagnosis before recording",
            "Active listening and responsiveness when customer does have questions",
            "Clear communication about the work being done",
            "Professional acknowledgment of customer input",
            "IMPORTANT: Check if customer questions are answered in the next 1-3 utterances before flagging as 'missing'"
        ],
        "common_issues": [
            "Over-diagnosing when customer is satisfied and has no questions",
            "Under-responding when customer DOES have legitimate concerns",
            "Dismissing customer questions or concerns",
            "Interrupting customer when they're explaining issues",
            "Assuming understanding without confirming when customer asks questions",
            "AVOID: Flagging 'missing' explanations when they appear shortly after the question in natural conversation flow"
        ],
        "what_to_highlight": [
            "Context-appropriate level of inquiry (don't penalize brief exchanges if customer has no concerns)",
            "Good responsiveness to customer questions when they arise",
            "Active listening and confirmation when diagnosis is needed",
            "Clear, helpful communication appropriate to the situation",
            "ACTUAL missed opportunities where customer concerns are never addressed (not just delayed responses)",
            "Questions that truly go unanswered throughout the entire conversation"
        ]
    },
    "solution_explanation": {
        "focus_areas": [
            "Clarity of explanation",
            "Technical jargon vs plain language",
            "Checking customer understanding",
            "Explaining 'why' not just 'what'",
            "Visual aids or examples mentioned",
            "Responsiveness to customer questions about the work",
            "Check if technical terms are explained when customer asks"
        ],
        "common_issues": [
            "Too much technical jargon without explanation",
            "Unclear explanations",
            "Not checking if customer understands",
            "Rushing through explanation",
            "AVOID: Flagging 'missing' explanations if they appear in the next few utterances"
        ],
        "what_to_highlight": [
            "Clear, accessible language",
            "Good use of analogies",
            "Checking for understanding",
            "Technical terms that are explained when customer asks",
            "ACTUAL confusing jargon that is never explained (not just temporarily unexplained)"
        ]
    },
    "upsell_attempts": {
        "focus_areas": [
            "Natural transition to upsell",
            "Value proposition clarity",
            "Customer-focused vs pushy approach",
            "Addressing customer needs",
            "Handling objections professionally",
            "Offering incentives or limited-time offers is NOT inherently pushy",
            "Check how technician responds to 'no' before flagging as pushy"
        ],
        "common_issues": [
            "ACTUALLY pushy: Persisting after customer says no multiple times",
            "ACTUALLY pushy: Using guilt, pressure, or manipulation",
            "ACTUALLY pushy: Ignoring clear customer discomfort or resistance",
            "Not explaining benefits clearly",
            "Poor timing of upsell",
            "Not reading customer signals of genuine discomfort",
            "AVOID flagging as 'pushy': Offering discounts/incentives (normal sales)",
            "AVOID flagging as 'pushy': Single upsell attempt that customer declines politely"
        ],
        "what_to_highlight": [
            "Natural, consultative approach",
            "Clear value communication",
            "Professional objection handling (accepting 'no' gracefully)",
            "ACTUAL pushy behavior: Multiple attempts after customer says no",
            "ACTUAL pushy behavior: Guilt trips or pressure tactics",
            "Genuine missed opportunities where value wasn't explained",
            "NOT pushy: Offering time-limited incentives once",
            "NOT pushy: Customer declining calmly and technician accepting it"
        ]
    },
    "maintenance_plan": {
        "focus_areas": [
            "Mention of maintenance plan",
            "Plan details and benefits",
            "Cost/value explanation",
            "Customer objection handling professionally",
            "Creating urgency without pressure",
            "Offering plan is good practice, even if customer declines",
            "Check response to 'no' before flagging as pushy"
        ],
        "common_issues": [
            "Not offering maintenance plan at all (missed opportunity)",
            "Vague plan details without clear benefits",
            "Not explaining ROI/value clearly",
            "ACTUALLY pushy: Persisting after customer clearly declines",
            "AVOID flagging as 'pushy': Single professional offer with clear value",
            "AVOID flagging as 'too pushy on price': Mentioning price once is normal"
        ],
        "what_to_highlight": [
            "Clear plan explanation with benefits",
            "Strong value proposition",
            "Professional acceptance of customer decision",
            "Missing offer entirely (genuine missed opportunity)",
            "Weak or unclear presentation that confuses customer",
            "NOT pushy: Professional offer that customer declines calmly"
        ]
    },
    "closing": {
        "focus_areas": [
            "Cordial conversation",
            "Thank you statement",
            "Next steps clarity",
            "Follow-up information",
            "Professional tone",
            "Leaving door open for future contact"
        ],
        "common_issues": [
            "No thank you",
            "Abrupt ending",
            "Unclear next steps",
            "Missing contact information",
            "Unprofessional tone"
        ],
        "what_to_highlight": [
            "Warm, professional thank you",
            "Clear next steps",
            "Good final impression",
            "Missing or weak closing",
            "Rushed or abrupt ending"
        ]
    }
}


def load_analyzed_transcript():
    """Load the analyzed transcript from Phase 2"""
    transcript_path = PROJECT_ROOT / "data" / "transcript_analyzed.json"
    with open(transcript_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_stage_utterances_with_indices(transcript_data, stage_key):
    """Get utterances for a stage with their original indices"""
    stage_info = transcript_data["stage_summary"].get(stage_key, {})
    utterance_indices = stage_info.get("utterance_indices", [])
    
    utterances_with_indices = []
    for idx in utterance_indices:
        if idx < len(transcript_data["utterances"]):
            utterances_with_indices.append({
                "index": idx,
                "utterance": transcript_data["utterances"][idx]
            })
    
    return utterances_with_indices


def format_utterances_for_annotation(utterances_with_indices, speaker_map):
    """Format utterances for GPT annotation"""
    formatted = []
    for item in utterances_with_indices:
        utt = item["utterance"]
        speaker_label = speaker_map.get(utt["speaker"], utt["speaker"])
        formatted.append({
            "index": item["index"],
            "speaker": speaker_label,
            "timestamp": f"[{utt['start']:.2f}s - {utt['end']:.2f}s]",
            "text": utt["text"]
        })
    return formatted


def annotate_stage_with_gpt(stage_key, stage_name, utterances_with_indices, stage_analysis, speaker_map):
    """
    Identify critical moments in a stage and generate annotations
    """
    if not utterances_with_indices:
        print(f"   ⚠️  No utterances to annotate for {stage_name}")
        return []
    
    formatted_utterances = format_utterances_for_annotation(utterances_with_indices, speaker_map)
    
    # Get compliance questions that were answered
    questions_summary = []
    for q in stage_analysis.get("questions", []):
        questions_summary.append({
            "id": q["id"],
            "question": q["question"],
            "answer": q["answer"],
            "score": q["score"]
        })
    
    # Get stage-specific guidelines
    guidelines = STAGE_ANNOTATION_GUIDELINES.get(stage_key, {})
    
    prompt = f"""You are annotating critical moments in the **{stage_name}** stage of a service call.

STAGE UTTERANCES:
{json.dumps(formatted_utterances, indent=2)}

COMPLIANCE ANALYSIS SUMMARY:
Overall Compliance: {stage_analysis.get('overall_compliance', 'N/A')}
Quality Rating: {stage_analysis.get('quality_rating', 'N/A')}
Score: {stage_analysis.get('compliance_score', 0)}/100

Questions Evaluated:
{json.dumps(questions_summary, indent=2)}

Key Strengths: {json.dumps(stage_analysis.get('key_strengths', []))}
Critical Gaps: {json.dumps(stage_analysis.get('critical_gaps', []))}

STAGE-SPECIFIC FOCUS AREAS:
{json.dumps(guidelines.get('focus_areas', []), indent=2)}

COMMON ISSUES TO WATCH FOR:
{json.dumps(guidelines.get('common_issues', []), indent=2)}

WHAT TO HIGHLIGHT:
{json.dumps(guidelines.get('what_to_highlight', []), indent=2)}

Your task: Identify 3-5 CRITICAL MOMENTS in these utterances that deserve annotation.

IMPORTANT - CONTEXT CHECKING:
- Before flagging something as "missing", check if it appears in SUBSEQUENT utterances
- If a customer asks a question, look at the NEXT 2-3 technician responses to see if it was answered
- Only flag as "missing" if the element truly never appears in the conversation
- Do NOT create false negatives by annotating too early in the conversation flow

Example - Question/Answer:
- Customer: "What is a HERS test?"
- Technician: "It's a home efficiency test..."
- This should NOT be flagged as "Missing explanation" because it WAS explained

IMPORTANT - PUSHY vs CONSULTATIVE SALES:
- Before flagging as "pushy", check how technician responds to customer objections
- Offering incentives (discounts, time-limited offers) is NORMAL sales behavior, NOT pushy
- PUSHY = Persisting multiple times after customer says no, using guilt/pressure, ignoring discomfort
- NOT PUSHY = Single offer with incentive + accepting "no" gracefully

Example - NOT Pushy:
- Technician: "If you sign today, we can waive the repair charge"
- Customer: "No, we won't do that today"
- Technician: "Absolutely. Let me provide you with other options..."
- This is PROFESSIONAL sales, not pushy. Customer declined calmly, technician accepted it.

Example - ACTUALLY Pushy:
- Customer: "No, I need to think about it"
- Technician: "But this offer expires today, you're really missing out..."
- Customer: "I said no"
- Technician: "Are you sure? Most people regret not taking this deal..."
- This IS pushy: multiple attempts after clear "no", pressure tactics

Use the stage-specific focus areas above to guide your analysis. Look for:
- Moments that directly relate to the focus areas listed above
- Examples of common issues mentioned
- Instances that match the "what to highlight" criteria
- Compliance questions marked NO or PARTIAL (high priority)
- Particularly good examples worth highlighting (YES answers)
- Important customer signals or reactions
- Notable strengths or weaknesses
- ACTUAL missing elements (not questions that get answered later)

For each critical moment, provide:

ANNOTATION TYPES:
- "success" (✓) - Something done well, compliant behavior
- "warning" (❌) - Missing element, non-compliant, problem
- "partial" (⚠️) - Partially done, could be better
- "info" (ℹ️) - Neutral observation, context
- "opportunity" (💡) - Missed sales or service opportunity
- "customer_signal" (👤) - Important customer cue or reaction

OUTPUT FORMAT (JSON):
{{
  "annotations": [
    {{
      "utterance_index": 1,
      "type": "warning",
      "icon": "❌",
      "title": "Missing: [Specific Element]",
      "description": "Clear, specific description of what's missing or wrong, relating to the stage-specific focus areas.",
      "related_question_id": "question_id_if_applicable",
      "severity": "high",
      "impact": "Specific impact on customer experience or compliance",
      "recommendation": "Specific, actionable suggestion for improvement"
    }},
    {{
      "utterance_index": 2,
      "type": "success",
      "icon": "✓",
      "title": "Strong [Specific Strength]",
      "description": "Describe what was done well and why it matters for this stage.",
      "related_question_id": "question_id_if_applicable",
      "severity": "low",
      "impact": "Positive outcome or benefit",
      "recommendation": null
    }},
    {{
      "utterance_index": 5,
      "type": "opportunity",
      "icon": "💡",
      "title": "Missed Opportunity: [What]",
      "description": "Describe what could have been done based on the stage focus areas.",
      "related_question_id": null,
      "severity": "medium",
      "impact": "What was lost by missing this",
      "recommendation": "How to capture this opportunity in future calls"
    }}
  ],
  "stage_notes": "1-2 sentence summary of how this stage performed overall, highlighting the key theme from your annotations"
}}

STAGE-SPECIFIC ANNOTATION EXAMPLES:

For **{stage_name}** stage specifically, consider annotating:
- If compliance questions show NO/PARTIAL answers, identify the exact utterances where elements are missing
- Highlight specific phrases or moments that align with the focus areas listed above
- Note any common issues from the list that appear in the utterances
- Identify transitions, tone shifts, or key phrases relevant to this stage

IMPORTANT:
- Return ONLY valid JSON
- Focus on the MOST IMPORTANT moments (3-5 annotations max)
- Be SPECIFIC - reference actual words/phrases from the utterances
- Make titles clear and scannable (e.g., "Missing: Company Name" not just "Issue")
- Tailor annotations to THIS stage's unique focus areas
- severity: "high" (critical issue), "medium" (notable), "low" (minor)
- related_question_id should match IDs from the questions if applicable
- recommendation can be null for positive annotations

CRITICAL - AVOID FALSE NEGATIVES:
- Read the ENTIRE conversation flow before annotating
- Check if customer questions get answered in subsequent utterances
- Only annotate "missing" elements if they truly never appear
- If a technician explains something 1-2 utterances later, that's FINE - don't flag it
- Focus on ACTUAL problems, not timing delays in natural conversation
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert service call analyst who identifies critical moments and provides actionable feedback. You create clear, specific annotations that help improve service quality."
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
        return result.get("annotations", [])
        
    except Exception as e:
        print(f"❌ Error annotating {stage_name}: {e}")
        return []


def apply_annotations_to_transcript(transcript_data, all_annotations):
    """Apply all annotations to the transcript utterances"""
    # Create a mapping of utterance index to annotations
    annotation_map = {}
    for ann in all_annotations:
        idx = ann["utterance_index"]
        if idx not in annotation_map:
            annotation_map[idx] = []
        annotation_map[idx].append(ann)
    
    # Apply annotations to utterances
    annotations_added = 0
    for idx, annotations in annotation_map.items():
        if idx < len(transcript_data["utterances"]):
            # Initialize annotations array if it doesn't exist
            if "annotations" not in transcript_data["utterances"][idx]:
                transcript_data["utterances"][idx]["annotations"] = []
            
            # Add new annotations
            transcript_data["utterances"][idx]["annotations"].extend(annotations)
            annotations_added += len(annotations)
    
    print(f"   ✓ Applied {annotations_added} annotations to {len(annotation_map)} utterances")
    
    return transcript_data


def generate_call_type_identification(transcript_data, speaker_map):
    """Identify the type of service call"""
    print("\nIdentifying call type...")
    
    # Get a summary of the call
    stage_summary = transcript_data.get("stage_summary", {})
    overall_compliance = transcript_data.get("overall_compliance", {})
    
    # Sample utterances from across the call
    sample_utterances = []
    for i in range(0, len(transcript_data["utterances"]), max(1, len(transcript_data["utterances"]) // 10)):
        utt = transcript_data["utterances"][i]
        speaker_label = speaker_map.get(utt["speaker"], utt["speaker"])
        sample_utterances.append({
            "speaker": speaker_label,
            "timestamp": f"[{utt['start']:.2f}s]",
            "text": utt["text"]
        })
    
    prompt = f"""Identify the type of service call based on this transcript analysis.

CALL SUMMARY:
- Stages present: {list(stage_summary.keys())}
- Overall compliance: {overall_compliance.get('score', 0)}/100

SAMPLE UTTERANCES:
{json.dumps(sample_utterances[:15], indent=2)}

CALL TYPES:
- repair_call - Fixing a broken system or component
- maintenance_visit - Routine maintenance or check-up
- installation - Installing new equipment
- emergency_service - Urgent service request
- follow_up - Follow-up visit after previous service
- post repair consultation - Quote or consultation for future work
- warranty_service - Service under warranty
- other - Specify if different

OUTPUT FORMAT (JSON):
{{
  "primary_call_type": "repair_call",
  "secondary_types": ["maintenance_visit"],
  "confidence": 0.9,
  "evidence": ["Key phrases or details that indicate this call type"],
  "reasoning": "Clear explanation of how you determined the call type",
  "service_details": {{
    "system_type": "HVAC / Plumbing / Electrical / Other",
    "issue_type": "Brief description of the issue or service",
    "urgency": "routine / moderate / urgent"
  }}
}}

Return ONLY valid JSON.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at categorizing service calls based on transcript content."
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
        print(f"   ✓ Call type: {result.get('primary_call_type', 'unknown')}")
        return result
        
    except Exception as e:
        print(f"❌ Error identifying call type: {e}")
        return {
            "primary_call_type": "unknown",
            "error": str(e)
        }


def generate_sales_insights(transcript_data, speaker_map):
    """Generate comprehensive sales insights"""
    print("\nGenerating sales insights...")
    
    # Get upsell and maintenance plan analyses
    upsell_analysis = transcript_data.get("stage_analyses", {}).get("upsell_attempts", {})
    maintenance_analysis = transcript_data.get("stage_analyses", {}).get("maintenance_plan", {})
    
    # Get relevant utterances
    upsell_indices = transcript_data.get("stage_summary", {}).get("upsell_attempts", {}).get("utterance_indices", [])
    maintenance_indices = transcript_data.get("stage_summary", {}).get("maintenance_plan", {}).get("utterance_indices", [])
    
    relevant_utterances = []
    for idx in upsell_indices + maintenance_indices:
        if idx < len(transcript_data["utterances"]):
            utt = transcript_data["utterances"][idx]
            speaker_label = speaker_map.get(utt["speaker"], utt["speaker"])
            relevant_utterances.append({
                "speaker": speaker_label,
                "timestamp": f"[{utt['start']:.2f}s]",
                "text": utt["text"]
            })
    
    prompt = f"""Provide comprehensive, SPECIFIC SALES INSIGHTS for this service call.

UPSELL STAGE ANALYSIS:
{json.dumps(upsell_analysis, indent=2)}

MAINTENANCE PLAN ANALYSIS:
{json.dumps(maintenance_analysis, indent=2)}

RELEVANT UTTERANCES:
{json.dumps(relevant_utterances[:20], indent=2)}

Your goal is to extract ACTIONABLE INTELLIGENCE that sales managers and business owners care about:

REQUIRED ANALYSIS:

1. **CUSTOMER INTERESTS & PURCHASE INTENT**
   - What specific products/services is the customer interested in? (Be specific: brand names, models, features)
   - What price points were discussed? (Include actual dollar amounts mentioned)
   - What is the customer's decision timeline? (Today, within week, need to discuss with spouse, etc.)
   - What factors are influencing their decision? (Price, features, energy efficiency, aesthetics, etc.)
   - How likely are they to purchase? (Hot lead, warm lead, cold lead)

2. **OPPORTUNITIES CAPTURED (Seized Sales Opportunities)**
   - What SPECIFIC products/services did the technician successfully present?
   - What was the estimated value/price of each opportunity?
   - What made the presentation effective?
   - Did customer commit, show strong interest, or remain neutral?
   - What's the next step? (Customer will call back, estimate sent, deposit taken, etc.)

3. **OPPORTUNITIES MISSED (Lost Revenue Potential)**
   - What SPECIFIC additional products/services could have been offered but weren't?
   - What was the estimated lost revenue for each missed opportunity?
   - Where in the conversation was the opening? (Quote specific moment)
   - Why was it missed? (Didn't identify need, didn't mention, customer objection not addressed)
   - What would have been a better approach?

4. **CUSTOMER BUYING SIGNALS**
   - What specific statements indicate interest, concern, or hesitation?
   - Did the technician capitalize on positive signals?
   - Did the technician address negative signals?

5. **DECISION-MAKING FACTORS**
   - What are the customer's priorities? (Cost, quality, speed, energy efficiency, warranty, etc.)
   - What concerns or objections did they raise?
   - How well did the technician address these?

6. **ACTIONABLE FOLLOW-UP**
   - What should happen next?
   - When should follow-up occur?
   - What information does customer need to make a decision?

EFFECTIVENESS RATING CRITERIA:

For "opportunities_captured", rate effectiveness using letter grades:

**Grade A (90-100):**
- Clear, compelling value proposition presented
- Natural, consultative approach (not pushy)
- Customer showed strong interest or agreement
- Benefits clearly explained and understood
- Professional handling of any objections
- Strong closing or call-to-action

**Grade B (70-89):**
- Value proposition presented but could be stronger
- Mostly natural approach with minor pushiness
- Customer showed moderate interest
- Benefits mentioned but not fully explored
- Adequate objection handling
- Decent closing but room for improvement

**Grade C (50-69):**
- Weak or unclear value proposition
- Somewhat pushy or awkward approach
- Customer showed limited interest
- Benefits poorly explained or vague
- Weak objection handling
- Minimal or unclear closing

**Grade D (0-49):**
- No clear value proposition
- Pushy, aggressive, or unprofessional approach
- Customer showed disinterest or resistance
- Benefits not explained
- Poor or no objection handling
- No effective closing or follow-through

For "overall_sales_rating", use the same criteria to evaluate the entire sales performance.

OUTPUT FORMAT (JSON):
{{
  "customer_purchase_profile": {{
    "interested_products": [
      {{
        "product_name": "Specific product/service (e.g., 'Bryant Heat Pump Model X', 'Bosch HVAC System')",
        "details": "Specific features or configuration discussed",
        "price_discussed": "$X,XXX (or range if applicable)",
        "customer_interest_level": "high / medium / low"
      }}
    ],
    "decision_timeline": "Specific timeline (e.g., 'needs to discuss with spouse', 'ready to decide within 2 weeks', 'gathering quotes')",
    "decision_factors": ["List of what matters to customer: price, efficiency, brand, warranty, etc."],
    "purchase_likelihood": "hot_lead / warm_lead / cold_lead / not_interested",
    "estimated_deal_value": "$X,XXX total potential revenue",
    "next_steps": "What needs to happen next (estimate sent, follow-up call scheduled, waiting on customer decision, etc.)"
  }},
  "opportunities_captured": [
    {{
      "opportunity": "SPECIFIC product/service presented (e.g., 'HVAC System Replacement - Bryant vs Bosch options')",
      "specific_details": "Exact products, models, configurations discussed",
      "estimated_value": "$X,XXX",
      "evidence": "Direct quote from transcript",
      "effectiveness_grade": "A / B / C / D",
      "effectiveness_score": 0-100,
      "what_worked_well": "Why this was effective",
      "customer_response": "How customer reacted (interested, neutral, declined)",
      "status": "closed / pending_decision / follow_up_needed"
    }}
  ],
  "opportunities_missed": [
    {{
      "opportunity": "SPECIFIC product/service that should have been offered (e.g., 'Extended Warranty', 'Air Quality System')",
      "estimated_lost_revenue": "$X,XXX",
      "where_it_should_have_been_offered": "Specific moment in conversation with quote",
      "why_it_was_missed": "Technician didn't identify need / didn't mention / customer objection not addressed",
      "customer_need_evidence": "Why customer needed this (quote or observation)",
      "recommended_approach": "Exactly how to present this in future"
    }}
  ],
  "customer_buying_signals": [
    {{
      "signal": "Specific indicator of interest or concern",
      "type": "positive / negative / question / objection",
      "evidence": "Exact quote",
      "technician_response": "How it was handled (or not)",
      "effectiveness": "well_handled / adequately_handled / missed_opportunity"
    }}
  ],
  "objections_and_concerns": [
    {{
      "objection": "Specific customer concern",
      "category": "price / timeline / product_fit / decision_making / trust / other",
      "evidence": "Quote",
      "handling": "How technician addressed it",
      "resolution": "resolved / partially_resolved / unresolved"
    }}
  ],
  "sales_strengths": ["Specific things done well with examples"],
  "areas_for_improvement": ["Specific, actionable improvements with examples"],
  "overall_sales_grade": "A / B / C / D",
  "overall_sales_score": 0-100,
  "grade_justification": "Why this grade, referencing specific moments",
  "summary": "2-3 sentence summary of sales performance and revenue potential",
  "key_takeaways_for_management": [
    "3-5 bullet points with actionable business intelligence",
    "Include revenue numbers, customer profile, and follow-up actions"
  ]
}}

IMPORTANT - BE SPECIFIC:
- Extract ACTUAL product names, brand names, model numbers mentioned (e.g., "Bryant Heat Pump", not just "HVAC system")
- Extract ACTUAL dollar amounts discussed (e.g., "$15,000", not "expensive")
- Quote EXACT phrases from transcript, don't paraphrase
- For missed opportunities, calculate estimated revenue based on typical industry pricing
- Use the effectiveness criteria above to consistently grade all opportunities
- Be specific about which criteria were met or not met
- Base all analysis on actual evidence from the transcript
- overall_sales_score should align with overall_sales_grade (A=90-100, B=70-89, C=50-69, D=0-49)
- Use letter grades (A/B/C/D) not text descriptions
- Focus on ACTIONABLE intelligence that helps close deals and increase revenue

Return ONLY valid JSON.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert sales analyst specializing in service industry sales and upselling techniques."
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
        print(f"   ✓ Sales rating: {result.get('overall_sales_rating', 'N/A')}")
        return result
        
    except Exception as e:
        print(f"❌ Error generating sales insights: {e}")
        return {"error": str(e)}


def save_final_transcript(transcript_data, call_type, sales_insights):
    """Save the final annotated transcript"""
    
    # Add final data
    transcript_data["call_type"] = call_type
    transcript_data["sales_insights"] = sales_insights
    
    # Add metadata about annotation phase
    transcript_data["annotation_metadata"] = {
        "phase": "phase3_utterance_annotations",
        "total_annotations": sum(
            len(utt.get("annotations", [])) 
            for utt in transcript_data["utterances"]
        ),
        "annotated_utterances": sum(
            1 for utt in transcript_data["utterances"] 
            if utt.get("annotations", [])
        )
    }
    
    # Save to file
    output_path = PROJECT_ROOT / "data" / "annotated_transcript.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript_data, f, indent=2)
    
    print(f"\n✓ Final annotated transcript saved to: {output_path}")
    
    return output_path


def print_annotation_summary(transcript_data):
    """Print summary of annotations"""
    print("\n" + "="*60)
    print("ANNOTATION SUMMARY")
    print("="*60)
    
    # Count annotations by type
    annotation_types = {}
    total_annotations = 0
    
    for utt in transcript_data["utterances"]:
        for ann in utt.get("annotations", []):
            ann_type = ann.get("type", "unknown")
            annotation_types[ann_type] = annotation_types.get(ann_type, 0) + 1
            total_annotations += 1
    
    print(f"\nTotal annotations: {total_annotations}")
    print(f"Annotated utterances: {transcript_data['annotation_metadata']['annotated_utterances']}")
    print(f"\nAnnotations by type:")
    for ann_type, count in sorted(annotation_types.items()):
        print(f"  {ann_type}: {count}")


def main():
    print("="*60)
    print("PHASE 3: UTTERANCE-LEVEL ANNOTATIONS")
    print("="*60)
    
    # Step 1: Load analyzed transcript
    print("\nStep 1: Loading analyzed transcript from Phase 2...")
    transcript_data = load_analyzed_transcript()
    speaker_map = transcript_data.get("speaker_identification", {})
    print(f"✓ Loaded transcript with {len(transcript_data['utterances'])} utterances")
    
    # Step 2: Annotate each stage
    print("\nStep 2: Annotating critical moments in each stage...")
    
    all_annotations = []
    stage_analyses = transcript_data.get("stage_analyses", {})
    
    for i, (stage_key, stage_analysis) in enumerate(stage_analyses.items(), 1):
        stage_name = stage_analysis.get("stage_name", stage_key)
        print(f"\n[{i}/6] Annotating {stage_name}...")
        
        # Get utterances for this stage
        utterances_with_indices = get_stage_utterances_with_indices(transcript_data, stage_key)
        
        if not utterances_with_indices:
            print(f"   ⚠️  No utterances to annotate")
            continue
        
        print(f"   Analyzing {len(utterances_with_indices)} utterances...")
        
        # Get annotations from GPT
        annotations = annotate_stage_with_gpt(
            stage_key, 
            stage_name, 
            utterances_with_indices, 
            stage_analysis, 
            speaker_map
        )
        
        print(f"   ✓ Generated {len(annotations)} annotations")
        all_annotations.extend(annotations)
    
    # Step 3: Apply annotations to transcript
    print("\nStep 3: Applying annotations to transcript...")
    transcript_data = apply_annotations_to_transcript(transcript_data, all_annotations)
    
    # Step 4: Identify call type
    print("\nStep 4: Identifying call type...")
    call_type = generate_call_type_identification(transcript_data, speaker_map)
    
    # Step 5: Generate sales insights
    print("\nStep 5: Generating sales insights...")
    sales_insights = generate_sales_insights(transcript_data, speaker_map)
    
    # Step 6: Save final transcript
    print("\nStep 6: Saving final annotated transcript...")
    output_path = save_final_transcript(transcript_data, call_type, sales_insights)
    
    # Step 7: Print summary
    print_annotation_summary(transcript_data)
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Call Type: {call_type.get('primary_call_type', 'unknown')}")
    print(f"Overall Compliance: {transcript_data['overall_compliance']['score']}/100 ({transcript_data['overall_compliance']['rating']})")
    print(f"Sales Rating: {sales_insights.get('overall_sales_rating', 'N/A')}")
    print(f"Total Annotations: {transcript_data['annotation_metadata']['total_annotations']}")
    
    print("\n" + "="*60)
    print("✓ PHASE 3 COMPLETE!")
    print("="*60)
    print(f"\nNext step: Build web UI to display the annotated transcript")
    print(f"Output file ready: {output_path}")
    print("\nThis file contains:")
    print("  • Labeled utterances with stage tags")
    print("  • Compliance analysis for all 6 stages")
    print("  • Detailed annotations on critical moments")
    print("  • Call type identification")
    print("  • Comprehensive sales insights")


if __name__ == "__main__":
    main()

