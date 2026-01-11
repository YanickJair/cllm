import torch
import torch.nn as nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PretrainedConfig,
    AutoConfig,
)
import json
from typing import Optional
import re


class CLLMConfig(PretrainedConfig):
    model_type = "clm_core"

    def __init__(
        self,
        base_model_name: str = "meta-llama/Llama-2-7b-hf",
        cllm_vocab_size: int = 200,
        cllm_embedding_dim: int = 768,
        use_hierarchical_attention: bool = True,
        compression_awareness: bool = True,
        token: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        base_model_config = AutoConfig.from_pretrained(base_model_name, token=token)
        self.hidden_size = base_model_config.hidden_size

        print("HF Token", token)
        self.base_model_name = base_model_name
        self.cllm_vocab_size = cllm_vocab_size
        self.cllm_embedding_dim = cllm_embedding_dim
        self.use_hierarchical_attention = use_hierarchical_attention
        self.compression_awareness = compression_awareness
        self.token = token


class CLLMEmbedding(nn.Module):
    """
    Custom embedding layer for CLLM tokens
    Maps compressed tokens like [REQ:ANALYZE] directly to embeddings
    """

    def __init__(self, vocab_size: int, embedding_dim: int):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim

        # Learnable embeddings for each CLLM token
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)

        # Token to ID mapping
        self.token_to_id = {}
        self.id_to_token = {}

        # Initialize with token vocabulary
        self._load_vocabulary()

    def _load_vocabulary(self):
        """Load CLLM token vocabulary"""
        try:
            with open("data/vocabulary/cllm_token_vocab.json", "r") as f:
                vocab = json.load(f)

            idx = 0
            # Add special tokens
            for token in vocab.get("special_tokens", []):
                self.token_to_id[token] = idx
                self.id_to_token[idx] = token
                idx += 1

            # Add CLLM tokens
            for token in vocab.get("req_tokens", []):
                full_token = f"[REQ:{token}]"
                self.token_to_id[full_token] = idx
                self.id_to_token[idx] = full_token
                idx += 1

            for token in vocab.get("target_tokens", []):
                full_token = f"[TARGET:{token}]"
                self.token_to_id[full_token] = idx
                self.id_to_token[idx] = full_token
                idx += 1

            for token in vocab.get("extract_tokens", []):
                full_token = f"[EXTRACT:{token}]"
                self.token_to_id[full_token] = idx
                self.id_to_token[idx] = full_token
                idx += 1

            print(f"✅ Loaded {len(self.token_to_id)} CLLM tokens")

        except FileNotFoundError:
            print("⚠️  cllm_token_vocab.json not found. Using default vocabulary.")
            # Fallback: create basic vocabulary
            self._create_default_vocabulary()

    def _create_default_vocabulary(self):
        """Create a basic vocabulary if file not found"""
        basic_tokens = [
            "[PAD]",
            "[UNK]",
            "[CLS]",
            "[SEP]",
            "[REQ:ANALYZE]",
            "[REQ:EXTRACT]",
            "[REQ:GENERATE]",
            "[TARGET:CODE]",
            "[TARGET:TRANSCRIPT]",
            "[TARGET:DATA]",
        ]

        for idx, token in enumerate(basic_tokens):
            self.token_to_id[token] = idx
            self.id_to_token[idx] = token

    def tokenize_cllm(self, text: str) -> torch.Tensor:
        """Convert CLLM text to token IDs"""
        # Extract CLLM tokens from text
        tokens = re.findall(r"\[[^\]]+\]", text)

        # Convert to IDs
        ids = []
        for token in tokens:
            if token in self.token_to_id:
                ids.append(self.token_to_id[token])
            else:
                ids.append(self.token_to_id.get("[UNK]", 1))

        return torch.tensor(ids, dtype=torch.long)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        """Get embeddings for token IDs"""
        return self.embeddings(token_ids)


