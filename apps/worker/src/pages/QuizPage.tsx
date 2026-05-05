import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { HelpCircle, CheckCircle2, XCircle, Loader2, Trophy } from "lucide-react";

export default function QuizPage() {
  const [quiz, setQuiz] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<number|null>(null);
  const [result, setResult] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    apiFetch("/api/gamification/quiz/today").then(async r => {
      if(r.ok){const d=await r.json();setQuiz(d.quiz);}
      setLoading(false);
    });
  },[]);

  const answer = async () => {
    if(selected===null||!quiz) return;
    setSubmitting(true);
    const r = await apiFetch(`/api/gamification/quiz/${quiz.id}/answer`,{
      method:"POST",body:JSON.stringify({selected_index:selected})
    });
    if(r.ok) setResult(await r.json());
    setSubmitting(false);
  };

  if(loading) return <p className="text-slate-400 text-center py-12">퀴즈 로딩...</p>;
  if(!quiz) return (
    <div className="text-center py-12">
      <HelpCircle size={40} className="text-slate-600 mx-auto mb-3"/>
      <p className="text-slate-400">오늘의 퀴즈가 없습니다</p>
    </div>
  );
  if(quiz.already_answered&&!result) return (
    <div className="text-center py-12">
      <CheckCircle2 size={40} className="text-emerald-400 mx-auto mb-3"/>
      <p className="text-white font-medium">오늘 퀴즈 완료!</p>
      <p className="text-slate-500 text-sm mt-1">내일 새 퀴즈가 나옵니다</p>
    </div>
  );

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-white">안전 퀴즈</h1>
      <div className="bg-slate-900 rounded-2xl p-5 border border-slate-800">
        <p className="text-white leading-relaxed">{quiz.question}</p>
      </div>

      <div className="space-y-2">
        {quiz.options.map((opt:string,i:number) => {
          let style = "bg-slate-900 border-slate-800";
          if(result){
            if(i===result.correct_index) style="bg-emerald-900/30 border-emerald-600";
            else if(i===selected) style="bg-red-900/30 border-red-600";
            else style="bg-slate-900 border-slate-800 opacity-40";
          } else if(i===selected) style="bg-slate-800 border-emerald-500";

          return (
            <button key={i} onClick={()=>!result&&setSelected(i)} disabled={!!result}
              className={`w-full text-left p-4 rounded-2xl border transition-all flex items-center gap-3 active:scale-[0.98] ${style}`}>
              <span className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-xs text-white shrink-0">
                {String.fromCharCode(65+i)}
              </span>
              <span className="text-white text-sm flex-1">{opt}</span>
              {result&&i===result.correct_index&&<CheckCircle2 size={18} className="text-emerald-400"/>}
              {result&&i===selected&&i!==result.correct_index&&<XCircle size={18} className="text-red-400"/>}
            </button>
          );
        })}
      </div>

      {!result?(
        <button onClick={answer} disabled={selected===null||submitting}
          className="w-full py-3 bg-emerald-600 text-white rounded-2xl font-medium disabled:opacity-50 active:scale-95 transition-transform">
          {submitting?<Loader2 size={18} className="animate-spin mx-auto"/>:"정답 확인"}
        </button>
      ):(
        <div className={`rounded-2xl p-4 border ${result.is_correct?"bg-emerald-900/20 border-emerald-700/30":"bg-red-900/20 border-red-700/30"}`}>
          <div className="flex items-center gap-2 mb-1">
            {result.is_correct?<><Trophy size={18} className="text-amber-400"/><span className="text-emerald-400 font-medium">정답! +{result.points_earned}점</span></>
            :<><XCircle size={18} className="text-red-400"/><span className="text-red-400 font-medium">오답</span></>}
          </div>
          {result.explanation&&<p className="text-slate-300 text-sm">{result.explanation}</p>}
        </div>
      )}
    </div>
  );
}
