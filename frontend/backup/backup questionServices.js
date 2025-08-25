// ==============================
// 🔍 services/questionService.js - Dynamic Question Bank Discovery (WITH DEBUG)
// ==============================

/**
 * Dynamic Question Service that auto-discovers question banks
 * No hard-coding needed - automatically finds all available question banks
 */

// Cache for discovered question banks
let discoveredBanks = null;
let lastDiscoveryTime = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Auto-discover all available question banks from the question_banks folder
 * @returns {Promise<Array>} Array of discovered question bank metadata
 */
export const discoverQuestionBanks = async () => {
  console.log('🔍 === DISCOVERY DEBUG START ===');
  
  // Check cache first
  const now = Date.now();
  if (discoveredBanks && lastDiscoveryTime && (now - lastDiscoveryTime) < CACHE_DURATION) {
    console.log('🔄 Using cached question banks:', discoveredBanks.length);
    return discoveredBanks;
  }

  try {
    console.log('🔍 Auto-discovering question banks...');
    
    // Try to get a list of folders by attempting to fetch metadata files
    const potentialBanks = await attemptBankDiscovery();
    console.log('📋 Potential banks from discovery:', potentialBanks.slice(0, 10)); // Show first 10
    
    const validBanks = [];
    
    // Validate each discovered bank
    for (const bankId of potentialBanks) {
      console.log(`🔍 Checking bank: ${bankId}`);
      
      try {
        const metadata = await loadBankMetadata(bankId);
        if (metadata) {
          console.log(`✅ Metadata found for ${bankId}`);
          // Check if questions file exists
          const questionValidation = await validateQuestionFile(bankId);
          if (questionValidation.valid) {
            console.log(`✅ Questions file found for ${bankId}: ${questionValidation.fileName}`);
            validBanks.push({
              id: bankId,
              name: metadata.name || formatBankName(bankId),
              description: metadata.description || formatBankDescription(bankId),
              estimatedCount: metadata.estimatedCount || metadata.total_questions || 'Unknown',
              subject: metadata.subject || extractSubjectFromId(bankId),
              level: metadata.level || 'IGCSE',
              session: metadata.session || extractSessionFromId(bankId),
              paper_number: metadata.paper_number || extractPaperFromId(bankId),
              lastUpdated: metadata.extraction_date || metadata.lastUpdated,
              // Additional categorization
              exam_board: metadata.exam_board || 'Cambridge IGCSE',
              difficulty_level: metadata.difficulty_level || 'Standard',
              tags: metadata.tags || [],
              questionFileName: questionValidation.fileName
            });
          } else {
            console.warn(`⚠️ Bank ${bankId} has metadata but no valid questions file:`, questionValidation.error);
          }
        } else {
          console.log(`⚠️ No metadata for ${bankId}, checking for questions file anyway`);
        }
      } catch (error) {
        console.warn(`⚠️ Could not load metadata for ${bankId}:`, error.message);
        
        // Still try to add the bank with basic info if question file exists
        const basicValidation = await validateQuestionFile(bankId);
        if (basicValidation.valid) {
          console.log(`✅ Added ${bankId} without metadata, using basic info`);
          validBanks.push({
            id: bankId,
            name: formatBankName(bankId),
            description: formatBankDescription(bankId),
            estimatedCount: 'Unknown',
            subject: extractSubjectFromId(bankId),
            level: 'IGCSE',
            session: extractSessionFromId(bankId),
            paper_number: extractPaperFromId(bankId),
            lastUpdated: null,
            exam_board: 'Cambridge IGCSE',
            difficulty_level: 'Standard',
            tags: [],
            questionFileName: basicValidation.fileName
          });
        } else {
          console.log(`❌ ${bankId} has no valid questions file: ${basicValidation.error}`);
        }
      }
    }

    // Cache the results
    discoveredBanks = validBanks;
    lastDiscoveryTime = now;
    
    console.log(`✅ === DISCOVERY COMPLETE: ${validBanks.length} banks found ===`);
    console.log('📋 Final banks:', validBanks.map(b => `${b.id} (${b.questionFileName || 'no file'})`));
    return validBanks;

  } catch (error) {
    console.error('❌ Error discovering question banks:', error);
    return [];
  }
};

/**
 * Attempt to discover available banks using common naming patterns
 * @returns {Promise<Array>} Array of potential bank IDs
 */
