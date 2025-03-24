import React, { useEffect, useState } from "react";
import styles from "./Static.module.css";
import { useNavigate } from "react-router-dom";

const Static: React.FC = () => {
  const navigate = useNavigate();
  const [showAbout, setShowAbout] = useState(false);

  useEffect(() => {
    // the amber gradient background
    document.body.style.background = "linear-gradient(to top right, #4c8ddd,rgb(239, 228, 228) 60%)";
    document.body.style.height = "100vh";
    document.body.style.margin = "0";
    document.body.style.overflow = "hidden"; 

    const numCircles = 10;
    const container = document.body;

    // Remove existing circles before adding new ones
    let circlesData = localStorage.getItem("circlesData");

    if (!circlesData) {
      const fixedCircleData = Array.from({ length: numCircles }).map(() => ({
        width: Math.random() * 100 + 20, 
        left: Math.random() * 100, 
        top: Math.random() * 100, 
        opacity: Math.random() * 0.5 + 0.5, 
      }));
      
      // Save the generated positions to localStorage
      localStorage.setItem("circlesData", JSON.stringify(fixedCircleData));
      circlesData = JSON.stringify(fixedCircleData); 
    }

    const parsedCircles = JSON.parse(circlesData);

    // Remove any existing circles before adding new ones
    document.querySelectorAll(".random-circle").forEach(circle => circle.remove());
    //creating new circles
    parsedCircles.forEach((circleData, index) => {
      const circle = document.createElement("img");
      circle.src = "/images/Ellipse.png"; 
      circle.classList.add("random-circle"); 
      circle.style.position = "absolute";
      circle.style.width = `${circleData.width}px`; 
      circle.style.left = `${circleData.left}vw`; 
      circle.style.top = `${circleData.top}vh`; 
      circle.style.opacity = `${circleData.opacity}`;
      circle.style.zIndex = "-1"; 

      container.appendChild(circle);
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
        <div className={styles["nav-right"]}>
          <a onClick={() => navigate("/auth/login")}>CHAT NOW</a>
        </div>
      </nav>

      {/* about page information */}
      {showAbout && (
        <div className={styles["about-page"]}>
          <h2>Sanvia Mission Statement</h2>
          <br></br>
          <p>At Sanvia, we believe that access to reliable, understandable, and personalized 
            health information is a fundamental right. Our AI-integrated web application is 
            designed to bridge the gap between complex medical knowledge and everyday users, 
            empowering individuals to make informed decisions about their health. 
          </p>
          <p>Sanvia leverages advanced AI technology to provide clear, concise, and personalized 
            insights based on trusted medical sources. Whether you're looking to understand symptoms, 
            explore treatment options, or gain knowledge about a medical condition, our platform 
            ensures that accurate information is always within reach. 
          </p>
          <p>
            Our mission is to eliminate barriers to health literacy by offering an intuitive, user-friendly 
            experience tailored to diverse needs. By combining cutting-edge AI with a human-centered 
            approach, we strive to make healthcare information more transparent, accessible, and 
            actionable for everyone.
          </p>
            <p>At Sanvia, we are not just creating a tool—we are fostering a future where knowledge leads to better health outcomes.
            </p>
        </div>
      )}

      <div style={{ display: showAbout ? "none" : "block" }}>
        {/* Brand intro */}
        <div className={styles.content} >
          <div id="header">
            <h1>Welcome to</h1>
            <h1> <span className={styles.highlight}>sanvia</span></h1>
          </div>
          <button className={styles["get-started"]} onClick={() => navigate("/auth/signup")}>
            ↗ get started
          </button>
        </div>
      
        {/* Cards */}
        <div className={styles["info-section"]}>
          {/* individual 3 squares for the middle */}
          <div className={styles.card}>
            <div className="logo-static-section">
              <div className="logo-static-container">
                <img id="logo-static" src="/images/logo1.png" alt="Logo" />
              </div>
            </div>
          </div>
          <div className={styles.card}>
            <img src="/images/static2.png" alt="app logo" />
          </div>
          <div className={styles.card}>
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
              <a href="#read-more" className={styles["read-more"]}>
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
