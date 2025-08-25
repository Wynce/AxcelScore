// ==============================
// 🔍 services/questionService.js - TRULY SCALABLE AUTO-DISCOVERY
// ==============================

let cachedBanks = null;
let cachedSubjects = null;

/**
 * TRUE AUTO-DISCOVERY - No manual paper list needed!
 */
async function autoDiscoverAllQuestionBanks() {
  console.log('🔍 TRUE AUTO-DISCOVERY: Scanning all available question banks...');
  
  const discoveredBanks = [];
  
  try {
    // Step 1: Try to get index.json if it exists (optional registry)
    let registryFolders = [];
    try {
      const indexResponse = await fetch('/question_banks/index.json');
      if (indexResponse.ok) {
        const indexData = await indexResponse.json();
        if (indexData.folders && Array.isArray(indexData.folders)) {
          registryFolders = indexData.folders;
          console.log(`📋 Found registry with ${registryFolders.length} folders`);
        }
      }
    } catch (e) {
      console.log('📁 No registry found, using pattern scanning...');
    }
    
    // Step 2: If no registry, use pattern-based discovery
    if (registryFolders.length === 0) {
      registryFolders = await patternBasedDiscovery();
    }
    
    // Step 3: Validate each discovered folder
    for (const folderName of registryFolders) {
      try {
        const bankInfo = await validateAndProcessFolder(folderName);
        if (bankInfo) {
          discoveredBanks.push(bankInfo);
          console.log(`✅ Discovered: ${bankInfo.name} (${bankInfo.estimatedCount} questions)`);
        }
      } catch (error) {
        console.warn(`⚠️ Skipping ${folderName}: ${error.message}`);
      }
    }
    
    console.log(`🎉 AUTO-DISCOVERY COMPLETE: Found ${discoveredBanks.length} question banks`);
    return discoveredBanks;
    
  } catch (error) {
    console.error('❌ Auto-discovery failed:', error);
    return [];
  }
}

/**
 * Pattern-based discovery for common naming conventions
 */
async function patternBasedDiscovery() {
  console.log('🔎 Pattern-based folder discovery...');
  
  const subjects = ['physics', 'mathematics', 'chemistry', 'biology', 'computer_science', 'english', 'history'];
  const years = ['2023', '2024', '2025', '2026'];
  const sessions = ['mar', 'may', 'oct', 'nov'];
  const papers = ['11', '12', '13', '21', '22', '23', '31', '32', '33'];
  
  const possibleFolders = [];
  
  // Generate all possible combinations
  for (const subject of subjects) {
    for (const year of years) {
      for (const session of sessions) {
        for (const paper of papers) {
          possibleFolders.push(`${subject}_${year}_${session}_${paper}`);
        }
      }
    }
  }
  
  // Test each possibility (sample small batch to avoid overwhelming)
  const existingFolders = [];
  const batchSize = 50; // Test in batches to avoid too many requests
  
  for (let i = 0; i < Math.min(possibleFolders.length, 200); i += batchSize) {
    const batch = possibleFolders.slice(i, i + batchSize);
    const batchPromises = batch.map(async (folderName) => {
      try {
        // Quick test - try to access folder metadata
        const testResponse = await fetch(`/question_banks/${folderName}/metadata.json`, { method: 'HEAD' });
        if (testResponse.ok) {
          return folderName;
        }
        // Alternative test - try direct question file
        const altResponse = await fetch(`/question_banks/${folderName}/solutions.json`, { method: 'HEAD' });
        if (altResponse.ok) {
          return folderName;
        }
        return null;
      } catch (e) {
        return null;
      }
    });
    
    const batchResults = await Promise.all(batchPromises);
    const foundInBatch = batchResults.filter(folder => folder !== null);
    existingFolders.push(...foundInBatch);
    
    if (foundInBatch.length > 0) {
      console.log(`📂 Found ${foundInBatch.length} folders in batch ${Math.floor(i/batchSize) + 1}`);
    }
  }
  
  return existingFolders;
}

/**
 * Validate folder and extract question bank info
 */
