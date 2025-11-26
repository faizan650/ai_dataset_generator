import React from "react";
import logo from "/logo.png"; // ✅ Correct relative import (Vite handles this)

export default function Navbar({ user, onLogout, setPage }) {
  return (
    <nav className="bg-black border-b border-zinc-800 flex justify-between items-center p-4">
      {/* Left Section */}
      <div className="flex items-center gap-3">
        <img
          src={logo}
          alt="Dataset AI Logo"
          className="w-10 h-10 drop-shadow-lg"
        />
        <h1 className="text-xl font-bold text-white tracking-wide">
          Dataset AI
        </h1>
      </div>

      {/* Navigation Buttons */}
      <div className="flex gap-4 items-center text-gray-300">
        <button
          onClick={() => setPage("home")}
          className="hover:text-red-500 transition"
        >
          Home
        </button>

        <button
          onClick={() => setPage("datasets")}
          className="hover:text-red-500 transition"
        >
          My Datasets
        </button>

        <button
          onClick={onLogout}
          className="text-red-500 font-semibold hover:text-red-400 transition"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
