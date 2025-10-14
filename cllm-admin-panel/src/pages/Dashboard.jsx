import StatsCard from '../components/dashboard/StatsCard';
import MetricsChart from '../components/dashboard/MetricsChart';
import { TrendingUp, Users, Zap, DollarSign, Activity, Target } from 'lucide-react';

function Dashboard() {
  // Mock data for stats
  const stats = [
    {
      title: 'Active Agents',
      value: '5,000',
      change: '+12.5%',
      changeType: 'positive',
      icon: Users,
      subtitle: 'Target: 80,000',
      color: 'blue'
    },
    {
      title: 'Compression Rate',
      value: '92.3%',
      change: 'Optimal',
      changeType: 'positive',
      icon: Zap,
      subtitle: '2,920 → 225 tokens',
      color: 'green'
    },
    {
      title: 'Monthly Savings',
      value: '$2.82M',
      change: '+18.2%',
      changeType: 'positive',
      icon: DollarSign,
      subtitle: 'At 5K agents',
      color: 'emerald'
    },
    {
      title: 'Annual Projection',
      value: '$45M',
      change: 'At 80K scale',
      changeType: 'positive',
      icon: TrendingUp,
      subtitle: 'Target savings',
      color: 'purple'
    },
    {
      title: 'NBA Wrapups',
      value: '29,000',
      change: '+5.3%',
      changeType: 'positive',
      icon: Activity,
      subtitle: 'Per month',
      color: 'orange'
    },
    {
      title: 'Total NBAs',
      value: '12',
      change: '3 pending',
      changeType: 'neutral',
      icon: Target,
      subtitle: 'Active definitions',
      color: 'indigo'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Overview of CLLM performance and NBA management system
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsChart 
          title="Token Usage Trend"
          type="line"
        />
        <MetricsChart 
          title="Cost Savings"
          type="bar"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center px-4 py-3 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition-colors font-medium">
            Create New NBA
          </button>
          <button className="flex items-center justify-center px-4 py-3 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors font-medium">
            View CLLM Stats
          </button>
          <button className="flex items-center justify-center px-4 py-3 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors font-medium">
            Manage Prompts
          </button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;