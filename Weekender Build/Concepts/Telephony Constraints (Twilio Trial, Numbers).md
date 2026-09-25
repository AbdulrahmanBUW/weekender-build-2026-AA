---
type: concept
tags: [voice]
sources: ["https://www.twilio.com/docs/usage/trials", "https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account", "https://help.twilio.com/articles/360036052753-Twilio-Free-Trial-Limitations", "https://www.twilio.com/en-us/voice/pricing/de", "https://support.twilio.com/hc/en-us/articles/8338625205147-How-to-Submit-a-Regulatory-Bundle-for-Phone-Number-Regulatory-Compliance", "https://docs.retellai.com/deploy/international-call", "https://docs.retellai.com/api-references/create-phone-call", "https://docs.vapi.ai/calls/outbound-calling", "https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/native-integration", "https://community.retellai.com/t/cannot-make-outbound-calls-to-uk-destination-number-is-not-allowed/3493"]
---
# Telephony Constraints (Twilio Trial, Numbers)

**Definition:** what stops us from ringing a German mobile (the teammate playing the receptionist) this weekend.
**Why it matters for us:** if the phone doesn't ring on stage, there is no demo. Solve this on **Friday night**.
**Related:** [[Voice Platform Comparison]] · [[DEC-001 Voice platform (proposed)]] · [[Voice Pipeline - Architecture]] · [[Voice Risks and Mitigations]]

## Twilio trial (2026)
From [Twilio trial docs](https://www.twilio.com/docs/usage/trials) and the [free-trial tutorial](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account):
- **Voice is limited to your sign-up country** (set by the phone number you registered with). International calling is blocked until you upgrade.
- **Only verified numbers** can be called (max 5; verification by SMS only on trial).
- Callees hear a **trial announcement** before the call connects — ugly on stage.
- One Twilio number per trial account; calls capped at **10 min**; 5 concurrent calls; trial expires after 30 days; ~75 free voice minutes.
- **Grey zone (unverified):** if someone signs up with a German mobile, Germany is the "sign-up country" — but the trial number itself would be a US number (a German number needs a regulatory bundle, below). Whether a US trial number may then call the verified German mobile is unclear. Don't bet on it.

**Conclusion:** for a clean demo, **upgrade Twilio** (add a card, top up — commonly $20; exact minimum unverified) → no announcement, no verified-only rule, then enable **Germany** under *Console → Voice → Settings → Geo permissions* (a Retell forum case shows calls fail with "destination number is not allowed" until the country is fully approved, [forum](https://community.retellai.com/t/cannot-make-outbound-calls-to-uk-destination-number-is-not-allowed/3493)).

## Numbers
| Number type | Available this weekend? | Notes |
|---|---|---|
| Twilio **US local** number | Yes, instantly (~$1.15/mo) | Caller ID shows +1 — fine for a demo, bad for real Praxis calls (fewer pickups). |
| Twilio **German (+49)** number | **No** — needs a regulatory bundle (business registration + address), 2–3 business days review ([Twilio](https://support.twilio.com/hc/en-us/articles/8338625205147-How-to-Submit-a-Regulatory-Bundle-for-Phone-Number-Regulatory-Compliance)). DE local $1.35/mo, DE mobile $30/mo. | Production item (Monday-morning list). |
| Twilio **Verified Caller ID** (your own German mobile as caller ID) | Probably (outbound only) | ElevenLabs supports Twilio verified caller IDs for outbound AI calls ([docs](https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/native-integration)). Shows a +49 number to the Praxis. Test. |
| **Retell-managed** number (US) | Yes, $2/mo, bought in the Retell dashboard | Retell's intl. page lists **Germany at $0.10/min** via Twilio ([docs](https://docs.retellai.com/deploy/international-call)); the API reference still says Retell numbers call US only ([docs](https://docs.retellai.com/api-references/create-phone-call)). **Conflict → test the very first thing.** No Twilio account needed if it works. |
| **Vapi free** number | No outbound, no international ([docs](https://docs.vapi.ai/calls/outbound-calling)) | Import a Twilio number instead. |
| **ElevenLabs** | Has no own numbers → Twilio (import SID + token) or SIP trunk | |

## Costs (weekend scale)
- Twilio → German mobile: **$0.042/min**, landline $0.0283/min ([Twilio DE](https://www.twilio.com/en-us/voice/pricing/de)).
- Retell → Germany: $0.10/min on top of the agent minute price.
- 30 test calls × 3 min ≈ 90 min → a few euros on any path.

## Fallbacks if no phone call works
1. **Browser (WebRTC) call, no telephony at all:** Retell "web call", ElevenLabs widget / "Test agent", Vapi web call. The receptionist teammate talks into a laptop; the same agent, prompt, tools and webhooks run. Honest framing for jurors: "same agent, telephone leg swapped for the browser".
2. **Receptionist on a laptop, agent calls a US/verified number** that is forwarded (unverified; skip unless trivial).
3. **Pre-recorded backup video** of a successful run (already in the demo plan of [[Idea A - HalloTermin (Abdul)]]).

## Friday-night checklist
- [ ] Create Retell account → buy number → create German test agent → dashboard "call" to the teammate's +49 mobile. Works? → done.
- [ ] If not: upgrade Twilio, buy US number, enable Germany geo permission, import into Retell *or* ElevenLabs, retry.
- [ ] Note which path works in [[DEC-001 Voice platform (proposed)]].
