import { useState } from "react";
import styles from "./ChatInput.module.css";

export default function ChatInput({ onSend }) {
  const [value, setValue] = useState(""); // message text
  const [files, setFiles] = useState([]); // selected files

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

    // Pass content and files to Chat.jsx handleSend
    await onSend({ content: value.trim(), files });

    // Clear local input and preview
    setValue("");
    setFiles([]);
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
      <button className={styles.button} onClick={handleSend}>
        Send
      </button>
    </div>
  );
}
