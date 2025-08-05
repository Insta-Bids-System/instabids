import { Toaster } from "react-hot-toast";
// Docker Live Reload Test - Agent 6
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import HomeownerProjectWorkspace from "@/components/HomeownerProjectWorkspace";
// import { AuthProvider } from "@/contexts/AuthContext";
import { AdminAuthProvider } from "@/hooks/useAdminAuth";
import AuthCallbackPage from "@/pages/AuthCallbackPage";
import AdminDashboardPage from "@/pages/admin/AdminDashboardPage";
import AdminLoginPage from "@/pages/admin/AdminLoginPage";
import BidCardTest from "@/pages/BidCardTest";
import ChatPage from "@/pages/ChatPage";
import CIATestPage from "@/pages/CIATestPage";
import ContractorDashboardPage from "@/pages/ContractorDashboardPage";
import ContractorLandingPage from "@/pages/contractor/ContractorLandingPage";
import DashboardPage from "@/pages/DashboardPage";
import ExternalBidCardDemo from "@/pages/ExternalBidCardDemo";
import ExternalBidCardLanding from "@/pages/ExternalBidCardLanding";
import HomePage from "@/pages/HomePage";
import InspirationDemo from "@/pages/InspirationDemo";
import LoginPage from "@/pages/LoginPage";
import ProjectDetailPage from "@/pages/ProjectDetailPage";
import SignupPage from "@/pages/SignupPage";
import TestPage from "@/pages/TestPage";
import WebRTCTestPage from "@/pages/WebRTCTestPage";
import { MessagingDemo } from "@/test/MessagingDemo";
import { TestMessagingPage } from "@/test/test-messaging-api";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/bid-card-test" element={<BidCardTest />} />
            <Route path="/cia-test" element={<CIATestPage />} />
            <Route path="/test-messaging" element={<TestMessagingPage />} />
            <Route path="/messaging-demo" element={<MessagingDemo />} />
            <Route path="/inspiration-demo" element={<InspirationDemo />} />
            <Route path="/demo/homeowner" element={<InspirationDemo />} />
            <Route path="/demo/homeowner/inspiration" element={<InspirationDemo />} />
            <Route path="/webrtc-test" element={<WebRTCTestPage />} />
            <Route path="/auth/callback" element={<AuthCallbackPage />} />
            <Route path="/external-bid-card-demo" element={<ExternalBidCardDemo />} />
            <Route path="/join" element={<ExternalBidCardLanding />} />
            <Route path="/contractor" element={<ContractorLandingPage />} />
            <Route
              path="/admin/*"
              element={
                <AdminAuthProvider>
                  <Routes>
                    <Route path="login" element={<AdminLoginPage />} />
                    <Route path="dashboard" element={<AdminDashboardPage />} />
                  </Routes>
                </AdminAuthProvider>
              }
            />
            <Route
              path="/dashboard"
              element={<DashboardPage />}
            />
            <Route
              path="/contractor/dashboard"
              element={
                <ProtectedRoute requiredRole="contractor">
                  <ContractorDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat"
              element={
                <ProtectedRoute requiredRole="homeowner">
                  <ChatPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects/:id"
              element={
                <ProtectedRoute requiredRole="homeowner">
                  <ProjectDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bid-cards/:id"
              element={<HomeownerProjectWorkspace />}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster position="top-right" />
        </div>
    </Router>
  );
}

export default App;
