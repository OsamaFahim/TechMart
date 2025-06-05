import React, { useEffect, useState } from "react";
import { fetchLowStockProducts } from "../../api/products";
import { DataGrid } from "@mui/x-data-grid";
import type { GridColDef } from "@mui/x-data-grid";
import { Chip, Paper, Typography, TextField, Button, CircularProgress, Alert } from "@mui/material";
import { saveAs } from "file-saver";

/**
 Filters type
 Represents the dashboard filter state passed from the parent (Dashboard) component.
 Used to re-fetch low stock products when filters change.
 */

type Filters = {
  dateFrom: string;
  dateTo: string;
  category: string;
  segment: string;
};

/**
 ProductRow type
 Represents a single row in the low stock products table.
   id: Unique product ID
   name: Product name
   stock_quantity: Current stock level
   status: "Critical" if stock < 5, otherwise "Low"
 */

type ProductRow = {
  id: number;
  name: string;
  stock_quantity: number;
  status: string;
};

/**
DataGrid columns definition
 Name: Product name
 Stock: Current stock quantity
 Status: Shows a colored chip ("Critical" or "Low") based on stock level
 */

const columns: GridColDef<ProductRow>[] = [
  { field: "name", headerName: "Name", flex: 1 },
  { field: "stock_quantity", headerName: "Stock", width: 100 },
  {
    field: "status",
    headerName: "Status",
    width: 130,
    renderCell: (params) =>
      params.value === "Critical" ? (
        <Chip label="Critical" color="error" />
      ) : (
        <Chip label="Low" color="warning" />
      ),
    sortable: false,
    filterable: false,
  },
];

/**
 LowStockProductsWidget Component

Displays a table of products with low stock.
 Fetches low stock products from the backend (filtered by dashboard filters)
 Supports search by product name and CSV export
 Shows loading and error states
 */

const LowStockProductsWidget: React.FC<{ filters: Filters }> = ({ filters }) => {
  // State for the fetched products, search input, loading and error
  const [products, setProducts] = useState<ProductRow[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch low stock products whenever filters change
  useEffect(() => {
    setLoading(true);
    fetchLowStockProducts()
      .then((data) => {
        setProducts(
          data.map((row: any) => ({
            ...row,
            status: row.stock_quantity < 5 ? "Critical" : "Low",
          }))
        );
        setError(null);
      })
      .catch(() => setError("Failed to load products."))
      .finally(() => setLoading(false));
  }, [filters]); // re-fetch if filters change

  // Filter products by search input (case-insensitive)
  const filteredRows = products.filter((prod) =>
    prod.name.toLowerCase().includes(search.toLowerCase())
  );

  // Simple CSV export
  const handleExport = () => {
    const csv = [
      ["Name", "Stock", "Status"],
      ...filteredRows.map((row) => [row.name, row.stock_quantity, row.status]),
    ]
      .map((row) => row.join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    saveAs(blob, "low_stock_products.csv");
  };

  return (
    <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        Low Stock Products
      </Typography>
      {/* CSV export button */}
      <Button variant="outlined" size="small" sx={{ mb: 1 }} onClick={handleExport}>
        Export CSV
      </Button>
       {/* Product search input */}
      <TextField
        fullWidth
        size="small"
        placeholder="Search products..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        sx={{ mb: 2 }}
      />
       {/* Loading, error, or DataGrid table */}
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <div style={{ height: 350, width: "100%" }}>
          <DataGrid<ProductRow>
            rows={filteredRows}
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

export default LowStockProductsWidget;