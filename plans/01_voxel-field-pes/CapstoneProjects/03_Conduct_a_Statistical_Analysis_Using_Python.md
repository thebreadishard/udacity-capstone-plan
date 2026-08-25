# Conduct a Statistical Analysis Using Python

## Project Overview

1. APA Resources

   1

   * Using APA Style in the AI Mastery Capstone
   * Writing Your Capstone Reports: Explaining Your Work Clearly and Credibly
   * Finding and Using Sources for Your Capstone Reports
   * APA In-Text Citations and References Made Simple
   * Academic Integrity and Responsible Use in Your Capstone Projects
2. AI Programming Foundations Project

   2

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
3. Conduct a Statistical Analysis Using Python

   3

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
4. Applied Machine Learning: Model Design, Training, and Performance Evaluation

   4

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
5. Deep Learning Systems

   5

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
6. Generative AI Applications

   6

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
7. Design of Autonomous and Semi-Autonomous Agentic Workflows

   7

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
8. Industry-Integrated AI Systems Synthesis

   8

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
9. Professional Industry Defense

   9

   * Project Overview
   * Instructions
   * Project Rubric
   * Submit Project

# Project Overview

## Overview

In this project, you will conduct a complete statistical analysis using the data and statistics skills you developed in your Nanodegree. You will select a dataset, explore it with descriptive statistics, create visualizations, perform at least one hypothesis test, and communicate your findings in a clear and professional way for both technical and non-technical readers.

This project uses only the tools you already know:

* Python
* NumPy
* Pandas
* Matplotlib / Seaborn
* SciPy statistics
* Jupyter Notebooks

You are not training machine learning models yet. This project focuses on statistical reasoning and inference that later ML, Deep Learning, Generative AI, and Agentic AI projects will build on. As part of this work, you must reference the provided scholarly article on reproducible data science to support at least one workflow, reproducibility, or design decision you made in this project. You must also identify and cite at least one additional peer-reviewed scholarly source that supports a relevant analytical or methodological choice in your work.

## Why This Project Matters

Sound statistical reasoning is essential for almost every AI or data science project. Employers expect professionals to:

* Work with real datasets and understand their structure
* Compute and interpret descriptive statistics
* Formulate and test statistical hypotheses
* Create clear visualizations that support conclusions
* Explain results accurately in plain language
* Identify limitations, bias, and data quality issues

This project develops these habits so your later models, systems, and agents are grounded in reliable evidence and quantitative thinking.

## What You Will Build

You will create:

* A Jupyter Notebook (analysis.ipynb) that loads your dataset, computes descriptive statistics, creates visualizations, and performs at least one hypothesis test using appropriate statistical methods.
* A Statistical Analysis Report (module\_summary.pdf) that explains your question, methods, results, limitations, and next steps in clear language for technical and non-technical audiences. This report must include in-text citations and a References section.

## Citation Expectations

In your Statistical Analysis Report, you must use citations when you:

* Refer to statistical definitions or concepts (such as p-values, confidence intervals, or test assumptions)
* Justify why a specific statistical test or method is appropriate
* Discuss best practices for visualization, interpretation, or handling limitations and bias

You do not need to cite your own code, computations, or observations that come directly from your notebook outputs and visualizations. Your report must end with a References section that lists all sources you used (for example, course materials, textbooks, or official documentation).

## Submission Instructions

Make sure your submission includes all of the following components.

### Notebook

* analysis.ipynb runs top to bottom without execution errors
* Dataset loads correctly, and data types are appropriate
* Descriptive statistics are computed and explained
* At least three visualizations are included, each with titles and axis labels
* One hypothesis test is performed with clearly stated null and alternative hypotheses
* A short notebook summary section is included

### Statistical Analysis Report

* module\_summary.pdf is included
* Report contains all required sections:
  + Overview
  + Dataset Description
  + Methods
  + Results
  + Interpretation for a Non-Technical Audience
  + Limitations and Potential Bias
  + References
* Interpretations and conclusions are grounded in the student’s own results and figures
* In-text citations are used where required
* References section uses a consistent citation style
* At least two credible sources are cited, with at least one scholarly source

### Dataset File

* Original dataset file (CSV or other tabular format) is included
* Dataset meets all stated size and content requirements

### requirements.txt

* requirements.txt file is included
* File was generated using:
  pip freeze > requirements.txt

If all items above are present and complete, the project is ready for submission.

---

## Environment Setup

1. APA Resources

   1

   * Using APA Style in the AI Mastery Capstone
   * Writing Your Capstone Reports: Explaining Your Work Clearly and Credibly
   * Finding and Using Sources for Your Capstone Reports
   * APA In-Text Citations and References Made Simple
   * Academic Integrity and Responsible Use in Your Capstone Projects
2. AI Programming Foundations Project

   2

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
3. Conduct a Statistical Analysis Using Python

   3

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
4. Applied Machine Learning: Model Design, Training, and Performance Evaluation

   4

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
5. Deep Learning Systems

   5

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
6. Generative AI Applications

   6

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
7. Design of Autonomous and Semi-Autonomous Agentic Workflows

   7

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
8. Industry-Integrated AI Systems Synthesis

   8

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
9. Professional Industry Defense

   9

   * Project Overview
   * Instructions
   * Project Rubric
   * Submit Project

# Environment Setup

## Local Machine Instructions

Before you begin the project, make sure your environment is set up correctly. This will help you avoid errors and ensure your statistical analysis notebook runs smoothly from start to finish.

1. Install Python 3.x
   1. You can use any recent version of Python 3 (3.9 or higher).
2. Install Jupyter Notebook or JupyterLab
3. You may use any of the following environments:
   1. Jupyter Notebook
   2. JupyterLab
   3. VS Code with the Jupyter Extension
   4. Anaconda (includes Jupyter by default)
4. Install Required Python Libraries
5. Make sure the following libraries are installed:
   1. NumPy
   2. Pandas
   3. Matplotlib
   4. Seaborn
   5. SciPy (for hypothesis testing)
6. If you are using Anaconda, these libraries may already be available.

### Validate Your Environment

1. Open a new Jupyter Notebook
2. Run this code:

```
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pandas as pd
```

3. Load the dataset
4. Create Your requirements.txt File
5. Generate a reproducibility file

---

## Instructions

1. APA Resources

   1

   * Using APA Style in the AI Mastery Capstone
   * Writing Your Capstone Reports: Explaining Your Work Clearly and Credibly
   * Finding and Using Sources for Your Capstone Reports
   * APA In-Text Citations and References Made Simple
   * Academic Integrity and Responsible Use in Your Capstone Projects
2. AI Programming Foundations Project

   2

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
3. Conduct a Statistical Analysis Using Python

   3

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
4. Applied Machine Learning: Model Design, Training, and Performance Evaluation

   4

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
5. Deep Learning Systems

   5

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
6. Generative AI Applications

   6

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
7. Design of Autonomous and Semi-Autonomous Agentic Workflows

   7

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
8. Industry-Integrated AI Systems Synthesis

   8

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
9. Professional Industry Defense

   9

   * Project Overview
   * Instructions
   * Project Rubric
   * Submit Project

# Instructions

## Project 2 — Data and Statistical Reasoning

Complete Statistical Analysis with Descriptive Statistics, Visualization, Hypothesis Testing, and Interpretation

## What You Will Submit

* analysis.ipynb
* Statistical\_Analysis\_Report.pdf
* requirements.txt
* Your dataset file (CSV)

## Project Instructions

### Task 1 — Choose Your Dataset

For this project, you must find your own dataset. Selecting an appropriate dataset is part of the assessment.

#### Dataset Requirements

Your dataset must:

* Have at least 500 rows
* Have at least 6 columns
* Include at least:
  + one numeric variable
  + one categorical or grouping variable
* Be in CSV or another tabular format
* Be publicly available and appropriate for academic use
* Not be synthetic or AI-generated
* Not the same dataset used in Project 1

#### Accepted Sources

* Kaggle Datasets
* UCI Machine Learning Repository
* Data.gov
* FiveThirtyEight Data
* Open government data portals

