#!/usr/bin/env python3
"""
setup_solver.py - Setup script for AI Solver System
"""

import os
import json
from pathlib import Path
from solver_config import SolverConfig

def setup_solver_system():
    """Setup the AI Solver System in the existing backend"""
    print("🚀 Setting up AI Solver System...")
    print("="*50)
    
    # 1. Create configuration
    config = SolverConfig()
    print("✅ Configuration system initialized")
    
    # 2. Create necessary directories
    directories = [
        "question_banks",
        "solutions",
        "reports",
        "marking_schemes"
    ]
    
    print("\n📁 Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   Created: {directory}/")
    
    # 3. Create sample question bank structure
    sample_paper = config.get('paths.default_paper', 'physics_2025_mar_13')
    print(f"\n📚 Setting up sample question bank: {sample_paper}")
    
    paper_dirs = [
        f"question_banks/{sample_paper}",
        f"question_banks/{sample_paper}/images",
        f"question_banks/{sample_paper}/solutions", 
        f"question_banks/{sample_paper}/marking_scheme",
        f"question_banks/{sample_paper}/validation",
        f"question_banks/{sample_paper}/reports"
    ]
    
    for directory in paper_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print(f"   Created question bank structure for: {sample_paper}")
    
    # 4. Create sample marking scheme
    print("\n📋 Creating sample marking scheme...")
    sample_marking = create_sample_marking_scheme()
    
    marking_file = f"question_banks/{sample_paper}/marking_scheme/{sample_paper}_marking_scheme.json"
    try:
        with open(marking_file, 'w') as f:
            json.dump(sample_marking, f, indent=2)
        print(f"   Created: {marking_file}")
    except Exception as e:
        print(f"   ❌ Error creating marking scheme: {e}")
    
    # 5. Create requirements file if it doesn't exist
    print("\n📄 Checking requirements...")
    create_requirements_file()
    
    # 6. Create example usage file
    print("\n📝 Creating example usage file...")
    create_example_usage()
    
    # 7. Check API keys
    print("\n🔑 Checking API Key Configuration:")
    check_api_keys(config)
    
    # 8. Create instructions file
    create_instructions_file(sample_paper)
    
    print("\n✅ Setup completed successfully!")
    print("="*50)
    
    return True

def create_sample_marking_scheme():
    """Create a comprehensive sample marking scheme"""
    return {
        "paper_info": {
            "subject": "Physics",
            "level": "A Level",
            "year": 2025,
            "session": "March",
            "total_marks": 100
        },
        "q01": {
            "answer": "9.8 m/s²",
            "marking_points": [
                "Correct identification of acceleration due to gravity",
                "Proper use of kinematic equations",
                "Correct substitution of values",
                "Appropriate units (m/s²)"
            ],
            "marks": 4,
            "topic": "Mechanics - Motion",
            "difficulty": "Medium"
        },
        "q02": {
            "answer": "24 J",
            "marking_points": [
                "Correct energy formula (KE = ½mv²)",
                "Substitution of mass and velocity",
                "Correct calculation",
                "Appropriate units (J)"
            ],
            "marks": 3,
            "topic": "Energy",
            "difficulty": "Easy"
        },
        "q03": {
            "answer": "2.5 × 10⁸ m/s",
            "marking_points": [
                "Application of wave equation v = fλ",
                "Correct identification of frequency and wavelength",
                "Scientific notation used appropriately",
                "Correct significant figures"
            ],
            "marks": 5,
            "topic": "Waves",
            "difficulty": "Hard"
        },
        "q04": {
            "answer": "1.6 A",
            "marking_points": [
                "Ohm's law correctly applied (V = IR)",
                "Rearrangement to find current (I = V/R)",
                "Correct substitution",
                "Appropriate units and significant figures"
            ],
            "marks": 3,
            "topic": "Electricity",
            "difficulty": "Medium"
        },
        "q05": {
            "answer": "450 N",
            "marking_points": [
                "Newton's second law applied (F = ma)",
                "Correct calculation of acceleration",
                "Force calculation with correct direction",
                "Appropriate units (N)"
            ],
            "marks": 6,
            "topic": "Forces",
            "difficulty": "Hard"
        }
    }

