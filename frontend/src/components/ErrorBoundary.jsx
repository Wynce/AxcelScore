// ==============================
// 🛡️ components/ErrorBoundary.js - Error Handling Component
// ==============================
import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to console and capture error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // You can also log the error to an error reporting service here
    // logErrorToService(error, errorInfo);
  }

  handleReload = () => {
    // Reload the page to reset the application state
    window.location.reload();
  };

  handleGoHome = () => {
    // Reset error state and trigger navigation to home
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null 
    });
    
    // If the parent component has a navigation method, call it
    if (this.props.onNavigateHome) {
      this.props.onNavigateHome();
    } else {
      // Fallback: reload the page
      window.location.reload();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-white flex items-center justify-center p-6">
          <div className="max-w-md mx-auto text-center">
            {/* Error Icon */}
            <div className="w-20 h-20 bg-[#fdeaea] rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertTriangle size={40} className="text-[#F44336]" />
            </div>

            {/* Error Message */}
            <h1 className="text-2xl font-bold text-[#000000] mb-4">
              Oops! Something went wrong
            </h1>
            
            <p className="text-[#58585A] mb-6 leading-relaxed">
              We encountered an unexpected error while running the quiz application. 
              This might be due to a problem with loading questions or a technical issue.
            </p>

            {/* Error Details (Development Mode) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="bg-[#e9f0f6] border border-[#e5e6ea] rounded-lg p-4 mb-6 text-left">
                <h3 className="font-semibold text-[#F44336] mb-2">Error Details (Development Mode):</h3>
                <div className="text-sm text-[#000000] font-mono bg-white p-3 rounded border overflow-auto max-h-40">
                  <p><strong>Error:</strong> {this.state.error.toString()}</p>
                  {this.state.errorInfo.componentStack && (
                    <p className="mt-2">
                      <strong>Component Stack:</strong>
                      <pre className="whitespace-pre-wrap text-xs mt-1">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={this.handleReload}
                className="w-full bg-[#0453f1] text-white py-3 px-6 rounded-lg font-semibold hover:bg-[#0341c7] transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                <RefreshCw size={20} />
                <span>Reload Application</span>
              </button>
              
              <button
                onClick={this.handleGoHome}
                className="w-full bg-[#e5e6ea] text-[#000000] py-3 px-6 rounded-lg font-semibold hover:bg-[#d1d2d6] transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                <Home size={20} />
                <span>Go to Home</span>
              </button>
            </div>

            {/* Help Text */}
            <div className="mt-6 p-4 bg-[#f2e08a] rounded-lg">
              <h4 className="font-semibold text-[#000000] mb-2">
                💡 Troubleshooting Tips
              </h4>
              <ul className="text-sm text-[#000000] text-left space-y-1">
                <li>• Check if your question bank files are properly placed in the <code>question_banks</code> folder</li>
                <li>• Ensure all question JSON files have the correct format</li>
                <li>• Verify that image files exist in the respective <code>images</code> folders</li>
                <li>• Try refreshing the page or selecting a different question bank</li>
              </ul>
            </div>

            {/* Technical Information */}
            <div className="mt-4 text-xs text-[#58585A]">
              Error ID: {Date.now().toString(36)}
              <br />
              Time: {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      );
    }

    // If no error, render children normally
    return this.props.children;
  }
}

// Higher-order component wrapper for functional components
export const withErrorBoundary = (Component, errorBoundaryProps = {}) => {
  return function WrappedComponent(props) {
    return (
      <ErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
};

// Hook for error handling in functional components
export const useErrorHandler = () => {
  const [error, setError] = React.useState(null);

  const resetError = () => setError(null);
  
  const captureError = (error, errorInfo = {}) => {
    console.error('Error captured:', error, errorInfo);
    setError({ error, errorInfo });
  };

  React.useEffect(() => {
    if (error) {
      // You could trigger an error boundary here
      throw new Error(error.error?.message || 'An error occurred');
    }
  }, [error]);

  return { captureError, resetError };
};

export default ErrorBoundary;