Download your dataset and place it in the same folder as your notebook.

### Task 2 — Load Your Dataset

In analysis.ipynb:

* Load your dataset
* Display the first few rows using df.head
* Confirm that all columns and data types loaded correctly

This ensures your project begins with usable data.

### Task 3 — Conduct Descriptive Statistics

Compute and explore:

* Summary statistics using df.describe
* Counts of categorical values
* Distributions of key numeric variables

Add short Markdown notes explaining what these statistics reveal about your dataset.

### Task 4 — Create and Compare Three Visual Models of the Dataset

Create at least three visual models that represent patterns in your real-world dataset using Matplotlib or Seaborn. In this project, a visual model means a graph or chart that helps model, represent, or explain a pattern in the data. These are not machine-learning, deep-learning, neural-network, or predictive models.

Examples include:

* Histogram
* Boxplot
* Scatterplot
* Bar chart
* Correlation heatmap

Each visual model must include:

* A descriptive title
* Clearly labeled axes

After creating the visual models, add Markdown notes comparing them. Explain what each visual model reveals about the dataset and identify which visual model best supports your analytical question.

### Task 5 — Perform One Hypothesis Test

Choose a hypothesis test that fits your dataset and analytical question. Examples include:

* t-test
* chi-square test
* correlation test
* ANOVA

Your notebook must include:

* The null and alternative hypotheses in Markdown
* Code that performs the test
* The resulting test statistic and p-value

Full interpretation will be included in your written report.

### Task 6 — Write a Short Notebook Summary

Add a brief Markdown section (4 to 6 sentences) describing:

* What you explored
* Any interesting or unexpected findings
* Any challenges you encountered

This concludes your notebook.

### Task 7 — Write the Statistical Analysis Report with Academic Citations

Create a file named Statistical\_Analysis\_Report.pdf. As part of this report, you must read and cite the required peer-reviewed article [Initial Data Analysis for Longitudinal Studies to Build a Solid Foundation for Reproducible Analysis(opens in a new tab)](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0295726&utm_source=chatgpt.com). You must use this article to support at least one statistical method, assumption, or analytical decision you made in this project (for example, choice of descriptive statistics, hypothesis testing approach, or interpretation of results).

In addition, you must find and cite at least one other peer-reviewed scholarly source that supports a relevant statistical best-practice claim in your report. Both sources must appear as in-text citations and in the References section of Statistical\_Analysis\_Report.pdf.

Statistical\_Analysis\_Report.pdf should also have the following sections:

#### Overview

Write 2 to 4 sentences explaining what you analyzed and why. Include the dataset name and source link.

#### Dataset Description

Write 3 to 6 sentences describing:

* What the dataset represents
* Number of rows and columns
* Key variables examined

#### Methods

Explain:

* Why you selected your descriptive statistics
* Why you chose each type of model
* Why your hypothesis test was appropriate
* Any assumptions required for the test

#### Results

Summarize the main findings and reference the figures in your notebook.

#### Interpretation for a Non-Technical Audience

Explain what your results mean in clear language suitable for readers without statistical training.

#### Limitations and Potential Bias

Discuss at least one dataset limitation and at least one potential source of bias in the data or interpretation.

#### Citation Requirements

Use academic citations when:

* Defining statistical terms or assumptions
* Justifying test selection
* Explaining best practices
* Discussing bias or limitations

Do not cite your own numerical results or observations.

#### References

Include all sources in a consistent citation style.

### Task 8 — Create requirements.txt

Generate your reproducibility file using:

```
pip freeze > requirements.txt
```

This ensures your analysis can be rerun in an identical environment.

---

## Rubric

1. APA Resources

   1

   * Using APA Style in the AI Mastery Capstone
   * Writing Your Capstone Reports: Explaining Your Work Clearly and Credibly
   * Finding and Using Sources for Your Capstone Reports
   * APA In-Text Citations and References Made Simple
   * Academic Integrity and Responsible Use in Your Capstone Projects
