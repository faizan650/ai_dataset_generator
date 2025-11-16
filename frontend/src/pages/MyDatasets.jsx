import React, { useEffect, useState } from "react";
import axios from "axios";
import { FaDatabase, FaDownload } from "react-icons/fa";

const API_BASE = "http://127.0.0.1:8000";

export default function MyDatasets({ user }) {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        const res = await axios.get(
          `${API_BASE}/queries/user?user_email=${user.email}`
        );
        setDatasets(res.data.datasets || []);
      } catch (err) {
        console.error("❌ Error fetching datasets:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDatasets();
  }, [user.email]);

  if (loading) {
    return <p className="text-center mt-20 text-gray-400">Loading datasets…</p>;
  }

  return (
    <div className="max-w-3xl mx-auto mt-10 p-6 bg-black/70 border border-zinc-800 rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold flex items-center gap-2 mb-4">
        <FaDatabase className="text-red-500" /> My Datasets
      </h2>

      {datasets.length === 0 ? (
        <p className="text-gray-400">No datasets found yet.</p>
      ) : (
        <ul className="space-y-4">
          {datasets.map((d, i) => (
            <li
              key={i}
              className="flex justify-between items-center bg-zinc-900 rounded-lg p-3"
            >
              <div>
                <p className="font-semibold text-white">{d.query}</p>
                <p className="text-sm text-gray-500">{d.file_name}</p>
              </div>

              <a
                href={`${API_BASE}/download/${d.file_name}`}
                download={d.file_name}
                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2"
              >
                <FaDownload /> Download
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
