import React, { createContext, useContext, useState, useEffect } from "react";
import { fetchDashboardOverview } from "../api/dashboard";

// DashboardData type
// Represents the structure of the data returned by the dashboard overview API.
type DashboardData = {
  total_sales: number;
  total_transactions: number;
  new_customers: number;
  low_stock_products: number;
};

// DashboardContext
// Provides the dashboard data to components that need it.
const DashboardContext = createContext<DashboardData | null>(null);

// useDashboard hook
// Custom hook to access the DashboardContext.
export const useDashboard = () => useContext(DashboardContext);

// DashboardProvider component
// Wraps the application and provides the dashboard data context.
export const DashboardProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [data, setData] = useState<DashboardData | null>(null);

  // Fetch the dashboard overview data when the component mounts
  useEffect(() => {
    fetchDashboardOverview().then(setData);
    // Poll every 30s for real-time updates
    const interval = setInterval(() => fetchDashboardOverview().then(setData), 30000);
    return () => clearInterval(interval);
  }, []);

  // If data is not yet loaded, return null to avoid rendering children prematurely
  return (
    <DashboardContext.Provider value={data}>
      {children}
    </DashboardContext.Provider>
  );
};