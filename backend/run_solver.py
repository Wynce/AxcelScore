#!/usr/bin/env python3
"""
run_solver.py - Main runner script for AI Solver System
Simple command-line interface for all solver operations
"""

import asyncio
import sys
import argparse
from pathlib import Path

def print_banner():
    """Print the application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   🎓 AI SOLVER SYSTEM                        ║
║              Cambridge Exam Question Processor               ║
║                                                              ║
║  Multi-layer validation • Cambridge marking scheme           ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_help():
    """Print detailed help information"""
    help_text = """
🚀 USAGE COMMANDS:

📋 SETUP & CONFIGURATION:
  python run_solver.py setup                           # Initialize the system
  python run_solver.py config                          # Check configuration
  python run_solver.py config --set-key deepseek sk-xxx # Set DeepSeek API key
  python run_solver.py config --set-key claude sk-xxx   # Set Claude API key
  python run_solver.py config --cost                   # Show cost estimates

📝 PROCESSING QUESTIONS (DeepSeek + Claude Strategy):
  python run_solver.py batch <paper_id>                 # Process all questions
  python run_solver.py batch <paper_id> --range 1 10   # Process questions 1-10
  python run_solver.py single <image_path> <paper_id>   # Process single question
  python run_solver.py test                             # Test with sample data

📊 ANALYSIS & REPORTS:
  python run_solver.py report <paper_id>        # Generate detailed report
  python run_solver.py list                     # List available papers
  python run_solver.py status <paper_id>        # Check processing status

🎯 EXAMPLES:
  python run_solver.py setup
  python run_solver.py config --set-key deepseek your-deepseek-key
  python run_solver.py config --set-key claude your-claude-key
  python run_solver.py batch physics_2025_mar_13
  python run_solver.py single uploads/q1.png physics_2025_mar_13

💰 COST-OPTIMIZED STRATEGY:
  ✅ Primary: DeepSeek (~$0.02 for 40 questions)
  ✅ Validation: Claude for <92% confidence (~$0.70 for typical validation)
  ✅ Total: ~$0.72 for 40 questions with 92%+ accuracy
  ✅ Manual review: Questions that fail both DeepSeek + Claude validation

📁 FILE LOCATIONS:
  Question images:  question_banks/<paper_id>/images/ OR uploads/
  Solutions:        solutions/ AND question_banks/<paper_id>/solutions/
  Manual review:    manual_review/ (flagged questions)
  Reports:          reports/
  Configuration:    solver_config.json

