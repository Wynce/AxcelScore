#!/usr/bin/env python3
"""
Data models and schemas for the tutor app
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExamMetadata(BaseModel):
    """Exam metadata model"""
    exam_type: str = Field(default="Cambridge", description="Exam board (e.g., Cambridge)")
    subject: str = Field(..., description="Subject (Physics, Chemistry, Biology)")
    year: int = Field(..., description="Exam year (e.g., 2024)")
    paper_type: str = Field(..., description="Paper type (Core, Extended)")
    paper_code: str = Field(..., description="Paper code (e.g., 11, 12, 13, 21, 22, 23)")
    original_filename: Optional[str] = None
    upload_timestamp: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "exam_type": "Cambridge",
                "subject": "Physics",
                "year": 2024,
                "paper_type": "Extended",
                "paper_code": "13",
                "original_filename": "0625_w24_qp_13.pdf"
            }
        }

class QuestionOptions(BaseModel):
    """Question options model"""
    A: str = Field(default="A")
    B: str = Field(default="B") 
    C: str = Field(default="C")
    D: str = Field(default="D")

class Question(BaseModel):
    """Individual question model"""
    id: str = Field(..., description="Unique question identifier")
    question_number: int = Field(..., description="Question number in paper")
    question_text: str = Field(default="", description="Question text content")
    options: QuestionOptions = Field(default_factory=QuestionOptions)
    image_filename: Optional[str] = Field(None, description="Associated image filename")
    page: Optional[int] = Field(None, description="Page number in original PDF")
    marks: Optional[int] = Field(1, description="Marks allocated")
    subject: str = Field(default="physics", description="Subject area")
    difficulty: str = Field(default="medium", description="Difficulty level")
    
    # AI solver fields
    correct_answer: str = Field(default="", description="Correct answer (A, B, C, D)")
    explanation: str = Field(default="", description="Step-by-step explanation")
    syllabus_topic: str = Field(default="", description="Main syllabus topic")
    sub_topic: str = Field(default="", description="Specific sub-topic")
    keywords: List[str] = Field(default_factory=list, description="Relevant keywords")
    difficulty_level: str = Field(default="medium", description="AI-assessed difficulty")
    formula_used: List[str] = Field(default_factory=list, description="Formulas used in solution")
    confidence_score: float = Field(default=0.5, description="AI confidence in solution")
    
    # Status and metadata
    has_images: bool = Field(default=True, description="Whether question has images")
    ai_solved: bool = Field(default=False, description="Whether AI has solved this question")
    ai_solver_version: Optional[str] = Field(None, description="AI solver version used")
    solving_timestamp: Optional[str] = Field(None, description="When question was solved")
    
    # Quality control flags
    needs_review: bool = Field(default=False, description="Requires human review")
    flagged_bad_image: bool = Field(default=False, description="Image quality issues")
    flagged_wrong_answer: bool = Field(default=False, description="Potentially wrong answer")
    flagged_low_confidence: bool = Field(default=False, description="Low AI confidence")
    auto_flagged: bool = Field(default=False, description="Automatically flagged by system")
    
    # Manual updates
    image_manually_updated: bool = Field(default=False, description="Image manually replaced")
    manually_verified: bool = Field(default=False, description="Manually verified by human")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    
    # Extraction metadata
    extraction_method: str = Field(default="boundary_detection", description="How question was extracted")
    detection_strategy: Optional[str] = Field(None, description="Detection strategy used")
    extraction_confidence: float = Field(default=0.8, description="Extraction confidence")

class QuestionBank(BaseModel):
    """Complete question bank model"""
    metadata: Dict[str, Any] = Field(..., description="Question bank metadata")
    questions: List[Question] = Field(..., description="List of questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "app_name": "Tutor App",
                    "exam_paper": "Cambridge IGCSE Physics 0625/13",
                    "total_questions": 25,
                    "created_date": "2024-08-06T10:00:00",
                    "version": "1.0.0"
                },
                "questions": []
            }
        }

class ExtractionResult(BaseModel):
    """Result from PDF extraction process"""
    success: bool = Field(..., description="Whether extraction succeeded")
    questions: List[Question] = Field(default_factory=list, description="Extracted questions")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Extraction statistics")
    error: Optional[str] = Field(None, description="Error message if failed")
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class SolverResult(BaseModel):
    """Result from AI solving process"""
    success: bool = Field(..., description="Whether solving succeeded")
    questions: List[Question] = Field(default_factory=list, description="Solved questions")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Solving statistics")
    interface_url: Optional[str] = Field(None, description="URL to solving interface")
    error: Optional[str] = Field(None, description="Error message if failed")
    solving_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class SessionStatus(BaseModel):
    """Current session status"""
    session_id: Optional[str] = Field(None, description="Current session ID")
    status: str = Field(default="idle", description="Current processing status")
    questions_count: int = Field(default=0, description="Number of questions processed")
    metadata: Optional[ExamMetadata] = Field(None, description="Current exam metadata")
    progress: float = Field(default=0.0, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current processing step")

class QuestionFilters(BaseModel):
    """Filters for querying question bank"""
    subject: Optional[str] = Field(None, description="Filter by subject")
    year: Optional[int] = Field(None, description="Filter by year") 
    difficulty: Optional[str] = Field(None, description="Filter by difficulty")
    paper_type: Optional[str] = Field(None, description="Filter by paper type")
    paper_code: Optional[str] = Field(None, description="Filter by paper code")
    topic: Optional[str] = Field(None, description="Filter by syllabus topic")
    needs_review: Optional[bool] = Field(None, description="Filter by review status")
    flagged_only: Optional[bool] = Field(None, description="Show only flagged questions")
    approved_only: Optional[bool] = Field(True, description="Show only approved questions")
    limit: Optional[int] = Field(None, description="Limit number of results")
    random: bool = Field(False, description="Random selection")

class ProcessingStats(BaseModel):
    """Processing statistics"""
    total_questions: int = Field(default=0)
    extracted_questions: int = Field(default=0)
    solved_questions: int = Field(default=0)
    approved_questions: int = Field(default=0)
    flagged_questions: int = Field(default=0)
    manual_reviews_needed: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    approval_rate: float = Field(default=0.0)
    average_confidence: float = Field(default=0.0)
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool = Field(..., description="Whether request succeeded")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error details if failed")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Response models for specific endpoints
class UploadResponse(APIResponse):
    """Upload endpoint response"""
    session_id: Optional[str] = None
    filename: Optional[str] = None
    metadata: Optional[ExamMetadata] = None

class ExtractionResponse(APIResponse):
    """Extraction endpoint response"""
    questions_found: Optional[int] = None
    questions: Optional[List[Question]] = None
    extraction_stats: Optional[Dict[str, Any]] = None

class SolvingResponse(APIResponse):
    """Solving endpoint response"""
    interface_url: Optional[str] = None
    questions_count: Optional[int] = None
    processing_stats: Optional[ProcessingStats] = None

class QuestionBankResponse(APIResponse):
    """Question bank query response"""
    questions: List[Question] = Field(default_factory=list)
    total: int = Field(default=0)
    filtered: int = Field(default=0)
    filters_applied: Optional[QuestionFilters] = None
    metadata: Optional[Dict[str, Any]] = None