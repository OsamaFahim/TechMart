import React from "react";
import { AlertsProvider } from "./contexts/AlertsContext";
import { DashboardProvider } from "./contexts/DashboardContext";
import Dashboard from "./pages/Dashboard";
import { Snackbar, Alert } from "@mui/material";
import AlertsContext from "./contexts/AlertsContext";

// GlobalSnackbar as a child component
const GlobalSnackbar: React.FC = () => {
  const { alerts, removeAlert } = React.useContext(AlertsContext);
  const alert = alerts[0];
  const handleClose = () => {
    if (alerts.length > 0) removeAlert(0);
  };
  return (
    <Snackbar
      open={!!alert}
      autoHideDuration={4000}
      onClose={handleClose}
      anchorOrigin={{ vertical: "top", horizontal: "center" }}
    >
      {alert && <Alert severity={alert.type} onClose={handleClose}>{alert.message}</Alert>}
    </Snackbar>
  );
};

const App: React.FC = () => (
  <AlertsProvider>
    <DashboardProvider>
      <Dashboard />
      <GlobalSnackbar />
    </DashboardProvider>
  </AlertsProvider>
);

export default App;