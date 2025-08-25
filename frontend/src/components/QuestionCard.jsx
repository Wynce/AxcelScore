import React, { useState, useEffect } from 'react';

const QuestionCard = ({ 
  questionObj, 
  currentIndex, 
  total, 
  selectedAnswer, 
  onSelect, 
  onAnswer, 
  onBack, 
  selectedBank,
  goHome,
  darkMode = false, // 🌙 Dark mode prop
  darkModeToggle // 🌙 NEW: Dark mode toggle component prop
}) => {
  const [currentSelection, setCurrentSelection] = useState(selectedAnswer || "");
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  // Add safety checks to prevent undefined errors
  if (!questionObj) {
    return (
      <div className={`flex items-center justify-center min-h-[400px] transition-colors duration-300 ${
        darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'
      }`}>
        <div className="text-center">
          <div className={`animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4 ${
            darkMode ? 'border-blue-400' : 'border-blue-600'
          }`}></div>
          <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>Loading question...</p>
        </div>
      </div>
    );
  }

  // 🎯 Auto-generate image path based on question number and bank ID
  const getQuestionImagePath = () => {
    if (!selectedBank?.id) {
      console.warn('No selectedBank.id available for image path');
      return null;
    }
    
    // 🎯 FIXED: Use original question number instead of current index
    let questionNumber;
    
    // Try to extract question number from question ID first
    if (questionObj.id) {
      const match = questionObj.id.toString().match(/(\d+)/);
      if (match) {
        questionNumber = parseInt(match[1]);
        console.log(`🎯 Using question ID number: ${questionNumber} from ID: ${questionObj.id}`);
      }
    }
    
    // Fallback: use current index + 1 (for normal quiz flow)
    if (!questionNumber) {
      questionNumber = currentIndex + 1;
      console.log(`🔍 Using current index: ${questionNumber} (fallback)`);
    }
    
    const paddedNumber = questionNumber.toString().padStart(2, '0');
    const imagePath = `/question_banks/${selectedBank.id}/images/question_${paddedNumber}_enhanced.png`;
    
    console.log(`🖼️ Generated image path: ${imagePath} (Question ${questionNumber})`);
    return imagePath;
  };

  // Update selection when selectedAnswer prop changes (navigation)
  useEffect(() => {
    setCurrentSelection(selectedAnswer || "");
  }, [selectedAnswer, currentIndex]);

  // Reset image states when question changes
  useEffect(() => {
    setImageError(false);
    setImageLoading(true);
  }, [questionObj.id, currentIndex]);

  // Handle option selection - adapt to your existing onSelect pattern
  const handleOptionSelect = (optionKey) => {
    setCurrentSelection(optionKey);
    if (onSelect) {
      onSelect(questionObj.id, optionKey); // Pass question ID and answer
    }
  };

  // Handle next button - adapt to your existing onAnswer pattern
  const handleNext = () => {
    if (!currentSelection) {
      alert('Please select an answer before continuing.');
      return;
    }
    if (onAnswer) {
      onAnswer(currentSelection); // Your existing pattern
    }
  };

  // Handle previous button
  const handlePrevious = () => {
    if (onBack) {
      onBack();
    }
  };

  // Handle jump to first question
  const handleGoToFirst = () => {
    if (goHome) {
      goHome();
    }
  };

  // Handle jump to last question
  const handleGoToLast = () => {
    console.log('Go to last question - needs implementation in App.jsx');
  };

  // Handle image load events
  const handleImageLoad = () => {
    setImageLoading(false);
    setImageError(false);
    console.log('✅ Image loaded successfully');
  };

  const handleImageError = (e) => {
    setImageLoading(false);
    setImageError(true);
    console.warn(`❌ Failed to load image: ${e.target.src}`);
  };

  // Ensure we have the required data with fallbacks
  const questionText = questionObj.question_text || questionObj.question || 'Question text not available';
  const options = questionObj.options || {};
  
  // 🎯 Use auto-generated image path instead of questionObj.image_url
  const imageUrl = getQuestionImagePath();
  const questionId = questionObj.id || `q_${currentIndex + 1}`;

  const isLastQuestion = currentIndex === total - 1;
  const isFirstQuestion = currentIndex === 0;
  const progress = ((currentIndex + 1) / total) * 100;

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'
    }`}>
      {/* Progress Bar */}
      <div className={darkMode ? 'bg-gray-800 h-2' : 'bg-gray-200 h-2'}>
        <div 
          className="bg-orange-500 h-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="p-6 max-w-4xl mx-auto">
        {/* Header with Home/End buttons */}
        <div className="flex justify-between items-center mb-6">
          {/* Left side - Navigation shortcuts with Dark Mode Toggle */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleGoToFirst}
              disabled={isFirstQuestion}
              className={`
                p-2 rounded-lg transition-colors text-sm
                ${isFirstQuestion
                  ? `${darkMode ? 'text-gray-600' : 'text-gray-400'} cursor-not-allowed`
                  : `${darkMode ? 'text-gray-300 hover:text-white hover:bg-gray-800' : 'text-gray-600 hover:text-black hover:bg-gray-100'}`
                }
              `}
              title="Go to first question"
            >
              🏠 Home
            </button>
            
            <button
              onClick={handleGoToLast}
              disabled={isLastQuestion}
              className={`
                p-2 rounded-lg transition-colors text-sm
                ${isLastQuestion
                  ? `${darkMode ? 'text-gray-600' : 'text-gray-400'} cursor-not-allowed`
                  : `${darkMode ? 'text-gray-300 hover:text-white hover:bg-gray-800' : 'text-gray-600 hover:text-black hover:bg-gray-100'}`
                }
              `}
              title="Go to last question"
            >
              🏁 End
            </button>

            {/* 🌙 Dark Mode Toggle - Beside Home/End buttons */}
            {darkModeToggle}
          </div>

          {/* Center - Question info */}
          <div className="text-center">
            <h2 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-black'}`}>
              Question {currentIndex + 1} of {total}
            </h2>
            <p className={darkMode ? 'text-gray-400' : 'text-gray-600'}>
              {selectedBank?.name} • {questionObj.topic || 'Physics'}
            </p>
          </div>

          {/* Right side - Exit button */}
          <div>
            {goHome && (
              <button
                onClick={goHome}
                className={`transition-colors p-2 rounded-lg ${
                  darkMode 
                    ? 'text-gray-400 hover:text-red-400 hover:bg-gray-800' 
                    : 'text-gray-600 hover:text-red-600 hover:bg-red-50'
                }`}
                title="Exit quiz"
              >
                <span className="text-xl">❌</span>
              </button>
            )}
          </div>
        </div>

        {/* Question Card */}
        <div className={`rounded-xl p-6 mb-6 border transition-colors duration-300 ${
          darkMode 
            ? 'bg-gray-800 border-gray-700' 
            : 'bg-blue-50 border-gray-200'
        }`}>
          {/* 🎯 Always show image section for enhanced PNG files */}
          <div className="mb-6">
            {imageLoading && (
              <div className={`w-full h-64 rounded-lg flex items-center justify-center ${
                darkMode ? 'bg-gray-700' : 'bg-gray-200'
              }`}>
                <div className="text-center">
                  <div className={`animate-spin rounded-full h-8 w-8 border-b-2 mx-auto mb-2 ${
                    darkMode ? 'border-blue-400' : 'border-blue-600'
                  }`}></div>
                  <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Loading question image...
                  </p>
                </div>
              </div>
            )}
            
            {imageError && (
              <div className={`w-full h-64 border rounded-lg flex items-center justify-center ${
                darkMode 
                  ? 'bg-red-900 border-red-700' 
                  : 'bg-red-50 border-red-300'
              }`}>
                <div className={`text-center ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                  <span className="text-2xl mb-2 block">🖼️</span>
                  <p className="text-sm">Failed to load question image</p>
                  <p className="text-xs mt-1">Expected: {imageUrl}</p>
                  <p className="text-xs">Please check if the image file exists</p>
                </div>
              </div>
            )}
            
            {imageUrl && (
              <div className="relative inline-block">
                <img
                  src={imageUrl}
                  alt={`Question ${currentIndex + 1} - Enhanced`}
                  onLoad={handleImageLoad}
                  onError={handleImageError}
                  className={`
                    w-full rounded-lg border shadow-sm
                    ${darkMode ? 'border-gray-600' : 'border-gray-200'}
                    ${imageLoading ? 'hidden' : imageError ? 'hidden' : 'block'}
                  `}
                  style={{ maxHeight: '600px', objectFit: 'contain' }}
                />
                
                {/* 🎯 White overlay to hide question numbers (single & double digit, mobile-friendly) */}
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

          {/* 🎯 Simplified since image contains everything - show only A,B,C,D buttons */}
          <div className="mb-6">
            <div className="text-center mb-4">
              <p className={`text-lg font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                Select your answer:
              </p>
            </div>
            
            {/* Horizontal A,B,C,D Buttons Only */}
            <div className="grid grid-cols-4 gap-4">
              {['A', 'B', 'C', 'D'].map((optionKey) => {
                const isSelected = currentSelection === optionKey;
                
                return (
                  <button
                    key={optionKey}
                    onClick={() => handleOptionSelect(optionKey)}
                    className={`
                      p-6 rounded-lg border-2 transition-all duration-200
                      min-h-[80px] flex items-center justify-center text-center
                      relative group font-bold text-2xl
                      ${isSelected
                        ? 'border-orange-500 bg-orange-500 text-white shadow-lg transform scale-105'
                        : darkMode
                        ? 'border-gray-600 bg-gray-700 text-gray-200 hover:border-orange-500 hover:bg-gray-600 hover:shadow-md'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-orange-500 hover:bg-orange-50 hover:shadow-md'
                      }
                    `}
                  >
                    {optionKey}
                    
                    {/* Selection indicator */}
                    {isSelected && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-white rounded-full flex items-center justify-center border-2 border-orange-500">
                        <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Selection Status */}
          {currentSelection && (
            <div className={`p-3 rounded-lg border ${
              darkMode 
                ? 'bg-green-900 border-green-700' 
                : 'bg-green-100 border-green-300'
            }`}>
              <p className={`font-medium text-center ${
                darkMode ? 'text-green-200' : 'text-black'
              }`}>
                ✓ You selected: <strong>{currentSelection}</strong>
              </p>
            </div>
          )}

          {/* Difficulty Badge */}
          <div className="mt-4 flex justify-center">
            <span className={`
              px-3 py-1 rounded-full text-sm font-medium
              ${questionObj.difficulty === 'easy' 
                ? (darkMode ? 'bg-green-900 text-green-300' : 'bg-green-100 text-green-700') :
                questionObj.difficulty === 'hard' 
                ? (darkMode ? 'bg-red-900 text-red-300' : 'bg-red-100 text-red-700') :
                (darkMode ? 'bg-orange-900 text-orange-300' : 'bg-orange-100 text-orange-700')
              }
            `}>
              {questionObj.difficulty?.charAt(0).toUpperCase() + questionObj.difficulty?.slice(1) || 'Medium'}
            </span>
          </div>
        </div>

        {/* Navigation Row - Separate from question */}
        <div className={`rounded-xl p-4 border shadow-sm transition-colors duration-300 ${
          darkMode 
            ? 'bg-gray-800 border-gray-700' 
            : 'bg-white border-gray-200'
        }`}>
          <div className="flex justify-between items-center">
            <button
              onClick={handlePrevious}
              disabled={isFirstQuestion}
              className={`
                flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
                min-h-[44px] min-w-[120px]
                ${isFirstQuestion
                  ? (darkMode ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-200 text-gray-400 cursor-not-allowed')
                  : (darkMode ? 'bg-gray-600 text-gray-200 hover:bg-gray-500 shadow-sm hover:shadow-md transform hover:scale-105' : 'bg-gray-200 text-black hover:bg-gray-300 active:bg-gray-400 shadow-sm hover:shadow-md transform hover:scale-105')
                }
              `}
            >
              <span className="text-lg">←</span>
              <span>Previous</span>
            </button>

            {/* Center Progress Indicator */}
            <div className="flex flex-col items-center space-y-2">
              <div className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                Progress: {currentIndex + 1} / {total}
              </div>
              <div className={`w-48 rounded-full h-3 ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
                <div 
                  className="bg-orange-500 h-3 rounded-full transition-all duration-300 relative"
                  style={{ width: `${progress}%` }}
                >
                  <div className="absolute right-0 top-0 w-3 h-3 bg-orange-600 rounded-full"></div>
                </div>
              </div>
            </div>

            <button
              onClick={handleNext}
              disabled={!currentSelection}
              className={`
                flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
                min-h-[44px] min-w-[120px]
                ${!currentSelection
                  ? (darkMode ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gray-200 text-gray-400 cursor-not-allowed')
                  : isLastQuestion
                  ? (darkMode ? 'bg-green-700 text-white hover:bg-green-600 shadow-sm hover:shadow-md transform hover:scale-105' : 'bg-green-600 text-white hover:bg-green-700 active:bg-green-800 shadow-sm hover:shadow-md transform hover:scale-105')
                  : (darkMode ? 'bg-blue-700 text-white hover:bg-blue-600 shadow-sm hover:shadow-md transform hover:scale-105' : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-sm hover:shadow-md transform hover:scale-105')
                }
              `}
            >
              <span>{isLastQuestion ? 'Complete Quiz' : 'Next'}</span>
              <span className="text-lg">{isLastQuestion ? '🏆' : '→'}</span>
            </button>
          </div>

          {/* Help Text */}
          {!currentSelection && (
            <div className="mt-3 text-center">
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                💡 Select an answer above, then click Next to continue
              </p>
            </div>
          )}
        </div>

        {/* Question Metadata (for debugging) */}
        {process.env.NODE_ENV === 'development' && (
          <div className={`mt-4 p-4 rounded-lg text-xs ${
            darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-100 text-gray-600'
          }`}>
            <strong>Debug Info:</strong> Question ID: {questionId}, 
            Image Path: {imageUrl || 'None'}, 
            Bank ID: {selectedBank?.id || 'None'},
            Question Number: {currentIndex + 1},
            Confidence: {questionObj.confidence_score || 'N/A'},
            Dark Mode: {darkMode ? 'On' : 'Off'}
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionCard;