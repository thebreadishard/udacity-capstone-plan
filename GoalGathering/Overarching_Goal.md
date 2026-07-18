# Overarching Capstone Objective: Acquiring Chemically Precise Spectral Lines

## The Core Mission
The ultimate goal of this project is to successfully obtain chemically precise anharmonic infrared spectral lines for complex molecules. While developing a machine learning pipeline to map molecular geometry directly to spectra is a leading strategy to overcome traditional computational bottlenecks, the predictive ML pipeline is only a means to an end. Any approach—whether it involves novel neural architectures, discovering alternative computational pathways, or finding more efficient ways to execute the rigorous math—that reliably and efficiently yields chemically precise spectra is a valid path forward. Attaining that exact precision is the true north.

## Project Scope and Progression
- **Long-Term Target:** Complex Polycyclic Aromatic Hydrocarbons (PAHs).
- **Starting Scope:** Start as small as necessary. There is no requirement to begin with massive aromatic rings; the pipeline can be constructed and validated on small molecules (such as those found in QM9 or ANI-1ccx test sets) to ensure the technical mechanics are flawless before attempting to scale up.
- **Approach:** Leverage the absolute latest developments in the field (e.g. recent continuous-filter potentials that produce smooth PES landscapes). Do not reinvent the wheel or re-do things unnecessarily if a robust modern architecture already exists.

## The Prime Directive: Absolute Chemical Precision
The most critical pillar of this project is the integrity of the data. 

- **100% Chemical Precision:** The Training Set, Validation Set, and Test Set **must** be chemically precise (typically defined as < 1 kcal/mol error / sub-wavenumber precision, originating from gold-standard CCSD(T) or Complete Basis Set limit calculations).
- **Strict Adherence:** We are aiming to maintain this level of precision for 100% of the project stages.
- **Rules for Deviation:** We will only deviate from absolute chemical precision if there is absolutely no other technical solution available, AND only with an extremely compelling, well-documented reason. Compromising the mathematical accuracy of the baseline sets is the absolute last resort.
