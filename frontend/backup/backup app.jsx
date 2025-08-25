import React, { useState, useEffect } from 'react';
import StartScreen from './screens/StartScreen';
import QuestionCard from './components/QuestionCard';
import ResultScreen from './screens/ResultScreen';
import ReviewScreen from './screens/ReviewScreen';

// EMERGENCY: Hard-coded bank for testing
const EMERGENCY_BANK = {
  id: 'physics_2025_mar_13',
  name: 'Physics 2025 Mar 13',
  description: 'Physics Mar 2025 Paper 13',
  estimatedCount: 'Unknown',
  subject: 'Physics',
  level: 'IGCSE',
  session: 'Mar',
  paper_number: '13',
  lastUpdated: null,
  exam_board: 'Cambridge IGCSE',
  difficulty_level: 'Standard',
  tags: [],
  questionFileName: 'physics_2025_Mar_13_question_bank.json'
};

// Simple question loader
const loadQuestionsSimple = async (bankId) => {
  console.log(`📚 Loading questions for: ${bankId}`);
  
  try {
    const url = '/question_banks/physics_2025_mar_13/physics_2025_Mar_13_question_bank.json';
    console.log('📂 Loading from:', url);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to load: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('✅ Raw data loaded');
    
    // Handle different data structures
    let questions = [];
    if (Array.isArray(data)) {
      questions = data;
    } else if (data.questions && Array.isArray(data.questions)) {
      questions = data.questions;
    } else if (typeof data === 'object') {
      questions = Object.values(data);
    }
    
    console.log(`✅ Found ${questions.length} questions`);
    
    // Process questions
    const processedQuestions = questions.map((q, index) => {
      if (!q || typeof q !== 'object') {
        return null;
      }
      
      return {
        id: q.id || q.question_id || `q_${index + 1}`,
        question_text: q.question_text || q.text || q.question || `Question ${index + 1}`,
        options: q.options || q.answers || {},
        correct_answer: q.correct_answer || q.answer || q.correct,
        topic: q.topic || q.category || 'Physics',
        difficulty: q.difficulty || 'medium',
        simple_answer: q.simple_answer || '',
        calculation_steps: q.calculation_steps || [],
        detailed_explanation: q.detailed_explanation || {},
        image_url: q.image_url ? `/question_banks/physics_2025_mar_13/images/${q.image_url}` : null,
        image_alt: q.image_alt || `Question ${q.id || index + 1} diagram`,
        confidence_score: q.confidence_score || 1.0,
        auto_flagged: q.auto_flagged || false
      };
    }).filter(q => q !== null);
    
    console.log(`✅ Processed ${processedQuestions.length} valid questions`);
    return processedQuestions;
    
  } catch (error) {
    console.error('❌ Load error:', error);
    throw error;
  }
};

function App() {
  // Main app state
  const [currentScreen, setCurrentScreen] = useState('start');
  const [questionBanks, setQuestionBanks] = useState([]);
  const [selectedBank, setSelectedBank] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Quiz state
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [quizStartTime, setQuizStartTime] = useState(null);
  const [quizEndTime, setQuizEndTime] = useState(null);

  // EMERGENCY: Set the hard-coded bank immediately
  useEffect(() => {
    console.log('🚀 App: Emergency setup - using hard-coded bank');
    setQuestionBanks([EMERGENCY_BANK]);
    setLoading(false);
  }, []);

  // Start quiz handler - matches what StartScreen expects
  const handleStartQuiz = async ({ bankId, questionCount }) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🚀 Starting quiz with bank:', bankId);
      
      // Find the selected bank
      const bank = questionBanks.find(b => b.id === bankId);
      if (!bank) {
        throw new Error('Selected bank not found');
      }
      
      // Load questions using simple loader
      const loadedQuestions = await loadQuestionsSimple(bankId);
      
      if (!loadedQuestions || loadedQuestions.length === 0) {
        throw new Error('No questions found in the selected question bank');
      }

      // Shuffle questions and take requested amount
      const shuffledQuestions = [...loadedQuestions]
        .sort(() => Math.random() - 0.5)
        .slice(0, Math.min(questionCount, loadedQuestions.length));

      setSelectedBank(bank);
      setQuestions(shuffledQuestions);
      setCurrentQuestionIndex(0);
      setAnswers({});
      setQuizStartTime(new Date());
      setQuizEndTime(null);
      setCurrentScreen('quiz');
      
      console.log('✅ Quiz started with', shuffledQuestions.length, 'questions');
    } catch (err) {
      console.error('❌ Failed to start quiz:', err);
      setError(`Failed to start quiz: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle answer selection
  const handleAnswerSelect = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  // Navigate to next question
  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      // Quiz finished
      setQuizEndTime(new Date());
      setCurrentScreen('result');
    }
  };

  // Navigate to previous question
  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  // Calculate results
  const calculateResults = () => {
    let correctCount = 0;
    let totalQuestions = questions.length;

    questions.forEach(question => {
      const userAnswer = answers[question.id];
      if (userAnswer === question.correct_answer) {
        correctCount++;
      }
    });

    const percentage = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;
    const timeTaken = quizEndTime && quizStartTime 
      ? Math.round((quizEndTime - quizStartTime) / 1000) 
      : 0;

    return {
      correctCount,
      totalQuestions,
      percentage,
      timeTaken,
      questions,
      answers
    };
  };

  // Navigation functions
  const goToStart = () => {
    setCurrentScreen('start');
    setSelectedBank(null);
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setQuizStartTime(null);
    setQuizEndTime(null);
    setError(null);
  };

  const goToReview = () => {
    setCurrentScreen('review');
  };

  // Error boundary for quiz errors
  if (error && currentScreen === 'quiz') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Quiz Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={goToStart}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Start
          </button>
        </div>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Render current screen
  switch (currentScreen) {
    case 'start':
      return (
        <div className="min-h-screen bg-gray-50">
          <StartScreen
            onStart={handleStartQuiz}
            selectedBank={selectedBank}
            setSelectedBank={setSelectedBank}
            availableBanks={questionBanks}
            loading={loading}
            error={error}
          />
        </div>
      );

    case 'quiz':
      if (questions.length === 0) {
        return (
          <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading questions...</p>
            </div>
          </div>
        );
      }

      const currentQuestion = questions[currentQuestionIndex];
      const currentQuestionId = currentQuestion?.id;
      
      return (
        <div className="min-h-screen bg-gray-50 py-8">
          <QuestionCard
            questionObj={currentQuestion}
            currentIndex={currentQuestionIndex}
            total={questions.length}
            selectedAnswer={answers[currentQuestionId]}
            onSelect={handleAnswerSelect}
            onAnswer={handleNextQuestion}
            onBack={handlePreviousQuestion}
            selectedBank={selectedBank}
            goHome={goToStart}
          />
        </div>
      );

    case 'result':
      return (
        <ResultScreen
          results={calculateResults()}
          onRestart={goToStart}
          onReview={goToReview}
        />
      );

    case 'review':
      return (
        <ReviewScreen
          results={calculateResults()}
          onBackToStart={goToStart}
          onBackToResults={() => setCurrentScreen('result')}
        />
      );

    default:
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Unknown Screen</h2>
            <button
              onClick={goToStart}
              className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Start
            </button>
          </div>
        </div>
      );
  }
}

export default App;