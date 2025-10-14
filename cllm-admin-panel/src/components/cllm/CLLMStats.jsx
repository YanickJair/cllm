// src/components/cllm/CLLMStats.jsx
import { Zap, TrendingDown, DollarSign, Clock } from 'lucide-react';

function CLLMStats() {
  const stats = [
    {
      title: 'Compression Rate',
      value: '92.3%',
      subtitle: '2,920 → 225 tokens avg',
      icon: Zap,
      color: 'green',
      trend: '+2.1% vs last month'
    },
    {
      title: 'Tokens Saved',
      value: '2,695',
      subtitle: 'Per NBA wrapup',
      icon: TrendingDown,
      color: 'blue',
      trend: 'Consistent performance'
    },
    {
      title: 'Monthly Savings',
      value: '$2.82M',
      subtitle: 'At 5,000 agents',
      icon: DollarSign,
      color: 'emerald',
      trend: '+18.2% this month'
    },
    {
      title: 'Latency Improvement',
      value: '4.5x',
      subtitle: '1.8s → 0.4s',
      icon: Clock,
      color: 'purple',
      trend: 'Faster response time'
    }
  ];

  const colorClasses = {
    green: 'bg-green-50 text-green-600 border-green-100',
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100'
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className={`p-3 rounded-lg border ${colorClasses[stat.color]}`}>
              <stat.icon className="w-6 h-6" />
            </div>
          </div>
          
          <div className="mb-1">
            <h3 className="text-sm font-medium text-gray-600">{stat.title}</h3>
            <div className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</div>
            <p className="text-xs text-gray-500 mt-1">{stat.subtitle}</p>
          </div>
          
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-600">{stat.trend}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

export default CLLMStats;