2. AI Programming Foundations Project

   2

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
3. Conduct a Statistical Analysis Using Python

   3

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
4. Applied Machine Learning: Model Design, Training, and Performance Evaluation

   4

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
5. Deep Learning Systems

   5

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
6. Generative AI Applications

   6

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
7. Design of Autonomous and Semi-Autonomous Agentic Workflows

   7

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
8. Industry-Integrated AI Systems Synthesis

   8

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
9. Professional Industry Defense

   9

   * Project Overview
   * Instructions
   * Project Rubric
   * Submit Project

# Rubric

Use this project rubric to understand and assess the project criteria.

## Technical Implementation

| Criteria | Submission Requirements |
| --- | --- |
| Data Ingestion | Dataset loads correctly in the notebook and displays without errors. |
| Descriptive Statistics | Notebook includes summary statistics, categorical counts, and distribution exploration. |
| Visualizations | At least three visual models are present for the data set, each with a clear title and labeled axes. |
| Hypothesis Test | One valid hypothesis test is performed, including clearly stated hypotheses, a test statistic, and a p-value. |
| Notebook Summary | Notebook ends with a summary of findings and challenges. |
| Reproducibility | A text file is created using pip freeze is included in the submission. |
| Interpretation of Statistics | Descriptive statistics are interpreted accurately in the written report. |
| Test Selection Justification | The written report explains why the chosen hypothesis test is appropriate for the dataset and analytical question. |
| Results Interpretation | The written report correctly interprets the hypothesis test results and the patterns observed in the visualizations. |
| Limitations and Bias | The written report identifies at least one dataset limitation and one potential source of bias with explanation. |
| Citation Requirements | The written report includes citations for statistical concepts, methodological choices, and assumptions, and concludes with a references section. |
| Report Organization and Clarity | Statistical\_Analysis\_Report.pdf contains all required sections and communicates results in a clear and organized manner. |
| Non-Technical Explanation | The report includes a clear explanation of findings intended for non-technical audiences. |
| Dataset Appropriateness | The dataset meets all project requirements and is appropriate for descriptive statistics and hypothesis testing. |
| Workflow Completeness | Submission resembles a complete, professional statistical analysis workflow suitable for a student portfolio. |

## Analytical Reasoning

| Criteria | Submission Requirements |
| --- | --- |
| Experimental Design Justification | The student explains how the three different visual models reveal about the dataset and which visual model best supports their analytical question. |
| Performance Evaluation and Comparison | The student compares results from across visual models using appropriate metrics and clearly explains observed trade-offs between the different visual models and how they represent the real-world data. |
| Results Interpretation | The student interprets model behavior using the student’s actual training and evaluation results, not generic statements. |

## Ethical and Responsible Practice

| Criteria | Submission Requirements |
| --- | --- |
| Bias and Risk Awareness | The student identifies at least one potential ethical concern, bias, or misuse risk related to the dataset, model, or application domain and explains its implications. |

## Communication and Presentation

| Criteria | Submission Requirements |
| --- | --- |
| Notebook Organization | The notebook uses clear markdown headings to separate data handling, model definition, training, evaluation, and summary sections. |
| Code Readability and Documentation | Code is readable, logically organized, and includes comments or docstrings where appropriate. |
| Written Analysis Quality | module\_summary.pdf includes all required sections and communicates ideas clearly for both technical and non-technical readers. |
| Use of Citations | module\_summary.pdf uses in-text citations when referencing deep learning concepts, architectural patterns, training practices, or ethical considerations and includes a References section. |

## Integration and Professional Relevance

| Criteria | Submission Requirements |
| --- | --- |
| Workflow Completeness and Portfolio Readiness | The submission represents a complete deep learning experiment and analysis suitable for inclusion in a professional portfolio or applied research context. |

## Marvin AI

New Chat

View Chat History

Provide Feedback

Did I read somewhere that the dataset selected for the "Conduct a Statistical Analysis Using Python" course of the Capstone project cannot be the same as the dataset used for the "AI Programming Foundations Project" course?

Yes — that’s stated on the page you’re viewing now.

The dataset requirements say your dataset must be:

* not synthetic or AI-generated
* publicly available
* and **not the same dataset used in Project 1**

