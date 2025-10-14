// src/components/dashboard/MetricsChart.jsx
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

function MetricsChart({ title, type = 'line' }) {
  // Mock data for token usage trend
  const tokenData = [
    { month: 'Jan', traditional: 2920, cllm: 225, savings: 2695 },
    { month: 'Feb', traditional: 2935, cllm: 228, savings: 2707 },
    { month: 'Mar', traditional: 2910, cllm: 222, savings: 2688 },
    { month: 'Apr', traditional: 2925, cllm: 226, savings: 2699 },
    { month: 'May', traditional: 2940, cllm: 230, savings: 2710 },
    { month: 'Jun', traditional: 2920, cllm: 225, savings: 2695 },
  ];

  // Mock data for cost savings
  const savingsData = [
    { month: 'Jan', current: 235000, projected: 3750000 },
    { month: 'Feb', current: 238000, projected: 3800000 },
    { month: 'Mar', current: 232000, projected: 3712000 },
    { month: 'Apr', current: 240000, projected: 3840000 },
    { month: 'May', current: 245000, projected: 3920000 },
    { month: 'Jun', current: 282000, projected: 4512000 },
  ];

  const data = type === 'line' ? tokenData : savingsData;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.name.includes('$') ? `$${(entry.value / 1000).toFixed(0)}K` : entry.value.toLocaleString()}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      
      <ResponsiveContainer width="100%" height={300}>
        {type === 'line' ? (
          <LineChart data={data}>
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
          </LineChart>
        ) : (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#6b7280" style={{ fontSize: '12px' }} />
            <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="current" fill="#3b82f6" name="Current (5K agents)" radius={[8, 8, 0, 0]} />
            <Bar dataKey="projected" fill="#8b5cf6" name="Projected (80K agents)" radius={[8, 8, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>

      {type === 'line' && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <p className="text-sm text-green-800">
            <span className="font-semibold">92.3% compression rate</span> achieved - saving an average of 2,695 tokens per NBA wrapup
          </p>
        </div>
      )}

      {type === 'bar' && (
        <div className="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
          <p className="text-sm text-purple-800">
            <span className="font-semibold">$45M annual savings</span> projected at 80K agent scale
          </p>
        </div>
      )}
    </div>
  );
}

export default MetricsChart;