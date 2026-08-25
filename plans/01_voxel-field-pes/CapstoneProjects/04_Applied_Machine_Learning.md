# Applied Machine Learning

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

In this project, you will complete a full machine learning workflow using the modeling skills you developed in your Nanodegree. You will select a dataset, prepare and preprocess the data, build and train a supervised or unsupervised machine learning model, evaluate its performance using appropriate metrics, and communicate your results clearly and professionally.

This project uses only the tools you already know:

* Python
* NumPy
* Pandas
* scikit-learn or PyTorch
* Matplotlib / Seaborn
* Jupyter Notebooks

You are building and evaluating machine learning models in this project. The focus is on understanding the end-to-end ML workflow, making appropriate design decisions, and interpreting model performance rather than maximizing accuracy.

## Why This Project Matters

Machine learning models are only as useful as the reasoning behind their design and evaluation. Employers expect professionals to:

* Select and prepare data appropriately for modeling
* Choose models that fit the problem and data characteristics
* Use evaluation metrics that align with the task and goals
* Interpret model performance honestly and accurately
* Communicate results, tradeoffs, and limitations clearly
* Recognize sources of bias and uncertainty in model outcomes

This project develops the analytical judgment required to move from raw data to evaluated predictive insight, which is foundational for more advanced work in deep learning, generative AI, and agentic systems.

## What You Will Build

You will create:

* A Jupyter Notebook (modeling.ipynb) that loads and preprocesses your dataset, builds and trains a machine learning model, evaluates its performance using appropriate metrics, and includes outputs or visualizations that support interpretation.
* A Machine Learning Analysis Report (module\_summary.pdf) that explains your problem, dataset, modeling approach, evaluation results, assumptions, limitations, and potential improvements in clear language for both technical and non-technical audiences. This report must include in-text citations and a References section.

## Citation Expectations

In your Machine Learning Analysis Report, you must use citations when you:

* Refer to machine learning concepts or definitions (such as model types, loss functions, evaluation metrics, or overfitting)
* Justify why a particular model, preprocessing step, or evaluation metric is appropriate
* Discuss best practices related to model evaluation, bias, fairness, or responsible use

You do not need to cite your own code, training results, metrics, or observations that come directly from your notebook outputs and visualizations. Your report must end with a References section that lists all sources you used, such as course materials, textbooks, or official library documentation.

## Submission Instructions

Make sure your submission includes all of the following components.

### Notebook

* modeling.ipynb runs top to bottom without execution errors
* Dataset loads correctly, and preprocessing steps are clearly shown
* A supervised or unsupervised machine learning model is implemented and trained
* Model evaluation metrics appropriate to the task are computed and reported
* Visualizations or tables supporting model evaluation are included (where appropriate)
* A short notebook summary section is included

### Machine Learning Analysis Report

* module\_summary.pdf is included
* The report contains all required sections:
  + Overview
  + Dataset Description
  + Modeling Approach
  + Results
  + Interpretation for a Non-Technical Audience
  + Limitations and Potential Bias
  + References
* Modeling choices and evaluation results are grounded in the student’s own notebook outputs
* In-text citations are used where required
* References section uses a consistent citation style
* At least two credible sources are cited, with at least one scholarly source

### Dataset File

* Original dataset file (CSV or other tabular format) is included
* Dataset meets the stated requirements for machine learning

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

Before you begin the project, make sure your environment is set up correctly. This will help you avoid errors and ensure your machine learning notebook runs smoothly from start to finish.

1. Install Python 3.x
   You can use any recent version of Python 3 (3.9 or higher).
2. Install a notebook environment
   You may use any of the following:
   * Jupyter Notebook
   * JupyterLab
   * VS Code with the Jupyter Extension
   * Anaconda (includes Jupyter by default)
3. Install required Python libraries
   Make sure the following libraries are installed:
   * NumPy
   * Pandas
   * Matplotlib
   * Seaborn
   * One machine learning library: scikit-learn or PyTorch  
     If you are using Anaconda, many of these libraries may already be available.

## Validate Your Environment

1. Open a new Jupyter Notebook.
2. Run the following code to confirm core libraries import correctly:

```
import numpy as np
 import pandas as pd
 import matplotlib.pyplot as plt
 import seaborn as sns
```

1. Import the machine learning library you plan to use:
   For scikit-learn:

```
import sklearn
```

Or for PyTorch:

```
import torch
```

1. Load your dataset to confirm file access works correctly:

```
df = pd.read_csv("your_dataset.csv")
 df.head()
```

If the imports run without errors and the dataset loads correctly, your environment is ready.

## Create Your requirements.txt File

Before submitting your project, generate a reproducibility file from your environment:

```
pip freeze > requirements.txt
```

This file allows others to rerun your notebook using the same package versions.

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

## Project 3 — Machine Learning Foundations

Applied Predictive Modeling, Evaluation, and Interpretation

## What You Will Submit:

* modeling.ipynb
* Machine\_Learning\_Analysis\_Report.pdf
* requirements.txt
* Your dataset file (CSV)

## Project Instructions

### Task 1 — Define the Problem and Choose Your Dataset

For this project, you must find your own dataset and define a machine learning problem. Selecting an appropriate dataset and framing the problem correctly is part of the assessment.

You must clearly state whether your task is:

* supervised learning (classification or regression), or
* unsupervised learning (such as clustering)

#### Dataset Requirements

Your dataset must:

* Be appropriate for machine learning
* Have enough rows and features to support training and evaluation
* Include a clear target variable (for supervised learning) or meaningful structure (for unsupervised learning)
* Be in CSV or another tabular format
* Be publicly available and appropriate for academic use
* Not be synthetic or AI-generated
* Not the same dataset used in Projects 1 or 2

#### Accepted Sources

