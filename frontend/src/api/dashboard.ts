import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

export const fetchDashboardOverview = async () => {
  const res = await axios.get(`${API_BASE}/dashboard/overview`);
  return res.data;
};

//Fetch sales over time with filters
export const fetchSalesOverTime = async (filters: {
  dateFrom: string;
  dateTo: string;
  category: string;
  segment: string;
}) => {
  // Construct query parameters based on filters
  // Only include parameters that are set
  const params: any = {};
  if (filters.dateFrom) params.dateFrom = filters.dateFrom;
  if (filters.dateTo) params.dateTo = filters.dateTo;
  if (filters.category && filters.category !== "All") params.category = filters.category;
  if (filters.segment && filters.segment !== "All") params.segment = filters.segment;
  const res = await axios.get(`${API_BASE}/analytics/sales-over-time`, { params });
  return res.data;
};