import { motion } from "framer-motion";

export default function TypingDots() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="flex items-end gap-3 justify-start"
    >
      <div className="w-9 h-9 rounded-full bg-slate-800 text-white flex items-center justify-center text-sm shadow">
        🤖
      </div>

      <div className="px-5 py-3 max-w-[65%] rounded-2xl text-sm leading-relaxed shadow bg-slate-800 text-white rounded-bl-none">
        <span className="typing-dots">
          <span className="dot">•</span>
          <span className="dot">•</span>
          <span className="dot">•</span>
        </span>
      </div>
    </motion.div>
  );
}
