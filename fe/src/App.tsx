import "./App.css";
import ChatWindow from "./components/ChatWindow";

function App() {
  return (
    <div className="h-screen w-full flex flex-col bg-slate-50">
      <header className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white shadow">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500 flex items-center justify-center text-xl">
            👨🏻‍💼
          </div>
          <div>
            <h1 className="text-lg font-semibold">김안전 비서</h1>
            <p className="text-xs text-slate-300">
              AI EHS 규제 컴플라이언스 챗봇
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm bg-emerald-600/20 text-emerald-400 px-3 py-1 rounded-xl">
            Beta
          </span>
          <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
            🧑‍💻
          </div>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-6">
        <ChatWindow />
      </main>
    </div>
  );
}

export default App;
