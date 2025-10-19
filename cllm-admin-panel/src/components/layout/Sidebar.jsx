// src/components/layout/Sidebar.jsx
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  GitBranch, 
  BarChart3, 
  MessageSquare, 
  BookOpen, 
  Settings 
} from 'lucide-react';

function Sidebar() {
  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/nba', icon: GitBranch, label: 'NBA Management' },
    { path: '/cllm', icon: BarChart3, label: 'CLLM Stats' },
    { path: '/prompts', icon: MessageSquare, label: 'System Prompts' },
    { path: '/vocabulary', icon: BookOpen, label: 'Vocabulary' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo/Brand */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">CL</span>
          </div>
          <span className="text-xl font-bold text-gray-900">CLLM Admin</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon 
                  className={`w-5 h-5 mr-3 ${
                    isActive ? 'text-primary-600' : 'text-gray-500'
                  }`} 
                />
                {item.label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 space-y-1">
          <div className="flex justify-between">
            <span>Active Agents:</span>
            <span className="font-semibold text-gray-700">5,000</span>
          </div>
          <div className="flex justify-between">
            <span>Target Scale:</span>
            <span className="font-semibold text-primary-600">80,000</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;