def create_requirements_file():
    """Create or update requirements.txt"""
    requirements = """# AI Solver System Requirements
aiohttp>=3.8.0
Pillow>=9.0.0
openai>=1.0.0
anthropic>=0.8.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
tqdm>=4.64.0
numpy>=1.21.0
pandas>=1.3.0

# Optional: For web interface integration
fastapi>=0.68.0
uvicorn>=0.15.0

# Optional: For enhanced text processing
nltk>=3.6
scikit-learn>=1.0.0
"""

    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        with open(requirements_file, "w") as f:
            f.write(requirements)
        print("   Created: requirements.txt")
    else:
        print("   requirements.txt already exists")

def create_example_usage():
    """Create an example usage file"""
    example_code = '''#!/usr/bin/env python3
"""
example_usage.py - Examples of how to use the AI Solver System
"""

import asyncio
from solver_config import SolverConfig
from ai_solver_enhanced import AISolverPipeline, QuestionMetadata, solve_single_image
from batch_processor import run_batch_processing

async def example_single_question():
    """Example: Process a single question"""
    print("🔍 Example: Processing single question")
    
    try:
        # Method 1: Quick solve
        result = await solve_single_image(
            "uploads/sample_question.png",  # Your image path
            "physics_2025_mar_13",          # Paper ID
            1                               # Question number
        )
        
        print(f"✅ Solution completed!")
        print(f"Confidence: {result.confidence_level}")
        print(f"Final Answer: {result.final_answer}")
        print(f"Consensus Score: {result.consensus_score:.2f}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def example_batch_processing():
    """Example: Process multiple questions"""
    print("🔍 Example: Batch processing")
    
    try:
        # Process all questions in a paper
        summary = await run_batch_processing("physics_2025_mar_13")
        
        if summary:
            print(f"✅ Processed {summary['total_processed']} questions")
            print(f"Success rate: {summary['success_rate']:.1f}%")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def example_custom_pipeline():
    """Example: Custom pipeline configuration"""
    print("🔍 Example: Custom pipeline setup")
    
    try:
        # Load configuration
        config = SolverConfig()
        
        # Custom pipeline configuration
        pipeline_config = {
            'openai_api_key': config.get('openai.api_key'),
            'claude_api_key': config.get('claude.api_key'),
            'question_bank_dir': 'question_banks/physics_2025_mar_13',
            'marking_scheme_dir': 'question_banks/physics_2025_mar_13/marking_scheme'
        }
        
        # Create pipeline
        pipeline = AISolverPipeline(pipeline_config)
        
        # Create custom metadata
        metadata = QuestionMetadata(
            question_id="custom_q01",
            paper_id="physics_2025_mar_13",
            subject="Physics",
            year=2025,
            session="March",
            question_number=1,
            topic="Mechanics",
            marks=5
        )
        
        # Process question
        solution = await pipeline.solve_question(
            "uploads/your_image.png",  # Replace with actual image path
            metadata
        )
        
        print(f"✅ Custom processing completed!")
        print(f"Question ID: {solution.metadata.question_id}")
        print(f"Confidence: {solution.confidence_level}")
        
        return solution
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def example_config_management():
    """Example: Configuration management"""
    print("🔍 Example: Configuration management")
    
    # Load configuration
    config = SolverConfig()
    
    # Check API keys
    print("API Key Status:")
    config.check_api_keys()
    
    # Update API key (example)
    # config.update_api_key('openai', 'your-new-api-key')
    
    # Get specific configuration values
    max_concurrent = config.get('processing.max_concurrent', 3)
    print(f"Max concurrent processing: {max_concurrent}")
    
    # Update configuration
    config.set('processing.max_concurrent', 5)
    print("Updated max concurrent to 5")

async def main():
    """Run all examples"""
    print("🚀 AI Solver System - Usage Examples")
    print("="*50)
    
    # Configuration example
    example_config_management()
    print()
    
    # Check if API key is configured
    config = SolverConfig()
    if not config.get('openai.api_key'):
        print("⚠️  Please configure your OpenAI API key first:")
        print("   Edit solver_config.json and add your API key")
        return
    
    # Single question example
    await example_single_question()
    print()
    
    # Batch processing example  
    await example_batch_processing()
    print()
    
    # Custom pipeline example
    await example_custom_pipeline()

if __name__ == "__main__":
    asyncio.run(main())
'''

    with open("example_usage.py", "w") as f:
        f.write(example_code)
    print("   Created: example_usage.py")

