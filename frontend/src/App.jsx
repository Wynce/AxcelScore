import React, { useState, useEffect } from 'react';
import StartScreen from './screens/StartScreen';
import QuestionCard from './components/QuestionCard';
import ResultScreen from './screens/ResultScreen';
import ReviewScreen from './screens/ReviewScreen';
import { loadQuestionBank } from './services/questionService';

function App() {
  // UI THEME STATE
  const [uiTheme, setUiTheme] = useState(() => {
    try {
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } catch (error) {
      return 'light';
    }
  });

  // Main app state
  const [currentScreen, setCurrentScreen] = useState('start');
  const [selectedBanks, setSelectedBanks] = useState([]);
  const [questionCount, setQuestionCount] = useState(40);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Quiz state
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [quizStartTime, setQuizStartTime] = useState(null);
  const [quizEndTime, setQuizEndTime] = useState(null);

  // RETEST state
  const [isRetestMode, setIsRetestMode] = useState(false);
  const [originalQuestions, setOriginalQuestions] = useState([]);
  const [originalAnswers, setOriginalAnswers] = useState({});

  // TIMER STATE
  const [totalTimeLeft, setTotalTimeLeft] = useState(0);
  const [questionTimeLeft, setQuestionTimeLeft] = useState(60);
  const [questionStartTime, setQuestionStartTime] = useState(null);
  const [timerActive, setTimerActive] = useState(false);
  const [timeWarning, setTimeWarning] = useState(false);

  // TIMER CONSTANTS
  const QUESTION_TIME_LIMIT = 60;
  const getMaxQuizTime = (questionCount) => {
    return Math.min(questionCount * 60, 45 * 60);
  };

  // Theme Toggle Functions
  const toggleDarkMode = () => {
    setUiTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const toggleGenAlpha = () => {
    setUiTheme(prev => prev === 'genalpha' ? 'light' : 'genalpha');
  };

  // Theme Toggle Components
  const DarkModeToggle = ({ className = "" }) => (
    <button
      onClick={toggleDarkMode}
      className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl ${
        uiTheme === 'dark'
          ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
          : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
      } ${className}`}
      title={uiTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      {uiTheme === 'dark' ? '☀️' : '🌙'}
    </button>
  );

  const GenAlphaToggle = ({ className = "" }) => (
    <button
      onClick={toggleGenAlpha}
      className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl font-bold text-lg ${
        uiTheme === 'genalpha'
          ? 'genalpha-button text-white hover:scale-110 border-2 border-white/30' 
          : 'bg-white text-purple-600 hover:bg-purple-50 border border-purple-200'
      } ${className}`}
      title={uiTheme === 'genalpha' ? 'Switch to Light Mode' : 'Switch to Gen Alpha Mode'}
    >
      α
    </button>
  );

  // UI THEME EFFECTS
  useEffect(() => {
    const root = document.documentElement;
    
    // Remove all theme classes
    root.classList.remove('light', 'dark', 'genalpha');
    
    // Add current theme class
    root.classList.add(uiTheme);
    
    // Set CSS custom properties based on theme
    switch(uiTheme) {
      case 'dark':
        root.style.setProperty('--bg-primary', '#0f172a');
        root.style.setProperty('--bg-secondary', '#1e293b');
        root.style.setProperty('--text-primary', '#f8fafc');
        root.style.setProperty('--text-secondary', '#cbd5e1');
        root.style.setProperty('--accent-primary', '#3b82f6');
        break;
      case 'genalpha':
        root.style.setProperty('--bg-primary', 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%)');
        root.style.setProperty('--bg-secondary', 'rgba(255, 255, 255, 0.15)');
        root.style.setProperty('--text-primary', '#ffffff');
        root.style.setProperty('--text-secondary', 'rgba(255, 255, 255, 0.9)');
        root.style.setProperty('--accent-primary', '#ff6b6b');
        break;
      default: // light
        root.style.setProperty('--bg-primary', '#ffffff');
        root.style.setProperty('--bg-secondary', '#f8fafc');
        root.style.setProperty('--text-primary', '#1e293b');
        root.style.setProperty('--text-secondary', '#64748b');
        root.style.setProperty('--accent-primary', '#3b82f6');
    }
  }, [uiTheme]);

  // MAIN TIMER EFFECT
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

  // Handle when current question time expires
  const handleQuestionTimeUp = () => {
    console.log('⏰ Question time expired, moving to next question');
    handleNextQuestion();
  };

  // Handle when total quiz time expires
  const handleTimeUp = () => {
    console.log('⏰ Quiz time expired, finishing quiz');
    setTimerActive(false);
    setQuizEndTime(new Date());
    setCurrentScreen('result');
  };

  // Start question timer
  const startQuestionTimer = () => {
    setQuestionStartTime(new Date());
    setQuestionTimeLeft(QUESTION_TIME_LIMIT);
  };

  // LOAD AND COMBINE QUESTIONS FROM MULTIPLE BANKS
  const loadQuestionsFromBanks = async (banks, requestedCount) => {
    try {
      console.log(`🚀 Loading questions from ${banks.length} banks, requesting ${requestedCount} total questions`);
      
      let allQuestions = [];
      
      // Load questions from each selected bank
      for (const bank of banks) {
        try {
          const data = await loadQuestionBank(bank.id);
          if (data.questions && data.questions.length > 0) {
            // Add bank info to each question for tracking
            const questionsWithBank = data.questions.map(q => ({
              ...q,
              bankName: bank.name,
              bankId: bank.id
            }));
            allQuestions = [...allQuestions, ...questionsWithBank];
            console.log(`✅ Loaded ${data.questions.length} questions from ${bank.name}`);
          } else {
            console.warn(`⚠️ No questions found in bank: ${bank.name}`);
          }
        } catch (bankError) {
          console.error(`❌ Failed to load bank ${bank.name}:`, bankError);
        }
      }

      if (allQuestions.length === 0) {
        throw new Error('No questions could be loaded from the selected question banks');
      }

      // Shuffle all questions
      const shuffledQuestions = [...allQuestions].sort(() => Math.random() - 0.5);
      
      // Select the requested number of questions
      const selectedQuestions = shuffledQuestions.slice(0, requestedCount);
      
      console.log(`✅ Successfully loaded ${selectedQuestions.length} questions from ${banks.length} banks`);
      
      return selectedQuestions;
    } catch (error) {
      console.error('❌ Failed to load questions from banks:', error);
      throw error;
    }
  };

  // START QUIZ HANDLER
  const handleStartQuiz = async (requestedQuestionCount, selectedQuestionBanks) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🚀 Starting quiz with:', {
        questionCount: requestedQuestionCount,
        banks: selectedQuestionBanks?.map(b => b.name)
      });
      
      if (!selectedQuestionBanks || selectedQuestionBanks.length === 0) {
        throw new Error('No question banks selected');
      }

      // Store the selection for future reference
      setSelectedBanks(selectedQuestionBanks);
      setQuestionCount(requestedQuestionCount);
      
      // Load questions from selected banks
      const selectedQuestions = await loadQuestionsFromBanks(selectedQuestionBanks, requestedQuestionCount);

      setQuestions(selectedQuestions);
      setCurrentQuestionIndex(0);
      setAnswers({});
      
      // Initialize timers
      const now = new Date();
      setQuizStartTime(now);
      setQuizEndTime(null);
      setTotalTimeLeft(getMaxQuizTime(selectedQuestions.length));
      setTimerActive(true);
      startQuestionTimer();
      
      setIsRetestMode(false);
      setCurrentScreen('quiz');
      
      console.log(`✅ Quiz started with ${selectedQuestions.length} questions, ${getMaxQuizTime(selectedQuestions.length)/60} minutes total`);
    } catch (err) {
      console.error('❌ Failed to start quiz:', err);
      setError(`Failed to start quiz: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Start retest with incorrect questions only
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
      
      // Initialize retest timers
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
      startQuestionTimer();
    } else {
      // Quiz finished
      setTimerActive(false);
      setQuizEndTime(new Date());
      setCurrentScreen('result');
    }
  };

  // Navigate to previous question
  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      startQuestionTimer();
    }
  };

  // Calculate results
  const calculateResults = () => {
    let correctCount = 0;
    let totalQuestions = questions.length;

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

  // Navigation functions
  const goToStart = () => {
    // Stop all timers
    setTimerActive(false);
    setTotalTimeLeft(0);
    setQuestionTimeLeft(60);
    setQuestionStartTime(null);
    setTimeWarning(false);
    
    setCurrentScreen('start');
    setSelectedBanks([]);
    setQuestionCount(40);
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
    setTimerActive(false);
    setCurrentScreen('review');
  };

  // Format time for display (MM:SS)
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // GET THEME CLASSES - FIXED FOR CONSISTENT GEN ALPHA ANIMATION
  const getAppClasses = (screenSpecific = '') => {
    const baseClasses = `min-h-screen transition-all duration-500 ${screenSpecific}`;
    
    switch(uiTheme) {
      case 'dark':
        return `${baseClasses} dark bg-gray-900 text-white`;
      case 'genalpha':
        // FIXED: Always include genalpha-animated for consistent animation across all screens
        return `${baseClasses} genalpha genalpha-animated text-white`;
      default: // light
        return `${baseClasses} light bg-gray-50 text-gray-900`;
    }
  };

  // Helper functions for theme-specific classes
  const getErrorCardClasses = () => {
    switch(uiTheme) {
      case 'dark': return 'bg-gray-800 border border-gray-700';
      case 'genalpha': return 'genalpha-card backdrop-blur-xl border border-white/20';
      default: return 'bg-white';
    }
  };

  const getTextClasses = (type) => {
    if (type === 'primary') {
      switch(uiTheme) {
        case 'dark': return 'text-white';
        case 'genalpha': return 'text-white';
        default: return 'text-gray-800';
      }
    } else { // secondary
      switch(uiTheme) {
        case 'dark': return 'text-gray-300';
        case 'genalpha': return 'text-white/90';
        default: return 'text-gray-600';
      }
    }
  };

  const getSpinnerClasses = () => {
    switch(uiTheme) {
      case 'dark': return 'border-white';
      case 'genalpha': return 'border-white';
      default: return 'border-blue-600';
    }
  };

  const getTimerClasses = (type, warning) => {
    const baseClasses = warning ? 'animate-pulse' : '';
    
    switch(uiTheme) {
      case 'dark':
        if (warning) {
          return `${baseClasses} ${type === 'total' ? 'bg-red-800 text-red-200' : 'bg-orange-800 text-orange-200'} border border-gray-600`;
        }
        return `${baseClasses} bg-gray-800 text-gray-200 border border-gray-600`;
      
      case 'genalpha':
        if (warning) {
          return `${baseClasses} ${type === 'total' ? 'genalpha-warning-total' : 'genalpha-warning-question'} backdrop-blur-xl border border-white/30`;
        }
        return `${baseClasses} genalpha-timer backdrop-blur-xl border border-white/30`;
      
      default: // light
        if (warning) {
          return `${baseClasses} ${type === 'total' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'} border border-gray-200`;
        }
        return `${baseClasses} bg-white text-gray-700 border border-gray-200`;
    }
  };

  // Error boundary for quiz errors
  if (error && currentScreen !== 'start') {
    return (
      <div className={getAppClasses('flex items-center justify-center p-4')}>
        <div className="fixed top-4 right-4 z-50 flex gap-2">
          <DarkModeToggle />
          <GenAlphaToggle />
        </div>

        <div className={`max-w-md w-full rounded-lg shadow-lg p-6 text-center ${getErrorCardClasses()}`}>
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className={`text-xl font-semibold mb-2 ${getTextClasses('primary')}`}>
            Quiz Error
          </h2>
          <p className={`mb-4 ${getTextClasses('secondary')}`}>
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
        <div className="fixed top-4 right-4 z-50 flex gap-2">
          <DarkModeToggle />
          <GenAlphaToggle />
        </div>

        <div className="text-center">
          <div className={`animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4 ${getSpinnerClasses()}`}></div>
          <p className={getTextClasses('secondary')}>Loading...</p>
        </div>
      </div>
    );
  }

  // Render current screen
  switch (currentScreen) {
    case 'start':
      return (
        <div className={getAppClasses()}>
          <div className="fixed top-4 right-4 z-50 flex gap-2">
            <DarkModeToggle />
            <GenAlphaToggle />
          </div>

          <StartScreen
            onStart={handleStartQuiz}
            uiTheme={uiTheme}
          />
        </div>
      );

    case 'quiz':
      if (questions.length === 0) {
        return (
          <div className={getAppClasses('flex items-center justify-center')}>
            <div className="text-center">
              <div className={`animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4 ${getSpinnerClasses()}`}></div>
              <p className={getTextClasses('secondary')}>Loading questions...</p>
            </div>
          </div>
        );
      }

      const currentQuestion = questions[currentQuestionIndex];
      const currentQuestionId = currentQuestion?.id;
      
      return (
        <div className={getAppClasses()}>
          {/* Mobile-Friendly Timer Layout */}
          <div className="fixed top-0 left-0 right-0 z-40 p-4">
            <div className="flex justify-between items-start">
              {/* Left: Total Time */}
              <div className={`px-3 py-2 rounded-lg shadow-lg transition-all duration-300 flex-shrink-0 ${getTimerClasses('total', timeWarning)}`}>
                <div className="text-xs font-medium">Total Time</div>
                <div className="text-lg font-bold">{formatTime(totalTimeLeft)}</div>
              </div>

              {/* Right: Question Time */}
              <div className={`px-3 py-2 rounded-lg shadow-lg transition-all duration-300 flex-shrink-0 ${getTimerClasses('question', questionTimeLeft <= 10)}`}>
                <div className="text-xs font-medium text-center">Question Time</div>
                <div className="text-lg font-bold text-center">{formatTime(questionTimeLeft)}</div>
              </div>
            </div>
          </div>

          {/* Main content with proper top padding for mobile */}
          <div className="py-8" style={{ 
            paddingTop: '6rem'
          }}>
            <QuestionCard
              questionObj={currentQuestion}
              currentIndex={currentQuestionIndex}
              total={questions.length}
              selectedAnswer={answers[currentQuestionId]}
              onSelect={handleAnswerSelect}
              onAnswer={handleNextQuestion}
              onBack={handlePreviousQuestion}
              selectedBank={currentQuestion?.bankId ? { name: currentQuestion.bankName, id: currentQuestion.bankId } : (selectedBanks.length === 1 ? selectedBanks[0] : { name: `${selectedBanks.length} Banks`, id: 'multi' })}
              goHome={goToStart}
              uiTheme={uiTheme}
              isRetestMode={isRetestMode}
              // Timer props
              totalTimeLeft={totalTimeLeft}
              questionTimeLeft={questionTimeLeft}
              timeWarning={timeWarning}
              // Toggle functions
              onToggleDarkMode={toggleDarkMode}
              onToggleGenAlpha={toggleGenAlpha}
            />
          </div>
        </div>
      );

    case 'result':
      const results = calculateResults();
      return (
        <div className={getAppClasses()}>
          <div className="fixed top-4 right-4 z-50 flex gap-2">
            <DarkModeToggle />
            <GenAlphaToggle />
          </div>

          <ResultScreen
            questions={results.questions}
            answers={results.answers}
            onRetestIncorrect={handleRetestIncorrect}
            onReview={goToReview}
            goHome={goToStart}
            selectedBank={selectedBanks.length === 1 ? selectedBanks[0] : { name: `${selectedBanks.length} Banks`, id: 'multi' }}
            startTimestamp={quizStartTime?.getTime()}
            uiTheme={uiTheme}
            isRetestMode={isRetestMode}
          />
        </div>
      );

    case 'review':
      const reviewResults = calculateResults();
      return (
        <div className={getAppClasses()}>
          <div className="fixed top-4 right-4 z-50 flex gap-2">
            <DarkModeToggle />
            <GenAlphaToggle />
          </div>

          <ReviewScreen
            questions={reviewResults.questions}
            answers={reviewResults.answers}
            onBackToStart={goToStart}
            onBackToResults={() => setCurrentScreen('result')}
            selectedBank={selectedBanks.length === 1 ? selectedBanks[0] : { name: `${selectedBanks.length} Banks`, id: 'multi' }}
            uiTheme={uiTheme}
          />
        </div>
      );

    default:
      return (
        <div className={getAppClasses('flex items-center justify-center')}>
          <div className="text-center">
            <h2 className={`text-xl font-semibold mb-2 ${getTextClasses('primary')}`}>
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