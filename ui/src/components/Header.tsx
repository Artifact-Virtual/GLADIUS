import { Bell, User } from 'lucide-react';
import { useSystemStore } from '../stores/systemStore';

const Header = () => {
  const systemStatus = useSystemStore((state) => state.systemStatus);

  const getOverallStatus = () => {
    const statuses = [
      systemStatus.gladius.status,
      systemStatus.sentinel.status,
      systemStatus.legion.status,
      systemStatus.artifact.status,
    ];

    if (statuses.some(s => s === 'error')) return 'error';
    if (statuses.some(s => s === 'stopped')) return 'warning';
    if (statuses.every(s => s === 'running')) return 'success';
    return 'unknown';
  };

  const overallStatus = getOverallStatus();

  return (
    <header className="h-16 bg-secondary border-b border-accent/10 flex items-center justify-between px-6">
      {/* System Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-text-dim">System Status:</span>
          <div className="flex items-center gap-2">
            {overallStatus === 'success' && (
              <>
                <span className="status-running" />
                <span className="text-sm text-success font-semibold">All Systems Operational</span>
              </>
            )}
            {overallStatus === 'error' && (
              <>
                <span className="status-stopped" />
                <span className="text-sm text-error font-semibold">System Error</span>
              </>
            )}
            {overallStatus === 'warning' && (
              <>
                <span className="status-warning" />
                <span className="text-sm text-warning font-semibold">Partial Operation</span>
              </>
            )}
            {overallStatus === 'unknown' && (
              <>
                <span className="status-dot bg-text-dim" />
                <span className="text-sm text-text-dim font-semibold">Initializing...</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <button className="btn-ghost p-2">
          <Bell size={20} />
        </button>
        <button className="btn-ghost p-2">
          <User size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;
