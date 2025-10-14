// src/components/prompts/PromptTester.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Play, RotateCcw, CheckCircle, XCircle } from 'lucide-react';
import { mockPrompts } from '../../utils/mockPromptData';

function PromptTester() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState(null);
  const [testInput, setTestInput] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const sampleTranscripts = [
    {
      id: 1,
      name: 'Billing Dispute',
      text: `Agent: Hello, thank you for calling. How can I help you today?
Customer: Hi, I'm looking at my bill and there's a charge for $49.99 that I don't recognize. I didn't authorize this.
Agent: I understand your concern. Let me help you with that.
Customer: It showed up on my card yesterday. I want to know what this is for.
Agent: I'll review your recent charges right away.`
    },
    {
      id: 2,
      name: 'Technical Support',
      text: `Agent: Thank you for calling technical support. How can I assist you?
Customer: My internet has been down since this morning. I've tried restarting the router but nothing works.
Agent: I'm sorry to hear that. Let me run some diagnostics.
Customer: It's really frustrating because I need to work from home today.
Agent: I completely understand. Let's get this resolved quickly.`
    },
    {
      id: 3,
      name: 'Account Update',
      text: `Agent: Hello! How can I help you today?
Customer: Hi, I recently moved and need to update my address on file.
Agent: No problem! I can help you with that.
Customer: Also, I'd like to update my email address while we're at it.
Agent: Absolutely, I can update both for you.`
    }
  ];

  useEffect(() => {
    const foundPrompt = mockPrompts.find(p => p.id === id);
    if (foundPrompt) {
      setPrompt(foundPrompt);
      // Set default test input
      if (foundPrompt.type === 'user') {
        setTestInput(sampleTranscripts[0].text);
      }
    }
  }, [id]);

  const handleTest = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      // Mock response
      const mockResponse = {
        success: true,
        originalPromptTokens: prompt.originalTokens,
        compressedPromptTokens: prompt.compressedTokens,
        inputTokens: Math.ceil(testInput.split(/\s+/).length * 1.3),
        totalTokensTraditional: prompt.originalTokens + Math.ceil(testInput.split(/\s+/).length * 1.3),
        totalTokensCLLM: prompt.compressedTokens + Math.ceil(testInput.split(/\s+/).length * 1.3),
        compressionRate: ((prompt.originalTokens - prompt.compressedTokens) / prompt.originalTokens * 100).toFixed(1),
        semanticPreserved: true,
        modelOutput: {
          intent: "BILLING_ISSUE",
          confidence: 0.92,
          recommended_actions: [
            { nba_id: "BILLING_ISSUE", action: "Review Recent Charges", confidence: 0.95 },
            { nba_id: "BILLING_ISSUE", action: "Initiate Dispute Process", confidence: 0.88 }
          ],
          reasoning: "Customer explicitly mentioned unrecognized charge and did not authorize it, indicating a billing dispute requiring immediate investigation."
        }
      };

      setTestResult(mockResponse);
      setIsLoading(false);
    }, 1500);
  };

  const handleReset = () => {
    setTestInput('');
    setTestResult(null);
  };

  const loadSample = (sample) => {
    setTestInput(sample.text);
    setTestResult(null);
  };

  if (!prompt) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Prompt Not Found</h2>
        <p className="text-gray-600 mb-6">The prompt you're looking for doesn't exist.</p>
        <button
          onClick={() => navigate('/prompts')}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Back to Prompts
        </button>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold text-gray-900">Test Prompt</h1>
          <p className="text-gray-600 mt-1">{prompt.name}</p>
        </div>
      </div>

      {/* Prompt Info */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-600">Feature</div>
            <div className="text-lg font-semibold text-gray-900">{prompt.feature}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Type</div>
            <div className="text-lg font-semibold text-gray-900 capitalize">{prompt.type}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Compressed Token</div>
            <code className="text-sm bg-gray-100 px-2 py-1 rounded text-gray-800">
              {prompt.compressedToken}
            </code>
          </div>
          <div>
            <div className="text-sm text-gray-600">Compression Rate</div>
            <div className="text-lg font-semibold text-green-600">{prompt.compressionRate}%</div>
          </div>
        </div>
      </div>

      {/* Test Input */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Test Input</h2>
          <div className="flex space-x-2">
            <button
              onClick={handleReset}
              className="flex items-center px-3 py-1.5 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <RotateCcw className="w-4 h-4 mr-1" />
              Reset
            </button>
            <button
              onClick={handleTest}
              disabled={!testInput || isLoading}
              className="flex items-center px-4 py-1.5 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-4 h-4 mr-1" />
              {isLoading ? 'Testing...' : 'Run Test'}
            </button>
          </div>
        </div>

        {/* Sample Transcripts */}
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">Load Sample Transcript:</div>
          <div className="flex space-x-2">
            {sampleTranscripts.map(sample => (
              <button
                key={sample.id}
                onClick={() => loadSample(sample)}
                className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                {sample.name}
              </button>
            ))}
          </div>
        </div>

        <textarea
          value={testInput}
          onChange={(e) => setTestInput(e.target.value)}
          placeholder="Enter test transcript or conversation here..."
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
        />
      </div>

      {/* Test Results */}
      {testResult && (
        <div className="space-y-4">
          {/* Compression Stats */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-4">
              {testResult.success ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <XCircle className="w-6 h-6 text-red-600" />
              )}
              <h2 className="text-lg font-semibold text-gray-900">
                {testResult.success ? 'Test Successful' : 'Test Failed'}
              </h2>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Traditional Total</div>
                <div className="text-2xl font-bold text-red-600">{testResult.totalTokensTraditional}</div>
                <div className="text-xs text-gray-500">tokens</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">CLLM Total</div>
                <div className="text-2xl font-bold text-green-600">{testResult.totalTokensCLLM}</div>
                <div className="text-xs text-gray-500">tokens</div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Tokens Saved</div>
                <div className="text-2xl font-bold text-blue-600">
                  {testResult.totalTokensTraditional - testResult.totalTokensCLLM}
                </div>
                <div className="text-xs text-gray-500">tokens</div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="text-xs text-green-700 mb-1">Compression</div>
                <div className="text-2xl font-bold text-green-600">{testResult.compressionRate}%</div>
                <div className="text-xs text-green-700">rate</div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-green-900">
                  Semantic meaning preserved: {testResult.semanticPreserved ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>

          {/* Model Output */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Model Output</h2>
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
              {JSON.stringify(testResult.modelOutput, null, 2)}
            </pre>
          </div>

          {/* Token Breakdown */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Token Breakdown</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between py-2 border-b border-gray-200">
                <span className="text-gray-600">Prompt (Original):</span>
                <span className="font-medium text-red-600">{testResult.originalPromptTokens} tokens</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-200">
                <span className="text-gray-600">Prompt (Compressed):</span>
                <span className="font-medium text-green-600">{testResult.compressedPromptTokens} tokens</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-200">
                <span className="text-gray-600">Input (Transcript):</span>
                <span className="font-medium text-gray-900">{testResult.inputTokens} tokens</span>
              </div>
              <div className="flex justify-between py-2 pt-2 font-semibold">
                <span className="text-gray-900">Total Saved:</span>
                <span className="text-blue-600">
                  {testResult.totalTokensTraditional - testResult.totalTokensCLLM} tokens
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PromptTester;