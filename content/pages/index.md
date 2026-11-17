---
permalink: /
template: home.html
head_title: Zhe Jia · AI scientist and seismologist
description: >-
  Zhe Jia, Research Assistant Professor at UT Austin. Training language models end to end,
  from pretraining to reinforcement learning, building sim-to-real models for sensor
  arrays, and studying how large earthquakes rupture.

hero:
  eyebrow: AI scientist · Seismologist · UT Austin
  lead: >-
    I train machine learning models end to end, from data pipelines and pretraining to
    fine-tuning, reinforcement learning, and evaluation. I also build models for physical
    sensor data and study how large earthquakes rupture. I am a Research Assistant Professor
    at the [Institute for Geophysics](https://ig.utexas.edu), The University of Texas at Austin.
  buttons:
    - {label: The LLM lifecycle, url: /llm/}
    - {label: Earthquake gallery, url: /earthquakes/}
  photo: /assets/img/zhe_jia_portrait.webp
  photo_caption: At the University of Texas Institute for Geophysics.
  trace_caption: Ground motion at station IU.MAJO in Japan, 76° from the 2023 Mw 7.8 Turkey earthquake
  trace_note: vertical · 40 samples/s · 80 minutes · 0.05–8 Hz

llm:
  label: Language models
  title: The full LLM lifecycle, built from scratch
  text: >-
    Three open repositories cover every stage of a language model, from crawling the data to
    reinforcement learning on a 24-GPU cluster. Every number is measured, and every failure is
    written down with its evidence.
  stages:
    - label: Stage 1 · Pretraining
      title: nanoGPT-Seis
      repo: jiazhe868/nanogpt-seis
      image: /assets/img/llm/pretrain-scaling.webp
      image_caption: IsoFLOP profiles and the compute-optimal frontier from 25 muP runs.
      text: >-
        A 113M-parameter GPT pretrained from scratch on earthquake science and general text,
        with a crawler, MinHash deduplication, a BPE tokenizer, a GQA and RoPE decoder,
        two-GPU DDP training, and a scaling-law sweep.
      facts:
        - [Parameters, 113M]
        - [Training tokens, 822.7M]
        - [Hardware, "2× A30, 6.5 h"]
        - [Optimal size, "N ∝ C<sup>0.69</sup>"]
      links:
        - {label: Code, url: "https://github.com/jiazhe868/nanogpt-seis", icon: github}
        - {label: Model, url: "https://huggingface.co/jiazhe868/nanogpt_seis", icon: hf}
    - label: Stage 2 · Post-training
      title: nanoGPT-Seis-Posttrain
      repo: jiazhe868/nanogpt-seis-posttrain
      image: /assets/img/llm/post-general-models.webp
      image_caption: The 113M model against general Qwen models on held-out seismology questions.
      text: >-
        SFT and GRPO-style RL with programmatic verifiers, then executed equations so that an
        interpreter does the arithmetic. Held-out accuracy on numerical seismology questions
        rose from 4.7% to 27.9%.
      facts:
        - [Held-out accuracy, 4.7% → 27.9%]
        - [vs Qwen3.5-2B, +10.4 points]
        - [Teacher, Qwen3.8-27B on 2 GPUs]
        - [Pitfalls documented, "15"]
      links:
        - {label: Code, url: "https://github.com/jiazhe868/nanogpt-seis-posttrain", icon: github}
        - {label: Model, url: "https://huggingface.co/jiazhe868/nanogpt_seis_posttrain", icon: hf}
    - label: Stage 3 · Scale-up
      title: qwen-seis-posttrain
      repo: jiazhe868/qwen-seis-posttrain
      image: /assets/img/llm/qwen-samples.webp
      image_caption: Where the answers go after SFT and RL on two numerical test sets.
      text: >-
        Full-parameter SFT and multi-task RL of Qwen3.5-9B with verl, Megatron, and vLLM on
        8 nodes of 3 A100 GPUs, with frozen test sets, two judges, contamination checks, and
        an account of 27 failures.
      facts:
        - [D-Num-hard, 62.0 → 70.1]
        - [GPQA Diamond, 56.6 → 74.2]
        - [Tokens per answer, −62%]
        - [Cluster, 24 × A100-40GB]
      links:
        - {label: Code, url: "https://github.com/jiazhe868/qwen-seis-posttrain", icon: github}
        - {label: Write-up, url: "/llm/#stage-3-post-training-qwen35-9b", icon: arrow}
  more: {label: Read the full write-up, url: /llm/}

features:
  - id: sensoformer
    label: Scientific machine learning
    title: Sensoformer
    text: >-
      A set transformer that reads seismograms from any set of stations and returns an
      earthquake's magnitude and focal mechanism in one forward pass. Physics-structured domain
      randomization lets it learn from 100,000 simulations and transfer to real data.
    points:
      - "**19.7°** median error on held-out real earthquakes, equal to the uncertainty of the catalog labels"
      - "**78%** smaller gap between simulated and real embeddings after domain randomization"
      - "**10%** of the real labels outperform training from scratch on all of them"
      - "**+31.8%** more reliable focal mechanisms across the Southern California catalog"
    image: /assets/img/sensoformer/architecture.webp
    image_caption: The Sensoformer architecture and its two-stage training pipeline.
    links:
      - {label: Project page, url: /sensoformer/}
      - {label: arXiv, url: "https://arxiv.org/abs/2601.06320"}
      - {label: Code, url: "https://github.com/jiazhe868/Sensoformer"}
  - id: submit
    flip: true
    label: Earthquake source inversion
    title: SubMIT
    text: >-
      Bayesian subevent inversion for large earthquakes, and the method behind my studies of the
      Fiji, Ridgecrest, South Sandwich Islands, Noto, and Calama earthquakes. One command goes
      from downloaded waveforms to subevent models with uncertainties.
    points:
      - "**Parallel MCMC** over the time, location, depth, and duration of each subevent, with moment tensors solved exactly"
      - "**Automatic choice** of the number of subevents, with a check that the choice is stable"
      - "**Teleseismic and regional** waveforms, with exact timing for each subevent"
    image: /assets/img/submit/concept.webp
    image_caption: A large earthquake as a few subevents, and how stations in different directions see them.
    links:
      - {label: About SubMIT, url: /submit/}
      - {label: Code, url: "https://github.com/jiazhe868/SubMIT"}

quakes:
  label: Earthquake research
  title: How large earthquakes break
  text: >-
    Plain-language summaries of my earthquake studies, from the 2023 Turkey doublet to deep
    earthquakes 600 km below Fiji, with figures from each paper.
  ids: [turkey2023, calama2024, deepeq2025, sandwich2021, fiji2018, ridgecrest2020, noto2024, ridgecrest2019]
  more: Open the earthquake gallery

about_title: Research and background
news_limit: 6
---

I am a Research Assistant Professor at the University of Texas Institute for Geophysics (UTIG), where I lead a group working on machine learning for physical systems and on earthquake physics. Before joining UT Austin in 2024, I was a Cecil H. and Ida M. Green Postdoctoral Fellow at Scripps Institution of Oceanography, UC San Diego. I received my PhD in geophysics from Caltech in 2022, and my BS and MS from the University of Science and Technology of China, where I studied in the School for the Gifted Young.

My current work is on language models and scientific machine learning: pretraining and post-training LLMs, sim-to-real learning for sensor arrays, and neural surrogates for physical simulations. My earthquake research uses Bayesian inversion, high-performance computing, and dynamic rupture simulation to work out how large earthquakes start, grow, and stop. My publications include 23 papers and preprints, two of them in *Science*, with more than 1,300 citations.

I teach Environmental and Earthquake Seismology and Frontiers in Earthquake Physics at UT Austin and advise PhD students and postdocs. [Teaching and mentoring](/teaching/) · [Publications](/publications/) · [CV](/assets/pdf/CV_Zhe.pdf)
