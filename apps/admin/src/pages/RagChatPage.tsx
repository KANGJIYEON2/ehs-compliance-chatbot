import ChatWindow from "../components/ChatWindow";

export default function RagChatPage() {
  return (
    <div className="h-full">
      <h1 className="text-2xl font-bold text-white mb-4">법령 검색</h1>
      <div className="bg-slate-800 rounded-xl border border-slate-700 h-[calc(100vh-12rem)]">
        <ChatWindow />
      </div>
    </div>
  );
}
