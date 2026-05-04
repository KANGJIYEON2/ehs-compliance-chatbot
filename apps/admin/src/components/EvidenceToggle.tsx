import { useState } from "react";
import { ChevronDown, ChevronRight, ImageOff } from "lucide-react";

export type Hit = {
  law_name: string;
  article_id: string;
  content: string;
  distance: number;
  label?: string;
  image_url?: string;
  content_format?: "markdown" | string;
};

type Props = {
  hits: Hit[];
};

export default function EvidenceToggle({ hits }: Props) {
  const [open, setOpen] = useState(false);

  if (!hits || hits.length === 0) return null;

  return (
    <div className="w-full">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="group inline-flex items-center gap-2 text-xs px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
        title="근거자료 펼치기/접기"
      >
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <span className="font-medium">근거자료</span>
        <span className="text-slate-500">({hits.length}건)</span>
      </button>

      {open && (
        <div className="mt-3 space-y-3">
          {hits.map((h, i) => (
            <div
              key={i}
              className="w-full rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden"
            >
              <div className="px-4 py-2 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
                <div className="text-xs text-slate-700">
                  <span className="font-semibold">
                    {h.label ?? `${h.law_name} · ${h.article_id}`}
                  </span>
                </div>
                <div className="text-[11px] text-slate-500">
                  L2={h.distance.toFixed(4)}
                </div>
              </div>

              {/* 본문/표/이미지 */}
              <div className="p-4 space-y-3">
                {/* 텍스트/표 (간단히 프리뷰) */}
                {h.content && (
                  <div className="text-xs leading-relaxed">
                    {h.content_format === "markdown" ? (
                      // 라이브러리 없이 일단 프리 렌더(표도 줄바꿈 손실 없이 보여줌)
                      <pre className="text-xs whitespace-pre-wrap overflow-x-auto font-mono bg-slate-50 p-3 rounded-md border border-slate-200">
                        {h.content}
                      </pre>
                    ) : (
                      <pre className="text-xs whitespace-pre-wrap">
                        {h.content}
                      </pre>
                    )}
                  </div>
                )}

                {/* 이미지(있으면) */}
                {h.image_url ? (
                  <div className="w-full">
                    <img
                      src={h.image_url}
                      alt={h.label ?? "annex image"}
                      className="w-full max-h-[520px] object-contain rounded-md border border-slate-200"
                      loading="lazy"
                    />
                  </div>
                ) : (
                  <div className="text-[11px] text-slate-400 inline-flex items-center gap-1">
                    <ImageOff size={14} />
                    이미지는 제공되지 않았습니다.
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