def check_api_keys(config):
    """Check and display API key status"""
    keys_status = config.check_api_keys()
    
    if not any(keys_status.values()):
        print("\n⚠️  No API keys configured yet!")
        print("   Please edit solver_config.json to add your API keys")
    elif keys_status['openai']:
        print("✅ OpenAI API key is configured - ready to process!")
    else:
        print("⚠️  OpenAI API key is required for basic functionality")

def create_instructions_file(sample_paper):
    """Create detailed instructions file"""
    instructions = f"""# AI Solver System - Quick Start Guide

## 🚀 Getting Started

### 1. Configure API Keys
Edit `solver_config.json` and add your OpenAI API key:
```json
{{
  "openai": {{
    "api_key": "sk-your-openai-api-key-here"
  }}
}}
```

### 2. Add Question Images
Place your question images in one of these locations:
- `question_banks/{sample_paper}/images/`
- `uploads/`
- Current directory

Supported formats: PNG, JPG
Naming: Any format (question_01.png, q1.jpg, etc.)

### 3. Add Marking Schemes (Optional)
Create marking scheme files in:
- `question_banks/{sample_paper}/marking_scheme/{sample_paper}_marking_scheme.json`

See the sample file for format examples.

## 🔧 Usage Commands

### Setup System
```bash
python setup_solver.py
```

### Process All Questions
```bash
python run_solver.py batch {sample_paper}
```

### Process Specific Range
```bash
python run_solver.py batch {sample_paper} 1 10  # Questions 1-10
```

### Process Single Question
```bash
python run_solver.py single path/to/image.png {sample_paper}
```

### Check Configuration
```bash
python solver_config.py
```

## 📊 Output

### Solutions
- Saved in: `solutions/` and `question_banks/{sample_paper}/solutions/`
- Format: JSON with complete solution data
- Includes: Simple & detailed explanations, calculations, confidence scores

### Reports
- Saved in: `reports/`
- Format: JSON with batch processing summaries
- Includes: Success rates, confidence distribution, estimated marks

## 🎯 Key Features

✅ **Cambridge-specific prompting** - Optimized for A-level standards
✅ **Multi-tier explanations** - Simple + detailed solutions
✅ **Marking scheme validation** - Compare against official answers
✅ **Confidence scoring** - HIGH/MEDIUM/LOW reliability assessment
✅ **Batch processing** - Handle multiple questions automatically
✅ **Progress tracking** - Real-time processing updates

## 🔍 Troubleshooting

### No images found
- Check image file locations
- Verify supported formats (PNG, JPG)
- Ensure files are not corrupted

### API errors
- Verify API key is correct
- Check internet connection
- Ensure sufficient API credits

### Low confidence scores
- Check image quality and clarity
- Verify marking scheme accuracy
- Consider manual review for complex questions

## 📞 Support

For issues or questions:
1. Check the example_usage.py file
2. Review solver_config.json settings
3. Examine batch processing reports for error details
"""

    with open("INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    print("   Created: INSTRUCTIONS.md")

def main():
    """Main setup function"""
    try:
        setup_solver_system()
        
        print("\n📋 Next Steps:")
        print("1. Edit solver_config.json with your OpenAI API key")
        print("2. Place question images in question_banks/physics_2025_mar_13/images/")
        print("3. Run: python run_solver.py batch physics_2025_mar_13")
        print("4. Check INSTRUCTIONS.md for detailed usage guide")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    main()