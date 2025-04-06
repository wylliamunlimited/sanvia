import React, { useEffect, useState } from "react";
import styles from "./Static.module.css";
import { useNavigate } from "react-router-dom";

const Static: React.FC = () => {
  const navigate = useNavigate();
  const [showAbout, setShowAbout] = useState(false);


  return (
    <div className={styles.home}>
      {/* Top navigation */}
      <nav className={styles.navbar}>
        <div className={styles["nav-left"]}>
          <a href="" onClick={() => setShowAbout(false)}>HOME</a>
          <a href="#about" onClick={() => setShowAbout(true)}>ABOUT</a>
        </div>
        <img className = {styles.line}/>        
          <div className={styles["nav-right"]}>
          <a onClick={() => navigate("/auth/login")}>LOG IN</a>
        </div>
      </nav>

      {/* about page information */}
      {showAbout && (
        <div className={styles["about-page"]}>
          <h2>Sanvia Mission Statement</h2>
        </div>
      )}

      <div style={{ display: showAbout ? "none" : "block" }}>
        {/* Brand intro */}
        <div className={styles.content} >
          <div id="header">
          <h1 className={styles.title}>Welcome to</h1>
          <h1 className={styles.brand}>Sanvia</h1>
          </div>
          <button className={styles["get-started"]} onClick={() => navigate("/auth/signup")}>
            ↗ get started
          </button>
        </div>
      
        {/* Cards */}
        <div className={styles["info-section"]}>
          {/* individual 3 squares for the middle */}
          <div className={styles.card}>
          <img src="/images/static1.png" 
            alt="logo" 
            style={{height:"30vh", paddingTop: "5px"}}/>
          </div>
          <div className={styles.card}>
            <img id= "extra" src="/images/static3.png" alt="app logo"/>
          </div>
          <div className={styles.card2}>
            <div className={styles.promise}>
              <h3>OUR MISSION</h3>
              <p>
                Our mission is to make reliable health information accessible to
                everyone through our AI-powered web application. Sanvia simplifies
                complex medical knowledge, providing clear, personalized insights
                from trusted sources. We aim to bridge the gap between healthcare
                and everyday users, ensuring informed decision-making and better
                health outcomes.
              </p>
              <a href="#about" onClick={() => setShowAbout(true)} className={styles["read-more"]}>
                Read more ↗
              </a>
              </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Static;
