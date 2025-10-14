// src/utils/mockPromptData.js

export const mockPrompts = [
  {
    id: "nba_system_prompt",
    feature: "NBA",
    type: "system",
    name: "NBA Agent System Prompt",
    description: "Core system instructions for NBA recommendation engine",
    originalText: `You are a Next Best Action recommendation system for customer service agents.
Analyze live call transcripts and recommend the top 2 most relevant actions from the provided NBA catalog. 

Your responsibilities:
- Identify customer intent from conversation context
- Consider conversation history and customer sentiment
- Match intents to appropriate NBAs based on keywords and prerequisites
- Recommend actions with confidence scores (0-1)
- Provide brief reasoning for each recommendation
- Always prioritize customer satisfaction and agent efficiency

Output Format:
Return recommendations as JSON with fields: 'intent', 'confidence', 'recommended_actions' (array), and 'reasoning'.

Quality Guidelines:
- Only recommend actions when confidence > 0.7
- Ensure prerequisites are met before recommending
- Consider conversation tone and urgency
- Provide actionable recommendations agent can immediately execute`,
    compressedToken: "[REF:NBA_AGENT_V1:1.0]",
    originalTokens: 400,
    compressedTokens: 1,
    compressionRate: 99.8,
    version: "1.0",
    status: "active",
    createdAt: "2025-01-15",
    updatedAt: "2025-10-10"
  },
  {
    id: "nba_user_instruction",
    feature: "NBA",
    type: "user",
    name: "NBA User Instruction",
    description: "Specific instructions for analyzing transcripts",
    originalText: `Analyze the call transcript below. From the NBA catalog provided, identify the customer's primary intent and recommend the top 2 most relevant actions.

Instructions:
- Read the entire conversation carefully
- Identify explicit and implicit customer needs
- Match needs to NBA catalog entries
- Select top 2 most relevant actions
- Include confidence scores (0-1) for each recommendation
- Provide brief reasoning explaining why these actions are recommended

Return results as JSON with these fields:
{
  "intent": "detected customer intent",
  "confidence": 0.85,
  "recommended_actions": [
    {"nba_id": "BILLING_ISSUE", "action": "Review Recent Charges", "confidence": 0.9},
    {"nba_id": "BILLING_ISSUE", "action": "Initiate Dispute Process", "confidence": 0.75}
  ],
  "reasoning": "Customer mentioned unrecognized charge, indicating billing dispute"
}`,
    compressedToken: "[REQ:CLASSIFY] [TARGET:TRANSCRIPT] [EXTRACT:INTENT+TOP_ACTIONS:LIMIT=2] [OUT:JSON:CONFIDENCE]",
    originalTokens: 120,
    compressedTokens: 4,
    compressionRate: 96.7,
    version: "1.0",
    status: "active",
    createdAt: "2025-01-15",
    updatedAt: "2025-10-10"
  },
  {
    id: "nba_system_prompt_v2",
    feature: "NBA",
    type: "system",
    name: "NBA Agent System Prompt v2 (Draft)",
    description: "Enhanced system instructions with sentiment analysis",
    originalText: `You are an advanced Next Best Action recommendation system for customer service agents.
Analyze live call transcripts and recommend the most relevant actions from the NBA catalog.

Enhanced Capabilities:
- Identify customer intent and sentiment from conversation
- Analyze conversation urgency and customer frustration levels
- Match intents to appropriate NBAs considering emotional context
- Recommend actions with confidence scores and priority levels
- Provide reasoning with sentiment indicators
- Prioritize urgent issues and frustrated customers

Context Awareness:
- Track conversation flow and topic transitions
- Identify when customer is repeating concerns (escalation signal)
- Recognize positive sentiment for upsell opportunities
- Detect confusion or uncertainty requiring clarification

Output Format:
Return JSON with: 'intent', 'sentiment', 'urgency', 'confidence', 'recommended_actions', and 'reasoning'.

Quality Guidelines:
- Confidence > 0.7 for standard recommendations
- Confidence > 0.8 for actions requiring authorization
- Flag urgent cases (sentiment negative + repeated concerns)
- Suggest empathy-based actions for frustrated customers`,
    compressedToken: "[REF:NBA_AGENT_V2:2.0]",
    originalTokens: 450,
    compressedTokens: 1,
    compressionRate: 99.8,
    version: "2.0",
    status: "draft",
    createdAt: "2025-10-01",
    updatedAt: "2025-10-12"
  }
];

export const features = [
  { id: "NBA", name: "Next Best Actions", description: "Agent recommendation system" },
  { id: "SENTIMENT", name: "Sentiment Analysis", description: "Customer emotion detection (Future)" },
  { id: "SUMMARY", name: "Call Summarization", description: "Automated call summaries (Future)" }
];

export const promptTypes = [
  { id: "system", name: "System Prompt", description: "Core system instructions" },
  { id: "user", name: "User Instruction", description: "Specific task instructions" },
  { id: "assistant", name: "Assistant Context", description: "Response formatting rules" }
];

// Utility functions
export const getCompressionColor = (rate) => {
  if (rate >= 95) return 'green';
  if (rate >= 85) return 'blue';
  if (rate >= 70) return 'yellow';
  return 'gray';
};

export const getStatusColor = (status) => {
  const colors = {
    active: 'green',
    draft: 'yellow',
    archived: 'gray',
    testing: 'blue'
  };
  return colors[status] || 'gray';
};