// src/components/prompts/PromptEditor.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Zap } from 'lucide-react';
import { mockPrompts, features, promptTypes } from '../../utils/mockPromptData';

function PromptEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [formData, setFormData] = useState({
    id: '',
    feature: 'NBA',
    type: 'system',
    name: '',
    description: '',
    originalText: '',
    compressedToken: '',
    version: '1.0',
    status: 'draft'
  });

  useEffect(() => {
    if (isEdit) {
      const prompt = mockPrompts.find(p => p.id === id);
      if (prompt) {
        setFormData(prompt);
      }
    }
  }, [id, isEdit]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Saving prompt:', formData);
    alert(isEdit ? 'Prompt updated successfully!' : 'Prompt created successfully!');
    navigate('/prompts');
  };

  // Calculate estimated token counts
  const estimatedOriginalTokens = Math.ceil(formData.originalText.split(/\s+/).length * 1.3);
  const estimatedCompressedTokens = formData.compressedToken.split(/\s+/).length;
  const compressionRate = estimatedOriginalTokens > 0 
    ? ((estimatedOriginalTokens - estimatedCompressedTokens) / estimatedOriginalTokens * 100).toFixed(1)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/prompts')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {isEdit ? 'Edit Prompt' : 'Create New Prompt'}
          </h1>
          <p className="text-gray-600 mt-1">
            {isEdit ? 'Update prompt details and compression token' : 'Define a new prompt for CLLM compression'}
          </p>
        </div>
      </div>

      {/* Compression Preview */}
      {formData.originalText && formData.compressedToken && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-green-600" />
              <div>
                <div className="text-sm font-medium text-green-900">Compression Estimate</div>
                <div className="text-xs text-green-700 mt-1">
                  {estimatedOriginalTokens} → {estimatedCompressedTokens} tokens
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-green-600">{compressionRate}%</div>
              <div className="text-xs text-green-700">Estimated Rate</div>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prompt ID <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="id"
                value={formData.id}
                onChange={handleInputChange}
                placeholder="e.g., nba_system_prompt"
                disabled={isEdit}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-gray-100"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Version
              </label>
              <input
                type="text"
                name="version"
                value={formData.version}
                onChange={handleInputChange}
                placeholder="e.g., 1.0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Feature <span className="text-red-500">*</span>
              </label>
              <select
                name="feature"
                value={formData.feature}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              >
                {features.map(f => (
                  <option key={f.id} value={f.id}>{f.name}</option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">Which feature does this prompt belong to?</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type <span className="text-red-500">*</span>
              </label>
              <select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              >
                {promptTypes.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g., NBA Agent System Prompt"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Brief description of what this prompt does..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="testing">Testing</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>

        {/* Original Prompt Text */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Original Prompt Text</h2>
          <p className="text-sm text-gray-600 mb-4">
            The full text that will be compressed. This is what gets sent to the LLM traditionally.
          </p>
          
          <textarea
            name="originalText"
            value={formData.originalText}
            onChange={handleInputChange}
            placeholder="Enter the full prompt text here..."
            rows={12}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
            required
          />
          
          <div className="mt-2 text-xs text-gray-500">
            Estimated tokens: {estimatedOriginalTokens}
          </div>
        </div>

        {/* Compressed Token */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Compressed CLLM Token</h2>
          <p className="text-sm text-gray-600 mb-4">
            The semantic token that represents this prompt after CLLM compression.
          </p>
          
          <input
            type="text"
            name="compressedToken"
            value={formData.compressedToken}
            onChange={handleInputChange}
            placeholder="e.g., [REF:NBA_AGENT_V1:1.0]"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono"
            required
          />
          
          <div className="mt-2 text-xs text-gray-500">
            Estimated tokens: {estimatedCompressedTokens}
          </div>

          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs text-blue-800">
              <span className="font-semibold">Tip:</span> Use descriptive tokens like [REF:FEATURE_NAME_VERSION] for system prompts
              or [REQ:ACTION] for user instructions. The token should be unique and meaningful.
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/prompts')}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="flex items-center px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Save className="w-5 h-5 mr-2" />
            {isEdit ? 'Update Prompt' : 'Create Prompt'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default PromptEditor;