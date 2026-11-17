---
title: Language models
permalink: /llm/
template: page.html
toc: true
eyebrow: Language models
heading: The LLM lifecycle, built from scratch
description: >-
  Pretraining a 113M-parameter GPT from scratch, post-training it with SFT and
  GRPO-style reinforcement learning, and applying the recipe to Qwen3.5-9B on a
  24-GPU cluster. Data, training, evaluation, and the failures along the way.
lead: >-
  Three open repositories cover every stage of a language model: data collection,
  tokenizer, pretraining, supervised fine-tuning, reinforcement learning with
  verifiable rewards, tool use, and evaluation. The first two train and post-train
  a 113M-parameter GPT on two GPUs. The third applies the post-training recipe to
  Qwen3.5-9B on 24 A100 GPUs. Every number below was measured, and each write-up
  records the failures as well as the results.
links:
  - label: nanoGPT-Seis
    url: https://github.com/jiazhe868/nanogpt-seis
    icon: github
  - label: nanoGPT-Seis-Posttrain
    url: https://github.com/jiazhe868/nanogpt-seis-posttrain
    icon: github
  - label: qwen-seis-posttrain
    url: https://github.com/jiazhe868/qwen-seis-posttrain
    icon: github
  - label: Models on Hugging Face
    url: https://huggingface.co/jiazhe868
    icon: hf
---

## Overview

I wanted to understand each stage of a modern language model by building it myself and measuring it. The domain is earthquake science. It gives a concrete test that is easy to score: can the model solve quantitative seismology problems from papers it has never seen?

{{ m.flow([
  {'tag': 'Data', 'title': 'Crawl and clean', 'text': '533k documents, MinHash dedup'},
  {'tag': 'Tokens', 'title': 'BPE tokenizer', 'text': 'byte-level, 16,384 tokens'},
  {'tag': 'Pretrain', 'title': '113M decoder', 'text': 'GQA, RoPE, 4096 context'},
  {'tag': 'SFT', 'title': 'Fine-tuning', 'text': 'teacher-written solutions'},
  {'tag': 'RL', 'title': 'GRPO-style RL', 'text': 'programmatic verifiers'},
  {'tag': 'Tools', 'title': 'Executed equations', 'text': 'an interpreter computes'},
  {'tag': 'Eval', 'title': 'Held-out tests', 'text': 'paired bootstrap CIs'},
  {'tag': 'Scale', 'title': 'Qwen3.5-9B', 'text': 'verl, Megatron, vLLM'},
]) }}

{{ m.metrics([
  ('113M', 'parameters, pretrained from scratch on 822.7M tokens'),
  ('6.5 h', 'pretraining time on two NVIDIA A30 GPUs'),
  ('4.7% → 27.9%', 'held-out accuracy of the 113M model through post-training'),
  ('62.0 → 70.1', 'Qwen3.5-9B on the hardest seismology test set after SFT and RL'),
], cols=4) }}

## Stage 1 · Pretraining

