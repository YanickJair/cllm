from clm_core import CLMConfig, CLMEncoder


turn = """I'm calling to complaing about a duplicated charge on my account"""

cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)
output = encoder.encode(input_=turn, metadata={})
print(output.compressed)
result = encoder.ts_encoder.encode(
    thread=turn,
    is_turn=True,
    metadata={}
)
print(result.to_dict())
