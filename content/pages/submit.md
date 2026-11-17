---
title: SubMIT
permalink: /submit/
template: page.html
section: /earthquakes/
toc: true
eyebrow: Earthquake source inversion
heading: "SubMIT: subevent inversion for large earthquakes"
description: >-
  SubMIT describes a large earthquake as a few subevents and finds them by Bayesian
  sampling of global and regional seismograms. It is the method behind studies of the
  Fiji, Ridgecrest, South Sandwich Islands, Noto, and Calama earthquakes.
lead: >-
  SubMIT describes a large earthquake as a small number of subevents, each with its own
  time, location, depth, duration, and type of faulting. It fits global and regional
  seismograms with parallel Bayesian sampling, decides how many subevents the data
  support, and reports the uncertainty of every parameter. It is the method behind my
  studies of the Fiji, Ridgecrest, South Sandwich Islands, Noto, and Calama earthquakes.
links:
  - label: Code on GitHub
    url: https://github.com/jiazhe868/SubMIT
    icon: github
  - label: Earthquake gallery
    url: /earthquakes/
    icon: arrow
---

## Why subevents

A large earthquake is not a single instant of slip. The rupture spreads along the fault for seconds to minutes, and on the way it can change position, depth, and style of faulting. A single point source cannot reproduce the seismograms of such a rupture. A few subevents can. Each one is a short burst of slip with its own start time, location, depth, duration, size, and moment tensor.

Subevents at different places produce a signature that stations can see. A station that the rupture runs toward records the bursts bunched together, and a station on the other side records them spread out. Fitting many stations at once recovers where and when each burst happened.

{{ m.fig('/assets/img/submit/concept.webp', 'The idea in three panels. A large earthquake is modeled as a few subevents (left). Each releases its moment as a smooth pulse (middle). Stations in different directions see the pulses compressed or stretched in time (right). The panels are a schematic built from an example run.', wide=True) }}

## How it works

{{ m.table(['Part', 'What SubMIT does'], [
  ['Parameters', 'Each subevent has a time, horizontal position, depth, and duration, which are sampled. Its five moment-tensor components are solved exactly for every sample by damped least squares, tied to the catalog moment tensor.'],
  ['Data', 'Teleseismic P and SH waves from 40° to 90° (0.005 to 0.2 Hz) and regional three-component waveforms up to about 750 km (0.02 to 0.15 Hz).'],
  ['Green\'s functions', 'Ray theory with a CRUST1.0 source crust for teleseismic waves, and frequency-wavenumber synthetics in a 1D CRUST1.0 model for regional waves, with exact timing for each subevent.'],
  ['Prior', 'A smoothed map of the first week of aftershocks, with background seismicity removed, plus causality and minimum-separation rules.'],
  ['Sampling', 'Up to 32 parallel Metropolis-Hastings chains with adaptive joint moves, relocation moves drawn from the prior, warm starts from the best model with one fewer subevent, and resampling within groups of chains.'],
  ['Model selection', 'The chosen number of subevents is the smallest one whose best misfit is within 5% of the best over all numbers tried. A bootstrap over independent groups of chains reports whether that choice is stable.'],
  ['Uncertainty', '95% intervals for every parameter from the pooled posterior samples, with split R-hat for each parameter as a convergence check.'],
]) }}

The pipeline runs in four steps with one command. It downloads and processes waveforms, computes Green's functions, screens bad stations, builds the prior, runs the inversions for one, two, three, and more subevents, selects the model, and writes the figures and a summary.

{{ m.fig('/assets/img/submit/pipeline.webp', 'From downloaded waveforms to final figures: data processing, preparation, Bayesian inversion with automatic model selection, and results.', wide=True) }}

## Example: the 2024 Calama earthquake

