import { createBrowserRouter } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DashboardPage from "./pages/DashboardPage";
import RagChatPage from "./pages/RagChatPage";
import SitesPage from "./pages/SitesPage";
import IncidentListPage from "./pages/IncidentListPage";
import IncidentFormPage from "./pages/IncidentFormPage";
import IncidentDetailPage from "./pages/IncidentDetailPage";
import SafetyNewsPage from "./pages/SafetyNewsPage";
import AnonymousReportsPage from "./pages/AnonymousReportsPage";
import VoiceReportPage from "./pages/VoiceReportPage";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/signup",
    element: <SignupPage />,
  },
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "chat", element: <RagChatPage /> },
      { path: "sites", element: <SitesPage /> },
      { path: "incidents", element: <IncidentListPage /> },
      { path: "incidents/new", element: <IncidentFormPage /> },
      { path: "incidents/:id", element: <IncidentDetailPage /> },
      { path: "news", element: <SafetyNewsPage /> },
      { path: "reports", element: <AnonymousReportsPage /> },
      { path: "voice", element: <VoiceReportPage /> },
    ],
  },
]);
