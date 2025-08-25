// ==============================
// 📚 screens/ReviewScreen.js - Answer Review & Explanations + Dark Mode
// ==============================
import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, CheckCircle, XCircle, ArrowLeft, Image as ImageIcon } from 'lucide-react';
import axcelLogo from '../assets/axcel-logo.png';

const ReviewScreen = ({
  questions,
  answers,
  onBackToStart,
  onBackToResults,
  selectedBank,
  darkMode = false // 🌙 NEW: Dark mode prop
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  const currentQuestion = questions?.[currentIndex];
  const userAnswer = answers?.find(a => a.questionId === currentQuestion?.id);
  const isCorrect = userAnswer?.correct || false;

  // 🎯 NEW: Auto-generate image path like QuestionCard
  const getQuestionImagePath = () => {
    if (!selectedBank?.id) {
      console.warn('No selectedBank.id available for image path');
      return null;
    }
    
    // 🎯 FIXED: Use original question number instead of current index
    let questionNumber;
    
    // Try to extract question number from question ID first
    if (currentQuestion?.id) {
      const match = currentQuestion.id.toString().match(/(\d+)/);
      if (match) {
        questionNumber = parseInt(match[1]);
        console.log(`🎯 Review using question ID number: ${questionNumber} from ID: ${currentQuestion.id}`);
      }
    }
    
    // Fallback: use current index + 1 (for normal review flow)
    if (!questionNumber) {
      questionNumber = currentIndex + 1;
      console.log(`📍 Review using current index: ${questionNumber} (fallback)`);
    }
    
    const paddedNumber = questionNumber.toString().padStart(2, '0');
    const imagePath = `/question_banks/${selectedBank.id}/images/question_${paddedNumber}_enhanced.png`;
    
    console.log(`🖼️ Generated image path for review: ${imagePath} (Question ${questionNumber})`);
    return imagePath;
  };

  // Reset image states when question changes - ENHANCED
  useEffect(() => {
    setImageError(false);
    setImageLoading(true);
  }, [currentQuestion?.id, currentIndex]);

  // Handle image load events - UNCHANGED
  const handleImageLoad = () => {
    setImageLoading(false);
    setImageError(false);
  };

  const handleImageError = () => {
    setImageLoading(false);
    setImageError(true);
    console.warn(`Failed to load image: ${getQuestionImagePath()}`);
  };

  // Navigation functions - UNCHANGED
  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  // 🌙 DARK MODE STYLING HELPERS
  const getBackgroundClass = () => {
    return darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900';
  };

  const getCardClass = (customBg = null) => {
    if (customBg) return customBg;
    
    const baseClass = 'rounded-xl p-6 border transition-colors duration-300';
    if (darkMode) {
      return `${baseClass} bg-gray-800 border-gray-700`;
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

  const getOptionButtonClass = (isUserAnswer, isCorrectAnswer, isCorrect) => {
    const baseClass = 'w-full p-4 rounded-lg border-2 text-left transition-all duration-200';
    
    if (isCorrectAnswer) {
      if (darkMode) {
        return `${baseClass} border-green-500 bg-green-900 text-gray-200`;
      }
      return `${baseClass} border-[#4CAF50] bg-[#e8f5e8] text-[#000000]`;
    } else if (isUserAnswer && !isCorrect) {
      if (darkMode) {
        return `${baseClass} border-red-500 bg-red-900 text-gray-200`;
      }
      return `${baseClass} border-[#F44336] bg-[#fdeaea] text-[#000000]`;
    } else {
      if (darkMode) {
        return `${baseClass} border-gray-600 bg-gray-700 text-gray-200`;
      }
      return `${baseClass} border-[#e5e6ea] bg-white text-[#000000]`;
    }
  };

  const getSummaryCardClass = () => {
    const baseClass = 'rounded-lg border p-4 transition-colors duration-300';
    if (darkMode) {
      return `${baseClass} bg-gray-700 border-gray-600`;
    }
    return `${baseClass} bg-white border-[#e5e6ea]`;
  };

  const getExplanationCardClass = (bgType = 'default') => {
    const baseClass = 'rounded-xl p-6 border transition-colors duration-300';
    
    if (bgType === 'quick-answer') {
      if (darkMode) {
        return `${baseClass} bg-yellow-900 border-yellow-700`;
      }
      return `${baseClass} bg-[#f2e08a] border-[#FF6701]`;
    }
    
    if (darkMode) {
      return `${baseClass} bg-gray-800 border-gray-700`;
    }
    return `${baseClass} bg-white border-[#e5e6ea]`;
  };

  // Error state - ENHANCED with dark mode
  if (!questions || !answers || questions.length === 0) {
    return (
      <div className={`min-h-screen p-6 flex items-center justify-center transition-colors duration-300 ${getBackgroundClass()}`}>
        <div className="text-center text-red-500">
          ⚠️ Error: Review data not found
          <button 
            onClick={onBackToResults || onBackToStart}
            className="block mt-4 mx-auto px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Back to Results
          </button>
        </div>
      </div>
    );
  }

  if (!currentQuestion || !userAnswer) {
    return (
      <div className={`min-h-screen p-6 flex items-center justify-center transition-colors duration-300 ${getBackgroundClass()}`}>
        <div className="text-center text-red-500">
          ⚠️ Error: Question or answer data missing
          <div className={`mt-4 text-sm ${getTextClass('body')}`}>
            <p>Question index: {currentIndex}</p>
            <p>Questions available: {questions.length}</p>
            <p>Answers available: {answers.length}</p>
          </div>
          <button 
            onClick={onBackToResults || onBackToStart}
            className="block mt-4 mx-auto px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Back to Results
          </button>
        </div>
      </div>
    );
  }

  const isFirstQuestion = currentIndex === 0;
  const isLastQuestion = currentIndex === questions.length - 1;
  
  // 🎯 Use auto-generated image path
  const imageUrl = getQuestionImagePath();

  return (
    <div className={`min-h-screen p-6 transition-colors duration-300 ${getBackgroundClass()}`}>
      <div className="max-w-4xl mx-auto">
        {/* Header with Logo */}
        <div className="flex justify-between items-start mb-6">
          {/* Left side - Logo and Question Info */}
          <div className="flex items-start space-x-3">
            {/* 🎯 Logo integrated in header */}
            <img 
              src={axcelLogo} 
              alt="Axcel Logo" 
              className={`h-8 w-auto mt-1 transition-opacity duration-300 ${
                darkMode ? 'opacity-90' : 'opacity-80'
              }`}
            />
            <div>
              <h2 className={`text-xl font-semibold ${getTextClass('heading')}`}>
                Review: Question {currentIndex + 1} of {questions.length}
              </h2>
              <p className={getTextClass('body')}>
                {currentQuestion.topic} • {isCorrect ? '✅ Correct' : '❌ Incorrect'}
              </p>
              {selectedBank && (
                <p className={`text-sm mt-1 ${getTextClass('body')}`}>
                  {selectedBank.name}
                </p>
              )}
            </div>
          </div>
          
          {/* Right side - Back Button */}
          <button
            onClick={onBackToResults || onBackToStart}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              darkMode 
                ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' 
                : 'bg-[#e5e6ea] text-[#000000] hover:bg-[#d1d2d6]'
            }`}
          >
            <ArrowLeft size={16} />
            <span>Back to Results</span>
          </button>
        </div>

        {/* Question Card */}
        <div className={`${getCardClass()} mb-6`}>
          {/* Question Image - 🎯 ENHANCED: Use auto-generated path with overlay */}
          <div className="mb-6">
            {imageLoading && (
              <div className={`w-full h-48 rounded-lg flex items-center justify-center ${
                darkMode ? 'bg-gray-700' : 'bg-[#e5e6ea]'
              }`}>
                <div className="text-center">
                  <div className={`animate-spin rounded-full h-8 w-8 border-b-2 mx-auto mb-2 ${
                    darkMode ? 'border-blue-400' : 'border-[#0453f1]'
                  }`}></div>
                  <p className={`text-sm ${getTextClass('body')}`}>Loading image...</p>
                </div>
              </div>
            )}
            
            {imageError && (
              <div className={`w-full h-48 border rounded-lg flex items-center justify-center ${
                darkMode 
                  ? 'bg-red-900 border-red-700 text-red-400' 
                  : 'bg-[#fdeaea] border-[#F44336] text-[#F44336]'
              }`}>
                <div className="text-center">
                  <ImageIcon size={32} className="mx-auto mb-2" />
                  <p className="text-sm">Failed to load question image</p>
                  <p className="text-xs mt-1">Expected: {imageUrl}</p>
                </div>
              </div>
            )}
            
            {imageUrl && (
              <div className="relative inline-block">
                <img
                  src={imageUrl}
                  alt={`Question ${currentIndex + 1} - Enhanced Review`}
                  onLoad={handleImageLoad}
                  onError={handleImageError}
                  className={`
                    w-full max-w-2xl mx-auto rounded-lg border shadow-sm
                    ${darkMode ? 'border-gray-600' : 'border-[#e5e6ea]'}
                    ${imageLoading ? 'hidden' : imageError ? 'hidden' : 'block'}
                  `}
                  style={{ maxHeight: '400px', objectFit: 'contain' }}
                />
                
                {/* 🎯 Same white overlay as QuestionCard */}
                <div className="absolute top-1 left-1 md:top-2 md:left-2 bg-white rounded-sm shadow-sm select-none pointer-events-none" 
                     style={{ 
                       width: '36px', 
                       height: '24px',
                       '@media (max-width: 768px)': {
                         width: '30px',
                         height: '20px'
                       }
                     }}>
                  {/* Invisible overlay to hide question number (covers 1-40) */}
                </div>
              </div>
            )}
          </div>

          {/* Question Text - Only show for context since image has everything */}
          <h3 className={`text-lg font-medium mb-6 leading-relaxed ${getTextClass('heading')}`}>
            {currentQuestion.question_text}
          </h3>

          {/* Answer Options with Results - Show A,B,C,D with status */}
          <div className="space-y-3 mb-6">
            {['A', 'B', 'C', 'D'].map((optionKey) => {
              const optionText = currentQuestion.options?.[optionKey] || `Option ${optionKey}`;
              const isUserAnswer = userAnswer.userAnswer === optionKey;
              const isCorrectAnswer = currentQuestion.correct_answer === optionKey;
              
              let icon = null;
              let statusText = '';

              if (isCorrectAnswer) {
                icon = <CheckCircle size={20} className={darkMode ? 'text-green-400' : 'text-[#4CAF50]'} />;
                statusText = 'Correct Answer';
              } else if (isUserAnswer && !isCorrect) {
                icon = <XCircle size={20} className={darkMode ? 'text-red-400' : 'text-[#F44336]'} />;
                statusText = 'Your Answer';
              }

              return (
                <div key={optionKey} className={getOptionButtonClass(isUserAnswer, isCorrectAnswer, isCorrect)}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <span className="font-semibold mr-3">{optionKey}.</span>
                      {optionText}
                      {statusText && (
                        <span className="ml-3 text-sm font-medium opacity-75">
                          ({statusText})
                        </span>
                      )}
                    </div>
                    {icon}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Your Answer vs Correct Answer Summary */}
          <div className={getSummaryCardClass()}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`text-sm font-semibold mb-1 ${getTextClass('body')}`}>Your Answer:</p>
                <p className={`text-lg font-medium ${
                  isCorrect 
                    ? (darkMode ? 'text-green-400' : 'text-[#4CAF50]') 
                    : (darkMode ? 'text-red-400' : 'text-[#F44336]')
                }`}>
                  {userAnswer.userAnswer} - {currentQuestion.options?.[userAnswer.userAnswer] || 'Option ' + userAnswer.userAnswer}
                </p>
              </div>
              <div>
                <p className={`text-sm font-semibold mb-1 ${getTextClass('body')}`}>Correct Answer:</p>
                <p className={`text-lg font-medium ${darkMode ? 'text-green-400' : 'text-[#4CAF50]'}`}>
                  {currentQuestion.correct_answer} - {currentQuestion.options?.[currentQuestion.correct_answer] || 'Option ' + currentQuestion.correct_answer}
                </p>
              </div>
            </div>
            
            {/* Result Badge */}
            <div className="mt-4 text-center">
              <span className={`
                inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border
                ${isCorrect 
                  ? (darkMode ? 'bg-green-900 text-green-400 border-green-500' : 'bg-[#e8f5e8] text-[#4CAF50] border-[#4CAF50]')
                  : (darkMode ? 'bg-red-900 text-red-400 border-red-500' : 'bg-[#fdeaea] text-[#F44336] border-[#F44336]')
                }
              `}>
                {isCorrect ? '✅ Correct' : '❌ Incorrect'}
              </span>
            </div>
          </div>
        </div>

        {/* Explanations */}
        <div className="space-y-6 mb-8">
          {/* Simple Answer */}
          {currentQuestion.simple_answer && (
            <div className={getExplanationCardClass('quick-answer')}>
              <h4 className={`font-semibold mb-3 flex items-center ${getTextClass('heading')}`}>
                <span className="mr-2">💡</span>
                Quick Answer
              </h4>
              <p className={`leading-relaxed ${getTextClass('body')}`}>
                {currentQuestion.simple_answer}
              </p>
            </div>
          )}

          {/* Step-by-step Solution */}
          {currentQuestion.calculation_steps && currentQuestion.calculation_steps.length > 0 && (
            <div className={getExplanationCardClass()}>
              <h4 className={`font-semibold mb-4 flex items-center ${getTextClass('heading')}`}>
                <span className="mr-2">📝</span>
                Step-by-Step Solution
              </h4>
              <ol className="space-y-3">
                {currentQuestion.calculation_steps.map((step, index) => (
                  <li key={index} className="flex items-start">
                    <span className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold mr-4 mt-0.5 flex-shrink-0 ${
                      darkMode ? 'bg-blue-600 text-white' : 'bg-[#0453f1] text-white'
                    }`}>
                      {index + 1}
                    </span>
                    <span className={`leading-relaxed flex-1 ${getTextClass('body')}`}>
                      {step}
                    </span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Detailed Explanation */}
          {currentQuestion.detailed_explanation && (
            <div className={getExplanationCardClass()}>
              <h4 className={`font-semibold mb-4 flex items-center ${getTextClass('heading')}`}>
                <span className="mr-2">📖</span>
                Detailed Explanation
              </h4>
              
              <div className="space-y-4">
                {/* Why Correct */}
                {currentQuestion.detailed_explanation.why_correct && (
                  <div>
                    <h5 className={`font-medium mb-2 flex items-center ${
                      darkMode ? 'text-green-400' : 'text-[#4CAF50]'
                    }`}>
                      <CheckCircle size={16} className="mr-2" />
                      Why {currentQuestion.correct_answer} is correct:
                    </h5>
                    <p className={`ml-6 leading-relaxed ${getTextClass('body')}`}>
                      {currentQuestion.detailed_explanation.why_correct}
                    </p>
                  </div>
                )}
                
                {/* Why Others Wrong */}
                {currentQuestion.detailed_explanation.why_others_wrong && 
                 Object.keys(currentQuestion.detailed_explanation.why_others_wrong).length > 0 && (
                  <div>
                    <h5 className={`font-medium mb-3 flex items-center ${
                      darkMode ? 'text-red-400' : 'text-[#F44336]'
                    }`}>
                      <XCircle size={16} className="mr-2" />
                      Why other options are wrong:
                    </h5>
                    <div className="ml-6 space-y-2">
                      {Object.entries(currentQuestion.detailed_explanation.why_others_wrong).map(([option, explanation]) => (
                        <div key={option} className={`border-l-4 pl-3 ${
                          darkMode ? 'border-red-500' : 'border-[#F44336]'
                        }`}>
                          <span className={`font-medium ${getTextClass('heading')}`}>Option {option}: </span>
                          <span className={getTextClass('body')}>{explanation}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={isFirstQuestion}
            className={`
              flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
              ${isFirstQuestion
                ? (darkMode ? 'bg-gray-800 text-gray-500 cursor-not-allowed' : 'bg-[#e5e6ea] text-[#58585A] cursor-not-allowed')
                : (darkMode ? 'bg-gray-700 text-gray-200 hover:bg-gray-600 shadow-sm hover:shadow-md' : 'bg-[#e5e6ea] text-[#000000] hover:bg-[#d1d2d6] shadow-sm hover:shadow-md')
              }
            `}
          >
            <ChevronLeft size={20} />
            <span>Previous</span>
          </button>

          <div className={`text-center ${getTextClass('body')}`}>
            <p className="text-sm">Question {currentIndex + 1} of {questions.length}</p>
            <div className={`w-32 rounded-full h-2 mt-1 ${darkMode ? 'bg-gray-700' : 'bg-[#e5e6ea]'}`}>
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  darkMode ? 'bg-blue-500' : 'bg-[#0453f1]'
                }`}
                style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>

          <button
            onClick={handleNext}
            disabled={isLastQuestion}
            className={`
              flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
              ${isLastQuestion
                ? (darkMode ? 'bg-gray-800 text-gray-500 cursor-not-allowed' : 'bg-[#e5e6ea] text-[#58585A] cursor-not-allowed')
                : (darkMode ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md' : 'bg-[#0453f1] text-white hover:bg-[#0341c7] shadow-sm hover:shadow-md')
              }
            `}
          >
            <span>Next</span>
            <ChevronRight size={20} />
          </button>
        </div>

        {/* Quick Navigation Hints */}
        <div className={`mt-6 text-center text-sm ${getTextClass('muted')}`}>
          {!isFirstQuestion && !isLastQuestion && (
            <p>Use the Previous/Next buttons to review other questions</p>
          )}
          {isFirstQuestion && !isLastQuestion && (
            <p>This is the first question. Use Next to continue reviewing.</p>
          )}
          {isLastQuestion && !isFirstQuestion && (
            <p>This is the last question. Use Previous to go back or return to results.</p>
          )}
          {isFirstQuestion && isLastQuestion && (
            <p>Only one question to review. Return to results when ready.</p>
          )}
        </div>

        {/* Debug Info */}
        {process.env.NODE_ENV === 'development' && (
          <div className={`mt-8 p-4 rounded-lg text-xs ${
            darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-100 text-gray-600'
          }`}>
            <strong>Debug Info:</strong> 
            Questions: {questions?.length || 0}, 
            Answers: {answers?.length || 0},
            Current Index: {currentIndex},
            Question ID: {currentQuestion?.id || 'N/A'}, 
            User Answer: {userAnswer?.userAnswer || 'N/A'}, 
            Correct: {currentQuestion?.correct_answer || 'N/A'},
            Image: {imageUrl || 'None'},
            Dark Mode: {darkMode ? 'On' : 'Off'}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewScreen;