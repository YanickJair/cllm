import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from clm_core import CLMEncoder, CLMConfig, ThreadConfig

CX_TRANSCRIPTS = [
    {
        "id": "call_001",
        "issue": "INTERNET_OUTAGE",
        "clm_core": """
Agent: Good morning, thank you for calling TechCorp support. My name is Sarah. How can I help you today?

Customer: Hi Sarah, I’ve been having issues with my internet connection for the past three days. It keeps dropping every few hours, and I work from home so this is really frustrating.

Agent: I totally understand how important that is. Let’s get this sorted. Could I have your account number, please?

Customer: Sure, it’s 847-392-1045.

Agent: Thanks. I see you’re on the Premium 500 plan. When the connection drops, do all your devices lose internet, or just one?

Customer: Everything — my laptop, my wife’s phone, even the TV.

Agent: Got it. I’m running a quick diagnostic on your modem… okay, it looks like a line fluctuation issue in your area. We’ve had similar reports from nearby addresses.

Customer: So it’s not just me?

Agent: Correct. A technician is already assigned to inspect the local node this afternoon. I’ve added your account to that ticket so you’ll be notified once it’s resolved.

Customer: Great. Will I need to reboot anything?

Agent: Once service stabilizes, just unplug your modem for 30 seconds and plug it back in. That will refresh your connection.

Customer: Perfect. Thanks for the help.
""",
    },
    {
        "id": "call_002",
        "issue": "BILLING_DISPUTE",
        "clm_core": """
Agent: Hello, this is Daniel from MobileWave billing. How can I help you today?

Customer: Hi Daniel, I was charged twice for my plan this month. I only have one line, so I’m not sure why.

Agent: I see how that’s confusing. Let’s check it out. What’s your account ID?

Customer: MW-55983.

Agent: Thanks. I see two identical payments for $89.99 — one on the 2nd and one on the 4th. Looks like a duplicate authorization error.

Customer: Can that be fixed?

Agent: Yes, I’m submitting a refund request right now. You’ll see the refund within 3–5 business days. I’ll also apply a $10 courtesy credit for the inconvenience.

Customer: Wow, thanks so much.

Agent: My pleasure. Anything else I can assist with today?

Customer: Nope, that’s all. Appreciate it!
""",
    },
    {
        "id": "call_003",
        "issue": "DELIVERY_DELAY",
        "clm_core": """
Agent: Thanks for contacting ShopEase. This is Monica. How can I help?

Customer: I ordered a blender last week and it still hasn’t arrived. The tracking hasn’t updated since Friday.

Agent: I understand how frustrating that is. May I have your order number?

Customer: SE-90211.

Agent: Thanks. It looks like the package is delayed at your local distribution center due to a regional storm. It’s in transit now with an updated delivery date of Friday.

Customer: Okay, that’s fine. Just wanted to make sure it wasn’t lost.

Agent: Not at all — I’ll email you tracking updates. You should get it soon.
""",
    },
    {
        "id": "call_004",
        "issue": "LOGIN_FAILURE",
        "clm_core": """
Agent: Hi, this is Jason from CloudSync support. What seems to be the issue today?

Customer: I can’t log into my account. It says “password incorrect” but I didn’t change it.

Agent: No problem. Let’s fix that. What’s your registered email?

Customer: renee_hall@fastmail.com.

Agent: Thanks. I see your account’s been temporarily locked due to multiple failed attempts. I’m sending a reset link — could you check your email?

Customer: Got it. Clicking now… okay, password updated.

Agent: Great! Try logging in again.

Customer: It works now. Thanks!
""",
    },
    {
        "id": "call_005",
        "issue": "PRODUCT_DEFECT",
        "clm_core": """
Agent: Hello, this is Anita from HomePlus warranty. How can I help you today?

Customer: Hi, my air purifier stopped working yesterday. The power light turns on, but no air is coming out.

Agent: Thanks for letting me know. Can I get your model number?

Customer: HP-300A, purchased two months ago on your website.

Agent: Perfect. You’re still within warranty. Let’s try one quick thing: can you unplug it and hold the power button for 10 seconds, then plug it back in?

Customer: Okay... still not working.

Agent: Alright, we’ll replace it. You’ll receive a prepaid return label within 24 hours.
""",
    },
    # === LONG TRANSCRIPT (5-minute call) ===
    {
        "id": "call_006",
        "issue": "INTERNET_OUTAGE",
        "clm_core": """
Agent: Hi, you’ve reached TechLine Fiber Support. My name is Michael. How can I help?

Customer: Hey, Michael. My internet’s been cutting out randomly for the last week. It disconnects, then comes back after a few minutes. It’s driving me crazy.

Agent: I’m really sorry about that. Let’s take a deeper look. Can I have your account number?

Customer: Sure, it’s 154882. Address is 41 Riverbend Lane.

Agent: Thanks, found your account. You’re on the Fiber 1 Gbps plan. I see multiple drop events in the last 72 hours. Are you using a personal router or our company router?

Customer: I’m using your router, the one with the white antenna.

Agent: Got it. Can I ask if the lights on the router go red when it disconnects?

Customer: Yeah, it flashes red for a few seconds, then goes back to blue.

Agent: That’s a signal issue. It’s usually the optical line, not your devices. I’ll test your fiber link remotely… okay, the signal strength is below threshold intermittently.

Customer: So what does that mean?

Agent: It means the fiber cable connection outside your home might be slightly bent or dirty. I’ll schedule a technician to clean and re-terminate it. The next available slot is tomorrow morning between 9 and 11.

Customer: That works. Do I need to be home?

Agent: It’s best if you are, just in case they need indoor access. Also, I recommend avoiding frequent reboots tonight — it can worsen the signal calibration.

Customer: Got it. Thanks for the thorough explanation.

Agent: You’re very welcome. Once fixed, you’ll get a text confirmation and a feedback survey.
""",
    },
    {
        "id": "call_007",
        "issue": "ACCOUNT_HACKED",
        "clm_core": """
Agent: Hello, thank you for calling GameHub Security. My name is Leo. How can I assist you?

Customer: Hi Leo, I think my account got hacked. I can’t log in, and I got an email saying my password was changed.

Agent: That’s concerning. Can I get your original email address?

Customer: Yes, it’s skylar83@outlook.com.

Agent: Thank you. I’m checking… yep, there’s unauthorized access from a foreign IP. I’ll temporarily freeze the account and revert your email to the original.

Customer: Thank you. Can you also make sure none of my purchases were used?

Agent: Yes — I see one suspicious purchase for $49.99. I’ve flagged it for refund. You’ll receive an email confirmation and a password reset link in a few minutes.

Customer: Awesome. Really appreciate the help.

Agent: My pleasure. Security first!
""",
    },
    # === LONG TRANSCRIPT (5-minute call) ===
    {
        "id": "call_008",
        "issue": "DELIVERY_DELAY",
        "clm_core": """
Agent: Hi, this is Maria from ParcelLink. How may I help?

Customer: Hi Maria, my package was supposed to arrive three days ago. Tracking says “out for delivery,” but nothing’s come.

Agent: That’s frustrating — let’s fix that. May I have your tracking number?

Customer: It’s PL-7294008.

Agent: Thank you. Checking now… I see your parcel’s been looping between two depots due to an address mismatch. The street number is listed as 180 instead of 108.

Customer: Oh wow, that explains a lot.

Agent: No worries, I can correct that. I’ve updated your address and requested re-dispatch. It’s being prioritized for tomorrow morning delivery.

Customer: Perfect. Will I get a new tracking update?

Agent: Yes, you’ll receive an SMS within two hours with the corrected link.

Customer: Okay, thanks. I was worried it was lost.

Agent: Not at all. I’ve also added a note for the courier to call you before delivery.

Customer: Appreciate that. You’ve been really helpful.
""",
    },
    # === LONG TRANSCRIPT (5-minute call) ===
    {
        "id": "call_009",
        "issue": "BILLING_DISPUTE",
        "clm_core": """
Agent: Hi, thank you for contacting Streamly billing. This is Raj. How can I assist?

Customer: Hi Raj, I was just checking my card statement and saw two charges for my monthly subscription — one for $14.99 and another for $16.99. What’s going on?

Agent: That’s definitely unusual. Let me check. Can you give me the email linked to your account?

Customer: Sure, it’s emily.thomas@icloud.com.

Agent: Thanks. I see you recently upgraded from Standard to Premium. The $14.99 was for your old plan, and the $16.99 is for the new one. The overlap happened because the upgrade occurred mid-billing cycle.

Customer: So I was charged twice for the same month?

Agent: In a sense, yes — a partial overlap. But don’t worry, I can refund the difference. I’ll also adjust your billing cycle so this won’t happen again.

Customer: That would be great. I’ve been a customer for years, so I was surprised.

Agent: I completely understand. I’ve processed a $12 credit back to your card and emailed a breakdown of your new billing schedule.

Customer: You’ve been really clear — thank you.

Agent: My pleasure. Anything else I can help with today?

Customer: Nope, that’s all!
""",
    },
    {
        "id": "call_010",
        "issue": "CLAIM_STATUS",
        "clm_core": """
Agent: Good afternoon, you’ve reached SafeSure Insurance. My name is Priya. How can I help?

Customer: Hi Priya, I filed a car accident claim two weeks ago and haven’t heard back.

Agent: Let’s check that. What’s your claim number?

Customer: SS-CLA-89210.

Agent: Thank you. I see it’s been reviewed and approved for payout. The funds should reach your account within 3 business days.

Customer: That’s a relief! Thanks.
""",
    },
]


