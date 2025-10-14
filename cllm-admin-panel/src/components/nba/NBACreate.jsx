// src/components/nba/NBACreate.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, X, Save } from 'lucide-react';
import { toCLLMToken } from '../../utils/mockNBAData';

function NBACreate() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    id: '',
    title: '',
    description: '',
    priority: 'MEDIUM',
    prerequisites: [],
    successIndicators: [],
    keywords: [],
    actions: [],
    status: 'active'
  });

  const [newPrerequisite, setNewPrerequisite] = useState('');
  const [newSuccessIndicator, setNewSuccessIndicator] = useState('');
  const [newKeyword, setNewKeyword] = useState('');
  const [showActionForm, setShowActionForm] = useState(false);
  const [currentAction, setCurrentAction] = useState({
    name: '',
    description: '',
    whenToUse: '',
    estimatedTimeMinutes: 0,
    authorizationRequired: false,
    prerequisites: []
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddItem = (field, value, setter) => {
    if (value.trim()) {
      setFormData(prev => ({
        ...prev,
        [field]: [...prev[field], value.trim()]
      }));
      setter('');
    }
  };

  const handleRemoveItem = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  const handleAddAction = () => {
    if (currentAction.name && currentAction.description && currentAction.whenToUse) {
      setFormData(prev => ({
        ...prev,
        actions: [...prev.actions, { ...currentAction }]
      }));
      setCurrentAction({
        name: '',
        description: '',
        whenToUse: '',
        estimatedTimeMinutes: 0,
        authorizationRequired: false,
        prerequisites: []
      });
      setShowActionForm(false);
    }
  };

  const handleRemoveAction = (index) => {
    setFormData(prev => ({
      ...prev,
      actions: prev.actions.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would typically send to API
    console.log('Creating NBA:', formData);
    alert('NBA created successfully!');
    navigate('/nba');
  };

  // Generate preview token
  const previewToken = formData.id && formData.priority ? 
    `[NBA:${formData.id}:P=${formData.priority}:ACTIONS=${formData.actions.length}]` : 
    '[NBA:ID:P=PRIORITY:ACTIONS=0]';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/nba')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create New NBA</h1>
          <p className="text-gray-600 mt-1">Define a new Next Best Action for agents</p>
        </div>
      </div>

      {/* CLLM Token Preview */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-blue-900 mb-1">CLLM Token Preview</div>
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

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                NBA ID <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="id"
                value={formData.id}
                onChange={handleInputChange}
                placeholder="e.g., BILLING_ISSUE"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Use uppercase with underscores</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority <span className="text-red-500">*</span>
              </label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              >
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="e.g., Billing Issue Resolution"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe when and how this NBA should be used..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>
        </div>

        {/* Prerequisites */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Prerequisites</h2>
          
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={newPrerequisite}
              onChange={(e) => setNewPrerequisite(e.target.value)}
              placeholder="e.g., customer_verified"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddItem('prerequisites', newPrerequisite, setNewPrerequisite))}
            />
            <button
              type="button"
              onClick={() => handleAddItem('prerequisites', newPrerequisite, setNewPrerequisite)}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {formData.prerequisites.map((item, index) => (
              <span key={index} className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                {item}
                <button
                  type="button"
                  onClick={() => handleRemoveItem('prerequisites', index)}
                  className="ml-2 text-gray-500 hover:text-red-600"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Success Indicators */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Success Indicators</h2>
          
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={newSuccessIndicator}
              onChange={(e) => setNewSuccessIndicator(e.target.value)}
              placeholder="e.g., issue_resolved"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddItem('successIndicators', newSuccessIndicator, setNewSuccessIndicator))}
            />
            <button
              type="button"
              onClick={() => handleAddItem('successIndicators', newSuccessIndicator, setNewSuccessIndicator)}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {formData.successIndicators.map((item, index) => (
              <span key={index} className="inline-flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                {item}
                <button
                  type="button"
                  onClick={() => handleRemoveItem('successIndicators', index)}
                  className="ml-2 text-green-600 hover:text-red-600"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Keywords */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Keywords</h2>
          
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              placeholder="e.g., billing"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddItem('keywords', newKeyword, setNewKeyword))}
            />
            <button
              type="button"
              onClick={() => handleAddItem('keywords', newKeyword, setNewKeyword)}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {formData.keywords.map((item, index) => (
              <span key={index} className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                {item}
                <button
                  type="button"
                  onClick={() => handleRemoveItem('keywords', index)}
                  className="ml-2 text-blue-600 hover:text-red-600"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Actions ({formData.actions.length})</h2>
            <button
              type="button"
              onClick={() => setShowActionForm(true)}
              className="flex items-center px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Action
            </button>
          </div>

          {/* Action List */}
          <div className="space-y-3">
            {formData.actions.map((action, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{action.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>⏱ {action.estimatedTimeMinutes} min</span>
                      {action.authorizationRequired && <span className="text-orange-600">🔒 Auth Required</span>}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveAction(index)}
                    className="p-1 text-red-600 hover:bg-red-50 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Action Form Modal */}
          {showActionForm && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Action</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Action Name</label>
                    <input
                      type="text"
                      value={currentAction.name}
                      onChange={(e) => setCurrentAction(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="e.g., Review Recent Charges"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea
                      value={currentAction.description}
                      onChange={(e) => setCurrentAction(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Describe what this action does..."
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">When to Use</label>
                    <input
                      type="text"
                      value={currentAction.whenToUse}
                      onChange={(e) => setCurrentAction(prev => ({ ...prev, whenToUse: e.target.value }))}
                      placeholder="e.g., Customer questions specific charges"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Estimated Time (minutes)</label>
                    <input
                      type="number"
                      value={currentAction.estimatedTimeMinutes}
                      onChange={(e) => setCurrentAction(prev => ({ ...prev, estimatedTimeMinutes: parseInt(e.target.value) || 0 }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={currentAction.authorizationRequired}
                      onChange={(e) => setCurrentAction(prev => ({ ...prev, authorizationRequired: e.target.checked }))}
                      className="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">Authorization Required</label>
                  </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowActionForm(false)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleAddAction}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Add Action
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/nba')}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="flex items-center px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Save className="w-5 h-5 mr-2" />
            Create NBA
          </button>
        </div>
      </form>
    </div>
  );
}

export default NBACreate;