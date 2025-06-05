import React from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Divider } from "@mui/material";


// Transaction type
// Represents a single transaction with relevant fields.
type Transaction = {
  id: number;
  customer: number;
  total_amount: number;
  timestamp: string;
  status?: string;
  payment_method?: string;
  // Add more fields as needed
};

// Props type
// Defines the properties expected by the TransactionModal component.
type Props = {
  open: boolean;
  onClose: () => void;
  transaction: Transaction | null;
};

// TransactionModal Component
// Displays detailed information about a transaction in a modal dialog.
const TransactionModal: React.FC<Props> = ({ open, onClose, transaction }) => {
  if (!transaction) return null;

  // Render the modal dialog with transaction details
  // It includes fields like ID, customer, amount, timestamp, status, and payment method.
  return (
    // Dialog component from Material-UI
    // It uses open prop to control visibility and onClose callback for closing the dialog.
    // maxWidth and fullWidth props for responsive design
    // DialogTitle for the header, DialogContent for the body, and DialogActions for buttons.
    // Typography for text formatting, Divider for visual separation.
    // The transaction details are displayed using Typography components.
    // The timestamp is formatted to a readable string using toLocaleString.
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Transaction Details</DialogTitle>
      <DialogContent dividers>
        <Typography>ID: {transaction.id}</Typography>
        <Typography>Customer: {transaction.customer}</Typography>
        <Typography>Amount: ${transaction.total_amount}</Typography>
        <Typography>Timestamp: {new Date(transaction.timestamp).toLocaleString()}</Typography>
        {transaction.status && <Typography>Status: {transaction.status}</Typography>}
        {transaction.payment_method && <Typography>Payment: {transaction.payment_method}</Typography>}
        <Divider sx={{ my: 2 }} />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained">Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default TransactionModal;