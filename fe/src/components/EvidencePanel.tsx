import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export type Hit = {
  law_name: string;
  article_id: string;
  content: string;
  distance: number;
  label?: string;
  image_url?: string;
  content_format?: string; // "markdown" for tables
};

type Props = {
  apiBase: string; // ex) http://127.0.0.1:8000
  hits: Hit[];
};

function absolutize(apiBase: string, url?: string) {
  if (!url) return undefined;
  try {
    // 이미 절대 URL이면 그대로
    if (/^https?:\/\//i.test(url)) return url;
    // /static/... 같은 루트 상대경로면 API_BASE 기준으로
    if (url.startsWith("/")) return new URL(url, apiBase).toString();
    // 그 외는 그냥 붙이기
    return `${apiBase.replace(/\/+$/, "")}/${url.replace(/^\/+/, "")}`;
  } catch {
    return url;
  }
}

export default function EvidencePanel({ apiBase, hits }: Props) {
  const [open, setOpen] = useState(true); // 기본 ON(토글 가능)

  const normalized = useMemo(() => {
    return hits.map((h) => ({
      ...h,
      _image_abs: absolutize(apiBase, h.image_url),
    }));
  }, [apiBase, hits]);

  if (!normalized?.length) return null;

  return (
    <div className="w-full">
      {/* 토글 버튼 */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs bg-slate-200 text-slate-700 hover:bg-slate-300 transition"
      >
        {open ? "근거 닫기 ▲" : "근거 보기 ▼"}
      </button>

      {!open ? null : (
        <div className="mt-3 space-y-3">
          {normalized.map((h, i) => (
            <div
              key={i}
              className="w-full rounded-xl border border-slate-200 bg-white shadow-sm p-3"
            >
              {/* 제목/라벨 */}
              <div className="text-xs font-semibold text-slate-700 mb-2">
                {h.label ? h.label : `[${h.law_name}] ${h.article_id}`}
                <span className="ml-2 text-[11px] text-slate-400">
                  L2={h.distance.toFixed(4)}
                </span>
              </div>

              {/* 이미지 미리보기 (있을 때만) */}
              {h._image_abs && (
                <div className="mb-2">
                  <img
                    src={h._image_abs}
                    alt={h.label || h.article_id || "annex image"}
                    className="w-full max-h-[480px] object-contain rounded-lg border"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                  <div className="text-[11px] text-slate-400 mt-1 break-all">
                    {h.image_url}
                  </div>
                </div>
              )}

              {/* 표(마크다운) | 일반 텍스트 */}
              {h.content_format === "markdown" ? (
                <div className="overflow-x-auto rounded-md border bg-slate-50 p-2">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: (props) => (
                        <table {...props} className="w-full text-xs" />
                      ),
                      th: (props) => (
                        <th
                          {...props}
                          className="border px-2 py-1 bg-slate-100 text-left"
                        />
                      ),
                      td: (props) => (
                        <td {...props} className="border px-2 py-1 align-top" />
                      ),
                    }}
                  >
                    {h.content || ""}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="text-xs text-slate-700 whitespace-pre-wrap">
                  {(h.content || "").trim().slice(0, 1200)}
                  {(h.content || "").length > 1200 ? " …" : ""}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
