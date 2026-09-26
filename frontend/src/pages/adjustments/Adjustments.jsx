import {
  ClipboardEdit,
  Plus,
  Search,
  PackageCheck,
} from "lucide-react";

function Adjustments() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Inventory Adjustment</h1>
          <p>Correct and update counted inventory quantities.</p>
        </div>

        <button className="primary-button">
          <Plus size={17} />
          New Adjustment
        </button>
      </div>

      <div className="page-toolbar">
        <div className="page-search">
          <Search size={17} />
          <input placeholder="Search adjustments..." />
        </div>

        <select className="page-select">
          <option>All Warehouses</option>
          <option>Main Warehouse</option>
          <option>Secondary Warehouse</option>
        </select>
      </div>

      <div className="data-card">
        <div className="table-header">
          <div>
            <h3>Inventory Adjustments</h3>
            <span>Review stock corrections and quantity changes</span>
          </div>
        </div>

        <div className="empty-table">
          <div className="empty-table-icon">
            <ClipboardEdit size={24} />
          </div>

          <h3>No adjustments available</h3>

          <p>
            Inventory adjustments will appear here after they are created.
          </p>

          <button className="primary-button">
            <PackageCheck size={16} />
            Create First Adjustment
          </button>
        </div>
      </div>
    </div>
  );
}

export default Adjustments;