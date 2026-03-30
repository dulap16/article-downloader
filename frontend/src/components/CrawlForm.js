import React, { useState } from "react";
import { startCrawl } from "../api";

function CrawlForm({ onSubmit }) {
  const [url, setUrl] = useState("");
  const [depth, setDepth] = useState(1);
  const [sameDomainOnly, setSameDomainOnly] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);

    try {
      await startCrawl(url.trim(), depth, sameDomainOnly);
      setUrl("");
      onSubmit();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="crawl-form" onSubmit={handleSubmit}>
      <h2>Download Articles</h2>

      <div className="form-row">
        <div className="form-group url-group">
          <label htmlFor="url">Article URL</label>
          <input
            id="url"
            type="url"
            placeholder="https://example.com/article"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="depth">Depth</label>
          <select
            id="depth"
            value={depth}
            onChange={(e) => setDepth(Number(e.target.value))}
          >
            <option value={0}>0 — Only this page</option>
            <option value={1}>1 — This + linked pages</option>
            <option value={2}>2 — Two levels deep</option>
            <option value={3}>3 — Three levels deep</option>
            <option value={4}>4 — Four levels deep</option>
            <option value={5}>5 — Five levels deep</option>
          </select>
          <span className="depth-hint">
            Higher depth = more pages downloaded
          </span>
        </div>
      </div>

      <div className="checkbox-row">
        <input
          type="checkbox"
          id="sameDomain"
          checked={sameDomainOnly}
          onChange={(e) => setSameDomainOnly(e.target.checked)}
        />
        <label htmlFor="sameDomain">
          Stay on the same domain (recommended)
        </label>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? "Starting…" : "Download Articles"}
      </button>
    </form>
  );
}

export default CrawlForm;
