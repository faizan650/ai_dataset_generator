import React, { useState, useEffect } from "react";
import API from "../api/axios";
import { motion } from "framer-motion";
import { FaDownload, FaDatabase } from "react-icons/fa";
import DatasetPreview from "../components/DatasetPreview";
import ProgressBar from "../components/ProgressBar";
import logo from "../assets/logo.png";
import "../styles/main.css";

export default function Home({ user }) {
  const [domain, setDomain] = useState("");
  const [records, setRecords] = useState(100);
  const [batchSize, setBatchSize] = useState(20);
  const [fileName, setFileName] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [message, setMessage] = useState("");
  const [preview, setPreview] = useState([]);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("idle");
  const [loading, setLoading] = useState(false);

  // ---------------- Poll status ----------------
  useEffect(() => {
    let interval;
    if (status === "running" && fileName) {
      interval = setInterval(checkStatus, 3000);
    }
    return () => clearInterval(interval);
  }, [status, fileName]);

  // ---------------- Start dataset generation ----------------
  const startGeneration = async () => {
    if (!domain.trim()) {
      setMessage("⚠️ Please enter a dataset topic.");
      return;
    }

    const storedUser = JSON.parse(localStorage.getItem("user")) || {};

    setMessage("");
    setProgress(0);
    setStatus("running");
    setLoading(true);
    setPreview([]);

    try {
      const formData = new FormData();
      formData.append("domain", domain);
      formData.append("records", String(records));
      formData.append("batch_size", String(batchSize));
      formData.append("user_email", storedUser.email || "");

      const res = await API.post("/generate/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (res.data?.file_name) {
        setFileName(res.data.file_name);

        // FIXED: No API.defaults.baseURL (Cloudflare breaks it)
        setDownloadUrl(
          import.meta.env.VITE_BACKEND_URL + res.data.download_url
        );

        setMessage(`🧠 Generating dataset for '${domain}' ...`);
        setStatus("running");
      }
    } catch (err) {
      console.error("❌ Generation failed:", err);
      setMessage("❌ Error starting generation.");
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  // ---------------- Check Status (CLOUD SAFE) ----------------
  const checkStatus = async () => {
    if (!fileName) return;

    try {
      const res = await API.get("/status", {
        params: { file_name: fileName }
      });

      setProgress(res.data.progress);
      setStatus(res.data.status);

      if (res.data.progress >= 100 || res.data.status === "completed") {
        setProgress(100);
        setStatus("completed");
        setTimeout(fetchPreview, 600);
      }
    } catch (err) {
      console.error("❌ Status error:", err);
      setStatus("error");
      setMessage("❌ Could not reach backend.");
    }
  };

  // ---------------- Fetch Preview ----------------
  const fetchPreview = async () => {
    try {
      const res = await API.get("/preview", {
        params: { file_name: fileName, lines: 8 }
      });

      if (res.data.preview?.length > 0) {
        setPreview(res.data.preview);
        setMessage("✅ Dataset generation complete!");
      } else {
        setMessage("⚠️ No preview available.");
      }
    } catch (err) {
      console.error("❌ Preview fetch failed:", err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-black text-white font-inter">
      
      {/* Header */}
      <header className="text-center mt-10 mb-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center justify-center gap-3 mb-3">
            <img src={logo} alt="Dataset AI Logo" className="w-16 h-16 drop-shadow-lg" />
            <h1 className="text-4xl font-bold tracking-wide">AI Dataset Generator</h1>
          </div>
          <p className="text-gray-400">
            Create synthetic JSONL datasets for LLM fine-tuning — fast & domain-specific.
          </p>
        </motion.div>
      </header>

      {/* Main Section */}
      <main className="flex-1 flex flex-col items-center">
        <div className="w-full max-w-3xl bg-black/60 border border-red-900/30 rounded-2xl shadow-lg p-6 mx-4">
          
          {/* Input Section */}
          <div className="space-y-4">
            <div className="flex gap-3">
              <input
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="Enter domain (e.g. sports consultant, text-to-sql)"
                className="flex-1 p-3 rounded-lg bg-zinc-900 border border-zinc-700"
              />
              <button
                onClick={startGeneration}
                disabled={loading}
                className="px-5 py-3 bg-red-600 hover:bg-red-700 rounded-lg"
              >
                {loading ? "Starting..." : "Generate"}
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div>
                <label className="text-sm text-gray-400">Records</label>
                <input
                  type="number"
                  value={records}
                  onChange={(e) => setRecords(Number(e.target.value))}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-2"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400">Batch Size</label>
                <input
                  type="number"
                  value={batchSize}
                  onChange={(e) => setBatchSize(Number(e.target.value))}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-2"
                />
              </div>

              {status === "completed" && (
                <div className="flex flex-col justify-end">
                  <a
                    href={downloadUrl}
                    download={fileName}
                    className="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 rounded-lg p-2"
                  >
                    <FaDownload /> Download
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* Progress */}
          <div className="mt-6 bg-zinc-900/60 rounded-lg p-4 border border-zinc-800">
            <p className="text-gray-300 text-sm mb-2">{message}</p>
            <ProgressBar progress={progress} />
            <p className="text-xs text-gray-400 mt-2">
              Status: {status} — {progress}%
            </p>
          </div>

          {/* Preview */}
          {preview.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="mt-6 bg-black/70 border border-zinc-800 rounded-lg p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <FaDatabase className="text-red-500" /> Dataset Preview
              </h3>
              <DatasetPreview data={preview} />
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}
