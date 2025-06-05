import React, { useEffect, useState } from "react";
import { fetchTopProducts } from "../../api/products";
import { DataGrid } from "@mui/x-data-grid";
import type { GridColDef } from "@mui/x-data-grid";
import { Paper, Typography, Button, CircularProgress, Alert } from "@mui/material";
import { saveAs } from "file-saver";

// Filters type
// Represents the dashboard filter state passed from the parent (Dashboard) component.

type TopProductRow = {
  id: number;
  product__name: string;
  product__category?: string;
  total_sold: number;
};

// DataGrid columns definition
// product__name: Name of the product

const columns: GridColDef<TopProductRow>[] = [
  { field: "product__name", headerName: "Product Name", flex: 1 },
  { field: "product__category", headerName: "Category", flex: 1 },
  { field: "total_sold", headerName: "Total Sold", width: 130 },
];

// TopProductsWidget Component
// Displays a list of top-selling products with export functionality.
const TopProductsWidget: React.FC = () => {
  const [rows, setRows] = useState<TopProductRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

// Fetch top products from the backend
  useEffect(() => {
    setLoading(true);
    fetchTopProducts()
      .then(data => {
        // Use backend 'id' directly, fallback to index if missing
        setRows(
          // Map the data to the expected row format
          data.map((row: any, idx: number) => ({
            id: row.id ?? idx + 1,
            product__name: row.product__name ?? "Unknown",
            product__category: row.product__category ?? "Unknown",
            total_sold: row.total_sold ?? 0,
          }))
        );
        setError(null);
      })
      // Handle errors and set loading state
      .catch(() => setError("Failed to load top products."))
      .finally(() => setLoading(false));
  }, []);

  // Handle CSV export
  // We are creating CSV by joining rows with commas and newlines.
  // The first row contains headers.
  // The saveAs function from file-saver is used to trigger the download.
  // The CSV format is simple, with no special escaping or quoting.
  const handleExport = () => {
    const csv = [
      ["Product Name", "Category", "Total Sold"],
      ...rows.map(row => [row.product__name, row.product__category, row.total_sold]),
    ]
      .map(row => row.join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    // Use file-saver to save the CSV file
    // The filename is hardcoded as "top_products.csv"
    saveAs(blob, "top_products.csv");
  };

  // Render the component
  return (
    // Paper component for styling
    // Contains a title, export button, and the DataGrid for displaying products
    <Paper elevation={3} sx={{ p: 2, mb: 0 }}>
      <Typography variant="h6" gutterBottom>
        Top Products
      </Typography>
      <Button variant="outlined" size="small" sx={{ mb: 1 }} onClick={handleExport}>
        Export CSV
      </Button>
      { /*DataGrid component for displaying the top products
      // It uses the rows and columns defined above. CircularProgress is shown while loading,*/}
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        // DataGrid to display the top products
        // It uses the rows and columns defined above.
        <div style={{ height: 350, width: "100%" }}>
          <DataGrid<TopProductRow>
            rows={rows}
            columns={columns}
            pageSizeOptions={[5]}
            initialState={{
              pagination: { paginationModel: { pageSize: 5, page: 0 } }
            }}
            disableRowSelectionOnClick
            autoHeight
          />
        </div>
      )}
    </Paper>
  );
};

export default TopProductsWidget;