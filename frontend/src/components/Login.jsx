import React from "react";
import "./Login.css";
import { supabase } from "../../supabaseClient"; // our supbase client.js
const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;
export default function Login() {
  // -------------------- Handle Login --------------------
  const handleLogin = async () => {
    try {
      await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: FRONTEND_URL, 
        },
      });
    } catch (error) {
      console.error("Login failed:", error.message);
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <button onClick={handleLogin} className="google-login-btn">
        Login with Google
      </button>
    </div>
  );
}
