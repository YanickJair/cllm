// src/components/cllm/TokenAnalysis.jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart } from 'recharts';
import { Activity } from 'lucide-react';

function TokenAnalysis() {
  // Historical data showing token usage over time
  const historicalData = [
    { month: 'Jan', traditional: 2950, cllm: 230, wrapups: 27000 },
    { month: 'Feb', traditional: 2935, cllm: 228, wrapups: 27500 },
    { month: 'Mar', traditional: 2910, cllm: 222, wrapups: 28200 },
    { month: 'Apr', traditional: 2925, cllm: 226, wrapups: 28500 },
    { month: 'May', traditional: 2940, cllm: 230, wrapups: 28800 },
    { month: 'Jun', traditional: 2920, cllm: 225, wrapups: 29000 },
  ];

  // Daily token usage for the current week
  const dailyData = [
    { day: 'Mon', tokens: 18500, saved: 17200 },
    { day: 'Tue', tokens: 19200, saved: 17800 },
    { day: 'Wed', tokens: 20100, saved: 18600 },
    { day: 'Thu', tokens: 19800, saved: 18300 },
    { day: 'Fri', tokens: 21000, saved: 19400 },
    { day: 'Sat', tokens: 15500, saved: 14300 },
    { day: 'Sun', tokens: 14200, saved: 13100 },
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value.toLocaleString()}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-2">
        <Activity className="w-6 h-6 text-primary-600" />
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Token Usage Analysis</h2>
          <p className="text-sm text-gray-600">Historical trends and daily patterns</p>
        </div>
      </div>

      {/* Monthly Trend */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-base font-semibold text-gray-900 mb-4">Monthly Token Usage Trend</h3>
        
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={historicalData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#6b7280" style={{ fontSize: '12px' }} />
            <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="traditional" 
              stroke="#ef4444" 
              strokeWidth={2}
              name="Traditional"
              dot={{ fill: '#ef4444', r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="cllm" 
              stroke="#10b981" 
              strokeWidth={2}
              name="CLLM"
              dot={{ fill: '#10b981', r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="wrapups" 
              stroke="#3b82f6" 
              strokeWidth={2}
              name="Wrapups (scaled)"
              yAxisId="right"
              dot={{ fill: '#3b82f6', r: 3 }}
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>

        <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <div className="text-xl font-bold text-red-600">2,920</div>
            <div className="text-xs text-gray-600">Avg Traditional Tokens</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-green-600">225</div>
            <div className="text-xs text-gray-600">Avg CLLM Tokens</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-blue-600">29,000</div>
            <div className="text-xs text-gray-600">Monthly Wrapups</div>
          </div>
        </div>
      </div>

      {/* Daily Usage Pattern */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-base font-semibold text-gray-900 mb-4">Daily Token Savings (This Week)</h3>
        
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={dailyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="day" stroke="#6b7280" style={{ fontSize: '12px' }} />
            <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="tokens" 
              fill="#93c5fd" 
              stroke="#3b82f6"
              name="CLLM Tokens Used"
            />
            <Area 
              type="monotone" 
              dataKey="saved" 
              fill="#86efac" 
              stroke="#10b981"
              name="Tokens Saved"
            />
          </AreaChart>
        </ResponsiveContainer>

        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <p className="text-sm text-green-800">
            <span className="font-semibold">This week:</span> Saved an average of 17,244 tokens per day, 
            resulting in approximately <span className="font-bold">$361 daily savings</span>.
          </p>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-2">Peak Efficiency Day</div>
          <div className="text-2xl font-bold text-green-600">Friday</div>
          <div className="text-xs text-gray-500 mt-1">19,400 tokens saved</div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-2">Consistency Score</div>
          <div className="text-2xl font-bold text-blue-600">98.7%</div>
          <div className="text-xs text-gray-500 mt-1">Stable compression rate</div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-2">Avg Response Time</div>
          <div className="text-2xl font-bold text-purple-600">0.4s</div>
          <div className="text-xs text-gray-500 mt-1">4.5x faster than traditional</div>
        </div>
      </div>
    </div>
  );
}

export default TokenAnalysis;