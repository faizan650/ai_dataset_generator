import React from "react";
import logo from "/logo.png";

export default function Navbar({ user, onLogout, setPage }) {
  return (
    <nav className="bg-black border-b border-zinc-800 flex justify-between items-center p-4">
      <div className="flex items-center gap-3">
        <img src={logo} alt="Dataset AI Logo" className="w-10 h-10" />
        <h1 className="text-xl font-bold text-white">Dataset AI</h1>
      </div>

      <div className="flex gap-4 items-center">
        <button onClick={() => setPage("home")} className="hover:text-red-500">
          Home
        </button>
        <button
          onClick={() => setPage("datasets")}
          className="hover:text-red-500"
        >
          My Datasets
        </button>
        <button onClick={onLogout} className="text-red-500 font-semibold">
          Logout
        </button>
      </div>
    </nav>
  );
}
