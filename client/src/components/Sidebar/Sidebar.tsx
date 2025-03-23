import { useEffect, useState } from 'react'
import './Sidebar.css'
import { useNavigate } from 'react-router-dom'
import { firestoreApi } from '../../api/firestoreApi'
import Profile from '../Profile/Profile.tsx'
import { useAuth } from '../../provider/AuthContext'

type NavItem = {
  id: string
  label: string
  icon: React.ReactNode
}

type SidebarProps = {
  activeSection: string
  onSectionChange: (section: string) => void
  onCollapse: () => void
}

const navItems: NavItem[] = [
  {
    id: 'chat',
    label: 'Chat',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    )
  },
  {
    id: 'documents',
    label: 'Documents',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
      </svg>
    )
  },
  {
    id: 'history',
    label: 'History',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 8v4l3 3" />
        <circle cx="12" cy="12" r="9" />
      </svg>
    )
  },


]



const Sidebar = ({ activeSection, onSectionChange, onCollapse }: SidebarProps) => {
  const [menuOpen, setMenuOpen] = useState(false)
  const [userName, setUserName] = useState("Anonymous");
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();


  const [userData, setUserData] = useState({
    firstName: '',
    lastName: '',
    height: '',
    weight: '',
    gender: '',
    sex: '',
    age: ''
  });

  // const userInitials = 'YN'
  // Fetch profile only after the auth state is determined
  useEffect(() => {
    // Wait until loading is finished and the user is available
    if (loading) return;
    if (!user) {
      console.warn("No authenticated user found, skipping profile fetch.");
      return;
    }

    const fetchProfile = async () => {
      try {
        const data = await firestoreApi.get_user_profile();
        console.log(`Fetching user profile data: ${JSON.stringify(data)}...`);

        const fullName = `${data['first-name']} ${data['last-name']}`;
        setUserName(fullName);

        setUserData({
          firstName: data['first-name'],
          lastName: data['last-name'],
          height: data['Height'],
          weight: data['Weight'],
          gender: data['Gender'],
          sex: data['Sex'],
          age: data['Age']
        });

        console.log("Profile data fetched:", data);
      } catch (error) {
        console.error("Error fetching profile:", error);
      }
    };

    fetchProfile();
  }, [user, loading]);

  // const userInitials = 'JW'
  // userName = 'Justin Wang'
  const [showProfile, setShowProfile] = useState(false)

  // const userInitials = 'YN'
  const handleLogout = () => {
    setMenuOpen(false);
    logout();
    navigate('/auth/login');
  };

  const handleSave = (updatedData: typeof userData) => {
    console.log("Updated Profile:", updatedData);
    setUserData(updatedData);
    setShowProfile(false);
  };

  const menuItems = [
    {
      id: 'profile',
      label: 'Profile',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="7" r="4" />
          <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" />
        </svg>
      ),
      onClick: () => {
        console.log('Profile button clicked');
        setShowProfile(true);
        setMenuOpen(false);
      }
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      ),
      onClick: () => {
        console.log('Settings clicked');
        setMenuOpen(false);
      }
    },
    {
      id: 'feedback',
      label: 'Feedback',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      ),
      onClick: () => {
        console.log('Feedback clicked');
        setMenuOpen(false);
      }
    },
    {
      id: 'logout',
      label: 'Log out',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
      ),
      onClick: () => {
        console.log('Logout clicked');
        handleLogout();
        setMenuOpen(false);
      }
    },
  ]
  return (
    <div className="sidebar">
      <button
        className="collapse-button"
        onClick={onCollapse}
        aria-label="Collapse sidebar"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <div className="sidebar-header">
      </div>
      <div className="logo-section">
        <div className="logo-container">
          <img src="/images/logo.png" alt="Logo" />
          <span className="logo-text">Sanvia</span>
        </div>
      </div>
      <div className="sidebar-content">
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => onSectionChange(item.id)}
            >
              <span className="nav-item-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </div>
      <div className="profile-menu">
        <button
          className="profile-section"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          <div className="profile-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <span className="user-name">{userName}</span>
        </button>
        {menuOpen && (
          <div className="menu-dropdown">
            {menuItems.map(item => (
              <button
                key={item.id}
                className="menu-item"
                onClick={item.onClick}
              >
                <span className="menu-item-icon">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>
        )}
      </div>
      {showProfile && (
        <Profile
          {...userData}
          onClose={() => setShowProfile(false)}
          onSave={handleSave}
        />
      )}
    </div>
  )
}

export default Sidebar 