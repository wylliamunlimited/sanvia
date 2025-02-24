import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css'
import Sidebar from '../components/Sidebar/Sidebar'
import Chat from '../components/Chat/Chat'
import Documents from '../components/Documents/Documents'
import History from '../components/History/History'
import Register from '../components/Register/Register'
import Login from '../components/Login/Login'


function App() {
  const [activeSection, setActiveSection] = useState('chat')
  const [isSidebarOpen, setSidebarOpen] = useState(true)
  const [isLogged, setIsLogged] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false); 

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
          path="/register"
          element={
            isRegistered ? (
              <Navigate to="/login" replace />
            ) : (
              <Register
                onRegisterSuccess={() => {
                  setIsRegistered(true);
                  localStorage.setItem('isRegistered', 'true');
                }}
              />
            )
          }
        />
        <Route
          path="/login"
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
          ) : <Navigate to="/login" replace/>}
        />
      </Routes>
    </Router>
  );
}

export default App;