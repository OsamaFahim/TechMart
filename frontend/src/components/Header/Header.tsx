import React from "react";
import { AppBar, Toolbar, Typography, Box, Paper } from "@mui/material";
import { useDashboard } from "../../contexts/DashboardContext";

/**
 * Header Component
 * Displays the main header with the dashboard title and key metrics.
 * Uses Material-UI components for styling.
 */

const Header: React.FC = () => {
  // Access the dashboard context to get the metrics
  // This assumes useDashboard is a custom hook that provides the dashboard state
  const dashboard = useDashboard();

  return (
    // AppBar component for the header
    <AppBar position="static" color="primary" sx={{ mb: 2 }}>
      <Toolbar>
        {/* Title of the dashboard */}
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          TechMart Dashboard
        </Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
          {/* Display key metrics in Paper components for styling */}
          <Paper sx={{ p: 1, minWidth: 120, textAlign: "center" }}>
            <Typography variant="body2">Total Sales</Typography>
            <Typography variant="subtitle1">${dashboard?.total_sales ?? "--"}</Typography>
          </Paper>
          
          <Paper sx={{ p: 1, minWidth: 120, textAlign: "center" }}>
            <Typography variant="body2">Transactions</Typography>
            <Typography variant="subtitle1">{dashboard?.total_transactions ?? "--"}</Typography>
          </Paper>
          <Paper sx={{ p: 1, minWidth: 120, textAlign: "center" }}>
            <Typography variant="body2">New Customers</Typography>
            <Typography variant="subtitle1">{dashboard?.new_customers ?? "--"}</Typography>
          </Paper>
          <Paper sx={{ p: 1, minWidth: 120, textAlign: "center" }}>
            <Typography variant="body2">Low Stock</Typography>
            <Typography variant="subtitle1">{dashboard?.low_stock_products ?? "--"}</Typography>
          </Paper>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;