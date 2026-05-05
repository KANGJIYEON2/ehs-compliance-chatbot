import { Outlet, Navigate } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import BottomNav from "./BottomNav";

export default function MobileLayout() {
  const accessToken = useAuthStore((s) => s.accessToken);

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <main className="pb-20 max-w-lg mx-auto px-4 pt-4">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
