import re

import spacy


class CLLMDecoder:
    """Main CLLM decoder - gets a compressed prompt and returns natural language"""

    def __init__(self, model: str = "en_core_web_sm"):
        self.nlp: spacy.Language = spacy.load(model)

        self.req_expansions = {
            'ANALYZE': [
                'Analyze', 'Review', 'Examine', 'Evaluate', 'Assess',
                'Carefully analyze', 'Please analyze'
            ],
            'EXTRACT': [
                'Extract', 'Pull out', 'Identify and extract', 'Find and extract',
                'Please extract', 'Retrieve'
            ],
            'GENERATE': [
                'Generate', 'Create', 'Write', 'Produce', 'Develop',
                'Please generate', 'Please create'
            ],
            'SUMMARIZE': [
                'Summarize', 'Provide a summary of', 'Give a brief summary of',
                'Condense', 'Please summarize'
            ],
            'TRANSFORM': [
                'Transform', 'Convert', 'Change', 'Rewrite', 'Modify',
                'Please transform', 'Please convert'
            ],
            'EXPLAIN': [
                'Explain', 'Describe', 'Tell me about', 'Clarify',
                'Please explain', 'Can you explain'
            ],
            'COMPARE': [
                'Compare', 'Compare and contrast', 'Show the differences between',
                'Please compare'
            ],
            'CLASSIFY': [
                'Classify', 'Categorize', 'Sort', 'Organize',
                'Please classify', 'Group'
            ],
            'DEBUG': [
                'Debug', 'Fix', 'Troubleshoot', 'Find and fix bugs in',
                'Please debug', 'Identify bugs in'
            ],
            'OPTIMIZE': [
                'Optimize', 'Improve', 'Enhance', 'Refactor',
                'Please optimize', 'Make improvements to'
            ],
            'VALIDATE': [
                'Validate', 'Verify', 'Check', 'Confirm',
                'Please validate', 'Ensure the correctness of'
            ],
            'SEARCH': [
                'Search', 'Find', 'Look for', 'Search for',
                'Please search', 'Locate'
            ],
            'RANK': [
                'Rank', 'Prioritize', 'Order', 'Sort by priority',
                'Please rank'
            ],
            'PREDICT': [
                'Predict', 'Forecast', 'Estimate', 'Project',
                'Please predict'
            ],
            'FORMAT': [
                'Format', 'Structure', 'Organize the format of',
                'Please format'
            ],
            'DETECT': [
                'Detect', 'Identify', 'Find', 'Discover',
                'Please detect', 'Look for'
            ],
            'CALCULATE': [
                'Calculate', 'Compute', 'Determine', 'Figure out',
                'Please calculate'
            ],
            'AGGREGATE': [
                'Aggregate', 'Combine', 'Group together', 'Consolidate',
                'Please aggregate'
            ],
            'DETERMINE': [
                'Determine', 'Decide', 'Figure out', 'Assess',
                'Please determine'
            ],
            'ROUTE': [
                'Route', 'Assign', 'Direct', 'Forward',
                'Please route'
            ],
            'EXECUTE': [
                'Use', 'Apply', 'Implement', 'Run', 'Execute',
                'Please use'
            ],
            'LIST': [
                'List', 'Enumerate', 'Provide a list of', 'Itemize',
                'Please list'
            ],
            'QUERY': [
                'Answer', 'What is', 'Tell me', 'Explain',
                'Please explain'
            ],
        }

        # TARGET token to natural language expansions
        self.target_expansions = {
            'CODE': 'this code',
            'DATA': 'this data',
            'QUERY': 'this query',
            'ENDPOINT': 'this API endpoint',
            'COMPONENT': 'this component',
            'SYSTEM': 'this system',
            'TEST': 'this test',
            'LOG': 'these logs',
            'RECORD': 'this record',
            'STRATEGY': 'this strategy',
            'DOCUMENT': 'this document',
            'EMAIL': 'this email',
            'REPORT': 'this report',
            'TICKET': 'this ticket',
            'TRANSCRIPT': 'this transcript',
            'FEEDBACK': 'this feedback',
            'COMMENT': 'this comment',
            'COMPLAINT': 'this complaint',
            'REQUEST': 'this request',
            'INQUIRY': 'this inquiry',
            'INTERACTION': 'this interaction',
            'CALL': 'this call',
            'DESCRIPTION': 'a description',
            'SUMMARY': 'a summary',
            'PLAN': 'a plan',
            'POST': 'a post',
            'PRESS_RELEASE': 'a press release',
            'INTRODUCTION': 'an introduction',
            'CAPTION': 'a caption',
            'QUESTIONS': 'questions',
            'RESPONSE': 'a response',
            'LOGS': 'the logs',
            'CORRELATION': 'the correlation',
            'TRADEOFF': 'the trade-offs',
            'PARADIGM': 'the paradigm',
            'PAIN_POINTS': 'the pain points',
            'PATTERN': 'the pattern',
            'CHURN': 'the churn rate',
            'FEATURES': 'the features',
            'METRICS': 'the metrics',
            'REGIONS': 'the regions',
            'ITEMS': 'items',
            'CONCEPT': 'this concept',
            'PROCEDURE': 'this procedure',
            'FACT': 'the facts',
            'ANSWER': 'an answer',
            'CONVERSATION': 'this conversation',
        }

        # Domain-specific templates
        self.domain_templates = {
            'SUPPORT': 'customer support',
            'MEETING': 'meeting',
            'INTERVIEW': 'interview',
            'CALL': 'call',
            'CHAT': 'chat',
            'PHONE': 'phone call',
            'VIDEO': 'video call',
        }

        # Language templates
        self.language_templates = {
            'PYTHON': 'Python',
            'JAVASCRIPT': 'JavaScript',
            'JAVA': 'Java',
            'CPP': 'C++',
            'GO': 'Go',
            'RUST': 'Rust',
            'TYPESCRIPT': 'TypeScript',
        }

        # Context aspect templates
        self.context_templates = {
            'TONE': {
                'PROFESSIONAL': 'in a professional tone',
                'CASUAL': 'in a casual tone',
                'EMPATHETIC': 'in an empathetic tone',
                'TECHNICAL': 'in a technical tone',
            },
            'STYLE': {
                'SIMPLE': 'in simple terms',
                'DETAILED': 'in detail',
                'CONCISE': 'concisely',
                'COMPREHENSIVE': 'comprehensively',
            },
            'AUDIENCE': {
                'TECHNICAL': 'for a technical audience',
                'BUSINESS': 'for a business audience',
                'CHILD': 'for children',
                'EXPERT': 'for experts',
            },
            'LENGTH': {
                'BRIEF': 'briefly',
                'SHORT': 'in a short form',
                'MEDIUM': 'in medium length',
                'LONG': 'in detail',
            },
        }

        # Output format templates
        self.output_templates = {
            'JSON': 'in JSON format',
            'MARKDOWN': 'in Markdown format',
            'TABLE': 'in table format',
            'LIST': 'as a list',
            'PLAIN': 'in plain text',
            'CSV': 'in CSV format',
            'HTML': 'in HTML format',
            'XML': 'in XML format',
            'YAML': 'in YAML format',
            'CODE': 'as code',
            'STRUCTURED': 'in structured format',
            'BREAKDOWN': 'as a breakdown',
            'SUMMARY': 'as a summary',
            'REPORT': 'as a report',
            'DIFF': 'as a diff',
        }

    @staticmethod
    def parse_token(token_str: str) -> dict:
        """Parse a single CLLM token into its components"""
        parts = token_str.split(':')

        result = {
            'type': parts[0],
            'value': parts[1] if len(parts) > 1 else None,
            'attributes': {}
        }

        # Parse attributes
        if len(parts) > 2:
            for attr in parts[2:]:
                if '=' in attr:
                    key, val = attr.split('=', 1)
                    result['attributes'][key] = val
                else:
                    # Modifier without value
                    result['attributes'][attr] = True

        return result

    def decode_req(self, token: dict) -> str:
        """Decode REQ token to natural language"""
        req = token['value']
        expansions = self.req_expansions.get(req, [req.lower()])
        return expansions[0]

    def decode_target(self, token: dict) -> str:
        """Decode TARGET token to natural language"""
        target = token['value']
        base = self.target_expansions.get(target, target.lower())

        # Add domain if present
        if 'DOMAIN' in token['attributes']:
            domain = token['attributes']['DOMAIN']
            domain_text = self.domain_templates.get(domain, domain.lower())
            return f"this {domain_text} {base.replace('this ', '')}"

        # Add language if present
        if 'LANG' in token['attributes']:
            lang = token['attributes']['LANG']
            lang_text = self.language_templates.get(lang.upper(), lang)
            return f"this {lang_text} {base.replace('this ', '')}"

        return base

    def decode_extract(self, token: dict) -> str:
        """Decode EXTRACT token to natural language"""
        fields = token['value'].split('+')

        # Clean up field names
        cleaned_fields = []
        for field in fields:
            # Convert NEXT_STEPS to "next steps"
            cleaned = field.replace('_', ' ').lower()
            cleaned_fields.append(cleaned)

        if len(cleaned_fields) == 1:
            return f"and extract the {cleaned_fields[0]}"
        elif len(cleaned_fields) == 2:
            return f"and extract the {cleaned_fields[0]} and {cleaned_fields[1]}"
        else:
            # Join with commas and "and" for last item
            all_but_last = ', '.join(cleaned_fields[:-1])
            return f"and extract the {all_but_last}, and {cleaned_fields[-1]}"

    def decode_ctx(self, token: dict) -> str:
        """Decode CTX token to natural language"""
        aspect = token['value']

        if '=' in aspect:
            key, value = aspect.split('=', 1)
            if key in self.context_templates and value in self.context_templates[key]:
                return self.context_templates[key][value]
            return f"with {key.lower()} set to {value.lower()}"

        return f"with context: {aspect.lower()}"

    def decode_out(self, token: dict) -> str:
        """Decode OUT token to natural language"""
        format_type = token['value']
        return self.output_templates.get(format_type, f"in {format_type.lower()} format")

    def decompress(self, compressed: str, verbose: bool = False) -> str:
        """
        Decode compressed CLLM tokens to natural language

        Args:
            compressed: CLLM token sequence like "[REQ:ANALYZE] [TARGET:CODE]"

        Returns:
            Natural language reconstruction
        """
        if len(compressed) == 0:
            return ""

        tokens = re.findall(r'\[([^\]]+)\]', compressed)

        if not tokens:
            return compressed

        tokens = [self.parse_token(t) for t in tokens]

        req_tokens = [t for t in tokens if t['type'] == 'REQ']
        target_tokens = [t for t in tokens if t['type'] == 'TARGET']
        extract_tokens = [t for t in tokens if t['type'] == 'EXTRACT']
        ctx_tokens = [t for t in tokens if t['type'] == 'CTX']
        out_tokens = [t for t in tokens if t['type'] == 'OUT']

        parts = []

        # 1. Start with REQ (action)
        if req_tokens:
            parts.append(self.decode_req(req_tokens[0]))

        # 2. Add TARGET
        if target_tokens:
            parts.append(self.decode_target(target_tokens[0]))

        # 3. Add EXTRACT fields
        if extract_tokens:
            parts.append(self.decode_extract(extract_tokens[0]))

        # 4. Add CTX constraints
        for ctx_token in ctx_tokens:
            parts.append(self.decode_ctx(ctx_token))

        # 5. Add OUT format
        if out_tokens:
            parts.append(self.decode_out(out_tokens[0]))

        # Construct final sentence
        if not parts:
            return compressed

        sentence = self._join_parts(parts)

        # Ensure proper capitalization and punctuation
        if sentence:
            sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            if not sentence.endswith('.'):
                sentence += '.'

        return sentence

    @staticmethod
    def _join_parts(parts: list[str]) -> str:
        """Intelligently join sentence parts"""
        if not parts:
            return ""

        # Start with first part
        result = parts[0]

        # Add remaining parts with proper spacing
        for i, part in enumerate(parts[1:], 1):
            if part.startswith('and '):
                result += f" {part}"
            elif part.startswith('in ') or part.startswith('as ') or part.startswith('for ') or part.startswith(
                    'with '):
                result += f" {part}"
            elif part.endswith('ly'):  # Adverbs
                result += f" {part}"
            else:
                result += f" {part}"

        return result

    def decompress_batch(self, compressed_list: list[str], verbose: bool = False):
        return [self.decompress(c) for c in compressed_list]


