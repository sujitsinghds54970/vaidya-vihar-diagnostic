import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Toaster } from 'react-hot-toast';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Toaster position="top-right" />
          {/* Import the main page component */}
          {React.lazy(() => import('./pages/index'))}
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
