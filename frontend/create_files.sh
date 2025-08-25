#!/bin/bash

echo "Creating AI Tutor Frontend Structure..."

# Create directories
mkdir -p src/components
mkdir -p src/screens  
mkdir -p src/services
mkdir -p src/styles
mkdir -p src/utils
mkdir -p src/hooks

echo "✅ Directories created"

# Create component files
touch src/components/QuestionCard.js
touch src/components/ErrorBoundary.js

echo "✅ Component files created"

# Create screen files
touch src/screens/StartScreen.js
touch src/screens/ResultScreen.js
touch src/screens/ReviewScreen.js

echo "✅ Screen files created"

# Create service files
touch src/services/questionService.js

echo "✅ Service files created"

# Create style files
touch src/styles/theme.js

echo "✅ Style files created"

# Update main files (preserve existing content)
if [ ! -f src/App.js ]; then
    touch src/App.js
fi
if [ ! -f src/index.css ]; then
    touch src/index.css
fi

echo "✅ Main files ready"

echo ""
echo "📁 Complete structure created:"
echo "src/"
echo "├── App.js"
echo "├── index.css"
echo "├── components/"
echo "│   ├── QuestionCard.js"
echo "│   └── ErrorBoundary.js"
echo "├── screens/"
echo "│   ├── StartScreen.js"
echo "│   ├── ResultScreen.js"
echo "│   └── ReviewScreen.js"
echo "├── services/"
echo "│   └── questionService.js"
echo "├── styles/"
echo "│   └── theme.js"
echo "├── utils/"
echo "└── hooks/"
echo ""
echo "🎯 Next steps:"
echo "1. Run this script: chmod +x create_files.sh && ./create_files.sh"
echo "2. Copy the provided code into each file"
echo "3. Update questionService.js paths to point to ../question_banks/"
echo "4. Install dependencies: npm install lucide-react"

