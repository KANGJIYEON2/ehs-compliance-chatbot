import { useEffect, useRef, useState } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import TypingDots from "./TypingDots";
import EvidenceToggle, { type Hit } from "./EvidenceToggle";
import { RotateCcw, Scale, Settings2 } from "lucide-react";

const API_BASE =
  (import.meta as any)?.env?.VITE_API_URL ?? "http://127.0.0.1:8000";

type AskResponse = {
  question: string;
  answer: string;
  mode: "auto" | "law" | "rule";
  hits: Hit[];
  used_dbs: string[];
};

const GREETING =
  "안녕하세요. SafetyAI 법령 검색 엔진입니다.\n산업안전보건법, 중대재해처벌법 등 EHS 규제에 대해 질문하세요.";

type Msg = { sender: "user" | "bot"; text: string; hits?: Hit[] };

export default function ChatWindow() {
  const [messages, setMessages] = useState<Msg[]>([{ sender: "bot", text: GREETING }]);
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [mode, setMode] = useState<"auto" | "law" | "rule">("auto");
  const [useLaw, setUseLaw] = useState(true);
  const [useRule, setUseRule] = useState(true);
  const [topk, setTopk] = useState(5);
  const [ctxChars, setCtxChars] = useState(6000);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" }), 50);
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;
    setMessages((prev) => [...prev, { sender: "user", text }]);
    setLoading(true);
    try {
      const dbs: string[] = [];
      if (useLaw) dbs.push("vector_db_law");
      if (useRule) dbs.push("vector_db_rule");
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text, topk, mode, ctx_chars: ctxChars, dbs: dbs.length ? dbs : undefined }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: AskResponse = await res.json();
      setMessages((prev) => [...prev, { sender: "bot", text: data.answer, hits: data.hits ?? [] }]);
    } catch (err: any) {
      setMessages((prev) => [...prev, { sender: "bot", text: `오류: ${err?.message || "알 수 없는 오류"}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl overflow-hidden border border-slate-200 shadow-sm">
      {/* 헤더 */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center">
            <Scale size={16} className="text-emerald-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800 leading-none">법령 검색 엔진</p>
            <p className="text-[10px] text-slate-400 mt-0.5">RAG + 국가법령정보센터 API</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => setShowSettings(!showSettings)}
            className={`p-1.5 rounded-lg transition-colors ${showSettings ? "bg-slate-100 text-slate-700" : "text-slate-400 hover:text-slate-600"}`}>
            <Settings2 size={15} />
          </button>
          <button onClick={() => setMessages([{ sender: "bot", text: GREETING }])}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg transition-colors">
            <RotateCcw size={15} />
          </button>
        </div>
      </div>

      {showSettings && (
        <div className="px-5 py-2 bg-slate-50 border-b border-slate-100 flex items-center gap-4 text-[11px] text-slate-500 flex-wrap">
          <div className="flex items-center gap-1.5">
            <span>모드</span>
            <select value={mode} onChange={(e) => setMode(e.target.value as any)}
              className="px-2 py-0.5 bg-white text-slate-700 rounded border border-slate-200 text-[11px]">
              <option value="auto">자동</option>
              <option value="law">법률</option>
              <option value="rule">규칙/별표</option>
            </select>
          </div>
          <label className="flex items-center gap-1"><input type="checkbox" checked={useLaw} onChange={(e) => setUseLaw(e.target.checked)} className="w-3 h-3 accent-emerald-600" />법률</label>
          <label className="flex items-center gap-1"><input type="checkbox" checked={useRule} onChange={(e) => setUseRule(e.target.checked)} className="w-3 h-3 accent-emerald-600" />규칙</label>
          <div className="flex items-center gap-1.5">
            <span>TopK</span>
            <input type="number" min={1} max={20} value={topk} onChange={(e) => setTopk(Math.min(20, Math.max(1, +e.target.value)))}
              className="w-12 px-1.5 py-0.5 bg-white text-slate-700 rounded border border-slate-200 text-[11px]" />
          </div>
        </div>
      )}

      <div className="px-5 py-1.5 bg-amber-50 border-b border-amber-100">
        <p className="text-[10px] text-amber-600">AI 답변은 참고 정보입니다. 법적 판단은 최신 법령 원문을 확인하세요.</p>
      </div>

      <div className="flex-1 p-5 space-y-4 overflow-y-auto bg-slate-50/30">
        {messages.map((msg, i) => (
          <ChatMessage key={i} sender={msg.sender} text={msg.text}>
            {msg.sender === "bot" && msg.hits && msg.hits.length > 0 && (
              <div className="mt-2"><EvidenceToggle hits={msg.hits} /></div>
            )}
          </ChatMessage>
        ))}
        {loading && <TypingDots />}
        <div ref={bottomRef} />
      </div>

      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  );
}
