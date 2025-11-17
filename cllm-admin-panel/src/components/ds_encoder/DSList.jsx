// src/pages/StructuredDataList.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Eye, Trash2, Search, Filter, Zap, Copy, CheckCircle2 } from 'lucide-react';

// Mock data for structured data configs
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
    exampleOutput: '[KB_CATALOG:2]\n [KB:PROD-001:WIRELESS_HEADPHONES:DESCRIPTION=HIGH-QUALITY_BLUETOOTH_HEADPHONES_WITH_NOISE_CANCELLATION:PRICE=199.99:CATEGORY=ELECTRONICS:BRAND=TECHBRAND:IN_STOCK=True]\n [KB:PROD-002:LAPTOP_STAND:DESCRIPTION=ERGONOMIC_ADJUSTABLE_LAPTOP_STAND:PRICE=49.99:CATEGORY=ACCESSORIES:BRAND=ERGOTECH:IN_STOCK=True]\n]'
  },
  {
    id: 'cfg-002',
    name: 'Service Plans',
    description: 'Compression for warranty and service plan offerings',
    dataType: 'ServicePlan',
    status: 'active',
    compressionRatio: 0.92,
    requiredFields: ['plan_id', 'plan_name'],
    fieldImportance: {
      coverage_details: 0.8,
      monthly_cost: 1.0,
      duration_months: 1.0,
      features: 0.5
    },
    excludedFields: ['commission_rate', 'partner_id'],
    autoDetect: true,
    importanceThreshold: 0.6,
    maxDescriptionLength: 150,
    preserveStructure: true,
    itemCount: 45,
    avgOriginalSize: 680,
    avgCompressedSize: 54,
    updatedAt: '2025-01-10T14:20:00Z',
    exampleOutput: '[KB_CATALOG:3]\n [KB:PLAN-001:EXTENDED_WARRANTY:MONTHLY_COST=9.99:DURATION_MONTHS=24:COVERAGE_DETAILS=COMPREHENSIVE_COVERAGE]\n [KB:PLAN-002:PREMIUM_SUPPORT:MONTHLY_COST=14.99:DURATION_MONTHS=12:COVERAGE_DETAILS=24/7_PRIORITY_SUPPORT]\n [KB:PLAN-003:BASIC_PROTECTION:MONTHLY_COST=4.99:DURATION_MONTHS=12:COVERAGE_DETAILS=STANDARD_COVERAGE]\n]'
  },
  {
    id: 'cfg-003',
    name: 'Promotion Codes',
    description: 'Active promotions and discount codes for customer service',
    dataType: 'Promotion',
    status: 'draft',
    compressionRatio: 0.81,
    requiredFields: ['code', 'discount_type'],
    fieldImportance: {
      discount_value: 1.0,
      valid_until: 1.0,
      min_purchase: 0.8,
      description: 0.5
    },
    excludedFields: ['internal_code', 'cost_center'],
    autoDetect: false,
    importanceThreshold: 0.5,
    maxDescriptionLength: 100,
    preserveStructure: true,
    itemCount: 28,
    avgOriginalSize: 320,
    avgCompressedSize: 61,
    updatedAt: '2025-01-08T09:15:00Z',
    exampleOutput: '[KB_CATALOG:2]\n [KB:PROMO-SAVE20:20_PERCENT_OFF:DISCOUNT_VALUE=20:VALID_UNTIL=2025-02-28:MIN_PURCHASE=50.00]\n [KB:PROMO-SHIP10:FREE_SHIPPING:DISCOUNT_VALUE=10:VALID_UNTIL=2025-01-31:MIN_PURCHASE=25.00]\n]'
  }
];