So if your “AI Programming Foundations Project” was Project 1, then you should choose a different dataset for this statistical analysis project.

If you want, I can also help you sanity-check whether a dataset you’re considering would meet all the project requirements.

Copy

This response was helpful.

This response was not helpful.

Regenerate

But how is that consistent with the sentence in the first project overview that "This project focuses on building the workflow that later ML, Deep Learning, Generative AI, and Agentic AI projects will build on." Doesn't that also apply to the second project, and therefor not to one of the two, since if you are building on one of the two datasets later, you won't be building on the other.

I think those two statements are talking about different things.

“This project focuses on building the workflow that later … projects will build on” means the later projects build on the **skills/process** — loading data, cleaning, exploring, visualizing, documenting, using Git — not that they must literally reuse the **same dataset**.

So it’s consistent for Udacity to say both:

* Project 1 teaches the reproducible workflow foundation.
* Project 2 must use a different dataset from Project 1.

In other words, what carries forward is the **workflow**, not the specific data. If you want, I can help you interpret the exact dataset rule for Project 2 more carefully by checking the project requirements text.

Copy

This response was helpful.

This response was not helpful.

Regenerate

Yes please

I checked the lesson content around this project, and in the material I can see for the **AI Programming Foundations Project**, there’s no rule saying its dataset must differ from a later project’s dataset. The instructions here only say your dataset must meet size/format/safety requirements.

So the “not the same dataset used in Project 1” rule appears to belong to the later statistical analysis project, not this first one. That makes the logic one-way:

* Project 1: choose any valid dataset.
* Project 2: choose a valid dataset that is **different from Project 1**.

So your interpretation is right that “later projects build on this” refers to the **workflow and skills**, not a promise that every later project will reuse the same dataset. If you want, I can help you think through why Udacity might intentionally require a different dataset for Project 2.

Copy

This response was helpful.

This response was not helpful.

Regenerate

Why is that? Because project 2 does other things than project 1, and in my opinion could take the first project's status a bit further.

That’s a reasonable critique. Pedagogically, reusing the same dataset across projects could make sense because it lets you go deeper instead of restarting context each time.

My best read is that Udacity likely wants Project 2 to test **transfer**: can you apply the same workflow/statistical thinking to a new dataset, not just keep polishing one you already know well? Using a different dataset also reduces the chance that Project 2 becomes mostly a continuation of earlier cleaning/EDA work rather than fresh analysis.

So I’d frame it as:

* reusing the same dataset would emphasize **depth**
* requiring a new dataset emphasizes **generalization**

Neither is inherently wrong — it’s just a curriculum design choice. If you want, I can help you pick a Project 2 dataset that still feels close to your Project 1 topic so you keep some continuity without violating the rule.

Copy

This response was helpful.

This response was not helpful.

Regenerate

No, it's okay. I think I want to use the Nasa Ames PAHdb for project 1.

That could be a strong choice for Project 1 if you can turn it into a clean tabular dataset for loading with Pandas and doing EDA/visualization.

Just sanity-check a few things:

* it should be publicly available
* ideally CSV or another easy tabular format
* enough rows/columns to support cleaning and visualization
* variables that let you tell a clear story, not just dump scientific measurements

A good test is: can you imagine at least 2 cleaning steps, 1 EDA function, and 3 meaningful plots from it? If yes, it’s probably workable. If you want, I can help you pressure-test that dataset against the project tasks before you commit.

Copy

This response was helpful.

This response was not helpful.

Regenerate

Okay, I will use another dataset, QM9, for the Foundations Project.

That sounds like a safer pick. QM9 is structured enough that you should be able to load it, clean it, explore relationships, and make a few solid visualizations.

Before you commit, just verify:

* you have it in a tabular format you can read easily with Pandas
* it has at least 200 rows and 5 columns
* you can explain what the columns mean in plain language
* you can identify a few interesting numeric relationships to visualize

If you want, I can help you sketch 2–3 good analysis questions and plot ideas for QM9 without doing the project for you.

Copy

This response was helpful.

