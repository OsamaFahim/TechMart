import React, { useState } from "react";
import { Container, Grid } from "@mui/material";
import Header from "../components/Header/Header";
import SalesChart from "../components/Charts/SalesChart";
import LowStockProductsWidget from "../components/DashboardWidgets/LowStockProductsWidget";
import TransactionsFeed from "../components/DashboardWidgets/TransactionsFeed";
import DashboardFilters from "../components/DashboardWidgets/DashboardFilters";
import TopProductsWidget from "../components/DashboardWidgets/TopProductsWidget";

/**
 * Layout:
 Header at the top
 Filters below the header
 Main content is a two-column grid:
      Left (md=8): Sales chart at the top, Suspicious Transactions below
      Right (md=4): Low Stock Products at the top, Top Products below
 */

const Dashboard: React.FC = () => {
  // Dashboard filters state (date range, category, segment)
  const [filters, setFilters] = useState({
    dateFrom: "",
    dateTo: "",
    category: "All",
    segment: "All",
  });

  return (
    <>
      {/* Top navigation/header */}
      <Header />
      {/* Main container for dashboard content */}
      <Container maxWidth="lg" sx={{ mt: 4, mb: 0 }}>
        {/* Dashboard filters (date range, category, segment) */}
        <DashboardFilters onFilter={setFilters} />
        <Grid container spacing={3}>
          {/* Left column: Sales chart and suspicious transactions */}
          {/*md={8} / md={4} means: on medium and larger screens (e.g., tablets/desktops), divide the space in a 12-column layout,
           with 8 columns for the left section and 4 for the right.*/}
          <Grid item xs={12} md={8}>
            {/* Sales performance chart (filtered by dashboard filters) */}
            <SalesChart filters={filters} />
            {/* Recent suspicious transactions feed (filtered by dashboard filters) */}
            <TransactionsFeed filters={filters} />
          </Grid>
          {/* Right column: Low stock products and top products */}
          <Grid item xs={12} md={4}>
            {/* Low stock products table (filtered by dashboard filters) */}
            <LowStockProductsWidget filters={filters} />
            {/* Top products by sales quantity */}
            <TopProductsWidget />
          </Grid>
        </Grid>
      </Container>
    </>
  );
};

export default Dashboard;