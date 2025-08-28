// Fix for Review tab JavaScript functions
window.reviewFixes = {
    cancelReplacement: function(questionNumber) {
        fetch('/api/review/cancel-replacement', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question_number: questionNumber })
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            const card = document.getElementById('image-card-' + questionNumber);
            const previewDiv = document.getElementById('preview-' + questionNumber);
            
            card.classList.remove('has-replacement');
            previewDiv.classList.remove('active');
            
            delete pendingReplacements[questionNumber];
            updatePendingCount();
            
            showAlert('reviewStatus', 'info', 'Replacement cancelled');
        })
        .catch(function(error) {
            const card = document.getElementById('image-card-' + questionNumber);
            const previewDiv = document.getElementById('preview-' + questionNumber);
            
            card.classList.remove('has-replacement');
            previewDiv.classList.remove('active');
            
            delete pendingReplacements[questionNumber];
            updatePendingCount();
            
            showAlert('reviewStatus', 'warning', 'Replacement cancelled');
        });
    }
};

// Override the global function
window.cancelReplacement = window.reviewFixes.cancelReplacement;

console.log('Review fixes loaded');
