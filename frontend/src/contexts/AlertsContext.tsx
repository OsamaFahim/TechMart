import React, { createContext, useContext, useState } from "react";

// This context provides a way to manage alerts in the application.
// It allows components to add and remove alerts, which can be used to show success, error, or informational messages to the user.
type Alert = { message: string; type: "success" | "error" | "info" };

// Create a context for alerts with default values
const AlertsContext = createContext<{
  alerts: Alert[];
  addAlert: (alert: Alert) => void;
  removeAlert: (index: number) => void;
}>({
  alerts: [],
  addAlert: () => {},
  removeAlert: () => {},
});

// Custom hook to use the AlertsContext
export const useAlerts = () => useContext(AlertsContext);

// Provider component to wrap around parts of the app that need access to alerts
// This component manages the state of alerts and provides functions to add and remove them.  
export const AlertsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const addAlert = (alert: Alert) => setAlerts((prev) => [...prev, alert]);
  const removeAlert = (index: number) =>
    setAlerts((prev) => prev.filter((_, i) => i !== index));

  return (
    <AlertsContext.Provider value={{ alerts, addAlert, removeAlert }}>
      {children}
    </AlertsContext.Provider>
  );
};

export default AlertsContext;