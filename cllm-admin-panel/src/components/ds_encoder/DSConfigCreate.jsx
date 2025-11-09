// src/pages/StructuredDataCreate.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Save, 
  X, 
  Plus, 
  Trash2, 
  Info,
  AlertCircle
} from 'lucide-react';

function StructuredDataCreate() {
  const navigate = useNavigate();
  
  const [config, setConfig] = useState({
    name: '',
    description: '',
    required_fields: [],
    auto_detect: true,
    importance_threshold: 0.5,
    field_importance: {},
    excluded_fields: [],
    max_description_length: 200,
    preserve_structure: true
  });

  const [newRequiredField, setNewRequiredField] = useState('');
  const [newExcludedField, setNewExcludedField] = useState('');
  const [newImportanceField, setNewImportanceField] = useState('');
  const [newImportanceValue, setNewImportanceValue] = useState(0.5);

  // Field importance presets
  const importancePresets = [
    { label: 'Critical', value: 1.0, description: 'Always include (id, name)' },
    { label: 'High', value: 0.8, description: 'Usually include (description, category)' },
    { label: 'Medium', value: 0.5, description: 'Sometimes include (tags, metadata)' },
    { label: 'Low', value: 0.2, description: 'Rarely include (timestamps, codes)' },
    { label: 'Never', value: 0.0, description: 'Never include (passwords, secrets)' }
  ];

  const handleAddRequiredField = () => {
    if (newRequiredField.trim() && !config.required_fields.includes(newRequiredField.trim())) {
      setConfig({
        ...config,
        required_fields: [...config.required_fields, newRequiredField.trim()]
      });
      setNewRequiredField('');
    }
  };

  const handleRemoveRequiredField = (field) => {
    setConfig({
      ...config,
      required_fields: config.required_fields.filter(f => f !== field)
    });
  };

  const handleAddExcludedField = () => {
    if (newExcludedField.trim() && !config.excluded_fields.includes(newExcludedField.trim())) {
      setConfig({
        ...config,
        excluded_fields: [...config.excluded_fields, newExcludedField.trim()]
      });
      setNewExcludedField('');
    }
  };

  const handleRemoveExcludedField = (field) => {
    setConfig({
      ...config,
      excluded_fields: config.excluded_fields.filter(f => f !== field)
    });
  };

  const handleAddFieldImportance = () => {
    if (newImportanceField.trim() && !(newImportanceField.trim() in config.field_importance)) {
      setConfig({
        ...config,
        field_importance: {
          ...config.field_importance,
          [newImportanceField.trim()]: newImportanceValue
        }
      });
      setNewImportanceField('');
      setNewImportanceValue(0.5);
    }
  };

  const handleRemoveFieldImportance = (field) => {
    const { [field]: _, ...rest } = config.field_importance;
    setConfig({
      ...config,
      field_importance: rest
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate
    if (!config.name.trim()) {
      alert('Please provide a configuration name');
      return;
    }

    // TODO: Send to API
    console.log('Submitting config:', config);
    
    // Navigate back
    navigate('/components/structured-data');
  };

  const getImportanceLabel = (value) => {
    const preset = importancePresets.find(p => p.value === value);
    return preset ? preset.label : value.toFixed(1);
  };

  const getImportanceColor = (value) => {
    if (value >= 0.8) return 'text-green-600 bg-green-50';
    if (value >= 0.5) return 'text-blue-600 bg-blue-50';
    if (value >= 0.2) return 'text-yellow-600 bg-yellow-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Create Compression Config
            </h1>
            <p className="mt-2 text-gray-600">
              Define how structured data should be compressed for this catalog
            </p>
          </div>
          <button
            onClick={() => navigate('/components/structured-data')}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors flex items-center space-x-2"
          >
            <X className="w-5 h-5" />
            <span>Cancel</span>
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Info */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Configuration Name *
              </label>
              <input
                type="text"
                value={config.name}
                onChange={(e) => setConfig({ ...config, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., Product Catalog Config"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={config.description}
                onChange={(e) => setConfig({ ...config, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Describe what this configuration is for..."
              />
            </div>
          </div>
        </div>

        {/* Auto-Detection Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Auto-Detection Settings</h2>
          
          <div className="space-y-6">
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="auto_detect"
                checked={config.auto_detect}
                onChange={(e) => setConfig({ ...config, auto_detect: e.target.checked })}
                className="mt-1 w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <div className="flex-1">
                <label htmlFor="auto_detect" className="block text-sm font-medium text-gray-900">
                  Enable Auto-Detection
                </label>
                <p className="text-sm text-gray-500 mt-1">
                  Automatically detect and include important fields based on threshold
                </p>
              </div>
            </div>

            {config.auto_detect && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Importance Threshold: {config.importance_threshold.toFixed(1)}
                </label>
                <div className="flex items-center space-x-4">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.importance_threshold}
                    onChange={(e) => setConfig({ ...config, importance_threshold: parseFloat(e.target.value) })}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                  />
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getImportanceColor(config.importance_threshold)}`}>
                    {getImportanceLabel(config.importance_threshold)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Fields with importance ≥ {config.importance_threshold.toFixed(1)} will be included
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Field Importance Mappings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Field Importance</h2>
              <p className="text-sm text-gray-500 mt-1">
                Define custom importance scores for specific fields
              </p>
            </div>
            <Info className="w-5 h-5 text-gray-400" />
          </div>

          {/* Importance Presets Reference */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs font-medium text-gray-700 mb-2">Importance Levels:</p>
            <div className="grid grid-cols-5 gap-2">
              {importancePresets.map((preset) => (
                <div key={preset.value} className="text-xs">
                  <span className={`inline-block px-2 py-1 rounded font-medium ${getImportanceColor(preset.value)}`}>
                    {preset.label} ({preset.value})
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Add New Field Importance */}
          <div className="flex items-end space-x-3 mb-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Field Name
              </label>
              <input
                type="text"
                value={newImportanceField}
                onChange={(e) => setNewImportanceField(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddFieldImportance())}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., price"
              />
            </div>
            <div className="w-48">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Importance
              </label>
              <select
                value={newImportanceValue}
                onChange={(e) => setNewImportanceValue(parseFloat(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                {importancePresets.map((preset) => (
                  <option key={preset.value} value={preset.value}>
                    {preset.label} ({preset.value})
                  </option>
                ))}
              </select>
            </div>
            <button
              type="button"
              onClick={handleAddFieldImportance}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Add</span>
            </button>
          </div>

          {/* Field Importance List */}
          {Object.keys(config.field_importance).length > 0 && (
            <div className="space-y-2">
              {Object.entries(config.field_importance).map(([field, importance]) => (
                <div
                  key={field}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <code className="text-sm font-mono text-gray-900">{field}</code>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImportanceColor(importance)}`}>
                      {getImportanceLabel(importance)}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveFieldImportance(field)}
                    className="text-red-600 hover:text-red-700 p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Required Fields */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Required Fields</h2>
            <p className="text-sm text-gray-500 mt-1">
              These fields will always be included regardless of importance
            </p>
          </div>

          <div className="flex items-end space-x-3 mb-4">
            <div className="flex-1">
              <input
                type="text"
                value={newRequiredField}
                onChange={(e) => setNewRequiredField(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddRequiredField())}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., id, name, product_id"
              />
            </div>
            <button
              type="button"
              onClick={handleAddRequiredField}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Add</span>
            </button>
          </div>

          {config.required_fields.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {config.required_fields.map((field) => (
                <div
                  key={field}
                  className="flex items-center space-x-2 px-3 py-2 bg-green-50 text-green-700 rounded-lg border border-green-200"
                >
                  <code className="text-sm font-mono">{field}</code>
                  <button
                    type="button"
                    onClick={() => handleRemoveRequiredField(field)}
                    className="text-green-600 hover:text-green-800"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Excluded Fields */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Excluded Fields</h2>
            <p className="text-sm text-gray-500 mt-1">
              These fields will never be included in compression
            </p>
          </div>

          <div className="flex items-end space-x-3 mb-4">
            <div className="flex-1">
              <input
                type="text"
                value={newExcludedField}
                onChange={(e) => setNewExcludedField(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddExcludedField())}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., password, secret_key, internal_notes"
              />
            </div>
            <button
              type="button"
              onClick={handleAddExcludedField}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Add</span>
            </button>
          </div>

          {config.excluded_fields.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {config.excluded_fields.map((field) => (
                <div
                  key={field}
                  className="flex items-center space-x-2 px-3 py-2 bg-red-50 text-red-700 rounded-lg border border-red-200"
                >
                  <code className="text-sm font-mono">{field}</code>
                  <button
                    type="button"
                    onClick={() => handleRemoveExcludedField(field)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Additional Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Settings</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Description Length
              </label>
              <input
                type="number"
                value={config.max_description_length}
                onChange={(e) => setConfig({ ...config, max_description_length: parseInt(e.target.value) || 0 })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                min="0"
                placeholder="200"
              />
              <p className="text-xs text-gray-500 mt-1">
                Truncate long text fields to this character limit (0 = no limit)
              </p>
            </div>

            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="preserve_structure"
                checked={config.preserve_structure}
                onChange={(e) => setConfig({ ...config, preserve_structure: e.target.checked })}
                className="mt-1 w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <div className="flex-1">
                <label htmlFor="preserve_structure" className="block text-sm font-medium text-gray-900">
                  Preserve Structure
                </label>
                <p className="text-sm text-gray-500 mt-1">
                  Keep nested dictionaries and lists in their original structure
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={() => navigate('/components/structured-data')}
            className="px-6 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
          >
            <Save className="w-5 h-5" />
            <span>Create Configuration</span>
          </button>
        </div>
      </form>
    </div>
  );
}

export default StructuredDataCreate;