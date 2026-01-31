import { Link, useLocation } from 'react-router-dom';
import { Home, Zap, Shield, Users, Package, FileText, Settings, Activity, BarChart2 } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/gladius', icon: Zap, label: 'GLADIUS' },
    { path: '/sentinel', icon: Shield, label: 'SENTINEL' },
    { path: '/legion', icon: Users, label: 'LEGION' },
    { path: '/syndicate', icon: BarChart2, label: 'SYNDICATE' },
    { path: '/arty', icon: Activity, label: 'ARTY' },
    { path: '/artifact', icon: Package, label: 'Artifact' },
    { path: '/logs', icon: FileText, label: 'Logs' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className="w-64 bg-secondary border-r border-accent/10 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-accent/10">
        <h1 className="text-2xl font-bold gradient-text">GLADIUS</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={isActive ? 'sidebar-link-active' : 'sidebar-link'}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-accent/10">
        <p className="text-xs text-text-dim text-center">
          GLADIUS v2.0
        </p>
        <p className="text-xs text-text-dim text-center mt-1">
          Artifact Virtual
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
