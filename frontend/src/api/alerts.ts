import axios from "axios";

//base API URL for the backend
//These are the urls where data would be sent to the backend to receive the response
const API_BASE = "http://127.0.0.1:8000/api";

export const createAlert = async (alertData: { alert: string }) => {
  const res = await axios.post(`${API_BASE}/alerts`, alertData);
  return res.data;
};