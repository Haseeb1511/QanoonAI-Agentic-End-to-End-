import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL;

// ✅ Create axios instance with interceptor
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

// ✅ Add auth token to all requests
axiosInstance.interceptors.request.use(
  async (config) => {
    // Import supabase in your api.jsx file
    const { supabase } = await import('../supabaseClient');
    const { data: { session } } = await supabase.auth.getSession();
    
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

export const api = {
  // Get all threads for sidebar
  getAllThreads: async (token) => {
    const response = await axiosInstance.get('/all_threads', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  // Get specific thread details
  getThread: async (threadId, token) => {
    const response = await axiosInstance.get(`/get_threads/${threadId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  }
};