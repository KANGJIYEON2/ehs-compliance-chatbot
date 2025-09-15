import { ExternalLink } from "lucide-react";

export type Hit = {
  law_name: string;
  article_id: string;
  content: string;
  distance: number;
  label?: string;
  image_url?: string;
};

type Props = {
  hit: Hit;
  apiBase: string;
};

export default function HitCard({ hit, apiBase }: Props) {
  const title = hit.label || `[${hit.law_name}] ${hit.article_id}`;
  const hasImg = !!hit.image_url;
  const imgSrc = hasImg
    ? hit.image_url!.startsWith("http")
      ? hit.image_url!
      : apiBase.replace(/\/$/, "") + hit.image_url!
    : undefined;

  return (
    <div className="group rounded-xl border bg-white shadow hover:shadow-md transition overflow-hidden">
      {hasImg && (
        <a
          href={imgSrc}
          target="_blank"
          rel="noreferrer"
          className="block aspect-[4/3] overflow-hidden bg-slate-100"
          title="이미지 열기"
        >
          {/* 이미지 비율 유지를 위해 object-cover */}
          <img
            src={imgSrc}
            alt={title}
            className="w-full h-full object-cover group-hover:opacity-95"
            loading="lazy"
          />
        </a>
      )}

      <div className="p-3">
        <div className="text-xs font-semibold text-slate-700 line-clamp-1">
          {title}
        </div>
        <div className="mt-1 text-xs text-slate-500 line-clamp-3 whitespace-pre-wrap">
          {hit.content?.slice(0, 400) || ""}
        </div>

        <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
          <span>L2 {hit.distance.toFixed(4)}</span>
          {hasImg && (
            <a
              href={imgSrc}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 hover:text-slate-600"
              title="원본 이미지 열기"
            >
              <ExternalLink size={14} />
              열기
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
