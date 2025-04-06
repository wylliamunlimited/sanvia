import React, { useEffect, useState } from "react";
import styles from "./Static.module.css";
import { useNavigate } from "react-router-dom";

const Static: React.FC = () => {
  const navigate = useNavigate();
  const [showAbout, setShowAbout] = useState(false);

  useEffect(() => {
    // Set the amber gradient background for the body
    document.body.style.background = "black";
    document.body.style.height = "100vh";
    document.body.style.margin = "0";
    document.body.style.overflow = "hidden";
    const isLargeScreen = window.innerWidth > 1000;
    const specificCircleData = [
      {
        width: isLargeScreen ? 70 : 50,
        left: isLargeScreen ? -20 : -10,
        top: 0,
        opacity: 0.8,
      },
    ];

    // Remove any existing circles before adding new ones
    document.querySelectorAll(".random-circle").forEach(circle => circle.remove());

    // Add circles to the body based on specific positions
    specificCircleData.forEach((circleData, index) => {
      const circle = document.createElement("img");
      circle.src = "/images/Ellipse2.png"; // Your circle image source
      circle.classList.add("random-circle");
      circle.style.position = "absolute";
      circle.style.width = `${circleData.width}px`;
      circle.style.left = `${circleData.left}vw`; // Using specific values (vw)
      circle.style.top = `${circleData.top}vh`; // Using specific values (vh)
      circle.style.opacity = `${circleData.opacity}`;
      circle.style.zIndex = "-1"; // Set behind content

      document.body.appendChild(circle); // Append the circle to the body
    });
  }, []);

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