class HierarchicalAttention(nn.Module):
    """
    Hierarchical attention mechanism for CLLM
    - Coarse attention: Semantic structure (REQ → TARGET → OUT)
    - Fine attention: Individual token details
    """

    def __init__(self, hidden_dim: int, num_heads: int = 8):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads

        # Semantic-level attention (coarse)
        self.semantic_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim, num_heads=num_heads, batch_first=True
        )

        # Token-level attention (fine)
        self.token_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim, num_heads=num_heads, batch_first=True
        )

        # Cross-level fusion
        self.fusion = nn.Linear(hidden_dim * 2, hidden_dim)

    def forward(
        self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Apply hierarchical attention"""

        # Semantic-level attention
        semantic_output, _ = self.semantic_attention(
            hidden_states, hidden_states, hidden_states, key_padding_mask=attention_mask
        )

        # Token-level attention
        token_output, _ = self.token_attention(
            hidden_states, hidden_states, hidden_states, key_padding_mask=attention_mask
        )

        # Fuse both levels
        fused = torch.cat([semantic_output, token_output], dim=-1)
        output = self.fusion(fused)

        return output


class CLLMModel(PreTrainedModel):
    """
    CLLM Model Core
    Language model that natively understands compressed CLLM tokens
    """

    config_class = CLLMConfig

    def __init__(self, config: CLLMConfig):
        super().__init__(config)
        self.config = config

        print("\n🔧 Initializing CLLM Model...")
        print(f"   Base model: {config.base_model_name}")
        print(f"   CLLM vocab size: {config.cllm_vocab_size}")

        # 1. Load base language model
        self.wrapped_model = AutoModelForCausalLM.from_pretrained(
            config.base_model_name,
            torch_dtype=torch.float16,
            device_map="cpu",
        )
        self.wrapped_tokenizer = AutoTokenizer.from_pretrained(
            config.base_model_name,
            token=config.token,
            load_in_8bit=True,
            device_map="cpu",
        )
        if self.wrapped_tokenizer.pad_token is None:
            self.wrapped_tokenizer.pad_token = self.wrapped_tokenizer.eos_token

        # 2. Custom CLLM embedding layer
        self.cllm_embeddings = CLLMEmbedding(
            vocab_size=config.cllm_vocab_size, embedding_dim=config.cllm_embedding_dim
        ).to(self.wrapped_model.dtype)

        # 3. Projection layer to match base model's embedding dimension
        base_hidden_size = self.wrapped_model.config.hidden_size
        self.cllm_projection = nn.Linear(
            config.cllm_embedding_dim, base_hidden_size
        ).to(self.wrapped_model.dtype)

        # 4. Optional hierarchical attention
        if config.use_hierarchical_attention:
            self.hierarchical_attention = HierarchicalAttention(
                hidden_dim=base_hidden_size
            ).to(self.wrapped_model.dtype)

        print("✅ CLLM Model initialized\n")

    def prepare_inputs(
        self, cllm_instruction: str, data: str, device: torch.device
    ) -> dict[str, torch.Tensor]:
        """
        Prepare inputs combining CLLM instruction + regular text data

        Args:
            cllm_instruction: Compressed instruction like "[REQ:ANALYZE] [TARGET:CODE]"
            data: Regular text data (not compressed)
            device: Target device

        Returns:
            Dictionary with input_ids, attention_mask, cllm_mask
        """

        # 1. Process CLLM instruction
        cllm_token_ids = self.cllm_embeddings.tokenize_cllm(cllm_instruction)
        cllm_embeddings = self.cllm_embeddings(cllm_token_ids)
        cllm_embeddings = self.cllm_projection(cllm_embeddings)

        # 2. Process regular data with base tokenizer
        data_tokens = self.wrapped_tokenizer(
            data, return_tensors="pt", padding=True, truncation=True, max_length=2048
        )

        data_input_ids = data_tokens["input_ids"].to(device)
        data_embeddings = self.wrapped_model.get_input_embeddings()(data_input_ids)

        # 3. Concatenate CLLM instruction + data
        combined_embeddings = torch.cat(
            [cllm_embeddings.unsqueeze(0).to(device), data_embeddings], dim=1
        )

        # 4. Create attention mask
        cllm_mask = torch.ones(1, cllm_embeddings.size(0), device=device)
        data_mask = data_tokens["attention_mask"].to(device)
        combined_mask = torch.cat([cllm_mask, data_mask], dim=1)

        return {
            "inputs_embeds": combined_embeddings,
            "attention_mask": combined_mask,
            "cllm_length": cllm_embeddings.size(0),
        }

    def forward(
        self,
        cllm_instruction: Optional[str] = None,
        data: Optional[str] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        **kwargs,
    ):
        """Forward pass through CLLM model"""

        # If raw strings provided, prepare inputs
        if cllm_instruction is not None and data is not None:
            prepared = self.prepare_inputs(
                cllm_instruction, data, device=self.wrapped_model.device
            )
            inputs_embeds = prepared["inputs_embeds"]
            attention_mask = prepared["attention_mask"]

        # Apply hierarchical attention if enabled
        if self.config.use_hierarchical_attention and inputs_embeds is not None:
            inputs_embeds = self.hierarchical_attention(inputs_embeds, attention_mask)

        # Forward through base model
        outputs = self.base_model(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            labels=labels,
            **kwargs,
        )

        return outputs

    def generate(
        self,
        cllm_instruction: str,
        data: str,
        max_new_tokens: int = 512,
        **generation_kwargs,
    ) -> str:
        """
        Generate response given CLLM instruction + data

        Args:
            cllm_instruction: Compressed instruction
            data: Input data
            max_new_tokens: Maximum tokens to generate

        Returns:
            Generated response text
        """

        # Prepare inputs
        prepared = self.prepare_inputs(
            cllm_instruction, data, device=self.base_model.device
        )

        # Generate
        with torch.no_grad():
            outputs = self.wrapped_model.generate(
                inputs_embeds=prepared["inputs_embeds"],
                attention_mask=prepared["attention_mask"],
                max_new_tokens=max_new_tokens,
                **generation_kwargs,
            )

        # Decode
        generated_text = self.wrapped_tokenizer.decode(
            outputs[0][prepared["inputs_embeds"].size(1) :], skip_special_tokens=True
        )

        return generated_text

    def get_input_embeddings(self):
        return self.wrapped_model.get_input_embeddings()

    def set_input_embeddings(self, value):
        self.wrapped_model.set_input_embeddings(value)

    @classmethod
    def from_pretrained(cls, model_path: str, **kwargs):
        """Load pre-trained CLLM model"""
        config = CLLMConfig.from_pretrained(model_path)
        model = cls(config)

        # Load weights
        state_dict = torch.load(f"{model_path}/pytorch_model.bin")
        model.load_state_dict(state_dict, strict=False)

        return model

    def save_pretrained(self, save_directory: str):
        """Save CLLM model"""
        import os

        os.makedirs(save_directory, exist_ok=True)

        # Save config
        self.config.save_pretrained(save_directory)

        # Save model weights
        torch.save(self.state_dict(), f"{save_directory}/pytorch_model.bin")

        print(f"✅ Model saved to {save_directory}")


def test_cllm_model():
    """Test CLLM model initialization and forward pass"""

    print("\n" + "=" * 80)
    print("🧪 TESTING CLLM MODEL")
    print("=" * 80 + "\n")

    # Initialize config
    config = CLLMConfig(
        base_model_name="microsoft/phi-2",  # Change to your model
        cllm_vocab_size=200,
        cllm_embedding_dim=768,
    )

    # Create model
    model = CLLMModel(config)

    # Test input
    cllm_instruction = "[REQ:ANALYZE] [TARGET:CODE]"
    data = "def foo():\n    return 42"

    print("Test Input:")
    print(f"  CLLM Instruction: {cllm_instruction}")
    print(f"  Data: {data}\n")

    # Test generation
    print("Generating response...")
    response = model.generate(
        cllm_instruction=cllm_instruction, data=data, max_new_tokens=100
    )

    print(f"\nGenerated Response:\n{response}\n")
    print("=" * 80)
    print("✅ Test complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_cllm_model()
