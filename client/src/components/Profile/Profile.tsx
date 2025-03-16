import './Profile.css';

interface ProfileProps {
  firstName: string;
  lastName: string;
  height: string;
  weight: string;
  gender: string;
  sex: string;
  age: string;
  onClose: () => void;

}

const Profile: React.FC<ProfileProps> = ({
  firstName,
  lastName,
  height,
  weight,
  gender,
  sex,
  age,
  onClose
}) => {
console.log("Profile props:", { firstName, lastName, height, weight, gender, sex, age });

console.log("Sidebar is rendering");

  return (
    <div className="overlay" onClick={onClose}>
      <div className="card" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button 
              onClick={() => {
                console.log('Close button clicked'); // ✅ Add this log
                onClose(); // This calls the onClose function passed from Sidebar
              }} 
              className="close-button"
            >

          ✕
        </button>

        {/* Profile Icon */}
        <div className="profile-card-icon">
          {firstName.charAt(0).toUpperCase()}
          {lastName.charAt(0).toUpperCase()}
        </div>

        {/* Profile Content */}
        <div className="profile-content">
          <h2>{firstName} {lastName}</h2>
          <p><strong>Age:</strong> {age}</p>
          <p><strong>Height:</strong> {height}</p>
          <p><strong>Weight:</strong> {weight}</p>
          <p><strong>Gender:</strong> {gender}</p>
          <p><strong>Sex:</strong> {sex}</p>
        </div>
      </div>
    </div>
  );
};

export default Profile;
