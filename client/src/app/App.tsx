import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css'
import Sidebar from '../components/Sidebar/Sidebar'
import Chat from '../components/Chat/Chat'
import Documents from '../components/Documents/Documents'
import History from '../components/History/History'
import SignUp from '../components/SignUp/SignUp'
import Login from '../components/Login/Login'
import Survey from '../components/Survey/Survey'



function App() {
  const [activeSection, setActiveSection] = useState('chat')
  const [isSidebarOpen, setSidebarOpen] = useState(true)
  const [isLogged, setIsLogged] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false); 

  const getActiveComponent = () => {
    if (activeSection === 'chat') {
      return <Chat />
    } else if (activeSection === 'documents') {
      return <Documents />
    } else if (activeSection === 'history') {
      return <History />
    } else {
      return <Chat />
    }
  }

  return (
    <Router>
      <Routes>
        {/* Login/Register Route */}
        <Route
          path="/auth/signup"
          element={
            isSignUp? (
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
        <Route
          path="/auth/login"
          element={
            isLogged ? (
              <Navigate to="/" replace />
            ) : (
              <Login
                onLoginSuccess={() => {
                  setIsLogged(true);
                  localStorage.setItem('isLogged', 'true');
                }}
              />
            )
          }
        />
        <Route
          path="/auth/survey"
          element={
            isSignUp ? (
              <Survey />
            ) : (
              <Navigate to="/auth/login" replace />
            )
          }
        />
        <Route 
          path="/*" 
          element={isLogged ? (
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
          ) : <Navigate to="/auth/login" replace/>}
        />
      </Routes>
    </Router>
  );
}

export default App;