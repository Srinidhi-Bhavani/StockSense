import {
  ClipboardPlus,
  Plus,
  Search,
  PackageCheck,
} from "lucide-react";

function Receipts() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Receipts</h1>
          <p>Manage incoming stock and supplier receipts.</p>
        </div>

        <button className="primary-button">
          <Plus size={17} />
          Create Receipt
        </button>
      </div>

      <div className="page-toolbar">
        <div className="page-search">
          <Search size={17} />
          <input placeholder="Search receipts..." />
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
            <h3>Incoming Receipts</h3>
            <span>Track incoming inventory from suppliers</span>
          </div>
        </div>

        <div className="empty-table">
          <div className="empty-table-icon">
            <ClipboardPlus size={24} />
          </div>

          <h3>No receipts available</h3>

          <p>
            New supplier receipts will appear here after they are created.
          </p>

          <button className="primary-button">
            <PackageCheck size={16} />
            Create First Receipt
          </button>
        </div>
      </div>
    </div>
  );
}

export default Receipts;