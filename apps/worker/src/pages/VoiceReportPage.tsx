import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { Mic, Square, Loader2, CheckCircle2, AlertTriangle } from "lucide-react";

export default function VoiceReportPage() {
  const navigate = useNavigate();
  const [sites, setSites] = useState<{id:string;name:string}[]>([]);
  const [siteId, setSiteId] = useState("");
  const [recording, setRecording] = useState(false);
  const [step, setStep] = useState<"idle"|"recording"|"processing"|"review"|"done">("idle");
  const [transcript, setTranscript] = useState("");
  const [parsed, setParsed] = useState<any>(null);
  const [error, setError] = useState("");
  const mediaRef = useRef<MediaRecorder|null>(null);
  const chunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    apiFetch("/api/sites").then(async r => {
      if(r.ok){const d=await r.json();setSites(d);if(d.length===1)setSiteId(d[0].id);}
    });
  },[]);

  const startRec = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio:true});
      const rec = new MediaRecorder(stream);
      chunksRef.current = [];
      rec.ondataavailable = e => { if(e.data.size>0) chunksRef.current.push(e.data); };
      rec.onstop = async () => {
        stream.getTracks().forEach(t=>t.stop());
        const blob = new Blob(chunksRef.current, {type:"audio/webm"});
        setStep("processing");
        const fd = new FormData(); fd.append("file",blob,"rec.webm");
        const tr = await apiFetch("/api/voice/transcribe",{method:"POST",body:fd,headers:{}});
        if(!tr.ok){setError("음성 인식 실패");setStep("idle");return;}
        const {text} = await tr.json(); setTranscript(text);
        const pr = await apiFetch(`/api/voice/parse?text=${encodeURIComponent(text)}`,{method:"POST"});
        if(pr.ok){setParsed((await pr.json()).parsed);setStep("review");}
        else{setError("분석 실패");setStep("idle");}
      };
      rec.start(); mediaRef.current=rec; setRecording(true); setStep("recording"); setError("");
    } catch { setError("마이크 접근 거부"); }
  };

  const stopRec = () => { mediaRef.current?.stop(); setRecording(false); };

  const submit = async () => {
    if(!parsed||!siteId) return;
    setStep("processing");
    const r = await apiFetch("/api/voice/submit",{method:"POST",body:JSON.stringify({
      site_id:siteId,incident_type:parsed.incident_type||"other",
      severity:parsed.severity||"near_miss",description:parsed.description||transcript,
      cause_estimate:parsed.cause_estimate
    })});
    if(r.ok){setStep("done");setTimeout(()=>navigate("/"),1500);}
    else{setError("등록 실패");setStep("review");}
  };

  return (
    <div className="space-y-6 text-center">
      <h1 className="text-xl font-bold text-white">음성 보고</h1>

      {step==="idle"&&(
        <>
          <select value={siteId} onChange={e=>setSiteId(e.target.value)}
            className="w-full px-4 py-3 bg-slate-900 text-white rounded-2xl border border-slate-800">
            <option value="">사업장 선택</option>
            {sites.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <button onClick={startRec} disabled={!siteId}
            className="w-28 h-28 mx-auto rounded-full bg-red-600 text-white flex items-center justify-center shadow-lg shadow-red-600/30 active:scale-90 transition-transform disabled:bg-slate-700">
            <Mic size={40}/>
          </button>
          <p className="text-slate-500 text-sm">버튼을 누르고 말하세요</p>
        </>
      )}

      {step==="recording"&&(
        <>
          <button onClick={stopRec}
            className="w-28 h-28 mx-auto rounded-full bg-red-600 text-white flex items-center justify-center animate-pulse shadow-lg shadow-red-600/50 active:scale-90 transition-transform">
            <Square size={34}/>
          </button>
          <p className="text-red-400 text-sm animate-pulse">녹음 중...</p>
        </>
      )}

      {step==="processing"&&(
        <div className="py-12"><Loader2 size={40} className="text-emerald-400 animate-spin mx-auto"/><p className="text-slate-400 mt-3">AI 분석 중...</p></div>
      )}

      {step==="review"&&parsed&&(
        <div className="space-y-4 text-left">
          <div className="bg-slate-900 rounded-2xl p-4 border border-slate-800">
            <p className="text-[11px] text-slate-500 mb-1">인식 결과</p>
            <p className="text-white text-sm">{transcript}</p>
          </div>
          <div className="bg-emerald-950/30 rounded-2xl p-4 border border-emerald-800/30 space-y-2">
            <p className="text-emerald-400 text-xs font-medium">AI 자동 분류</p>
            <p className="text-white text-sm">{parsed.description}</p>
            {parsed.cause_estimate&&<p className="text-slate-400 text-xs">원인: {parsed.cause_estimate}</p>}
          </div>
          <div className="flex gap-3">
            <button onClick={submit} className="flex-1 py-3 bg-emerald-600 text-white rounded-2xl font-medium active:scale-95 transition-transform">등록</button>
            <button onClick={()=>{setStep("idle");setParsed(null);}} className="px-6 py-3 bg-slate-800 text-white rounded-2xl active:scale-95 transition-transform">다시</button>
          </div>
        </div>
      )}

      {step==="done"&&(
        <div className="py-12"><CheckCircle2 size={48} className="text-emerald-400 mx-auto"/><p className="text-white mt-3 font-medium">등록 완료!</p></div>
      )}

      {error&&<p className="text-red-400 text-sm flex items-center justify-center gap-1"><AlertTriangle size={14}/>{error}</p>}
    </div>
  );
}
