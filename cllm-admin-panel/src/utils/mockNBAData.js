// src/utils/mockNBAData.js

export const mockNBAs = [
  {
    id: "BILLING_ISSUE",
    title: "Billing Issue Resolution",
    description: "Handle billing problems including disputed charges, incorrect amounts, and billing cycle questions. Use when customer mentions bill, charge, payment, or invoice concerns.",
    priority: "HIGH",
    prerequisites: ["customer_verified", "account_accessible"],
    successIndicators: ["issue_resolved", "customer_satisfied"],
    keywords: ["bill", "charge", "payment", "invoice", "billing"],
    actions: [
      {
        name: "Review Recent Charges",
        description: "Display last 3 months of charges in agent UI",
        whenToUse: "Customer questions specific charges",
        estimatedTimeMinutes: 3,
        uiComponent: "ChargeHistoryWidget",
        authorizationRequired: false,
        prerequisites: []
      },
      {
        name: "Initiate Dispute Process",
        description: "Start formal charge dispute procedure",
        whenToUse: "Customer disputes unauthorized charge",
        prerequisites: ["charge_less_than_60_days"],
        estimatedTimeMinutes: 7,
        authorizationRequired: false
      },
      {
        name: "Apply Account Credit",
        description: "Credit customer account for disputed amount",
        whenToUse: "Clear billing error identified",
        authorizationRequired: true,
        estimatedTimeMinutes: 2,
        prerequisites: []
      }
    ],
    status: "active",
    createdAt: "2025-01-15",
    updatedAt: "2025-10-10"
  },
  {
    id: "ACCOUNT_UPDATE",
    title: "Account Information Update",
    description: "Handle account information changes including address, email, phone, contact preferences. Use when customer wants to update personal information.",
    priority: "MEDIUM",
    prerequisites: ["customer_verified"],
    successIndicators: ["info_updated", "confirmation_sent"],
    keywords: ["update", "change", "address", "email", "phone"],
    actions: [
      {
        name: "Update Contact Information",
        description: "Modify email, phone, or mailing address",
        whenToUse: "Customer requests contact info change",
        estimatedTimeMinutes: 5,
        authorizationRequired: false,
        prerequisites: []
      },
      {
        name: "Update Communication Preferences",
        description: "Modify email/SMS notification settings",
        whenToUse: "Customer wants to change how they receive updates",
        estimatedTimeMinutes: 3,
        authorizationRequired: false,
        prerequisites: []
      }
    ],
    status: "active",
    createdAt: "2025-01-20",
    updatedAt: "2025-09-15"
  },
  {
    id: "TECH_SUPPORT",
    title: "Technical Support",
    description: "Resolve technical issues including connectivity problems, device setup, app troubleshooting, and system errors.",
    priority: "HIGH",
    prerequisites: ["customer_verified", "account_accessible"],
    successIndicators: ["issue_resolved", "customer_can_use_service"],
    keywords: ["not working", "broken", "error", "technical", "help"],
    actions: [
      {
        name: "Basic Troubleshooting",
        description: "Run through standard troubleshooting steps",
        whenToUse: "Initial technical complaint",
        estimatedTimeMinutes: 10,
        authorizationRequired: false,
        prerequisites: []
      },
      {
        name: "Remote Diagnostic",
        description: "Run remote system diagnostic",
        whenToUse: "Basic troubleshooting didn't resolve issue",
        estimatedTimeMinutes: 15,
        authorizationRequired: false,
        prerequisites: []
      },
      {
        name: "Schedule Technician Visit",
        description: "Arrange on-site technical support",
        whenToUse: "Remote resolution not possible",
        estimatedTimeMinutes: 5,
        authorizationRequired: true,
        prerequisites: []
      },
      {
        name: "Provide Temporary Workaround",
        description: "Offer interim solution while issue is resolved",
        whenToUse: "Immediate fix not available",
        estimatedTimeMinutes: 5,
        authorizationRequired: false,
        prerequisites: []
      }
    ],
    status: "active",
    createdAt: "2025-02-01",
    updatedAt: "2025-10-12"
  },
  {
    id: "CANCEL_SERVICE",
    title: "Service Cancellation",
    description: "Process service cancellation requests. Follow retention protocols and ensure proper account closure.",
    priority: "HIGH",
    prerequisites: ["customer_verified", "account_holder_confirmed"],
    successIndicators: ["cancellation_processed", "final_bill_explained"],
    keywords: ["cancel", "close", "terminate", "stop service"],
    actions: [
      {
        name: "Understand Cancellation Reason",
        description: "Document why customer wants to cancel",
        whenToUse: "Customer requests cancellation",
        estimatedTimeMinutes: 3,
        authorizationRequired: false,
        prerequisites: []
      },
      {
        name: "Offer Retention Incentive",
        description: "Present approved retention offers",
        whenToUse: "Cancellation reason is addressable",
        estimatedTimeMinutes: 5,
        authorizationRequired: false,
        prerequisites: ["retention_eligible"]
      },
      {
        name: "Process Cancellation",
        description: "Complete service termination",
        whenToUse: "Customer confirms cancellation decision",
        estimatedTimeMinutes: 8,
        authorizationRequired: true,
        prerequisites: []
      }
    ],
    status: "active",
    createdAt: "2025-01-10",
    updatedAt: "2025-09-28"
  },
  {
    id: "UPGRADE_PLAN",
    title: "Plan Upgrade",
    description: "Process plan upgrade requests. Present options and handle upgrade implementation.",
    priority: "MEDIUM",
    prerequisites: ["customer_verified", "account_accessible"],
    successIndicators: ["upgrade_completed", "customer_understands_changes"],
    keywords: ["upgrade", "better plan", "more features", "increase"],
    actions: [
      {
        name: "Review Current Plan",
        description: "Display customer's current plan details",
        whenToUse: "Customer interested in upgrading",
        estimatedTimeMinutes: 2,
        authorizationRequired: false,
        prerequisites: []
      },
      {
        name: "Present Upgrade Options",
        description: "Show available upgrade plans with benefits",
        whenToUse: "After reviewing current plan",
        estimatedTimeMinutes: 5,
        authorizationRequired: false,
        prerequisites: []
      },
      {
        name: "Process Upgrade",
        description: "Complete plan upgrade transaction",
        whenToUse: "Customer selects upgrade option",
        estimatedTimeMinutes: 7,
        authorizationRequired: false,
        prerequisites: []
      }
    ],
    status: "active",
    createdAt: "2025-02-10",
    updatedAt: "2025-10-01"
  }
];

// Utility function to convert NBA to CLLM token
export const toCLLMToken = (nba) => {
  return `[NBA:${nba.id}:P=${nba.priority}:ACTIONS=${nba.actions.length}]`;
};

// Utility function to get priority badge color
export const getPriorityColor = (priority) => {
  const colors = {
    HIGH: 'red',
    MEDIUM: 'yellow',
    LOW: 'green'
  };
  return colors[priority] || 'gray';
};

// Utility function to get status badge color
export const getStatusColor = (status) => {
  const colors = {
    active: 'green',
    draft: 'gray',
    archived: 'red'
  };
  return colors[status] || 'gray';
};