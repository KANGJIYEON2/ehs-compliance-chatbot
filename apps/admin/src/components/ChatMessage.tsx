import { motion } from "framer-motion";

type Props = {
  sender: "user" | "bot";
  text: string;
  children?: React.ReactNode;
};

export default function ChatMessage({ sender, text, children }: Props) {
  const isUser = sender === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}
    >
      <div
        className={`flex items-end gap-3 ${
          isUser ? "justify-end" : "justify-start"
        }`}
      >
        {!isUser && (
          <div className="w-9 h-9 rounded-full bg-slate-800 text-white flex items-center justify-center text-sm shadow">
            🤖
          </div>
        )}
        <div
          className={`px-5 py-3 max-w-[65%] rounded-2xl text-sm leading-relaxed shadow whitespace-pre-wrap ${
            isUser
              ? "bg-emerald-500 text-white rounded-br-none"
              : "bg-slate-800 text-white rounded-bl-none"
          }`}
        >
          {text}
        </div>
      </div>

      {/* 버블 하단 확장 블록(근거 카드 등) */}
      {children}
    </motion.div>
  );
}
