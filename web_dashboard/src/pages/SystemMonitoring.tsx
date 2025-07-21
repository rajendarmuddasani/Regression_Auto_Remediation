import type { SystemHealth } from '../types';

interface SystemMonitoringProps {
  systemHealth: SystemHealth | null;
}

export default function SystemMonitoring({ systemHealth }: SystemMonitoringProps) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">System Monitoring</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor system health and performance metrics
        </p>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Current System Status</h3>
        <p className="text-gray-500">
          Status: {systemHealth?.overall_status || 'Unknown'}
        </p>
        <p className="text-sm text-gray-400 mt-2">
          Detailed monitoring functionality coming soon...
        </p>
      </div>
    </div>
  );
}
