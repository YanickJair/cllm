// src/components/prompts/SystemPromptsList.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, TestTube, Eye, Trash2, Filter, Search } from 'lucide-react';
import { mockPrompts, features, promptTypes, getCompressionColor, getStatusColor } from '../../utils/mockPromptData';

function SystemPromptsList() {
  const navigate = useNavigate();
  const [prompts, setPrompts] = useState(mockPrompts);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterFeature, setFilterFeature] = useState('ALL');
  const [filterType, setFilterType] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');

  // Filter prompts
  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFeature = filterFeature === 'ALL' || prompt.feature === filterFeature;
    const matchesType = filterType === 'ALL' || prompt.type === filterType;
    const matchesStatus = filterStatus === 'ALL' || prompt.status === filterStatus;
    return matchesSearch && matchesFeature && matchesType && matchesStatus;
  });

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      setPrompts(prompts.filter(p => p.id !== id));
    }
  };

  const CompressionBadge = ({ rate }) => {
    const color = getCompressionColor(rate);
    const colorClasses = {
      green: 'bg-green-100 text-green-700',
      blue: 'bg-blue-100 text-blue-700',
      yellow: 'bg-yellow-100 text-yellow-700',
      gray: 'bg-gray-100 text-gray-700'
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClasses[color]}`}>
        {rate}%
      </span>
    );
  };

  const StatusBadge = ({ status }) => {
    const color = getStatusColor(status);
    const colorClasses = {
      green: 'bg-green-100 text-green-700',
      yellow: 'bg-yellow-100 text-yellow-700',
      gray: 'bg-gray-100 text-gray-700',
      blue: 'bg-blue-100 text-blue-700'
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClasses[color]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Prompts</h1>
          <p className="text-gray-600 mt-1">
            Manage prompts that get compressed by CLLM
          </p>
        </div>
        <button
          onClick={() => navigate('/prompts/create')}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
        >
          <Plus className="w-5 h-5 mr-2" />
          Create Prompt
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{prompts.length}</div>
          <div className="text-sm text-gray-600">Total Prompts</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-green-600">
            {prompts.filter(p => p.status === 'active').length}
          </div>
          <div className="text-sm text-gray-600">Active</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">
            {prompts.reduce((sum, p) => sum + p.originalTokens, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Original Tokens</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-green-600">
            {prompts.reduce((sum, p) => sum + p.compressedTokens, 0)}
          </div>
          <div className="text-sm text-gray-600">Compressed Tokens</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search prompts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={filterFeature}
              onChange={(e) => setFilterFeature(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="ALL">All Features</option>
              {features.map(f => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>

            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="ALL">All Types</option>
              {promptTypes.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="ALL">All Status</option>
              <option value="active">Active</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>
      </div>

      {/* Prompts Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Prompt
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Feature
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tokens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Compression
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPrompts.map((prompt) => (
                <tr key={prompt.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <div className="text-sm font-medium text-gray-900">{prompt.name}</div>
                      <div className="text-xs text-gray-500 mt-1">{prompt.description}</div>
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-800 mt-2 inline-block">
                        {prompt.compressedToken}
                      </code>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                      {prompt.feature}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-900 capitalize">{prompt.type}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      <div className="text-red-600 line-through">{prompt.originalTokens}</div>
                      <div className="text-green-600 font-medium">{prompt.compressedTokens}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <CompressionBadge rate={prompt.compressionRate} />
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={prompt.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => navigate(`/prompts/test/${prompt.id}`)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Test Prompt"
                      >
                        <TestTube className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => navigate(`/prompts/edit/${prompt.id}`)}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        title="View"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => navigate(`/prompts/edit/${prompt.id}`)}
                        className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                        title="Edit"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(prompt.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredPrompts.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No prompts found matching your criteria.</p>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">About System Prompts</h3>
        <p className="text-sm text-blue-800">
          System prompts are the instructions that guide the AI model. CLLM compresses these prompts into semantic tokens,
          achieving up to 99.8% compression while maintaining their full meaning. Each prompt is tied to a feature (like NBA)
          and can be versioned for A/B testing.
        </p>
      </div>
    </div>
  );
}

export default SystemPromptsList;