This response was not helpful.

Regenerate

It contains 134,000 molecules.

That’s plenty — 134,000 rows easily clears the minimum size requirement.

The main question now isn’t “is it big enough?” but “is it manageable for a clean notebook?” With QM9, you’ll probably want to work with a subset of columns and maybe a sample of rows for plotting so your notebook stays readable and fast.

A good direction is to focus on:

* a few molecular descriptors/properties
* missing values or odd ranges as cleaning targets
* relationships between 2–3 numeric variables for plots

If you want, I can help you narrow QM9 into a simple Project 1 scope that won’t become overwhelming.

Copy

This response was helpful.

This response was not helpful.

Regenerate

Summarize this pageQuiz me on this pageGive me a practice exercise for this pageCatch me up on what came before

Add workspace files

---

## Project: Conduct a Statistical Analysis Using Python

1. APA Resources

   1

   * Using APA Style in the AI Mastery Capstone
   * Writing Your Capstone Reports: Explaining Your Work Clearly and Credibly
   * Finding and Using Sources for Your Capstone Reports
   * APA In-Text Citations and References Made Simple
   * Academic Integrity and Responsible Use in Your Capstone Projects
2. AI Programming Foundations Project

   2

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
3. Conduct a Statistical Analysis Using Python

   3

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
4. Applied Machine Learning: Model Design, Training, and Performance Evaluation

   4

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
5. Deep Learning Systems

   5

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
6. Generative AI Applications

   6

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
7. Design of Autonomous and Semi-Autonomous Agentic Workflows

   7

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
8. Industry-Integrated AI Systems Synthesis

   8

   * Project Overview
   * Environment Setup
   * Instructions
   * Project Rubric
   * Submit Project
9. Professional Industry Defense

   9

   * Project Overview
   * Instructions
   * Project Rubric
   * Submit Project

# Project: Conduct a Statistical Analysis Using Python

## Submit Project

Zip FilePublic GitHub Repository

Upload Zip File

Compress your project file(s) into a single zip file on your computer. 500 MB limit (uncompressed).

Choose File

Select Public GitHub Repository

Connected with the account **thebreadishard**. Please ensure that your project is on the default branch.

udacity-data-visualizationudacity-data-wranglingudacity-investigate-a-datasetai-programming-foundations-projectudacity-beavers-choiceudacity-udaplayudacity-innovatenextudacity-agentsville-trip-plannerudacity-idoouudacity-omnitrainer-multimodaludacity-nasa-rag-chat-projectteach-llm-to-countsentiment-scopepcep\_projectface-generatorlandmark\_classifiermnist\_handwritten\_digitspdsnd\_githubCosmicNetworkSim1cd0428-landing-pagepersonal-blog-websitefendcourse-JS-and-the-DOMcd2073-intro-to-js-1-project-starterRock-Paper-Scissorsmeme-generatorcd0010-advanced-python-techniques-project-starterJavascript

## Marvin AI

New Chat

View Chat History

Provide Feedback

Did I read somewhere that the dataset selected for the "Conduct a Statistical Analysis Using Python" course of the Capstone project cannot be the same as the dataset used for the "AI Programming Foundations Project" course?

Yes — that’s stated on the page you’re viewing now.

The dataset requirements say your dataset must be:

* not synthetic or AI-generated
* publicly available
* and **not the same dataset used in Project 1**

So if your “AI Programming Foundations Project” was Project 1, then you should choose a different dataset for this statistical analysis project.

If you want, I can also help you sanity-check whether a dataset you’re considering would meet all the project requirements.

Copy

This response was helpful.

This response was not helpful.

Regenerate

But how is that consistent with the sentence in the first project overview that "This project focuses on building the workflow that later ML, Deep Learning, Generative AI, and Agentic AI projects will build on." Doesn't that also apply to the second project, and therefor not to one of the two, since if you are building on one of the two datasets later, you won't be building on the other.

I think those two statements are talking about different things.

“This project focuses on building the workflow that later … projects will build on” means the later projects build on the **skills/process** — loading data, cleaning, exploring, visualizing, documenting, using Git — not that they must literally reuse the **same dataset**.

