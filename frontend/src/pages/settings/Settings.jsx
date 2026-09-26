import {
  Settings as SettingsIcon,
  Warehouse,
  MapPin,
  Plus,
} from "lucide-react";

function Settings() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Settings & Warehouse</h1>
          <p>Manage warehouse locations and inventory settings.</p>
        </div>

        <button className="primary-button">
          <Plus size={17} />
          Add Warehouse
        </button>
      </div>

      <div className="settings-grid">
        <div className="data-card settings-card">
          <div className="settings-icon">
            <Warehouse size={22} />
          </div>

          <h3>Warehouses</h3>

          <p>
            Manage your company warehouses and inventory locations.
          </p>

          <div className="settings-row">
            <span>Main Warehouse</span>
            <span className="status-badge">Active</span>
          </div>

          <div className="settings-row">
            <span>Secondary Warehouse</span>
            <span className="status-badge">Active</span>
          </div>
        </div>

        <div className="data-card settings-card">
          <div className="settings-icon">
            <MapPin size={22} />
          </div>

          <h3>Locations</h3>

          <p>
            Configure storage locations within your warehouses.
          </p>

          <div className="settings-row">
            <span>Storage Area A</span>
            <span>Location</span>
          </div>

          <div className="settings-row">
            <span>Storage Area B</span>
            <span>Location</span>
          </div>
        </div>

        <div className="data-card settings-card">
          <div className="settings-icon">
            <SettingsIcon size={22} />
          </div>

          <h3>Inventory Settings</h3>

          <p>
            Configure general inventory management preferences.
          </p>

          <div className="settings-row">
            <span>Low Stock Alerts</span>
            <span className="status-badge">Enabled</span>
          </div>

          <div className="settings-row">
            <span>Multi-Warehouse</span>
            <span className="status-badge">Enabled</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;