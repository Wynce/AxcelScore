#!/usr/bin/env python3
"""
JavaScript Manager for AI Tutor Backend
Provides JavaScript functions and utilities for the web interface
"""

class JavaScriptManager:
    """Manages JavaScript functions for the web interface"""
    
    def __init__(self):
        pass
    
    def get_main_javascript(self):
        """Return the main JavaScript code for the interface"""
        return '''
        // Main JavaScript for AI Tutor Interface
        
        let currentFolder = null;
        let currentFiles = [];
        
        // File operations
        function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file first');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('File uploaded successfully!');
                    loadQuestionBanks();
                } else {
                    alert('Upload failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('Upload error: ' + error.message);
            });
        }
        
        function loadQuestionBanks() {
            fetch('/api/list-question-banks')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayQuestionBanks(data.folders);
                } else {
                    console.error('Error loading question banks:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        function displayQuestionBanks(folders) {
            const container = document.getElementById('questionBanks');
            if (!container) return;
            
            container.innerHTML = '<h3>📚 Question Banks</h3>';
            
            if (folders.length === 0) {
                container.innerHTML += '<p>No question banks found. Upload a PDF to get started.</p>';
                return;
            }
            
            folders.forEach(folder => {
                const folderDiv = document.createElement('div');
                folderDiv.className = 'folder-item';
                folderDiv.innerHTML = `
                    <div class="folder-header" onclick="toggleFolder('${folder.name}')">
                        <span class="folder-icon">📁</span>
                        <span class="folder-name">${folder.name}</span>
                        <span class="folder-toggle">▼</span>
                    </div>
                    <div class="folder-content" id="folder-${folder.name}" style="display: none;">
                        <div class="folder-actions">
                            <button onclick="extractQuestions('${folder.name}')">🔍 Extract Questions</button>
                            <button onclick="openAISolver('${folder.name}')">🤖 AI Solver</button>
                            <button onclick="deleteFolder('${folder.name}')">🗑️ Delete</button>
                        </div>
                        <div class="folder-files" id="files-${folder.name}">
                            Loading files...
                        </div>
                    </div>
                `;
                container.appendChild(folderDiv);
            });
        }
        
        function toggleFolder(folderName) {
            const content = document.getElementById(`folder-${folderName}`);
            const toggle = event.target.closest('.folder-header').querySelector('.folder-toggle');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                toggle.textContent = '▲';
                loadFolderFiles(folderName);
            } else {
                content.style.display = 'none';
                toggle.textContent = '▼';
            }
        }
        
        function loadFolderFiles(folderName) {
            fetch(`/api/list-files/${folderName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayFolderFiles(folderName, data.files);
                } else {
                    document.getElementById(`files-${folderName}`).innerHTML = 'Error loading files';
                }
            })
            .catch(error => {
                document.getElementById(`files-${folderName}`).innerHTML = 'Error loading files';
            });
        }
        
        function displayFolderFiles(folderName, files) {
            const container = document.getElementById(`files-${folderName}`);
            
            if (files.length === 0) {
                container.innerHTML = '<p>No files in this folder</p>';
                return;
            }
            
            container.innerHTML = '';
            files.forEach(file => {
                const fileDiv = document.createElement('div');
                fileDiv.className = 'file-item';
                fileDiv.innerHTML = `
                    <span class="file-icon">${getFileIcon(file.name)}</span>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                `;
                container.appendChild(fileDiv);
            });
        }
        
        function getFileIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            switch (ext) {
                case 'pdf': return '📄';
                case 'png': case 'jpg': case 'jpeg': return '🖼️';
                case 'json': return '📋';
                case 'html': return '🌐';
                default: return '📄';
            }
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function extractQuestions(folderName) {
            const button = event.target;
            button.disabled = true;
            button.textContent = '🔄 Extracting...';
            
            fetch('/api/extract-questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ folder_name: folderName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Extraction completed!\\nExtracted ${data.questions_extracted} questions`);
                    loadFolderFiles(folderName); // Refresh file list
                } else {
                    alert('❌ Extraction failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Extraction error: ' + error.message);
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = '🔍 Extract Questions';
            });
        }
        
        function openAISolver(folderName) {
            const button = event.target;
            button.disabled = true;
            button.textContent = '🔄 Initializing...';
            
            fetch('/api/ai-solver/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ paper_folder: folderName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Open AI Solver interface in new tab
                    window.open(`/ai-solver/${folderName}`, '_blank');
                } else {
                    alert('❌ AI Solver initialization failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ AI Solver error: ' + error.message);
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = '🤖 AI Solver';
            });
        }
        
        function deleteFolder(folderName) {
            if (!confirm(`Are you sure you want to delete "${folderName}"?\\nThis will delete all files in the folder.`)) {
                return;
            }
            
            fetch('/api/delete-folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ folder_name: folderName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Folder deleted successfully');
                    loadQuestionBanks(); // Refresh folder list
                } else {
                    alert('❌ Delete failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Delete error: ' + error.message);
            });
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            loadQuestionBanks();
            console.log('🚀 AI Tutor Interface loaded successfully');
        });
        
        // File input change handler
        document.addEventListener('DOMContentLoaded', function() {
            const fileInput = document.getElementById('fileInput');
            if (fileInput) {
                fileInput.addEventListener('change', function() {
                    const file = this.files[0];
                    if (file) {
                        document.getElementById('fileName').textContent = file.name;
                    }
                });
            }
        });
        '''
    
    def get_ai_solver_javascript(self):
        """Return JavaScript specifically for AI Solver interface"""
        return '''
        // AI Solver specific JavaScript
        let solutions = {};
        let currentProgress = {};
        
        function copyPrompt(questionNum) {
            // Implementation for copying prompts
            alert('Prompt copy functionality - to be implemented');
        }
        
        function saveSolution(questionNum) {
            // Implementation for saving solutions
            alert('Solution save functionality - to be implemented');
        }
        
        function validateJSON(questionNum) {
            // Implementation for validating JSON
            alert('JSON validation functionality - to be implemented');
        }
        '''

