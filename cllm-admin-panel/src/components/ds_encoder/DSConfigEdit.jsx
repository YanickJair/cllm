// src/pages/StructuredDataEdit.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  ArrowLeft, 
  Save, 
  Trash2, 
  Plus, 
  X, 
  Info,
  Copy,
  CheckCircle2,
  Zap
} from 'lucide-react';

// Mock data - in real app, this would come from API
const mockConfigs = [
  {
    id: 'cfg-001',
    name: 'Product Catalog',
    description: 'Compression config for product catalog with pricing and inventory',
    dataType: 'Product',
    status: 'active',
    compressionRatio: 0.87,
    requiredFields: ['id', 'name', 'price'],
    fieldImportance: {
      description: 0.8,
      price: 1.0,
      category: 0.8,
      brand: 0.5,
      in_stock: 0.8
    },
    excludedFields: ['internal_notes', 'supplier_id'],
    autoDetect: true,
    importanceThreshold: 0.5,
    maxDescriptionLength: 200,
    preserveStructure: true,
    itemCount: 1250,
    avgOriginalSize: 450,
    avgCompressedSize: 58,
    updatedAt: '2025-01-15T10:30:00Z',
    createdAt: '2024-12-10T08:00:00Z',
    exampleOutput: '[KB_CATALOG:2]\n [KB:PROD-001:WIRELESS_HEADPHONES:DESCRIPTION=HIGH-QUALITY_BLUETOOTH_HEADPHONES_WITH_NOISE_CANCELLATION:PRICE=199.99:CATEGORY=ELECTRONICS:BRAND=TECHBRAND:IN_STOCK=True]\n [KB:PROD-002:LAPTOP_STAND:DESCRIPTION=ERGONOMIC_ADJUSTABLE_LAPTOP_STAND:PRICE=49.99:CATEGORY=ACCESSORIES:BRAND=ERGOTECH:IN_STOCK=True]\n]'
  }
];

function StructuredDataEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [config, setConfig] = useState(null);
  const [copied, setCopied] = useState(false);

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

  useEffect(() => {
    // Simulate loading config data
    const foundConfig = mockConfigs.find(c => c.id === id);
    if (foundConfig) {
      setConfig({ ...foundConfig });
    }
    setLoading(false);
  }, [id]);

  const handleAddRequiredField = () => {
    if (newRequiredField.trim() && !config.requiredFields.includes(newRequiredField.trim())) {
      setConfig({
        ...config,
        requiredFields: [...config.requiredFields, newRequiredField.trim()]
      });
      setNewRequiredField('');
    }
  };

  const handleRemoveRequiredField = (field) => {
    setConfig({
      ...config,
      requiredFields: config.requiredFields.filter(f => f !== field)
    });
  };

  const handleAddExcludedField = () => {
    if (newExcludedField.trim() && !config.excludedFields.includes(newExcludedField.trim())) {
      setConfig({
        ...config,
        excludedFields: [...config.excludedFields, newExcludedField.trim()]
      });
      setNewExcludedField('');
    }
  };

  const handleRemoveExcludedField = (field) => {
    setConfig({
      ...config,
      excludedFields: config.excludedFields.filter(f => f !== field)
    });
  };

  const handleAddFieldImportance = () => {
    if (newImportanceField.trim() && !(newImportanceField.trim() in config.fieldImportance)) {
      setConfig({
        ...config,
        fieldImportance: {
          ...config.fieldImportance,
          [newImportanceField.trim()]: newImportanceValue
        }
      });
      setNewImportanceField('');
      setNewImportanceValue(0.5);
    }
  };

  const handleRemoveFieldImportance = (field) => {
    const { [field]: _, ...rest } = config.fieldImportance;
    setConfig({
      ...config,
      fieldImportance: rest
    });
  };

  const handleSave = () => {
    console.log('Saving config:', config);
    alert('Configuration updated successfully!');
    navigate('/components/structured-data');
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this configuration? This action cannot be undone.')) {
      console.log('Deleting config:', id);
      alert('Configuration deleted successfully!');
      navigate('/components/structured-data');
    }
  };

  const handleCopyExample = () => {
    navigator.clipboard.writeText(config.exampleOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Configuration Not Found</h2>
        <p className="text-gray-600 mb-6">The configuration you're looking for doesn't exist.</p>
        <button
          onClick={() => navigate('/components/structured-data')}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Back to Configurations
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/components/structured-data')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{config.name}</h1>
            <p className="text-gray-600 mt-1">Edit compression configuration</p>
          </div>
        </div>
        <button
          onClick={handleDelete}
          className="flex items-center px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
        >
          <Trash2 className="w-5 h-5 mr-2" />
          Delete Config
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Items Compressed</div>
          <div className="text-2xl font-bold text-gray-900">
            {config.itemCount.toLocaleString()}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Compression Ratio</div>
          <div className="text-2xl font-bold text-green-600">
            {(config.compressionRatio * 100).toFixed(0)}%
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Avg Size Reduction</div>
          <div className="text-2xl font-bold text-gray-900">
            {config.avgOriginalSize - config.avgCompressedSize}B
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Status</div>
          <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
            config.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
          }`}>
            {config.status.charAt(0).toUpperCase() + config.status.slice(1)}
          </div>
        </div>
      </div>

      {/* Compressed Output Preview */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-sm font-medium text-blue-900 mb-1">Compressed Output Format</div>
            <div className="text-xs text-blue-700">
              {config.avgOriginalSize}B → {config.avgCompressedSize}B 
              ({(config.compressionRatio * 100).toFixed(1)}% compression)
            </div>
          </div>
          <button
            onClick={handleCopyExample}
            className="flex items-center space-x-2 px-3 py-2 bg-white text-blue-700 rounded-lg hover:bg-blue-100 transition-colors text-sm"
          >
            {copied ? (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
          <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap break-all">
            {config.exampleOutput}
          </pre>
        </div>
      </div>

      {/* Configuration Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="space-y-6">
        {/* Basic Info */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Configuration ID
              </label>
              <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-600">
                {config.id}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data Type
              </label>
              <div className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-600">
                {config.dataType}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Configuration Name *
              </label>
              <input
                type="text"
                value={config.name}
                onChange={(e) => setConfig({ ...config, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
                checked={config.autoDetect}
                onChange={(e) => setConfig({ ...config, autoDetect: e.target.checked })}
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

            {config.autoDetect && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Importance Threshold: {config.importanceThreshold.toFixed(1)}
                </label>
                <div className="flex items-center space-x-4">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.importanceThreshold}
                    onChange={(e) => setConfig({ ...config, importanceThreshold: parseFloat(e.target.value) })}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                  />
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getImportanceColor(config.importanceThreshold)}`}>
                    {getImportanceLabel(config.importanceThreshold)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Fields with importance ≥ {config.importanceThreshold.toFixed(1)} will be included
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
          {Object.keys(config.fieldImportance).length > 0 && (
            <div className="space-y-2">
              {Object.entries(config.fieldImportance).map(([field, importance]) => (
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

          {config.requiredFields.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {config.requiredFields.map((field) => (
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

          {config.excludedFields.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {config.excludedFields.map((field) => (
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
                value={config.maxDescriptionLength}
                onChange={(e) => setConfig({ ...config, maxDescriptionLength: parseInt(e.target.value) || 0 })}
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
                checked={config.preserveStructure}
                onChange={(e) => setConfig({ ...config, preserveStructure: e.target.checked })}
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

        {/* Metadata */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Metadata</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Created:</span>
              <span className="text-gray-600 ml-2">{new Date(config.createdAt).toLocaleDateString()}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Last Updated:</span>
              <span className="text-gray-600 ml-2">{new Date(config.updatedAt).toLocaleDateString()}</span>
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
            type="button"
            onClick={() => navigate(`/components/structured-data/test/${config.id}`)}
            className="flex items-center space-x-2 px-6 py-2.5 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
          >
            <Zap className="w-5 h-5" />
            <span>Test Compression</span>
          </button>
          <button
            type="submit"
            className="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
          >
            <Save className="w-5 h-5" />
            <span>Save Changes</span>
          </button>
        </div>
      </form>
    </div>
  );
}

export default StructuredDataEdit;