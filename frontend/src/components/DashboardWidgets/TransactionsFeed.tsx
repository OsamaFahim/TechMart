import React, { useEffect, useState } from "react";
import { fetchSuspiciousTransactions } from "../../api/transactions";
import { DataGrid } from "@mui/x-data-grid";
import type { GridColDef } from "@mui/x-data-grid";
import { Chip, Paper, Typography, TextField } from "@mui/material";
import TransactionModal from "../../Modals/TransactionModal";

// Filters type
// Represents the dashboard filter state passed from the parent (Dashboard) component.

type Filters = {
  dateFrom: string;
  dateTo: string;
  category: string;
  segment: string;
};

// TransactionRow type
// Represents a single row in the transactions table.
type TransactionRow = {
  id: number;
  customer: number;
  total_amount: number;
  timestamp: string;
  risk: string;
};

// DataGrid columns definition
// ID: Unique transaction ID
const columns: GridColDef<TransactionRow>[] = [
  // ID: Unique transaction ID
  { field: "id", headerName: "ID", width: 70 },
  { field: "customer", headerName: "Customer", width: 120 },
  { field: "total_amount", headerName: "Amount ($)", width: 120 },
  {
    field: "timestamp",
    headerName: "Timestamp",
    flex: 1,
    valueGetter: (params: { row: TransactionRow }) =>
      params.row && params.row.timestamp
        ? new Date(params.row.timestamp).toLocaleString()
        : "",
  },
  {
    field: "risk",
    headerName: "Risk",
    width: 100,
    renderCell: () => <Chip label="Risk" color="error" />,
    sortable: false,
    filterable: false,
  },
];

// TransactionsFeed Component
// Displays a list of suspicious transactions with search and modal details.
const TransactionsFeed: React.FC<{ filters: Filters }> = ({ filters }) => {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<TransactionRow | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  // Fetch transactions when filters change
  useEffect(() => {
    fetchSuspiciousTransactions().then(setTransactions);
  }, [filters]);

  // Filter transactions based on search input
  const filteredRows: TransactionRow[] = transactions
    .map((row: any) => ({
      ...row,
      customer: Number(row.customer), // Ensure customer is a number
      risk: "Risk",
    }))
    .filter(
      (tx: TransactionRow) =>
        tx.customer.toString().toLowerCase().includes(search.toLowerCase()) ||
        tx.total_amount.toString().includes(search)
    );

  // Handle row click to open modal
  // Sets the selected transaction and opens the modal.
  const handleRowClick = (params: { row: TransactionRow }) => {
    setSelected(params.row);
    setModalOpen(true);
  };

  // Render the component
  return (
    // Main Paper container for the transactions feed
    <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        Recent Suspicious Transactions
      </Typography>
      <TextField
        fullWidth
        size="small"
        placeholder="Search by customer or amount..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        sx={{ mb: 2 }}
      />
      {/* DataGrid to display transactions */}
      {/* Uses filteredRows to show only relevant transactions based on search input */}
      <div style={{ height: 350, width: "100%" }}>
        <DataGrid<TransactionRow>
          rows={filteredRows}
          columns={columns}
          pageSizeOptions={[5]}
          initialState={{
            pagination: { paginationModel: { pageSize: 5, page: 0 } }
          }}
          disableRowSelectionOnClick
          autoHeight
          onRowClick={handleRowClick}
        />
      </div>
      {/* Transaction details modal */}
      {/* Opens when a row is clicked, showing detailed transaction info */}
      <TransactionModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        transaction={selected}
      />
    </Paper>
  );
};

export default TransactionsFeed;