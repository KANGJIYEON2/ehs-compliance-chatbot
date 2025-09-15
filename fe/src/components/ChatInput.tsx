import { useState } from "react";
import { Send } from "lucide-react";

export type ChatInputProps = {
  onSend: (text: string) => void | Promise<void>;
  disabled?: boolean; // ← 이게 핵심!
};

export default function ChatInput({
  onSend,
  disabled = false,
}: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text);
    setText("");
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!text.trim() || disabled) return;
      onSend(text);
      setText("");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-3 p-4 border-t bg-white"
    >
      <textarea
        value={text}
        disabled={disabled}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        className="flex-1 px-4 py-3 text-sm border rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60 resize-none min-h-[44px] max-h-[160px]"
        placeholder={
          disabled
            ? "응답 생성 중..."
            : "메시지를 입력하세요... (Enter: 전송 / Shift+Enter: 줄바꿈)"
        }
      />
      <button
        type="submit"
        disabled={disabled}
        className="p-3 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition flex items-center justify-center shadow disabled:opacity-60 disabled:hover:bg-emerald-500"
        title={disabled ? "응답 생성 중" : "보내기"}
      >
        <Send size={20} />
      </button>
    </form>
  );
}
