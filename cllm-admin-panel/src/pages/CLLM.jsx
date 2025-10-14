import CLLMStats from '../components/cllm/CLLMStats';
import CompressionMonitor from '../components/cllm/CompressionMonitor';
import SavingsCalculator from '../components/cllm/SavingsCalculator';
import TokenAnalysis from '../components/cllm/TokenAnalysis';

function CLLM() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">CLLM Statistics</h1>
        <p className="text-gray-600 mt-1">
          Monitor compression performance and calculate savings
        </p>
      </div>

      {/* Stats Overview */}
      <CLLMStats />

      {/* Compression Monitor & Savings Calculator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CompressionMonitor />
        <SavingsCalculator />
      </div>

      {/* Token Analysis */}
      <TokenAnalysis />
    </div>
  );
}
export default CLLM;