import React, { useState, useEffect } from 'react';
import StartScreen from './screens/StartScreen';
import QuestionCard from './components/QuestionCard';
import ResultScreen from './screens/ResultScreen';
import ReviewScreen from './screens/ReviewScreen';
import { loadQuestionBank } from './services/questionService';

function App() {
  // 🌙 DARK MODE STATE
  const [darkMode, setDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('axcelscore-dark-mode');
    if (savedMode !== null) {
      return JSON.parse(savedMode);
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Main app state
  const [currentScreen, setCurrentScreen] = useState('start');
  const [selectedBank, setSelectedBank] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Quiz state
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [quizStartTime, setQuizStartTime] = useState(null);
  const [quizEndTime, setQuizEndTime] = useState(null);

  // 🎯 RETEST state
  const [isRetestMode, setIsRetestMode] = useState(false);
  const [originalQuestions, setOriginalQuestions] = useState([]);
  const [originalAnswers, setOriginalAnswers] = useState({});

  // ⏰ NEW: TIMER STATE
  const [totalTimeLeft, setTotalTimeLeft] = useState(0); // Total quiz time remaining (seconds)
  const [questionTimeLeft, setQuestionTimeLeft] = useState(60); // Current question time remaining
  const [questionStartTime, setQuestionStartTime] = useState(null); // When current question started
  const [timerActive, setTimerActive] = useState(false); // Is timer running
  const [timeWarning, setTimeWarning] = useState(false); // Show warning when time low

  // ⏰ TIMER CONSTANTS
  const QUESTION_TIME_LIMIT = 60; // 1 minute per question
  const getMaxQuizTime = (questionCount) => {
    // IGCSE timing: 1 minute per question, max 45 minutes for 40 questions
    return Math.min(questionCount * 60, 45 * 60);
  };

  // 🌙 DARK MODE EFFECTS
  useEffect(() => {
    localStorage.setItem('axcelscore-dark-mode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // ⏰ MAIN TIMER EFFECT - Handles both total quiz time and current question time
  useEffect(() => {
    let interval = null;

    if (timerActive && currentScreen === 'quiz') {
      interval = setInterval(() => {
        const now = new Date();
        
        // Update total quiz time
        if (quizStartTime) {
          const totalElapsed = Math.floor((now - quizStartTime) / 1000);
          const maxTime = getMaxQuizTime(questions.length);
          const timeLeft = Math.max(0, maxTime - totalElapsed);
          setTotalTimeLeft(timeLeft);
          
          // Auto-finish quiz if total time expires
          if (timeLeft === 0) {
            handleTimeUp();
            return;
          }
          
          // Set warning when less than 5 minutes left
          setTimeWarning(timeLeft <= 300);
        }
        
        // Update current question time
        if (questionStartTime) {
          const questionElapsed = Math.floor((now - questionStartTime) / 1000);
          const questionTimeRemaining = Math.max(0, QUESTION_TIME_LIMIT - questionElapsed);
          setQuestionTimeLeft(questionTimeRemaining);
          
          // Auto-advance to next question if time expires
          if (questionTimeRemaining === 0) {
            handleQuestionTimeUp();
          }
        }
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [timerActive, currentScreen, quizStartTime, questionStartTime, questions.length]);

  // ⏰ Handle when current question time expires
  const handleQuestionTimeUp = () => {
    console.log('⏰ Question time expired, moving to next question');
    // Don't record an answer if user didn't select one
    handleNextQuestion();
  };

  // ⏰ Handle when total quiz time expires
  const handleTimeUp = () => {
    console.log('⏰ Quiz time expired, finishing quiz');
    setTimerActive(false);
    setQuizEndTime(new Date());
    setCurrentScreen('result');
  };

  // ⏰ Start question timer
  const startQuestionTimer = () => {
    setQuestionStartTime(new Date());
    setQuestionTimeLeft(QUESTION_TIME_LIMIT);
  };

  // 🌙 DARK MODE TOGGLE
  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  // Start quiz handler - ENHANCED with timer
  const handleStartQuiz = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🚀 Starting quiz with bank:', selectedBank?.id);
      
      if (!selectedBank) {
        throw new Error('No question bank selected');
      }
      
      // Load questions using the dynamic service
      const data = await loadQuestionBank(selectedBank.id);
      
      if (!data.questions || data.questions.length === 0) {
        throw new Error('No questions found in the selected question bank');
      }

      // Shuffle questions
      const shuffledQuestions = [...data.questions]
        .sort(() => Math.random() - 0.5);

      setQuestions(shuffledQuestions);
      setCurrentQuestionIndex(0);
      setAnswers({});
      
      // ⏰ Initialize timers
      const now = new Date();
      setQuizStartTime(now);
      setQuizEndTime(null);
      setTotalTimeLeft(getMaxQuizTime(shuffledQuestions.length));
      setTimerActive(true);
      startQuestionTimer();
      
      setIsRetestMode(false);
      setCurrentScreen('quiz');
      
      console.log(`✅ Quiz started with ${shuffledQuestions.length} questions, ${getMaxQuizTime(shuffledQuestions.length)/60} minutes total`);
    } catch (err) {
      console.error('❌ Failed to start quiz:', err);
      setError(`Failed to start quiz: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 🎯 Start retest with incorrect questions only - ENHANCED with timer
  const handleRetestIncorrect = () => {
    try {
      console.log('🔄 Starting retest with incorrect questions...');
      
      // Calculate which questions were incorrect
      const incorrectQuestions = questions.filter(question => {
        const userAnswer = answers[question.id];
        return userAnswer !== question.correct_answer;
      });

      if (incorrectQuestions.length === 0) {
        alert('No incorrect questions to practice!');
        return;
      }

      console.log(`🎯 Found ${incorrectQuestions.length} incorrect questions for retest`);

      // Store original data for reference
      setOriginalQuestions(questions);
      setOriginalAnswers(answers);

      // Set up retest
      const shuffledIncorrectQuestions = [...incorrectQuestions]
        .sort(() => Math.random() - 0.5);

      setQuestions(shuffledIncorrectQuestions);
      setCurrentQuestionIndex(0);
      setAnswers({});
      
      // ⏰ Initialize retest timers
      const now = new Date();
      setQuizStartTime(now);
      setQuizEndTime(null);
      setTotalTimeLeft(getMaxQuizTime(shuffledIncorrectQuestions.length));
      setTimerActive(true);
      startQuestionTimer();
      
      setIsRetestMode(true);
      setCurrentScreen('quiz');
      
      console.log(`✅ Retest started with ${shuffledIncorrectQuestions.length} questions`);
    } catch (err) {
      console.error('❌ Failed to start retest:', err);
      alert('Failed to start retest. Please try again.');
    }
  };

  // Handle bank selection
  const handleBankSelect = (bank) => {
    console.log('🎯 Bank selected:', bank?.name);
    setSelectedBank(bank);
  };

  // Handle answer selection
  const handleAnswerSelect = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  // Navigate to next question - ENHANCED with timer
  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      startQuestionTimer(); // ⏰ Start timer for next question
    } else {
      // Quiz finished
      setTimerActive(false);
      setQuizEndTime(new Date());
      setCurrentScreen('result');
    }
  };

  // Navigate to previous question - ENHANCED with timer
  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      startQuestionTimer(); // ⏰ Reset timer for previous question
    }
  };

  // Calculate results - UNCHANGED
  const calculateResults = () => {
    let correctCount = 0;
    let totalQuestions = questions.length;

    // Create answers array in format expected by ResultScreen
    const answersArray = questions.map(question => {
      const userAnswer = answers[question.id];
      const isCorrect = userAnswer === question.correct_answer;
      
      if (isCorrect) {
        correctCount++;
      }
      
      return {
        questionId: question.id,
        userAnswer: userAnswer,
        correctAnswer: question.correct_answer,
        correct: isCorrect,
        topic: question.topic || 'General',
        question: question
      };
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
      answers: answersArray,
      isRetestMode,
      originalQuestions: isRetestMode ? originalQuestions : null,
      originalAnswers: isRetestMode ? originalAnswers : null
    };
  };

  // Navigation functions - ENHANCED to reset timers
  const goToStart = () => {
    // ⏰ Stop all timers
    setTimerActive(false);
    setTotalTimeLeft(0);
    setQuestionTimeLeft(60);
    setQuestionStartTime(null);
    setTimeWarning(false);
    
    setCurrentScreen('start');
    setSelectedBank(null);
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setQuizStartTime(null);
    setQuizEndTime(null);
    setError(null);
    setIsRetestMode(false);
    setOriginalQuestions([]);
    setOriginalAnswers({});
  };

  const goToReview = () => {
    setTimerActive(false); // ⏰ Stop timer during review
    setCurrentScreen('review');
  };

  // ⏰ Format time for display (MM:SS)
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // 🌙 DARK MODE WRAPPER CLASSES
  const getAppClasses = (screenSpecific = '') => {
    const baseClasses = `min-h-screen transition-colors duration-300 ${screenSpecific}`;
    if (darkMode) {
      return `${baseClasses} dark bg-gray-900 text-white`;
    }
    return baseClasses;
  };

  // Error boundary for quiz errors
  if (error && currentScreen !== 'start') {
    return (
      <div className={getAppClasses('flex items-center justify-center p-4')}>
        <div className="fixed top-4 right-4 z-50">
          <button
            onClick={toggleDarkMode}
            className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl ${
              darkMode 
                ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
                : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
            }`}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>

        <div className={`max-w-md w-full rounded-lg shadow-lg p-6 text-center ${
          darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'
        }`}>
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className={`text-xl font-semibold mb-2 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            Quiz Error
          </h2>
          <p className={`mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            {error}
          </p>
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
  if (loading && currentScreen !== 'start') {
    return (
      <div className={getAppClasses('flex items-center justify-center')}>
        <div className="fixed top-4 right-4 z-50">
          <button
            onClick={toggleDarkMode}
            className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl ${
              darkMode 
                ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
                : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
            }`}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>

        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>Loading...</p>
        </div>
      </div>
    );
  }

  // Render current screen
  switch (currentScreen) {
    case 'start':
      return (
        <>
          <div className="fixed top-4 right-4 z-50">
            <button
              onClick={toggleDarkMode}
              className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl ${
                darkMode 
                  ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>

          <StartScreen
            onStart={handleStartQuiz}
            selectedBank={selectedBank}
            onBankSelect={handleBankSelect}
            darkMode={darkMode}
          />
        </>
      );

    case 'quiz':
      if (questions.length === 0) {
        return (
          <div className={getAppClasses('flex items-center justify-center')}>
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>Loading questions...</p>
            </div>
          </div>
        );
      }

      const currentQuestion = questions[currentQuestionIndex];
      const currentQuestionId = currentQuestion?.id;
      
      return (
        <>
          {/* ⏰ Mobile-Friendly Timer Layout */}
          <div className="fixed top-0 left-0 right-0 z-40 p-4">
            <div className="flex justify-between items-start">
              {/* Left: Total Time */}
              <div className={`px-3 py-2 rounded-lg shadow-lg transition-all duration-300 flex-shrink-0 ${
                timeWarning 
                  ? (darkMode ? 'bg-red-800 text-red-200 animate-pulse' : 'bg-red-100 text-red-700 animate-pulse')
                  : (darkMode ? 'bg-gray-800 text-gray-200 border border-gray-600' : 'bg-white text-gray-700 border border-gray-200')
              }`}>
                <div className="text-xs font-medium">Total Time</div>
                <div className="text-lg font-bold">{formatTime(totalTimeLeft)}</div>
              </div>

              {/* Right: Question Time */}
              <div className={`px-3 py-2 rounded-lg shadow-lg transition-all duration-300 flex-shrink-0 ${
                questionTimeLeft <= 10 
                  ? (darkMode ? 'bg-orange-800 text-orange-200 animate-pulse' : 'bg-orange-100 text-orange-700 animate-pulse')
                  : (darkMode ? 'bg-gray-800 text-gray-200 border border-gray-600' : 'bg-white text-gray-700 border border-gray-200')
              }`}>
                <div className="text-xs font-medium text-center">Question Time</div>
                <div className="text-lg font-bold text-center">{formatTime(questionTimeLeft)}</div>
              </div>
            </div>
          </div>

          {/* Main content with proper top padding for mobile */}
          <div className={getAppClasses('py-8')} style={{ paddingTop: '6rem' }}>
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
              darkMode={darkMode}
              isRetestMode={isRetestMode}
              // ⏰ Timer props
              totalTimeLeft={totalTimeLeft}
              questionTimeLeft={questionTimeLeft}
              timeWarning={timeWarning}
              // 🌙 Dark mode toggle component to be rendered beside Home/End
              darkModeToggle={
                <button
                  onClick={toggleDarkMode}
                  className={`p-2 sm:p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl flex-shrink-0 ml-2 ${
                    darkMode 
                      ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
                      : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                  }`}
                  title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                >
                  {darkMode ? '☀️' : '🌙'}
                </button>
              }
            />
          </div>
        </>
      );

    case 'result':
      const results = calculateResults();
      return (
        <>
          <div className="fixed top-4 right-4 z-50">
            <button
              onClick={toggleDarkMode}
              className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl ${
                darkMode 
                  ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>

          <ResultScreen
            questions={results.questions}
            answers={results.answers}
            onRetestIncorrect={handleRetestIncorrect}
            onReview={goToReview}
            goHome={goToStart}
            selectedBank={selectedBank}
            startTimestamp={quizStartTime?.getTime()}
            darkMode={darkMode}
            isRetestMode={isRetestMode}
          />
        </>
      );

    case 'review':
      const reviewResults = calculateResults();
      return (
        <>
          <div className="fixed top-4 right-4 z-50">
            <button
              onClick={toggleDarkMode}
              className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl ${
                darkMode 
                  ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>

          <ReviewScreen
            questions={reviewResults.questions}
            answers={reviewResults.answers}
            onBackToStart={goToStart}
            onBackToResults={() => setCurrentScreen('result')}
            selectedBank={selectedBank}
            darkMode={darkMode}
          />
        </>
      );

    default:
      return (
        <div className={getAppClasses('flex items-center justify-center')}>
          <div className="text-center">
            <h2 className={`text-xl font-semibold mb-2 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              Unknown Screen
            </h2>
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