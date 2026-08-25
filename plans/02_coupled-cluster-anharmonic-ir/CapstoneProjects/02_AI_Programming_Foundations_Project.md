# AI Programming Foundations Project

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

In this project, you will create a complete, reproducible data workflow using the Python skills you developed in your Nanodegree. You will load a dataset, clean and transform it, explore it, visualize it, and communicate your findings in a clear and professional way.

This project uses only the tools you already know:

* Python
* NumPy
* Pandas
* Matplotlib / Seaborn
* Git & GitHub
* Jupyter Notebooks

You are not training machine learning models yet. This project focuses on building the workflow that later ML, Deep Learning, Generative AI, and Agentic AI projects will build on. As part of this work, you will reference one provided scholarly article on reproducible data science to support at least one workflow or design decision, and you will identify and cite at least one additional scholarly source that supports your analysis or methodological choices.

## Why This Project Matters

A clean and reproducible data workflow is the first step in almost every AI or data science project. Employers expect professionals to:

* Write modular, reusable code
* Work with real datasets
* Clean and explore data
* Create meaningful visualizations
* Document their work clearly
* Use Git for version control

## What You Will Build

You will create:

1. A Jupyter Notebook with a complete data workflow following a clear structure.
2. A README File explaining your project, how to run it, and how it connects to future AI work.
3. A written summary with academic citations and a References section using the template provided.
4. A GitHub Repository with multiple commits and at least one additional branch to demonstrate professional version control.

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

Before you begin the project, make sure your environment is set up correctly. This will help you avoid errors and ensure your notebook runs smoothly from start to finish.

1. **Install Python 3.x**

* You can use any recent version of Python 3 (3.9 or higher).
* If you have already completed the Nanodegree projects, you should already have this installed.

1. **Install Jupyter Notebook or JupyterLab**
   You may use any of the following:

* Jupyter Notebook
* JupyterLab
* VS Code with the Jupyter Extension
* Anaconda (includes Jupyter by default)
  To install Jupyter via pip:

```
pip install notebook
```

To start Jupyter Notebook:

```
jupyter notebook
```

1. **Install Required Python Libraries**
   Make sure the following libraries are installed:

* NumPy
* Pandas
* Matplotlib
* Seaborn
  Install them with:

```
pip install numpy pandas matplotlib seaborn
```

If you are using Anaconda, these will already be available.

1. **Install and Set Up Git**
   Make sure Git is installed and connected to your GitHub account.
   Check your Git version:

```
git --version
```

