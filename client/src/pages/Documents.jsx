import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { clearDocuments, deleteDocument, getDocuments } from "../api/ragApi";

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyKey, setBusyKey] = useState("");

  const totalChunks = useMemo(
    () => documents.reduce((sum, doc) => sum + (doc.chunks || 0), 0),
    [documents]
  );

  const loadDocuments = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getDocuments();
      setDocuments(Array.isArray(data?.documents) ? data.documents : []);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleDelete = async (source) => {
    setBusyKey(source);
    setError("");
    try {
      await deleteDocument(source);
      setDocuments((prev) => prev.filter((doc) => doc.source !== source));
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to delete document");
    } finally {
      setBusyKey("");
    }
  };

  const handleClearAll = async () => {
    setBusyKey("ALL");
    setError("");
    try {
      await clearDocuments();
      setDocuments([]);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to clear documents");
    } finally {
      setBusyKey("");
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h2>Document Context</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={loadDocuments} disabled={loading || !!busyKey}>
            Refresh
          </button>
          <button onClick={handleClearAll} disabled={!documents.length || !!busyKey}>
            {busyKey === "ALL" ? "Clearing..." : "Clear All"}
          </button>
          <Link to="/chat">Back To Chat</Link>
        </div>
      </div>

      <p style={{ marginBottom: 12 }}>
        Existing uploaded documents are automatically used as chat context.
      </p>

      <p style={{ marginBottom: 12 }}>
        Documents: <strong>{documents.length}</strong> | Chunks Indexed: <strong>{totalChunks}</strong>
      </p>

      {error && (
        <div style={{ color: "#dc2626", marginBottom: 12 }}>{error}</div>
      )}

      {loading ? (
        <div>Loading documents...</div>
      ) : documents.length === 0 ? (
        <div>No documents in context.</div>
      ) : (
        <div style={{ display: "grid", gap: 8 }}>
          {documents.map((doc) => (
            <div
              key={doc.source}
              style={{
                border: "1px solid #d1d5db",
                borderRadius: 8,
                padding: 10,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>{doc.source}</div>
                <div style={{ fontSize: 13, opacity: 0.8 }}>Chunks: {doc.chunks}</div>
              </div>
              <button
                onClick={() => handleDelete(doc.source)}
                disabled={!!busyKey}
                style={{ color: "#b91c1c" }}
              >
                {busyKey === doc.source ? "Removing..." : "Remove"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
