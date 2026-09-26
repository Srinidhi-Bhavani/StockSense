import {
  Package,
  Plus,
  Search,
  MoreHorizontal,
  AlertTriangle,
} from "lucide-react";

function Products() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Products</h1>
          <p>Manage products, SKUs, categories and inventory.</p>
        </div>

        <button className="primary-button">
          <Plus size={17} />
          Add Product
        </button>
      </div>

      <div className="page-toolbar">
        <div className="page-search">
          <Search size={17} />
          <input placeholder="Search by product name or SKU..." />
        </div>

        <select className="page-select">
          <option>All Categories</option>
          <option>Electronics</option>
          <option>Furniture</option>
          <option>Office Supplies</option>
        </select>

        <select className="page-select">
          <option>All Stock Status</option>
          <option>In Stock</option>
          <option>Low Stock</option>
          <option>Out of Stock</option>
        </select>
      </div>

      <div className="data-card">
        <div className="table-header">
          <div>
            <h3>Product Inventory</h3>
            <span>Manage your current inventory items</span>
          </div>
        </div>

        <div className="empty-table">
          <div className="empty-table-icon">
            <Package size={24} />
          </div>

          <h3>No products available</h3>

          <p>
            Products created through the inventory system will appear here.
          </p>

          <button className="primary-button">
            <Plus size={16} />
            Add First Product
          </button>
        </div>
      </div>
    </div>
  );
}

export default Products;