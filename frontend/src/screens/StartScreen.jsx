// ==============================
// 📱 StartScreen.jsx - Enhanced with Subject Organization + Dark Mode + Logo
// ==============================

import React, { useState, useEffect } from 'react';
import { getAvailableSubjects, getBanksForSubject } from '../services/questionService';
// 🎯 Import your logo
import axcelLogo from '../assets/axcel-logo.png';

const StartScreen = ({ onStart, selectedBank, onBankSelect, darkMode = false, toggleDarkMode }) => {
  // All existing state - UNCHANGED
  const [subjects, setSubjects] = useState({});
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [subjectBanks, setSubjectBanks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // All existing functions - UNCHANGED
  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('📚 Loading available subjects...');
      const availableSubjects = await getAvailableSubjects();
      
      console.log('✅ Subjects loaded:', Object.keys(availableSubjects));
      setSubjects(availableSubjects);
      
      // Auto-select first subject if available
      const subjectNames = Object.keys(availableSubjects);
      if (subjectNames.length > 0) {
        const firstSubject = subjectNames[0];
        setSelectedSubject(firstSubject);
        await loadBanksForSubject(firstSubject);
      }
      
    } catch (error) {
      console.error('❌ Failed to load subjects:', error);
      setError('Failed to load subjects');
    } finally {
      setLoading(false);
    }
  };

  const loadBanksForSubject = async (subject) => {
    try {
      console.log(`📚 Loading banks for ${subject}...`);
      const banks = await getBanksForSubject(subject);
      
      console.log(`✅ Found ${banks.length} banks for ${subject}`);
      setSubjectBanks(banks);
      
      // Auto-select first bank if available
      if (banks.length > 0 && !selectedBank) {
        onBankSelect(banks[0]);
      }
      
    } catch (error) {
      console.error(`❌ Failed to load banks for ${subject}:`, error);
      setSubjectBanks([]);
    }
  };

  const handleSubjectChange = async (subject) => {
    setSelectedSubject(subject);
    setSubjectBanks([]);
    onBankSelect(null); // Clear selected bank
    
    await loadBanksForSubject(subject);
  };

  const handleBankSelect = (bank) => {
    console.log('🎯 Bank selected:', bank.name);
    onBankSelect(bank);
  };

  const handleStart = () => {
    if (!selectedBank) {
      alert('Please select a question bank first');
      return;
    }
    
    console.log('🚀 Starting quiz with:', selectedBank.name);
    onStart();
  };

  // 🌙 DARK MODE STYLING HELPERS - New addition
  const getGradientClass = (fromColor, toColor) => {
    if (darkMode) {
      return `bg-gradient-to-br from-gray-800 to-gray-900`;
    }
    return `bg-gradient-to-br from-${fromColor} to-${toColor}`;
  };

  const getCardClass = (additionalClasses = '') => {
    const baseClasses = `rounded-lg shadow-lg p-6 transition-colors duration-300 ${additionalClasses}`;
    if (darkMode) {
      return `${baseClasses} bg-gray-800 border border-gray-700`;
    }
    return `${baseClasses} bg-white`;
  };

  const getTextClass = (textType = 'body') => {
    if (darkMode) {
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

  // Loading state - ENHANCED with dark mode + logo
  if (loading) {
    return (
      <div className={`min-h-screen p-4 ${getGradientClass('blue-50', 'indigo-100')}`}>
        {/* Dark Mode Toggle - Fixed Position */}
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

        <div className="max-w-2xl mx-auto pt-20">
          <div className="text-center">
            {/* 🎯 Logo in loading screen */}
            <div className="mb-8">
              <div className={`inline-block p-3 rounded-full mb-4 shadow-lg ${
                darkMode ? 'bg-gray-700/80' : 'bg-white/90'
              } backdrop-blur-sm`}>
                <img 
                  src={axcelLogo} 
                  alt="Axcel Logo" 
                  className="h-16 w-auto opacity-80"
                />
              </div>
            </div>
            
            <div className={`animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4 ${
              darkMode ? 'border-blue-400 border-t-transparent' : ''
            }`}></div>
            <h2 className={`text-xl font-semibold ${getTextClass('subheading')}`}>
              Loading Question Banks...
            </h2>
          </div>
        </div>
      </div>
    );
  }

  // Error state - ENHANCED with dark mode + logo
  if (error) {
    return (
      <div className={`min-h-screen p-4 ${getGradientClass('red-50', 'pink-100')}`}>
        {/* Dark Mode Toggle - Fixed Position */}
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

        <div className="max-w-2xl mx-auto pt-20">
          <div className="text-center">
            {/* 🎯 Logo in error screen */}
            <div className="mb-8">
              <div className={`inline-block p-3 rounded-full mb-4 shadow-lg ${
                darkMode ? 'bg-red-900/60' : 'bg-white/90'
              } backdrop-blur-sm`}>
                <img 
                  src={axcelLogo} 
                  alt="Axcel Logo" 
                  className="h-16 w-auto opacity-60"
                />
              </div>
            </div>
            
            <div className="text-6xl mb-4">❌</div>
            <h2 className={`text-xl font-semibold mb-2 ${darkMode ? 'text-red-400' : 'text-red-700'}`}>
              Error Loading Question Banks
            </h2>
            <p className={`mb-4 ${darkMode ? 'text-red-300' : 'text-red-600'}`}>{error}</p>
            <button 
              onClick={loadSubjects}
              className={`px-6 py-2 rounded-lg transition-colors ${
                darkMode 
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

  // No subjects at all - ENHANCED with dark mode + logo
  if (subjectNames.length === 0) {
    return (
      <div className={`min-h-screen p-4 ${getGradientClass('gray-50', 'gray-100')}`}>
        {/* Dark Mode Toggle - Fixed Position */}
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

        <div className="max-w-2xl mx-auto pt-20">
          <div className="text-center">
            {/* 🎯 Logo in no subjects screen */}
            <div className="mb-8">
              <div className={`inline-block p-3 rounded-full mb-4 shadow-lg ${
                darkMode ? 'bg-gray-700/80' : 'bg-white/90'
              } backdrop-blur-sm`}>
                <img 
                  src={axcelLogo} 
                  alt="Axcel Logo" 
                  className="h-20 w-auto"
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
              darkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-800'
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

  // Has subjects but no banks - ENHANCED with dark mode + logo
  if (!hasAnyBanks) {
    return (
      <div className={`min-h-screen p-4 ${getGradientClass('yellow-50', 'orange-100')}`}>
        {/* Dark Mode Toggle - Fixed Position */}
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

        <div className="max-w-2xl mx-auto pt-20">
          <div className="text-center">
            {/* 🎯 Logo in no banks screen */}
            <div className="mb-8">
              <div className={`inline-block p-3 rounded-full mb-4 shadow-lg ${
                darkMode ? 'bg-orange-900/60' : 'bg-white/90'
              } backdrop-blur-sm`}>
                <img 
                  src={axcelLogo} 
                  alt="Axcel Logo" 
                  className="h-20 w-auto"
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
                    <span className={`text-sm ${darkMode ? 'text-red-400' : 'text-red-500'}`}>
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

  // Main screen - ENHANCED with dark mode + prominent logo
  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      darkMode ? 'bg-gray-900 text-white' : getGradientClass('blue-50', 'indigo-100')
    }`}>
      {/* Dark Mode Toggle - Fixed Position */}
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

      {/* Mobile-First Container - Yellow Box Area */}
      <div className="p-4 sm:p-6 lg:p-8">
        <div className="max-w-4xl mx-auto pt-8 sm:pt-12">
          {/* Header with Logo - ENHANCED */}
          <div className="text-center mb-8">
            {/* 🎯 Logo with enhanced background for both modes */}
            <div className="mb-6">
              <div className={`inline-block p-3 rounded-full mb-4 shadow-lg transition-all duration-300 hover:scale-105 ${
                darkMode ? 'bg-gray-700/80 border border-gray-600' : 'bg-white/90 border border-gray-200'
              } backdrop-blur-sm`}>
                <img 
                  src={axcelLogo} 
                  alt="Axcel Logo" 
                  className="h-16 sm:h-20 w-auto transition-transform duration-300 hover:scale-105"
                />
              </div>
            </div>
            
            <h1 className={`text-3xl sm:text-4xl font-bold mb-2 ${getTextClass('heading')}`}>
              🎓 AI Tutor Quiz
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
                        ? darkMode
                          ? 'border-blue-400 bg-blue-900 text-blue-200'
                          : 'border-blue-500 bg-blue-50 text-blue-700'
                        : hasQuestions
                        ? darkMode
                          ? 'border-gray-600 bg-gray-700 hover:border-blue-400 hover:bg-blue-900 text-gray-200'
                          : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50 text-gray-800'
                        : darkMode
                        ? 'border-gray-700 bg-gray-800 text-gray-500 cursor-not-allowed'
                        : 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    <div className="text-base sm:text-lg font-semibold capitalize">{subject}</div>
                    <div className="text-sm mt-1">
                      {hasQuestions ? (
                        <span className={darkMode ? 'text-green-400' : 'text-green-600'}>
                          {subjectData.count} question banks
                        </span>
                      ) : (
                        <span className={darkMode ? 'text-red-400' : 'text-red-500'}>
                          No questions available
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Question Bank Selection - Mobile-Optimized */}
          {selectedSubject && (
            <div className={getCardClass('mb-6')}>
              <h2 className={`text-lg sm:text-xl font-semibold mb-4 ${getTextClass('subheading')}`}>
                📝 Select Question Bank - {selectedSubject}
              </h2>
              
              {subjectBanks.length > 0 ? (
                <div className="space-y-3">
                  {subjectBanks.map(bank => {
                    const isSelected = selectedBank?.id === bank.id;
                    
                    return (
                      <button
                        key={bank.id}
                        onClick={() => handleBankSelect(bank)}
                        className={`w-full p-3 sm:p-4 rounded-lg border-2 text-left transition-all ${
                          isSelected
                            ? darkMode
                              ? 'border-green-400 bg-green-900'
                              : 'border-green-500 bg-green-50'
                            : darkMode
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
                          
                          {isSelected && (
                            <div className={`text-lg sm:text-xl ml-2 ${darkMode ? 'text-green-400' : 'text-green-500'}`}>
                              ✅
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-3">🔭</div>
                  <h3 className={`text-base sm:text-lg font-semibold mb-2 ${getTextClass('subheading')}`}>
                    No Question Banks for {selectedSubject}
                  </h3>
                  <p className={`${getTextClass('body')} text-sm sm:text-base`}>
                    Add question bank files to get started with {selectedSubject} practice.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Start Button - Mobile-Optimized */}
          {selectedBank && (
            <div className="text-center pb-8">
              <button
                onClick={handleStart}
                className={`w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 text-lg sm:text-xl font-semibold rounded-lg transition-all shadow-lg hover:shadow-xl ${
                  darkMode
                    ? 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white'
                    : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white'
                }`}
              >
                🚀 Start Test
              </button>
              
              <p className={`text-sm mt-3 ${getTextClass('body')} px-4 sm:px-0`}>
                Ready to start with <strong>{selectedBank.name}</strong>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StartScreen;