async function validateAndProcessFolder(folderName) {
  console.log(`🔍 Validating folder: ${folderName}`);
  
  // Try different file formats in priority order
  const possibleFiles = [
    'solutions.json',
    `${folderName}_question_bank.json`,
    'questions.json',
    'question_bank.json'
  ];
  
  let questionFile = null;
  let questionsData = null;
  
  // Find the question file
  for (const fileName of possibleFiles) {
    try {
      const fileUrl = `/question_banks/${folderName}/${fileName}`;
      const response = await fetch(fileUrl);
      
      if (response.ok) {
        const data = await response.json();
        if (isValidQuestionData(data)) {
          questionFile = fileName;
          questionsData = data;
          break;
        }
      }
    } catch (e) {
      continue;
    }
  }
  
  if (!questionFile || !questionsData) {
    throw new Error('No valid question file found');
  }
  
  // Extract metadata from folder name
  const metadata = parseFolderName(folderName);
  
  // Count questions
  const questionCount = countQuestions(questionsData);
  if (questionCount === 0) {
    throw new Error('No questions found in file');
  }
  
  // Build bank info
  const bankInfo = {
    id: folderName,
    name: metadata.displayName,
    description: `${metadata.subject} ${metadata.session} ${metadata.year} Paper ${metadata.paper}`,
    subject: metadata.subject,
    level: metadata.level || 'IGCSE',
    session: metadata.session,
    paper_number: metadata.paper,
    year: metadata.year,
    exam_board: metadata.examBoard || 'Cambridge IGCSE',
    questionFileName: questionFile,
    filePath: `/question_banks/${folderName}/${questionFile}`,
    estimatedCount: questionCount,
    lastUpdated: new Date().toISOString(),
    discovered_method: 'auto_discovery',
    tags: [metadata.subject, metadata.year, metadata.session, metadata.paper]
  };
  
  return bankInfo;
}

/**
 * Check if data contains valid questions
 */
function isValidQuestionData(data) {
  if (Array.isArray(data) && data.length > 0) {
    return data[0].question_text || data[0].question || data[0].options;
  }
  
  if (typeof data === 'object' && data !== null) {
    if (data.questions && Array.isArray(data.questions)) {
      return data.questions.length > 0;
    }
    
    // Check if it's AI Solver format (object with question keys)
    const keys = Object.keys(data);
    if (keys.length > 0) {
      const firstItem = data[keys[0]];
      return firstItem && (firstItem.question_text || firstItem.options);
    }
  }
  
  return false;
}

/**
 * Count questions in different data formats
 */
function countQuestions(data) {
  if (Array.isArray(data)) {
    return data.length;
  }
  
  if (typeof data === 'object' && data !== null) {
    if (data.questions && Array.isArray(data.questions)) {
      return data.questions.length;
    }
    return Object.keys(data).length; // AI Solver format
  }
  
  return 0;
}

/**
 * Parse folder name to extract metadata
 */
function parseFolderName(folderName) {
  const parts = folderName.split('_');
  
  if (parts.length >= 4) {
    const [subject, year, session, paper] = parts;
    
    return {
      subject: capitalizeFirst(subject),
      year: year,
      session: capitalizeFirst(session),
      paper: paper,
      level: 'IGCSE',
      examBoard: 'Cambridge IGCSE',
      displayName: `${capitalizeFirst(subject)} ${year} ${capitalizeFirst(session)} ${paper}`
    };
  }
  
  // Fallback for non-standard names
  return {
    subject: 'Unknown',
    year: 'Unknown',
    session: 'Unknown', 
    paper: 'Unknown',
    displayName: `Question Bank - ${folderName}`
  };
}

/**
 * Main discovery function - TRULY SCALABLE
 */
export const discoverQuestionBanks = async () => {
  console.log('🚀 SCALABLE DISCOVERY: Starting...');
  
  if (cachedBanks) {
    console.log('💾 Using cached banks:', cachedBanks.length);
    return cachedBanks;
  }

  try {
    // Auto-discover all available banks
    const questionBanks = await autoDiscoverAllQuestionBanks();
    
    // Organize by subjects
    const organizedBanks = organizeBySubjects(questionBanks);
    
    console.log(`✅ DISCOVERY COMPLETE: ${questionBanks.length} banks across ${Object.keys(organizedBanks).length} subjects`);
    
    cachedBanks = questionBanks;
    cachedSubjects = organizedBanks;
    
    return questionBanks;
    
  } catch (error) {
    console.error('❌ Discovery error:', error);
    return [];
  }
};

/**
 * SOLUTION MATCHING - Critical for random questions
 */
