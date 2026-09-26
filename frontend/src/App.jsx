import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

import MainLayout from "./layouts/MainLayout";
import Dashboard from "./pages/dashboard/Dashboard";
import Products from "./pages/products/Products";
import Receipts from "./pages/receipts/Receipts";
import Deliveries from "./pages/deliveries/Deliveries";
import Adjustments from "./pages/adjustments/Adjustments";
import Transfers from "./pages/transfers/Transfers";
import History from "./pages/history/History";
import Settings from "./pages/settings/Settings";
import Profile from "./pages/profile/Profile";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/receipts" element={<Receipts />} />
          <Route path="/deliveries" element={<Deliveries />} />
          <Route path="/adjustments" element={<Adjustments />} />
          <Route path="/transfers" element={<Transfers />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;