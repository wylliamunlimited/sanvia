import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import './App.css'
import Sidebar from '../components/Sidebar/Sidebar'
import Chat from '../components/Chat/Chat'
import Documents from '../components/Documents/Documents'
import History from '../components/History/History'
import SignUp from '../components/SignUp/SignUp'
import Login from '../components/Login/Login'
import { FirebaseProvider } from '../provider/FirebaseContext';
import { AuthProvider, useAuth } from '../provider/AuthContext';
import Survey from '../components/Survey/Survey';


function App() {
  const [activeSection, setActiveSection] = useState('chat')
  const [isSidebarOpen, setSidebarOpen] = useState(true)
  // const [isLogged, setIsLogged] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  // const [isSurveyCompleted, setIsSurveyCompleted] = useState(false);

  const getActiveComponent = () => {
    switch (activeSection) {
      case 'chat': return <Chat />;
      case 'documents': return <Documents />;
      case 'history': return <History />;
      default: return <Chat />;
    }
  };

  const AppRoutes = () => {
    const { user, loading } = useAuth();

    if (loading) return <div>Loading...</div>;
    return (
      <Routes>
        {/* Sign-Up Route */}
        <Route
          path="/auth/signup"
          element={
            isSignUp ? (
              <Navigate to="/auth/survey" replace />
            ) : (
              <SignUp
                onSignUpSuccess={() => {
                  setIsSignUp(true);
                  localStorage.setItem('isSignUp', 'true');
                }}
              />
            ) 
          }
        />

        {/* Login Route */}
        <Route
          path="/auth/login"
          element={
            user ? (
              <Navigate to="/" replace />
            ) : (
              <Login
                onLoginSuccess={() => {
                  // setIsLogged(true);
                  localStorage.setItem('isLogged', 'true');
                }}
              />
            ) 
          }
        />

        
        {/* Survey Route */}
        <Route
          path="/auth/survey"
          element={
            user && isSignUp ? (
              <Survey
                onSurveyComplete={() => {
                  // setIsSurveyCompleted(true);
                  localStorage.setItem('isSurveyCompleted', 'true');
                }}
              />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        
        <Route
          path="/home"
          element={user ? (
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
                      <polyline points="9 18 15 12 9 6" />
                    </svg>
                  </button>
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
            </div>
          ) : <Navigate to="/auth/login" replace />}
        />
      </Routes>
    );

  };

  return (
    <FirebaseProvider>
      <AuthProvider>
        <Router>
          <AppRoutes></AppRoutes>
        </Router>
      </AuthProvider>
    </FirebaseProvider>
  );
}

export default App;