# Global function for backward compatibility
def get_main_javascript():
    """Global function that returns main JavaScript"""
    manager = JavaScriptManager()
    return manager.get_main_javascript()#!/usr/bin/env python3
"""
JavaScript Manager for AI Tutor Backend
Provides JavaScript functions and utilities for the web interface
"""

class JavaScriptManager:
    """Manages JavaScript functions for the web interface"""
    
    def __init__(self):
        pass
    
    def get_main_javascript(self):
        """Return the main JavaScript code for the interface"""
        return '''
        // Main JavaScript for AI Tutor Interface
        
        let currentFolder = null;
        let currentFiles = [];
        
        // File operations
        function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file first');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('File uploaded successfully!');
                    loadQuestionBanks();
                } else {
                    alert('Upload failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('Upload error: ' + error.message);
            });
        }
        
        function loadQuestionBanks() {
            fetch('/api/list-question-banks')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayQuestionBanks(data.folders);
                } else {
                    console.error('Error loading question banks:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        function displayQuestionBanks(folders) {
            const container = document.getElementById('questionBanks');
            if (!container) return;
            
            container.innerHTML = '<h3>📚 Question Banks</h3>';
            
            if (folders.length === 0) {
                container.innerHTML += '<p>No question banks found. Upload a PDF to get started.</p>';
                return;
            }
            
            folders.forEach(folder => {
                const folderDiv = document.createElement('div');
                folderDiv.className = 'folder-item';
                folderDiv.innerHTML = `
                    <div class="folder-header" onclick="toggleFolder('${folder.name}')">
                        <span class="folder-icon">📁</span>
                        <span class="folder-name">${folder.name}</span>
                        <span class="folder-toggle">▼</span>
                    </div>
                    <div class="folder-content" id="folder-${folder.name}" style="display: none;">
                        <div class="folder-actions">
                            <button onclick="extractQuestions('${folder.name}')">🔍 Extract Questions</button>
                            <button onclick="openAISolver('${folder.name}')">🤖 AI Solver</button>
                            <button onclick="deleteFolder('${folder.name}')">🗑️ Delete</button>
                        </div>
                        <div class="folder-files" id="files-${folder.name}">
                            Loading files...
                        </div>
                    </div>
                `;
                container.appendChild(folderDiv);
            });
        }
        
        function toggleFolder(folderName) {
            const content = document.getElementById(`folder-${folderName}`);
            const toggle = event.target.closest('.folder-header').querySelector('.folder-toggle');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                toggle.textContent = '▲';
                loadFolderFiles(folderName);
            } else {
                content.style.display = 'none';
                toggle.textContent = '▼';
            }
        }
        
        function loadFolderFiles(folderName) {
            fetch(`/api/list-files/${folderName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayFolderFiles(folderName, data.files);
                } else {
                    document.getElementById(`files-${folderName}`).innerHTML = 'Error loading files';
                }
            })
            .catch(error => {
                document.getElementById(`files-${folderName}`).innerHTML = 'Error loading files';
            });
        }
        
        function displayFolderFiles(folderName, files) {
            const container = document.getElementById(`files-${folderName}`);
            
            if (files.length === 0) {
                container.innerHTML = '<p>No files in this folder</p>';
                return;
            }
            
            container.innerHTML = '';
            files.forEach(file => {
                const fileDiv = document.createElement('div');
                fileDiv.className = 'file-item';
                fileDiv.innerHTML = `
                    <span class="file-icon">${getFileIcon(file.name)}</span>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                `;
                container.appendChild(fileDiv);
            });
        }
        
        function getFileIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            switch (ext) {
                case 'pdf': return '📄';
                case 'png': case 'jpg': case 'jpeg': return '🖼️';
                case 'json': return '📋';
                case 'html': return '🌐';
                default: return '📄';
            }
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function extractQuestions(folderName) {
            const button = event.target;
            button.disabled = true;
            button.textContent = '🔄 Extracting...';
            
            fetch('/api/extract-questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ folder_name: folderName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Extraction completed!\\nExtracted ${data.questions_extracted} questions`);
                    loadFolderFiles(folderName); // Refresh file list
                } else {
                    alert('❌ Extraction failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Extraction error: ' + error.message);
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = '🔍 Extract Questions';
            });
        }
        
        function openAISolver(folderName) {
            const button = event.target;
            button.disabled = true;
            button.textContent = '🔄 Initializing...';
            
            fetch('/api/ai-solver/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ paper_folder: folderName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Open AI Solver interface in new tab
                    window.open(`/ai-solver/${folderName}`, '_blank');
                } else {
                    alert('❌ AI Solver initialization failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ AI Solver error: ' + error.message);
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = '🤖 AI Solver';
            });
        }
        
        function deleteFolder(folderName) {
            if (!confirm(`Are you sure you want to delete "${folderName}"?\\nThis will delete all files in the folder.`)) {
                return;
            }
            
            fetch('/api/delete-folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ folder_name: folderName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Folder deleted successfully');
                    loadQuestionBanks(); // Refresh folder list
                } else {
                    alert('❌ Delete failed: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Delete error: ' + error.message);
            });
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            loadQuestionBanks();
            console.log('🚀 AI Tutor Interface loaded successfully');
        });
        
        // File input change handler
        document.addEventListener('DOMContentLoaded', function() {
            const fileInput = document.getElementById('fileInput');
            if (fileInput) {
                fileInput.addEventListener('change', function() {
                    const file = this.files[0];
                    if (file) {
                        document.getElementById('fileName').textContent = file.name;
                    }
                });
            }
        });
        '''
    
    def get_ai_solver_javascript(self):
        """Return JavaScript specifically for AI Solver interface"""
        return '''
        // AI Solver specific JavaScript
        let solutions = {};
        let currentProgress = {};
        
        function copyPrompt(questionNum) {
            // Implementation for copying prompts
            alert('Prompt copy functionality - to be implemented');
        }
        
        function saveSolution(questionNum) {
            // Implementation for saving solutions
            alert('Solution save functionality - to be implemented');
        }
        
        function validateJSON(questionNum) {
            // Implementation for validating JSON
            alert('JSON validation functionality - to be implemented');
        }
        '''

# Global function for backward compatibility
def get_main_javascript():
    """Global function that returns main JavaScript"""
    manager = JavaScriptManager()
    return manager.get_main_javascript()