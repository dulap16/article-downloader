import React, { useState, useEffect, useCallback } from "react";
import CrawlForm from "./components/CrawlForm";
import JobList from "./components/JobList";
import { getJobs } from "./api";
import "./App.css";

function App() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);

  const fetchJobs = useCallback(async () => {
    try {
      const data = await getJobs();
      setJobs(data);
      setError(null);
    } catch (err) {
      setError("Failed to connect to the server. Is the backend running?");
    }
  }, []);

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 2000);
    return () => clearInterval(interval);
  }, [fetchJobs]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>
            <span className="icon">📄</span> Article Downloader
          </h1>
          <p className="subtitle">
            Recursively download articles and all their linked pages
          </p>
        </div>
      </header>

      <main className="app-main">
        {error && <div className="error-banner">{error}</div>}
        <CrawlForm onSubmit={fetchJobs} />
        <JobList jobs={jobs} onRefresh={fetchJobs} />
      </main>

      <footer className="app-footer">
        <p>
          Article Downloader &middot;{" "}
          <a
            href="https://github.com/dulap16/article-downloader"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