export const loadQuestionsWithSolutionMatching = async (bankId) => {
  console.log(`📚 Loading questions with solution matching: ${bankId}`);
  
  const banks = await discoverQuestionBanks();
  const bank = banks.find(b => b.id === bankId);
  
  if (!bank) {
    throw new Error(`Unknown bank: ${bankId}`);
  }
  
  try {
    // Load main question data
    const questionResponse = await fetch(bank.filePath);
    if (!questionResponse.ok) {
      throw new Error(`Failed to load questions: ${questionResponse.status}`);
    }
    const questionData = await questionResponse.json();
    
    // Load solutions data (AI Solver export)
    let solutionsData = null;
    try {
      const solutionsResponse = await fetch(`/question_banks/${bankId}/solutions.json`);
      if (solutionsResponse.ok) {
        solutionsData = await solutionsResponse.json();
        console.log('✅ Solutions data loaded for answer matching');
      }
    } catch (e) {
      console.warn('⚠️ No solutions.json found - using question data for answers');
    }
    
    // Process and match questions with solutions
    const questions = processQuestionsData(questionData);
    const matchedQuestions = matchQuestionsWithSolutions(questions, solutionsData);
    
    // Validate the matching
    const validation = validateQuestionSolutionMatch(matchedQuestions);
    if (!validation.valid) {
      console.error('❌ Question-solution mismatch detected:', validation.issues);
      // Continue anyway but log the issues
    }
    
    console.log(`✅ Loaded ${matchedQuestions.length} questions with ${validation.matchedCount} solution matches`);
    return matchedQuestions;
    
  } catch (error) {
    console.error('❌ Load error:', error);
    throw error;
  }
};

/**
 * Match questions with their solutions
 */
function matchQuestionsWithSolutions(questions, solutionsData) {
  if (!solutionsData) {
    return questions; // Use questions as-is if no separate solutions
  }
  
  return questions.map(question => {
    const questionNum = extractQuestionNumber(question.id);
    const solutionKey = findSolutionKey(questionNum, solutionsData);
    
    if (solutionKey && solutionsData[solutionKey]) {
      const solution = solutionsData[solutionKey];
      
      return {
        ...question,
        // Override with solution data if available
        correct_answer: solution.correct_answer || question.correct_answer,
        simple_answer: solution.simple_answer || question.simple_answer,
        calculation_steps: solution.calculation_steps || question.calculation_steps,
        detailed_explanation: solution.detailed_explanation || question.detailed_explanation,
        confidence_score: solution.confidence_score || question.confidence_score,
        solution_matched: true,
        solution_source: 'ai_solver'
      };
    }
    
    return {
      ...question,
      solution_matched: false,
      solution_source: 'question_data'
    };
  });
}

/**
 * Extract question number from various ID formats
 */
function extractQuestionNumber(questionId) {
  if (typeof questionId === 'number') return questionId;
  
  const matches = questionId.toString().match(/\d+/);
  return matches ? parseInt(matches[0]) : null;
}

/**
 * Find corresponding solution key for question number
 */
function findSolutionKey(questionNum, solutionsData) {
  if (!questionNum || !solutionsData) return null;
  
  // Try different key formats
  const possibleKeys = [
    questionNum.toString(),
    `q${questionNum}`,
    `question_${questionNum}`,
    `${questionNum}`
  ];
  
  for (const key of possibleKeys) {
    if (solutionsData[key]) {
      return key;
    }
  }
  
  return null;
}

/**
 * Validate question-solution matching
 */
function validateQuestionSolutionMatch(questions) {
  const validation = {
    valid: true,
    issues: [],
    totalQuestions: questions.length,
    matchedCount: 0,
    unmatchedCount: 0
  };
  
  questions.forEach((question, index) => {
    const expectedNum = index + 1;
    const actualNum = extractQuestionNumber(question.id);
    
    // Check numbering
    if (actualNum !== expectedNum) {
      validation.issues.push(`Question ${actualNum} in position ${expectedNum}`);
      validation.valid = false;
    }
    
    // Check solution matching
    if (question.solution_matched) {
      validation.matchedCount++;
    } else {
      validation.unmatchedCount++;
    }
    
    // Validate answer consistency
    if (!question.correct_answer || !['A', 'B', 'C', 'D'].includes(question.correct_answer)) {
      validation.issues.push(`Question ${actualNum}: Invalid correct answer`);
      validation.valid = false;
    }
  });
  
  return validation;
}

// ... Helper functions
function organizeBySubjects(banks) {
  const organized = {};
  
  for (const bank of banks) {
    const subject = bank.subject || 'Unknown';
    
    if (!organized[subject]) {
      organized[subject] = {
        name: subject,
        banks: [],
        count: 0
      };
    }
    
    organized[subject].banks.push(bank);
    organized[subject].count++;
  }
  
  return organized;
}

