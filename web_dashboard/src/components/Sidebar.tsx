import React from 'react';
import { NavLink } from 'react-router-dom';
import { X, BarChart3, FileText, AlertTriangle, Lightbulb, Activity, TrendingUp, Settings } from 'lucide-react';
import { cn } from '../utils';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
  { name: 'File Parser', href: '/parser', icon: FileText },
  { name: 'Issue Classifier', href: '/classifier', icon: AlertTriangle },
  { name: 'Solution Recommender', href: '/recommender', icon: Lightbulb },
  { name: 'System Monitoring', href: '/monitoring', icon: Activity },
  { name: 'Analytics', href: '/analytics', icon: TrendingUp },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={onClose}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </div>
      )}

      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
        open ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="ml-3">
              <h1 className="text-lg font-semibold text-gray-900">
                Auto-Remediation
              </h1>
            </div>
          </div>
          <button
            type="button"
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            onClick={onClose}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="mt-5 px-2">
          <div className="space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors",
                    isActive
                      ? "bg-blue-100 text-blue-900"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  )
                }
              >
                <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                {item.name}
              </NavLink>
            ))}
          </div>
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            Regression Auto-Remediation v1.0.0
          </div>
        </div>
      </div>
    </>
  );
}
