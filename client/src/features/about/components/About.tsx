import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './About.css';

const About = () => {
    const [activeSection, setActiveSection] = useState('about');
    const sections = useRef<{ [key: string]: HTMLDivElement | null }>({});
    const navigate = useNavigate();

    useEffect(() => {
        const handleScroll = () => {
            const scrollPosition = window.scrollY + window.innerHeight / 2;
            Object.entries(sections.current).forEach(([id, element]) => {
                if (element) {
                    const { offsetTop, offsetHeight } = element;
                    if (scrollPosition >= offsetTop && 
                        scrollPosition < offsetTop + offsetHeight) {
                        setActiveSection(id);
                    }
                }
            });
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToSection = (id: string) => {
        const element = sections.current[id];
        if (element) {
            const headerOffset = 80; // Height of the nav bar
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset - 20; // 20px spacing below nav
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    };

    const handleSectionRef = (id: string) => (el: HTMLDivElement | null) => {
        sections.current[id] = el;
    };

    return (
        <div className="about-container">
            <nav className="landing-nav">
                <div className="nav-left">
                    <span className="landing-logo-text">Sanvia</span>
                    <button className="nav-button about" onClick={() => navigate('/')}>Home</button>
                </div>
                <img src="./images/Vector.png" alt="Sanvia Logo" />
                <div className="nav-right">
                    <button 
                        className="nav-button login"
                        onClick={() => navigate('/auth/login')}
                    >
                        Log In
                    </button>
                    <button 
                        className="nav-button signup"
                        onClick={() => navigate('/waitlist')}
                    >
                        Waitlist
                    </button>
                </div>
            </nav>

            <div className="about-content">
                <div className="vertical-nav">
                    <button 
                        className={`nav-button ${activeSection === 'about' ? 'active' : ''}`}
                        onClick={() => scrollToSection('about')}
                    >
                        About
                    </button>
                    <button 
                        className={`nav-button ${activeSection === 'privacy' ? 'active' : ''}`}
                        onClick={() => scrollToSection('privacy')}
                    >
                        Privacy
                    </button>
                    <button 
                        className={`nav-button ${activeSection === 'terms' ? 'active' : ''}`}
                        onClick={() => scrollToSection('terms')}
                    >
                        Terms
                    </button>
                </div>

                <div className="sections-container">
                    <section 
                        id="about" 
                        ref={handleSectionRef('about')}
                        className="about-section"
                    >
                        <h1>About Sanvia</h1>
                        <p className="about-description">
                            Sanvia is revolutionizing healthcare by making medical information accessible and understandable.
                        </p>
                        <div className="spacer"></div>
                        <div className="about-content">
                            <h3>Our Mission</h3>
                            <p>
                                Sanvia is an AI-powered platform that transforms how people understand their medical information. We combine your personal health data with trusted medical sources to provide clear, personalized answers to your health questions.
                            </p>

                            <h3>How We Help</h3>
                            <p>
                                Unlike traditional search engines, Sanvia:
                            </p>
                            <ul>
                                <li>Processes complex medical questions with context</li>
                                <li>Connects with your health records and fitness trackers</li>
                                <li>Uses trusted medical sources like MD Wiki and Wikidocs</li>
                                <li>Provides personalized, easy-to-understand explanations</li>
                                <li>Helps you make informed decisions about your health</li>
                            </ul>

                            <h3>Why We Exist</h3>
                            <p>
                                People often turn to the internet for health information, but current solutions have limitations:
                            </p>
                            <ul>
                                <li>Generic health articles don't address individual needs</li>
                                <li>Online support groups may compromise privacy</li>
                                <li>Search engines can't understand complex medical context</li>
                                <li>Traditional methods don't connect with personal health data</li>
                            </ul>

                            <h3>Our Solution</h3>
                            <p>
                                Sanvia bridges these gaps by:
                            </p>
                            <ul>
                                <li>Using AI to understand your specific health situation</li>
                                <li>Maintaining privacy while providing personalized insights</li>
                                <li>Connecting with your healthcare providers when needed</li>
                                <li>Providing clear, trustworthy information you can act on</li>
                            </ul>
                        </div>
                    </section>

                    <section 
                        id="privacy" 
                        ref={handleSectionRef('privacy')}
                        className="legal-section"
                    >
                        <h2>Privacy Notice</h2>
                        <p>Effective Date: 4/23/2025</p>
                        <p>
                            This Privacy Notice describes how Sanvia ("Sanvia," "we," "us," or "our") collects, uses, discloses, and safeguards your information when you use our website, services, and associated technologies (the "Services"). Sanvia is committed to protecting your privacy and maintaining the security of your personal data. This Privacy Notice is drafted in accordance with applicable U.S. privacy laws, including the Health Insurance Portability and Accountability Act ("HIPAA") where applicable, and reflects our intention to comply with HIPAA requirements before public launch.
                        </p>

                        <h3>1. Information We Collect</h3>
                        <p>We collect information you voluntarily provide and data collected automatically through your use of the Services. This may include:</p>
                        <ul>
                            <li>Personal Information: Full name, contact details, demographic details (age, gender, height, weight), health conditions, medications, and other information you optionally provide.</li>
                            <li>Health Data: Uploaded health-related documents (e.g., PDFs, images), third-party EHR data (e.g., via EPIC FHIR), wearable device data (e.g., WHOOP), and other medically relevant inputs.</li>
                            <li>Usage Data: Logs of HTTP requests, IP addresses, browser types, and usage behavior on the platform.</li>
                            <li>Identifiers: Firebase authentication tokens, device identifiers, and OAuth credentials.</li>
                        </ul>
                        <p>We do not collect geolocation information or use persistent device fingerprinting or session replay scripts.</p>

                        <h3>2. How We Use Your Information</h3>
                        <p>We use your data to:</p>
                        <ul>
                            <li>Provide personalized health information explanations</li>
                            <li>Enable interaction with third-party health data systems (with your consent)</li>
                            <li>Parse and contextualize your documents for improved query response</li>
                            <li>Maintain service functionality, security, and performance</li>
                            <li>Comply with legal obligations</li>
                            <li>Improve our services and conduct internal research</li>
                            <li>Facilitate user-requested comparisons with de-identified patient profiles</li>
                        </ul>
                        <p>De-identified data may also be used in partnerships with academic or healthcare institutions for scientific research, only with your explicit consent.</p>

                        <h3>3. Sharing and Disclosure of Information</h3>
                        <p>We do not sell personally identifiable information. We may share information as follows:</p>
                        <ul>
                            <li>With your consent: For example, when you opt in to data sharing with research institutions.</li>
                            <li>With our internal team and contractors: As necessary for service provision.</li>
                            <li>With third-party service providers: Including Firebase, Google Cloud, Cloudflare, and OAuth identity providers.</li>
                            <li>In corporate transactions: Such as mergers or acquisitions.</li>
                            <li>To comply with legal obligations: In response to subpoenas, court orders, or law enforcement demands.</li>
                            <li>To protect rights and safety: Where we believe necessary to enforce Terms of Service or protect users and Sanvia.</li>
                            <li>As aggregated or de-identified data: For analytical, educational, or commercial purposes.</li>
                        </ul>

                        <h3>4. Your Rights and Choices</h3>
                        <p>You may:</p>
                        <ul>
                            <li>Request access to the data we hold about you</li>
                            <li>Request correction of incorrect or incomplete data</li>
                            <li>Request deletion of your data (note: we retain past versions for audit and compliance)</li>
                            <li>Withdraw consent for data sharing at any time</li>
                        </ul>
                        <p>To exercise these rights, contact us at: support@sanvia.app</p>
                        <p>We do not honor "Do Not Track" browser signals.</p>

                        <h3>5. Security Measures</h3>
                        <p>Sanvia implements administrative, technical, and physical safeguards to protect your information, including:</p>
                        <ul>
                            <li>Data encryption at rest and in transit</li>
                            <li>De-identification of critical health data</li>
                            <li>Access controls with two-factor authentication</li>
                            <li>Activity logging for auditability</li>
                            <li>Use of secure, industry-compliant third-party infrastructure (e.g., Google Cloud, Firebase)</li>
                        </ul>

                        <h3>6. Children's Privacy</h3>
                        <p>Our Services are intended for individuals aged 18 and older. We do not knowingly collect information from children under 18. If you are a parent or guardian and believe we have collected data from a minor, please contact us immediately.</p>

                        <h3>7. International Users</h3>
                        <p>Sanvia does not specifically target users in the EU, UK, or EEA. However, international users may access our platform. In such cases, personal data will be processed in the United States under applicable U.S. law.</p>

                        <h3>8. Data Retention</h3>
                        <p>We retain user information as long as necessary for service provision, legal compliance, or legitimate internal purposes. Historical data versions are retained for accountability and transparency, even after user-initiated deletion.</p>

                        <h3>9. Changes to This Notice</h3>
                        <p>We may update this Privacy Notice periodically. Users will be notified of material changes via email or platform notification. Continued use of the Services following updates indicates acceptance of the revised terms.</p>

                        <h3>10. Contact Us</h3>
                        <p>If you have questions or concerns about this Privacy Notice, or wish to exercise your data rights, contact us at:</p>
                        <p>Sanvia Support<br />
                        support@sanvia.app</p>

                        <p>This Privacy Notice is a binding part of our commitment to responsible data practices. We value your trust and are committed to transparency, security, and user autonomy in all data-related matters.</p>
                    </section>

                    <section 
                        id="terms" 
                        ref={handleSectionRef('terms')}
                        className="legal-section"
                    >
                        <h2>Terms of Service</h2>
                        <p>Effective Date: 4/24/2025</p>
                        <p>
                            These Terms of Service ("Terms") constitute a legally binding agreement between you ("you" or "User") and Sanvia ("Sanvia," "we," "our," or "us"), governing your use of the Sanvia website, web application, and related services (collectively, the "Services"). By accessing or using our Services, you agree to be bound by these Terms. If you do not agree, do not use our Services.
                        </p>

                        <h3>1. Eligibility</h3>
                        <p>You must be at least 18 years old to access or use the Services. By using the Services, you represent and warrant that you meet this age requirement and that all information you provide to Sanvia is accurate and truthful.</p>

                        <h3>2. Personal Use Only</h3>
                        <p>The Services are intended for personal, non-commercial use. You agree not to republish, redistribute, or exploit any content from the Services for commercial purposes without our prior written consent.</p>

                        <h3>3. Nature of the Services</h3>
                        <p>Sanvia provides educational and informational explanations of health-related knowledge based on user input. The Services do not provide medical diagnoses, treatment plans, or medical advice, and are not a substitute for professional healthcare consultation. You agree not to use the Services for any official medical decision-making.</p>

                        <h3>4. User Accounts</h3>
                        <p>To access certain features, you may need to create an account. You must provide accurate information and keep your credentials secure. Users are not permitted to create usernames or aliases; only your registered personal information is used. We reserve the right to suspend or terminate your account for any misuse of the Services.</p>

                        <h3>5. Acceptable Use Policy</h3>
                        <p>You agree not to:</p>
                        <ul>
                            <li>Use the Services for unlawful, misleading, abusive, or harassing behavior;</li>
                            <li>Upload non-health-related or irrelevant documents;</li>
                            <li>Impersonate any individual or entity;</li>
                            <li>Interfere with or disrupt the Services;</li>
                            <li>Attempt to gain unauthorized access to any systems or data;</li>
                            <li>Use automated scripts, bots, or scrapers without our permission.</li>
                        </ul>
                        <p>Violation of these rules may result in termination of access.</p>

                        <h3>6. Subscription and Payments</h3>
                        <p>Certain features of the Services are accessible only through an annual subscription. Sanvia offers a 3-month grace period during which you may request a full refund. After this period, payments are non-refundable. We process payments through third-party providers (e.g., Apple Pay, Google Pay, PayPal) and do not store credit card information directly.</p>

                        <h3>7. Intellectual Property</h3>
                        <p>Sanvia retains all rights, title, and interest in and to the Services, including all content, features, software, and branding. User-submitted content remains the intellectual property of the user. However, you grant Sanvia a non-exclusive license to use such content solely for the purpose of providing the Services. Redistribution of Sanvia-generated outputs for commercial use is prohibited.</p>

                        <h3>8. User-Submitted Content</h3>
                        <p>You may upload health-related content, including documents and data. You represent that you have the right to share such information and that it does not violate any third-party rights or laws. Sanvia will use and store such content in accordance with our Privacy Notice.</p>

                        <h3>9. Limitation of Liability</h3>
                        <p>To the fullest extent permitted by law, Sanvia disclaims all warranties, express or implied, regarding the Services. The Services are provided "as is." Sanvia shall not be liable for any indirect, incidental, consequential, or punitive damages arising from or related to your use of the Services.</p>

                        <h3>10. Indemnification</h3>
                        <p>You agree to indemnify and hold harmless Sanvia, its officers, affiliates, and employees from any claims, losses, liabilities, or expenses (including legal fees) arising from your use of the Services or violation of these Terms.</p>

                        <h3>11. Dispute Resolution and Governing Law</h3>
                        <p>These Terms shall be governed by the laws of the Commonwealth of Massachusetts. Any dispute arising out of these Terms shall be resolved through binding arbitration. Arbitration shall be conducted in Boston, Massachusetts. If arbitration is not enforceable, then jurisdiction shall lie in the courts of Suffolk County, Massachusetts.</p>

                        <h3>12. Termination</h3>
                        <p>Sanvia reserves the right to suspend or terminate your access to the Services at our discretion, without prior notice, for conduct that violates these Terms or is otherwise harmful to our interests or those of other users.</p>

                        <h3>13. Changes to the Terms</h3>
                        <p>Sanvia may revise these Terms at any time. Material changes will be communicated to you through the platform or email. Your continued use of the Services after any update constitutes your acceptance of the revised Terms.</p>

                        <h3>14. Contact Us</h3>
                        <p>If you have any questions about these Terms, please contact:</p>
                        <p>Sanvia Support<br />
                        support@sanvia.app</p>

                        <p>By using the Services, you acknowledge that you have read, understood, and agreed to these Terms of Service in full.</p>
                    </section>
                </div>
            </div>
        </div>
    );
};

export default About; 