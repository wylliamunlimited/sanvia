import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./WaitlistForm.css";
import { submitWaitlist } from "../../../api/waitlist";

const WaitlistForm = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        age: "",
        role: "",
    });
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsSubmitting(true);

        // Name validation
        if (/\d/.test(formData.name)) {
            setError("Name should not contain numbers");
            setIsSubmitting(false);
            return;
        }

        // Basic validation
        if (!formData.email || !formData.name) {
            setError("Please fill in all required fields");
            setIsSubmitting(false);
            return;
        }

        try {
            await submitWaitlist(formData);
            setSuccess(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to submit. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

    if (success) {
        return (
            <div className="waitlist-container">
                <div className="success-message">
                    <h2>Thank you for joining our waitlist!</h2>
                    <p>We'll be in touch soon with updates about Sanvia.</p>
                    <button 
                        className="return-home-button"
                        onClick={() => navigate('/')}
                    >
                        Return to Home
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="waitlist-container">
            <div className="waitlist-card">
                <h2>
                    <span className="hero-text-italic">Join the</span>{" "}
                    <span className="hero-text-bold">Sanvia</span>{" "}
                    <span className="hero-text-regular">Waitlist</span>
                </h2>
                <p className="subtitle">
                    <span className="hero-text-bold">Reclaim Control</span>{" "}
                    <span className="hero-text-regular">of Your Health,</span>
                    <br />
                    <span className="hero-text-italic">with Intelligence</span>{" "}
                    <span className="hero-text-bold">You Can Trust.</span>
                </p>

                <form onSubmit={handleSubmit} className="waitlist-form">
                    <div className="form-group">
                        <label htmlFor="name">Name *</label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            placeholder="Your full name"
                            disabled={isSubmitting}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email *</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            placeholder="your@email.com"
                            disabled={isSubmitting}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="age">Age</label>
                        <input
                            type="text"
                            id="age"
                            name="age"
                            value={formData.age}
                            onChange={handleChange}
                            placeholder="Your age"
                            disabled={isSubmitting}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="role">Role</label>
                        <input
                            type="text"
                            id="role"
                            name="role"
                            value={formData.role}
                            onChange={handleChange}
                            placeholder="Your role"
                            disabled={isSubmitting}
                        />
                    </div>

                    {error && <p className="error-message">{error}</p>}

                    <button
                        type="submit"
                        className="submit-button"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? "Submitting..." : "Join Waitlist"}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default WaitlistForm; 