function processQuestionsData(data) {
  let questions = [];
  
  if (Array.isArray(data)) {
    questions = data;
  } else if (data.questions && Array.isArray(data.questions)) {
    questions = data.questions;
  } else if (typeof data === 'object') {
    questions = Object.values(data);
  }
  
  return questions.map((q, index) => ({
    id: q.question_number || q.id || `q_${index + 1}`,
    question_text: q.question_text || q.question || `Question ${index + 1}`,
    options: q.options || {},
    correct_answer: q.correct_answer,
    topic: q.topic || 'General',
    difficulty: q.difficulty || 'medium',
    simple_answer: q.simple_answer || '',
    calculation_steps: q.calculation_steps || [],
    detailed_explanation: q.detailed_explanation || {},
    image_url: q.image_url || null,
    image_alt: q.image_alt || `Question ${index + 1}`,
    confidence_score: q.confidence_score || 1.0
  }));
}

function capitalizeFirst(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// ==============================
// 🚀 MAIN EXPORTED FUNCTIONS
// ==============================

export const loadQuestions = loadQuestionsWithSolutionMatching;

export const loadQuestionBank = async (bankId) => {
  const questions = await loadQuestionsWithSolutionMatching(bankId);
  return {
    questions: questions,
    metadata: {
      bankId: bankId,
      questionCount: questions.length,
      loadedAt: new Date().toISOString(),
      solutionMatching: questions.filter(q => q.solution_matched).length
    }
  };
};

export const getAvailableBanks = async () => {
  return await discoverQuestionBanks();
};

export const getAvailableSubjects = async () => {
  if (cachedSubjects) {
    return cachedSubjects;
  }
  await discoverQuestionBanks();
  return cachedSubjects || {};
};

// ⭐ MISSING FUNCTION - This is what StartScreen.jsx needs!
export const getBanksForSubject = async (subject) => {
  console.log(`📚 Getting banks for subject: ${subject}`);
  
  // Ensure subjects are loaded
  const subjects = await getAvailableSubjects();
  
  if (!subjects[subject]) {
    console.warn(`⚠️ Subject '${subject}' not found`);
    return [];
  }
  
  const subjectData = subjects[subject];
  console.log(`✅ Found ${subjectData.count} banks for ${subject}`);
  
  return subjectData.banks || [];
};

export const clearCache = () => {
  cachedBanks = null;
  cachedSubjects = null;
  console.log('🗑️ Cache cleared - will rediscover on next request');
};

// ==============================
// 🔧 VALIDATION FUNCTIONS
// ==============================

export const validateQuestionBankStructure = async (bankId) => {
  console.log(`🔍 Validating structure for: ${bankId}`);
  
  try {
    const questions = await loadQuestionsWithSolutionMatching(bankId);
    const validation = validateQuestionSolutionMatch(questions);
    
    console.log(`📊 Validation Results:
    ✅ Total Questions: ${validation.totalQuestions}
    ✅ Solution Matches: ${validation.matchedCount}
    ❌ Unmatched: ${validation.unmatchedCount}
    ⚠️ Issues: ${validation.issues.length}`);
    
    if (validation.issues.length > 0) {
      console.warn('Issues found:', validation.issues);
    }
    
    return validation;
    
  } catch (error) {
    console.error('❌ Validation failed:', error);
    return { valid: false, error: error.message };
  }
};

export const quickHealthCheck = async (bankId) => {
  console.log(`🏥 Health check for: ${bankId}`);
  
  try {
    const start = performance.now();
    const questions = await loadQuestionsWithSolutionMatching(bankId);
    const loadTime = performance.now() - start;
    
    const health = {
      bankId: bankId,
      status: 'healthy',
      loadTime: `${loadTime.toFixed(2)}ms`,
      questionCount: questions.length,
      hasImages: questions.filter(q => q.image_url).length,
      solutionMatches: questions.filter(q => q.solution_matched).length,
      timestamp: new Date().toISOString()
    };
    
    console.log(`✅ Health Check Complete:
    📊 Questions: ${health.questionCount}
    ⏱️ Load Time: ${health.loadTime}
    🖼️ Images: ${health.hasImages}
    🎯 Solutions: ${health.solutionMatches}`);
    
    return health;
    
  } catch (error) {
    console.error('❌ Health check failed:', error);
    return {
      bankId: bankId,
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
};