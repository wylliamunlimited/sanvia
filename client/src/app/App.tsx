import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';

import './App.css'
import Sidebar from '../features/sidebar/components/Sidebar'
import Chat from '../features/chat/components/Chat'
import NewChat from '../features/chat/components/NewChat'
import Documents from '../features/documents/components/Documents'
import History from '../features/history/components/History'
import SignUp from '../features/auth/components/SignUp'
import Login from '../features/auth/components/Login'
import { FirebaseProvider } from '../context/FirebaseContext';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { ProfileProvider } from '../context/ProfileContext';
import AnimatedSurvey from '../features/onboarding/components/Survey';
import ProfilePage from '../features/profile/components/Profile';

function App() {
  // const [activeSection, setActiveSection] = useState('chat')
  const [isSidebarOpen, setSidebarOpen] = useState(true)
  const [isSignUp, setIsSignUp] = useState(false);
  // const [isSurveyCompleted, setIsSurveyCompleted] = useState(false);

  // const getActiveComponent = () => {
  //   switch (activeSection) {
  //     case 'chat': return <Chat />;
  //     case 'documents': return <Documents />;
  //     case 'history': return <History />;
  //     default: return <Chat />;
  //   }
  // };

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
      if (path === '/profile') return 'profile';
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
              <AnimatedSurvey
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
                  <Route path="/profile" element={<ProfilePage />} />
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