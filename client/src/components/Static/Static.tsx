import react from "react";
import styles from './Static.module.css';
import { useNavigate } from "react-router-dom";

const Static: React.FC = () => {
const navigate = useNavigate();
  return (
    <div className={styles.home}>
      <nav className={styles.navbar}>
        <div className={styles['nav-left']}>
        {/* nothing in here yet bc we havent decided what to write */}
          <a href="#home">HOME</a>
          <a href="#about">ABOUT</a>
        </div>
        <div className={styles['nav-right']}>
        {/* sends the user to login to start using the app */}
          <a onClick={() => navigate("/auth/login")}>CHAT NOW</a>
        </div>
      </nav>

      <div className={styles.content}>
        <h1>
          welcome to <span className={styles.highlight}>sanvia</span>
        </h1>
        {/* sends the user to sign up to create an account to use the app */}
        <button className={styles['get-started']} onClick={() => navigate("/auth/signup")}>
          ↗ get started
        </button>
      </div>

      <div className={styles['info-section']}>
        {/* We will add the final logo  */}
        <div className={styles.card}>
            <div className="logo-section">
                <div className="logo-container">
                    <img src="/images/logo1.png" alt="Logo" />
                <span className="logo-text">Sanvia</span>
            </div>
      </div>
        </div>
        <div className={styles.card}>
        {/* will be added once the final app logo is done */}
          <img src="path-to-sanvia-app-ogo" alt="app logo" />
        </div>
        <div className={styles.card}>
          <div className={styles.promise}>
            <h3>OUR MISSION</h3>
            <p>
              Our main goal is to make health information accesible via our ai web application etc 
            </p>
            <p>
                Some more info bla bla bla
            </p>
            {/* Nothing here yet either need to decide what to write */}
            <a href="#read-more" className={styles['read-more']}>
              Read more ↗
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Static;