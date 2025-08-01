import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/contexts/AuthContext'
import HomePage from '@/pages/HomePage'
import LoginPage from '@/pages/LoginPage'
import SignupPage from '@/pages/SignupPage'
import DashboardPage from '@/pages/DashboardPage'
import ContractorDashboardPage from '@/pages/ContractorDashboardPage'
import ChatPage from '@/pages/ChatPage'
import TestPage from '@/pages/TestPage'
import WebRTCTestPage from '@/pages/WebRTCTestPage'
import AuthCallbackPage from '@/pages/AuthCallbackPage'
import ProjectDetailPage from '@/pages/ProjectDetailPage'
import HomeownerProjectWorkspace from '@/components/HomeownerProjectWorkspace'
import ExternalBidCardDemo from '@/pages/ExternalBidCardDemo'
import ExternalBidCardLanding from '@/pages/ExternalBidCardLanding'
import ContractorHeroLanding from '@/pages/ContractorHeroLanding'
import ContractorLandingPage from '@/pages/contractor/ContractorLandingPage'
import ProtectedRoute from '@/components/auth/ProtectedRoute'

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/webrtc-test" element={<WebRTCTestPage />} />
            <Route path="/auth/callback" element={<AuthCallbackPage />} />
            <Route path="/external-bid-card-demo" element={<ExternalBidCardDemo />} />
            <Route path="/join" element={<ExternalBidCardLanding />} />
            <Route path="/contractor" element={<ContractorLandingPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute requiredRole="homeowner">
                  <DashboardPage />
                </ProtectedRoute>
              }
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
              element={
                <ProtectedRoute requiredRole="homeowner">
                  <HomeownerProjectWorkspace />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster position="top-right" />
        </div>
      </AuthProvider>
    </Router>
  )
}

export default App