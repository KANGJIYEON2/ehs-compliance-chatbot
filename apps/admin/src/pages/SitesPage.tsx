import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { Plus, Trash2 } from "lucide-react";

interface Site {
  id: string;
  name: string;
  address: string | null;
  company_id: string;
}

export default function SitesPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");

  const fetchSites = async () => {
    const res = await apiFetch("/api/sites");
    if (res.ok) setSites(await res.json());
    setLoading(false);
  };

  useEffect(() => {
    fetchSites();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await apiFetch("/api/sites", {
      method: "POST",
      body: JSON.stringify({ name, address: address || null }),
    });
    if (res.ok) {
      setName("");
      setAddress("");
      setShowForm(false);
      fetchSites();
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("정말 삭제하시겠습니까?")) return;
    const res = await apiFetch(`/api/sites/${id}`, { method: "DELETE" });
    if (res.ok) fetchSites();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">사업장 관리</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm transition-colors"
        >
          <Plus size={16} />
          사업장 추가
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="bg-slate-800 rounded-xl p-6 border border-slate-700 space-y-4"
        >
          <div>
            <label className="block text-sm text-slate-300 mb-1">
              사업장명 *
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:border-emerald-500 focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1">주소</label>
            <input
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm transition-colors"
          >
            등록
          </button>
        </form>
      )}

      {loading ? (
        <p className="text-slate-400">로딩 중...</p>
      ) : sites.length === 0 ? (
        <div className="bg-slate-800 rounded-xl p-8 border border-slate-700 text-center">
          <p className="text-slate-400">
            등록된 사업장이 없습니다. 위 버튼으로 사업장을 추가하세요.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {sites.map((site) => (
            <div
              key={site.id}
              className="bg-slate-800 rounded-xl p-4 border border-slate-700 flex items-center justify-between"
            >
              <div>
                <p className="text-white font-medium">{site.name}</p>
                {site.address && (
                  <p className="text-slate-400 text-sm mt-1">{site.address}</p>
                )}
              </div>
              <button
                onClick={() => handleDelete(site.id)}
                className="p-2 text-slate-400 hover:text-red-400 transition-colors"
                title="삭제"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
