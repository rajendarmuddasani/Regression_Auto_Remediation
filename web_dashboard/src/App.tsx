import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import FileParser from './pages/FileParser';
import IssueClassifier from './pages/IssueClassifier';
import SolutionRecommender from './pages/SolutionRecommender';
import SystemMonitoring from './pages/SystemMonitoring';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import NotificationProvider from './components/NotificationProvider';
import { systemApi } from './services/api';
import type { SystemHealth } from './types';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSystemHealth = async () => {
      try {
        const health = await systemApi.getHealth();
        setSystemHealth(health);
      } catch (error) {
        console.error('Failed to fetch system health:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSystemHealth();
    
    // Poll health status every 30 seconds
    const interval = setInterval(fetchSystemHealth, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Regression Auto-Remediation Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <NotificationProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 flex">
          {/* Sidebar */}
          <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          
          {/* Main content area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <Header 
              onMenuClick={() => setSidebarOpen(true)} 
              systemHealth={systemHealth}
            />
            
            {/* Main content */}
            <main className="flex-1 overflow-auto bg-gray-50">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard systemHealth={systemHealth} />} />
                  <Route path="/parser" element={<FileParser />} />
                  <Route path="/classifier" element={<IssueClassifier />} />
                  <Route path="/recommender" element={<SolutionRecommender />} />
                  <Route path="/monitoring" element={<SystemMonitoring systemHealth={systemHealth} />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </div>
            </main>
          </div>
        </div>
      </Router>
    </NotificationProvider>
  );
}

export default App;
