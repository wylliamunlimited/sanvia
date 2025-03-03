import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Sidebar from '../components/Sidebar/Sidebar';
import Chat from '../components/Chat/Chat';
import Documents from '../components/Documents/Documents';
import History from '../components/History/History';
import SignUp from '../components/SignUp/SignUp';
import Login from '../components/Login/Login';
import Survey from '../components/Survey/Survey';

function App() {
  const [activeSection, setActiveSection] = useState<string>('chat');
  const [isSidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [isLogged, setIsLogged] = useState<boolean>(false);
  const [isSignUp, setIsSignUp] = useState<boolean>(false);
  const [isSurveyCompleted, setIsSurveyCompleted] = useState<boolean>(false);

  useEffect(() => {
    // Checking localStorage to persist state across page reloads
    const logged = localStorage.getItem('isLogged') === 'true';
    const signedUp = localStorage.getItem('isSignUp') === 'true';
    const surveyCompleted = localStorage.getItem('isSurveyCompleted') === 'true';
    
    setIsLogged(logged);
    setIsSignUp(signedUp);
    setIsSurveyCompleted(surveyCompleted);
  }, []);

  useEffect(() => {
    // Persist state to localStorage whenever there is a change
    localStorage.setItem('isLogged', isLogged.toString());
    localStorage.setItem('isSignUp', isSignUp.toString());
    localStorage.setItem('isSurveyCompleted', isSurveyCompleted.toString());
  }, [isLogged, isSignUp, isSurveyCompleted]);

  const getActiveComponent = () => {
    switch (activeSection) {
      case 'chat': return <Chat />;
      case 'documents': return <Documents />;
      case 'history': return <History />;
      default: return <Chat />;
    }
  };

  return (
    <Router>
      <Routes>
        {/* Sign-Up Route */}
        <Route
          path="/auth/signup"
          element={
            !isSignUp ? (
              <SignUp
                onSignUpSuccess={() => {
                  setIsSignUp(true);
                  localStorage.setItem('isSignUp', 'true');
                }}
              />
            ) : (
              <Navigate to="/auth/survey" replace />
            )
          }
        />

        {/* Login Route */}
        <Route
          path="/auth/login"
          element={
            !isLogged ? (
              <Login
                onLoginSuccess={() => {
                  setIsLogged(true);
                  localStorage.setItem('isLogged', 'true');
                }}
              />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Survey Route */}
        <Route
          path="/auth/survey"
          element={
            isSignUp && !isSurveyCompleted ? (
              <Survey
                onSurveyComplete={() => {
                  setIsSurveyCompleted(true);
                  localStorage.setItem('isSurveyCompleted', 'true');
                }}
              />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Home Page (Main App) */}
        <Route 
          path="/*" 
          element={
            isLogged || isSurveyCompleted ? (
              <div className="app-container">
                {isSidebarOpen && (
                  <Sidebar 
                    activeSection={activeSection} 
                    onSectionChange={setActiveSection}
                    onCollapse={() => setSidebarOpen(false)}
                  />
                )}
                <div className="main-section">
                  {!isSidebarOpen && (
                    <button 
                      className="open-sidebar-button"
                      onClick={() => setSidebarOpen(true)}
                      aria-label="Open sidebar"
                    >
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="9 18 15 12 9 6"/>
                      </svg>
                    </button>
                  )}
                  {getActiveComponent()}
                </div>
              </div>
            ) : (
              <Navigate to="/auth/login" replace />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
