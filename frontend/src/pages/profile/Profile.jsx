import {
  User,
  Mail,
  ShieldCheck,
  Building2,
  LogOut,
} from "lucide-react";

function Profile() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>My Profile</h1>
          <p>View your account and inventory access details.</p>
        </div>

        <button className="secondary-button">
          <LogOut size={17} />
          Logout
        </button>
      </div>

      <div className="profile-grid">
        <div className="data-card profile-card">
          <div className="profile-avatar">
            S
          </div>

          <h2>Spoorthy</h2>
          <p className="profile-role">Inventory Manager</p>
        </div>

        <div className="data-card profile-details">
          <h3>Account Information</h3>

          <div className="profile-row">
            <div className="profile-row-icon">
              <User size={18} />
            </div>
            <div>
              <span>Name</span>
              <strong>Spoorthy</strong>
            </div>
          </div>

          <div className="profile-row">
            <div className="profile-row-icon">
              <Mail size={18} />
            </div>
            <div>
              <span>Email</span>
              <strong>spoorthy@example.com</strong>
            </div>
          </div>

          <div className="profile-row">
            <div className="profile-row-icon">
              <ShieldCheck size={18} />
            </div>
            <div>
              <span>Role</span>
              <strong>Inventory Manager</strong>
            </div>
          </div>

          <div className="profile-row">
            <div className="profile-row-icon">
              <Building2 size={18} />
            </div>
            <div>
              <span>Department</span>
              <strong>Inventory Operations</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;