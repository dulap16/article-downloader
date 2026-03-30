/**
 * API client for the Article Downloader backend.
 */

const API_BASE = process.env.REACT_APP_API_URL || "/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res;
}

export async function startCrawl(url, depth, sameDomainOnly) {
  const res = await request("/crawl", {
    method: "POST",
    body: JSON.stringify({ url, depth, same_domain_only: sameDomainOnly }),
  });
  return res.json();
}

export async function getJobs() {
  const res = await request("/jobs");
  return res.json();
}

export async function getJob(jobId) {
  const res = await request(`/jobs/${jobId}`);
  return res.json();
}

export async function downloadJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/download`);
  if (!res.ok) throw new Error("Download failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `articles_${jobId}.zip`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function deleteJob(jobId) {
  await request(`/jobs/${jobId}`, { method: "DELETE" });
}
