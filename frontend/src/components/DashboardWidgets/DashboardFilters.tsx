import React, { useState, useEffect } from "react";
import { Box, TextField, MenuItem, Button } from "@mui/material";
import { fetchCategories, fetchSegments } from "../../api/products";

// DashboardFilters Component

type Props = {
  onFilter: (filters: { dateFrom: string; dateTo: string; category: string; segment: string }) => void;
};

//REMOVE HARDODED CATEGORIES AND SEGMENTS and fetch them from API
// Predefined categories and segments for filtering
//const categories = ["All", "Electronics", "Clothing", "Books"];
// Predefined customer segments for filtering
// I will adjust it later to send an api call to first fetch the categories and segments
//const segments = ["All", "Retail", "Wholesale"];

// DashboardFilters component
// Provides date range, category, and segment filters for the dashboard
const DashboardFilters: React.FC<Props> = ({ onFilter }) => {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [category, setCategory] = useState("All");
  const [segment, setSegment] = useState("All");
  // State for categories and segments, initialized with "All"
  const [categories, setCategories] = useState<string[]>(["All"]);
  const [segments, setSegments] = useState<string[]>(["All"]);

  // Fetch categories and segments from the backend API on mount
  useEffect(() => {
    fetchCategories().then((cats) => {
      // Only add if there are categories in the DB
      setCategories(["All", ...cats.filter((c: string) => !!c)]);
    });
    fetchSegments().then((segs) => {
      setSegments(["All", ...segs.filter((s: string) => !!s)]);
    });
  }, []);

  const handleApply = () => {
    onFilter({ dateFrom, dateTo, category, segment });
  };

  // Render the filter controls
  // Date fields use type="date" for date pickers
  // Category and segment fields use select for dropdowns
  // Apply button triggers the onFilter callback with current filter values
  // Flexbox layout for responsive design
  // Gap and margin for spacing
  // Flex-wrap for wrapping on smaller screens
  return (
    <Box display="flex" gap={2} mb={2} flexWrap="wrap">
      <TextField
        label="From"
        type="date"
        size="small"
        InputLabelProps={{ shrink: true }}
        value={dateFrom}
        onChange={e => setDateFrom(e.target.value)}
      />
      <TextField
        label="To"
        type="date"
        size="small"
        InputLabelProps={{ shrink: true }}
        value={dateTo}
        onChange={e => setDateTo(e.target.value)}
      />
      <TextField
        label="Category"
        select
        size="small"
        value={category}
        onChange={e => setCategory(e.target.value)}
      >
        {categories.map(cat => (
          <MenuItem key={cat} value={cat}>{cat}</MenuItem>
        ))}
      </TextField>
      <TextField
        label="Customer Segment"
        select
        size="small"
        value={segment}
        onChange={e => setSegment(e.target.value)}
      >
        {segments.map(seg => (
          <MenuItem key={seg} value={seg}>{seg}</MenuItem>
        ))}
      </TextField>
      <Button variant="contained" onClick={handleApply}>Apply</Button>
    </Box>
  );
};

export default DashboardFilters;