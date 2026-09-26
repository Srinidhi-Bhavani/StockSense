import {
  Truck,
  Plus,
  Search,
  PackageCheck,
} from "lucide-react";

function Deliveries() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Delivery Orders</h1>
          <p>Manage outgoing stock and customer deliveries.</p>
        </div>

        <button className="primary-button">
          <Plus size={17} />
          Create Delivery
        </button>
      </div>

      <div className="page-toolbar">
        <div className="page-search">
          <Search size={17} />
          <input placeholder="Search delivery orders..." />
        </div>

        <select className="page-select">
          <option>All Statuses</option>
          <option>Draft</option>
          <option>Ready</option>
          <option>Validated</option>
        </select>
      </div>

      <div className="data-card">
        <div className="table-header">
          <div>
            <h3>Delivery Orders</h3>
            <span>Track outgoing inventory and deliveries</span>
          </div>
        </div>

        <div className="empty-table">
          <div className="empty-table-icon">
            <Truck size={24} />
          </div>

          <h3>No delivery orders available</h3>

          <p>
            New delivery orders will appear here after they are created.
          </p>

          <button className="primary-button">
            <PackageCheck size={16} />
            Create First Delivery
          </button>
        </div>
      </div>
    </div>
  );
}

export default Deliveries;