const attemptBankDiscovery = async () => {
  // Start with known banks from your folder structure
  const knownBanks = [
    'physics_2024_mar_13',
    'physics_2025_mar_13'
  ];
  
  console.log('📋 Known banks to check:', knownBanks);
  
  // You can expand this list as you add more question banks
  const potentialBanks = [...knownBanks];
  
  // Multi-subject support - easily expandable
  const subjects = [
    'physics', 
    'chemistry', 
    'biology', 
    'mathematics', 
    'math',
    'english', 
    'history', 
    'geography',
    'computer_science',
    'cs',
    'economics',
    'business'
  ];
  
  const years = ['2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027'];
  const sessions = ['feb', 'mar', 'may', 'jun', 'oct', 'nov'];
  const papers = ['11', '12', '13', '21', '22', '23', '31', '32', '33', '41', '42', '43'];
  
  // Generate potential bank IDs based on patterns (for future expansion)
  for (const subject of ['physics']) { // Focus on physics for now
    for (const year of years) {
      for (const session of sessions) {
        for (const paper of papers) {
          potentialBanks.push(`${subject}_${year}_${session}_${paper}`);
        }
      }
    }
  }
  
  // Filter out duplicates
  const finalBanks = [...new Set(potentialBanks)];
  console.log('📋 All potential banks to validate:', finalBanks.length, 'banks');
  return finalBanks;
};

/**
 * Load metadata.json for a specific question bank
 * @param {string} bankId - Question bank identifier
 * @returns {Promise<Object|null>} Metadata object or null if not found
 */
const loadBankMetadata = async (bankId) => {
  try {
    const metadataPath = `/question_banks/${bankId}/metadata.json`;
    console.log(`📄 Trying to load metadata: ${metadataPath}`);
    
    const response = await fetch(metadataPath);
    
    if (response.ok) {
      const metadata = await response.json();
      console.log(`✅ Metadata loaded successfully for ${bankId}`);
      return metadata.exam_info || metadata; // Handle different metadata structures
    } else {
      console.log(`⚠️ Metadata response: ${response.status} ${response.statusText} for ${bankId}`);
    }
    return null;
  } catch (error) {
    console.log(`⚠️ Metadata fetch error for ${bankId}:`, error.message);
    return null;
  }
};

/**
 * Validate that a question file exists for a bank (with case-insensitive matching)
 * @param {string} bankId - Question bank identifier
 * @returns {Promise<Object>} Validation result
 */
