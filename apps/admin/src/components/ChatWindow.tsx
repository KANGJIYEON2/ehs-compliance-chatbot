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
  const [messages, setMessages] = useState<Msg[]>([
    { sender: "bot", text: GREETING },
  ]);
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const [mode, setMode] = useState<"auto" | "law" | "rule">("auto");
  const [useLaw, setUseLaw] = useState(true);
  const [useRule, setUseRule] = useState(true);
  const [topk, setTopk] = useState(5);
  const [ctxChars, setCtxChars] = useState(6000);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const t = setTimeout(() => {
      bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, 50);
    return () => clearTimeout(t);
  }, [messages, loading]);

  const handleReset = () => {
    setMessages([{ sender: "bot", text: GREETING }]);
  };

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
        body: JSON.stringify({
          question: text,
          topk,
          mode,
          ctx_chars: ctxChars,
          dbs: dbs.length ? dbs : undefined,
        }),
      });

      if (!res.ok) throw new Error(await res.text());
      const data: AskResponse = await res.json();
      setMessages((prev) => [...prev, { sender: "bot", text: data.answer, hits: data.hits ?? [] }]);
    } catch (err: any) {
      setMessages((prev) => [...prev, { sender: "bot", text: `오류가 발생했습니다: ${err?.message || "알 수 없는 오류"}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 rounded-xl overflow-hidden border border-slate-800">
      {/* 헤더 */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-amber-500/20 rounded-lg flex items-center justify-center">
            <Scale size={14} className="text-amber-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-white leading-none">법령 검색 엔진</p>
            <p className="text-[10px] text-slate-500 mt-0.5">산안법 · 중대재해처벌법 · 규칙/별표</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <button onClick={() => setShowSettings(!showSettings)}
            className="p-1.5 text-slate-500 hover:text-white transition-colors rounded-lg hover:bg-slate-800" title="설정">
            <Settings2 size={15} />
          </button>
          <button onClick={handleReset}
            className="p-1.5 text-slate-500 hover:text-white transition-colors rounded-lg hover:bg-slate-800" title="초기화">
            <RotateCcw size={15} />
          </button>
        </div>
      </div>

      {/* 설정 패널 (접이식) */}
      {showSettings && (
        <div className="px-4 py-2.5 bg-slate-900/80 border-b border-slate-800 flex items-center gap-4 text-[11px] text-slate-400 flex-wrap">
          <div className="flex items-center gap-1.5">
            <span>모드</span>
            <select value={mode} onChange={(e) => setMode(e.target.value as any)}
              className="px-2 py-0.5 bg-slate-800 text-white rounded border border-slate-700 text-[11px]">
              <option value="auto">자동</option>
              <option value="law">법률 우선</option>
              <option value="rule">규칙/별표</option>
            </select>
          </div>
          <label className="flex items-center gap-1">
            <input type="checkbox" checked={useLaw} onChange={(e) => setUseLaw(e.target.checked)} className="w-3 h-3" />법률
          </label>
          <label className="flex items-center gap-1">
            <input type="checkbox" checked={useRule} onChange={(e) => setUseRule(e.target.checked)} className="w-3 h-3" />규칙
          </label>
          <div className="flex items-center gap-1.5">
            <span>TopK</span>
            <input type="number" min={1} max={20} value={topk}
              onChange={(e) => setTopk(Math.min(20, Math.max(1, +e.target.value)))}
              className="w-12 px-1.5 py-0.5 bg-slate-800 text-white rounded border border-slate-700 text-[11px]" />
          </div>
        </div>
      )}

      {/* 안내 */}
      <div className="px-4 py-1.5 bg-amber-500/5 border-b border-amber-500/10">
        <p className="text-[10px] text-amber-400/70">
          AI 생성 답변은 참고 정보입니다. 실제 준수는 최신 법령 원문을 확인하세요.
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 space-y-4 overflow-y-auto">
        {messages.map((msg, i) => (
          <ChatMessage key={i} sender={msg.sender} text={msg.text}>
            {msg.sender === "bot" && msg.hits && msg.hits.length > 0 && (
              <div className="mt-2">
                <EvidenceToggle hits={msg.hits} />
              </div>
            )}
          </ChatMessage>
        ))}
        {loading && <TypingDots />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  );
}
