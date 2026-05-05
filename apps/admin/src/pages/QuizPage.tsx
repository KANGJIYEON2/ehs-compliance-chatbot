import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { HelpCircle, CheckCircle2, XCircle, Loader2, Trophy } from "lucide-react";

interface Quiz {
  id: string;
  question: string;
  options: string[];
  already_answered: boolean;
  correct_index: number | null;
  explanation: string | null;
}

export default function QuizPage() {
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<number | null>(null);
  const [result, setResult] = useState<{
    is_correct: boolean;
    correct_index: number;
    explanation: string | null;
    points_earned: number;
  } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    apiFetch("/api/gamification/quiz/today").then(async (res) => {
      if (res.ok) {
        const data = await res.json();
        setQuiz(data.quiz);
      }
      setLoading(false);
    });
  }, []);

  const handleAnswer = async () => {
    if (selected === null || !quiz) return;
    setSubmitting(true);
    const res = await apiFetch(`/api/gamification/quiz/${quiz.id}/answer`, {
      method: "POST",
      body: JSON.stringify({ selected_index: selected }),
    });
    if (res.ok) {
      setResult(await res.json());
    }
    setSubmitting(false);
  };

  if (loading) return <p className="text-slate-400 p-6">퀴즈 로딩 중...</p>;

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <HelpCircle className="text-amber-400" size={24} />
        <h1 className="text-2xl font-bold text-white">오늘의 안전 퀴즈</h1>
      </div>

      {!quiz ? (
        <div className="bg-slate-800 rounded-xl p-12 border border-slate-700 text-center">
          <HelpCircle className="mx-auto text-slate-500 mb-3" size={40} />
          <p className="text-slate-400">오늘의 퀴즈를 준비할 수 없습니다.</p>
        </div>
      ) : quiz.already_answered && !result ? (
        <div className="bg-slate-800 rounded-xl p-8 border border-emerald-600/30 text-center space-y-3">
          <CheckCircle2 className="mx-auto text-emerald-400" size={40} />
          <p className="text-white font-medium">오늘의 퀴즈를 이미 풀었습니다!</p>
          <p className="text-slate-400 text-sm">내일 새로운 퀴즈가 생성됩니다.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* 문제 */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <p className="text-white text-lg font-medium leading-relaxed">{quiz.question}</p>
          </div>

          {/* 선택지 */}
          <div className="space-y-2">
            {quiz.options.map((opt, i) => {
              let style = "bg-slate-800 border-slate-700 hover:border-slate-500";
              if (result) {
                if (i === result.correct_index) style = "bg-emerald-900/30 border-emerald-500";
                else if (i === selected) style = "bg-red-900/30 border-red-500";
                else style = "bg-slate-800 border-slate-700 opacity-50";
              } else if (i === selected) {
                style = "bg-slate-700 border-emerald-500";
              }

              return (
                <button
                  key={i}
                  onClick={() => !result && setSelected(i)}
                  disabled={!!result}
                  className={`w-full text-left p-4 rounded-xl border transition-colors flex items-center gap-3 ${style}`}
                >
                  <span className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm text-white shrink-0">
                    {String.fromCharCode(65 + i)}
                  </span>
                  <span className="text-white text-sm">{opt}</span>
                  {result && i === result.correct_index && <CheckCircle2 size={18} className="ml-auto text-emerald-400" />}
                  {result && i === selected && i !== result.correct_index && <XCircle size={18} className="ml-auto text-red-400" />}
                </button>
              );
            })}
          </div>

          {/* 제출 or 결과 */}
          {!result ? (
            <button
              onClick={handleAnswer}
              disabled={selected === null || submitting}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-medium disabled:opacity-50 transition-colors"
            >
              {submitting ? <Loader2 size={18} className="animate-spin mx-auto" /> : "정답 확인"}
            </button>
          ) : (
            <div className={`rounded-xl p-5 border ${result.is_correct ? "bg-emerald-900/20 border-emerald-600/30" : "bg-red-900/20 border-red-600/30"}`}>
              <div className="flex items-center gap-2 mb-2">
                {result.is_correct ? (
                  <>
                    <Trophy size={18} className="text-amber-400" />
                    <span className="text-emerald-400 font-medium">정답! +{result.points_earned}점</span>
                  </>
                ) : (
                  <>
                    <XCircle size={18} className="text-red-400" />
                    <span className="text-red-400 font-medium">오답</span>
                  </>
                )}
              </div>
              {result.explanation && (
                <p className="text-slate-300 text-sm">{result.explanation}</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
