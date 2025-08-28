import React, { useState, useEffect, useRef } from 'react';

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
  uiTheme = 'light',
  // FIXED: Use props instead of window functions
  onToggleDarkMode, // Function passed from App.jsx
  onToggleGenAlpha // Function passed from App.jsx
}) => {
  const [currentSelection, setCurrentSelection] = useState(selectedAnswer || "");
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);
  const [questionNumberOverlays, setQuestionNumberOverlays] = useState([]);
  const canvasRef = useRef(null);
  const imageRef = useRef(null);

  // Helper function to get theme-specific classes
  const getThemeClasses = (element) => {
    switch(uiTheme) {
      case 'dark':
        return {
          background: 'bg-gray-900 text-white',
          card: 'bg-gray-800 border-gray-700',
          cardSecondary: 'bg-gray-800 border-gray-700',
          text: 'text-white',
          textSecondary: 'text-gray-300',
          textMuted: 'text-gray-400',
          button: 'bg-blue-700 text-white hover:bg-blue-600',
          buttonSecondary: 'bg-gray-600 text-gray-200 hover:bg-gray-500',
          buttonDisabled: 'bg-gray-700 text-gray-500 cursor-not-allowed',
          border: 'border-gray-600',
          progressBar: 'bg-gray-800',
          spinner: 'border-blue-400',
          overlay: 'bg-gray-700',
        }[element];
      case 'genalpha':
        return {
          background: 'genalpha genalpha-animated text-white',
          card: 'genalpha-card backdrop-blur-xl border-white/20',
          cardSecondary: 'genalpha-card backdrop-blur-xl border-white/20',
          text: 'text-white',
          textSecondary: 'text-white/90',
          textMuted: 'text-white/70',
          button: 'genalpha-button text-white',
          buttonSecondary: 'genalpha-card backdrop-blur-xl border-white/20 text-white hover:bg-white/20',
          buttonDisabled: 'bg-white/10 text-white/50 cursor-not-allowed border border-white/20',
          border: 'border-white/20',
          progressBar: 'bg-white/20',
          spinner: 'border-white',
          overlay: 'bg-white/20 backdrop-blur-xl',
        }[element];
      default: // light
        return {
          background: 'bg-white text-gray-900',
          card: 'bg-blue-50 border-gray-200',
          cardSecondary: 'bg-white border-gray-200',
          text: 'text-black',
          textSecondary: 'text-gray-600',
          textMuted: 'text-gray-600',
          button: 'bg-blue-600 text-white hover:bg-blue-700',
          buttonSecondary: 'bg-gray-200 text-black hover:bg-gray-300',
          buttonDisabled: 'bg-gray-200 text-gray-400 cursor-not-allowed',
          border: 'border-gray-200',
          progressBar: 'bg-gray-200',
          spinner: 'border-blue-600',
          overlay: 'bg-gray-200',
        }[element];
    }
  };

  // FIXED: Create toggle components using the prop functions
  const DarkModeToggle = () => (
    <button
      onClick={onToggleDarkMode}
      className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl ${
        uiTheme === 'dark'
          ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
          : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
      }`}
      title={uiTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      {uiTheme === 'dark' ? '☀️' : '🌙'}
    </button>
  );

  const GenAlphaToggle = () => (
    <button
      onClick={onToggleGenAlpha}
      className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl font-bold text-lg ${
        uiTheme === 'genalpha'
          ? 'genalpha-button text-white hover:scale-110 border-2 border-white/30' 
          : 'bg-white text-purple-600 hover:bg-purple-50 border border-purple-200'
      }`}
      title={uiTheme === 'genalpha' ? 'Switch to Light Mode' : 'Switch to Gen Alpha Mode'}
    >
      α
    </button>
  );

  // Add safety checks to prevent undefined errors
  if (!questionObj) {
    return (
      <div className={`flex items-center justify-center min-h-[400px] transition-colors duration-300 ${getThemeClasses('background')}`}>
        <div className="text-center">
          <div className={`animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4 ${getThemeClasses('spinner')}`}></div>
          <p className={getThemeClasses('textSecondary')}>Loading question...</p>
        </div>
      </div>
    );
  }

  // Auto-generate image path based on question number and bank ID
  const getQuestionImagePath = () => {
    if (!selectedBank?.id) {
      console.warn('No selectedBank.id available for image path');
      return null;
    }
    
    let questionNumber;
    
    // Try to extract question number from question ID first
    if (questionObj.id) {
      const match = questionObj.id.toString().match(/(\d+)/);
      if (match) {
        questionNumber = parseInt(match[1]);
        console.log(`Using question ID number: ${questionNumber} from ID: ${questionObj.id}`);
      }
    }
    
    // Fallback: use current index + 1 (for normal quiz flow)
    if (!questionNumber) {
      questionNumber = currentIndex + 1;
      console.log(`Using current index: ${questionNumber} (fallback)`);
    }
    
    const paddedNumber = questionNumber.toString().padStart(2, '0');
    const imagePath = `/question_banks/${selectedBank.id}/images/question_${paddedNumber}_enhanced.png`;
    
    console.log(`Generated image path: ${imagePath} (Question ${questionNumber})`);
    return imagePath;
  };

  // Dynamic question number detection function
  const detectQuestionNumbers = (imageElement) => {
    if (!canvasRef.current || !imageElement) return [];

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match image
    canvas.width = imageElement.naturalWidth;
    canvas.height = imageElement.naturalHeight;
    
    // Draw image to canvas
    ctx.drawImage(imageElement, 0, 0);
    
    // Get image data
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    
    const overlays = [];
    
    // Focused search area for question numbers - top-left corner
    const searchHeight = Math.min(100, canvas.height * 0.12); // Search top 12% of image
    const searchWidth = Math.min(140, canvas.width * 0.15); // Search left 15% of image
    
    // Look for dark pixels that might be text (question numbers)
    for (let y = 8; y < searchHeight; y += 6) {
      for (let x = 8; x < searchWidth; x += 6) {
        const index = (y * canvas.width + x) * 4;
        const r = data[index];
        const g = data[index + 1];
        const b = data[index + 2];
        
        // Check if pixel is dark (likely text)
        const brightness = (r + g + b) / 3;
        if (brightness < 90) { // Balanced threshold
          // Check for cluster of dark pixels (text area)
          let darkPixelCount = 0;
          const checkRadius = 14;
          
          for (let dy = -checkRadius; dy <= checkRadius; dy += 3) {
            for (let dx = -checkRadius; dx <= checkRadius; dx += 3) {
              const checkX = x + dx;
              const checkY = y + dy;
              if (checkX >= 0 && checkX < canvas.width && checkY >= 0 && checkY < canvas.height) {
                const checkIndex = (checkY * canvas.width + checkX) * 4;
                const checkBrightness = (data[checkIndex] + data[checkIndex + 1] + data[checkIndex + 2]) / 3;
                if (checkBrightness < 90) darkPixelCount++;
              }
            }
          }
          
          // If enough dark pixels found and in the prime question number location
          if (darkPixelCount > 7) {
            // Calculate overlay position and size
            const scaleX = imageElement.offsetWidth / canvas.width;
            const scaleY = imageElement.offsetHeight / canvas.height;
            
            overlays.push({
              left: Math.max(0, (x - 18) * scaleX),
              top: Math.max(0, (y - 14) * scaleY),
              width: 48 * scaleX,
              height: 28 * scaleY
            });
            
            // Skip ahead to avoid multiple overlays for same area
            x += 35;
          }
        }
      }
      // Early exit after finding first overlay to prevent multiple overlays
      if (overlays.length > 0) break;
    }
    
    // Return only the first overlay found (should be the question number)
    return overlays.slice(0, 1);
  };

  // Update selection when selectedAnswer prop changes (navigation)
  useEffect(() => {
    setCurrentSelection(selectedAnswer || "");
  }, [selectedAnswer, currentIndex]);

  // Reset image states when question changes
  useEffect(() => {
    setImageError(false);
    setImageLoading(true);
    setQuestionNumberOverlays([]);
  }, [questionObj.id, currentIndex]);

  // Handle option selection
  const handleOptionSelect = (optionKey) => {
    setCurrentSelection(optionKey);
    if (onSelect) {
      onSelect(questionObj.id, optionKey);
    }
  };

  // Handle next button
  const handleNext = () => {
    if (!currentSelection) {
      alert('Please select an answer before continuing.');
      return;
    }
    if (onAnswer) {
      onAnswer(currentSelection);
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
    console.log('Image loaded successfully');
    
    // Detect question numbers after image loads
    setTimeout(() => {
      if (imageRef.current) {
        const overlays = detectQuestionNumbers(imageRef.current);
        setQuestionNumberOverlays(overlays);
        console.log(`Detected ${overlays.length} question number overlays`);
      }
    }, 100);
  };

  const handleImageError = (e) => {
    setImageLoading(false);
    setImageError(true);
    console.warn(`Failed to load image: ${e.target.src}`);
  };

  // Get required data with fallbacks
  const imageUrl = getQuestionImagePath();
  const questionId = questionObj.id || `q_${currentIndex + 1}`;

  const isLastQuestion = currentIndex === total - 1;
  const isFirstQuestion = currentIndex === 0;
  const progress = ((currentIndex + 1) / total) * 100;

  return (
    <div className={`min-h-screen transition-all duration-500 ${
      uiTheme === 'genalpha' ? 'bg-transparent' : getThemeClasses('background')
    }`}>
      {/* Hidden canvas for image analysis */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      
      {/* Progress Bar */}
      <div className={getThemeClasses('progressBar') + ' h-2'}>
        <div 
          className="bg-orange-500 h-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="p-4 sm:p-6 max-w-4xl mx-auto">
        {/* Header with Home/End buttons and Theme Toggles */}
        <div className="flex justify-between items-center mb-4 sm:mb-6">
          
          {/* Left side - Navigation shortcuts with Theme Toggles */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleGoToFirst}
              disabled={isFirstQuestion}
              className={`
                p-2 rounded-lg transition-colors text-sm
                ${isFirstQuestion
                  ? `${getThemeClasses('textMuted')} cursor-not-allowed`
                  : `${getThemeClasses('textSecondary')} hover:${getThemeClasses('text')} ${uiTheme === 'dark' ? 'hover:bg-gray-800' : uiTheme === 'genalpha' ? 'hover:bg-white/10' : 'hover:bg-gray-100'}`
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
                  ? `${getThemeClasses('textMuted')} cursor-not-allowed`
                  : `${getThemeClasses('textSecondary')} hover:${getThemeClasses('text')} ${uiTheme === 'dark' ? 'hover:bg-gray-800' : uiTheme === 'genalpha' ? 'hover:bg-white/10' : 'hover:bg-gray-100'}`
                }
              `}
              title="Go to last question"
            >
              🔚 End
            </button>

            {/* FIXED: Theme Toggles - Use proper component functions with debugging */}
            {onToggleDarkMode && (
              <button
                onClick={() => {
                  console.log('Dark mode toggle clicked in QuestionCard');
                  onToggleDarkMode();
                }}
                className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl ${
                  uiTheme === 'dark'
                    ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-600' 
                    : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                }`}
                title={uiTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                {uiTheme === 'dark' ? '☀️' : '🌙'}
              </button>
            )}
            {onToggleGenAlpha && (
              <button
                onClick={() => {
                  console.log('Gen Alpha toggle clicked in QuestionCard');
                  onToggleGenAlpha();
                }}
                className={`p-3 rounded-full transition-all duration-300 shadow-lg hover:shadow-xl font-bold text-lg ${
                  uiTheme === 'genalpha'
                    ? 'genalpha-button text-white hover:scale-110 border-2 border-white/30' 
                    : 'bg-white text-purple-600 hover:bg-purple-50 border border-purple-200'
                }`}
                title={uiTheme === 'genalpha' ? 'Switch to Light Mode' : 'Switch to Gen Alpha Mode'}
              >
                α
              </button>
            )}
          </div>

          {/* Center - Question info */}
          <div className="text-center">
            <h2 className={`text-lg sm:text-xl font-semibold ${getThemeClasses('text')}`}>
              Question {currentIndex + 1} of {total}
            </h2>
            <p className={getThemeClasses('textSecondary') + ' text-sm sm:text-base'}>
              {selectedBank?.name} • {questionObj.topic || 'Physics'}
            </p>
          </div>

          {/* Right side - Exit button */}
          <div>
            {goHome && (
              <button
                onClick={goHome}
                className={`transition-colors p-2 rounded-lg ${
                  uiTheme === 'dark'
                    ? 'text-gray-400 hover:text-red-400 hover:bg-gray-800' 
                    : uiTheme === 'genalpha'
                    ? 'text-white/70 hover:text-red-400 hover:bg-white/10'
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
        <div className={`rounded-xl p-4 sm:p-6 mb-4 sm:mb-6 border transition-colors duration-300 ${getThemeClasses('card')}`}>
          
          {/* Image section with dynamic overlays */}
          <div className="mb-6">
            {imageLoading && (
              <div className={`w-full h-48 sm:h-64 rounded-lg flex items-center justify-center ${getThemeClasses('overlay')}`}>
                <div className="text-center">
                  <div className={`animate-spin rounded-full h-8 w-8 border-b-2 mx-auto mb-2 ${getThemeClasses('spinner')}`}></div>
                  <p className={`text-sm ${getThemeClasses('textSecondary')}`}>
                    Loading question image...
                  </p>
                </div>
              </div>
            )}
            
            {imageError && (
              <div className={`w-full h-48 sm:h-64 border rounded-lg flex items-center justify-center ${
                uiTheme === 'dark'
                  ? 'bg-red-900 border-red-700' 
                  : uiTheme === 'genalpha'
                  ? 'bg-red-500/20 border-red-400/30 backdrop-blur-xl'
                  : 'bg-red-50 border-red-300'
              }`}>
                <div className={`text-center ${
                  uiTheme === 'dark'
                    ? 'text-red-400' 
                    : uiTheme === 'genalpha'
                    ? 'text-red-200'
                    : 'text-red-600'
                }`}>
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
                  ref={imageRef}
                  src={imageUrl}
                  alt={`Question ${currentIndex + 1} - Enhanced`}
                  onLoad={handleImageLoad}
                  onError={handleImageError}
                  className={`
                    w-full rounded-lg border shadow-sm
                    ${getThemeClasses('border')}
                    ${imageLoading ? 'hidden' : imageError ? 'hidden' : 'block'}
                  `}
                  style={{ maxHeight: '600px', objectFit: 'contain' }}
                />
                
                {/* Dynamic question number overlays */}
                {questionNumberOverlays.map((overlay, index) => (
                  <div 
                    key={index}
                    className="absolute bg-white rounded-sm shadow-sm select-none pointer-events-none"
                    style={{
                      left: `${overlay.left}px`,
                      top: `${overlay.top}px`,
                      width: `${overlay.width}px`,
                      height: `${overlay.height}px`
                    }}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Answer selection */}
          <div className="mb-6">
            <div className="text-center mb-4">
              <p className={`text-base sm:text-lg font-medium ${getThemeClasses('textSecondary')}`}>
                Select your answer:
              </p>
            </div>
            
            {/* Horizontal A,B,C,D Buttons - Same size as Next/Previous */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
              {['A', 'B', 'C', 'D'].map((optionKey) => {
                const isSelected = currentSelection === optionKey;
                
                return (
                  <button
                    key={optionKey}
                    onClick={() => handleOptionSelect(optionKey)}
                    className={`
                      px-4 py-3 sm:px-6 sm:py-3 rounded-lg border-2 transition-all duration-200
                      min-h-[44px] min-w-[120px] flex items-center justify-center text-center
                      relative group font-bold text-xl sm:text-2xl
                      ${isSelected
                        ? 'border-orange-500 bg-orange-500 text-white shadow-lg transform scale-105'
                        : uiTheme === 'dark'
                        ? 'border-gray-600 bg-gray-700 text-gray-200 hover:border-orange-500 hover:bg-gray-600 hover:shadow-md'
                        : uiTheme === 'genalpha'
                        ? 'border-white/20 bg-white/10 text-white hover:border-white/40 hover:bg-white/20 hover:shadow-md backdrop-blur-xl'
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
              uiTheme === 'dark'
                ? 'bg-green-900 border-green-700' 
                : uiTheme === 'genalpha'
                ? 'status-success backdrop-blur-xl border-green-400/30'
                : 'bg-green-100 border-green-300'
            }`}>
              <p className={`font-medium text-center ${
                uiTheme === 'dark'
                  ? 'text-green-200' 
                  : uiTheme === 'genalpha'
                  ? 'text-white'
                  : 'text-black'
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
                ? (uiTheme === 'dark' 
                  ? 'bg-green-900 text-green-300' 
                  : uiTheme === 'genalpha'
                  ? 'status-success text-white'
                  : 'bg-green-100 text-green-700') :
                questionObj.difficulty === 'hard' 
                ? (uiTheme === 'dark' 
                  ? 'bg-red-900 text-red-300' 
                  : uiTheme === 'genalpha'
                  ? 'status-error text-white'
                  : 'bg-red-100 text-red-700') :
                (uiTheme === 'dark' 
                  ? 'bg-orange-900 text-orange-300' 
                  : uiTheme === 'genalpha'
                  ? 'status-warning text-black'
                  : 'bg-orange-100 text-orange-700')
              }
            `}>
              {questionObj.difficulty?.charAt(0).toUpperCase() + questionObj.difficulty?.slice(1) || 'Medium'}
            </span>
          </div>
        </div>

        {/* Navigation Row - Separate from question */}
        <div className={`rounded-xl p-4 border shadow-sm transition-colors duration-300 ${getThemeClasses('cardSecondary')}`}>
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <button
              onClick={handlePrevious}
              disabled={isFirstQuestion}
              className={`
                flex items-center space-x-2 px-4 sm:px-6 py-3 rounded-lg font-medium transition-all duration-200
                min-h-[44px] min-w-[120px] w-full sm:w-auto
                ${isFirstQuestion
                  ? getThemeClasses('buttonDisabled')
                  : getThemeClasses('buttonSecondary') + ' shadow-sm hover:shadow-md transform hover:scale-105'
                }
              `}
            >
              <span className="text-lg">←</span>
              <span>Previous</span>
            </button>

            {/* Center Progress Indicator */}
            <div className="flex flex-col items-center space-y-2">
              <div className={`text-sm font-medium ${getThemeClasses('textSecondary')}`}>
                Progress: {currentIndex + 1} / {total}
              </div>
              <div className={`w-48 rounded-full h-3 ${getThemeClasses('progressBar')}`}>
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
                flex items-center space-x-2 px-4 sm:px-6 py-3 rounded-lg font-medium transition-all duration-200
                min-h-[44px] min-w-[120px] w-full sm:w-auto
                ${!currentSelection
                  ? getThemeClasses('buttonDisabled')
                  : isLastQuestion
                  ? (uiTheme === 'dark'
                    ? 'bg-green-700 text-white hover:bg-green-600 shadow-sm hover:shadow-md transform hover:scale-105' 
                    : uiTheme === 'genalpha'
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 shadow-sm hover:shadow-md transform hover:scale-105'
                    : 'bg-green-600 text-white hover:bg-green-700 active:bg-green-800 shadow-sm hover:shadow-md transform hover:scale-105')
                  : getThemeClasses('button') + ' shadow-sm hover:shadow-md transform hover:scale-105'
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
              <p className={`text-sm ${getThemeClasses('textSecondary')}`}>
                💡 Select an answer above, then click Next to continue
              </p>
            </div>
          )}
        </div>

        {/* Question Metadata (for debugging) */}
        {process.env.NODE_ENV === 'development' && (
          <div className={`mt-4 p-4 rounded-lg text-xs ${getThemeClasses('cardSecondary')} ${getThemeClasses('textMuted')}`}>
            <strong>Debug Info:</strong> Question ID: {questionId}, 
            Image Path: {imageUrl || 'None'}, 
            Bank ID: {selectedBank?.id || 'None'},
            Question Number: {currentIndex + 1},
            Confidence: {questionObj.confidence_score || 'N/A'},
            UI Theme: {uiTheme},
            Overlays Detected: {questionNumberOverlays.length}
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionCard;