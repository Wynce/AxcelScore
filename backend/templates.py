#!/usr/bin/env python3
"""
HTML and Prompt templates for the Enhanced AI Solver
Only contains hardcoded strings that were cluttering the main file
"""

def get_claude_prompt_template(subject: str, question_number: int) -> str:
    """Generate the Claude API prompt template"""
    return f"""Please analyze this Cambridge IGCSE {subject} question {question_number} and provide a clear, focused analysis.

IMPORTANT: Extract ALL text accurately and use this EXACT JSON format:

{{
  "question_text": "Complete question text extracted from image word-for-word",
  "options": {{
    "A": "Option A text exactly as shown",
    "B": "Option B text exactly as shown",
    "C": "Option C text exactly as shown", 
    "D": "Option D text exactly as shown"
  }},
  
  "correct_answer": "C",
  "simple_answer": "Brief, clear answer in one sentence",
  
  "calculation_steps": [
    "Clear step showing key information or setup",
    "Main calculation or reasoning process", 
    "Final result with units and conclusion"
  ],
  
  "detailed_explanation": {{
    "why_correct": "Clear explanation of why the correct answer is right, including relevant {subject.lower()} principles",
    "why_others_wrong": {{
      "A": "Specific reason why option A is incorrect",
      "B": "Specific reason why option B is incorrect", 
      "D": "Specific reason why option D is incorrect"
    }}
  }},
  
  "topic": "Motion and Forces",
  "difficulty": "medium", 
  "confidence_score": 0.95
}}

INSTRUCTIONS:
1. Extract ALL text from image accurately - do not miss any words
2. Give a simple, direct answer that students can understand
3. For calculation_steps: Use as many steps as needed (can be 2, 3, 4, or more steps)
4. Only include calculation steps if the question involves calculations
5. For conceptual questions, focus on explaining the {subject.lower()} concepts clearly
6. Explain why each wrong answer is wrong - be specific
7. Set confidence_score between 0.0-1.0 based on how certain you are
8. Choose appropriate difficulty: "easy", "medium", or "hard"

Be educational and help students understand the underlying {subject.lower()} concepts!"""

def get_css_styles() -> str:
    """Get the complete CSS styles for the focused interface"""
    return '''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header { 
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white; 
            padding: 2rem; 
            text-align: center; 
        }
        .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .header p { margin: 0.5rem 0; opacity: 0.9; }
        
        .status-section {
            padding: 1.5rem;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 2rem;
            align-items: center;
        }
        .status-info {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            text-align: center;
        }
        .status-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .status-card h4 { font-size: 0.9rem; margin-bottom: 0.5rem; color: #666; }
        .status-card div { font-size: 1.2rem; font-weight: bold; color: #333; }
        
        .automation-controls {
            display: flex;
            gap: 1rem;
        }
        .btn {
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-automate { background: linear-gradient(135deg, #28a745, #34ce57); color: white; }
        .btn-preview { background: linear-gradient(135deg, #17a2b8, #20c997); color: white; }
        .btn-check { background: linear-gradient(135deg, #6f42c1, #8b5cf6); color: white; }
        
        .process-section {
            padding: 2rem;
            background: #e3f2fd;
            border-radius: 12px;
            margin: 1.5rem;
            border-left: 4px solid #2196f3;
        }
        .process-section h3 { margin-bottom: 1rem; color: #1976d2; }
        .process-steps { list-style: none; }
        .process-steps li { 
            margin: 0.5rem 0; 
            padding: 0.5rem 0; 
            border-bottom: 1px solid rgba(25,118,210,0.1);
        }
        
        .images-section {
            padding: 2rem;
        }
        .images-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        .image-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        .image-card:hover { transform: translateY(-3px); }
        
        .image-header {
            background: #f8f9fa;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e9ecef;
        }
        .image-header h4 { color: #333; }
        .status-badge {
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-solved { background: #28a745; color: white; }
        .status-pending { background: #6c757d; color: white; }
        .status-review { background: #dc3545; color: white; }
        
        .image-preview {
            width: 100%;
            height: 200px;
            object-fit: contain;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            cursor: pointer;
        }
        
        .image-info {
            padding: 1rem;
        }
        .image-info p { margin: 0.25rem 0; font-size: 0.9rem; color: #666; }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        .notification.show { transform: translateX(0); }
        .notification.success { background: #28a745; }
        .notification.error { background: #dc3545; }
        .notification.info { background: #17a2b8; }
        
        /* Home page specific styles */
        .paper-card { 
            background: #f8f9fa; 
            border: 1px solid #dee2e6; 
            border-radius: 12px; 
            padding: 1.5rem; 
            margin: 1rem 0; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        .paper-info h3 { margin: 0 0 0.5rem 0; color: #333; }
        .paper-info p { margin: 0.25rem 0; color: #666; font-size: 0.9rem; }
        .no-papers { text-align: center; padding: 3rem; color: #6c757d; }
        .api-status { padding: 1rem; margin: 1rem 0; border-radius: 8px; text-align: center; }
        .api-ready { background: #e8f5e8; color: #2e7d32; border: 1px solid #4caf50; }
        .api-not-ready { background: #ffebee; color: #d32f2f; border: 1px solid #f44336; }
        
        @media (max-width: 768px) {
            .container { margin: 10px; border-radius: 15px; }
            .header { padding: 1.5rem; }
            .status-section { grid-template-columns: 1fr; gap: 1rem; }
            .status-info { grid-template-columns: repeat(2, 1fr); }
            .automation-controls { justify-content: center; }
            .images-grid { grid-template-columns: 1fr; }
            .paper-card { flex-direction: column; gap: 1rem; text-align: center; }
        }
    '''