[nanoGPT-Seis](https://github.com/jiazhe868/nanogpt-seis) pretrains a small GPT for earthquake science. The repository goes through each stage in order with code and measured numbers: crawling, cleaning, tokenization, the model, distributed training, inference, and a scaling-law sweep. The checkpoint is on [Hugging Face](https://huggingface.co/jiazhe868/nanogpt_seis).

{{ m.fig('/assets/img/llm/pretrain-workflow.webp', 'The pretraining pipeline: six free data sources, crawling, cleaning and deduplication, a 16k BPE tokenizer, a 113M-parameter decoder, two-GPU training, and streaming inference.', wide=True) }}

### Data

The corpus combines earthquake-science text with general text. Open-access papers come from Crossref and Unpaywall (11 journals and a broad pool), together with arXiv and EarthArXiv preprints, Wikipedia pages about earthquakes, and the Earthquake Insights newsletter. Wikipedia and FineWeb-Edu add general prose. Every PDF is validated before text extraction, because many links labeled open access return small anti-bot pages.

Cleaning normalizes the text and drops short, non-alphabetic, and non-English documents. Deduplication runs from the cheapest test to the most expensive: document id, exact hash, then MinHash with locality-sensitive hashing (128 permutations, word 5-grams, threshold 0.7). Documents are processed longest first, so the most complete copy of a paper survives. The final corpus has 533,248 documents, 485.7M words, and 822.7M training tokens, about 24% domain text and 76% general text.

### Tokenizer and model

The tokenizer is a byte-level BPE with 16,384 tokens, trained on the training split only. A small vocabulary keeps the tied embedding matrix at about 11% of the parameters, and common domain terms such as *earthquake* and *subduction* become single tokens.

The model is a Llama-style decoder with 113M parameters: 16 layers, width 768, grouped-query attention with 12 query heads and 4 key-value heads, rotary position embeddings, RMSNorm, SwiGLU, tied embeddings, and a 4096-token context. Grouped-query attention makes the KV cache three times smaller. Attention runs through PyTorch's fused FlashAttention kernel, and a tiled FlashAttention written from scratch in the repository matches it to about 1e‑15.

{{ m.figrow([
  {'src': '/assets/img/llm/pretrain-architecture.webp', 'caption': 'The decoder: 16 pre-norm blocks with grouped-query attention, RoPE, and SwiGLU.'},
  {'src': '/assets/img/llm/pretrain-embeddings.webp', 'caption': 'After pretraining, seismology terms and everyday words occupy separate regions of the embedding space.'},
]) }}

### Training

Training uses PyTorch DDP on two NVIDIA A30 GPUs (24 GB each), bf16, and `torch.compile`. Each step processes 393,216 tokens: 4 sequences of 4096 tokens per GPU, 12 accumulation steps, and 2 GPUs. AdamW (β = 0.9, 0.95; weight decay 0.1) warms up for 400 steps to a learning rate of 3e‑4 and follows a cosine schedule to 3e‑5. The run takes 8,000 steps, about 3.8 epochs, in 6.5 hours. The first loss was 9.85, close to the expected ln(16384) = 9.70, a quick check that the model and the loss are wired correctly.

I measured memory with a short probe before the long run. Weights, gradients, and Adam state take 1.8 GB, and activations at 4 sequences per GPU raise the peak to 15.2 GB. A batch of 8 runs out of memory. With more gradient accumulation the same 393,216-token step fits on a 16 GB card (8.9 GB peak) or a 12 GB card (5.3 GB).

### Results

Fluency is measured in bits per byte, which does not depend on the tokenizer. A first model trained only on papers wrote repetitive text outside the style of a paper. Adding general text lowered bits per byte on held-out Wikipedia and web text from 1.527 to 0.997, 35% lower, and raised it on earthquake papers from 0.78 to 0.95. The fluent mixed model is the right starting point for fine-tuning.

A longer context also helped. With the data held fixed, training at 4096 tokens instead of 1024 lowered perplexity from 10.93 to 9.74, about 11%, for about 26% more compute per step. The model uses that context: loss on tokens at positions 2048 to 4096 is 25% lower than on the first 64 tokens of a window. At inference, a KV cache gives about 176 ms to the first token and a steady 83 tokens per second up to the full context, and greedy decoding with and without the cache gives identical output.

{{ m.figrow([
  {'src': '/assets/img/llm/pretrain-bpb.webp', 'caption': 'Bits per byte for the domain-only model (v1) and the mixed model (v2). General text gets 35% cheaper to encode, and paper text 22% more expensive.'},
  {'src': '/assets/img/llm/pretrain-context.webp', 'caption': 'Loss by position in the 4096-token window. Tokens late in the window are predicted 24% better than the first 64.'},
]) }}

### Scaling laws

To check whether 113M parameters suits the compute budget, I ran an IsoFLOP sweep: 25 runs over 7 model sizes (0.74M to 122M non-embedding parameters) and 5 compute budgets (6e15 to 5.4e17 FLOPs). All runs use Maximal Update Parametrization (muP), so one base learning rate transfers across widths and tuning does not confound the comparison. For each budget, a parabola fit to loss against log model size gives the compute-optimal size.

The compute-optimal model size grows as C<sup>0.69</sup> and the data as C<sup>0.31</sup>. The size exponent is steeper than the Chinchilla value of about 0.5, so at this scale an undersized model costs more than an undertrained one. The 113M production run sits at 0.86 times the extrapolated compute-optimal size.

{{ m.fig('/assets/img/llm/pretrain-scaling.webp', 'Left: validation loss against model size for five compute budgets, with the optimum circled. Right: compute-optimal size against compute, N<sub>opt</sub> ∝ C<sup>0.69</sup>. The star marks the 113M run.', wide=True) }}

{{ m.lessons([
  ('Compare models with different tokenizers in bits per byte.', 'Perplexity depends on the vocabulary. Bits per byte made the domain-only and mixed models comparable.'),
  ('Store tokens independently of the context length.', 'The 1024 versus 4096 comparison needed no re-tokenization, so it was cheap to run.'),
  ('Probe memory before a long run.', 'The fixed state was 1.8 GB and the measured peak was 15.2 GB. Estimates of activation memory were less reliable than a ten-minute probe.'),
  ('Use muP for size sweeps.', 'One base learning rate transferred to every width, which removed tuning as a confound in the scaling fit.'),
  ('Check that the GPU is visible.', 'A PyTorch build for a newer CUDA than the driver reports no GPU and silently trains on the CPU.'),
]) }}

## Stage 2 · Post-training at 113M

[nanoGPT-Seis-Posttrain](https://github.com/jiazhe868/nanogpt-seis-posttrain) turns the pretrained base into a model that answers quantitative seismology questions. Everything runs on the same two A30 GPUs, including a Qwen3.8-27B teacher served with vLLM in FP8. The main test set has 153 numerical questions from papers never used in fine-tuning. An answer counts as correct within 5%, each model gets 6 seeds × 4 samples, and comparisons use paired bootstrap confidence intervals. The weights are on [Hugging Face](https://huggingface.co/jiazhe868/nanogpt_seis_posttrain).

{{ m.fig('/assets/img/llm/post-workflow.webp', 'The post-training phases with format compliance and held-out accuracy. The last box uses a majority vote over 8 samples. The others are single samples.', wide=True) }}

{{ m.fig('/assets/img/llm/post-stage-outputs.webp', 'One question answered at each phase. The base model continues the paper. After SFT it finds the method and does not finish. After GRPO it states the answer. The executed-equation model writes the derivation as equations that an interpreter runs, and 8 of 8 samples agree.', wide=True) }}

### SFT and GRPO

Supervised fine-tuning uses 14,068 question-answer pairs. The teacher wrote 17,289 pairs. Filters for contamination, phantom citations, off-domain content, and malformed tags kept 4,667, and 2,549 rewrites, 4,034 pairs on fundamentals, and 4,409 pairs on historical earthquakes complete the set. Splits are made by source paper, and the test set is pinned by hash. After SFT, 71% of answers were well formed and 4.7% were correct.

The RL stage is a GRPO-style method with programmatic verifier rewards for the numerical answer, key concepts, format, echoing the prompt, phantom citations, length, and termination. Each update uses 8 samples for each of 32 prompts, group-mean baselines scaled by one standard deviation pooled over the batch, and a KL penalty. Format compliance rose from 71% to 98% within 20 steps. Accuracy moved from 4.7% to 6.1%, and on the 92 questions outside the RL prompt pool the change was not statistically resolved (+0.8 points, 95% CI −0.5 to +2.1).

### Executed equations

Arithmetic was the bottleneck. The model learned to call a calculator tool in 93% of answers, and accuracy stayed flat. I then trained the model to write the whole derivation as equations that a restricted interpreter executes, and the final answer is written from the interpreter's result. Equations in the notation of the papers the model was pretrained on, such as `M0 = 10^(1.5*Mw + 9.1) [N m]`, ran more often than Python (75% of programs against 58%) and gave 17.8% accuracy against 11.3%, with 29% less data. With 105k teacher-written solutions, each kept only if executing it reproduces the label, held-out accuracy reached 19.7%.

### More data, fresh problems, and voting

Later rounds had the teacher write real-style problems from 40,000 unused corpus excerpts, with each label verified by execution or a blind re-solve. They also added 1.57B tokens of math and STEM mid-training and fine-tuned once on 279,929 rows, reaching 25.5%. GRPO on 2,082 problems held out of fine-tuning raised accuracy on 300 new problems by 2.9 points (95% CI +0.6 to +5.4), and on the 153 held-out questions the change was within noise. A majority vote over 8 executed answers gives the deployed model's 27.9%.

{{ m.ladder([
  ('SFT', 'prose answers', 4.7),
  ('+ GRPO', 'format reward', 6.1),
  ('Executed equations', 'paper notation, 105k solutions', 19.7),
  ('+ GRPO on the corpus', 'problems from unused excerpts', 22.0),
  ('Real-style data', 'one-stage fine-tune, mid-trained base', 25.5),
  ('+ GRPO on fresh problems', 'held out of fine-tuning', 26.4),
  ('+ vote@8', 'deployed model', 27.9, 'best'),
  ('Qwen3.8-27B teacher', 'reference, blind, single answer', 49.7, 'ref'),
], max=50, foot='Held-out accuracy (correct within 5%) on 153 numerical questions from papers never used in fine-tuning.') }}

With one executed answer per question, scored within 1%, the 113M model gets 22.6% of the held-out set. Qwen3.5-0.8B gets 3.1%, Qwen3.5-2B 12.3%, Qwen3.5-4B 30.4%, and Qwen3.5-9B 44.4%. The 113M model is 10.4 points ahead of the 2B model (95% CI +4.1 to +16.7) and uses about 190 times less compute per answer than the 9B model.

{{ m.fig('/assets/img/llm/post-general-models.webp', 'The 113M model against general Qwen models with one executed answer per question, and the share of key concepts named at equal answer length.', wide=True) }}

### What RL transferred

A transfer study explains why single GRPO steps were hard to resolve on held-out questions. On its own practice problems, GRPO raised accuracy from 48.8% to 85.4% in 75 steps. On other questions, the gain grew with similarity to the nearest trained problem: +27.2 points at similarity 0.5 and above, and close to zero below 0.2. Real held-out questions have a median similarity of 0.23 to 0.27 to the RL pools. Sampling shows the same pattern: pass@1 rose from 24.0% to 25.0% and pass@64 went from 64.7% to 62.1%, so RL sharpened skills the model already had.

{{ m.fig('/assets/img/llm/post-transfer.webp', '(a) Accuracy before and after GRPO on trained problems, other papers, and real held-out questions. (b) The gain grows with similarity to a trained question. (c, d) How program validity and log-probabilities changed.', wide=True) }}

### Measurement pitfalls

The repository's [PITFALLS.md](https://github.com/jiazhe868/nanogpt-seis-posttrain/blob/main/PITFALLS.md) records 15 failures in detail, and almost all of them are measurement problems. Four examples:

{{ m.figrow([
  {'src': '/assets/img/llm/post-pitfall-leakage.webp', 'caption': '**Leakage.** A pair-level split put every validation source paper in training. 39% of an apparent gain came from the leak.'},
  {'src': '/assets/img/llm/post-pitfall-circular.webp', 'caption': '**Circular evaluation.** A +590% reward headline was 73% format compliance. Held-out accuracy did not change significantly.'},
  {'src': '/assets/img/llm/post-pitfall-decoding.webp', 'caption': '**Decoding.** Raising the repetition penalty from 1.05 to 1.2 doubled SFT accuracy and flipped the sign of the SFT-to-RL comparison.'},
  {'src': '/assets/img/llm/post-pitfall-metric.webp', 'caption': '**Metric floor.** Under the first scoring rule, a blind spray of numbers beat the trained model. The fixed rule has a 5.9% floor and an 86.1% ceiling.'},
], wide=True) }}

## Stage 3 · Post-training Qwen3.5-9B

[qwen-seis-posttrain](https://github.com/jiazhe868/qwen-seis-posttrain) applies the recipe to Qwen3.5-9B on a shared Slurm cluster of 8 nodes with 3 A100-40GB GPUs each and no NVLink. The stack is verl with the Megatron engine for training and vLLM for rollouts, laid out as TP1 × PP8 × DP3 with 24 vLLM replicas on the same GPUs. Qwen3.8-27B wrote the SFT solutions and checked labels, Gemma 4 26B-A4B served as the reward judge, and a second judge that never touched training scored the written reports.

{{ m.fig('/assets/img/llm/qwen-workflow.webp', 'Qwen3.5-9B on D-Num-hard after SFT on 13,095 conversations and after 20 RL steps on a bank of 36,884 problems, with the mean answer length in tokens.', wide=True) }}

### Tests first

The test sets were frozen before any training data existed, with content hashes and canary strings, and the evaluation code cannot import the reward code. The domain sets are D-Num (300 numerical problems from 10 held-out families), D-Num-hard (160 multi-step problems), D-Fresh (60 problems written after the model's release), D-Code (150 tasks with hidden tests), and D-Report (100 reports judged pairwise against the base). General benchmarks are GPQA Diamond, MMLU-Pro, IFEval, LiveCodeBench, tool calling, and a 650-prompt refusal set. Every model, the base included, runs through one harness at temperature 1.0 with up to 32K output tokens.

### Data and rewards

The RL bank started with 57,037 generated problems. Filters for quality, MinHash duplicates, contamination, label verification, and difficulty left 36,884 in four task types: numerical, code, reports, and general instructions. For verification, the teacher solved 20 problems from each template 4 times and a judge ruled, and 20 of 102 templates were rejected whole. Contamination checks combine 13-gram and MinHash overlap, embedding similarity confirmed by an LLM judge, and answer matching. They removed 3.3% of the RL bank and 2.3% of the SFT data.

SFT used 13,095 conversations (44.1M tokens): verified teacher solutions, tool-use trajectories whose code passed hidden tests, judged reports, and replayed answers from the base model. Full-parameter training took 2 epochs, 206 steps, and 2.3 hours, and length bucketing cut padding from 33% to 1.9%. Rewards depend on the task: a solver-checked value within tolerance and with the right unit, the share of hidden unit tests passed in an Apptainer sandbox, a judged rubric score with a penalty for references that Crossref cannot verify, and programmatic checks of instruction constraints.

### The RL run

Each step samples 8 answers for each of 126 prompts (1,008 samples) with a 16K-token cap. The advantage is the reward minus its group mean, without division by the group's standard deviation, and answers cut off at the cap get zero advantage. The loss is a clipped PPO-style surrogate with asymmetric clipping (0.2 and 0.28) and no KL term. A truncated importance weight, min(π<sub>train</sub>/π<sub>rollout</sub>, 2), corrects for the numerical mismatch between the vLLM sampler and the Megatron trainer, and a monitor pauses the run when that mismatch grows. A step took about 4 minutes. Dev accuracy on numerical problems went from 92.0 to 97.3 at step 20 and down to 78.9 by step 40. The monitor stopped the run at step 56, and dev selection kept step 20.

{{ m.fig('/assets/img/llm/qwen-rl-steps.webp', 'Answer length, training accuracy, and groups with no learning signal at each RL step, for three task types. The run improved for 20 steps and then collapsed. The cause is under investigation.', wide=True) }}

### Results

{{ m.table(['Test set', 'Base', 'SFT', 'RL step 20'], [
  ['D-Num (300 problems, avg@8)', '**91.6**', '89.4', '89.2'],
  ['D-Num-hard (160)', '62.0', '68.1', '**70.1**'],
  ['D-Fresh (60, written after release)', '70.6', '78.8', '**83.3**'],
  ['D-Code (150, hidden tests)', '80.5', '**86.3**', '85.2'],
  ['GPQA Diamond (198)', '56.6', '71.3', '**74.2**'],
  ['LiveCodeBench, after 2025-01 (70)', '38.2', '**52.5**', '50.0'],
  ['IFEval (377)', '93.1', '93.1', '**93.9**'],
  ['Mean output tokens', '14,735', '9,517', '**5,637**'],
], num_cols=[1, 2, 3]) }}

SFT raised D-Num-hard by 6.1 points, D-Fresh by 8.1, D-Code by 5.8, and GPQA Diamond by 14.7, and it cut answer length by 35%. It also lowered D-Num by 2.2 points, outside the noise band measured over 10 base seeds. RL cut answer length by another 41%. At the full 32K budget its gains over SFT on D-Num-hard (+1.9, 95% CI −0.7 to +4.6) and D-Fresh (+4.6, CI −0.8 to +10.4) are inside the noise. At a 16K budget RL leads SFT by 10.2 points on D-Num-hard. The write-up concludes that this run made the model faster and did not make it more reliable. Refusals on prompts that should be refused fell from 56.0% to 45.7%, a regression that held under a broader refusal detector.

{{ m.fig('/assets/img/llm/qwen-results.webp', 'Scores with 95% intervals for the base, SFT, and RL models on the domain sets and general benchmarks, and the mean answer length.', wide=True) }}

### Where the gains came from

On a strong base model, post-training first buys efficiency. Within an 8K-token budget, the base answers 13.4% of D-Num correctly, SFT 60.0%, and RL 74.6%. Counting outcomes shows the mechanism. On D-Num-hard, unfinished answers fell from 421 to 211 out of 1,280, and wrong final values rose from 15 to 161. Post-training mostly changed when the model stops thinking, and a model that stops earlier is wrong more often. The token budget therefore decides the ranking. RL leads SFT by 10.2 points at 16K and by 1.9 points (within noise) at 32K, and it trails by 6.4 points when cut-off answers are continued to 64K.

{{ m.fig('/assets/img/llm/qwen-samples.webp', 'Outcomes on D-Num and D-Num-hard. Post-training turned unfinished answers into finished ones, and some of them into wrong values.', wide=True) }}

{{ m.fig('/assets/img/llm/qwen-test-time.webp', 'Accuracy against the token budget, and majority voting on D-Num.', wide=True) }}

### Judges and reward design

The reward judge and the independent judge disagreed. On D-Report, Gemma gave SFT an 86.0% win rate against the base, and the evaluation-only judge gave 49.0%. At a pass mark of 70, 8 of Gemma's 108 passes held under the second judge. The SFT reports had been chosen with Gemma, which likely explains the gap. A judged reward needs a second judge that never trains.

How the reward treats a cut-off answer decides where the gradient comes from. In a pilot with a soft length penalty, 29% of all groups got their gradient from the penalty alone, and a correct answer that finished at 23,500 tokens earned a lower advantage (−0.31) than an answer that never finished (0). The difficulty filter had also been run with the base model. Under the SFT policy, 87% of numerical and code groups were all correct in steps 1 to 20, so only 88 to 272 of 1,008 samples per step carried any signal. The redesigned run re-grades the bank with the SFT policy and scores a cut-off numerical answer as wrong.

{{ m.fig('/assets/img/llm/qwen-judges.webp', 'Win rate against the base under the reward judge and the evaluation-only judge, and dev scores at steps 0, 20, and 40.', wide=True) }}

{{ m.fig('/assets/img/llm/qwen-gradient.webp', 'Share of groups with gradient under three rules for cut-off answers, split into real right-versus-wrong signal and penalty-only signal.', wide=True) }}

### Systems

With TP1, the last pipeline stage holds the output layer, the multi-token-prediction head, and its own copy of the embedding, 3.14B parameters in all. At the longest training row it needed 77.7 GiB on a 40 GiB GPU. Adam on the CPU, Transformer Engine's cross entropy, BF16 logits, and a single decoder layer on the first and last stages brought it to 35.6 GiB, checked against an FP32 reference to within 1e‑4 nats per token. The 8-node pre-flight peaked at 40,366 of 40,437 MiB.

Several bugs were silent. verl passed an attention mask that marks the tokens to keep, and Megatron read it as the tokens to drop. Only the unfused A100 path at head dimension 256 applied the mask, so the bug does not appear on an H100. The log-probability gap between trainer and sampler was 1.80 nats per token before the fix and 3e‑4 after. Apptainer was missing on 7 of 8 nodes, so 79% of code rewards were zero until an alert on infrastructure errors caught it. Of the main job's 71.9 hours, 28.7 went to planned stages and 43.2 to incidents, waits, and holds. 21 of the 27 documented pitfalls were silent failures.

{{ m.fig('/assets/img/llm/qwen-memory.webp', 'Memory of the last pipeline stage before (77.7 GiB) and after (35.6 GiB) the fixes, and the SFT memory trace under the 40 GiB limit.', wide=True) }}

{{ m.fig('/assets/img/llm/qwen-hours.webp', 'Where the 71.9 hours of the main 8-node job went: planned stages in blue, incidents and waits in pink.', wide=True) }}

## Lessons across the three projects

{{ m.lessons([
  ('Freeze the tests before the training data exists.', 'The 113M project found 61 of its 153 scored questions word for word in an RL prompt pool, under different ids. The 9B project froze its tests, gates, and selection rules first.'),
  ('Report held-out metrics with paired confidence intervals.', 'Most single GRPO steps on the 113M model looked positive and were inside the noise. Only the larger changes, such as executed equations, were resolved.'),
  ('Pin the decoder before comparing checkpoints.', 'At 113M, the repetition penalty moved accuracy by 7.7 points, 2.3 times the effect of training.'),
  ('Write the cheating completion yourself.', 'A padded answer with filler scored 0.139 above the genuine answer until the echo penalty was normalized by the prompt length.'),
  ('Check where the gradient comes from.', 'A length penalty alone supplied the gradient for 29% of groups, and a difficulty filter run with the wrong model left most groups without signal.'),
  ('Keep one judge out of training.', 'The reward judge rated the SFT reports at 86.0% and the held-out judge at 49.0%.'),
  ('Alert on silent failures.', 'A reward that read a missing field stayed at 0.0000 for 300 steps, and code rewards were zero on nodes without the sandbox.'),
  ('Measure the heaviest stage at the longest sequence.', 'The memory plan said 32.3 GB for the heaviest stage and the measurement said 77.7 GiB.'),
  ('Move computation the model cannot do to a tool.', 'Executed equations took the 113M model from 4.7% to 19.7% on held-out questions.'),
]) }}

## Code and models

{{ m.table(['Project', 'Covers', 'Code', 'Weights'], [
  ['nanoGPT-Seis', 'Data, tokenizer, pretraining, scaling laws, inference', '[GitHub](https://github.com/jiazhe868/nanogpt-seis)', '[nanogpt_seis](https://huggingface.co/jiazhe868/nanogpt_seis)'],
  ['nanoGPT-Seis-Posttrain', 'SFT, GRPO, executed equations, evaluation', '[GitHub](https://github.com/jiazhe868/nanogpt-seis-posttrain)', '[nanogpt_seis_posttrain](https://huggingface.co/jiazhe868/nanogpt_seis_posttrain)'],
  ['qwen-seis-posttrain', 'SFT and multi-task RL of Qwen3.5-9B with verl and Megatron', '[GitHub](https://github.com/jiazhe868/qwen-seis-posttrain)', 'Not yet released'],
]) }}

Each repository has a detailed README in English and Chinese, and the two post-training repositories include a PITFALLS file with every failure, its evidence, and the fix.