The bundled Chile example is the magnitude 7.4 intermediate-depth earthquake beneath Calama, which I studied in [Nature Communications](/earthquakes/#calama2024). SubMIT selects four subevents within about 17 seconds. They stay within 15 km of the epicenter horizontally, and their depths step down from 126 km to 170 km, so the rupture grew mainly downward through the subducting slab. A five-subevent model, which the published study used, fits only 1.4% worse.

{{ m.fig('/assets/img/submit/chile-subevents.webp', 'Four subevents of the 2024 Calama earthquake: map with mechanisms and 95% uncertainty bars, moment-rate functions, and a depth section from 126 to 170 km.', wide=True) }}

{{ m.fig('/assets/img/submit/model-selection.webp', 'Choosing the number of subevents. Misfit relative to the best model against the number of subevents for the four examples. Stars mark the selected models, inside the 5% band.') }}

{{ m.fig('/assets/img/submit/results-overview.webp', 'Moment-rate functions of the four bundled examples, with each subevent in its own color.', wide=True) }}

The repository includes four examples with their input data: Calama, Chile (2024, Mw 7.4, 4 subevents), offshore Cape Mendocino, California (2024, Mw 7.0, 3 subevents), coastal Venezuela (2026, Mw 7.2, 6 subevents), and Kamchatka (2025, Mw 8.8, 7 subevents). The Venezuela and Kamchatka examples are being re-run with version 3, after the fixes described below changed their station processing and aftershock prior.

## Reliability work in version 3

Version 3 (November 2026) is a rewrite. It followed bug reports from a group of users on the 2026 Mw 7.4 Colombia earthquake, clean-install tests on three earthquakes the code had never seen, and an independent code review that found eleven defects. The repository's [PITFALLS.md](https://github.com/jiazhe868/SubMIT/blob/main/PITFALLS.md) documents each one with its evidence. In most cases the pipeline ran to the end and drew plausible figures. Two examples:

- **Horizontal components of unequal length were left unrotated.** In the Venezuela example, 26 of 56 SH records were really north or east components. The poor fits were first explained as polarity flips and then as a smooth background rupture.
- **One lucky chain could decide the number of subevents.** For one test earthquake, the selected model rested on a single chain, and the median chain was 16.6% worse. Version 3 reports how often independent groups of chains agree and warns when the choice is unstable.

{{ m.fig('/assets/img/submit/data-processing.webp', 'Automatic quality control, from records as downloaded to data ready for the inversion: drift removal, alignment, rejection of wrong amplitudes and flipped channels, and balanced weighting of wave types.') }}

## Studies that use the method

- [2018 Fiji deep earthquake doublet](/earthquakes/#fiji2018), *Earth and Planetary Science Letters* (2020)
- [2019 Ridgecrest multi-fault models](/earthquakes/#ridgecrest2020), *Geophysical Research Letters* (2020)
- [2021 South Sandwich Islands earthquake](/earthquakes/#sandwich2021), *Geophysical Research Letters* (2022)
- [2024 Noto Peninsula earthquake and tsunami](/earthquakes/#noto2024), *Geophysical Research Letters* (2024)
- [2024 Calama earthquake](/earthquakes/#calama2024), *Nature Communications* (2025)

Related subevent analyses include the [40 large deep earthquakes](/earthquakes/#deepeq2025) in *AGU Advances* (2025), which used a related grid-search subevent method, and the [2023 Turkey doublet](/earthquakes/#turkey2023) in *Science* (2023).

## Running it

SubMIT runs on Linux with MPI, C and Fortran compilers, SAC, Java, and a Python 3.12 environment. The core sampler is written in Fortran with MPI and the forward model in C. Each example can be reproduced from its frozen settings or rerun from scratch:

```bash
git clone https://github.com/jiazhe868/SubMIT && cd SubMIT
./submit check                    # are all dependencies installed?
./submit build                    # compile the bundled Green's-function codes
./submit example california       # reproduce the 2024 California M7.0 result (~10 min)
./submit compare california       # check it against the published numbers

./submit prepare /data/myevent && ./submit run /data/myevent    # a new earthquake
```

If you use SubMIT, please cite Jia et al. (2020a, 2020b, 2022a) and Jia et al. (2025a). The full list of references and the seismic networks to acknowledge are in the README.
