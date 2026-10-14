# LinkedIn post 5: Jev vs DeepSeek V4 Flash

_Draft, 2026-10-14. Image: `promo/jev-vs-deepseek.png` (rebuild: `python promo/build_post_images.py`). Standalone; follows the round 1 posts._

---

I tested a model 8x cheaper than Jev. Here's the honest scorecard.

Last month, a small decision model called Jev matched Claude Sonnet 5 on automated decisions at 1/52 of the cost. The obvious next question: what about something even cheaper?

So I ran DeepSeek V4 Flash through the same pipeline: same 1,000 bank customer messages, same 77 categories, same rules, written down before the run.

Jev won. But not on everything.

Where DeepSeek wins:
💰 Price. $0.013 per 1,000 messages vs $0.10. At a million messages a month, that's $13 vs $100.
🔓 Open weights. You can run it on your own servers and keep data in-house. Jev is a hosted beta product.
🎛️ A finer dial. Its confidence scores allow 349 automation settings, vs 67 for Jev.
🧰 It's general-purpose. The same model can also summarize, draft replies and explain itself. Jev only makes decisions.

Where Jev wins:
🎯 Accuracy where it counts. Set to automate about 70% of messages, Jev was right 91.4% of the time, DeepSeek 88.0%. Jev was ahead at every setting I tested.
🧭 Honest confidence. DeepSeek said it was 99.9%+ sure on 45% of messages, and was right on 93.8% of them. Jev's top score was right 98% of the time. When the score decides what goes out without a human, this is the whole game.
⚡ Speed. 0.22 seconds per message vs 1.46.
🔧 Less plumbing. To get DeepSeek's confidence, I had to pin a provider that exposes the model's internal probabilities, and add a retry for empty replies. Jev returns a score out of the box.

The math that decides it:
Take each model's 731 most confident answers. Jev got 91.4% right, DeepSeek 85.2%. That's about 45 more wrong answers per 1,000 messages going out unchecked, to save 9 cents. DeepSeek only comes out ahead if a wrong answer costs you less than a fifth of a cent.

One surprise: when Jev was confidently wrong, DeepSeek usually made the exact same mistake (56 times out of 63). Many of those turned out to be errors in the answer key. On a re-checked key, the gap narrows but stays: 98.8% vs 96.3%.

When I'd pick DeepSeek: a person reviews every decision anyway and the AI only pre-sorts, your data can't leave your servers, or one model has to do many jobs.

When I'd pick Jev: decisions go out with no human in the loop.

Caveats: one task (sorting short bank messages), one run per model, and Jev is still in beta.

Full results and every log: https://danielwipert.github.io/jev.sorter/

#AI #LLM #Automation #OpenSource

---

## Notes for Dan (not part of the post)

**Where every number comes from** (test set, 1,000 messages, v2 descriptions; site Finding 7 and the CHANGELOG entry of 2026-10-03):
- $0.013 vs $0.10 per 1,000; $13 vs $100 per million = billed OpenRouter cost per message, averaged.
- 349 vs 67 settings = distinct confidence values among answers that pass gate checks 1-3.
- 91.4% vs 88.0% = accuracy on auto-accepted at the pre-registered 70% row (realized: Jev 73.1%, DeepSeek 67.6%). At 50%: 97.0 vs 91.6. At 85%: 87.4 vs 80.9.
- 45% at 99.9+, 93.8% right = DeepSeek answers with confidence >= 99.9. Jev's top score (100) covers 39.7% of messages at 98.0%.
- 0.22 vs 1.46 seconds = median response time.
- Provider pin = `streamlake/fp8`, the cheapest provider that returns logprobs. Retry = one call (of about 2,000) came back with no reply.
- 731 / 91.4% / 85.2% / ~45 = same-volume check (Jev's number of auto-accepted answers at the 70% row): 6.2 points x 731 = 45.
- "A fifth of a cent" = $0.087 saved per 1,000 / 45 extra errors = $0.002 per error.
- 56 of 63 = Jev's wrong auto-accepted answers at the 70% row where DeepSeek picked the same wrong category.
- 98.8% vs 96.3% = Finding 8, cleaned answer key (secondary result; verdicts drafted by Claude, approved by you in bulk).
- DeepSeek's confidence = its probability for the category it wrote (logprobs), the same kind of score as Jev's. Its self-reported number did worse (81.4% right at the 70% row).

**Things to check before posting:**
- "Open weights": DeepSeek publishes the V4 Flash weights, so self-hosting is possible. We only ran it through OpenRouter, so the post doesn't claim anything about self-hosted cost or speed.
- The "When I'd pick" lines are judgment, not results. Change them if you see it differently.
