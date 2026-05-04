import { Outlet, Navigate } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import Sidebar from "./Sidebar";

export default function AppLayout() {
  const accessToken = useAuthStore((s) => s.accessToken);

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex h-screen bg-slate-900">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