def get_javascript_template(paper_folder: str, total_questions: int, subject: str) -> str:
    """Get the JavaScript functions template"""
    return f'''
    <script>
        const paperFolder = '{paper_folder}';
        const totalQuestions = {total_questions};
        const subject = '{subject}';
        let currentProgress = {{}};
        let promptCache = {{}};
        
        // Enhanced notification system
        function showNotification(message, type = 'success') {{
            const existing = document.querySelectorAll('.notification');
            existing.forEach(n => n.remove());
            
            const notification = document.createElement('div');
            notification.className = `notification ${{type}}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.classList.add('show'), 100);
            setTimeout(() => {{
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }}, 4000);
        }}
        
        // Enhanced prompt generation for Claude API
        function generatePrompt(questionNum) {{
            const promptText = `Please analyze this Cambridge IGCSE {subject} question ${{questionNum}} and provide a clear, focused analysis.

IMPORTANT: Extract ALL text accurately and use this EXACT JSON format:

{{
  "question_text": "Complete question text extracted from image word-for-word",
  "options": {{
    "A": "Option A text exactly as shown",
    "B": "Option B text exactly as shown",
    "C": "Option C text exactly as shown", 
    "D": "Option D text exactly as shown"
  }},
  
  "correct_answer": "C",
  "simple_answer": "Brief, clear answer in one sentence",
  
  "calculation_steps": [
    "Clear step showing key information or setup",
    "Main calculation or reasoning process", 
    "Final result with units and conclusion"
  ],
  
  "detailed_explanation": {{
    "why_correct": "Clear explanation of why the correct answer is right, including relevant {subject.lower()} principles",
    "why_others_wrong": {{
      "A": "Specific reason why option A is incorrect",
      "B": "Specific reason why option B is incorrect", 
      "D": "Specific reason why option D is incorrect"
    }}
  }},
  
  "topic": "Motion and Forces",
  "difficulty": "medium", 
  "confidence_score": 0.95
}}

INSTRUCTIONS:
1. Extract ALL text from image accurately - do not miss any words
2. Give a simple, direct answer that students can understand
3. For calculation_steps: Use as many steps as needed (can be 2, 3, 4, or more steps)
4. Only include calculation steps if the question involves calculations
5. For conceptual questions, focus on explaining the {subject.lower()} concepts clearly
6. Explain why each wrong answer is wrong - be specific
7. Set confidence_score between 0.0-1.0 based on how certain you are
8. Choose appropriate difficulty: "easy", "medium", or "hard"

Be educational and help students understand the underlying {subject.lower()} concepts!`;
            
            promptCache[questionNum] = promptText;
            return promptText;
        }}
        
        function copyPrompt(questionNum) {{
            const prompt = generatePrompt(questionNum);
            navigator.clipboard.writeText(prompt).then(() => {{
                showNotification(`✅ Prompt for Question ${{questionNum}} copied! Paste in Claude.ai`);
            }}).catch(() => {{
                showNotification('Copy failed. Please try again.', 'error');
            }});
        }}
        
        function togglePrompt(questionNum) {{
            const displayDiv = document.getElementById(`prompt-display-${{questionNum}}`);
            const textDiv = document.getElementById(`prompt-text-${{questionNum}}`);
            const button = event.target;
            
            if (displayDiv.style.display === 'none') {{
                if (!promptCache[questionNum]) {{
                    generatePrompt(questionNum);
                }}
                textDiv.textContent = promptCache[questionNum];
                displayDiv.style.display = 'block';
                button.textContent = '🙈 Hide Prompt';
            }} else {{
                displayDiv.style.display = 'none';
                button.textContent = '👁️ View Prompt';
            }}
        }}
        
        function saveSolution(questionNum) {{
            const textarea = document.getElementById(`solution-${{questionNum}}`);
            const solutionText = textarea.value.trim();
            
            if (!solutionText) {{
                showNotification('⚠️ Please enter a solution first', 'warning');
                return;
            }}
            
            try {{
                const solution = JSON.parse(solutionText);
                
                fetch('/api/save-solution', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        paper_folder: paperFolder,
                        question_number: questionNum,
                        solution: solution
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const status = data.quality_status;
                        updateQuestionStatus(questionNum, status);
                        updateProgressDisplay(data.progress);
                        showNotification(`🎉 Question ${{questionNum}} saved to master file!`);
                    }} else {{
                        showNotification(`⚠ Save failed: ${{data.error}}`, 'error');
                    }}
                }})
                .catch(error => {{
                    showNotification(`⚠ Save error: ${{error.message}}`, 'error');
                }});
                
            }} catch (e) {{
                showNotification(`⚠ Invalid JSON format: ${{e.message}}`, 'error');
            }}
        }}
        
        function validateJSON(questionNum) {{
            const textarea = document.getElementById(`solution-${{questionNum}}`);
            const solutionText = textarea.value.trim();
            
            if (!solutionText) {{
                showNotification('⚠️ Please enter a solution first', 'warning');
                return;
            }}
            
            try {{
                const solution = JSON.parse(solutionText);
                
                const required = ['question_text', 'options', 'correct_answer', 'simple_answer', 'detailed_explanation', 'topic'];
                const missing = required.filter(field => !solution[field]);
                
                if (missing.length > 0) {{
                    showNotification(`⚠️ Missing required fields: ${{missing.join(', ')}}`, 'warning');
                    return;
                }}
                
                const explanation = solution.detailed_explanation || {{}};
                if (!explanation.why_correct) {{
                    showNotification('⚠️ Missing detailed_explanation.why_correct', 'warning');
                    return;
                }}
                if (!explanation.why_others_wrong) {{
                    showNotification('⚠️ Missing detailed_explanation.why_others_wrong', 'warning');
                    return;
                }}
                
                const wrongOptions = Object.keys(explanation.why_others_wrong || {{}});
                if (wrongOptions.length < 3) {{
                    showNotification(`⚠️ Need explanations for at least 3 wrong options. Found: ${{wrongOptions.length}}`, 'warning');
                    return;
                }}
                
                showNotification('✅ JSON format is valid!', 'success');
            }} catch (e) {{
                showNotification(`⚠ Invalid JSON: ${{e.message}}`, 'error');
            }}
        }}
        
        function clearSolution(questionNum) {{
            if (confirm(`Clear solution for Question ${{questionNum}}? This will remove it from the master file.`)) {{
                document.getElementById(`solution-${{questionNum}}`).value = '';
                updateQuestionStatus(questionNum, {{ confidence: 0, auto_flagged: false }});
                refreshProgress();
                showNotification(`🗑️ Question ${{questionNum}} cleared`);
            }}
        }}
        
        function startClaudeAutomation() {{
            if (confirm(`Start automated Claude API solving for ${{paperFolder}}?\\n\\nThis will process all unsolved questions automatically.`)) {{
                showNotification('🤖 Claude API automation feature - connect to automated solver!', 'warning');
            }}
        }}
        
        function uploadMarkingScheme() {{
            showNotification('📄 Marking scheme upload - connect to enhanced interface!', 'warning');
        }}
        
        function updateQuestionStatus(questionNum, status) {{
            const statusDiv = document.getElementById(`status-${{questionNum}}`);
            const confidence = status.confidence || 0;
            
            if (confidence > 0) {{
                if (status.auto_flagged) {{
                    statusDiv.textContent = `Flagged (${{(confidence * 100).toFixed(0)}}%)`;
                    statusDiv.className = 'status-indicator flagged';
                }} else {{
                    statusDiv.textContent = `Solved (${{(confidence * 100).toFixed(0)}}%)`;
                    statusDiv.className = 'status-indicator solved';
                }}
            }} else {{
                statusDiv.textContent = 'Pending';
                statusDiv.className = 'status-indicator';
            }}
        }}
        
        function updateProgressDisplay(progress) {{
            if (!progress) return;
            
            const progressBar = document.getElementById('progressBar');
            const percentage = progress.completion_rate || 0;
            progressBar.style.width = percentage + '%';
            progressBar.textContent = `${{percentage}}% Complete`;
            
            document.getElementById('solvedCount').textContent = progress.solved_questions || 0;
            document.getElementById('flaggedCount').textContent = progress.flagged_questions || 0;
            
            const approvedCount = (progress.solved_questions || 0) - (progress.flagged_questions || 0);
            document.getElementById('approvedCount').textContent = approvedCount;
            document.getElementById('avgConfidence').textContent = `${{Math.round((progress.average_confidence || 0) * 100)}}%`;
        }}
        
        function refreshProgress() {{
            fetch('/api/get-progress', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ paper_folder: paperFolder }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    const progress = data.progress;
                    currentProgress = progress;
                    updateProgressDisplay({{
                        completion_rate: progress.completion_percentage,
                        solved_questions: progress.solved_count,
                        flagged_questions: progress.flagged_count,
                        average_confidence: progress.average_confidence
                    }});
                    
                    Object.keys(progress.question_status).forEach(qNum => {{
                        const status = progress.question_status[qNum];
                        updateQuestionStatus(parseInt(qNum), status);
                    }});
                    
                    showNotification('🔄 Progress refreshed from master file!');
                }}
            }})
            .catch(error => console.error('Progress refresh error:', error));
        }}
        
        function getBatchPrompts() {{
            let allPrompts = '';
            for (let i = 1; i <= totalQuestions; i++) {{
                allPrompts += `=== QUESTION ${{i}} ===\\n`;
                allPrompts += generatePrompt(i) + '\\n\\n';
            }}
            
            navigator.clipboard.writeText(allPrompts).then(() => {{
                showNotification(`📋 All ${{totalQuestions}} prompts copied to clipboard!`);
            }}).catch(() => {{
                showNotification('Clipboard failed. Opening in new window...', 'warning');
                const newWindow = window.open('', '_blank');
                newWindow.document.write(`<pre>${{allPrompts}}</pre>`);
            }});
        }}
        
        function exportSolutions() {{
            fetch('/api/export-solutions', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ paper_folder: paperFolder }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    showNotification(`📥 Backup created: ${{data.export_filename}}`);
                    
                    const link = document.createElement('a');
                    link.href = `/download-backup/${{paperFolder}}/${{data.export_filename}}`;
                    link.download = data.export_filename;
                    link.click();
                }} else {{
                    showNotification(`⚠ Backup failed: ${{data.error}}`, 'error');
                }}
            }})
            .catch(error => {{
                showNotification(`⚠ Export error: ${{error.message}}`, 'error');
            }});
        }}
        
        function openImage(imageUrl) {{
            window.open(imageUrl, '_blank');
        }}
        
        // Initialize enhanced system
        window.addEventListener('load', () => {{
            setTimeout(() => {{
                refreshProgress();
                showNotification('🚀 Enhanced AI Solver loaded - Claude API integration ready!');
            }}, 500);
        }});
        
        // Auto-refresh progress every 30 seconds
        setInterval(refreshProgress, 30000);
        
        console.log('🎯 Enhanced AI Solver with 91% Quality Threshold initialized!');
    </script>
    '''