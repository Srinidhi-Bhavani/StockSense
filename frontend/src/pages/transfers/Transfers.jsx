import {
  ArrowRightLeft,
  Plus,
  Search,
  PackageCheck,
} from "lucide-react";

function Transfers() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Transfers</h1>
          <p>Move inventory between warehouses and locations.</p>
        </div>

        <button className="primary-button">
          <Plus size={17} />
          New Transfer
        </button>
      </div>

      <div className="page-toolbar">
        <div className="page-search">
          <Search size={17} />
          <input placeholder="Search transfers..." />
        </div>

        <select className="page-select">
          <option>All Statuses</option>
          <option>Draft</option>
          <option>In Transit</option>
          <option>Completed</option>
        </select>
      </div>

      <div className="data-card">
        <div className="table-header">
          <div>
            <h3>Stock Transfers</h3>
            <span>Track inventory movement between locations</span>
          </div>
        </div>

        <div className="empty-table">
          <div className="empty-table-icon">
            <ArrowRightLeft size={24} />
          </div>

          <h3>No transfers available</h3>

          <p>
            Stock transfers will appear here after they are created.
          </p>

          <button className="primary-button">
            <PackageCheck size={16} />
            Create First Transfer
          </button>
        </div>
      </div>
    </div>
  );
}

export default Transfers;