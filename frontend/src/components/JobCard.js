import React, { useState } from "react";
import { downloadJob, deleteJob } from "../api";

function JobCard({ job, onRefresh }) {
  const [showPages, setShowPages] = useState(false);

  const progress =
    job.total_pages_found > 0
      ? Math.round((job.pages_downloaded / job.total_pages_found) * 100)
      : 0;

  const isActive = job.status === "pending" || job.status === "in_progress";

  const handleDownload = async () => {
    try {
      await downloadJob(job.job_id);
    } catch (err) {
      alert("Download failed: " + err.message);
    }
  };

  const handleDelete = async () => {
    if (window.confirm("Delete this download job?")) {
      try {
        await deleteJob(job.job_id);
        onRefresh();
      } catch (err) {
        alert("Delete failed: " + err.message);
      }
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleString();
  };

  return (
    <div className="job-card">
      <div className="job-card-header">
        <span className="job-url">{job.url}</span>
        <span className={`job-status status-${job.status}`}>{job.status}</span>
      </div>

      <div className="job-meta">
        <span>Depth: {job.depth}</span>
        <span>Pages: {job.pages_downloaded}</span>
        <span>{job.same_domain_only ? "Same domain" : "All domains"}</span>
        <span>Started: {formatDate(job.created_at)}</span>
      </div>

      {isActive && (
        <div className="job-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${Math.max(progress, 5)}%` }}
            />
          </div>
          <div className="progress-text">
            {job.pages_downloaded} / {job.total_pages_found || "?"} pages
            downloaded
          </div>
        </div>
      )}

      <div className="job-actions">
        {job.status === "completed" && (
          <button className="btn-download" onClick={handleDownload}>
            Download ZIP
          </button>
        )}
        <button className="btn-delete" onClick={handleDelete}>
          Delete
        </button>
      </div>

      {job.pages && job.pages.length > 0 && (
        <>
          <button
            className="job-pages-toggle"
            onClick={() => setShowPages(!showPages)}
          >
            {showPages
              ? "Hide pages"
              : `Show ${job.pages.length} downloaded pages`}
          </button>

          {showPages && (
            <div className="job-pages">
              {job.pages.map((page, i) => (
                <div className="page-item" key={i}>
                  <span className="page-depth">D{page.depth}</span>
                  <span className="page-title">
                    {page.title || page.url}
                  </span>
                  <span
                    className={
                      page.success ? "page-status-ok" : "page-status-fail"
                    }
                  >
                    {page.success ? "✓" : "✗"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default JobCard;
