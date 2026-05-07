import { createBrowserRouter } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import LandingPage from "./pages/LandingPage";
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
import QuizPage from "./pages/QuizPage";
import RankingPage from "./pages/RankingPage";
import RiskScoresPage from "./pages/RiskScoresPage";
import SafetyGuidePage from "./pages/SafetyGuidePage";
import TBMPage from "./pages/TBMPage";
import RiskAssessmentPage from "./pages/RiskAssessmentPage";

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  { path: "/login", element: <LoginPage /> },
  { path: "/signup", element: <SignupPage /> },
  {
    path: "/dashboard",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "incidents", element: <IncidentListPage /> },
      { path: "incidents/new", element: <IncidentFormPage /> },
      { path: "incidents/:id", element: <IncidentDetailPage /> },
      { path: "voice", element: <VoiceReportPage /> },
      { path: "reports", element: <AnonymousReportsPage /> },
      { path: "news", element: <SafetyNewsPage /> },
      { path: "quiz", element: <QuizPage /> },
      { path: "ranking", element: <RankingPage /> },
      { path: "risk", element: <RiskScoresPage /> },
      { path: "tbm", element: <TBMPage /> },
      { path: "risk-assessment", element: <RiskAssessmentPage /> },
      { path: "safety-guide", element: <SafetyGuidePage /> },
      { path: "chat", element: <RagChatPage /> },
      { path: "sites", element: <SitesPage /> },
    ],
  },
]);