function StructuredDataList() {
  const navigate = useNavigate();
  const [configs, setConfigs] = useState(mockConfigs);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [copiedId, setCopiedId] = useState(null);

  // Filter configs
  const filteredConfigs = configs.filter(config => {
    const matchesSearch = config.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.dataType.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'ALL' || config.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this configuration?')) {
      setConfigs(configs.filter(config => config.id !== id));
    }
  };

  const handleCopyExample = (id, example) => {
    navigator.clipboard.writeText(example);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const StatusBadge = ({ status }) => {
    const styles = {
      active: 'bg-green-100 text-green-700',
      draft: 'bg-gray-100 text-gray-700',
      archived: 'bg-red-100 text-red-700'
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const totalItemsCompressed = configs.reduce((sum, config) => sum + config.itemCount, 0);
  const avgCompressionRatio = configs.reduce((sum, config) => sum + config.compressionRatio, 0) / configs.length;
  const totalBytesSaved = configs.reduce((sum, config) => 
    sum + (config.avgOriginalSize - config.avgCompressedSize) * config.itemCount, 0
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Structured Data Encoder</h1>
          <p className="text-gray-600 mt-1">
            Manage compression configurations for catalogs and structured data
          </p>
        </div>
        <button
          onClick={() => navigate('/ds_encoder/create')}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
        >
          <Plus className="w-5 h-5 mr-2" />
          Create Config
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{configs.length}</div>
          <div className="text-sm text-gray-600">Total Configs</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-primary-600">
            {totalItemsCompressed.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Items Compressed</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-green-600">
            {(avgCompressionRatio * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-600">Avg Compression</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">
            {(totalBytesSaved / 1024 / 1024).toFixed(1)}MB
          </div>
          <div className="text-sm text-gray-600">Space Saved</div>
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
              placeholder="Search configs by name, type, or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
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

      {/* Config Cards */}
      <div className="space-y-4">
        {filteredConfigs.map((config) => (
          <div key={config.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="p-6">
              {/* Header Row */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{config.name}</h3>
                    <StatusBadge status={config.status} />
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                      {config.dataType}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{config.description}</p>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>ID: {config.id}</span>
                    <span>•</span>
                    <span>Updated: {new Date(config.updatedAt).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => navigate(`/ds_encoder/view/${config.id}`)}
                    className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => navigate(`/ds_encoder/edit/${config.id}`)}
                    className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(config.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Items</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {config.itemCount.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Compression</div>
                  <div className="text-lg font-semibold text-green-600">
                    {(config.compressionRatio * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Original Size</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {config.avgOriginalSize}B
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Compressed</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {config.avgCompressedSize}B
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Fields</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {Object.keys(config.fieldImportance).length + config.requiredFields.length}
                  </div>
                </div>
              </div>

              {/* Configuration Summary */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 text-sm">
                <div>
                  <div className="font-medium text-gray-700 mb-2">Required Fields:</div>
                  <div className="flex flex-wrap gap-1">
                    {config.requiredFields.map(field => (
                      <span key={field} className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-mono">
                        {field}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="font-medium text-gray-700 mb-2">Excluded Fields:</div>
                  <div className="flex flex-wrap gap-1">
                    {config.excludedFields.length > 0 ? (
                      config.excludedFields.map(field => (
                        <span key={field} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-mono">
                          {field}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-400 text-xs">None</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Compressed Output Example */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium text-gray-700 text-sm">Compressed Output Example:</div>
                  <button
                    onClick={() => handleCopyExample(config.id, config.exampleOutput)}
                    className="flex items-center space-x-1 px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 rounded transition-colors"
                  >
                    {copiedId === config.id ? (
                      <>
                        <CheckCircle2 className="w-3 h-3 text-green-600" />
                        <span className="text-green-600">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
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

              {/* Settings Row */}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 text-xs text-gray-600">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-1">
                    <Zap className="w-3 h-3" />
                    <span>Auto-detect: {config.autoDetect ? 'On' : 'Off'}</span>
                  </div>
                  {config.autoDetect && (
                    <span>Threshold: {config.importanceThreshold.toFixed(1)}</span>
                  )}
                  <span>Max length: {config.maxDescriptionLength || 'Unlimited'}</span>
                  <span>Structure: {config.preserveStructure ? 'Preserved' : 'Flattened'}</span>
                </div>
                <button
                  onClick={() => navigate(`/components/structured-data/test/${config.id}`)}
                  className="flex items-center space-x-1 px-3 py-1 bg-primary-50 text-primary-600 rounded hover:bg-primary-100 transition-colors"
                >
                  <Zap className="w-3 h-3" />
                  <span>Test Compression</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredConfigs.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <p className="text-gray-500">No configurations found matching your criteria.</p>
          <button
            onClick={() => navigate('/components/structured-data/create')}
            className="mt-4 text-primary-600 hover:text-primary-700 font-medium"
          >
            Create your first configuration
          </button>
        </div>
      )}
    </div>
  );
}

export default StructuredDataList;