// src/components/cllm/CompressionMonitor.jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function CompressionMonitor() {
  // Token breakdown data
  const tokenData = [
    { 
      component: 'System Prompt',
      traditional: 400,
      cllm: 1,
      saved: 399
    },
    { 
      component: 'User Instruction',
      traditional: 120,
      cllm: 4,
      saved: 116
    },
    { 
      component: 'NBA Catalog',
      traditional: 2200,
      cllm: 20,
      saved: 2180
    },
    { 
      component: 'Transcript',
      traditional: 800,
      cllm: 800,
      saved: 0
    }
  ];

  const totalTraditional = tokenData.reduce((sum, item) => sum + item.traditional, 0);
  const totalCLLM = tokenData.reduce((sum, item) => sum + item.cllm, 0);
  const compressionRate = ((totalTraditional - totalCLLM) / totalTraditional * 100).toFixed(1);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900 mb-2">{data.component}</p>
          <p className="text-sm text-red-600">Traditional: {data.traditional} tokens</p>
          <p className="text-sm text-green-600">CLLM: {data.cllm} tokens</p>
          <p className="text-sm text-blue-600 font-medium mt-1">Saved: {data.saved} tokens</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Compression Monitor</h2>
          <p className="text-sm text-gray-600 mt-1">Token usage breakdown by component</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-green-600">{compressionRate}%</div>
          <div className="text-xs text-gray-600">Total Compression</div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={tokenData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="component" 
            stroke="#6b7280" 
            style={{ fontSize: '12px' }}
            angle={-15}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="traditional" fill="#ef4444" name="Traditional" radius={[8, 8, 0, 0]} />
          <Bar dataKey="cllm" fill="#10b981" name="CLLM" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{totalTraditional.toLocaleString()}</div>
          <div className="text-xs text-gray-600 mt-1">Traditional Tokens</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{totalCLLM.toLocaleString()}</div>
          <div className="text-xs text-gray-600 mt-1">CLLM Tokens</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{(totalTraditional - totalCLLM).toLocaleString()}</div>
          <div className="text-xs text-gray-600 mt-1">Tokens Saved</div>
        </div>
      </div>

      {/* Note */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-xs text-blue-800">
          <span className="font-semibold">Note:</span> Transcript tokens remain unchanged as they contain the actual conversation content.
          Maximum compression is applied to system prompts and NBA catalog.
        </p>
      </div>
    </div>
  );
}

export default CompressionMonitor;