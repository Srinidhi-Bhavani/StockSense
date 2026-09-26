import {
  History as HistoryIcon,
  Search,
  ArrowDownToLine,
  ArrowUpFromLine,
  ArrowRightLeft,
} from "lucide-react";

function History() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Move History</h1>
          <p>Track all inventory movements across your warehouses.</p>
        </div>
      </div>

      <div className="page-toolbar">
        <div className="page-search">
          <Search size={17} />
          <input placeholder="Search movement history..." />
        </div>

        <select className="page-select">
          <option>All Movement Types</option>
          <option>Receipt</option>
          <option>Delivery</option>
          <option>Transfer</option>
          <option>Adjustment</option>
        </select>

        <select className="page-select">
          <option>All Warehouses</option>
          <option>Main Warehouse</option>
          <option>Secondary Warehouse</option>
        </select>
      </div>

      <div className="data-card">
        <div className="table-header">
          <div>
            <h3>Inventory Movement History</h3>
            <span>Complete record of stock movements</span>
          </div>
        </div>

        <div className="empty-table">
          <div className="empty-table-icon">
            <HistoryIcon size={24} />
          </div>

          <h3>No movement history available</h3>

          <p>
            Inventory movements will appear here once stock operations are
            completed.
          </p>

          <div className="history-types">
            <span>
              <ArrowDownToLine size={15} />
              Receipts
            </span>

            <span>
              <ArrowUpFromLine size={15} />
              Deliveries
            </span>

            <span>
              <ArrowRightLeft size={15} />
              Transfers
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default History;