If Git is not installed, download it here:
[https://git-scm.com/downloads(opens in a new tab)](https://git-scm.com/downloads)
You should be able to:

* Clone your project repository
* Create branches
* Commit and push your work to GitHub

1. **Validate Your Environment**
   Open a new Jupyter Notebook and run this code:

```
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
```

If the imports work with no errors, your environment is ready.
Next, test that you can load your dataset:

```
df = pd.read_csv("your_dataset.csv")
df.head()
```

If you see the first few rows of your dataset, everything is set up correctly.

5. **Create Your requirements.txt File**
   Before submitting your project, generate a reproducibility file:

```
pip freeze > requirements.txt
```

This file lists all the packages in your environment so someone else can run your notebook exactly as you did.

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

## Project Instructions

Follow the tasks below in order. Each task builds on the previous one. Complete each task before moving to the next.

### What You Will Submit:

1. data\_workflow.ipynb
2. module\_summary.pdf
3. requirements.txt
4. README.md
5. A GitHub repository link showing multiple commits and at least one additional branch

### Task 1 — Choose Your Dataset

Begin by selecting the dataset you will work with in this project.
You may choose from the recommended options below, or use your own dataset as long as it meets the project requirements.

#### Recommended Datasets

* [Titanic - Machine Learning from Disaster(opens in a new tab)](https://www.kaggle.com/c/titanic/data)
* [Iris (flower measurements)(opens in a new tab)](https://archive.ics.uci.edu/dataset/53/iris)
* [Wine (chemical properties and quality scores)(opens in a new tab)](https://archive.ics.uci.edu/dataset/186/wine+quality)
* [NYC Airbnb Listings (pricing and listing characteristics)(opens in a new tab)](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data)

#### If you choose your own dataset, it must:

* Contain at least 200 rows
* Have at least 5 columns
* Be a CSV or other tabular file
* Be safe and appropriate for academic use

After selecting your dataset, download it and place it in the same folder as your notebook.

---

### Task 2 — Create Your GitHub Repository

1. Create a new GitHub repository named: **ai-programming-foundations-project**
2. Clone it to your local machine.
3. Create at least **one** additional branch for development work.
4. Make regular commits as you complete each task.

Your repository should now contain at least two branches.

---

### Task 3 — Set Up Your Notebook

1. Create a new Jupyter Notebook named **data\_workflow.ipynb**.
2. In the first Markdown cell, include:

* Your name
* The dataset you selected
* A short 2–3 sentence description of the project

Your notebook should now have a clear and complete introduction.

---

### Task 4 — Import Libraries and Load Your Dataset

Add code cells that import the required libraries:

```
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
```

Then load your dataset:

```
df = pd.read_csv("your_dataset.csv")
df.head()
```

If the first rows display correctly, your data is loaded.

---

### Task 5 — Build Your Data Cleaning Functions

Write at least two cleaning functions.
Each function must include a docstring explaining what it does.

Apply your functions to your dataset.

---

### Task 6 — Write an Exploratory Analysis Function

Create one or more exploratory analysis (EDA) functions such as:

* Summary statistics
* Grouped or filtered views
* Correlation checks

Run your EDA function and review the output.

---

### Task 7 — Create Three Visualizations

Create **at least three** visualizations using Matplotlib or Seaborn.
Each visualization must include:

* A title
* Labeled axes

---

### Task 8 — Write Your Summary and Interpretation

Add a Markdown section that describes, in complete sentences:

* What you learned from the dataset
* Interesting patterns or insights
* Limitations or assumptions
* Anything surprising or unclear

### Task 9 — Create Your README File (Short Run Instructions Only)

* Create a file named README.md in your GitHub repo. Your README must include:
* Project Description (2–4 sentences)
* What you built
* What dataset you used (name + link)
* How to Run the Project
* How to install dependencies
* How to open and run data\_workflow.ipynb
* Create requirements.txt
* Include the command:

```
pip install -r requirements.txt

pip freeze > requirements.txt
```

**Important:** Do not put long explanations or citations in the README. All detailed explanations and academic citations belong in module\_summary.pdf. A reviewer should be able to follow your README and run your notebook successfully.

### Task 10 — Summary & Interpretation (with Academic Citations)

Each capstone module requires a written summary supported by academic citations. For this module, you must submit a separate written report.

Create a file named module\_summary.pdf. As part of this report, you must read and cite the required peer-reviewed article: [Reproducible Data Science with Python: An Open Learning Resource(opens in a new tab)](https://www.researchgate.net/publication/364706809_Reproducible_Data_Science_with_Python_An_Open_Learning_Resource) on reproducible data science.

You must use this article to support at least one workflow, reproducibility, or design decision you made in this project. In addition, you must find and cite at least one other peer-reviewed scholarly source that supports a relevant best-practice claim in your report. Both sources must appear as in-text citations and in the References section of module\_summary.pdf.

Your report must include the following sections:

* #### Overview (2–4 sentences)
* Explain what you built and what dataset you used. Include the dataset name and link.
* #### Dataset Description (3–6 sentences)
* Describe what the dataset represents, its size (rows/columns), and the key variables you focused on.
* #### Workflow Description (high level)
* Explain your workflow steps at a high level:

  + Ingestion
  + Cleaning
  + Exploratory analysis
  + Visualizations
  + Summary
* #### Key Decisions and Assumptions
* Explain the most important choices you made and why they were appropriate for your dataset:

  + Cleaning choices
  + What you focused on in EDA
  + What each plot was designed to show

**Tip:** When you make a best-practice claim (for example, about missing data, reproducibility, bias, or visualization choices), support it with a citation.

* #### Results and Interpretation
* Summarize the most important patterns you found. Refer to your notebook outputs and visualizations (for example: Figure 1, Figure 2, Figure 3).
* #### Responsible Practice (Bias and Data Quality)
* Explain where cleaning or data handling could introduce bias or misleading results in your dataset, and what you did (or would do next) to reduce that risk.
* #### Reproducibility
* Explain how someone else could rerun your work. Mention requirements.txt and your Git workflow (commits/branching).
* #### Sources and Citations (Required)
* Include a references list. Use citations in the report whenever you make a general claim about best practices.

  + Acceptable sources include:
  + Official documentation (Python, Pandas, Matplotlib, Git)
  + University or textbook resources
  + Peer-reviewed articles or conference papers

---

## Submission Instructions

Make sure your submission includes:

### GitHub Repository

* Multiple commits showing progress
* At least one additional branch
* All project files included

### Notebook

* Dataset loads correctly
* Two cleaning functions with docstrings
* One EDA function
* Three labeled visualizations
* Summary section
* No execution errors

### README

* Project description
* Reproducibility instructions
* How to run data\_workflow.ipynb
* How to install dependencies (pip install -r requirements.txt)

### requirements.txt

Created using:

```
pip freeze > requirements.txt
```

### Written summary report with in-text citations

* References section (consistent citation style)
* At least 2 credible sources (at least 1 scholarly source)
* Report content grounded in your dataset, code, and visualizations

If everything on the checklist is complete, your project is ready to submit.

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

## Untitled Section

| Criteria | Submission Requirements |
| --- | --- |
| Notebook Execution | Notebook runs top-to-bottom without errors; all cells execute successfully. |
| Data Ingestion | Dataset loads correctly using Pandas; first rows are displayed. |
| Data Cleaning Functions | At least two cleaning functions defined and used; each includes a clear docstring. |
| Exploratory Analysis Function | At least one EDA function defined and used (summary statistics, grouping, filtering, etc.). |
| Visualizations | At least three visualizations using Matplotlib/Seaborn; each has a title and labeled axes. |
| Reproducibility | A correct requirements.txt file created using pip freeze is included. |
| Cleaning Justification | Student clearly explains why cleaning steps were necessary and what issues they addressed. |
| Visualization Interpretation | Each visualization includes a brief, accurate interpretation of what the plot shows. |
| Summary & Interpretation | Final summary describes insights, patterns, assumptions, and limitations in complete sentences. |
| Bias Awareness | README includes a thoughtful response explaining where poor data cleaning could introduce bias. |
| Notebook includes required sections (Setup, Ingestion, Cleaning, EDA, Visualizations, Summary) with clear markdown headings. |  |
| All student-defined functions include informative docstrings; code formatting is readable. |  |
| README includes a project description, reproducibility instructions, and complete responses to all reflection questions. |  |
| Git/GitHub Usage | Repository includes multiple commits and at least one additional branch beyond main. |
| Future Integration Reflections | README includes complete answers on ML workflow changes, neural network preparation, and agentic automation potential. |
| Workflow Completeness | Submission resembles a professional, reusable data workflow appropriate as a foundation for ML/DL projects. |

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

## Project: AI Programming Foundations Project

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

# Project: AI Programming Foundations Project

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

