# LinkedIn post 3: cheap model first, and the road to 99%

_Draft. Numbers come from the round 1 test-set logs (`logs/decisions_{jev,sonnet}_test_v2.csv`, 1,000 messages) and `results/cascade.csv`. Images: `promo/cascade-1.png` (the cascade) and `promo/cascade-2.png` (the road to 99%)._

---

Cheap model first. Expensive model only when needed.

That design matched the expensive model at 71% less cost. It still isn't good enough for a real business. Here's how I'd close the gap.

Quick recap: 1,000 real bank customer messages, 77 categories. Jev (a small, specialized model) vs. Claude Sonnet 5, same pipeline.

The best result didn't come from a model. It came from a route:
→ Jev reads every message first (cheap)
→ If Jev is sure, its answer stands. That was 73% of messages.
→ If not, the message goes to Sonnet (expensive)

On all 1,000 messages:
• Jev first, Sonnet second: 82.8% correct, $1.51 per 1,000
• Sonnet alone: 82.3% correct, $5.25 per 1,000

But let's be honest: 82.8% is nowhere near good enough. If I ran a bank's support queue, I'd want 99%+ on anything a machine decides alone.

Here's my roadmap:

1. Stop automating everything. Pick the accuracy you need, then automate only what clears it. Today, Jev's surest answers cover 40% of messages at 98% correct. The rest go to a person.

2. Check the answer key. Jev was "wrong" 8 times at its top score. In all 8, Sonnet gave the same answer, and the official label looks wrong to me. ("whats your exchange rate" is labeled as a question about fees.) At the top end, the errors may be the test's, not the model's. In a business, that means fuzzy categories. Fix those first.

3. Set the bar per category. A wrong "exchange rate" answer is cheap. A wrong "lost or stolen card" answer isn't. Risky categories get a stricter bar or always go to a person.

4. Add cheap rule checks. Plain Python checks already stopped 1 in 7 wrong answers here.

5. Let people's corrections teach the system. Every message a person handles is a lesson for the next version.

6. Prove it before you trust it. Showing 99.9% takes about 3,000 checked decisions with zero mistakes. Then keep spot-checking after launch.

The model gets you to ~98% on the easy part. Getting to 99%+ is system design: routing, rules, clear categories, and people in the loop.

Full results and every log: https://danielwipert.github.io/jev.sorter/

#AI #MachineLearning #LLM #Automation

---

## Notes for Dan (not part of the post)

**The 8 "wrong" answers at Jev's top score (100).** Sonnet gave the same answer as Jev every time. Read these before posting point 2 and decide whether you agree:

| Message | Official label | Jev and Sonnet said |
|---|---|---|
| How long does it take for a transfer to get to a recipient? | transfer_not_received_by_recipient | transfer_timing |
| What should I do to get transactions off of my account if I didn't make them? My card must… | card_payment_not_recognised | compromised_card |
| The card got declined twice when I tried to use it to buy something online yesterday. | declined_transfer | declined_card_payment |
| My card is being declined for a purchase. I bought items before and the card worked… | reverted_card_payment? | declined_card_payment |
| How do I do a successful transfer to an account? | beneficiary_not_allowed | transfer_into_account |
| how many transactions can i make with a disposable card | get_disposable_virtual_card | disposable_card_limits |
| How long does a UK transfer take? | balance_not_updated_after_bank_transfer | transfer_timing |
| whats your exchange rate | exchange_charge | exchange_rate |

This is an after-the-fact reading, not a pre-registered re-scoring, so the post says "looks wrong to me" and "may be".

**Where the other numbers come from:**
- 73% sure = Jev's 70% setting (score 85 or higher): 73.1% of messages.
- 40% at 98% = Jev score 100 that passed the rule checks: 39.6% of messages, 97.98% correct.
- 71% cheaper = 1 − $1.51 / $5.25.
- 3,000 = the "rule of three": with zero errors in n checks, you can be 95% sure the true error rate is below 3/n. 3/3,000 = 0.1%.
- 1 in 7 = Finding 5 on the site (keyword check).
