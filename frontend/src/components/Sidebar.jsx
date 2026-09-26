import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Package,
  ClipboardCheck,
  Truck,
  ArrowRightLeft,
  ClipboardList,
  History,
  Settings,
  User,
  LogOut,
} from "lucide-react";

function Sidebar() {
  const menuItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Products", path: "/products", icon: Package },
    { name: "Receipts", path: "/receipts", icon: ClipboardCheck },
    { name: "Delivery Orders", path: "/deliveries", icon: Truck },
    { name: "Inventory Adjustment", path: "/adjustments", icon: ClipboardList },
    { name: "Move History", path: "/history", icon: History },
    { name: "Transfers", path: "/transfers", icon: ArrowRightLeft },
    { name: "Settings / Warehouse", path: "/settings", icon: Settings },
    { name: "My Profile", path: "/profile", icon: User },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">S</div>
        <div>
          <h2>StockSense</h2>
          <span>Inventory Management</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive ? "nav-item active" : "nav-item"
              }
            >
              <Icon size={20} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <button className="logout-button">
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;