# LinkedIn post 2: the confidence score

_Draft. Numbers come from the round 1 test-set logs (`logs/decisions_*_test_v2.csv`, 1,000 messages per model)._

---

Most AI leaderboards ask "how accurate is it?"

If you're automating real work, there's a better question: "how precisely can I control its mistakes?"

Last week I showed that a small, specialized model (Jev) matched Claude Sonnet 5 at sorting bank customer messages, at about 1/50th of the cost. There was a second finding that I think matters even more if you actually run one of these systems: the confidence score.

In production you don't automate everything. You automate the answers the model is sure about and send the rest to a person. So the confidence score is the knob that sets two things at once: how much work you automate, and how many mistakes get through.

So I measured how fine that knob is. Between 50% and 90% automation, here's how many settings each model gives you:

• Jev: 38
• Sonnet 5: 8
• Haiku 4.5: 3

Why? When you ask Claude how sure it is, it mostly answers 85, 90 or 95. Jev's score comes from inside the model, so it uses almost every number.

Here's what that looks like in practice. With Sonnet, you can automate 45% of messages or jump straight to 65%. Nothing in between. 196 of the 1,000 test messages got the same score of 85, so they all switch over together.

Say you want about 60% of messages automated:
→ Jev: 60% handled, 96.1% correct
→ Sonnet: either 45% handled (96.0% correct) or 65% handled (93.7% correct)

Jev also gives you an easy place to start. 40% of messages got a perfect score of 100, and 98% of those were right.

To be fair to Sonnet: when it says it's very sure (90 or above), it's right more often than Jev at the same score (96% vs. 92.5%). Its scores are more trustworthy. They're just too coarse to fine-tune with.

The takeaway: when you pick a model for automation, accuracy is only half the story. The confidence score decides how precisely you can set your error rate, so test it as carefully as you test accuracy.

Full results, methods and every log: https://danielwipert.github.io/jev.sorter/

#AI #MachineLearning #LLM #Automation
