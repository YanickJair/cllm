// src/components/nba/NBAList.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Eye, Trash2, Search, Filter } from 'lucide-react';
import { mockNBAs, toCLLMToken, getPriorityColor, getStatusColor } from '../../utils/mockNBAData';

function NBAList() {
  const navigate = useNavigate();
  const [nbas, setNbas] = useState(mockNBAs);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPriority, setFilterPriority] = useState('ALL');

  // Filter NBAs
  const filteredNBAs = nbas.filter(nba => {
    const matchesSearch = nba.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         nba.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         nba.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPriority = filterPriority === 'ALL' || nba.priority === filterPriority;
    return matchesSearch && matchesPriority;
  });

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this NBA?')) {
      setNbas(nbas.filter(nba => nba.id !== id));
    }
  };

  const PriorityBadge = ({ priority }) => {
    const color = getPriorityColor(priority);
    const colorClasses = {
      red: 'bg-red-100 text-red-700',
      yellow: 'bg-yellow-100 text-yellow-700',
      green: 'bg-green-100 text-green-700'
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClasses[color]}`}>
        {priority}
      </span>
    );
  };

  const StatusBadge = ({ status }) => {
    const color = getStatusColor(status);
    const colorClasses = {
      green: 'bg-green-100 text-green-700',
      gray: 'bg-gray-100 text-gray-700',
      red: 'bg-red-100 text-red-700'
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
          <h1 className="text-3xl font-bold text-gray-900">NBA Management</h1>
          <p className="text-gray-600 mt-1">
            Manage Next Best Actions for your contact center agents
          </p>
        </div>
        <button
          onClick={() => navigate('/nba/create')}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
        >
          <Plus className="w-5 h-5 mr-2" />
          Create NBA
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{nbas.length}</div>
          <div className="text-sm text-gray-600">Total NBAs</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-red-600">
            {nbas.filter(n => n.priority === 'HIGH').length}
          </div>
          <div className="text-sm text-gray-600">High Priority</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-green-600">
            {nbas.filter(n => n.status === 'active').length}
          </div>
          <div className="text-sm text-gray-600">Active</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">
            {nbas.reduce((sum, nba) => sum + nba.actions.length, 0)}
          </div>
          <div className="text-sm text-gray-600">Total Actions</div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search NBAs by title, ID, or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Priority Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="ALL">All Priorities</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* NBA Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  NBA
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CLLM Token
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Updated
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredNBAs.map((nba) => (
                <tr key={nba.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <div className="text-sm font-medium text-gray-900">{nba.title}</div>
                      <div className="text-xs text-gray-500">{nba.id}</div>
                      <div className="text-xs text-gray-500 mt-1 line-clamp-2">{nba.description}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <PriorityBadge priority={nba.priority} />
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {nba.actions.length}
                  </td>
                  <td className="px-6 py-4">
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-800">
                      {toCLLMToken(nba)}
                    </code>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={nba.status} />
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(nba.updatedAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => navigate(`/nba/edit/${nba.id}`)}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => navigate(`/nba/edit/${nba.id}`)}
                        className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                        title="Edit"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(nba.id)}
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

        {filteredNBAs.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No NBAs found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default NBAList;