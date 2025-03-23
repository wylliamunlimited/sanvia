import React, { useEffect } from "react";
import styles from "./Static.module.css";
import { useNavigate } from "react-router-dom";

const Static: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Apply the amber gradient background
    document.body.style.background = "linear-gradient(to top right, #4c8ddd, #f5f5f5 60%)";
    document.body.style.height = "100vh";
    document.body.style.margin = "0";
    document.body.style.overflow = "hidden"; // Prevents scrolling issues

    const numCircles = 10; // Number of circles to generate
    const container = document.body;

    // Remove existing circles before adding new ones
    let circlesData = localStorage.getItem("circlesData");

    if (!circlesData) {
      // If no circle data exists, create fixed random placements
      const fixedCircleData = Array.from({ length: numCircles }).map(() => ({
        width: Math.random() * 100 + 20, // Random size (20px - 120px)
        left: Math.random() * 100, // Random horizontal position (percentage of viewport width)
        top: Math.random() * 100, // Random vertical position (percentage of viewport height)
        opacity: Math.random() * 0.5 + 0.5, // Random opacity (0.5 - 1)
      }));
      
      // Save the generated positions to localStorage
      localStorage.setItem("circlesData", JSON.stringify(fixedCircleData));
      circlesData = JSON.stringify(fixedCircleData); // Use newly created data
    }

    const parsedCircles = JSON.parse(circlesData);

    // Remove any existing circles before adding new ones
    document.querySelectorAll(".random-circle").forEach(circle => circle.remove());

    parsedCircles.forEach((circleData, index) => {
      const circle = document.createElement("img");
      circle.src = "/images/Ellipse.png"; // Ensure this path is correct
      circle.classList.add("random-circle"); // Add class for easy cleanup
      circle.style.position = "absolute";
      circle.style.width = `${circleData.width}px`; // Set size from stored data
      circle.style.left = `${circleData.left}vw`; // Set position from stored data
      circle.style.top = `${circleData.top}vh`; // Set position from stored data
      circle.style.opacity = `${circleData.opacity}`; // Set opacity from stored data
      circle.style.zIndex = "-1"; // Keeps circles behind all other elements

      container.appendChild(circle);
    });
  }, []);

  return (
    <div className={styles.home}>
      <nav className={styles.navbar}>
        <div className={styles["nav-left"]}>
          <a href="#home">HOME</a>
          <a href="#about">ABOUT</a>
        </div>
        <div className={styles["nav-right"]}>
          <a onClick={() => navigate("/auth/login")}>CHAT NOW</a>
        </div>
      </nav>

      <div className={styles.content}>
        <div id = "header">
          <h1>
            welcome to 
          </h1>
          <h1><span className={styles.highlight}>sanvia</span></h1> 
        </div>
        <button className={styles["get-started"]} onClick={() => navigate("/auth/signup")}>
          ↗ get started
        </button>
      </div>

      <div className={styles["info-section"]}>
        <div className={styles.card}>
          <div className="logo-section">
            <div className="logo-container">
              <img src="/images/logo1.png" alt="Logo" />
              <span className="logo-text">Sanvia</span>
            </div>
          </div>
        </div>
        <div className={styles.card}>
          <img src="path-to-sanvia-app-logo" alt="app logo" />
        </div>
        <div className={styles.card}>
          <div className={styles.promise}>
            <h3>OUR MISSION</h3>
            <p>Our main goal is to make health information accessible via our AI web application etc</p>
            <p>Some more info bla bla bla</p>
            <a href="#read-more" className={styles["read-more"]}>
              Read more ↗
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Static;
