# Reply to the comment about auditing the answer-key re-check

_Draft for Dan to paste as a reply. Under LinkedIn's comment limit._

---

Great suggestion, so I did it.

Every re-checked label is now public: the original label, the alternative, the verdict, and what each model answered: https://danielwipert.github.io/jev.sorter/labels.html

Finding 8 now shows the full coverage/accuracy curve on the original key and on two corrected keys (clear errors only, and "either label where both fit"), side by side.

What it says about the Jev vs DeepSeek gap (each model's 731 most confident answers, 95% bootstrap interval):
- Original key: +6.2 points (4.2 to 8.2)
- Clear label errors fixed: +5.9 (4.0 to 8.0)
- Both-fit labels accepted too: +4.1 (2.6 to 5.8)

So fixing clear errors barely moves the gap, because they hurt both models equally. Ambiguity explains part of it: DeepSeek is very confident on messages that could go either way, and Jev isn't. Of DeepSeek's 45 extra mistakes, 28 are on messages nobody disputed.

Fair caveats: one run per model, so the interval only covers which messages were sampled, and the verdicts were drafted by Claude and approved by me.
