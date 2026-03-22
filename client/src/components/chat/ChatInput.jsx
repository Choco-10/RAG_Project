import { useState } from "react";
import styles from "./ChatInput.module.css";

export default function ChatInput({ onSend }) {
  const [value, setValue] = useState(""); // message text
  const [files, setFiles] = useState([]); // selected files
  const [isSending, setIsSending] = useState(false); // loading state

  // Add new files from input
  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...newFiles]);
    e.target.value = ""; // reset input
  };

  // Remove a file from preview
  const removeFile = (idx) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  // Send message + files to parent
  const handleSend = async () => {
    if (!value.trim() && files.length === 0) return;
    if (isSending) return; // Prevent duplicate sends

    const contentToSend = value.trim();
    const filesToSend = files;

    // Clear UI immediately so typing box does not wait for server response/stream
    setValue("");
    setFiles([]);

    setIsSending(true);
    try {
      // Pass content and files to Chat.jsx handleSend
      await onSend({ content: contentToSend, files: filesToSend });
    } catch (err) {
      console.error("Send failed:", err);

      // Restore unsent content so user can retry
      setValue(contentToSend);
      setFiles(filesToSend);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Textarea for message */}
      <textarea
        className={styles.textarea}
        rows={1}
        placeholder="Type a message or attach files..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* File input */}
      <input
        type="file"
        multiple
        onChange={handleFileChange}
        className={styles.fileInput}
      />

      {/* File preview */}
      {files.length > 0 && (
        <div className={styles.filePreview}>
          {files.map((file, idx) => (
            <div key={idx} className={styles.fileItem}>
              <span>{file.name}</span>
              <button onClick={() => removeFile(idx)}>✕</button>
            </div>
          ))}
        </div>
      )}

      {/* Send button */}
      <button className={styles.button} onClick={handleSend} disabled={isSending}>
        {isSending ? "Sending..." : "Send"}
      </button>
    </div>
  );
}