So it’s consistent for Udacity to say both:

* Project 1 teaches the reproducible workflow foundation.
* Project 2 must use a different dataset from Project 1.

In other words, what carries forward is the **workflow**, not the specific data. If you want, I can help you interpret the exact dataset rule for Project 2 more carefully by checking the project requirements text.

Copy

This response was helpful.

This response was not helpful.

Regenerate

Yes please

I checked the lesson content around this project, and in the material I can see for the **AI Programming Foundations Project**, there’s no rule saying its dataset must differ from a later project’s dataset. The instructions here only say your dataset must meet size/format/safety requirements.

So the “not the same dataset used in Project 1” rule appears to belong to the later statistical analysis project, not this first one. That makes the logic one-way:

* Project 1: choose any valid dataset.
* Project 2: choose a valid dataset that is **different from Project 1**.

So your interpretation is right that “later projects build on this” refers to the **workflow and skills**, not a promise that every later project will reuse the same dataset. If you want, I can help you think through why Udacity might intentionally require a different dataset for Project 2.

Copy

This response was helpful.

This response was not helpful.

Regenerate

Why is that? Because project 2 does other things than project 1, and in my opinion could take the first project's status a bit further.

That’s a reasonable critique. Pedagogically, reusing the same dataset across projects could make sense because it lets you go deeper instead of restarting context each time.

My best read is that Udacity likely wants Project 2 to test **transfer**: can you apply the same workflow/statistical thinking to a new dataset, not just keep polishing one you already know well? Using a different dataset also reduces the chance that Project 2 becomes mostly a continuation of earlier cleaning/EDA work rather than fresh analysis.

So I’d frame it as:

* reusing the same dataset would emphasize **depth**
* requiring a new dataset emphasizes **generalization**

Neither is inherently wrong — it’s just a curriculum design choice. If you want, I can help you pick a Project 2 dataset that still feels close to your Project 1 topic so you keep some continuity without violating the rule.

Copy

This response was helpful.

This response was not helpful.

Regenerate

No, it's okay. I think I want to use the Nasa Ames PAHdb for project 1.

That could be a strong choice for Project 1 if you can turn it into a clean tabular dataset for loading with Pandas and doing EDA/visualization.

Just sanity-check a few things:

* it should be publicly available
* ideally CSV or another easy tabular format
* enough rows/columns to support cleaning and visualization
* variables that let you tell a clear story, not just dump scientific measurements

A good test is: can you imagine at least 2 cleaning steps, 1 EDA function, and 3 meaningful plots from it? If yes, it’s probably workable. If you want, I can help you pressure-test that dataset against the project tasks before you commit.

Copy

This response was helpful.

This response was not helpful.

Regenerate

Okay, I will use another dataset, QM9, for the Foundations Project.

That sounds like a safer pick. QM9 is structured enough that you should be able to load it, clean it, explore relationships, and make a few solid visualizations.

Before you commit, just verify:

* you have it in a tabular format you can read easily with Pandas
* it has at least 200 rows and 5 columns
* you can explain what the columns mean in plain language
* you can identify a few interesting numeric relationships to visualize

If you want, I can help you sketch 2–3 good analysis questions and plot ideas for QM9 without doing the project for you.

Copy

This response was helpful.

This response was not helpful.

Regenerate

It contains 134,000 molecules.

That’s plenty — 134,000 rows easily clears the minimum size requirement.

The main question now isn’t “is it big enough?” but “is it manageable for a clean notebook?” With QM9, you’ll probably want to work with a subset of columns and maybe a sample of rows for plotting so your notebook stays readable and fast.

A good direction is to focus on:

* a few molecular descriptors/properties
* missing values or odd ranges as cleaning targets
* relationships between 2–3 numeric variables for plots

If you want, I can help you narrow QM9 into a simple Project 1 scope that won’t become overwhelming.

Copy

This response was helpful.

This response was not helpful.

Regenerate

Summarize this pageQuiz me on this pageGive me a practice exercise for this pageCatch me up on what came before

Add workspace files

---

