# 🎯 AxcelScore

**AI-Powered Question Bank Generator & Smart Tutoring Platform**

AxcelScore transforms PDF exam papers into interactive question banks with AI-powered solving capabilities. Built for IGCSE, A-Levels, and similar educational assessments.

## ✨ Features

### 🔍 Smart PDF Processing
- **Multi-Strategy Question Detection**: 7 different algorithms to identify questions
- **High-Quality Image Extraction**: 2x resolution with enhancement
- **Intelligent Boundary Detection**: Accurately separates questions and answers

### 🤖 AI Integration  
- **Claude Sonnet 4**: Advanced reasoning for complex problems
- **Step-by-Step Solutions**: Detailed explanations for learning
- **Multiple Subject Support**: Physics, Chemistry, Biology, Mathematics, and more

### 🌐 Modern Web Interface
- **Drag & Drop Upload**: Intuitive PDF processing
- **Real-Time Progress**: Live extraction feedback
- **Responsive Design**: Works on desktop and mobile
- **Professional UI**: Clean, modern interface

### 🚀 Production Ready
- **Vercel Deployment**: Serverless hosting
- **GitHub Integration**: Professional development workflow
- **Standardized Structure**: Clean, maintainable codebase
- **Comprehensive Testing**: Reliable extraction pipeline

## 🛠️ Tech Stack

**Frontend:**
- React.js with modern hooks
- Tailwind CSS for styling
- Responsive design principles

**Backend:** 
- Python Flask API
- PyMuPDF for PDF processing
- PIL for image enhancement
- Advanced NLP for question detection

**AI/ML:**
- Anthropic Claude API integration
- Multi-modal processing (text + images)
- Intelligent problem-solving algorithms

**Deployment:**
- Vercel for frontend hosting
- GitHub for version control
- Automated CI/CD pipeline

## 📁 Project Structure

```
AxcelScore/
├── frontend/              # React application
├── backend/               # Python Flask API
├── question_banks/        # Generated question banks
├── docs/                  # Documentation
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── package.json          # Node.js dependencies
└── vercel.json           # Deployment configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AxcelScore.git
   cd AxcelScore
   ```

2. **Set up backend**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your API keys and configuration
   ```

5. **Run the application**
   ```bash
   python backend/main.py
   ```

## 🎯 Usage

### PDF Processing
1. Upload your PDF exam paper
2. Select subject, year, and session
3. Click "Extract Questions" 
4. Get AI-generated question bank

### AI Tutoring
1. Browse extracted questions
2. Get instant AI solutions
3. Learn with step-by-step explanations
4. Track your progress

## 📊 Supported Formats

- **Exam Boards**: Cambridge IGCSE, A-Levels, IB
- **Subjects**: Physics, Chemistry, Biology, Mathematics, English, Economics
- **File Types**: PDF (optimized for exam papers)
- **Languages**: English (primary), with multi-language support planned

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Anthropic for Claude API
- Cambridge Assessment for educational standards
- Open source community for amazing tools

## 📞 Support

- 📧 Email: support@axcelscore.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/AxcelScore/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/AxcelScore/discussions)

---

**Made with ❤️ for educators and students worldwide**