def dump_to_json():
    with open("transcripts.json", "w", encoding="utf-8") as file:
        json.dump(CX_TRANSCRIPTS, file, ensure_ascii=False)


def show_comparison(encoder: CLMEncoder, transcript: str, metadata: dict):
    """Show before/after comparison"""

    print("\n📄 ORIGINAL TRANSCRIPT:")
    print("-" * 70)
    print(f"\nLength: {len(transcript)} characters")

    st = time.perf_counter()

    new_result = encoder.encode(input_=transcript, metadata={})
    print("Elapsed time:", time.perf_counter() - st)
    print(new_result.to_dict())
    # INFORMATION PRESERVATION CHECK
    print("\n" + "=" * 70)
    print("🎯 INFORMATION PRESERVATION CHECK")
    print("=" * 70)

    # COMPRESSION METRICS
    print("\n" + "=" * 70)
    print("📈 COMPRESSION METRICS")
    print("=" * 70)

    original_chars = len(transcript)
    new_chars = len(new_result.compressed)
    new_result.to_dict()

    print("\nCharacter count:")
    print(f"  Original:  {original_chars:>6} chars")
    print(
        f"  Compressed:       {new_chars:>6} chars ({(1 - new_chars / original_chars) * 100:>5.1f}% compression)"
    )

    print("\nToken count (approximate):")
    print(f"  Original:  {new_result.n_tokens:>6} tokens")
    print(
        f"  Compressed:       {new_result.c_tokens:>6} tokens ({new_result.compression_ratio:>5.1f}% compression)"
    )

    print(f"🗜️  Compression Ratio: {new_result.compression_ratio:.1f}%")

    print("\n✅ Ready for production use!")
    return new_result.metadata.get("analysis"), new_result


