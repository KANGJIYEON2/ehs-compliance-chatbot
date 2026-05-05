import { createBrowserRouter } from "react-router-dom";
import MobileLayout from "./components/MobileLayout";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import VoiceReportPage from "./pages/VoiceReportPage";
import AnonymousReportPage from "./pages/AnonymousReportPage";
import QuizPage from "./pages/QuizPage";
import MyPage from "./pages/MyPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    path: "/",
    element: <MobileLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "voice", element: <VoiceReportPage /> },
      { path: "report", element: <AnonymousReportPage /> },
      { path: "quiz", element: <QuizPage /> },
      { path: "my", element: <MyPage /> },
    ],
  },
]);
