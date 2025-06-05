import React, { useEffect, useState } from "react";
import { fetchSalesOverTime } from "../../api/dashboard";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Paper, Typography, CircularProgress, Alert } from "@mui/material";

/**
 * SalesChart Component
    Displays a line chart of sales over time.
    Fetches sales data from the backend, filtered by the provided filters.
    Shows loading and error states.
    Responsive and fits inside a Paper widget.
  Props:
    filters: { dateFrom, dateTo, category, segment }
 */


type Filters = {
  dateFrom: string;
  dateTo: string;
  category: string;
  segment: string;
};

const SalesChart: React.FC<{ filters: Filters }> = ({ filters }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchSalesOverTime(filters)
      .then(setData)
      .catch(() => setError("Failed to load sales data."))
      .finally(() => setLoading(false));
  }, [filters]);

  return (
    <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        Sales Over Time
      </Typography>
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="total_sales" stroke="#1976d2" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Paper>
  );
};

export default SalesChart;