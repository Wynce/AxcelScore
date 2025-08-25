// ==============================
// 🏆 screens/ResultScreen.js - Quiz Results & Actions + Dark Mode
// ==============================
import React, { useState, useEffect } from 'react';
import { Trophy, RotateCcw, BookOpen, Clock, Target, TrendingUp } from 'lucide-react';
import { colors } from '../styles/theme';
import axcelLogo from '../assets/axcel-logo.png';

const ResultScreen = ({
  questions,
  answers,
  onRetestIncorrect,
  onReview,
  goHome,
  selectedBank,
  startTimestamp,
  darkMode = false // 🌙 NEW: Dark mode prop
}) => {
  const [showAnimation, setShowAnimation] = useState(false);
  const [categoryBreakdown, setCategoryBreakdown] = useState({});

  // Calculate results - UNCHANGED
  const correctCount = answers.filter(a => a.correct).length;
  const totalQuestions = questions.length;
  const percentage = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;
  const incorrectCount = totalQuestions - correctCount;
  
  // Calculate time taken - UNCHANGED
  const timeTaken = startTimestamp ? Math.floor((Date.now() - startTimestamp) / 1000) : 0;
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Trigger animation on mount - UNCHANGED
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowAnimation(true);
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  // Calculate topic/category breakdown - UNCHANGED
  useEffect(() => {
    const breakdown = {};
    
    answers.forEach(answer => {
      const topic = answer.topic || 'General';
      if (!breakdown[topic]) {
        breakdown[topic] = { correct: 0, total: 0 };
      }
      breakdown[topic].total++;
      if (answer.correct) {
        breakdown[topic].correct++;
      }
    });

    setCategoryBreakdown(breakdown);
  }, [answers]);

  // Get performance message - UNCHANGED
  const getPerformanceMessage = () => {
    if (percentage >= 90) return {
      message: "Outstanding! You've mastered these concepts! 🌟",
      color: darkMode ? "text-green-400" : "text-[#4CAF50]",
      emoji: "🎉"
    };
    if (percentage >= 80) return {
      message: "Excellent work! You're doing great! 🎯",
      color: darkMode ? "text-green-400" : "text-[#4CAF50]",
      emoji: "🏆"
    };
    if (percentage >= 70) return {
      message: "Good job! You're on the right track! 👏",
      color: darkMode ? "text-orange-400" : "text-[#FF6701]",
      emoji: "💪"
    };
    if (percentage >= 60) return {
      message: "Nice effort! Keep practicing to improve! 📚",
      color: darkMode ? "text-orange-400" : "text-[#FF6701]",
      emoji: "🔥"
    };
    if (percentage >= 50) return {
      message: "You're getting there! Review and try again! 🚀",
      color: darkMode ? "text-red-400" : "text-[#F44336]",
      emoji: "💡"
    };
    return {
      message: "Keep going! Practice makes perfect! 🌱",
      color: darkMode ? "text-red-400" : "text-[#F44336]",
      emoji: "🌟"
    };
  };

  const performance = getPerformanceMessage();

  // Get score color - ENHANCED for dark mode
  const getScoreColor = () => {
    if (darkMode) {
      if (percentage >= 80) return "text-green-400";
      if (percentage >= 60) return "text-orange-400";
      return "text-red-400";
    } else {
      if (percentage >= 80) return "text-[#4CAF50]";
      if (percentage >= 60) return "text-[#FF6701]";
      return "text-[#F44336]";
    }
  };

  // Retry with new questions - UNCHANGED
  const handleRetryNewQuestions = () => {
    goHome(); // This will allow selecting new questions
  };

  // 🌙 DARK MODE STYLING HELPERS
  const getBackgroundClass = () => {
    return darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900';
  };

  const getCardClass = (customBg = null) => {
    if (customBg) return customBg; // For special cards like score card
    
    const baseClass = 'rounded-xl p-6 border transition-colors duration-300';
    if (darkMode) {
      return `${baseClass} bg-gray-800 border-gray-700`;
    }
    return `${baseClass} bg-white border-[#e5e6ea]`;
  };

  const getScoreCardClass = () => {
    const baseClass = 'rounded-xl p-8 mb-8 border transition-colors duration-300';
    if (darkMode) {
      return `${baseClass} bg-gray-800 border-gray-600`;
    }
    return `${baseClass} bg-[#e9f0f6] border-[#e5e6ea]`;
  };

  const getTextClass = (type = 'body') => {
    if (darkMode) {
      switch (type) {
        case 'heading': return 'text-white';
        case 'subheading': return 'text-gray-200';
        case 'body': return 'text-gray-300';
        case 'muted': return 'text-gray-400';
        default: return 'text-gray-300';
      }
    } else {
      switch (type) {
        case 'heading': return 'text-[#000000]';
        case 'subheading': return 'text-[#000000]';
        case 'body': return 'text-[#58585A]';
        case 'muted': return 'text-[#58585A]';
        default: return 'text-[#58585A]';
      }
    }
  };

  const getStatCardClass = () => {
    const baseClass = 'text-center p-4 rounded-lg border transition-colors duration-300';
    if (darkMode) {
      return `${baseClass} bg-gray-700 border-gray-600`;
    }
    return `${baseClass} bg-white border-[#e5e6ea]`;
  };

  const getTopicCardClass = () => {
    const baseClass = 'flex items-center justify-between p-3 rounded-lg transition-colors duration-300';
    if (darkMode) {
      return `${baseClass} bg-gray-700`;
    }
    return `${baseClass} bg-[#e9f0f6]`;
  };

  const getEncouragementCardClass = () => {
    const baseClass = 'mt-8 p-6 rounded-xl text-center transition-colors duration-300';
    if (darkMode) {
      return `${baseClass} bg-yellow-900 border border-yellow-700`;
    }
    return `${baseClass} bg-[#f2e08a]`;
  };

  return (
    <div className={`min-h-screen p-6 transition-colors duration-300 ${getBackgroundClass()}`}>
      <div className="max-w-4xl mx-auto">
        {/* Header with Logo */}
        <div className="text-center mb-8">
          {/* 🎯 Logo integrated in header */}
          <div className="flex items-center justify-center mb-4">
            <img 
              src={axcelLogo} 
              alt="Axcel Logo" 
              className={`h-8 w-auto mr-3 transition-opacity duration-300 ${
                darkMode ? 'opacity-90' : 'opacity-80'
              }`}
            />
            <h1 className={`text-3xl font-bold ${getTextClass('heading')}`}>
              Quiz Complete! {performance.emoji}
            </h1>
          </div>
          
          <div className="mb-6">
            <div className={`
              w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4 transition-all duration-1000
              ${showAnimation ? 'scale-100 opacity-100' : 'scale-50 opacity-0'}
              ${percentage >= 80 
                ? (darkMode ? 'bg-green-900' : 'bg-[#e8f5e8]') 
                : percentage >= 60 
                ? (darkMode ? 'bg-yellow-900' : 'bg-[#f2e08a]') 
                : (darkMode ? 'bg-red-900' : 'bg-[#fdeaea]')
              }
            `}>
              <Trophy size={48} className={getScoreColor()} />
            </div>
            
            <p className={`text-lg ${getTextClass('body')}`}>
              {selectedBank?.name}
            </p>
          </div>
        </div>

        {/* Main Score Card */}
        <div className={getScoreCardClass()}>
          <div className="text-center mb-6">
            <div className={`
              text-6xl font-bold mb-4 transition-all duration-1000 
              ${showAnimation ? 'scale-100 opacity-100' : 'scale-50 opacity-0'} 
              ${getScoreColor()}
            `}>
              {showAnimation ? percentage : 0}%
            </div>
            <p className={`text-2xl mb-2 ${getTextClass('heading')}`}>
              {correctCount} out of {totalQuestions} correct
            </p>
            <p className={`text-lg font-medium ${performance.color}`}>
              {performance.message}
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className={getStatCardClass()}>
              <Target className={`w-6 h-6 mx-auto mb-2 ${darkMode ? 'text-green-400' : 'text-[#4CAF50]'}`} />
              <p className={`text-sm ${getTextClass('body')}`}>Correct</p>
              <p className={`text-xl font-bold ${darkMode ? 'text-green-400' : 'text-[#4CAF50]'}`}>
                {correctCount}
              </p>
            </div>
            
            <div className={getStatCardClass()}>
              <RotateCcw className={`w-6 h-6 mx-auto mb-2 ${darkMode ? 'text-red-400' : 'text-[#F44336]'}`} />
              <p className={`text-sm ${getTextClass('body')}`}>Incorrect</p>
              <p className={`text-xl font-bold ${darkMode ? 'text-red-400' : 'text-[#F44336]'}`}>
                {incorrectCount}
              </p>
            </div>
            
            <div className={getStatCardClass()}>
              <Clock className={`w-6 h-6 mx-auto mb-2 ${darkMode ? 'text-orange-400' : 'text-[#FF6701]'}`} />
              <p className={`text-sm ${getTextClass('body')}`}>Time Taken</p>
              <p className={`text-xl font-bold ${darkMode ? 'text-orange-400' : 'text-[#FF6701]'}`}>
                {formatTime(timeTaken)}
              </p>
            </div>
            
            <div className={getStatCardClass()}>
              <TrendingUp className={`w-6 h-6 mx-auto mb-2 ${darkMode ? 'text-blue-400' : 'text-[#0453f1]'}`} />
              <p className={`text-sm ${getTextClass('body')}`}>Grade</p>
              <p className={`text-xl font-bold ${darkMode ? 'text-blue-400' : 'text-[#0453f1]'}`}>
                {percentage >= 90 ? 'A*' : 
                 percentage >= 80 ? 'A' : 
                 percentage >= 70 ? 'B' : 
                 percentage >= 60 ? 'C' : 
                 percentage >= 50 ? 'D' :
                 percentage >= 40 ? 'E' : 'U'}
              </p>
            </div>
          </div>
        </div>

        {/* Topic Breakdown */}
        {Object.keys(categoryBreakdown).length > 1 && (
          <div className={`${getCardClass()} mb-8`}>
            <h3 className={`text-lg font-semibold mb-4 flex items-center ${getTextClass('heading')}`}>
              <BookOpen className="w-5 h-5 mr-2" />
              Performance by Topic
            </h3>
            <div className="space-y-3">
              {Object.entries(categoryBreakdown).map(([topic, stats]) => {
                const topicPercentage = Math.round((stats.correct / stats.total) * 100);
                return (
                  <div key={topic} className={getTopicCardClass()}>
                    <div className="flex-1">
                      <p className={`font-medium ${getTextClass('heading')}`}>{topic}</p>
                      <p className={`text-sm ${getTextClass('body')}`}>
                        {stats.correct}/{stats.total} correct
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className={`w-20 rounded-full h-2 ${darkMode ? 'bg-gray-600' : 'bg-[#e5e6ea]'}`}>
                        <div 
                          className={`h-2 rounded-full transition-all duration-1000 ${
                            topicPercentage >= 80 
                              ? (darkMode ? 'bg-green-400' : 'bg-[#4CAF50]') :
                            topicPercentage >= 60 
                              ? (darkMode ? 'bg-orange-400' : 'bg-[#FF6701]') 
                              : (darkMode ? 'bg-red-400' : 'bg-[#F44336]')
                          }`}
                          style={{ width: showAnimation ? `${topicPercentage}%` : '0%' }}
                        />
                      </div>
                      <span className={`font-semibold text-sm ${
                        topicPercentage >= 80 
                          ? (darkMode ? 'text-green-400' : 'text-[#4CAF50]') :
                        topicPercentage >= 60 
                          ? (darkMode ? 'text-orange-400' : 'text-[#FF6701]') 
                          : (darkMode ? 'text-red-400' : 'text-[#F44336]')
                      }`}>
                        {topicPercentage}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-4">
          <button
            onClick={onReview}
            className={`w-full py-4 px-8 rounded-lg font-semibold text-lg transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-[1.02] ${
              darkMode 
                ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                : 'bg-[#0453f1] hover:bg-[#0341c7] text-white'
            }`}
          >
            📖 Review Answers & Explanations
          </button>
          
          {incorrectCount > 0 && (
            <button
              onClick={onRetestIncorrect}
              className={`w-full py-4 px-8 rounded-lg font-semibold text-lg transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-[1.02] ${
                darkMode 
                  ? 'bg-orange-600 hover:bg-orange-700 text-white' 
                  : 'bg-[#FF6701] hover:bg-[#e55a01] text-white'
              }`}
            >
              🔄 Practice Incorrect Questions ({incorrectCount})
            </button>
          )}
          
          <button
            onClick={handleRetryNewQuestions}
            className={`w-full py-4 px-8 rounded-lg font-semibold text-lg transition-all duration-200 shadow-sm hover:shadow-md ${
              darkMode 
                ? 'bg-gray-700 hover:bg-gray-600 text-gray-200' 
                : 'bg-[#e5e6ea] hover:bg-[#d1d2d6] text-[#000000]'
            }`}
          >
            🎯 Try New Questions
          </button>
          
          <button
            onClick={goHome}
            className={`w-full py-4 px-8 rounded-lg font-semibold text-lg transition-all duration-200 border-2 ${
              darkMode 
                ? 'bg-transparent border-gray-600 text-gray-300 hover:bg-gray-800 hover:border-gray-500' 
                : 'bg-white border-[#e5e6ea] text-[#58585A] hover:bg-[#e9f0f6] hover:border-[#d1d2d6]'
            }`}
          >
            🏠 Choose Different Question Bank
          </button>
        </div>

        {/* Encouragement Message */}
        <div className={getEncouragementCardClass()}>
          <h4 className={`font-semibold mb-3 ${getTextClass('heading')}`}>
            💡 Keep Learning!
          </h4>
          <p className={`text-sm leading-relaxed ${getTextClass('body')}`}>
            {percentage >= 80 
              ? "Fantastic work! You're clearly understanding these physics concepts well. Keep up the excellent progress!"
              : percentage >= 60
              ? "You're doing well! Review the explanations for questions you missed to strengthen your understanding."
              : "Every expert was once a beginner. Use the detailed explanations to learn from each question and keep practicing!"
            }
          </p>
        </div>

        {/* Debug Info */}
        {process.env.NODE_ENV === 'development' && (
          <div className={`mt-8 p-4 rounded-lg text-xs ${
            darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-100 text-gray-600'
          }`}>
            <strong>Debug Info:</strong> 
            Questions: {questions.length}, 
            Answers: {answers.length}, 
            Time: {timeTaken}s,
            Bank: {selectedBank?.id},
            Dark Mode: {darkMode ? 'On' : 'Off'}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultScreen;