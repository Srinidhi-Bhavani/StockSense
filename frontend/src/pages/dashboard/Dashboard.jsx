function Dashboard() {
  return (
    <div className="dashboard">
      <div className="page-heading">
        <div>
          <h1>Inventory Dashboard</h1>
          <p>Overview of your inventory operations</p>
        </div>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card">
          <span>Total Products in Stock</span>
          <strong>0</strong>
        </div>

        <div className="kpi-card">
          <span>Low / Out of Stock</span>
          <strong>0</strong>
        </div>

        <div className="kpi-card">
          <span>Pending Receipts</span>
          <strong>0</strong>
        </div>

        <div className="kpi-card">
          <span>Pending Deliveries</span>
          <strong>0</strong>
        </div>

        <div className="kpi-card">
          <span>Internal Transfers</span>
          <strong>0</strong>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>Inventory Overview</h2>
        <p>
          Inventory data will appear here after connecting the dashboard
          to the backend.
        </p>
      </div>
    </div>
  );
}

export default Dashboard;