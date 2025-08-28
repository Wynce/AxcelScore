# AxcelScore Quiz App

A comprehensive React-based quiz application with multiple question banks, timer functionality, and detailed review system.

## Features

- **Multi-Question Bank System**: Automatic discovery and selection of question banks
- **Timer-Based Quizzes**: Both total quiz timer and per-question timers
- **Three UI Themes**: Light, Dark, and Gen Alpha (animated gradient with glassmorphism)
- **Comprehensive Review System**: Step-by-step solutions with detailed explanations
- **Retest Functionality**: Focus on incorrect questions for targeted practice
- **Performance Analytics**: Detailed result screens with scoring breakdown

## Tech Stack

- React + Vite
- CSS3 with advanced animations and glassmorphism effects
- Question bank system with JSON data structure
- Image support for questions and solutions

## Project Structure

AxcelScore/
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── screens/
│   │   ├── services/
│   │   └── styles/
│   ├── public/
│   └── package.json
├── backend/               # AI solver backend (Python)
├── question_banks/        # Question data and images
└── README.md

## Local Development Setup

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository:
git clone https://github.com/Wynce/AxcelScore.git
cd AxcelScore

2. Install frontend dependencies:
cd frontend
npm install

3. Start development server:
npm run dev

## Deployment

### Vercel Deployment (Frontend)

1. Navigate to frontend directory:
cd frontend

2. Deploy to Vercel:
npm install -g vercel
vercel --prod

## Question Bank Structure

Place your question banks in the question_banks directory with this structure:

question_banks/
├── physics_2023_oct_13/
│   ├── physics_2023_oct_13.json
│   ├── solutions.json
│   ├── metadata.json
│   └── images/
├── physics_2025_mar_13/
└── physics_2025_may_13/

## Contributing

1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support, email wynceaxcel@gmail.com or create an issue in the GitHub repository.
