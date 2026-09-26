import {
  Package,
  AlertTriangle,
  ArrowDownToLine,
  ArrowUpFromLine,
  ArrowRightLeft,
  TrendingUp,
  MoreHorizontal,
  Clock3,
} from "lucide-react";

function Dashboard() {
  const kpis = [
    {
      title: "Products in Stock",
      value: "0",
      change: "Live data",
      icon: Package,
      className: "blue",
    },
    {
      title: "Low / Out of Stock",
      value: "0",
      change: "Needs attention",
      icon: AlertTriangle,
      className: "orange",
    },
    {
      title: "Pending Receipts",
      value: "0",
      change: "Awaiting validation",
      icon: ArrowDownToLine,
      className: "green",
    },
    {
      title: "Pending Deliveries",
      value: "0",
      change: "Awaiting dispatch",
      icon: ArrowUpFromLine,
      className: "purple",
    },
    {
      title: "Internal Transfers",
      value: "0",
      change: "In progress",
      icon: ArrowRightLeft,
      className: "cyan",
    },
  ];

  return (
    <div className="dashboard-page">
      {/* Page Header */}
      <div className="dashboard-header">
        <div>
          <div className="breadcrumb">Workspace / Dashboard</div>

          <h1>Inventory Overview</h1>

          <p>
            Monitor your inventory, stock movement and pending operations.
          </p>
        </div>

        <button className="dashboard-action">
          <TrendingUp size={17} />
          View Reports
        </button>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        {kpis.map((item) => {
          const Icon = item.icon;

          return (
            <div className="kpi-card" key={item.title}>
              <div className={`kpi-icon ${item.className}`}>
                <Icon size={21} />
              </div>

              <div className="kpi-content">
                <span className="kpi-title">{item.title}</span>

                <div className="kpi-value-row">
                  <strong>{item.value}</strong>
                </div>

                <span className="kpi-change">{item.change}</span>
              </div>

              <button className="card-menu">
                <MoreHorizontal size={19} />
              </button>
            </div>
          );
        })}
      </div>

      {/* Main Dashboard Grid */}
      <div className="dashboard-grid">
        {/* Inventory Overview */}
        <section className="dashboard-card inventory-card">
          <div className="card-header">
            <div>
              <h2>Inventory Overview</h2>
              <p>Stock activity across your inventory</p>
            </div>

            <select className="period-select" defaultValue="7">
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>

          <div className="chart-placeholder">
            <div className="chart-y-axis">
              <span>100</span>
              <span>75</span>
              <span>50</span>
              <span>25</span>
              <span>0</span>
            </div>

            <div className="chart-area">
              <div className="chart-grid-line"></div>
              <div className="chart-grid-line"></div>
              <div className="chart-grid-line"></div>
              <div className="chart-grid-line"></div>

              <div className="empty-chart">
                <TrendingUp size={30} />
                <strong>Inventory data will appear here</strong>
                <span>
                  Connect the dashboard to the inventory API to view trends.
                </span>
              </div>

              <div className="chart-labels">
                <span>Mon</span>
                <span>Tue</span>
                <span>Wed</span>
                <span>Thu</span>
                <span>Fri</span>
                <span>Sat</span>
                <span>Sun</span>
              </div>
            </div>
          </div>
        </section>

        {/* Stock Alerts */}
        <section className="dashboard-card alerts-card">
          <div className="card-header">
            <div>
              <h2>Stock Alerts</h2>
              <p>Items requiring attention</p>
            </div>

            <button className="view-all-button">View all</button>
          </div>

          <div className="empty-state">
            <div className="empty-icon">
              <AlertTriangle size={22} />
            </div>

            <strong>No stock alerts</strong>

            <span>
              Low-stock and out-of-stock products will appear here.
            </span>
          </div>
        </section>
      </div>

      {/* Recent Activity */}
      <section className="dashboard-card activity-card">
        <div className="card-header">
          <div>
            <h2>Recent Inventory Activity</h2>
            <p>Latest stock operations and movements</p>
          </div>

          <button className="view-all-button">View history</button>
        </div>

        <div className="activity-empty">
          <div className="activity-empty-icon">
            <Clock3 size={24} />
          </div>

          <div>
            <strong>No recent activity</strong>

            <p>
              Receipts, deliveries, transfers and adjustments will appear here
              once inventory activity is recorded.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;