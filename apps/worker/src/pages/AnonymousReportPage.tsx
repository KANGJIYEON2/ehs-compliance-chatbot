import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { MessageSquareWarning, CheckCircle2, Copy } from "lucide-react";

export default function AnonymousReportPage() {
  const [sites, setSites] = useState<{id:string;name:string}[]>([]);
  const [siteId, setSiteId] = useState("");
  const [content, setContent] = useState("");
  const [location, setLocation] = useState("");
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [checkToken, setCheckToken] = useState("");
  const [checkResult, setCheckResult] = useState<any>(null);

  useEffect(() => {
    apiFetch("/api/sites").then(async r => {
      if(r.ok){const d=await r.json();setSites(d);if(d.length===1)setSiteId(d[0].id);}
    });
  },[]);

  const submit = async () => {
    if(!siteId||!content.trim()) return;
    setLoading(true);
    const r = await apiFetch("/api/anonymous-reports",{method:"POST",body:JSON.stringify({
      site_id:siteId, content, location_hint:location||null
    })});
    if(r.ok) setToken((await r.json()).anonymous_token);
    setLoading(false);
  };

  const check = async () => {
    if(!checkToken.trim()) return;
    const r = await apiFetch(`/api/anonymous-reports/check/${checkToken}`);
    if(r.ok) setCheckResult(await r.json());
  };

  if(token) return (
    <div className="space-y-4 text-center py-8">
      <CheckCircle2 size={48} className="text-emerald-400 mx-auto"/>
      <p className="text-white font-medium">제보가 접수되었습니다</p>
      <p className="text-slate-400 text-sm">아래 토큰으로 조치 결과를 확인할 수 있습니다.</p>
      <div className="bg-slate-900 rounded-2xl p-4 border border-slate-800 flex items-center gap-2">
        <code className="text-emerald-400 text-xs flex-1 break-all">{token}</code>
        <button onClick={()=>navigator.clipboard.writeText(token)} className="text-slate-400 hover:text-white shrink-0">
          <Copy size={16}/>
        </button>
      </div>
      <button onClick={()=>{setToken("");setContent("");setLocation("");}}
        className="text-emerald-400 text-sm">새 제보하기</button>
    </div>
  );

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">익명 제보</h1>
      <p className="text-slate-500 text-sm">신원 정보는 일절 저장되지 않습니다.</p>

      <select value={siteId} onChange={e=>setSiteId(e.target.value)}
        className="w-full px-4 py-3 bg-slate-900 text-white rounded-2xl border border-slate-800">
        <option value="">사업장 선택</option>
        {sites.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
      </select>

      <textarea value={content} onChange={e=>setContent(e.target.value)} rows={4}
        className="w-full px-4 py-3 bg-slate-900 text-white rounded-2xl border border-slate-800 resize-none"
        placeholder="위험 상황을 알려주세요"/>

      <input value={location} onChange={e=>setLocation(e.target.value)}
        className="w-full px-4 py-3 bg-slate-900 text-white rounded-2xl border border-slate-800"
        placeholder="위치 (선택사항)"/>

      <button onClick={submit} disabled={loading||!content.trim()||!siteId}
        className="w-full py-3 bg-amber-600 text-white rounded-2xl font-medium disabled:opacity-50 active:scale-95 transition-transform">
        {loading?"제출 중...":"익명 제보하기"}
      </button>

      {/* 조회 */}
      <div className="border-t border-slate-800 pt-4 space-y-3">
        <p className="text-slate-500 text-xs">기존 제보 결과 확인</p>
        <div className="flex gap-2">
          <input value={checkToken} onChange={e=>setCheckToken(e.target.value)}
            className="flex-1 px-3 py-2 bg-slate-900 text-white rounded-xl border border-slate-800 text-sm"
            placeholder="토큰 입력"/>
          <button onClick={check} className="px-4 py-2 bg-slate-800 text-white rounded-xl text-sm">조회</button>
        </div>
        {checkResult&&(
          <div className="bg-slate-900 rounded-xl p-3 border border-slate-800 text-sm space-y-1">
            <p className="text-slate-400">상태: <span className="text-white">{checkResult.status}</span></p>
            <p className="text-slate-400">위험등급: <span className="text-white">{checkResult.risk_level}</span></p>
            {checkResult.admin_response&&<p className="text-emerald-400">응답: {checkResult.admin_response}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
