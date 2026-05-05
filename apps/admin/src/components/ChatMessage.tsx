import { motion } from "framer-motion";
import { Scale } from "lucide-react";

type Props = {
  sender: "user" | "bot";
  text: string;
  children?: React.ReactNode;
};

export default function ChatMessage({ sender, text, children }: Props) {
  const isUser = sender === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
    >
      <div className={`flex items-end gap-2 ${isUser ? "justify-end" : "justify-start"} max-w-[85%]`}>
        {!isUser && (
          <div className="w-7 h-7 rounded-lg bg-amber-500/15 flex items-center justify-center shrink-0">
            <Scale size={13} className="text-amber-400" />
          </div>
        )}
        <div
          className={`px-4 py-2.5 rounded-2xl text-[13px] leading-relaxed whitespace-pre-wrap ${
            isUser
              ? "bg-emerald-600 text-white rounded-br-sm"
              : "bg-slate-800 text-slate-200 border border-slate-700/50 rounded-bl-sm"
          }`}
        >
          {text}
        </div>
      </div>

      {children}
    </motion.div>
  );
}