🔧 API KEYS NEEDED:
  Required: DeepSeek API key (get from https://platform.deepseek.com/)
  Recommended: Claude API key (for validation of low-confidence solutions)
"""
    print(help_text)

def main():
    """Main entry point with command parsing"""
    
    # Print banner for all commands
    print_banner()
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="AI Solver System - Cambridge Exam Question Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # We'll handle help ourselves
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Initialize the system')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--check', action='store_true', help='Check current configuration')
    config_parser.add_argument('--set-key', nargs=2, metavar=('SERVICE', 'KEY'), 
                              help='Set API key for service (deepseek, claude, openai, gemini)')
    config_parser.add_argument('--cost', action='store_true', help='Show cost estimates')
    
    # Batch processing command
    batch_parser = subparsers.add_parser('batch', help='Process questions in batch')
    batch_parser.add_argument('paper_id', help='Paper ID to process (e.g., physics_2025_mar_13)')
    batch_parser.add_argument('--range', nargs=2, type=int, metavar=('START', 'END'),
                             help='Question range to process (e.g., --range 1 10)')
    batch_parser.add_argument('--config', default='solver_config.json', help='Config file path')
    
    # Single question command
    single_parser = subparsers.add_parser('single', help='Process single question')
    single_parser.add_argument('image_path', help='Path to question image')
    single_parser.add_argument('paper_id', help='Paper ID (e.g., physics_2025_mar_13)')
    single_parser.add_argument('--question-num', type=int, default=1, help='Question number')
    single_parser.add_argument('--config', default='solver_config.json', help='Config file path')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test system with sample data')
    test_parser.add_argument('--config', default='solver_config.json', help='Config file path')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate analysis report')
    report_parser.add_argument('paper_id', nargs='?', help='Paper ID for specific report')
    report_parser.add_argument('--latest', action='store_true', help='Show latest batch report')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available papers and solutions')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check processing status')
    status_parser.add_argument('paper_id', help='Paper ID to check')
    
    # Help command
    help_parser = subparsers.add_parser('help', help='Show detailed help')
    
    # Parse arguments
    if len(sys.argv) == 1:
        print_help()
        return
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'setup':
        run_setup()
    elif args.command == 'config':
        run_config(args)
    elif args.command == 'batch':
        asyncio.run(run_batch_processing(args))
    elif args.command == 'single':
        asyncio.run(run_single_question(args))
    elif args.command == 'test':
        asyncio.run(run_test(args))
    elif args.command == 'report':
        run_report(args)
    elif args.command == 'list':
        run_list()
    elif args.command == 'status':
        run_status(args)
    elif args.command == 'help':
        print_help()
    else:
        print_help()

def run_setup():
    """Run system setup"""
    try:
        from setup_solver import setup_solver_system
        print("🚀 Initializing AI Solver System...")
        success = setup_solver_system()
        if success:
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
    except ImportError:
        print("❌ Error: setup_solver.py not found. Please ensure all files are in place.")
    except Exception as e:
        print(f"❌ Setup error: {e}")

def run_config(args):
    """Handle configuration commands"""
    try:
        from solver_config import SolverConfig
        
        config = SolverConfig()
        
        if args.set_key:
            service, api_key = args.set_key
            config.update_api_key(service, api_key)
            print(f"✅ Updated {service} API key")
        elif args.cost:
            show_cost_estimates()
        else:
            print("🔑 Current Configuration Status:")
            config.check_api_keys()
            
            print(f"\n📁 File Paths:")
            print(f"Question banks: {config.get('paths.question_bank_base')}")
            print(f"Default paper: {config.get('paths.default_paper')}")
            print(f"Uploads directory: {config.get('paths.uploads_dir')}")
            
            print(f"\n⚙️  Validation Settings:")
            print(f"Primary model: {config.get('validation.primary_model', 'deepseek')}")
            print(f"Validation model: {config.get('validation.validation_model', 'claude')}")
            print(f"Confidence threshold: {config.get('validation.confidence_threshold', 0.92)}")
            print(f"Manual review threshold: {config.get('validation.manual_review_threshold', 0.92)}")
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")

def show_cost_estimates():
    """Show cost estimates for different strategies"""
    print("\n💰 COST ESTIMATES FOR 40 QUESTIONS")
    print("=" * 50)
    print("🎯 RECOMMENDED STRATEGY (DeepSeek + Claude validation):")
    print("   Primary DeepSeek (40 questions):     $0.02")
    print("   Claude validation (~15-20 questions): $0.72 - $0.96")
    print("   TOTAL:                               $0.74 - $0.98")
    print("   Expected accuracy:                   92-96%")
    print()
    print("💸 OTHER OPTIONS:")
    print("   Claude only (40 questions):         $1.92")
    print("   OpenAI only (40 questions):         $3.60")
    print("   Gemini only (40 questions):         $0.20")
    print()
    print("🎯 SCALING PROJECTIONS:")
    print("   100 questions (DeepSeek + Claude):  $1.85 - $2.45")
    print("   500 questions (DeepSeek + Claude):  $9.25 - $12.25")
    print("   1000 questions (DeepSeek + Claude): $18.50 - $24.50")

async def run_batch_processing(args):
    """Run batch processing with DeepSeek + Claude validation"""
    try:
        from batch_processor import run_batch_processing
        
        print(f"🚀 Starting DeepSeek + Claude validation for: {args.paper_id}")
        
        question_range = tuple(args.range) if args.range else None
        if question_range:
            print(f"📝 Processing questions {question_range[0]} to {question_range[1]}")
        
        summary = await run_batch_processing(args.paper_id, question_range)
        
        if summary and 'error' not in summary:
            print(f"\n🎉 Batch processing completed!")
            print(f"✅ Success rate: {summary.get('success_rate', 0):.1f}%")
            
            # Show validation statistics
            validation_stats = summary.get('validation_statistics', {})
            if validation_stats:
                print(f"🔍 Validation Statistics:")
                print(f"   DeepSeek passed directly: {validation_stats.get('deepseek_passed', 0)}")
                print(f"   Claude validated: {validation_stats.get('claude_validated', 0)}")
                print(f"   Manual review needed: {validation_stats.get('manual_review', 0)}")
            
            # Show cost estimate
            total_questions = summary.get('total_processed', 0)
            claude_validations = validation_stats.get('claude_validated', 0) if validation_stats else total_questions * 0.4
            estimated_cost = (total_questions * 0.0005) + (claude_validations * 0.048)
            print(f"💰 Estimated cost: ${estimated_cost:.2f}")
            
            if summary.get('total_max_marks', 0) > 0:
                estimated_percentage = summary.get('estimated_percentage', 0)
                print(f"📊 Estimated score: {estimated_percentage:.1f}%")
        else:
            print(f"\n❌ Batch processing failed: {summary.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Batch processing error: {e}")

async def run_single_question(args):
    """Process single question with DeepSeek + Claude validation"""
    try:
        from ai_solver_enhanced import solve_single_image
        
        print(f"📝 Processing with DeepSeek + Claude validation...")
        print(f"Image: {args.image_path}")
        print(f"Paper: {args.paper_id}")
        
        if not Path(args.image_path).exists():
            print(f"❌ Error: Image file not found: {args.image_path}")
            return
        
        solution = await solve_single_image(
            args.image_path, 
            args.paper_id, 
            args.question_num
        )
        
        print(f"\n✅ Solution completed!")
        print(f"🤖 Primary model: {solution.primary_model}")
        print(f"🔍 Validation status: {solution.validation_status}")
        print(f"🎯 Confidence: {solution.confidence_level}")
        print(f"📊 Consensus Score: {solution.consensus_score:.2f}")
        print(f"💡 Final Answer: {solution.final_answer}")
        
        if solution.cross_validations:
            for validation in solution.cross_validations:
                print(f"🔄 {validation.ai_model}: {validation.confidence_score:.2f} confidence")
                if validation.comments:
                    print(f"   Comments: {validation.comments}")
        
        if solution.marking_scheme:
            estimated_marks = solution.marking_scheme.estimated_marks
            max_marks = solution.marking_scheme.max_marks
            print(f"📋 Estimated Marks: {estimated_marks:.1f}/{max_marks}")
        
        if solution.validation_status == "MANUAL_REVIEW":
            print(f"⚠️  This question has been flagged for manual review")
        
    except Exception as e:
        print(f"❌ Single question processing error: {e}")

async def run_test(args):
    """Run system test"""
    try:
        from solver_config import SolverConfig
        
        config = SolverConfig()
        
        print("🧪 Running system tests...")
        
        # Test 1: Configuration
        print("\n1️⃣ Testing configuration...")
        if config.get('openai.api_key'):
            print("   ✅ OpenAI API key configured")
        else:
            print("   ❌ OpenAI API key not configured")
            print("   Run: python run_solver.py config --set-key openai YOUR_API_KEY")
            return
        
        # Test 2: Directory structure
        print("\n2️⃣ Testing directory structure...")
        required_dirs = ['question_banks', 'solutions', 'reports']
        for directory in required_dirs:
            if Path(directory).exists():
                print(f"   ✅ {directory}/ exists")
            else:
                print(f"   ❌ {directory}/ missing")
        
        # Test 3: Sample images
        print("\n3️⃣ Checking for test images...")
        test_locations = [
            "uploads/",
            "question_banks/physics_2025_mar_13/images/",
            "."
        ]
        
        found_images = []
        for location in test_locations:
            path = Path(location)
            if path.exists():
                images = list(path.glob("*.png")) + list(path.glob("*.jpg"))
                if images:
                    found_images.extend(images[:3])  # Take first 3
        
        if found_images:
            print(f"   ✅ Found {len(found_images)} test images")
            for img in found_images[:3]:
                print(f"      - {img}")
        else:
            print("   ⚠️  No test images found")
            print("      Place some PNG/JPG question images in uploads/ to test")
        
        # Test 4: Try processing if images available
        if found_images:
            print("\n4️⃣ Testing processing...")
            try:
                from ai_solver_enhanced import solve_single_image
                
                test_image = found_images[0]
                print(f"   Testing with: {test_image}")
                
                result = await solve_single_image(str(test_image))
                
                print("   ✅ Processing test successful!")
                print(f"   Confidence: {result.confidence_level}")
                print(f"   Answer: {result.final_answer[:50]}...")
                
            except Exception as e:
                print(f"   ❌ Processing test failed: {e}")
        
        print("\n🎉 System test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

def run_report(args):
    """Generate analysis report"""
    try:
        reports_dir = Path("reports")
        
        if args.paper_id:
            # Show reports for specific paper
            paper_reports = list(reports_dir.glob(f"batch_report_{args.paper_id}_*.json"))
            if paper_reports:
                latest_report = max(paper_reports, key=lambda x: x.stat().st_mtime)
                print(f"📊 Latest report for {args.paper_id}:")
                show_report_summary(latest_report)
            else:
                print(f"❌ No reports found for {args.paper_id}")
        
        elif args.latest:
            # Show latest report
            all_reports = list(reports_dir.glob("batch_report_*.json"))
            if all_reports:
                latest_report = max(all_reports, key=lambda x: x.stat().st_mtime)
                print("📊 Latest batch report:")
                show_report_summary(latest_report)
            else:
                print("❌ No reports found")
        
        else:
            # List all reports
            all_reports = list(reports_dir.glob("batch_report_*.json"))
            if all_reports:
                print("📊 Available Reports:")
                for report in sorted(all_reports, key=lambda x: x.stat().st_mtime, reverse=True):
                    print(f"   {report.name}")
            else:
                print("❌ No reports found")
                
    except Exception as e:
        print(f"❌ Report error: {e}")

def show_report_summary(report_file):
    """Show summary of a report file"""
    try:
        import json
        
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        print(f"   File: {report_file.name}")
        print(f"   Paper: {report.get('paper_id')}")
        print(f"   Date: {report.get('timestamp', '')[:19]}")
        print(f"   Total Questions: {report.get('total_processed')}")
        print(f"   Success Rate: {report.get('success_rate', 0):.1f}%")
        print(f"   Average Consensus: {report.get('average_consensus_score', 0):.2f}")
        
        if report.get('total_max_marks', 0) > 0:
            print(f"   Estimated Score: {report.get('estimated_percentage', 0):.1f}%")
        
        confidence_dist = report.get('confidence_distribution', {})
        if confidence_dist:
            print("   Confidence Distribution:")
            for level, count in confidence_dist.items():
                print(f"      {level}: {count}")
                
    except Exception as e:
        print(f"   ❌ Error reading report: {e}")

def run_list():
    """List available papers and solutions"""
    try:
        print("📚 Available Question Banks:")
        
        question_banks_dir = Path("question_banks")
        if question_banks_dir.exists():
            papers = [d for d in question_banks_dir.iterdir() if d.is_dir()]
            if papers:
                for paper in sorted(papers):
                    images_dir = paper / "images"
                    solutions_dir = paper / "solutions"
                    
                    image_count = len(list(images_dir.glob("*.png"))) + len(list(images_dir.glob("*.jpg"))) if images_dir.exists() else 0
                    solution_count = len(list(solutions_dir.glob("*.json"))) if solutions_dir.exists() else 0
                    
                    print(f"   📁 {paper.name}")
                    print(f"      Images: {image_count}, Solutions: {solution_count}")
            else:
                print("   No question banks found")
        else:
            print("   question_banks/ directory not found")
        
        print("\n💾 Recent Solutions:")
        solutions_dir = Path("solutions")
        if solutions_dir.exists():
            solutions = list(solutions_dir.glob("*.json"))
            for solution in sorted(solutions, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                print(f"   📄 {solution.name}")
        else:
            print("   No solutions found")
            
    except Exception as e:
        print(f"❌ List error: {e}")

def run_status(args):
    """Check processing status for a paper"""
    try:
        paper_id = args.paper_id
        
        print(f"📋 Status for: {paper_id}")
        
        # Check images
        images_locations = [
            Path(f"question_banks/{paper_id}/images"),
            Path(f"uploads/{paper_id}"),
            Path("uploads")
        ]
        
        total_images = 0
        for location in images_locations:
            if location.exists():
                images = list(location.glob("*.png")) + list(location.glob("*.jpg"))
                if images:
                    total_images = len(images)
                    print(f"   📸 Images: {total_images} found in {location}")
                    break
        
        if total_images == 0:
            print("   ❌ No images found")
            return
        
        # Check solutions
        solutions_locations = [
            Path(f"question_banks/{paper_id}/solutions"),
            Path("solutions")
        ]
        
        total_solutions = 0
        for location in solutions_locations:
            if location.exists():
                solutions = list(location.glob(f"{paper_id}_*.json"))
                total_solutions += len(solutions)
        
        print(f"   💾 Solutions: {total_solutions}/{total_images}")
        
        # Progress percentage
        if total_images > 0:
            progress = (total_solutions / total_images) * 100
            print(f"   📊 Progress: {progress:.1f}%")
        
        # Check latest report
        reports_dir = Path("reports")
        if reports_dir.exists():
            paper_reports = list(reports_dir.glob(f"batch_report_{paper_id}_*.json"))
            if paper_reports:
                latest_report = max(paper_reports, key=lambda x: x.stat().st_mtime)
                print(f"   📋 Latest report: {latest_report.name}")
            else:
                print("   📋 No processing reports found")
                
    except Exception as e:
        print(f"❌ Status error: {e}")

if __name__ == "__main__":
    main()