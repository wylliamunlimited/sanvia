import { useState } from 'react'
import './App.css'
import Sidebar from '../components/Sidebar/Sidebar'
import Chat from '../components/Chat/Chat'
import Documents from '../components/Documents/Documents'
import History from '../components/History/History'

function App() {
  const [activeSection, setActiveSection] = useState('chat')
  const [isSidebarOpen, setSidebarOpen] = useState(true)

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
  )
}

export default App 