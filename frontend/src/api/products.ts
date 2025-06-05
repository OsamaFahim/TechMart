import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

export const fetchLowStockProducts = async () => {
  const res = await axios.get(`${API_BASE}/inventory/low-stock`);
  return res.data;
};

export const fetchTopProducts = async () => {
  const res = await axios.get(`${API_BASE}/analytics/top-products`);
  return res.data;
};