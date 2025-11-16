import React, { useState } from "react";
import API from "../api/axios";

export default function Login({ onLogin }) {
  const [isSignup, setIsSignup] = useState(false);
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [message, setMessage] = useState("");

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isSignup) {
        await API.post("/auth/signup", form);
        setMessage("Signup successful! You can now log in.");
        setIsSignup(false);
      } else {
        const res = await API.post("/auth/login", form);
        localStorage.setItem("user", JSON.stringify(res.data));
        onLogin(res.data);
      }
    } catch (err) {
      setMessage(err.response?.data?.detail || "Error occurred");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white">
      <div className="bg-zinc-900 p-8 rounded-xl shadow-lg w-96">
        <h2 className="text-2xl font-bold mb-4 text-center text-red-500">
          {isSignup ? "Create Account" : "Welcome Back"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignup && (
            <input
              type="text"
              name="username"
              placeholder="Username"
              value={form.username}
              onChange={handleChange}
              className="w-full p-2 bg-zinc-800 border border-zinc-700 rounded"
            />
          )}
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            className="w-full p-2 bg-zinc-800 border border-zinc-700 rounded"
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className="w-full p-2 bg-zinc-800 border border-zinc-700 rounded"
          />
          <button type="submit" className="w-full bg-red-600 hover:bg-red-700 py-2 rounded font-semibold">
            {isSignup ? "Sign Up" : "Login"}
          </button>
        </form>
        <p className="text-gray-400 text-sm mt-3 text-center">{message}</p>
        <button
          onClick={() => setIsSignup(!isSignup)}
          className="text-red-500 mt-4 text-sm underline block mx-auto"
        >
          {isSignup ? "Already have an account? Log in" : "No account? Sign up"}
        </button>
      </div>
    </div>
  );
}
