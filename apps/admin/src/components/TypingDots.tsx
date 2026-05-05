import { motion } from "framer-motion";
import { Scale } from "lucide-react";

export default function TypingDots() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="flex items-end gap-2"
    >
      <div className="w-7 h-7 rounded-lg bg-amber-500/15 flex items-center justify-center shrink-0">
        <Scale size={13} className="text-amber-400" />
      </div>
      <div className="px-4 py-2.5 bg-slate-800 border border-slate-700/50 rounded-2xl rounded-bl-sm">
        <span className="typing-dots">
          <span className="dot">•</span>
          <span className="dot">•</span>
          <span className="dot">•</span>
        </span>
      </div>
    </motion.div>
  );
}