const validateQuestionFile = async (bankId) => {
  console.log(`🔍 Validating question file for: ${bankId}`);
  
  // Try common question file naming patterns with case variations
  const possibleFiles = [
    // Exact match patterns
    `${bankId}_question_bank.json`,
    `questions.json`,
    `question_bank.json`,
    
    // Case variations for the specific files you have
    `physics_2025_Mar_13_question_bank.json`, // Your actual file with capital M
    `physics_2024_Mar_13_question_bank.json`, // In case 2024 has capital M too
    
    // Other common patterns
    `${bankId}.json`,
    `exam_questions.json`,
    `past_paper_questions.json`
  ];
  
  // Try with different capitalization patterns
  const capitalizedVariants = possibleFiles.map(file => {
    // Convert to different case patterns
    return [
      file,
      file.replace(/_mar_/g, '_Mar_'), // mar -> Mar
      file.replace(/_may_/g, '_May_'), // may -> May  
      file.replace(/_jun_/g, '_Jun_'), // jun -> Jun
      file.replace(/_oct_/g, '_Oct_'), // oct -> Oct
      file.replace(/_nov_/g, '_Nov_'), // nov -> Nov
      file.replace(/_feb_/g, '_Feb_')  // feb -> Feb
    ];
  }).flat();
  
  const allPossibleFiles = [...new Set([...possibleFiles, ...capitalizedVariants])];
  
  console.log(`📁 Will check ${allPossibleFiles.length} possible files for ${bankId}:`, allPossibleFiles.slice(0, 8));
  
  for (const fileName of allPossibleFiles) {
    try {
      const filePath = `/question_banks/${bankId}/${fileName}`;
      console.log(`🔍 Trying file: ${filePath}`);
      
      const response = await fetch(filePath, { method: 'HEAD' });
      console.log(`📄 ${fileName} response: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        console.log(`✅ Found question file: ${fileName}`);
        return { valid: true, fileName, message: `Found question file: ${fileName}` };
      }
    } catch (error) {
      console.log(`❌ Error checking ${fileName}:`, error.message);
      continue;
    }
  }
  
  console.log(`❌ No question file found for ${bankId}`);
  return { valid: false, error: `No question file found for ${bankId}` };
};

/**
 * Get list of available question banks (cached)
 * @returns {Promise<Array>} Array of question bank metadata
 */
export const getAvailableBanks = async () => {
  return await discoverQuestionBanks();
};

/**
 * Load questions from a specific question bank (auto-detect file)
 * @param {string} bankId - Question bank identifier
 * @returns {Promise<Array>} Array of question objects
 */
export const loadQuestions = async (bankId) => {
  try {
    console.log(`📚 Loading questions from bank: ${bankId}`);
    
    // First, validate and find the correct question file
    const validation = await validateQuestionFile(bankId);
    if (!validation.valid) {
      throw new Error(validation.error);
    }
    
    // Construct file paths
    const basePath = `/question_banks/${bankId}/`;
    const questionFilePath = `${basePath}${validation.fileName}`;
    const solutionsFilePath = `${basePath}solutions.json`;
    const imagesBasePath = `${basePath}images/`;

    console.log(`📂 Loading questions from: ${questionFilePath}`);

    // Load questions and solutions files
    const [questionsResponse, solutionsResponse] = await Promise.all([
      fetch(questionFilePath),
      fetch(solutionsFilePath).catch(() => null)
    ]);

    if (!questionsResponse.ok) {
      throw new Error(`Failed to load questions file: ${questionsResponse.statusText}`);
    }

    const questionsData = await questionsResponse.json();
    let solutionsData = null;
    
    if (solutionsResponse && solutionsResponse.ok) {
      solutionsData = await solutionsResponse.json();
      console.log(`✅ Loaded solutions file for ${bankId}`);
    } else {
      console.log(`⚠️ No solutions file found for ${bankId}, using embedded solutions`);
    }

    // Process and merge questions with solutions
    const processedQuestions = processQuestions(questionsData, solutionsData, imagesBasePath);
    
    console.log(`✅ Successfully loaded ${processedQuestions.length} questions from ${bankId}`);
    
    return processedQuestions;

  } catch (error) {
    console.error(`❌ Error loading questions from ${bankId}:`, error);
    throw new Error(`Failed to load questions from ${bankId}: ${error.message}`);
  }
};

/**
 * Wrapper function for compatibility with App.jsx that expects loadQuestionBank
 * @param {string} bankId - Question bank identifier  
 * @returns {Promise<Object>} Object with questions array and metadata
 */
export const loadQuestionBank = async (bankId) => {
  try {
    console.log(`📚 Loading question bank: ${bankId}`);
    
    // Load questions using existing function
    const questions = await loadQuestions(bankId);
    
    // Load metadata for additional info
    const metadata = await loadBankMetadata(bankId);
    
    // Return in the format expected by App.jsx
    return {
      questions: questions,
      metadata: {
        bankId: bankId,
        questionCount: questions.length,
        loadedAt: new Date().toISOString(),
        bankMetadata: metadata
      }
    };
    
  } catch (error) {
    console.error(`❌ Error loading question bank ${bankId}:`, error);
    throw new Error(`Failed to load question bank: ${error.message}`);
  }
};

/**
 * Process raw questions data and merge with solutions
 * @param {Array|Object} questionsData - Raw questions data from JSON
 * @param {Array|Object} solutionsData - Solutions data (optional)
 * @param {string} imagesBasePath - Base path for images
 * @returns {Array} Processed questions array
 */
const processQuestions = (questionsData, solutionsData, imagesBasePath) => {
  let questions = [];

  // Handle different JSON structures
  if (Array.isArray(questionsData)) {
    questions = questionsData;
  } else if (questionsData.questions) {
    questions = questionsData.questions;
  } else if (typeof questionsData === 'object') {
    questions = Object.values(questionsData);
  } else {
    throw new Error('Unsupported questions data format');
  }

  if (!questions || questions.length === 0) {
    throw new Error('No questions found in data');
  }

  // Process each question with better error handling
  return questions.map((question, index) => {
    // Ensure we have a valid question object
    if (!question || typeof question !== 'object') {
      console.warn(`Invalid question at index ${index}:`, question);
      return null;
    }

    const processedQuestion = {
      id: question.id || question.question_id || `q_${index + 1}`,
      question_text: question.question_text || question.text || question.question || `Question ${index + 1}`,
      options: question.options || question.answers || {},
      correct_answer: question.correct_answer || question.answer || question.correct,
      topic: question.topic || question.category || 'Physics',
      difficulty: question.difficulty || 'medium',
      
      // Solution fields
      simple_answer: question.simple_answer || question.explanation || '',
      calculation_steps: question.calculation_steps || question.steps || [],
      detailed_explanation: question.detailed_explanation || {
        why_correct: question.why_correct || '',
        why_others_wrong: question.why_others_wrong || {}
      },

      // Image handling with better error checking
      image_url: question.image_url ? `${imagesBasePath}${question.image_url}` : null,
      image_alt: question.image_alt || `Question ${question.id || index + 1} diagram`,
      
      // Metadata
      confidence_score: question.confidence_score || 1.0,
      auto_flagged: question.auto_flagged || false
    };

    // Validate critical fields
    if (!processedQuestion.question_text) {
      console.warn(`Question ${processedQuestion.id} has no question text`);
    }
    
    if (!processedQuestion.options || Object.keys(processedQuestion.options).length === 0) {
      console.warn(`Question ${processedQuestion.id} has no options`);
      processedQuestion.options = {}; // Ensure it's an object
    }

    // Merge with external solutions if available
    if (solutionsData) {
      const solution = findSolutionForQuestion(solutionsData, processedQuestion.id);
      if (solution) {
        processedQuestion.simple_answer = solution.simple_answer || processedQuestion.simple_answer;
        processedQuestion.calculation_steps = solution.calculation_steps || processedQuestion.calculation_steps;
        processedQuestion.detailed_explanation = {
          ...processedQuestion.detailed_explanation,
          ...solution.detailed_explanation
        };
      }
    }

    return processedQuestion;
  }).filter(question => question !== null); // Remove any null questions
};

/**
 * Utility functions for formatting bank information
 */
const formatBankName = (bankId) => {
  const parts = bankId.split('_');
  return parts.map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
};

const formatBankDescription = (bankId) => {
  const parts = bankId.split('_');
  const subject = parts[0]?.charAt(0).toUpperCase() + parts[0]?.slice(1) || 'Unknown';
  const year = parts[1] || '';
  const session = parts[2]?.charAt(0).toUpperCase() + parts[2]?.slice(1) || '';
  const paper = parts[3] || '';
  
  // Handle subject variations
  let formattedSubject = subject;
  if (subject.toLowerCase() === 'cs') formattedSubject = 'Computer Science';
  if (subject.toLowerCase() === 'math') formattedSubject = 'Mathematics';
  
  return `${formattedSubject} ${session} ${year} Paper ${paper}`.trim();
};

const extractSubjectFromId = (bankId) => {
  const parts = bankId.split('_');
  const subject = parts[0]?.toLowerCase() || 'unknown';
  
  // Map common abbreviations to full names
  const subjectMap = {
    'physics': 'Physics',
    'chemistry': 'Chemistry', 
    'biology': 'Biology',
    'math': 'Mathematics',
    'mathematics': 'Mathematics',
    'english': 'English',
    'history': 'History',
    'geography': 'Geography',
    'cs': 'Computer Science',
    'computer_science': 'Computer Science',
    'economics': 'Economics',
    'business': 'Business Studies'
  };
  
  return subjectMap[subject] || subject.charAt(0).toUpperCase() + subject.slice(1);
};

const extractSessionFromId = (bankId) => {
  const parts = bankId.split('_');
  return parts[2]?.charAt(0).toUpperCase() + parts[2]?.slice(1) || '';
};

const extractPaperFromId = (bankId) => {
  const parts = bankId.split('_');
  return parts[3] || '';
};

/**
 * Find solution for a specific question from solutions data
 */
const findSolutionForQuestion = (solutionsData, questionId) => {
  if (Array.isArray(solutionsData)) {
    return solutionsData.find(solution => 
      solution.id === questionId || 
      solution.question_id === questionId
    );
  } else if (typeof solutionsData === 'object') {
    return solutionsData[questionId] || solutionsData[`question_${questionId}`];
  }
  return null;
};

/**
 * Load specific questions by IDs (for retest functionality)
 */
export const loadSpecificQuestions = async (bankId, questionIds) => {
  const allQuestions = await loadQuestions(bankId);
  return allQuestions.filter(question => questionIds.includes(question.id));
};

/**
 * Validate question bank exists and is accessible
 */
export const validateQuestionBank = async (bankId) => {
  try {
    const validation = await validateQuestionFile(bankId);
    return validation;
  } catch (error) {
    return { valid: false, error: `Validation failed: ${error.message}` };
  }
};

/**
 * Clear cache (useful for development/testing)
 */
export const clearCache = () => {
  discoveredBanks = null;
  lastDiscoveryTime = null;
  console.log('🗑️ Question bank cache cleared');
};

/**
 * Manual bank registration (for edge cases)
 */
export const registerQuestionBank = (bankInfo) => {
  if (discoveredBanks) {
    const existingIndex = discoveredBanks.findIndex(bank => bank.id === bankInfo.id);
    if (existingIndex >= 0) {
      discoveredBanks[existingIndex] = bankInfo;
    } else {
      discoveredBanks.push(bankInfo);
    }
  }
  console.log(`📝 Manually registered question bank: ${bankInfo.id}`);
};