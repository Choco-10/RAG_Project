import { useState } from "react";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";
import useChatStore from "../store/chatStore";
import { askRagQuery, uploadDocument } from "../api/ragApi";
import styles from "./Chat.module.css";

export default function Chat() {
  const addMessage = useChatStore((state) => state.addMessage);
  const updateFileProgress = useChatStore((state) => state.updateFileProgress);
  const markFileUploaded = useChatStore((state) => state.markFileUploaded);
  const markFileError = useChatStore((state) => state.markFileError);
  const updateLastAssistantMessage = useChatStore(
    (state) => state.updateLastAssistantMessage
  );
  const resetChat = useChatStore((state) => state.reset);

  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() =>
    crypto?.randomUUID ? crypto.randomUUID() : String(Date.now())
  );

  const handleSend = async ({ content, files }) => {
    if (!content && (!files || files.length === 0)) return;

    const messageId = addMessage({
      role: "user",
      content: content || "",
      files: files || [],
    });

    if (files && files.length > 0) {
      for (let idx = 0; idx < files.length; idx++) {
        const file = files[idx];
        try {
          await uploadDocument(file, (percent) => {
            updateFileProgress(messageId, idx, percent);
          });
          markFileUploaded(messageId, idx);
        } catch (err) {
          markFileError(messageId, idx, err?.message || "Upload failed");
        }
      }
    }

    if (content) addMessage({ role: "assistant", content: "" });

    if (content) {
      setLoading(true);
      try {
        const res = await askRagQuery({
          question: content,
          session_id: sessionId,
          top_k: 5,
        });
        updateLastAssistantMessage(res?.answer || "No response");
      } catch (err) {
        updateLastAssistantMessage("Error generating answer.");
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>RAG Chat</h2>
        <button className={styles.newChatButton} onClick={resetChat}>
          New Chat
        </button>
      </div>

      <div className={styles.chatWindow}>
        <ChatWindow loading={loading} />
      </div>

      <div className={styles.chatInputWrapper}>
        <ChatInput onSend={handleSend} />
      </div>
    </div>
  );
}