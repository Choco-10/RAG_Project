import { create } from "zustand";
import { v4 as uuidv4 } from "uuid";

const useChatStore = create((set) => ({
  messages: [],

  addMessage: ({ role, content = "", files = [] }) => {
    const message = {
      id: uuidv4(),
      role,
      content,
      files: files.map((f) => ({
        file: f,
        progress: 0,
        uploaded: false,
        error: null,
      })),
    };

    set((state) => ({ messages: [...state.messages, message] }));
    return message.id;
  },

  updateFileProgress: (messageId, fileIndex, progress) => {
    set((state) => ({
      messages: state.messages.map((msg) => {
        if (msg.id !== messageId) return msg;
        const updatedFiles = [...msg.files];
        updatedFiles[fileIndex] = { ...updatedFiles[fileIndex], progress };
        return { ...msg, files: updatedFiles };
      }),
    }));
  },

  markFileUploaded: (messageId, fileIndex) => {
    set((state) => ({
      messages: state.messages.map((msg) => {
        if (msg.id !== messageId) return msg;
        const updatedFiles = [...msg.files];
        updatedFiles[fileIndex] = {
          ...updatedFiles[fileIndex],
          progress: 100,
          uploaded: true,
        };
        return { ...msg, files: updatedFiles };
      }),
    }));
  },

  markFileError: (messageId, fileIndex, error) => {
    set((state) => ({
      messages: state.messages.map((msg) => {
        if (msg.id !== messageId) return msg;
        const updatedFiles = [...msg.files];
        updatedFiles[fileIndex] = { ...updatedFiles[fileIndex], error };
        return { ...msg, files: updatedFiles };
      }),
    }));
  },

  updateLastAssistantMessage: (chunk) => {
    set((state) => {
      if (!state.messages.length) return state;
      const last = state.messages[state.messages.length - 1];
      if (last.role !== "assistant") return state;

      return {
        messages: [
          ...state.messages.slice(0, -1),
          { ...last, content: last.content + chunk },
        ],
      };
    });
  },

  reset: () => set({ messages: [] }),
}));

export default useChatStore;