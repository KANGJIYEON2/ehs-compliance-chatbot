import { useState } from "react";
import { Send } from "lucide-react";

export type ChatInputProps = {
  onSend: (text: string) => void | Promise<void>;
  disabled?: boolean;
};

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [text, setText] = useState("");

  const submit = () => {
    if (!text.trim() || disabled) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="flex items-end gap-2 p-3 border-t border-slate-800 bg-slate-900">
      <textarea
        value={text}
        disabled={disabled}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
        }}
        className="flex-1 px-3.5 py-2.5 text-[13px] bg-slate-800 text-white border border-slate-700 rounded-xl focus:outline-none focus:border-emerald-500 disabled:opacity-50 resize-none min-h-[40px] max-h-[120px] placeholder-slate-500"
        placeholder={disabled ? "분석 중..." : "법령 관련 질문을 입력하세요..."}
        rows={1}
      />
      <button
        onClick={submit}
        disabled={disabled || !text.trim()}
        className="p-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl transition-colors disabled:opacity-40 shrink-0"
      >
        <Send size={16} />
      </button>
    </div>
  );
}
