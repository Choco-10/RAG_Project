import { useEffect, useRef } from "react";
import useChatStore from "../../store/chatStore";
import ChatMessage from "./ChatMessage";
import styles from "./ChatWindow.module.css";

export default function ChatWindow({ loading }) {
  const messages = useChatStore((state) => state.messages);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className={styles.container}>
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}

      {loading && (
        <div className={styles.aiTyping}>AI is typing...</div>
      )}

      <div ref={chatEndRef} />
    </div>
  );
}
