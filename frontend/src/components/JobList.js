import React from "react";
import JobCard from "./JobCard";

function JobList({ jobs, onRefresh }) {
  if (!jobs || jobs.length === 0) {
    return (
      <div className="job-list">
        <h2>Recent Downloads</h2>
        <div className="job-list-empty">
          <p>No downloads yet. Enter a URL above to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="job-list">
      <h2>Recent Downloads</h2>
      {jobs.map((job) => (
        <JobCard key={job.job_id} job={job} onRefresh={onRefresh} />
      ))}
    </div>
  );
}

export default JobList;
