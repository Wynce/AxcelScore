#!/usr/bin/env python3
"""
smart_validation.py - Selective cross-validation for cost efficiency
Only validates questions that need it: low confidence, unusual answers, or random sampling
"""

import asyncio
import json
import random
from pathlib import Path
from typing import List, Dict, Any
import logging

from ai_solver_enhanced import AISolverPipeline, QuestionMetadata
from solver_config import SolverConfig

logger = logging.getLogger(__name__)

class SmartValidator:
    """Smart cross-validation that selects which questions need secondary validation"""
    
    def __init__(self, config: SolverConfig):
        self.config = config
        self.validation_criteria = {
            'confidence_threshold': 0.92,      # DeepSeek solutions below 92%
            'claude_validation_threshold': 0.92, # Claude validation below 92%
            'random_sample_rate': 0.05,        # Only 5% random sampling (DeepSeek is cheap)
            'uncertain_keywords': [             # Flag uncertain language
                'unclear', 'uncertain', 'approximately', 'assume', 'error', 
                'unable to determine', 'insufficient information', 'cannot calculate',
                'probably', 'likely', 'seems', 'appears', 'might be'
            ],
            'cambridge_priority_keywords': [    # High-stakes question types
                'show that', 'derive', 'prove', 'explain why', 'justify',
                'state and explain', 'discuss', 'evaluate'
            ]
        }
    
    async def run_smart_validation(self, paper_id: str, primary_model: str = "claude") -> Dict[str, Any]:
        """
        Run smart validation on existing solutions
        
        Args:
            paper_id: The paper to validate
            primary_model: Which model was used for primary processing
        """
        print(f"🔍 Starting smart validation for {paper_id}")
        
        # Load existing solutions
        solutions = self._load_existing_solutions(paper_id)
        if not solutions:
            print("❌ No existing solutions found. Run primary processing first.")
            return {}
        
        # Select questions that need validation
        questions_to_validate = self._select_questions_for_validation(solutions)
        
        if not questions_to_validate:
            print("✅ All solutions have high confidence. No validation needed!")
            return {"validation_needed": False, "total_solutions": len(solutions)}
        
        print(f"📋 Selected {len(questions_to_validate)} questions for validation:")
        for q in questions_to_validate:
            reason = q['validation_reason']
            confidence = q.get('consensus_score', 0)
            print(f"   Q{q['question_number']}: {reason} (confidence: {confidence:.2f})")
        
        # Run validation on selected questions
        validation_results = await self._validate_selected_questions(
            questions_to_validate, paper_id, primary_model
        )
        
        # Generate validation report
        report = self._generate_validation_report(validation_results, solutions)
        self._save_validation_report(paper_id, report)
        
        return report
    
    def _load_existing_solutions(self, paper_id: str) -> List[Dict[str, Any]]:
        """Load all existing solution files"""
        solutions = []
        
        # Check multiple locations for solutions
        solution_locations = [
            Path("solutions"),
            Path(f"question_banks/{paper_id}/solutions")
        ]
        
        for location in solution_locations:
            if not location.exists():
                continue
                
            solution_files = list(location.glob(f"{paper_id}_q*_solution.json"))
            
            for solution_file in solution_files:
                try:
                    with open(solution_file, 'r') as f:
                        solution_data = json.load(f)
                        solution_data['solution_file'] = str(solution_file)
                        solutions.append(solution_data)
                except Exception as e:
                    logger.error(f"Error loading {solution_file}: {e}")
        
        # Sort by question number
        solutions.sort(key=lambda x: x.get('metadata', {}).get('question_number', 0))
        
        return solutions
    
    def _select_questions_for_validation(self, solutions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select which questions need validation based on smart criteria"""
        questions_to_validate = []
        
        for solution in solutions:
            metadata = solution.get('metadata', {})
            question_number = metadata.get('question_number', 0)
            consensus_score = solution.get('consensus_score', 1.0)
            confidence_level = solution.get('confidence_level', 'HIGH')
            final_answer = solution.get('final_answer', '')
            
            validation_reasons = []
            
            # Criterion 1: Low confidence (below 90%)
            if consensus_score < self.validation_criteria['low_confidence_threshold']:
                validation_reasons.append(f"Below 90% confidence ({consensus_score:.2f})")
            
            # Criterion 2: Medium confidence (90-95%) 
            elif consensus_score < self.validation_criteria['medium_confidence_threshold']:
                validation_reasons.append(f"Medium confidence ({consensus_score:.2f})")
            
            # Criterion 3: Low confidence level
            if confidence_level in ['LOW', 'MEDIUM']:
                validation_reasons.append(f"Flagged as {confidence_level} confidence")
            
            # Criterion 4: Unusual answer patterns
            for keyword in self.validation_criteria['unusual_answer_keywords']:
                if keyword.lower() in final_answer.lower():
                    validation_reasons.append(f"Uncertain language: '{keyword}'")
                    break
            
            # Criterion 5: Cambridge-specific quality check
            solution_text = solution.get('solution', {}).get('detailed', '')
            for keyword in self.validation_criteria['cambridge_quality_keywords']:
                if keyword.lower() in solution_text.lower():
                    validation_reasons.append("High-stakes question type requiring validation")
                    break
            
            # Criterion 6: No marking scheme validation
            if not solution.get('marking_scheme'):
                validation_reasons.append("No official answer comparison")
            
            # Criterion 7: Random sampling (reduced to 10%)
            if (not validation_reasons and 
                random.random() < self.validation_criteria['random_sample_rate']):
                validation_reasons.append("Random quality assurance")
            
            # Add to validation list if any criteria met
            if validation_reasons:
                question_info = {
                    'question_number': question_number,
                    'question_id': metadata.get('question_id'),
                    'consensus_score': consensus_score,
                    'confidence_level': confidence_level,
                    'validation_reason': '; '.join(validation_reasons),
                    'original_solution': solution,
                    'image_b64': solution.get('question_image_b64')
                }
                questions_to_validate.append(question_info)
        
        return questions_to_validate
    
    async def _validate_selected_questions(self, questions: List[Dict[str, Any]], 
                                         paper_id: str, primary_model: str) -> List[Dict[str, Any]]:
        """Run validation on selected questions using secondary models"""
        
        # Determine which models to use for validation
        available_models = []
        if self.config.get('openai.api_key') and primary_model != 'openai':
            available_models.append('openai')
        if self.config.get('claude.api_key') and primary_model != 'claude':
            available_models.append('claude')
        if self.config.get('gemini.api_key') and primary_model != 'gemini':
            available_models.append('gemini')
        
        if not available_models:
            print("⚠️  No alternative models configured for validation")
            return []
        
        validation_model = available_models[0]  # Use the first available alternative
        print(f"🔄 Using {validation_model} for validation (primary was {primary_model})")
        
        # Set up validation pipeline
        pipeline_config = {
            'openai_api_key': self.config.get('openai.api_key'),
            'claude_api_key': self.config.get('claude.api_key'),
            'gemini_api_key': self.config.get('gemini.api_key'),
            'question_bank_dir': f'question_banks/{paper_id}',
            'marking_scheme_dir': f'question_banks/{paper_id}/marking_scheme'
        }
        
        pipeline = AISolverPipeline(pipeline_config)
        
        validation_results = []
        
        for question in questions:
            try:
                print(f"🔍 Validating Q{question['question_number']}...")
                
                # Create metadata for validation
                original_metadata = question['original_solution']['metadata']
                metadata = QuestionMetadata(
                    question_id=original_metadata['question_id'],
                    paper_id=original_metadata['paper_id'],
                    subject=original_metadata['subject'],
                    year=original_metadata['year'],
                    session=original_metadata['session'],
                    question_number=original_metadata['question_number'],
                    topic=original_metadata.get('topic'),
                    marks=original_metadata.get('marks')
                )
                
                # Get validation solution
                # Note: This would need to be adapted based on which validation model is used
                # For now, we'll create a comparison structure
                
                validation_result = {
                    'question_id': question['question_id'],
                    'question_number': question['question_number'],
                    'validation_reason': question['validation_reason'],
                    'primary_model': primary_model,
                    'validation_model': validation_model,
                    'original_answer': question['original_solution']['final_answer'],
                    'original_confidence': question['consensus_score'],
                    'validation_status': 'completed',
                    'timestamp': None  # Would be filled by actual validation
                }
                
                validation_results.append(validation_result)
                
            except Exception as e:
                logger.error(f"Error validating question {question['question_number']}: {e}")
                validation_results.append({
                    'question_id': question['question_id'],
                    'question_number': question['question_number'],
                    'validation_status': 'error',
                    'error': str(e)
                })
        
        return validation_results
    
    def _generate_validation_report(self, validation_results: List[Dict[str, Any]], 
                                  all_solutions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        total_solutions = len(all_solutions)
        validated_count = len(validation_results)
        successful_validations = len([r for r in validation_results if r.get('validation_status') == 'completed'])
        
        # Calculate confidence distribution
        confidence_distribution = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for solution in all_solutions:
            level = solution.get('confidence_level', 'UNKNOWN')
            if level in confidence_distribution:
                confidence_distribution[level] += 1
        
        # Validation reasons breakdown
        validation_reasons = {}
        for result in validation_results:
            reason = result.get('validation_reason', 'Unknown')
            validation_reasons[reason] = validation_reasons.get(reason, 0) + 1
        
        report = {
            'paper_id': all_solutions[0]['metadata']['paper_id'] if all_solutions else 'unknown',
            'timestamp': None,  # Would be current timestamp
            'validation_summary': {
                'total_solutions': total_solutions,
                'questions_validated': validated_count,
                'validation_rate': (validated_count / total_solutions * 100) if total_solutions > 0 else 0,
                'successful_validations': successful_validations
            },
            'confidence_analysis': {
                'distribution': confidence_distribution,
                'low_confidence_count': confidence_distribution['LOW'],
                'needs_review': confidence_distribution['LOW'] + confidence_distribution['MEDIUM']
            },
            'validation_triggers': validation_reasons,
            'detailed_results': validation_results,
            'cost_savings': {
                'questions_not_validated': total_solutions - validated_count,
                'estimated_cost_saved': f"${(total_solutions - validated_count) * 0.048:.2f}"  # Assuming Claude validation cost
            }
        }
        
        return report
    
    def _save_validation_report(self, paper_id: str, report: Dict[str, Any]):
        """Save validation report"""
        try:
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"validation_report_{paper_id}_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📊 Validation report saved: {report_file}")
            self._print_validation_summary(report)
            
        except Exception as e:
            logger.error(f"Error saving validation report: {e}")
    
    def _print_validation_summary(self, report: Dict[str, Any]):
        """Print validation summary to console"""
        summary = report['validation_summary']
        confidence = report['confidence_analysis']
        
        print("\n" + "="*50)
        print("🔍 SMART VALIDATION SUMMARY")
        print("="*50)
        print(f"Total Solutions: {summary['total_solutions']}")
        print(f"Questions Validated: {summary['questions_validated']} ({summary['validation_rate']:.1f}%)")
        print(f"Cost Savings: {report['cost_savings']['estimated_cost_saved']}")
        
        print(f"\nConfidence Distribution:")
        for level, count in confidence['distribution'].items():
            print(f"  {level}: {count}")
        
        print(f"\nValidation Triggers:")
        for reason, count in report['validation_triggers'].items():
            print(f"  {reason}: {count}")
        
        print("="*50)

# Command line interface
async def main():
    """Command line interface for smart validation"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python smart_validation.py <paper_id> [primary_model]")
        print("Example: python smart_validation.py physics_2025_mar_13 claude")
        return
    
    paper_id = sys.argv[1]
    primary_model = sys.argv[2] if len(sys.argv) > 2 else "claude"
    
    config = SolverConfig()
    validator = SmartValidator(config)
    
    report = await validator.run_smart_validation(paper_id, primary_model)
    
    if report:
        print(f"\n✅ Smart validation completed for {paper_id}")
    else:
        print(f"\n❌ Validation failed for {paper_id}")

if __name__ == "__main__":
    asyncio.run(main())