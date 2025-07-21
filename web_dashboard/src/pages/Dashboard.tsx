import { useState, useEffect } from 'react';
import { FileText, AlertTriangle, Lightbulb, Activity } from 'lucide-react';
import { monitoringApi } from '../services/api';
import { cn } from '../utils';
import type { SystemHealth, UsageStats } from '../types';

interface DashboardProps {
  systemHealth: SystemHealth | null;
}

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  status?: 'healthy' | 'warning' | 'error';
}

function StatsCard({ title, value, icon: Icon, trend, status }: StatsCardProps) {
  const statusColors = {
    healthy: 'text-green-600 bg-green-100',
    warning: 'text-yellow-600 bg-yellow-100',
    error: 'text-red-600 bg-red-100',
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={cn(
              "w-8 h-8 rounded-md flex items-center justify-center",
              status ? statusColors[status] : "text-blue-600 bg-blue-100"
            )}>
              <Icon className="w-5 h-5" />
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900">{value}</div>
                {trend && (
                  <div className={cn(
                    "ml-2 flex items-baseline text-sm font-semibold",
                    trend.isPositive ? "text-green-600" : "text-red-600"
                  )}>
                    {trend.isPositive ? '+' : ''}{trend.value}%
                  </div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard({ systemHealth }: DashboardProps) {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await monitoringApi.getUsageStats(30);
        setAnalytics(data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white shadow rounded-lg p-5">
              <div className="animate-pulse">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-gray-200 rounded-md"></div>
                  <div className="ml-5 flex-1">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-6 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your regression auto-remediation system
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Files Processed"
          value={analytics?.total_files || 0}
          icon={FileText}
          trend={{ value: 12, isPositive: true }}
        />
        <StatsCard
          title="Issues Classified"
          value={analytics?.total_classifications || 0}
          icon={AlertTriangle}
          trend={{ value: 8, isPositive: true }}
        />
        <StatsCard
          title="Solutions Recommended"
          value={analytics?.total_recommendations || 0}
          icon={Lightbulb}
          trend={{ value: 15, isPositive: true }}
        />
        <StatsCard
          title="System Health"
          value={systemHealth?.overall_status || 'Unknown'}
          icon={Activity}
          status={systemHealth?.overall_status === 'healthy' ? 'healthy' : 'error'}
        />
      </div>

      {/* System Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Resources */}
        <div className="bg-white shadow rounded-lg">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Resources</h3>
            {systemHealth?.system_info ? (
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>CPU Usage</span>
                    <span>{systemHealth.system_info.cpu_usage_percent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${systemHealth.system_info.cpu_usage_percent}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Memory Usage</span>
                    <span>{systemHealth.system_info.memory.used_percent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ width: `${systemHealth.system_info.memory.used_percent}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Disk Usage</span>
                    <span>{systemHealth.system_info.disk.used_percent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-yellow-600 h-2 rounded-full" 
                      style={{ width: `${systemHealth.system_info.disk.used_percent}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">System information unavailable</p>
            )}
          </div>
        </div>

        {/* Component Status */}
        <div className="bg-white shadow rounded-lg">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Component Status</h3>
            {systemHealth?.components ? (
              <div className="space-y-3">
                {Object.entries(systemHealth.components).map(([name, component]) => (
                  <div key={name} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 capitalize">{name}</span>
                    <div className="flex items-center space-x-2">
                      <div className={cn(
                        "w-2 h-2 rounded-full",
                        component.status === 'healthy' ? "bg-green-500" : "bg-red-500"
                      )}></div>
                      <span className={cn(
                        "text-sm font-medium",
                        component.status === 'healthy' ? "text-green-600" : "text-red-600"
                      )}>
                        {component.status === 'healthy' ? 'Healthy' : 'Unhealthy'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">Component status unavailable</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg">
        <div className="p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">System health check completed</span>
              <span className="text-xs text-gray-400">2 minutes ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-gray-600">New test file processed</span>
              <span className="text-xs text-gray-400">5 minutes ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Issue classification updated</span>
              <span className="text-xs text-gray-400">10 minutes ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
