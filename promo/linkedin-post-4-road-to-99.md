# LinkedIn post 4: the road to 99%

_Draft. Image: `promo/cascade-2.png`. Follows post 3 (cheap model first)._

---

82.8% accuracy isn't good enough for a real business. Here's how I'd get to 99%.

In my last post, a cheap-model-first design matched Claude Sonnet 5 at 71% less cost, with 82.8% correct. But if I ran a bank's support queue, I'd want 99%+ on anything a machine decides alone.

My roadmap:

1. Automate less. Jev's surest answers cover 40% of messages at 98% correct. People handle the rest.

2. Check the answer key. Jev's 8 "errors" at its top score all look like labeling mistakes to me, and Sonnet gave the same answer every time. Fuzzy categories cap your accuracy.

3. Set the bar per category. A wrong "lost card" answer costs more than a wrong "exchange rate" one.

4. Add cheap rule checks. Plain Python checks already stopped 1 in 7 wrong answers.

5. Learn from people. Every message a person handles teaches the next version.

6. Prove it. Showing 99.9% takes about 3,000 checked decisions with zero mistakes. Then keep spot-checking.

The model gets you to ~98% on the easy part. The rest is system design.

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
