import { Bell, Search } from "lucide-react";

function Topbar() {
  return (
    <header className="topbar">
      <div className="topbar-search">
        <Search size={20} />
        <input
          type="text"
          placeholder="Search products, SKU..."
        />
      </div>

      <div className="topbar-right">
        <button className="notification-button">
          <Bell size={20} />
          <span className="notification-dot"></span>
        </button>

        <div className="user-info">
          <div className="user-avatar">S</div>
          <div>
            <strong>Spoorthy</strong>
            <span>Inventory Manager</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Topbar;