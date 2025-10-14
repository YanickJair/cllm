// src/components/cllm/SavingsCalculator.jsx
import { useState } from 'react';
import { Calculator, TrendingUp } from 'lucide-react';

function SavingsCalculator() {
  const [agents, setAgents] = useState(5000);
  const [wrapupsPerAgent, setWrapupsPerAgent] = useState(5.8); // 29K wrapups / 5K agents = 5.8 per agent per month
  const [costPer1k, setCostPer1k] = useState(0.003);

  // Constants
  const traditionalTokens = 2920;
  const cllmTokens = 225;
  const tokensSaved = traditionalTokens - cllmTokens;

  // Calculations
  const monthlyWrapups = agents * wrapupsPerAgent;
  const traditionalMonthlyCost = (monthlyWrapups * traditionalTokens / 1000) * costPer1k;
  const cllmMonthlyCost = (monthlyWrapups * cllmTokens / 1000) * costPer1k;
  const monthlySavings = traditionalMonthlyCost - cllmMonthlyCost;
  const annualSavings = monthlySavings * 12;
  const compressionRate = ((tokensSaved / traditionalTokens) * 100).toFixed(1);

  // ROI Calculation (assuming $4,087 implementation cost)
  const implementationCost = 4087;
  const breakEvenDays = (implementationCost / (annualSavings / 365)).toFixed(1);

  const formatCurrency = (value) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`;
    }
    return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-2 mb-6">
        <Calculator className="w-6 h-6 text-primary-600" />
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Savings Calculator</h2>
          <p className="text-sm text-gray-600">Calculate your potential cost savings</p>
        </div>
      </div>

      {/* Input Controls */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of Agents
          </label>
          <input
            type="number"
            value={agents}
            onChange={(e) => setAgents(parseInt(e.target.value) || 0)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            min="0"
            step="1000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            NBA Wrapups per Agent/Month
          </label>
          <input
            type="number"
            value={wrapupsPerAgent}
            onChange={(e) => setWrapupsPerAgent(parseFloat(e.target.value) || 0)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            min="0"
            step="0.1"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cost per 1K Tokens ($)
          </label>
          <input
            type="number"
            value={costPer1k}
            onChange={(e) => setCostPer1k(parseFloat(e.target.value) || 0)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            min="0"
            step="0.001"
          />
        </div>
      </div>

      {/* Results */}
      <div className="space-y-3 mb-6">
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm text-gray-600">Monthly Wrapups</span>
            <span className="text-lg font-bold text-gray-900">{monthlyWrapups.toLocaleString()}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Compression Rate</span>
            <span className="text-lg font-bold text-green-600">{compressionRate}%</span>
          </div>
        </div>

        <div className="p-4 bg-green-50 rounded-lg border border-green-200">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-green-900">Monthly Savings</span>
            <span className="text-2xl font-bold text-green-600">{formatCurrency(monthlySavings)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-green-900">Annual Savings</span>
            <span className="text-2xl font-bold text-green-600">{formatCurrency(annualSavings)}</span>
          </div>
        </div>

        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">ROI Analysis</span>
          </div>
          <div className="text-xs text-blue-800 space-y-1">
            <div>Implementation Cost: ${implementationCost.toLocaleString()}</div>
            <div className="font-semibold">Break-even: {breakEvenDays} days</div>
            <div>5-Year ROI: {((annualSavings * 5 - implementationCost) / implementationCost * 100).toFixed(0)}%</div>
          </div>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="pt-4 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Cost Breakdown</h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">Traditional Monthly Cost:</span>
            <span className="font-medium text-red-600">{formatCurrency(traditionalMonthlyCost)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">CLLM Monthly Cost:</span>
            <span className="font-medium text-green-600">{formatCurrency(cllmMonthlyCost)}</span>
          </div>
          <div className="flex justify-between pt-2 border-t border-gray-200">
            <span className="text-gray-900 font-medium">Monthly Savings:</span>
            <span className="font-bold text-green-600">{formatCurrency(monthlySavings)}</span>
          </div>
        </div>
      </div>

      {/* Presets */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-600 mb-2">Quick Presets:</p>
        <div className="flex space-x-2">
          <button
            onClick={() => setAgents(5000)}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
          >
            Current (5K)
          </button>
          <button
            onClick={() => setAgents(20000)}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
          >
            Mid (20K)
          </button>
          <button
            onClick={() => setAgents(80000)}
            className="px-3 py-1 text-xs bg-primary-100 text-primary-700 rounded hover:bg-primary-200 transition-colors font-medium"
          >
            Target (80K)
          </button>
        </div>
      </div>
    </div>
  );
}

export default SavingsCalculator;