if __name__ == "__main__":
    with open("./data/raw/transcripts_dataset.json", "r") as f:
        transcripts = json.load(f)

    t_cfg = ThreadConfig(
        include_summary=True,
        include_ctx_values=True
    )
    cfg = CLMConfig(lang="en", thread_config=t_cfg)
    encoder = CLMEncoder(cfg=cfg)
    result = []
    # test = "\nAgent: Hi, thank you for contacting Streamly Billing. This is Raj. How can I assist?\n\nCustomer: Hi Raj, I was just checking my card statement and saw two charges for my monthly subscription — one for $14.99 and another for $16.99. What’s going on?\n\nAgent: That’s definitely unusual. Let me check. Can you give me the email linked to your account?\n\nCustomer: Sure, it’s emily.thomas@icloud.com.\n\nAgent: Thanks. I see you recently upgraded from Standard to Premium. The $14.99 was for your old plan, and the $16.99 is for the new one. The overlap happened because the upgrade occurred mid-billing cycle.\n\nCustomer: So I was charged twice for the same month?\n\nAgent: In a sense, yes — a partial overlap. But don’t worry, I can refund the difference. I’ll also adjust your billing cycle so this won’t happen again.\n\nCustomer: That would be great. I’ve been a customer for years, so I was surprised.\n\nAgent: I completely understand. I’ve processed a $12 credit back to your card and emailed a breakdown of your new billing schedule.\n\nCustomer: You’ve been really clear — thank you.\n\nAgent: My pleasure. Anything else I can help with today?\n\nCustomer: Nope, that’s all!\n"
    # analysis, new_result = show_comparison(test)
    for transcript in transcripts:
        if transcript["metadata"]["channel"] == "voice":
            analysis, new_result = show_comparison(
                encoder, transcript.get("transcript"), metadata=transcript.get("metadata")
            )
            result.append(
                {
                    "n_tokens": new_result.n_tokens,
                    "c_tokens": new_result.c_tokens,
                    "ratio": new_result.compression_ratio,
                    "compressed": new_result.compressed,
                    "original": transcript.get("transcript"),
                    "summary": new_result.summary(cfg.thread_config.default_summary_template)
                }
            )
            print(new_result.to_dict())

    with open(".transcripts_v2.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
