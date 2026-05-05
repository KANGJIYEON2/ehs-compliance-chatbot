import { useState, useEffect } from "react";
import { apiFetch, API_BASE } from "../lib/api";
import { BookOpen, Plus, Globe, QrCode, Loader2 } from "lucide-react";

interface Site { id: string; name: string; }
interface Guide {
  id: string;
  target_type: string;
  target_name: string;
  content_ko: string;
  languages: string[];
}

const LANG_LABELS: Record<string, string> = {
  ko: "한국어", vi: "베트남어", en: "영어", km: "캄보디아어", ne: "네팔어", my: "미얀마어",
};
const TRANSLATE_LANGS = ["vi", "en", "km", "ne", "my"];

export default function SafetyGuidePage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [siteId, setSiteId] = useState("");
  const [guides, setGuides] = useState<Guide[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ target_type: "equipment", target_id: "", target_name: "", content_ko: "" });
  const [translating, setTranslating] = useState<string | null>(null);

  useEffect(() => {
    apiFetch("/api/sites").then(async (res) => {
      if (res.ok) {
        const data = await res.json();
        setSites(data);
        if (data.length > 0) setSiteId(data[0].id);
      }
    });
  }, []);

  const fetchGuides = async () => {
    if (!siteId) return;
    setLoading(true);
    const res = await apiFetch(`/api/safety-guide/list?site_id=${siteId}`);
    if (res.ok) setGuides(await res.json());
    setLoading(false);
  };

  useEffect(() => { fetchGuides(); }, [siteId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await apiFetch("/api/safety-guide", {
      method: "POST",
      body: JSON.stringify({ ...form, site_id: siteId, target_id: form.target_name }),
    });
    if (res.ok) {
      setForm({ target_type: "equipment", target_id: "", target_name: "", content_ko: "" });
      setShowForm(false);
      fetchGuides();
    }
  };

  const handleTranslate = async (guideId: string, lang: string) => {
    setTranslating(`${guideId}-${lang}`);
    await apiFetch(`/api/safety-guide/${guideId}/translate?lang=${lang}`, { method: "POST" });
    await fetchGuides();
    setTranslating(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BookOpen className="text-blue-400" size={24} />
          <h1 className="text-2xl font-bold text-white">다국어 안전 안내</h1>
        </div>
        <button onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm transition-colors">
          <Plus size={16} /> 안전수칙 등록
        </button>
      </div>

      {/* 사업장 선택 */}
      <select value={siteId} onChange={(e) => setSiteId(e.target.value)}
        className="px-3 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 text-sm">
        {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
      </select>

      {/* 등록 폼 */}
      {showForm && (
        <form onSubmit={handleCreate} className="bg-slate-800 rounded-xl p-6 border border-slate-700 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-slate-300 mb-1">대상 유형</label>
              <select value={form.target_type} onChange={(e) => setForm({ ...form, target_type: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600">
                <option value="equipment">장비</option>
                <option value="work_zone">작업구역</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-300 mb-1">대상 이름</label>
              <input value={form.target_name} onChange={(e) => setForm({ ...form, target_name: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600" required placeholder="예: 프레스기 #1" />
            </div>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1">안전수칙 (한국어)</label>
            <textarea value={form.content_ko} onChange={(e) => setForm({ ...form, content_ko: e.target.value })}
              rows={4} className="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 resize-none" required
              placeholder="1. 작업 전 방호장치 작동 확인&#10;2. 비상정지 버튼 위치 숙지&#10;3. 개인보호구 착용 필수" />
          </div>
          <button type="submit" className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm transition-colors">등록</button>
        </form>
      )}

      {/* 가이드 목록 */}
      {loading ? (
        <p className="text-slate-400">로딩 중...</p>
      ) : guides.length === 0 ? (
        <div className="bg-slate-800 rounded-xl p-12 border border-slate-700 text-center">
          <BookOpen className="mx-auto text-slate-500 mb-3" size={40} />
          <p className="text-slate-400">등록된 안전수칙이 없습니다.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {guides.map((g) => (
            <div key={g.id} className="bg-slate-800 rounded-xl p-5 border border-slate-700 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-white font-medium">{g.target_name}</span>
                  <span className="text-xs text-slate-500 ml-2">{g.target_type === "equipment" ? "장비" : "작업구역"}</span>
                </div>
                <a href={`${API_BASE}/api/safety-guide/qr/${g.id}?base_url=${window.location.origin}`}
                  target="_blank" rel="noopener noreferrer"
                  className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors">
                  <QrCode size={14} /> QR
                </a>
              </div>

              <p className="text-slate-300 text-sm whitespace-pre-wrap">{g.content_ko}</p>

              {/* 번역 버튼 */}
              <div className="flex items-center gap-2 flex-wrap">
                <Globe size={14} className="text-blue-400" />
                {TRANSLATE_LANGS.map((lang) => {
                  const done = g.languages.includes(lang);
                  const isLoading = translating === `${g.id}-${lang}`;
                  return (
                    <button key={lang} onClick={() => !done && handleTranslate(g.id, lang)} disabled={done || isLoading}
                      className={`px-2 py-0.5 rounded text-xs transition-colors ${
                        done ? "bg-emerald-600/20 text-emerald-400" : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                      }`}>
                      {isLoading ? <Loader2 size={12} className="animate-spin inline" /> : LANG_LABELS[lang]}
                      {done && " ✓"}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
