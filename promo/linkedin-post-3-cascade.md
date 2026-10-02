# LinkedIn post 3: cheap model first

_Draft. Image: `promo/cascade-1.png`. Numbers come from `results/cascade.csv` (Jev's 70% setting) and the round 1 test-set logs. Post 4 (the road to 99%) follows it._

---

Cheap model first. Expensive model only when needed.

I had two AI models sort 1,000 real bank customer messages into 77 categories: Jev, a small specialized model, and Claude Sonnet 5.

The best result didn't come from either model alone. It came from a route:
→ Jev reads every message first. It's cheap.
→ If Jev is sure, its answer stands. That was 73% of messages, and Jev got 91.4% of them right.
→ If not, the message goes to Sonnet.

On all 1,000 messages:
• Jev first, Sonnet second: 82.8% correct, $1.51 per 1,000
• Sonnet alone: 82.3% correct, $5.25 per 1,000

Same accuracy, 71% cheaper.

The lesson: don't just ask "which model is best?" Ask "which model should handle which message?"

(82.8% still isn't good enough for a real business. More on that in my next post.)

Full results and every log: https://danielwipert.github.io/jev.sorter/

#AI #MachineLearning #LLM #Automation
