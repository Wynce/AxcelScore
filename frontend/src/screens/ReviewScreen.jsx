// ==============================
// 📚 screens/ReviewScreen.js - Answer Review & Explanations + uiTheme Support
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
  uiTheme = 'light' // Updated to use uiTheme instead of darkMode
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);
  const [showDetailedExplanation, setShowDetailedExplanation] = useState(false);

  const currentQuestion = questions?.[currentIndex];
  const userAnswer = answers?.find(a => a.questionId === currentQuestion?.id);
  const isCorrect = userAnswer?.correct || false;

  // FIXED: Auto-generate image path with proper bank handling
  const getQuestionImagePath = () => {
    // FIXED: Handle multi-bank case by using the question's bankId
    let bankId = selectedBank?.id;
    
    // If selectedBank.id is "multi", try to get bankId from the current question
    if (bankId === 'multi' && currentQuestion?.bankId) {
      bankId = currentQuestion.bankId;
    }
    
    if (!bankId || bankId === 'multi') {
      console.warn('No specific bankId available for image path, selectedBank:', selectedBank);
      return null;
    }
    
    let questionNumber;
    
    // Try to extract question number from question ID first
    if (currentQuestion?.id) {
      const match = currentQuestion.id.toString().match(/(\d+)/);
      if (match) {
        questionNumber = parseInt(match[1]);
        console.log(`Review using question ID number: ${questionNumber} from ID: ${currentQuestion.id}`);
      }
    }
    
    // Fallback: use current index + 1 (for normal review flow)
    if (!questionNumber) {
      questionNumber = currentIndex + 1;
      console.log(`Review using current index: ${questionNumber} (fallback)`);
    }
    
    const paddedNumber = questionNumber.toString().padStart(2, '0');
    // FIXED: Correct path without leading dot
    const imagePath = `/question_banks/${bankId}/images/question_${paddedNumber}_enhanced.png`;
    
    console.log(`Generated image path for review: ${imagePath} (Question ${questionNumber}, Bank: ${bankId})`);
    return imagePath;
  };

  // Reset image states when question changes
  useEffect(() => {
    setImageError(false);
    setImageLoading(true);
    setShowDetailedExplanation(false); // Reset detailed explanation when changing questions
  }, [currentQuestion?.id, currentIndex]);

  // Handle image load events
  const handleImageLoad = () => {
    setImageLoading(false);
    setImageError(false);
  };

  const handleImageError = () => {
    setImageLoading(false);
    setImageError(true);
    console.warn(`Failed to load image: ${getQuestionImagePath()}`);
  };

  // Navigation functions
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

  // UPDATED: Theme styling helpers using uiTheme
  const getBackgroundClass = () => {
    switch(uiTheme) {
      case 'dark':
        return 'bg-gray-900 text-white';
      case 'genalpha':
        return 'genalpha genalpha-animated text-white';
      default:
        return 'bg-white text-gray-900';
    }
  };

  const getCardClass = (customBg = null) => {
    if (customBg) return customBg;
    
    const baseClass = 'rounded-xl p-6 border transition-colors duration-300';
    switch(uiTheme) {
      case 'dark':
        return `${baseClass} bg-gray-800 border-gray-700`;
      case 'genalpha':
        return `${baseClass} genalpha-card backdrop-blur-xl border border-white/20`;
      default:
        return `${baseClass} bg-[#e9f0f6] border-[#e5e6ea]`;
    }
  };

  const getTextClass = (type = 'body') => {
    switch(uiTheme) {
      case 'dark':
        switch (type) {
          case 'heading': return 'text-white';
          case 'subheading': return 'text-gray-200';
          case 'body': return 'text-gray-300';
          case 'muted': return 'text-gray-400';
          default: return 'text-gray-300';
        }
      case 'genalpha':
        switch (type) {
          case 'heading': return 'text-white';
          case 'subheading': return 'text-white/90';
          case 'body': return 'text-white/80';
          case 'muted': return 'text-white/70';
          default: return 'text-white/80';
        }
      default:
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
      switch(uiTheme) {
        case 'dark':
          return `${baseClass} border-green-500 bg-green-900 text-gray-200`;
        case 'genalpha':
          return `${baseClass} border-green-400 bg-green-500/20 text-white backdrop-blur-sm`;
        default:
          return `${baseClass} border-[#4CAF50] bg-[#e8f5e8] text-[#000000]`;
      }
    } else if (isUserAnswer && !isCorrect) {
      switch(uiTheme) {
        case 'dark':
          return `${baseClass} border-red-500 bg-red-900 text-gray-200`;
        case 'genalpha':
          return `${baseClass} border-red-400 bg-red-500/20 text-white backdrop-blur-sm`;
        default:
          return `${baseClass} border-[#F44336] bg-[#fdeaea] text-[#000000]`;
      }
    } else {
      switch(uiTheme) {
        case 'dark':
          return `${baseClass} border-gray-600 bg-gray-700 text-gray-200`;
        case 'genalpha':
          return `${baseClass} border-white/30 bg-white/10 text-white backdrop-blur-sm`;
        default:
          return `${baseClass} border-[#e5e6ea] bg-white text-[#000000]`;
      }
    }
  };

  const getSummaryCardClass = () => {
    const baseClass = 'rounded-lg border p-4 transition-colors duration-300';
    switch(uiTheme) {
      case 'dark':
        return `${baseClass} bg-gray-700 border-gray-600`;
      case 'genalpha':
        return `${baseClass} genalpha-card backdrop-blur-xl border border-white/20`;
      default:
        return `${baseClass} bg-white border-[#e5e6ea]`;
    }
  };

  const getExplanationCardClass = (bgType = 'default') => {
    const baseClass = 'rounded-xl p-6 border transition-colors duration-300';
    
    if (bgType === 'quick-answer') {
      switch(uiTheme) {
        case 'dark':
          return `${baseClass} bg-yellow-900 border-yellow-700`;
        case 'genalpha':
          return `${baseClass} bg-yellow-500/20 border-yellow-400/30 backdrop-blur-xl`;
        default:
          return `${baseClass} bg-[#f2e08a] border-[#FF6701]`;
      }
    }
    
    switch(uiTheme) {
      case 'dark':
        return `${baseClass} bg-gray-800 border-gray-700`;
      case 'genalpha':
        return `${baseClass} genalpha-card backdrop-blur-xl border border-white/20`;
      default:
        return `${baseClass} bg-white border-[#e5e6ea]`;
    }
  };

  const getButtonClass = (variant = 'default', disabled = false) => {
    const baseClass = 'flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200';
    
    if (disabled) {
      switch(uiTheme) {
        case 'dark':
          return `${baseClass} bg-gray-800 text-gray-500 cursor-not-allowed`;
        case 'genalpha':
          return `${baseClass} bg-white/5 text-white/30 cursor-not-allowed backdrop-blur-sm`;
        default:
          return `${baseClass} bg-[#e5e6ea] text-[#58585A] cursor-not-allowed`;
      }
    }

    switch(variant) {
      case 'primary':
        switch(uiTheme) {
          case 'dark':
            return `${baseClass} bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md`;
          case 'genalpha':
            return `${baseClass} genalpha-button text-white hover:scale-105 shadow-sm hover:shadow-md`;
          default:
            return `${baseClass} bg-[#0453f1] text-white hover:bg-[#0341c7] shadow-sm hover:shadow-md`;
        }
      case 'secondary':
        switch(uiTheme) {
          case 'dark':
            return `${baseClass} bg-gray-700 text-gray-200 hover:bg-gray-600 shadow-sm hover:shadow-md`;
          case 'genalpha':
            return `${baseClass} bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm border border-white/20 shadow-sm hover:shadow-md`;
          default:
            return `${baseClass} bg-[#e5e6ea] text-[#000000] hover:bg-[#d1d2d6] shadow-sm hover:shadow-md`;
        }
      default:
        switch(uiTheme) {
          case 'dark':
            return `${baseClass} bg-gray-700 text-gray-200 hover:bg-gray-600`;
          case 'genalpha':
            return `${baseClass} bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm border border-white/20`;
          default:
            return `${baseClass} bg-[#e5e6ea] text-[#000000] hover:bg-[#d1d2d6]`;
        }
    }
  };

  // Error state - Enhanced with uiTheme support
  if (!questions || !answers || questions.length === 0) {
    return (
      <div className={`min-h-screen p-6 flex items-center justify-center transition-colors duration-300 ${getBackgroundClass()}`}>
        <div className="text-center text-red-500">
          Warning: Review data not found
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
          Warning: Question or answer data missing
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
  
  // Use auto-generated image path
  const imageUrl = getQuestionImagePath();

  return (
    <div className={`min-h-screen p-6 transition-colors duration-300 ${getBackgroundClass()}`}>
      <div className="max-w-4xl mx-auto">
        {/* Header with Logo */}
        <div className="flex justify-between items-start mb-6">
          {/* Left side - Logo and Question Info */}
          <div className="flex items-start space-x-3">
            {/* Logo integrated in header */}
            <img 
              src={axcelLogo} 
              alt="Axcel Logo" 
              className={`h-8 w-auto mt-1 transition-opacity duration-300 ${
                uiTheme === 'dark' ? 'opacity-90' : 'opacity-80'
              }`}
            />
            <div>
              <h2 className={`text-xl font-semibold ${getTextClass('heading')}`}>
                Review: Question {currentIndex + 1} of {questions.length}
              </h2>
              <p className={getTextClass('body')}>
                {currentQuestion.topic} • {isCorrect ? 'Correct' : 'Incorrect'}
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
            className={getButtonClass('secondary')}
          >
            <ArrowLeft size={16} />
            <span>Back to Results</span>
          </button>
        </div>

        {/* Question Card */}
        <div className={`${getCardClass()} mb-6`}>
          {/* Question Image - Enhanced with proper path handling */}
          <div className="mb-6">
            {imageLoading && (
              <div className={`w-full h-48 rounded-lg flex items-center justify-center ${
                uiTheme === 'dark' ? 'bg-gray-700' : 
                uiTheme === 'genalpha' ? 'bg-white/10 backdrop-blur-sm' : 
                'bg-[#e5e6ea]'
              }`}>
                <div className="text-center">
                  <div className={`animate-spin rounded-full h-8 w-8 border-b-2 mx-auto mb-2 ${
                    uiTheme === 'dark' ? 'border-blue-400' : 
                    uiTheme === 'genalpha' ? 'border-white' : 
                    'border-[#0453f1]'
                  }`}></div>
                  <p className={`text-sm ${getTextClass('body')}`}>Loading image...</p>
                </div>
              </div>
            )}
            
            {imageError && (
              <div className={`w-full h-48 border rounded-lg flex items-center justify-center ${
                uiTheme === 'dark' ? 'bg-red-900 border-red-700 text-red-400' : 
                uiTheme === 'genalpha' ? 'bg-red-500/20 border-red-400/30 text-red-300 backdrop-blur-sm' :
                'bg-[#fdeaea] border-[#F44336] text-[#F44336]'
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
                    ${uiTheme === 'dark' ? 'border-gray-600' : 
                      uiTheme === 'genalpha' ? 'border-white/20' : 
                      'border-[#e5e6ea]'}
                    ${imageLoading ? 'hidden' : imageError ? 'hidden' : 'block'}
                  `}
                  style={{ maxHeight: '400px', objectFit: 'contain' }}
                />
                
                {/* Same white overlay as QuestionCard */}
                <div className="absolute top-1 left-1 md:top-2 md:left-2 bg-white rounded-sm shadow-sm select-none pointer-events-none" 
                     style={{ 
                       width: '36px', 
                       height: '24px'
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
                icon = <CheckCircle size={20} className={
                  uiTheme === 'dark' ? 'text-green-400' : 
                  uiTheme === 'genalpha' ? 'text-green-300' : 
                  'text-[#4CAF50]'
                } />;
                statusText = 'Correct Answer';
              } else if (isUserAnswer && !isCorrect) {
                icon = <XCircle size={20} className={
                  uiTheme === 'dark' ? 'text-red-400' : 
                  uiTheme === 'genalpha' ? 'text-red-300' : 
                  'text-[#F44336]'
                } />;
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
                    ? (uiTheme === 'dark' ? 'text-green-400' : 
                       uiTheme === 'genalpha' ? 'text-green-300' : 
                       'text-[#4CAF50]') 
                    : (uiTheme === 'dark' ? 'text-red-400' : 
                       uiTheme === 'genalpha' ? 'text-red-300' : 
                       'text-[#F44336]')
                }`}>
                  {userAnswer.userAnswer} - {currentQuestion.options?.[userAnswer.userAnswer] || 'Option ' + userAnswer.userAnswer}
                </p>
              </div>
              <div>
                <p className={`text-sm font-semibold mb-1 ${getTextClass('body')}`}>Correct Answer:</p>
                <p className={`text-lg font-medium ${
                  uiTheme === 'dark' ? 'text-green-400' : 
                  uiTheme === 'genalpha' ? 'text-green-300' : 
                  'text-[#4CAF50]'
                }`}>
                  {currentQuestion.correct_answer} - {currentQuestion.options?.[currentQuestion.correct_answer] || 'Option ' + currentQuestion.correct_answer}
                </p>
              </div>
            </div>
            
            {/* Result Badge */}
            <div className="mt-4 text-center">
              <span className={`
                inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border
                ${isCorrect 
                  ? (uiTheme === 'dark' ? 'bg-green-900 text-green-400 border-green-500' : 
                     uiTheme === 'genalpha' ? 'bg-green-500/20 text-green-300 border-green-400/30 backdrop-blur-sm' :
                     'bg-[#e8f5e8] text-[#4CAF50] border-[#4CAF50]')
                  : (uiTheme === 'dark' ? 'bg-red-900 text-red-400 border-red-500' :
                     uiTheme === 'genalpha' ? 'bg-red-500/20 text-red-300 border-red-400/30 backdrop-blur-sm' :
                     'bg-[#fdeaea] text-[#F44336] border-[#F44336]')
                }
              `}>
                {isCorrect ? 'Correct' : 'Incorrect'}
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
                <span className="mr-2">Quick Answer</span>
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
                <span className="mr-2">Step-by-Step Solution</span>
              </h4>
              <ol className="space-y-3">
                {currentQuestion.calculation_steps.map((step, index) => (
                  <li key={index} className="flex items-start">
                    <span className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold mr-4 mt-0.5 flex-shrink-0 ${
                      uiTheme === 'dark' ? 'bg-blue-600 text-white' : 
                      uiTheme === 'genalpha' ? 'bg-blue-500/80 text-white backdrop-blur-sm' :
                      'bg-[#0453f1] text-white'
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

          {/* Detailed Explanation - Now Clickable */}
          {currentQuestion.detailed_explanation && (
            <div className={getExplanationCardClass()}>
              <div 
                className={`cursor-pointer hover:opacity-80 transition-opacity ${getTextClass('heading')}`}
                onClick={() => setShowDetailedExplanation(!showDetailedExplanation)}
              >
                <h4 className="font-semibold mb-4 flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="mr-2">Detailed Explanation</span>
                  </div>
                  <div className={`transform transition-transform duration-200 ${showDetailedExplanation ? 'rotate-180' : ''}`}>
                    <ChevronRight size={20} />
                  </div>
                </h4>
              </div>
              
              {showDetailedExplanation && (
                <div className="space-y-4 mt-4 animate-in slide-in-from-top-2 duration-200">
                  {/* Handle your actual solutions.json structure */}
                  
                  {/* Approach */}
                  {currentQuestion.detailed_explanation.approach && (
                    <div>
                      <h5 className={`font-medium mb-2 flex items-center ${getTextClass('heading')}`}>
                        <span className="mr-2">🎯</span>
                        Approach:
                      </h5>
                      <p className={`ml-6 leading-relaxed ${getTextClass('body')}`}>
                        {currentQuestion.detailed_explanation.approach}
                      </p>
                    </div>
                  )}

                  {/* Reasoning */}
                  {currentQuestion.detailed_explanation.reasoning && (
                    <div>
                      <h5 className={`font-medium mb-2 flex items-center ${getTextClass('heading')}`}>
                        <span className="mr-2">🧠</span>
                        Reasoning:
                      </h5>
                      <p className={`ml-6 leading-relaxed ${getTextClass('body')}`}>
                        {currentQuestion.detailed_explanation.reasoning}
                      </p>
                    </div>
                  )}

                  {/* Calculation */}
                  {currentQuestion.detailed_explanation.calculation && (
                    <div>
                      <h5 className={`font-medium mb-2 flex items-center ${getTextClass('heading')}`}>
                        <span className="mr-2">🔢</span>
                        Calculation:
                      </h5>
                      <p className={`ml-6 leading-relaxed ${getTextClass('body')}`}>
                        {currentQuestion.detailed_explanation.calculation}
                      </p>
                    </div>
                  )}

                  {/* Conclusion */}
                  {currentQuestion.detailed_explanation.conclusion && (
                    <div>
                      <h5 className={`font-medium mb-2 flex items-center ${
                        uiTheme === 'dark' ? 'text-green-400' : 
                        uiTheme === 'genalpha' ? 'text-green-300' : 
                        'text-[#4CAF50]'
                      }`}>
                        <CheckCircle size={16} className="mr-2" />
                        Conclusion:
                      </h5>
                      <p className={`ml-6 leading-relaxed ${getTextClass('body')}`}>
                        {currentQuestion.detailed_explanation.conclusion}
                      </p>
                    </div>
                  )}

                  {/* Key Concepts (if available) */}
                  {currentQuestion.detailed_explanation.key_concepts && (
                    <div>
                      <h5 className={`font-medium mb-2 flex items-center ${getTextClass('heading')}`}>
                        <span className="mr-2">📝</span>
                        Key Concepts:
                      </h5>
                      <p className={`ml-6 leading-relaxed ${getTextClass('body')}`}>
                        {currentQuestion.detailed_explanation.key_concepts}
                      </p>
                    </div>
                  )}

                  {/* Common Mistakes (if available) */}
                  {currentQuestion.detailed_explanation.common_mistakes && (
                    <div>
                      <h5 className={`font-medium mb-2 flex items-center ${
                        uiTheme === 'dark' ? 'text-yellow-400' : 
                        uiTheme === 'genalpha' ? 'text-yellow-300' : 
                        'text-[#FF9800]'
                      }`}>
                        <span className="mr-2">⚠️</span>
                        Common Mistakes:
                      </h5>
                      <p className={`ml-6 leading-relaxed ${getTextClass('body')}`}>
                        {currentQuestion.detailed_explanation.common_mistakes}
                      </p>
                    </div>
                  )}

                  {/* Fallback: Original structure support */}
                  {currentQuestion.detailed_explanation.why_correct && (
                    <div>
                      <h5 className={`font-medium mb-2 flex items-center ${
                        uiTheme === 'dark' ? 'text-green-400' : 
                        uiTheme === 'genalpha' ? 'text-green-300' : 
                        'text-[#4CAF50]'
                      }`}>
                        <CheckCircle size={16} className="mr-2" />
                        Why {currentQuestion.correct_answer} is correct:
                      </h5>
                      <p className={`ml-6 leading-relaxed ${getTextClass('body')}`}>
                        {currentQuestion.detailed_explanation.why_correct}
                      </p>
                    </div>
                  )}
                  
                  {/* Fallback: Why Others Wrong */}
                  {currentQuestion.detailed_explanation.why_others_wrong && 
                   Object.keys(currentQuestion.detailed_explanation.why_others_wrong).length > 0 && (
                    <div>
                      <h5 className={`font-medium mb-3 flex items-center ${
                        uiTheme === 'dark' ? 'text-red-400' : 
                        uiTheme === 'genalpha' ? 'text-red-300' : 
                        'text-[#F44336]'
                      }`}>
                        <XCircle size={16} className="mr-2" />
                        Why other options are wrong:
                      </h5>
                      <div className="ml-6 space-y-2">
                        {Object.entries(currentQuestion.detailed_explanation.why_others_wrong).map(([option, explanation]) => (
                          <div key={option} className={`border-l-4 pl-3 ${
                            uiTheme === 'dark' ? 'border-red-500' : 
                            uiTheme === 'genalpha' ? 'border-red-400' : 
                            'border-[#F44336]'
                          }`}>
                            <span className={`font-medium ${getTextClass('heading')}`}>Option {option}: </span>
                            <span className={getTextClass('body')}>{explanation}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={isFirstQuestion}
            className={getButtonClass('secondary', isFirstQuestion)}
          >
            <ChevronLeft size={20} />
            <span>Previous</span>
          </button>

          <div className={`text-center ${getTextClass('body')}`}>
            <p className="text-sm">Question {currentIndex + 1} of {questions.length}</p>
            <div className={`w-32 rounded-full h-2 mt-1 ${
              uiTheme === 'dark' ? 'bg-gray-700' : 
              uiTheme === 'genalpha' ? 'bg-white/20' : 
              'bg-[#e5e6ea]'
            }`}>
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  uiTheme === 'dark' ? 'bg-blue-500' : 
                  uiTheme === 'genalpha' ? 'bg-white' : 
                  'bg-[#0453f1]'
                }`}
                style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>

          <button
            onClick={handleNext}
            disabled={isLastQuestion}
            className={getButtonClass('primary', isLastQuestion)}
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
            uiTheme === 'dark' ? 'bg-gray-800 text-gray-400' : 
            uiTheme === 'genalpha' ? 'bg-white/5 text-white/60 backdrop-blur-sm' :
            'bg-gray-100 text-gray-600'
          }`}>
            <strong>Debug Info:</strong><br />
            Questions: {questions?.length || 0}<br />
            Answers: {answers?.length || 0}<br />
            Current Index: {currentIndex}<br />
            Question ID: {currentQuestion?.id || 'N/A'}<br />
            Question Bank ID: {currentQuestion?.bankId || 'N/A'}<br />
            Selected Bank ID: {selectedBank?.id || 'N/A'}<br />
            User Answer: {userAnswer?.userAnswer || 'N/A'}<br />
            Correct: {currentQuestion?.correct_answer || 'N/A'}<br />
            Image: {imageUrl || 'None'}<br />
            UI Theme: {uiTheme}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewScreen;