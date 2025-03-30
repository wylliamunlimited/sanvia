import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';

import './App.css'
import Sidebar from '../components/Sidebar/Sidebar'
import Chat from '../components/Chat/Chat'
import NewChat from '../components/Chat/NewChat'
import Documents from '../components/Documents/Documents'
import History from '../components/History/History'
import SignUp from '../components/SignUp/SignUp'
import Login from '../components/Login/Login'
import { FirebaseProvider } from '../provider/FirebaseContext';
import { AuthProvider, useAuth } from '../provider/AuthContext';
import { ProfileProvider } from '../provider/ProfileContext';
import Survey from '../components/Survey/Survey';

function App() {
  const [isSidebarOpen, setSidebarOpen] = useState(true)
  const [isSignUp, setIsSignUp] = useState(false);

  const AppRoutes = () => {
    const { user, loading } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    if (loading) return null;

    const getActiveSection = () => {
      const path = location.pathname;
      if (path.match(/^\/chat\/[^/]+$/)) return 'chat';
      if (path === '/') return 'chat';
      if (path === '/documents') return 'documents';
      if (path === '/history') return 'history';
      if (path === '/settings') return 'settings';
      if (path === '/chat') return '';
      return 'chat';
    };

    return (
      <Routes>
        {/* Sign-Up Route */}
        <Route
          path="/auth/signup"
          element={
            isSignUp ? (
              <Navigate to="/onboarding" replace />
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
              <Navigate to="/chat" replace />
            ) : (
              <Login
                onLoginSuccess={() => {
                  localStorage.setItem('isLogged', 'true');
                }}
              />
            ) 
          }
        />
        
        {/* Survey Route */}
        <Route
          path="/onboarding"
          element={
            user ? (
              <Survey
                onSurveyComplete={() => {
                  localStorage.setItem('isSurveyCompleted', 'true');
                }}
              />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        
        {/* Main App Routes */}
        <Route
          path="/*"
          element={user ? (
            <div className="app-container">
              {isSidebarOpen && (
                <Sidebar
                  activeSection={getActiveSection()}
                  onSectionChange={(section) => {
                    navigate(`/${section}`);
                  }}
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
                <Routes>
                  <Route path="/" element={<Navigate to="/chat" replace />} />
                  <Route path="/chat" element={<NewChat />} />
                  <Route path="/chat/:threadId" element={<Chat />} />
                  <Route path="/documents" element={<Documents />} />
                  <Route path="/history" element={<History />} />
                  <Route path="/settings" element={<div>Settings Page</div>} />
                  <Route path="*" element={<Navigate to="/chat" replace />} />
                </Routes>
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
        <ProfileProvider>
          <Router>
            <AppRoutes></AppRoutes>
          </Router>
        </ProfileProvider>
      </AuthProvider>
    </FirebaseProvider>
  );
}

export default App;
