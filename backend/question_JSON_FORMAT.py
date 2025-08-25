# UPDATED JSON FORMAT - Simplified and More Focused

# NEW SIMPLIFIED JSON STRUCTURE:
simplified_json_format = {
    # CORE QUESTION DATA
    "question_text": "Complete question text extracted from image word-for-word",
    "options": {
        "A": "Option A text exactly as shown",
        "B": "Option B text exactly as shown", 
        "C": "Option C text exactly as shown",
        "D": "Option D text exactly as shown"
    },
    
    # SOLUTION SECTION - SIMPLIFIED
    "correct_answer": "C",
    "simple_answer": "The net force is 12 N to the right",  # NEW: Quick answer
    
    # STEP-BY-STEP CALCULATION - SIMPLIFIED
    "calculation_steps": [
        "Step 1: Identify forces: 20 N right, 8 N left",
        "Step 2: Net force = 20 N - 8 N = 12 N",
        "Step 3: Direction: Net force acts to the right"
    ],
    
    # DETAILED EXPLANATION - NEW FORMAT
    "detailed_explanation": {
        "why_correct": "Option C is correct because the net force is calculated by subtracting opposing forces: 20 N - 8 N = 12 N to the right",
        "why_others_wrong": {
            "A": "Incorrect because it only considers one force, ignoring the opposing 8 N force",
            "B": "Incorrect because it adds the forces instead of finding the net force (20 + 8 = 28 N is wrong)",
            "D": "Incorrect direction - the larger force (20 N) is to the right, so net force cannot be to the left"
        }
    },
    
    # SIMPLIFIED METADATA
    "topic": "Forces and Motion",  # Simplified from multiple topic fields
    "difficulty": "medium",  # easy/medium/hard
    "confidence_score": 0.95,
    "auto_flagged": false
}

# UPDATE THE CLAUDE PROMPT IN ai_solver.py
def generate_enhanced_claude_prompt(self, subject, question_num):
    """Generate enhanced Claude prompt optimized for physics - UPDATED VERSION"""
    return f"""Please analyze this Cambridge IGCSE {subject} question {question_num} and provide a clear, focused analysis.

IMPORTANT: Extract ALL text accurately and use this EXACT JSON format:

{{
  "question_text": "Complete question text extracted from image word-for-word",
  "options": {{
    "A": "Option A text exactly as shown",
    "B": "Option B text exactly as shown",
    "C": "Option C text exactly as shown", 
    "D": "Option D text exactly as shown"
  }},
  
  "correct_answer": "C",
  "simple_answer": "Brief, clear answer in one sentence",
  
  "calculation_steps": [
    "Step 1: What you identify or set up",
    "Step 2: The main calculation or reasoning",
    "Step 3: Final result with units if applicable"
  ],
  
  "detailed_explanation": {{
    "why_correct": "Clear explanation of why the correct answer is right",
    "why_others_wrong": {{
      "A": "Specific reason why option A is incorrect",
      "B": "Specific reason why option B is incorrect", 
      "D": "Specific reason why option D is incorrect"
    }}
  }},
  
  "topic": "Motion and Forces",
  "difficulty": "medium",
  "confidence_score": 0.95,
  "auto_flagged": false
}}

REQUIREMENTS:

1. **Text Extraction**: Extract ALL text word-for-word from the image

2. **Simple Answer**: One clear sentence answering the question directly

3. **Calculation Steps**: 
   - Use ONLY if calculation is needed
   - Keep to 2-4 steps maximum
   - Include units where relevant
   - If no calculation needed, use reasoning steps instead

4. **Detailed Explanation**:
   - "why_correct": Explain the reasoning behind the correct answer
   - "why_others_wrong": For each wrong option, explain the specific mistake or misconception

5. **Topics** (choose the most relevant):
   - "Motion and Forces" 
   - "Energy and Power"
   - "Heat and Temperature"
   - "Waves and Sound"
   - "Light and Optics"
   - "Electricity and Circuits"
   - "Magnetism and Electromagnetism"
   - "Atomic and Nuclear Physics"
   - "Space and Astronomy"

6. **Difficulty Levels**:
   - "easy": Basic recall or simple application
   - "medium": Multi-step reasoning or calculation  
   - "hard": Complex analysis or advanced concepts

7. **Confidence Score**:
   - 0.95-1.0: Completely certain
   - 0.85-0.94: Very confident
   - 0.70-0.84: Moderately confident  
   - Below 0.85: Set auto_flagged: true

8. **Auto-flagging**: Set auto_flagged: true if confidence_score < 0.85

Focus on clarity and educational value. The explanation should help students understand not just the right answer, but why the other options are wrong."""

# UPDATE THE JAVASCRIPT PROMPT FUNCTION IN THE HTML INTERFACE
javascript_prompt_update = """
function generatePrompt(questionNum) {
    return `Please analyze this Cambridge IGCSE ${subject} question ${questionNum} and provide a clear, focused analysis.

IMPORTANT: Extract ALL text accurately and use this EXACT JSON format:

{
  "question_text": "Complete question text extracted from image word-for-word",
  "options": {
    "A": "Option A text exactly as shown",
    "B": "Option B text exactly as shown",
    "C": "Option C text exactly as shown", 
    "D": "Option D text exactly as shown"
  },
  
  "correct_answer": "C",
  "simple_answer": "Brief, clear answer in one sentence",
  
  "calculation_steps": [
    "Step 1: What you identify or set up",
    "Step 2: The main calculation or reasoning", 
    "Step 3: Final result with units if applicable"
  ],
  
  "detailed_explanation": {
    "why_correct": "Clear explanation of why the correct answer is right",
    "why_others_wrong": {
      "A": "Specific reason why option A is incorrect",
      "B": "Specific reason why option B is incorrect",
      "D": "Specific reason why option D is incorrect"
    }
  },
  
  "topic": "Motion and Forces",
  "difficulty": "medium", 
  "confidence_score": 0.95,
  "auto_flagged": false
}

FOCUS ON:
1. Extract ALL text from image accurately
2. Give a simple, direct answer
3. Show calculation steps only if math is involved
4. Explain why each wrong answer is wrong
5. Set auto_flagged: true if confidence < 0.85`;
}
"""

# UPDATE THE VALIDATION FUNCTION
def validate_simplified_solution(solution):
    """Validate the simplified solution format"""
    required_fields = [
        'question_text', 'options', 'correct_answer', 
        'simple_answer', 'detailed_explanation', 
        'topic', 'confidence_score'
    ]
    
    missing_fields = []
    for field in required_fields:
        if not solution.get(field):
            missing_fields.append(field)
    
    # Validate detailed_explanation structure
    explanation = solution.get('detailed_explanation', {})
    if not explanation.get('why_correct'):
        missing_fields.append('detailed_explanation.why_correct')
    if not explanation.get('why_others_wrong'):
        missing_fields.append('detailed_explanation.why_others_wrong')
    
    # Validate options
    options = solution.get('options', {})
    expected_options = ['A', 'B', 'C', 'D']
    for opt in expected_options:
        if opt not in options:
            missing_fields.append(f'options.{opt}')
    
    return {
        'valid': len(missing_fields) == 0,
        'missing_fields': missing_fields,
        'has_calculation': 'calculation_steps' in solution and solution['calculation_steps'],
        'explanation_complete': (
            explanation.get('why_correct') and 
            explanation.get('why_others_wrong') and
            len(explanation.get('why_others_wrong', {})) >= 3
        )
    }
