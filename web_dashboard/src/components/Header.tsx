import { Menu, Bell, User, Wifi, WifiOff } from 'lucide-react';
import { cn } from '../utils';
import type { SystemHealth } from '../types';

interface HeaderProps {
  onMenuClick: () => void;
  systemHealth: SystemHealth | null;
}

export default function Header({ onMenuClick, systemHealth }: HeaderProps) {
  const isHealthy = systemHealth?.overall_status === 'healthy';

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <button
              type="button"
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              onClick={onMenuClick}
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="hidden lg:flex lg:items-center lg:space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                Regression Auto-Remediation Dashboard
              </h1>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* System Status */}
            <div className="flex items-center space-x-2">
              {isHealthy ? (
                <Wifi className="w-5 h-5 text-green-500" />
              ) : (
                <WifiOff className="w-5 h-5 text-red-500" />
              )}
              <span className={cn(
                "text-sm font-medium",
                isHealthy ? "text-green-600" : "text-red-600"
              )}>
                {systemHealth?.overall_status || 'Unknown'}
              </span>
            </div>

            {/* Notifications */}
            <button
              type="button"
              className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 relative"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 block h-2 w-2 bg-red-400 rounded-full"></span>
            </button>

            {/* User Menu */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-gray-600" />
                </div>
                <span className="hidden sm:block text-sm font-medium text-gray-700">
                  Admin
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
