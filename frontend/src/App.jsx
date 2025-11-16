import React, { useState } from "react";
import Home from "./pages/Home";
import Login from "./pages/Login";
import MyDatasets from "./pages/MyDatasets";
import NavBar from "./components/NavBar";

export default function App() {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  const [page, setPage] = useState("home");

  const handleLogout = () => {
    localStorage.removeItem("user");
    setUser(null);
  };

  if (!user) {
    return (
      <div className="bg-black min-h-screen flex items-center justify-center text-white">
        <Login onLogin={setUser} />
      </div>
    );
  }

  return (
    <div className="bg-black text-white min-h-screen font-inter">
      <NavBar user={user} onLogout={handleLogout} setPage={setPage} />
      <main className="pt-20">
        {page === "home" && <Home user={user} />}
        {page === "datasets" && <MyDatasets user={user} />}
      </main>
    </div>
  );
}
