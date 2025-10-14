// src/components/nba/NBAEdit.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';
import { mockNBAs } from '../../utils/mockNBAData';

function NBAEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [nba, setNba] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading NBA data
    const foundNBA = mockNBAs.find(n => n.id === id);
    if (foundNBA) {
      setNba(foundNBA);
    }
    setLoading(false);
  }, [id]);

  const handleSave = () => {
    // Here you would typically send to API
    console.log('Saving NBA:', nba);
    alert('NBA updated successfully!');
    navigate('/nba');
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this NBA?')) {
      console.log('Deleting NBA:', id);
      alert('NBA deleted successfully!');
      navigate('/nba');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!nba) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">NBA Not Found</h2>
        <p className="text-gray-600 mb-6">The NBA you're looking for doesn't exist.</p>
        <button
          onClick={() => navigate('/nba')}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Back to NBA List
        </button>
      </div>
    );
  }

  const previewToken = `[NBA:${nba.id}:P=${nba.priority}:ACTIONS=${nba.actions.length}]`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/nba')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{nba.title}</h1>
            <p className="text-gray-600 mt-1">Edit NBA details and actions</p>
          </div>
        </div>
        <button
          onClick={handleDelete}
          className="flex items-center px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
        >
          <Trash2 className="w-5 h-5 mr-2" />
          Delete NBA
        </button>
      </div>

      {/* CLLM Token Preview */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-blue-900 mb-1">CLLM Token</div>
            <code className="text-sm bg-white px-3 py-1 rounded text-blue-800 border border-blue-200">
              {previewToken}
            </code>
          </div>
          <div className="text-right">
            <div className="text-xs text-blue-700">Token Compression</div>
            <div className="text-lg font-bold text-blue-900">~92.3%</div>
          </div>
        </div>
      </div>

      {/* NBA Details */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">NBA ID</label>
            <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-600">
              {nba.id}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-900">
              {nba.title}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-900">
              {nba.description}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                nba.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
                nba.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                'bg-green-100 text-green-700'
              }`}>
                {nba.priority}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                nba.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
              }`}>
                {nba.status}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Prerequisites */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Prerequisites</h2>
        <div className="flex flex-wrap gap-2">
          {nba.prerequisites.length > 0 ? (
            nba.prerequisites.map((prereq, index) => (
              <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                {prereq}
              </span>
            ))
          ) : (
            <p className="text-gray-500 text-sm">No prerequisites defined</p>
          )}
        </div>
      </div>

      {/* Success Indicators */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Success Indicators</h2>
        <div className="flex flex-wrap gap-2">
          {nba.successIndicators.length > 0 ? (
            nba.successIndicators.map((indicator, index) => (
              <span key={index} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                {indicator}
              </span>
            ))
          ) : (
            <p className="text-gray-500 text-sm">No success indicators defined</p>
          )}
        </div>
      </div>

      {/* Keywords */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Keywords</h2>
        <div className="flex flex-wrap gap-2">
          {nba.keywords.length > 0 ? (
            nba.keywords.map((keyword, index) => (
              <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                {keyword}
              </span>
            ))
          ) : (
            <p className="text-gray-500 text-sm">No keywords defined</p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions ({nba.actions.length})</h2>
        
        <div className="space-y-4">
          {nba.actions.map((action, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="font-medium text-gray-900">{action.name}</h3>
                    {action.authorizationRequired && (
                      <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded text-xs font-medium">
                        Auth Required
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{action.description}</p>
                  <div className="text-xs text-gray-500 space-y-1">
                    <div><span className="font-medium">When to use:</span> {action.whenToUse}</div>
                    {action.estimatedTimeMinutes > 0 && (
                      <div><span className="font-medium">Estimated time:</span> {action.estimatedTimeMinutes} minutes</div>
                    )}
                    {action.uiComponent && (
                      <div><span className="font-medium">UI Component:</span> {action.uiComponent}</div>
                    )}
                    {action.prerequisites && action.prerequisites.length > 0 && (
                      <div><span className="font-medium">Prerequisites:</span> {action.prerequisites.join(', ')}</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Metadata</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Created:</span>
            <span className="text-gray-600 ml-2">{new Date(nba.createdAt).toLocaleDateString()}</span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Last Updated:</span>
            <span className="text-gray-600 ml-2">{new Date(nba.updatedAt).toLocaleDateString()}</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={() => navigate('/nba')}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Back to List
        </button>
        <button
          onClick={handleSave}
          className="flex items-center px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Save className="w-5 h-5 mr-2" />
          Save Changes
        </button>
      </div>
    </div>
  );
}

export default NBAEdit;