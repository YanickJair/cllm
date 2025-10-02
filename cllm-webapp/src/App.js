import React, { useState } from 'react';
import { Layers, Database, Cpu, Zap, GitBranch, Brain, FileText, Settings } from 'lucide-react';

const DCLLMArchitecture = () => {
  const [selectedLayer, setSelectedLayer] = useState('compression');

  const architectureLayers = {
    compression: {
      title: "1. Compression Layer",
      icon: FileText,
      color: "blue",
      components: [
        {
          name: "Semantic Encoder",
          description: "Converts natural language to semantic primitives",
          details: [
            "Token → Meaning mapping",
            "Preserves intent, removes redundancy",
            "Example: 'please' + 'could you' + 'kindly' → [POLITE_REQUEST]",
            "Compression: ~40% for typical prompts"
          ]
        },
        {
          name: "Statistical Compressor",
          description: "Pattern recognition and frequency encoding",
          details: [
            "Build domain-specific dictionaries",
            "N-gram pattern detection",
            "Huffman encoding for common sequences",
            "Compression: Additional 25%"
          ]
        },
        {
          name: "Mathematical Optimizer",
          description: "Entropy coding and optimal bit packing",
          details: [
            "Arithmetic coding for final pass",
            "Delta encoding for similar sequences",
            "Variable-length encoding",
            "Compression: Additional 15%"
          ]
        }
      ]
    },
    tokenization: {
      title: "2. Compressed Tokenization",
      icon: Layers,
      color: "purple",
      components: [
        {
          name: "Hierarchical Token Space",
          description: "Multi-level token vocabulary",
          details: [
            "Level 0: Semantic primitives (1000 tokens)",
            "Level 1: Compressed phrases (5000 tokens)",
            "Level 2: Domain patterns (10000 tokens)",
            "Level 3: Reference pointers (unlimited)"
          ]
        },
        {
          name: "Reference Resolution",
          description: "Pointer-based template system",
          details: [
            "Template IDs as special tokens",
            "Lazy loading: fetch only when needed",
            "Cache frequently used templates",
            "Support nested references"
          ]
        },
        {
          name: "Delta Token Encoding",
          description: "Difference-based representation",
          details: [
            "Store: [BASE_REF] + [DELTA_OPS]",
            "Operations: INSERT, DELETE, MODIFY, KEEP",
            "Positional encoding preserved",
            "Lossless reconstruction possible"
          ]
        }
      ]
    },
    model: {
      title: "3. CLLM Model Core",
      icon: Brain,
      color: "green",
      components: [
        {
          name: "Compressed Embeddings",
          description: "Direct embedding of compressed tokens",
          details: [
            "No decompression step",
            "Embeddings trained on compressed space",
            "Semantic similarity preserved",
            "Dimension: 768-2048 (same as standard LLM)"
          ]
        },
        {
          name: "Hierarchical Attention",
          description: "Multi-scale attention mechanism",
          details: [
            "Coarse attention on semantic level",
            "Fine attention on detail level",
            "Cross-level attention for context",
            "Reference-aware attention masking"
          ]
        },
        {
          name: "Differential Processing",
          description: "Process deltas without expansion",
          details: [
            "Base context loaded once",
            "Apply delta operations in attention space",
            "Incremental state updates",
            "Memory efficient: O(delta) not O(full)"
          ]
        }
      ]
    },
    training: {
      title: "4. Training Pipeline",
      icon: Settings,
      color: "orange",
      components: [
        {
          name: "Data Generation",
          description: "Create compressed training pairs",
          details: [
            "Start with standard LLM dataset",
            "Apply compression pipeline",
            "Generate: [compressed_input, output] pairs",
            "Preserve quality with validation"
          ]
        },
        {
          name: "Two-Stage Training",
          description: "Progressive learning approach",
          details: [
            "Stage 1: Compression-aware pretraining",
            "Stage 2: Differential fine-tuning",
            "Use existing LLM as teacher",
            "Distillation from uncompressed model"
          ]
        },
        {
          name: "Quality Gates",
          description: "Ensure semantic preservation",
          details: [
            "Lossless reconstruction test",
            "Semantic similarity scoring",
            "Task performance benchmarks",
            "Automatic rollback on degradation"
          ]
        }
      ]
    },
    inference: {
      title: "5. Inference Engine",
      icon: Zap,
      color: "pink",
      components: [
        {
          name: "Streaming Compression",
          description: "Real-time input compression",
          details: [
            "Compress as tokens arrive",
            "Template matching on-the-fly",
            "Incremental delta calculation",
            "Sub-millisecond latency"
          ]
        },
        {
          name: "Context Management",
          description: "Optimized memory handling",
          details: [
            "Store base templates in fast memory",
            "Delta cache with LRU eviction",
            "Lazy decompression only if needed",
            "Support for massive context windows"
          ]
        },
        {
          name: "Output Generation",
          description: "Flexible output formats",
          details: [
            "Can output compressed or standard",
            "Streaming generation",
            "Adaptive compression for output",
            "Backward compatible mode"
          ]
        }
      ]
    },
    repository: {
      title: "6. Template Repository",
      icon: Database,
      color: "cyan",
      components: [
        {
          name: "Distributed Storage",
          description: "High-performance template store",
          details: [
            "Key-value store for templates",
            "Versioning and immutability",
            "Global CDN distribution",
            "Sub-5ms retrieval time"
          ]
        },
        {
          name: "Smart Indexing",
          description: "Fast template matching",
          details: [
            "Semantic similarity search",
            "Fuzzy matching with thresholds",
            "Automatic clustering",
            "Usage-based prioritization"
          ]
        },
        {
          name: "Learning System",
          description: "Continuous optimization",
          details: [
            "Auto-generate templates from usage",
            "A/B test compression strategies",
            "Domain-specific dictionaries",
            "Feedback loop from model"
          ]
        }
      ]
    }
  };

  const Layer = architectureLayers[selectedLayer];
  const IconComponent = Layer.icon;

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-3">CLLM Architecture</h1>
          <p className="text-slate-300 text-xl">Compressed Language Model</p>
          <p className="text-slate-400 text-sm mt-2">Native compressed processing without decompression</p>
        </div>

        {/* Architecture Overview Diagram */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-700 rounded-2xl p-8 mb-8 border border-slate-600">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">System Flow</h2>
          <div className="flex items-center justify-between text-white">
            <div className="flex-1 text-center">
              <div className="bg-blue-500/20 border-2 border-blue-400 rounded-xl p-4 mb-2">
                <FileText className="mx-auto mb-2" size={32} />
                <div className="font-bold">Raw Input</div>
                <div className="text-xs text-blue-200 mt-1">10,000 tokens</div>
              </div>
            </div>
            
            <div className="text-4xl text-slate-500 px-4">→</div>
            
            <div className="flex-1 text-center">
              <div className="bg-purple-500/20 border-2 border-purple-400 rounded-xl p-4 mb-2">
                <Layers className="mx-auto mb-2" size={32} />
                <div className="font-bold">Compression</div>
                <div className="text-xs text-purple-200 mt-1">3-stage pipeline</div>
              </div>
            </div>
            
            <div className="text-4xl text-slate-500 px-4">→</div>
            
            <div className="flex-1 text-center">
              <div className="bg-green-500/20 border-2 border-green-400 rounded-xl p-4 mb-2">
                <Brain className="mx-auto mb-2" size={32} />
                <div className="font-bold">CLLM</div>
                <div className="text-xs text-green-200 mt-1">Native processing</div>
              </div>
            </div>
            
            <div className="text-4xl text-slate-500 px-4">→</div>
            
            <div className="flex-1 text-center">
              <div className="bg-pink-500/20 border-2 border-pink-400 rounded-xl p-4 mb-2">
                <Zap className="mx-auto mb-2" size={32} />
                <div className="font-bold">Output</div>
                <div className="text-xs text-pink-200 mt-1">Fast generation</div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <div className="inline-block bg-slate-900/50 rounded-lg px-6 py-3 border border-slate-600">
              <div className="text-green-400 font-bold text-lg">70% Token Reduction</div>
              <div className="text-slate-300 text-sm mt-1">No decompression required</div>
            </div>
          </div>
        </div>

        {/* Layer Selection */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
          {Object.entries(architectureLayers).map(([key, layer]) => {
            const Icon = layer.icon;
            const isSelected = selectedLayer === key;
            return (
              <button
                key={key}
                onClick={() => setSelectedLayer(key)}
                className={`p-4 rounded-xl border-2 transition-all ${
                  isSelected
                    ? `bg-${layer.color}-500/30 border-${layer.color}-400 shadow-lg`
                    : 'bg-slate-800/50 border-slate-600 hover:border-slate-500'
                }`}
              >
                <Icon className={`mx-auto mb-2 ${isSelected ? `text-${layer.color}-400` : 'text-slate-400'}`} size={28} />
                <div className={`text-sm font-semibold ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                  {layer.title.split('.')[1]}
                </div>
              </button>
            );
          })}
        </div>

        {/* Layer Details */}
        <div className="bg-slate-800 rounded-2xl p-8 border border-slate-600">
          <div className="flex items-center gap-4 mb-6">
            <div className={`bg-${Layer.color}-500/20 p-4 rounded-xl border-2 border-${Layer.color}-400`}>
              <IconComponent className={`text-${Layer.color}-400`} size={40} />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">{Layer.title}</h2>
              <p className="text-slate-400 mt-1">Core architectural component</p>
            </div>
          </div>

          <div className="space-y-6">
            {Layer.components.map((component, idx) => (
              <div key={idx} className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                <h3 className="text-xl font-bold text-white mb-2">{component.name}</h3>
                <p className="text-slate-300 mb-4">{component.description}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {component.details.map((detail, detailIdx) => (
                    <div key={detailIdx} className="flex items-start gap-3">
                      <div className={`w-2 h-2 mt-2 rounded-full bg-${Layer.color}-400 flex-shrink-0`} />
                      <div className="text-sm text-slate-300">{detail}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Technical Specifications */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-900/30 to-purple-900/30 rounded-xl p-6 border border-blue-500/30">
            <h3 className="text-xl font-bold text-white mb-4">Key Innovations</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-green-400 font-bold">1</span>
                </div>
                <div className="text-slate-300">
                  <strong className="text-white">No Decompression Step:</strong> Model processes compressed tokens directly
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-green-400 font-bold">2</span>
                </div>
                <div className="text-slate-300">
                  <strong className="text-white">Hierarchical Attention:</strong> Multi-scale processing for efficiency
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-green-400 font-bold">3</span>
                </div>
                <div className="text-slate-300">
                  <strong className="text-white">Differential Learning:</strong> Model learns compressed representations
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-green-400 font-bold">4</span>
                </div>
                <div className="text-slate-300">
                  <strong className="text-white">Template System:</strong> Reference-based memory optimization
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-900/30 to-teal-900/30 rounded-xl p-6 border border-green-500/30">
            <h3 className="text-xl font-bold text-white mb-4">Performance Targets</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-300 text-sm">Compression Ratio</span>
                  <span className="text-white font-bold">70%</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-green-500 to-emerald-400" style={{width: '70%'}} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-300 text-sm">Processing Speed</span>
                  <span className="text-white font-bold">3x faster</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-400" style={{width: '85%'}} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-300 text-sm">Memory Efficiency</span>
                  <span className="text-white font-bold">60% less</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-purple-500 to-pink-400" style={{width: '60%'}} />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-300 text-sm">Quality Preservation</span>
                  <span className="text-white font-bold">99.5%</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-yellow-500 to-orange-400" style={{width: '99.5%'}} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Research Directions */}
        <div className="mt-8 bg-gradient-to-r from-indigo-900/30 to-purple-900/30 rounded-xl p-6 border border-indigo-500/30">
          <h3 className="text-xl font-bold text-white mb-4">Open Research Questions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-indigo-400 font-semibold mb-2">🤔 Compression Limits</div>
              <div className="text-slate-300">How much can we compress before semantic loss becomes measurable?</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-purple-400 font-semibold mb-2">🧠 Training Strategy</div>
              <div className="text-slate-300">Should we fine-tune or train from scratch? What's optimal?</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-pink-400 font-semibold mb-2">⚡ Attention Mechanism</div>
              <div className="text-slate-300">How to design attention for hierarchical compressed tokens?</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-cyan-400 font-semibold mb-2">🔄 Bidirectional Compression</div>
              <div className="text-slate-300">Can the model output compressed format for chain-of-thought?</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DCLLMArchitecture;