if __name__ == "__main__":
    decoder = CLLMDecoder()
    test_cases = [
        {
            'compressed': '[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] [EXTRACT:ISSUE+SENTIMENT+ACTIONS] [OUT:JSON]',
            'expected': 'Analyze this customer support transcript and extract the issue, sentiment, and actions in JSON format.'
        },
        {
            'compressed': '[REQ:DEBUG] [TARGET:CODE:LANG=JAVASCRIPT]',
            'expected': 'Debug this JavaScript code.'
        },
        {
            'compressed': '[REQ:EXTRACT] [TARGET:TICKET] [EXTRACT:ISSUE]',
            'expected': 'Extract this ticket and extract the issue.'
        },
        {
            'compressed': '[REQ:GENERATE] [TARGET:SUMMARY] [CTX:LENGTH=BRIEF]',
            'expected': 'Generate a summary briefly.'
        },
        {
            'compressed': '[REQ:CLASSIFY] [TARGET:TICKET] [CTX:INTENT=ROUTING]',
            'expected': 'Classify this ticket with intent set to routing.'
        }
    ]

    print("=" * 80)
    print("CLLM DECODER TEST")
    print("=" * 80 + "\n")

    for i, test in enumerate(test_cases, 1):
        decoded = decoder.decompress(test['compressed'])
        print(f"Test {i}:")
        print(f"  Compressed:  {test['compressed']}")
        print(f"  Decoded:     {decoded}")
        print(f"  Expected:    {test['expected']}")
        print()