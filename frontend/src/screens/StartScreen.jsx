// ==============================
// StartScreen.jsx - Enhanced with Subject Organization + Dark Mode + Logo + Labubu GIF
// ==============================

import React, { useState, useEffect } from 'react';
import { getAvailableSubjects, getBanksForSubject } from '../services/questionService';
// Import your logo and labubu gif
import axcelLogo from '../assets/axcel-logo.png';
import labubuGif from '../assets/labubu.gif';

const StartScreen = ({ 
  onStart, 
  selectedBank, 
  onBankSelect, 
  uiTheme = 'light' // Only need uiTheme prop
}) => {
  // Convert uiTheme to boolean flags for existing logic compatibility
  const isDarkMode = uiTheme === 'dark';
  const isGenAlpha = uiTheme === 'genalpha';

  // All existing state - UNCHANGED
  const [subjects, setSubjects] = useState({});
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [subjectBanks, setSubjectBanks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // New state for question count and multi-select banks
  const [questionCount, setQuestionCount] = useState(5);
  const [selectedBanks, setSelectedBanks] = useState([]);

  // All existing functions - UNCHANGED
  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Loading available subjects...');
      const availableSubjects = await getAvailableSubjects();
      
      console.log('Subjects loaded:', Object.keys(availableSubjects));
      setSubjects(availableSubjects);
      
      // Auto-select first subject if available
      const subjectNames = Object.keys(availableSubjects);
      if (subjectNames.length > 0) {
        const firstSubject = subjectNames[0];
        setSelectedSubject(firstSubject);
        await loadBanksForSubject(firstSubject);
      }
      
    } catch (error) {
      console.error('Failed to load subjects:', error);
      setError('Failed to load subjects');
    } finally {
      setLoading(false);
    }
  };

  const loadBanksForSubject = async (subject) => {
    try {
      console.log(`Loading banks for ${subject}...`);
      const banks = await getBanksForSubject(subject);
      
      console.log(`Found ${banks.length} banks for ${subject}`);
      setSubjectBanks(banks);
      
      // Auto-select all banks by default
      setSelectedBanks(banks);
      
    } catch (error) {
      console.error(`Failed to load banks for ${subject}:`, error);
      setSubjectBanks([]);
      setSelectedBanks([]);
    }
  };

  const handleSubjectChange = async (subject) => {
    setSelectedSubject(subject);
    setSubjectBanks([]);
    setSelectedBanks([]);
    
    await loadBanksForSubject(subject);
  };

  const handleBankToggle = (bank) => {
    setSelectedBanks(prev => {
      const isSelected = prev.some(b => b.id === bank.id);
      if (isSelected) {
        return prev.filter(b => b.id !== bank.id);
      } else {
        return [...prev, bank];
      }
    });
  };

  const handleSelectAllBanks = () => {
    setSelectedBanks(subjectBanks);
  };

  const handleDeselectAllBanks = () => {
    setSelectedBanks([]);
  };

  const handleStart = () => {
    if (selectedBanks.length === 0) {
      alert('Please select at least one question bank');
      return;
    }
    
    console.log('Starting quiz with:', selectedBanks.length, 'banks, Questions:', questionCount);
    onStart(questionCount, selectedBanks); // Pass question count and selected banks to parent
  };

  // UPDATED STYLING HELPERS - Enhanced for Gen Alpha support
  const getGradientClass = (fromColor, toColor) => {
    if (isGenAlpha) {
      // Use inline styles for Gen Alpha animated gradient
      return 'min-h-screen';
    }
    if (isDarkMode) {
      return `bg-gradient-to-br from-gray-800 to-gray-900`;
    }
    return `bg-gradient-to-br from-${fromColor} to-${toColor}`;
  };

  const getCardClass = (additionalClasses = '') => {
    const baseClasses = `rounded-lg shadow-lg p-6 transition-colors duration-300 ${additionalClasses}`;
    if (isGenAlpha) {
      return `${baseClasses} bg-white/15 backdrop-blur-xl border border-white/20`;
    }
    if (isDarkMode) {
      return `${baseClasses} bg-gray-800 border border-gray-700`;
    }
    return `${baseClasses} bg-white`;
  };

  const getTextClass = (textType = 'body') => {
    if (isGenAlpha) {
      switch (textType) {
        case 'heading': return 'text-white';
        case 'subheading': return 'text-white/90';
        case 'body': return 'text-white/80';
        case 'muted': return 'text-white/70';
        default: return 'text-white/80';
      }
    }
    if (isDarkMode) {
      switch (textType) {
        case 'heading': return 'text-white';
        case 'subheading': return 'text-gray-200';
        case 'body': return 'text-gray-300';
        case 'muted': return 'text-gray-400';
        default: return 'text-gray-300';
      }
    } else {
      switch (textType) {
        case 'heading': return 'text-gray-800';
        case 'subheading': return 'text-gray-700';
        case 'body': return 'text-gray-600';
        case 'muted': return 'text-gray-500';
        default: return 'text-gray-600';
      }
    }
  };

  // Gen Alpha background style
  const genAlphaStyle = isGenAlpha ? {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%)',
    backgroundSize: '400% 400%',
    animation: 'gradientShift 8s ease infinite'
  } : {};

  // Loading state - ENHANCED with Gen Alpha support and Labubu
  if (loading) {
    return (
      <div className={`min-h-screen p-4 ${getGradientClass('blue-50', 'indigo-100')}`} style={genAlphaStyle}>
        <div className="max-w-2xl mx-auto pt-20">
          <div className="text-center">
            {/* Logo and Labubu in loading screen */}
            <div className="mb-8">
              <div className="flex justify-center items-center gap-4 mb-4">
                <div className={`inline-block p-3 rounded-full shadow-lg ${
                  isGenAlpha 
                    ? 'bg-white/15 backdrop-blur-xl border border-white/20'
                    : isDarkMode 
                    ? 'bg-gray-700/80' 
                    : 'bg-white/90'
                } backdrop-blur-sm`}>
                  <img 
                    src={axcelLogo} 
                    alt="Axcel Logo" 
                    className="h-16 w-auto opacity-80"
                  />
                </div>
                <img 
                  src={labubuGif} 
                  alt="Labubu" 
                  className="h-16 w-auto rounded-lg shadow-lg opacity-90"
                />
              </div>
            </div>
            
            <div className={`animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4 ${
              isGenAlpha ? 'border-white border-t-transparent' :
              isDarkMode ? 'border-blue-400 border-t-transparent' : ''
            }`}></div>
            <h2 className={`text-xl font-semibold ${getTextClass('subheading')}`}>
              Loading Question Banks...
            </h2>
          </div>
        </div>
      </div>
    );
  }

  // Error state - ENHANCED with Gen Alpha support and Labubu
  if (error) {
    return (
      <div className={`min-h-screen p-4 ${getGradientClass('red-50', 'pink-100')}`} style={genAlphaStyle}>
        <div className="max-w-2xl mx-auto pt-20">
          <div className="text-center">
            {/* Logo and Labubu in error screen */}
            <div className="mb-8">
              <div className="flex justify-center items-center gap-4 mb-4">
                <div className={`inline-block p-3 rounded-full shadow-lg ${
                  isGenAlpha
                    ? 'bg-red-500/20 backdrop-blur-xl border border-red-400/30'
                    : isDarkMode 
                    ? 'bg-red-900/60' 
                    : 'bg-white/90'
                } backdrop-blur-sm`}>
                  <img 
                    src={axcelLogo} 
                    alt="Axcel Logo" 
                    className="h-16 w-auto opacity-60"
                  />
                </div>
                <img 
                  src={labubuGif} 
                  alt="Labubu" 
                  className="h-16 w-auto rounded-lg shadow-lg opacity-70 grayscale"
                />
              </div>
            </div>
            
            <div className="text-6xl mb-4">âŒ</div>
            <h2 className={`text-xl font-semibold mb-2 ${
              isGenAlpha ? 'text-red-200' :
              isDarkMode ? 'text-red-400' : 'text-red-700'
            }`}>
              Error Loading Question Banks
            </h2>
            <p className={`mb-4 ${
              isGenAlpha ? 'text-red-200' :
              isDarkMode ? 'text-red-300' : 'text-red-600'
            }`}>{error}</p>
            <button 
              onClick={loadSubjects}
              className={`px-6 py-2 rounded-lg transition-colors ${
                isGenAlpha
                  ? 'bg-red-500/80 hover:bg-red-600/80 text-white backdrop-blur-xl'
                  : isDarkMode
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const subjectNames = Object.keys(subjects);
  const hasAnyBanks = subjectNames.some(subject => subjects[subject].count > 0);

  // No subjects at all - ENHANCED with Gen Alpha support and Labubu
  if (subjectNames.length === 0) {
    return (
      <div className={`min-h-screen p-4 ${getGradientClass('gray-50', 'gray-100')}`} style={genAlphaStyle}>
        <div className="max-w-2xl mx-auto pt-20">
          <div className="text-center">
            {/* Logo and Labubu in no subjects screen */}
            <div className="mb-8">
              <div className="flex justify-center items-center gap-4 mb-4">
                <div className={`inline-block p-3 rounded-full shadow-lg ${
                  isGenAlpha
                    ? 'bg-white/15 backdrop-blur-xl border border-white/20'
                    : isDarkMode 
                    ? 'bg-gray-700/80' 
                    : 'bg-white/90'
                } backdrop-blur-sm`}>
                  <img 
                    src={axcelLogo} 
                    alt="Axcel Logo" 
                    className="h-20 w-auto"
                  />
                </div>
                <img 
                  src={labubuGif} 
                  alt="Labubu" 
                  className="h-20 w-auto rounded-lg shadow-lg"
                />
              </div>
            </div>
            
            <div className="text-6xl mb-4">📁</div>
            <h2 className={`text-2xl font-bold mb-2 ${getTextClass('heading')}`}>
              No Question Banks Found
            </h2>
            <p className={`mb-6 ${getTextClass('body')}`}>
              No question bank folders were detected. Please add question banks to the following directory:
            </p>
            <div className={`p-4 rounded-lg text-left text-sm font-mono mb-6 ${
              isGenAlpha
                ? 'bg-white/15 backdrop-blur-xl border border-white/20 text-white'
                : isDarkMode 
                ? 'bg-gray-800 text-gray-300' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              public/question_banks/[subject]/[question_file].json
            </div>
            <p className={`text-sm ${getTextClass('muted')}`}>
              Example: public/question_banks/physics/physics_2023_oct_13.json
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Has subjects but no banks - ENHANCED with Gen Alpha support and Labubu
  if (!hasAnyBanks) {
    return (
      <div className={`min-h-screen p-4 ${getGradientClass('yellow-50', 'orange-100')}`} style={genAlphaStyle}>
        <div className="max-w-2xl mx-auto pt-20">
          <div className="text-center">
            {/* Logo and Labubu in no banks screen */}
            <div className="mb-8">
              <div className="flex justify-center items-center gap-4 mb-4">
                <div className={`inline-block p-3 rounded-full shadow-lg ${
                  isGenAlpha
                    ? 'bg-orange-500/20 backdrop-blur-xl border border-orange-400/30'
                    : isDarkMode 
                    ? 'bg-orange-900/60' 
                    : 'bg-white/90'
                } backdrop-blur-sm`}>
                  <img 
                    src={axcelLogo} 
                    alt="Axcel Logo" 
                    className="h-20 w-auto"
                  />
                </div>
                <img 
                  src={labubuGif} 
                  alt="Labubu" 
                  className="h-20 w-auto rounded-lg shadow-lg"
                />
              </div>
            </div>
            
            <div className="text-6xl mb-4">📚</div>
            <h2 className={`text-2xl font-bold mb-2 ${getTextClass('heading')}`}>
              No Question Banks Available
            </h2>
            <p className={`mb-6 ${getTextClass('body')}`}>
              Found {subjectNames.length} subject folder(s), but no valid question banks inside them.
            </p>
            
            <div className={getCardClass('mb-6')}>
              <h3 className={`font-semibold mb-3 ${getTextClass('subheading')}`}>
                Detected Subjects:
              </h3>
              <div className="space-y-2">
                {subjectNames.map(subject => (
                  <div key={subject} className="flex justify-between items-center">
                    <span className={`capitalize font-medium ${getTextClass('body')}`}>
                      {subject}
                    </span>
                    <span className={`text-sm ${
                      isGenAlpha ? 'text-red-200' :
                      isDarkMode ? 'text-red-400' : 'text-red-500'
                    }`}>
                      0 question banks
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <p className={`text-sm ${getTextClass('muted')}`}>
              Add JSON question bank files to any subject folder to get started.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Main screen - ENHANCED with Gen Alpha support, existing functionality, and Labubu
  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isGenAlpha ? '' : isDarkMode ? 'bg-gray-900 text-white' : getGradientClass('blue-50', 'indigo-100')
    }`} style={genAlphaStyle}>
      {/* Mobile-First Container - Yellow Box Area */}
      <div className="p-4 sm:p-6 lg:p-8">
        <div className="max-w-4xl mx-auto pt-8 sm:pt-12">
          {/* Header with Logo and Labubu - ENHANCED */}
          <div className="text-center mb-8">
            {/* Logo and Labubu with enhanced background for all themes */}
            <div className="mb-6">
              <div className="flex justify-center items-center gap-4 sm:gap-6 mb-4">
                {/* Axcel Logo */}
                <div className={`inline-block p-3 rounded-full shadow-lg transition-all duration-300 hover:scale-105 ${
                  isGenAlpha
                    ? 'bg-white/15 backdrop-blur-xl border border-white/20'
                    : isDarkMode 
                    ? 'bg-gray-700/80 border border-gray-600' 
                    : 'bg-white/90 border border-gray-200'
                } backdrop-blur-sm`}>
                  <img 
                    src={axcelLogo} 
                    alt="Axcel Logo" 
                    className="h-16 sm:h-20 w-auto transition-transform duration-300 hover:scale-105"
                  />
                </div>
                
                {/* Labubu GIF */}
                <div className="relative">
                  <img 
                    src={labubuGif} 
                    alt="Labubu" 
                    className={`h-16 sm:h-20 w-auto rounded-lg shadow-lg transition-all duration-300 hover:scale-105 ${
                      isGenAlpha
                        ? 'ring-2 ring-white/30'
                        : isDarkMode
                        ? 'ring-2 ring-gray-600'
                        : 'ring-2 ring-gray-200'
                    }`}
                  />
                  {/* Optional cute floating badge */}
                  <div className={`absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                    isGenAlpha
                      ? 'bg-pink-500/80 text-white backdrop-blur-sm'
                      : isDarkMode
                      ? 'bg-pink-600 text-white'
                      : 'bg-pink-500 text-white'
                  } shadow-lg`}>
                    💖
                  </div>
                </div>
              </div>
            </div>
            
            <h1 className={`text-3xl sm:text-4xl font-bold mb-2 ${getTextClass('heading')}`}>
               AxcelScore Practice 
            </h1>
            <p className={`${getTextClass('body')} px-4 sm:px-0`}>
              Select a subject and question bank to begin your practice session
            </p>
          </div>

          {/* Subject Selection - Mobile-Optimized */}
          <div className={getCardClass('mb-6')}>
            <h2 className={`text-lg sm:text-xl font-semibold mb-4 ${getTextClass('subheading')}`}>
              📚 Select Subject
            </h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {subjectNames.map(subject => {
                const subjectData = subjects[subject];
                const isSelected = selectedSubject === subject;
                const hasQuestions = subjectData.count > 0;
                
                return (
                  <button
                    key={subject}
                    onClick={() => hasQuestions && handleSubjectChange(subject)}
                    disabled={!hasQuestions}
                    className={`p-3 sm:p-4 rounded-lg border-2 transition-all text-left ${
                      isSelected && hasQuestions
                        ? isGenAlpha
                          ? 'border-white/60 bg-white/20 text-white backdrop-blur-sm'
                          : isDarkMode
                          ? 'border-blue-400 bg-blue-900 text-blue-200'
                          : 'border-blue-500 bg-blue-50 text-blue-700'
                        : hasQuestions
                        ? isGenAlpha
                          ? 'border-white/20 bg-white/10 hover:border-white/40 hover:bg-white/20 text-white backdrop-blur-sm'
                          : isDarkMode
                          ? 'border-gray-600 bg-gray-700 hover:border-blue-400 hover:bg-blue-900 text-gray-200'
                          : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50 text-gray-800'
                        : isGenAlpha
                        ? 'border-white/20 bg-white/5 text-white/50 cursor-not-allowed'
                        : isDarkMode
                        ? 'border-gray-700 bg-gray-800 text-gray-500 cursor-not-allowed'
                        : 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    <div className="text-base sm:text-lg font-semibold capitalize">{subject}</div>
                    <div className="text-sm mt-1">
                      {hasQuestions ? (
                        <span className={
                          isGenAlpha ? 'text-green-200' :
                          isDarkMode ? 'text-green-400' : 'text-green-600'
                        }>
                          {subjectData.count} question banks
                        </span>
                      ) : (
                        <span className={
                          isGenAlpha ? 'text-red-200' :
                          isDarkMode ? 'text-red-400' : 'text-red-500'
                        }>
                          No questions available
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Number of Questions Selection */}
          {selectedSubject && (
            <div className={getCardClass('mb-6')}>
              <h2 className={`text-lg sm:text-xl font-semibold mb-4 ${getTextClass('subheading')}`}>
                📊 Number of Questions
              </h2>
              <select
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                className={`w-full p-3 rounded-lg border-2 text-base font-medium transition-all ${
                  isGenAlpha
                    ? 'bg-white/10 border-white/20 text-white backdrop-blur-xl hover:border-white/40 focus:border-white/60'
                    : isDarkMode
                    ? 'bg-gray-700 border-gray-600 text-gray-200 hover:border-blue-400 focus:border-blue-400'
                    : 'bg-white border-gray-300 text-gray-800 hover:border-blue-500 focus:border-blue-500'
                } focus:outline-none focus:ring-0`}
              >
                <option value={5}>5 Questions (Quick Practice)</option>
                <option value={10}>10 Questions (Standard)</option>
                <option value={40}>40 Questions (Full Test)</option>
              </select>
            </div>
          )}

          {/* Question Bank Multi-Selection - Mobile-Optimized */}
          {selectedSubject && subjectBanks.length > 0 && (
            <div className={getCardClass('mb-6')}>
              <div className="flex justify-between items-center mb-4">
                <h2 className={`text-lg sm:text-xl font-semibold ${getTextClass('subheading')}`}>
                  📄 Select Question Banks - {selectedSubject}
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={handleSelectAllBanks}
                    className={`px-3 py-1 text-xs rounded transition-colors ${
                      isGenAlpha
                        ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white'
                        : isDarkMode
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-blue-500 hover:bg-blue-600 text-white'
                    }`}
                  >
                    Select All
                  </button>
                  <button
                    onClick={handleDeselectAllBanks}
                    className={`px-3 py-1 text-xs rounded transition-colors ${
                      isGenAlpha
                        ? 'bg-white/20 hover:bg-white/30 text-white backdrop-blur-sm'
                        : isDarkMode
                        ? 'bg-gray-600 hover:bg-gray-700 text-white'
                        : 'bg-gray-500 hover:bg-gray-600 text-white'
                    }`}
                  >
                    Clear All
                  </button>
                </div>
              </div>
              
              <div className="space-y-3">
                {subjectBanks.map(bank => {
                  const isSelected = selectedBanks.some(b => b.id === bank.id);
                  
                  return (
                    <button
                      key={bank.id}
                      onClick={() => handleBankToggle(bank)}
                      className={`w-full p-3 sm:p-4 rounded-lg border-2 text-left transition-all ${
                        isSelected
                          ? isGenAlpha
                            ? 'border-green-400/60 bg-green-500/20 backdrop-blur-xl'
                            : isDarkMode
                            ? 'border-green-400 bg-green-900'
                            : 'border-green-500 bg-green-50'
                          : isGenAlpha
                          ? 'border-white/20 bg-white/10 hover:border-green-400/40 hover:bg-green-500/20 backdrop-blur-xl'
                          : isDarkMode
                          ? 'border-gray-600 bg-gray-700 hover:border-green-400 hover:bg-green-900'
                          : 'border-gray-200 bg-white hover:border-green-300 hover:bg-green-50'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1 min-w-0">
                          <h3 className={`font-semibold text-sm sm:text-base ${getTextClass('heading')}`}>
                            {bank.name}
                          </h3>
                          <p className={`text-xs sm:text-sm mt-1 ${getTextClass('body')} truncate`}>
                            {bank.description}
                          </p>
                          <div className={`flex flex-wrap gap-2 sm:gap-4 mt-2 text-xs ${getTextClass('muted')}`}>
                            <span>📅 {bank.session} {bank.year}</span>
                            <span>📄 Paper {bank.paper_number}</span>
                            <span>📊 {bank.estimatedCount} questions</span>
                          </div>
                        </div>
                        
                        <div className={`text-lg sm:text-xl ml-2 ${
                          isSelected 
                            ? isGenAlpha 
                              ? 'text-green-200'
                              : isDarkMode 
                              ? 'text-green-400' 
                              : 'text-green-500'
                            : isGenAlpha
                            ? 'text-white/40'
                            : isDarkMode 
                            ? 'text-gray-600' 
                            : 'text-gray-400'
                        }`}>
                          {isSelected ? 'âœ…' : 'â˜'}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
              
              <div className={`mt-4 p-3 rounded-lg ${
                isGenAlpha
                  ? 'bg-white/10 backdrop-blur-xl border border-white/20'
                  : isDarkMode 
                  ? 'bg-gray-700' 
                  : 'bg-gray-50'
              }`}>
                <p className={`text-sm ${getTextClass('body')}`}>
                  <strong>{selectedBanks.length}</strong> of <strong>{subjectBanks.length}</strong> question banks selected
                  {selectedBanks.length > 0 && (
                    <span className={`ml-2 ${getTextClass('muted')}`}>
                      (Total: {selectedBanks.reduce((sum, bank) => sum + bank.estimatedCount, 0)} questions available)
                    </span>
                  )}
                </p>
              </div>
            </div>
          )}

          {/* Start Button */}
          {selectedSubject && selectedBanks.length > 0 && (
            <div className="text-center pb-8">
              <button
                onClick={handleStart}
                className={`w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 text-lg sm:text-xl font-semibold rounded-lg transition-all shadow-lg hover:shadow-xl ${
                  isGenAlpha
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white backdrop-blur-xl'
                    : isDarkMode
                    ? 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white'
                    : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white'
                }`}
              >
                🚀 Start {questionCount} Question Quiz
              </button>
              
              <p className={`text-sm mt-3 ${getTextClass('body')} px-4 sm:px-0`}>
                Ready to start {questionCount} random questions from {selectedBanks.length} selected bank(s)
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StartScreen;