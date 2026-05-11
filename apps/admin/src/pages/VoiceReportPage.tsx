import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { Mic, Square, Loader2, CheckCircle2, AlertTriangle } from "lucide-react";

interface ParsedReport {
  incident_type?: string;
  severity?: string;
  description?: string;
  cause_estimate?: string;
  location_hint?: string;
  urgency?: string;
}

const TYPE_LABELS: Record<string, string> = {
  caught: "끼임", fall: "추락", collision: "충돌", electric: "감전",
  fire: "화재", suffocation: "질식", falling_object: "낙하물",
  chemical: "화학물질", other: "기타",
};
const SEVERITY_LABELS: Record<string, string> = {
  death: "사망", serious: "중상", minor: "경상", near_miss: "아차사고",
};

interface Site { id: string; name: string; }

export default function VoiceReportPage() {
  const navigate = useNavigate();
  const [sites, setSites] = useState<Site[]>([]);
  const [siteId, setSiteId] = useState("");

  // 녹음 상태
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // 처리 단계
  const [step, setStep] = useState<"idle" | "recording" | "transcribing" | "parsing" | "review" | "submitting" | "done">("idle");
  const [transcript, setTranscript] = useState("");
  const [parsed, setParsed] = useState<ParsedReport | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/api/sites").then(async (res) => {
      if (res.ok) {
        const data = await res.json();
        setSites(data);
        if (data.length === 1) setSiteId(data[0].id);
      }
    });
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setAudioBlob(blob);
        stream.getTracks().forEach((t) => t.stop());
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setRecording(true);
      setStep("recording");
      setError("");
    } catch {
      setError("마이크 접근이 거부되었습니다.");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  // 녹음 완료 → 자동 전사
  useEffect(() => {
    if (audioBlob && step === "recording") {
      processAudio(audioBlob);
    }
  }, [audioBlob]);

  const processAudio = async (blob: Blob) => {
    setStep("transcribing");

    // 1. Whisper 전사
    const formData = new FormData();
    formData.append("file", blob, "recording.webm");
    const transRes = await apiFetch("/api/voice/transcribe", {
      method: "POST",
      body: formData,
      headers: {},
    });

    if (!transRes.ok) {
      setError("음성 인식에 실패했습니다.");
      setStep("idle");
      return;
    }

    const { text } = await transRes.json();
    setTranscript(text);
    setStep("parsing");

    // 2. GPT 파싱
    const parseRes = await apiFetch(`/api/voice/parse?text=${encodeURIComponent(text)}`, {
      method: "POST",
    });

    if (parseRes.ok) {
      const { parsed: p } = await parseRes.json();
      setParsed(p);
      setStep("review");
    } else {
      setError("내용 분석에 실패했습니다.");
      setStep("idle");
    }
  };

  const handleSubmit = async () => {
    if (!parsed || !siteId) return;
    setStep("submitting");

    const res = await apiFetch("/api/voice/submit", {
      method: "POST",
      body: JSON.stringify({
        site_id: siteId,
        incident_type: parsed.incident_type || "other",
        severity: parsed.severity || "near_miss",
        description: parsed.description || transcript,
        cause_estimate: parsed.cause_estimate,
      }),
    });

    if (res.ok) {
      const { incident_id } = await res.json();
      setStep("done");
      setTimeout(() => navigate(`/dashboard/incidents/${incident_id}`), 1500);
    } else {
      setError("등록에 실패했습니다.");
      setStep("review");
    }
  };

  const reset = () => {
    setStep("idle");
    setAudioBlob(null);
    setTranscript("");
    setParsed(null);
    setError("");
  };

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-white text-center">음성 보고</h1>
      <p className="text-slate-400 text-sm text-center">마이크 버튼을 누르고 상황을 말씀하세요. AI가 자동으로 사고 보고서를 작성합니다.</p>

      {/* 사업장 선택 */}
      {step === "idle" && (
        <div>
          <label className="block text-sm text-slate-300 mb-1">사업장</label>
          <select value={siteId} onChange={(e) => setSiteId(e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700">
            <option value="">선택</option>
            {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
      )}

      {/* 녹음 버튼 */}
      {(step === "idle" || step === "recording") && (
        <div className="flex justify-center py-8">
          {!recording ? (
            <button onClick={startRecording} disabled={!siteId}
              className="w-24 h-24 rounded-full bg-red-600 hover:bg-red-700 disabled:bg-slate-600 text-white flex items-center justify-center transition-colors shadow-lg shadow-red-600/30">
              <Mic size={36} />
            </button>
          ) : (
            <button onClick={stopRecording}
              className="w-24 h-24 rounded-full bg-red-600 text-white flex items-center justify-center animate-pulse shadow-lg shadow-red-600/50">
              <Square size={30} />
            </button>
          )}
        </div>
      )}

      {recording && (
        <p className="text-red-400 text-sm text-center animate-pulse">녹음 중... 완료되면 정지 버튼을 누르세요</p>
      )}

      {/* 처리 중 */}
      {(step === "transcribing" || step === "parsing") && (
        <div className="flex flex-col items-center py-8 gap-3">
          <Loader2 size={40} className="text-emerald-400 animate-spin" />
          <p className="text-slate-300">
            {step === "transcribing" ? "음성을 인식하고 있습니다..." : "AI가 내용을 분석하고 있습니다..."}
          </p>
        </div>
      )}

      {/* 리뷰 */}
      {step === "review" && parsed && (
        <div className="space-y-4">
          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <p className="text-xs text-slate-400 mb-1">음성 인식 결과</p>
            <p className="text-white text-sm">{transcript}</p>
          </div>

          <div className="bg-slate-800 rounded-xl p-5 border border-emerald-600/30 space-y-3">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={16} className="text-emerald-400" />
              <span className="text-sm font-medium text-emerald-400">AI 자동 분류 결과</span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-xs text-slate-400">사고 유형</span>
                <p className="text-white">{TYPE_LABELS[parsed.incident_type || ""] || parsed.incident_type || "-"}</p>
              </div>
              <div>
                <span className="text-xs text-slate-400">심각도</span>
                <p className="text-white">{SEVERITY_LABELS[parsed.severity || ""] || parsed.severity || "-"}</p>
              </div>
            </div>
            <div>
              <span className="text-xs text-slate-400">설명</span>
              <p className="text-white text-sm">{parsed.description || "-"}</p>
            </div>
            {parsed.cause_estimate && (
              <div>
                <span className="text-xs text-slate-400">추정 원인</span>
                <p className="text-white text-sm">{parsed.cause_estimate}</p>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            <button onClick={handleSubmit}
              className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium transition-colors">
              이대로 등록
            </button>
            <button onClick={reset}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors">
              다시 녹음
            </button>
          </div>
        </div>
      )}

      {/* 등록 중 */}
      {step === "submitting" && (
        <div className="flex flex-col items-center py-8 gap-3">
          <Loader2 size={40} className="text-emerald-400 animate-spin" />
          <p className="text-slate-300">사고를 등록하고 있습니다...</p>
        </div>
      )}

      {/* 완료 */}
      {step === "done" && (
        <div className="flex flex-col items-center py-8 gap-3">
          <CheckCircle2 size={48} className="text-emerald-400" />
          <p className="text-white font-medium">사고가 등록되었습니다</p>
          <p className="text-slate-400 text-sm">상세 페이지로 이동합니다...</p>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm justify-center">
          <AlertTriangle size={14} />{error}
        </div>
      )}
    </div>
  );
}
