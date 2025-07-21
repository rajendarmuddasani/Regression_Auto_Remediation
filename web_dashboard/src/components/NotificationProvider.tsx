import React, { createContext, useContext, useState, useCallback } from 'react';
import { X, CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { cn } from '../utils';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const colors = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
};

const iconColors = {
  success: 'text-green-400',
  error: 'text-red-400',
  warning: 'text-yellow-400',
  info: 'text-blue-400',
};

export default function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification = { ...notification, id };
    
    setNotifications(prev => [...prev, newNotification]);
    
    // Auto-remove after duration (default 5 seconds)
    const duration = notification.duration || 5000;
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  return (
    <NotificationContext.Provider value={{ notifications, addNotification, removeNotification }}>
      {children}
      
      {/* Notification Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map((notification) => {
          const Icon = icons[notification.type];
          return (
            <div
              key={notification.id}
              className={cn(
                "max-w-sm w-full shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 p-4",
                colors[notification.type]
              )}
            >
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <Icon className={cn("h-6 w-6", iconColors[notification.type])} />
                </div>
                <div className="ml-3 w-0 flex-1 pt-0.5">
                  <p className="text-sm font-medium">{notification.title}</p>
                  {notification.message && (
                    <p className="mt-1 text-sm opacity-90">{notification.message}</p>
                  )}
                </div>
                <div className="ml-4 flex-shrink-0 flex">
                  <button
                    className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    onClick={() => removeNotification(notification.id)}
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </NotificationContext.Provider>
  );
}
