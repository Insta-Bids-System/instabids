import { motion } from "framer-motion";
import { useState } from "react";
import type React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

// Tab Components (will be created next)
import CIAChatTab from "./tabs/CIAChatTab";
import DashboardTab from "./tabs/DashboardTab";
import AdminTab from "./tabs/AdminTab";
import ContractorTab from "./tabs/ContractorTab";
import InspirationTab from "./tabs/InspirationTab";

interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  icon?: string;
}

const TabButton: React.FC<TabButtonProps> = ({ active, onClick, children, icon }) => (
  <button
    type="button"
    onClick={onClick}
    className={`
      flex items-center gap-2 px-6 py-3 text-sm font-medium rounded-lg transition-all duration-200
      ${active 
        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg' 
        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
      }
    `}
  >
    {icon && <span className="text-lg">{icon}</span>}
    {children}
  </button>
);

const UnifiedDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // Extract tab from URL parameters
  React.useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab && ['chat', 'dashboard', 'admin', 'contractor', 'inspiration'].includes(tab)) {
      setActiveTab(tab);
    }
  }, []);

  // Update URL when tab changes
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    const newUrl = `/?tab=${tab}`;
    window.history.replaceState({}, '', newUrl);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Fixed Header with Tab Navigation */}
      <header className="bg-white/80 backdrop-blur-sm fixed top-0 w-full z-40 shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center mb-4">
            {/* Logo */}
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Instabids
            </h1>
            
            {/* User Menu */}
            <div className="flex items-center gap-4">
              {user ? (
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600">
                    Welcome, {user.user_metadata?.full_name || user.email}
                  </span>
                  <button
                    type="button"
                    onClick={() => logout()}
                    className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => navigate("/login")}
                    className="text-gray-700 hover:text-primary-600 transition-colors"
                  >
                    Login
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate("/signup")}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all duration-200"
                  >
                    Sign Up
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Tab Navigation */}
          <nav className="flex flex-wrap gap-2">
            <TabButton 
              active={activeTab === 'chat'} 
              onClick={() => handleTabChange('chat')}
              icon="💬"
            >
              Chat
            </TabButton>
            <TabButton 
              active={activeTab === 'dashboard'} 
              onClick={() => handleTabChange('dashboard')}
              icon="📊"
            >
              Dashboard
            </TabButton>
            <TabButton 
              active={activeTab === 'admin'} 
              onClick={() => handleTabChange('admin')}
              icon="⚙️"
            >
              Admin
            </TabButton>
            <TabButton 
              active={activeTab === 'contractor'} 
              onClick={() => handleTabChange('contractor')}
              icon="👷"
            >
              Contractors
            </TabButton>
            <TabButton 
              active={activeTab === 'inspiration'} 
              onClick={() => handleTabChange('inspiration')}
              icon="✨"
            >
              Inspiration
            </TabButton>
          </nav>
        </div>
      </header>
      
      {/* Tab Content */}
      <main className="pt-32 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'chat' && <CIAChatTab />}
            {activeTab === 'dashboard' && <DashboardTab />}
            {activeTab === 'admin' && <AdminTab />}
            {activeTab === 'contractor' && <ContractorTab />}
            {activeTab === 'inspiration' && <InspirationTab />}
          </motion.div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 text-center text-gray-500 text-sm border-t bg-white">
        <p>© 2025 Instabids. All rights reserved. | Privacy | Terms</p>
      </footer>
    </div>
  );
};

export default UnifiedDashboard;