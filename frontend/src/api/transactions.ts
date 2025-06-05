import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

export const fetchSuspiciousTransactions = async () => {
  const res = await axios.get(`${API_BASE}/transactions/suspicious`);
  return res.data;
};

export const createTransaction = async (transactionData: any) => {
  const res = await axios.post(`${API_BASE}/transactions`, transactionData);
  return res.data;
};