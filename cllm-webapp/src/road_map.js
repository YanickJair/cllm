import React, { useState } from 'react';
import { CheckCircle, Circle, Clock, Zap, FileText, Brain, Rocket, TrendingUp } from 'lucide-react';

const CLLMRoadmap = () => {
  const [selectedPhase, setSelectedPhase] = useState('phase1');

  const roadmap = {
    phase1: {
      title: "Phase 1: Foundation & Compression Design",
      duration: "2-3 weeks",
      status: "current",
      icon: FileText,
      color: "blue",
      objective: "Define compression format and build encoder/decoder",
      deliverables: [
        {
          name: "Compression Format Specification",
          tasks: [
            "Define semantic primitive vocabulary (1000 core concepts)",
            "Design token encoding schema [TYPE:VALUE:METADATA]",
            "Create compression ratio calculator",
            "Document lossless reconstruction rules"
          ],
          priority: "critical",
          status: "not-started"
        },
        {
          name: "Three-Stage Compression Pipeline",
          tasks: [
            "Build Semantic Encoder (intent preservation)",
            "Build Statistical Compressor (pattern recognition)",
            "Build Mathematical Optimizer (entropy coding)",
            "Implement quality gates for each stage"
          ],
          priority: "critical",
          status: "not-started"
        },
        {
          name: "Encoder/Decoder Implementation",
          tasks: [
            "Python implementation of full pipeline",
            "Unit tests for lossless reconstruction",
            "Benchmark compression ratios on real data",
            "Create visualization tool for compression"
          ],
          priority: "high",
          status: "not-started"
        },
        {
          name: "Initial Dataset Creation",
          tasks: [
            "Collect 10K diverse prompts (customer support, coding, general)",
            "Compress all prompts through pipeline",
            "Validate quality preservation",
            "Generate compressed-to-output pairs"
          ],
          priority: "high",
          status: "not-started"
        }
      ],
      successCriteria: [
        "70%+ compression ratio achieved",
        "99%+ semantic similarity maintained",
        "Lossless reconstruction validated",
        "10K+ compressed examples generated"
      ]
    },
    phase2: {
      title: "Phase 2: Model Architecture Design",
      duration: "3-4 weeks",
      status: "upcoming",
      icon: Brain,
      color: "purple",
      objective: "Design CLLM architecture and tokenization layer",
      deliverables: [
        {
          name: "Compressed Tokenizer",
          tasks: [
            "Design hierarchical token vocabulary",
            "Implement compressed token embeddings",
            "Build reference resolution system",
            "Create token position encoding for compressed space"
          ],
          priority: "critical",
          status: "not-started"
        },
        {
          name: "Hierarchical Attention Mechanism",
          tasks: [
            "Design multi-scale attention layers",
            "Implement coarse-to-fine attention",
            "Build cross-level attention masks",
            "Optimize for compressed input"
          ],
          priority: "critical",
          status: "not-started"
        },
        {
          name: "Model Architecture",
          tasks: [
            "Choose base architecture (Transformer variant)",
            "Design layer structure for compressed processing",
            "Implement differential processing modules",
            "Build memory-efficient context manager"
          ],
          priority: "high",
          status: "not-started"
        },
        {
          name: "Architecture Validation",
          tasks: [
            "Implement toy model (1M parameters)",
            "Test on small compressed dataset",
            "Validate attention patterns",
            "Benchmark memory usage vs standard LLM"
          ],
          priority: "high",
          status: "not-started"
        }
      ],
      successCriteria: [
        "Toy model processes compressed input",
        "Attention mechanism validated",
        "60%+ memory reduction vs baseline",
        "Architecture scales to production size"
      ]
    },
    phase3: {
      title: "Phase 3: Training Pipeline & Initial Model",
      duration: "4-6 weeks",
      status: "upcoming",
      icon: Zap,
      color: "green",
      objective: "Train first CLLM and validate performance",
      deliverables: [
        {
          name: "Training Data Pipeline",
          tasks: [
            "Generate 100K compressed training examples",
            "Implement data augmentation for compressed space",
            "Build validation set with quality metrics",
            "Create streaming data loader for compressed format"
          ],
          priority: "critical",
          status: "not-started"
        },
        {
          name: "Training Strategy",
          tasks: [
            "Design two-stage training approach",
            "Implement distillation from standard LLM",
            "Set up quality monitoring during training",
            "Configure hyperparameters and learning rate schedule"
          ],
          priority: "critical",
          status: "not-started"
        },
        {
          name: "First CLLM Model",
          tasks: [
            "Fine-tune LLAMA 7B on compressed data",
            "Train for 1-2 epochs with quality gates",
            "Benchmark against baseline LLM",
            "Evaluate on held-out test set"
          ],
          priority: "critical",
          status: "not-started"
        },
        {
          name: "Evaluation Framework",
          tasks: [
            "Build comprehensive benchmark suite",
            "Test on multiple task types",
            "Measure quality, speed, and cost metrics",
            "Generate comparison reports"
          ],
          priority: "high",
          status: "not-started"
        }
      ],
      successCriteria: [
        "CLLM matches 95%+ quality of baseline",
        "3x faster inference speed",
        "70% token reduction maintained",
        "Passes all quality gates"
      ]
    },
    phase4: {
      title: "Phase 4: Optimization & Scaling",
      duration: "6-8 weeks",
      status: "upcoming",
      icon: TrendingUp,
      color: "orange",
      objective: "Optimize for production and scale to larger models",
      deliverables: [
        {
          name: "Inference Optimization",
          tasks: [
            "Implement streaming compression",
            "Build efficient context caching",
            "Optimize attention computation",
            "Deploy on GPU/TPU infrastructure"
          ],
          priority: "high",
          status: "not-started"
        },
        {
          name: "Template Repository System",
          tasks: [
            "Build distributed template store",
            "Implement smart template matching",
            "Create auto-learning system",
            "Deploy CDN for global access"
          ],
          priority: "high",
          status: "not-started"
        },
        {
          name: "Larger Model Training",
          tasks: [
            "Scale to 13B or 30B parameters",
            "Train on 1M+ examples",
            "Fine-tune for specific domains",
            "Benchmark against GPT-3.5/4"
          ],
          priority: "medium",
          status: "not-started"
        },
        {
          name: "Performance Tuning",
          tasks: [
            "Profile and optimize bottlenecks",
            "Reduce latency to <100ms",
            "Optimize memory footprint",
            "Achieve 5x cost reduction"
          ],
          priority: "medium",
          status: "not-started"
        }
      ],
      successCriteria: [
        "Production-ready inference API",
        "Sub-100ms p99 latency",
        "5x cost savings demonstrated",
        "Scales to enterprise workloads"
      ]
    },
    phase5: {
      title: "Phase 5: Production & Ecosystem",
      duration: "8-12 weeks",
      status: "future",
      icon: Rocket,
      color: "pink",
      objective: "Launch production system and build developer ecosystem",
      deliverables: [
        {
          name: "Production Infrastructure",
          tasks: [
            "Deploy multi-region inference service",
            "Build monitoring and alerting",
            "Implement auto-scaling",
            "Set up CI/CD pipeline"
          ],
          priority: "critical",
          status: "not-started"
        },
        {
          name: "Developer SDK",
          tasks: [
            "Build Python SDK for CLLM",
            "Create JavaScript/TypeScript client",
            "Write comprehensive documentation",
            "Publish example applications"
          ],
          priority: "high",
          status: "not-started"
        },
        {
          name: "API & Platform",
          tasks: [
            "Launch public API",
            "Build developer dashboard",
            "Implement usage tracking and billing",
            "Create playground for testing"
          ],
          priority: "high",
          status: "not-started"
        },
        {
          name: "Community & Research",
          tasks: [
            "Publish research paper",
            "Open-source compression toolkit",
            "Build community around CLLM",
            "Partner with early adopters"
          ],
          priority: "medium",
          status: "not-started"
        }
      ],
      successCriteria: [
        "100+ developers using CLLM",
        "99.9% uptime achieved",
        "Research paper published",
        "Revenue-generating product"
      ]
    }
  };

  const phase = roadmap[selectedPhase];
  const PhaseIcon = phase.icon;

  const getStatusColor = (status) => {
    switch(status) {
      case 'current': return 'green';
      case 'upcoming': return 'blue';
      case 'future': return 'slate';
      default: return 'gray';
    }
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'yellow';
      default: return 'gray';
    }
  };

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-3">CLLM Development Roadmap</h1>
          <p className="text-indigo-200 text-xl">Structured Path to Production</p>
          <p className="text-indigo-300 text-sm mt-2">5 phases • 23-33 weeks • Clear deliverables</p>
        </div>

        {/* Timeline Overview */}
        <div className="mb-8 bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-6">Timeline Overview</h2>
          <div className="space-y-3">
            {Object.entries(roadmap).map(([key, p]) => {
              const Icon = p.icon;
              const statusColor = getStatusColor(p.status);
              return (
                <div 
                  key={key}
                  onClick={() => setSelectedPhase(key)}
                  className={`cursor-pointer transition-all ${
                    selectedPhase === key 
                      ? `bg-${p.color}-500/30 border-2 border-${p.color}-400` 
                      : 'bg-slate-800/50 border border-slate-600 hover:border-slate-500'
                  } rounded-lg p-4`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`bg-${p.color}-500/20 p-3 rounded-lg border border-${p.color}-400`}>
                        <Icon className={`text-${p.color}-400`} size={24} />
                      </div>
                      <div>
                        <div className="text-white font-bold text-lg">{p.title}</div>
                        <div className="text-slate-300 text-sm mt-1">{p.objective}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-${statusColor}-400 text-sm font-semibold capitalize mb-1`}>
                        {p.status}
                      </div>
                      <div className="text-slate-400 text-xs">{p.duration}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Phase Details */}
        <div className="bg-slate-800 rounded-xl p-8 border border-slate-600">
          <div className="flex items-center gap-4 mb-6">
            <div className={`bg-${phase.color}-500/20 p-4 rounded-xl border-2 border-${phase.color}-400`}>
              <PhaseIcon className={`text-${phase.color}-400`} size={40} />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-white">{phase.title}</h2>
              <p className="text-slate-300 mt-1">{phase.objective}</p>
            </div>
            <div className="text-right">
              <div className={`text-${getStatusColor(phase.status)}-400 text-sm font-bold uppercase mb-1`}>
                {phase.status}
              </div>
              <div className="text-slate-400 text-sm">{phase.duration}</div>
            </div>
          </div>

          {/* Deliverables */}
          <div className="space-y-6 mb-8">
            <h3 className="text-xl font-bold text-white">Deliverables</h3>
            {phase.deliverables.map((deliverable, idx) => (
              <div key={idx} className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-bold text-white">{deliverable.name}</h4>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold bg-${getPriorityColor(deliverable.priority)}-500/20 text-${getPriorityColor(deliverable.priority)}-300 uppercase`}>
                      {deliverable.priority}
                    </span>
                    {deliverable.status === 'completed' ? (
                      <CheckCircle className="text-green-400" size={20} />
                    ) : deliverable.status === 'in-progress' ? (
                      <Clock className="text-yellow-400" size={20} />
                    ) : (
                      <Circle className="text-slate-500" size={20} />
                    )}
                  </div>
                </div>
                
                <div className="space-y-2">
                  {deliverable.tasks.map((task, taskIdx) => (
                    <div key={taskIdx} className="flex items-start gap-3 text-sm">
                      <div className={`w-1.5 h-1.5 mt-2 rounded-full bg-${phase.color}-400 flex-shrink-0`} />
                      <div className="text-slate-300">{task}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Success Criteria */}
          <div className="bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-xl p-6 border border-green-500/30">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <CheckCircle className="text-green-400" size={24} />
              Success Criteria
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {phase.successCriteria.map((criterion, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded bg-green-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <CheckCircle className="text-green-400" size={16} />
                  </div>
                  <div className="text-slate-200">{criterion}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="mt-8 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl p-6 border border-blue-500/30">
          <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
            <Zap className="text-yellow-400" size={28} />
            Immediate Next Steps
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-blue-400 font-bold mb-2">1. Define Compression Format</div>
              <div className="text-slate-300 text-sm">
                Create the specification for how text gets compressed into semantic tokens
              </div>
              <div className="text-blue-300 text-xs mt-2">⏱️ Start: This week</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-purple-400 font-bold mb-2">2. Build Encoder Prototype</div>
              <div className="text-slate-300 text-sm">
                Implement the three-stage compression pipeline in Python
              </div>
              <div className="text-purple-300 text-xs mt-2">⏱️ Start: Week 2</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-green-400 font-bold mb-2">3. Generate Test Dataset</div>
              <div className="text-slate-300 text-sm">
                Collect and compress 1000 diverse prompts for testing
              </div>
              <div className="text-green-300 text-xs mt-2">⏱️ Start: Week 2</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-orange-400 font-bold mb-2">4. Validate Compression</div>
              <div className="text-slate-300 text-sm">
                Test lossless reconstruction and measure compression ratios
              </div>
              <div className="text-orange-300 text-xs mt-2">⏱️ Start: Week 3</div>
            </div>
          </div>
        </div>

        {/* Key Decisions Needed */}
        <div className="mt-8 bg-gradient-to-r from-red-900/30 to-pink-900/30 rounded-xl p-6 border border-red-500/30">
          <h3 className="text-2xl font-bold text-white mb-4">🎯 Key Decisions Needed</h3>
          <div className="space-y-3 text-sm">
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-red-300 font-semibold mb-2">Decision 1: Compression Format</div>
              <div className="text-slate-300">
                How do we encode semantic primitives? Token format? Hierarchy structure?
              </div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-pink-300 font-semibold mb-2">Decision 2: Training Strategy</div>
              <div className="text-slate-300">
                Fine-tune existing model or train from scratch? Which base model?
              </div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <div className="text-orange-300 font-semibold mb-2">Decision 3: Quality Thresholds</div>
              <div className="text-slate-300">
                What's acceptable quality loss? 99%? 95%? How do we measure?
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default CLLMRoadmap;