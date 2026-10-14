# LinkedIn post 4: the build plan to 99%

_Draft, updated 2026-10-14 with the DeepSeek and cleaned-key results. Image: `promo/cascade-2.png`. Follows post 3 (cheap model first)._

---

82.8% accuracy isn't good enough for a real business. Here's the build plan I'd follow to get to 99%.

First, a mindset shift: you don't get to 99% by finding a better model, or a cheaper one. (I tried: DeepSeek V4 Flash was 8x cheaper than Jev, and made about 45 more unchecked mistakes per 1,000 messages.) You get there by automating only the work you can prove is 99% right, then growing that share.

1. Define the target. "99%" means at most 1 wrong in 100 decisions the machine makes alone, checked by people on a random sample. Not 99% of everything.

2. Measure your human ceiling. Have two people label the same 1,000 messages. Where they disagree, your categories are fuzzy, and no AI will beat that. In my test, the answer key was a big part of the error: I had 206 doubtful labels re-checked blind, and on the corrected key Jev went from 91% to 95-99% right on what it automated.

3. Fix the categories. Merge the ones people confuse. Write tie-break rules, like "asks how long transfers take" vs. "says a transfer never arrived."

4. Run in shadow mode. The AI suggests, people still decide. A few weeks gives you thousands of labeled examples, with zero risk.

5. Set a bar per category. Use the shadow data to find the confidence level where each category is 99%+ right. Categories that never get there stay with people. High-risk ones (stolen cards, fraud) stay with people regardless.

6. Add checks that don't trust the AI. Simple rules: my keyword check caught 1 in 7 wrong answers. And checks against real records: if the AI says "transfer not received," is there actually a pending transfer? A second AI is not that check. When Jev was confidently wrong, DeepSeek picked the exact same wrong answer 56 times out of 63.

7. Turn it on one category at a time. Start with the safest, highest-volume ones.

8. Audit forever, with a brake. People review a random sample of automated decisions every week. 300 clean checks in a row supports 99%. If a category slips, it goes back to people automatically.

9. Close the loop. Human corrections feed better descriptions and rules. Re-test on a fixed test set before every change, and pin your model version.

The number to watch isn't accuracy. It's how much work you can automate while staying at 99%. Today, Jev alone handles 40% of messages at 98% against the official labels, and all 8 of its "mistakes" there turned out to be labeling problems when re-checked. That 40% may already be at 99%. Every step above grows it.

Full results and every log: https://danielwipert.github.io/jev.sorter/

#AI #MachineLearning #LLM #Automation

---

## Notes for Dan (not part of the post)

**Before posting, please read this.** Points 2 and the closing line rest on the cleaned-key re-check. Its verdicts were drafted by Claude (blind) and you approved all 206 in bulk. That's why the post says "I had ... re-checked" rather than "I re-checked". At minimum, read the 8 below; if you also skim `review/relabel_test.csv`, you can honestly say "I re-checked".

**The 8 "wrong" answers at Jev's top score (100).** Sonnet gave the same answer as Jev every time. In the blind re-check, 7 were relabeled to Jev's answer and 1 (the "compromised card" one) was "both fit":

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

The re-scoring rule was pre-registered (CHANGELOG, 2026-10-13), but it's still a secondary result with one reviewer, so the closing line says "may already be".

**Where the other numbers come from:**
- 73% sure = Jev's 70% setting (score 85 or higher): 73.1% of messages.
- 40% at 98% = Jev score 100 that passed the rule checks (39.6%, 97.98%), scored against the official labels.
- 71% cheaper = 1 − $1.51 / $5.25.
- 300 = the "rule of three": with zero errors in n checks, you can be 95% sure the true error rate is below 3/n. 3/300 = 1%, so 300 clean checks supports 99%. (99.9% would take 3,000.)
- 91% to 95-99% = Finding 8 on the site: Jev's 70% setting, official 91.4%, strict 94.9%, cleaned 98.8%.
- 40% slice on the cleaned key: 99.7% strict, 100% cleaned (all 8 errors resolved).
- 8x cheaper, ~45 more mistakes per 1,000 = Finding 7: $0.013 vs $0.10 per 1,000; each model's 731 most confident answers, 85.2% vs 91.4% right (6.2 points x 731 = 45).
- 56 of 63 = Jev's wrong auto-accepted answers at the 70% setting where DeepSeek picked the same wrong category.
- 1 in 7 = Finding 5 on the site (keyword check): 28 of Jev's 184 wrong answers on the test set, while blocking 13 of 816 right ones.
