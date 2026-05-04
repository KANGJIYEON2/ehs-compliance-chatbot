import { useEffect, useRef, useState } from "react";
import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";
import TypingDots from "../components/TypingDots";
import EvidenceToggle, { type Hit } from "./EvidenceToggle";
import { RotateCcw } from "lucide-react";

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
  "안녕하세요 👨🏻‍💼 김안전 비서입니다.\nEHS 규제 관련 어떤 도움을 드릴까요?";

type Msg = { sender: "user" | "bot"; text: string; hits?: Hit[] };

export default function ChatWindow() {
  const [messages, setMessages] = useState<Msg[]>([
    { sender: "bot", text: GREETING },
  ]);
  const [loading, setLoading] = useState(false);

  // 컨트롤
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

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || `HTTP ${res.status}`);
      }

      const data: AskResponse = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: data.answer,
          hits: data.hits ?? [],
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            "요청 처리 중 오류가 발생했어요 ⚠️\n" +
            (err?.message || "알 수 없는 오류"),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-full max-w-5xl h-[80vh] bg-white shadow-xl rounded-2xl overflow-hidden border border-slate-200">
      {/* 상단 툴바 */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-white">
        <div className="flex items-center gap-3 text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <span className="text-slate-500">모드</span>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as any)}
              className="px-2 py-1 border rounded-md text-sm"
            >
              <option value="auto">자동</option>
              <option value="law">법률 우선</option>
              <option value="rule">규칙/별표 우선</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={useLaw}
                onChange={(e) => setUseLaw(e.target.checked)}
              />
              <span>법률DB</span>
            </label>
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={useRule}
                onChange={(e) => setUseRule(e.target.checked)}
              />
              <span>규칙DB</span>
            </label>
          </div>

          <div className="flex items-center gap-2">
            <span>TopK</span>
            <input
              type="number"
              min={1}
              max={20}
              value={topk}
              onChange={(e) =>
                setTopk(Math.min(20, Math.max(1, Number(e.target.value))))
              }
              className="w-16 px-2 py-1 border rounded-md text-sm"
            />
          </div>

          <div className="flex items-center gap-2">
            <span>컨텍스트</span>
            <input
              type="number"
              min={1000}
              max={20000}
              step={500}
              value={ctxChars}
              onChange={(e) =>
                setCtxChars(
                  Math.min(20000, Math.max(1000, Number(e.target.value)))
                )
              }
              className="w-24 px-2 py-1 border rounded-md text-sm"
            />
          </div>
        </div>

        <button
          onClick={handleReset}
          className="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm bg-slate-800 text-white hover:bg-slate-700 transition shadow"
          title="대화 모두 지우기"
        >
          <RotateCcw size={16} /> Reset
        </button>
      </div>

      {/* 안내 배너 */}
      <div className="px-4 py-2 bg-amber-50 text-amber-800 text-xs border-b border-amber-200">
        ⚠️ 안내: 본 답변은 생성형 AI가 제공하는 <b>참고 정보</b>입니다. 실제
        준수·해석은
        <b> 최신 법령·고시 원문</b>과 관할기관 안내를 반드시 확인해 주세요.
      </div>

      {/* Messages */}
      <div className="flex-1 p-6 space-y-5 overflow-y-auto bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200">
        {messages.map((msg, i) => (
          <ChatMessage key={i} sender={msg.sender} text={msg.text}>
            {/* 근거자료: 기본 접힘(토글 컴포넌트) */}
            {msg.sender === "bot" && msg.hits && msg.hits.length > 0 && (
              <div className="ml-12 mt-1">
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