* Kaggle Datasets
* UCI Machine Learning Repository
* Data.gov
* Open government data portals

Download your dataset and place it in the same folder as your notebook.

### Task 2 — Load and Inspect Your Dataset

In modeling.ipynb:

* Load your dataset
* Display the first few rows using df.head
* Inspect column names and data types
* Briefly note any obvious data quality issues

This ensures you understand the structure of your data before modeling.

### Task 3 — Data Preparation and Preprocessing

Prepare your dataset for modeling. This may include:

* Handling missing values
* Encoding categorical variables
* Scaling or normalizing features
* Selecting or engineering features

Include short Markdown explanations describing what you did and why.

### Task 4 — Select and Train a Machine Learning Model

Choose an appropriate machine learning model based on your problem and dataset. Examples include:

* Linear or logistic regression
* Decision trees or ensemble models
* Clustering algorithms (for unsupervised learning)

Train your model using your prepared data. Clearly show the training process in your notebook.

### Task 5 — Evaluate Model Performance

Evaluate your model using metrics appropriate for your task. Examples include:

* Accuracy, precision, recall, or F1-score (classification)
* Mean squared error or R² (regression)
* Clustering metrics or qualitative evaluation (unsupervised learning)

Include numeric results and, where helpful, visualizations that support interpretation.

### Task 6 — Write a Short Notebook Summary

Add a brief Markdown section (4 to 6 sentences) summarizing:

* The problem you modeled
* The model you chose
* Key performance results
* Any challenges or limitations you observed

This concludes your notebook.

### Task 7 — Write the Machine Learning Analysis Report with Academic Citations

Create Machine\_Learning\_Analysis\_Report.pdf with the following sections:

#### Overview

Write 2 to 4 sentences explaining the machine learning problem you addressed, the dataset you used, and the type of model you built. Include the dataset name and source link.

#### Dataset Description

Write 3 to 6 sentences describing:

* What the dataset represents
* Number of rows and columns
* Key features and target variable (if applicable)

#### Modeling Approach

Explain:

* How you prepared the data for modeling
* Why you selected your model
* Why your evaluation metrics were appropriate
* Any assumptions made by the model

#### Results

Summarize model performance and reference specific metrics, tables, or figures from your notebook.

#### Interpretation for a Non-Technical Audience

Explain what the model’s performance means in clear, plain language suitable for readers without a machine learning background.

#### Limitations and Potential Bias

Discuss at least one limitation of your model or dataset and at least one potential source of bias or uncertainty in the results.

#### Citation Requirements

Use academic citations when:

* Defining machine learning concepts or evaluation metrics
* Justifying model or metric selection
* Discussing best practices, bias, or responsible use

Do not cite your own code, training results, or observed metrics.

#### References

Include all sources in a consistent citation style.

### Task 8 — Create requirements.txt

Generate your reproducibility file using:

```
pip freeze > requirements.txt
```

This ensures your machine learning workflow can be rerun in an identical environment.

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
| Notebook Execution | The notebook runs top-to-bottom without errors. All cells execute successfully, and required outputs (metrics, tables, or plots) are generated. |
| Data Preparation and Preprocessing | The dataset is loaded correctly and appropriate preprocessing steps are applied (for example: handling missing values, encoding variables, scaling features where needed). Preprocessing choices are consistent with the model used. |
| Model Selection and Implementation | At least one supervised or unsupervised machine learning model is correctly implemented using scikit-learn or PyTorch. The model choice is appropriate for the problem and dataset. |
| Training and Evaluation | The model is trained successfully and evaluated using at least one appropriate performance metric (for example: accuracy, precision, recall, F1-score, RMSE, or silhouette score). Evaluation results are clearly displayed. |
| Reproducibility | A valid requirements.txt file generated using pip freeze is included, allowing the notebook to be rerun in an equivalent environment. |

## Analytical Reasoning

| Criteria | Submission Requirements |
| --- | --- |
| Evaluation Metrics Justification | module\_summary.pdf explains why the chosen evaluation metric(s) are appropriate for the model type, task, and dataset. |
| Results Interpretation | module\_summary.pdf interprets the model’s performance using the student’s actual results, explaining what the metrics indicate about model behavior and effectiveness. |
| Model Limitations and Tradeoffs | module\_summary.pdf identifies at least one limitation or tradeoff in the model (such as bias, variance, data constraints, or metric limitations) and explains its impact on results. |

## Ethical and Responsible Practice

| Criteria | Submission Requirements |
| --- | --- |
| Bias and Responsible Use | module\_summary.pdf includes a section that identifies at least one potential source of bias or ethical concern related to the data, model, or evaluation, and describes one step taken or proposed to reduce that risk. |

## Communication and Presentation

| Criteria | Submission Requirements |
| --- | --- |
| Notebook Organization | The notebook uses clear markdown headings and logical structure for data preparation, modeling, evaluation, and outputs. |
| Code Readability and Documentation | Student-written code is readable, reasonably organized, and includes comments or docstrings where appropriate. |
| Written Analysis Quality | module\_summary.pdf is clearly written, logically structured, and understandable to both technical and non-technical readers. |
| Use of Citations | module\_summary.pdf uses in-text citations when referencing machine learning concepts, best practices, or evaluation methods, and includes a References section in a consistent citation style. |

## Integration and Professional Relevance

| Criteria | Submission Requirements |
| --- | --- |
| Workflow Completeness and Portfolio Readiness | The submission represents a complete, professional machine learning workflow appropriate for inclusion in a portfolio, demonstrating readiness for more advanced ML, deep learning, or applied AI projects. |

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

## Project: Applied Machine Learning: Model Design, Training, and Performance Evaluation

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

# Project: Applied Machine Learning: Model Design, Training, and Performance Evaluation

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

