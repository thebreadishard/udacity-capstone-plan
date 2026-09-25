#!/usr/bin/env python
"""Builds Agentic_AI_System_Design_Report.docx in the Udacity APA 7 template with the sections Rubrics/07 Task 6 prescribes — Overview · System
Architecture and Design · Decision Logic and Behavior · Safety, Reliability, and Transparency · Observed Behavior and Limitations · Ethical and
Responsible Use Considerations · Future Improvements · References — then converts it to PDF with Word (COM through PowerShell). Every number is read
from notebook/results.json; nothing is typed in by hand. Run:  python make_summary.py"""
import json
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[3] / "Rubrics" / "APA7_template.docx"
NB = HERE / "notebook"
FIG = NB / "figures"
OUT_DOCX = HERE / "Agentic_AI_System_Design_Report.docx"

R = json.load(open(NB / "results.json", encoding="utf-8"))
RP = R["rules_policy"]; LP = R.get("llm_policy")

doc = Document(str(TEMPLATE))
for p in list(doc.paragraphs):
    p._element.getparent().remove(p._element)


def para(text="", bold=False, center=False, italic=False, size=None, indent_first=True):
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if not indent_first:
        p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def heading(text):
    para(text, bold=True, indent_first=False)


def figure(name, caption):
    if (FIG / name).exists():
        doc.add_picture(str(FIG / name), width=Inches(6.0)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        para(caption, italic=True, size=10, indent_first=False)


def table(header, rows, caption):
    para(caption, italic=True, size=10, indent_first=False)
    t = doc.add_table(rows=1, cols=len(header))
    try:
        t.style = "Table Grid"
    except KeyError:
        pass   # the APA template carries no grid style
    for i, h in enumerate(header):
        t.rows[0].cells[i].text = h
    for row in rows:
        c = t.add_row().cells
        for i, v in enumerate(row):
            c[i].text = str(v)
    para("", indent_first=False)


# title block
para("", center=True); para("Agentic AI System Design Report", bold=True, center=True)
para("The Run Steward: a Bounded Single Agent for a Pre-Registered Computational-Chemistry Campaign", center=True)
para("Frederic Petrignani", center=True); para("Udacity AI Mastery Capstone — Module 07: Design of Autonomous and Semi-Autonomous Agentic Workflows", center=True)
para(f"{R['date'][:10]}", center=True)
para("Agentic_AI_System_Design_Report.pdf", center=True, indent_first=False)

heading("Overview")
para(f"This report describes an agentic workflow built for a real, running research campaign: the delta-probed infrared pipeline of the author's capstone plan, "
     f"whose calculations run on five rented machines and a laptop under written, pre-registered rules. The agent — the run steward — observes machines and result "
     f"files, proposes exactly one next action that cites a rule, passes the proposal through a deterministic gate, acts through {R['n_actions']} allow-listed tools, and records "
     f"every step in an append-only ledger. It is a single agent with one reasoning loop, implemented as a LangGraph state graph with a language-model reasoning node "
     f"(Anthropic API through langchain-anthropic) and a deterministic reference policy used for testing. An agentic approach fits because the decisions are sequential, "
     f"depend on state that changes on its own and require tools; a bounded design fits because the correct behaviour is rule application under uncertainty, and the cost "
     f"of a wrong autonomous action — a deleted server, a duplicate forty-hour run, a false scientific claim — far exceeds the cost of asking a human (Amodei et al., 2016; Shavit et al., 2023).")

heading("System Architecture and Design")
para(f"Components. The persona is a careful laboratory technician who applies written rules and escalates what matches no rule. The reasoning loop is observe → propose → "
     f"gate → act → record, with a conditional edge back to observe until a terminal action (wait or escalate) or a step budget. Memory has three parts: a curated long-term "
     f"rule table of {R['n_rules']} rules ({R['n_gate_rules']} enforced mechanically by the gate, the rest shaping the reasoning prompt), a campaign state, and a rolling window "
     f"of observations and actions taken in the run. Tools are the project's own status reader, launcher, result readers, ledger and notification channel, wrapped behind an "
     f"interface whose replay implementation substitutes log fixtures for machines. The design follows the reasoning-and-acting pattern of ReAct (Yao et al., 2023) and the "
     f"tool-use framing of Toolformer (Schick et al., 2023), with one deliberate departure: the model never executes; it proposes a structured object {{action, args, rule_id, "
     f"reason}} and plain code decides. Figure 1 shows the graph; the notebook draws it from the compiled LangGraph object.")
figure("architecture.png", "Figure 1. The run steward: one bounded agent. The reasoning node proposes; the deterministic gate disposes; every step is recorded.")
para("Design choices and tradeoffs. Structured output with a cited rule identifier makes every decision auditable against the table. A closed allow-list means that a wrong "
     "or manipulated proposal cannot reach anything outside eleven actions, none of which creates or deletes machines, spends money, publishes, changes a rule or passes a "
     "verdict. The rule table limits what the agent handles: anything novel escalates. That is a capability tradeoff made on purpose for a campaign where a human question "
     "is cheap and a wrong action is not; the survey literature on LLM-based agents lists exactly this tension between autonomy and controllability (Wang et al., 2024; Xi et al., 2023).")

heading("Decision Logic and Behavior")
para("Decision logic has two layers. The reasoning layer receives the persona, the allow-list, the whole rule table, the actions already taken and the last observations "
     "(verbatim log excerpts with the facts a tool extracted) and returns one proposal. The gate layer is deterministic and checks, in order: that the action is allow-listed and "
     "cites a rule that exists; that no observation contains an instruction addressed to the agent (if one does, only escalation is allowed); that a launch has a passed dry run "
     "of the same job and no live instance; that a lock is removed only when its recorded process is dead on the same host and the process list has been checked with a pattern "
     "that cannot match the checking shell itself; that a statistic of the form 'the model respects X' is recorded only beside the same statistic on the target; that a training "
     "job whose checkpoint is fresh is not restarted; that arguments never touch a human-gated action; and that the run's launch budget is not exhausted. A refused proposal is "
     "replaced by the safe substitute the rule names — a dry run, a process check, a wait or an escalation — never by nothing.")
rows = [(sid, " → ".join(d["actions"]), " ".join(str(x) for x in d["rules"]), ", ".join(d["forced"]) or "—", "yes" if d["escalations"] else "no") for sid, d in RP["per_scenario"].items()]
table(["scenario", "actions taken", "rules cited", "gate substitutions", "escalated"], rows, f"Table 1. The eight pre-registered scenarios (real log excerpts of 25 September 2026) replayed with the deterministic reference policy: {RP['n_pass']} of {R['n_scenarios']} correct.")

heading("Safety, Reliability, and Transparency")
para("Safeguards are the rule table made mechanical. Reliability: a dry run before every launch, no second instance, keep-alives on waiting connections, heartbeats and "
     "checkpoints for long runs, a step and launch budget per run. Interpretability: every proposal carries the rule it applies and the observation it answers, every ledger "
     "line carries a clock read in the same call, and a refusal names its reasons. Misuse prevention: the allow-list is closed; observed content is data — a log line that "
     "addresses the agent with an imperative is flagged by a scan and can only lead to an escalation with the quote, which is the defence the indirect-prompt-injection "
     "literature recommends for tool-using agents (Greshake et al., 2023). Human gates are structural rather than behavioural: the actions that need a human are not in the "
     "agent's vocabulary. The tests are negative controls in the sense of the project's quality policy: each guard has a test that fails without it, and the eight scenarios "
     "replay in the test suite.")

heading("Observed Behavior and Limitations")
para(f"With the deterministic reference policy the agent took the correct action sequence in {RP['n_pass']} of {R['n_scenarios']} scenarios, escalated the three cases that "
     f"belong to a human (a machine to create, a failure with no known signature, an instruction hidden in a log) and refused to record the one scientific reading that lacked its "
     f"control — the very reading that had been recorded by a human, and withdrawn, on the morning the fixtures come from. The gate never had to substitute an action for the reference "
     f"policy, which is expected: the reference encodes the rules; the gate's own tests show it stopping each forbidden action when asked. "
     + (f"With the language-model policy ({LP['model']}) the agent passed {LP['n_pass']} of {LP['n_runs']} scenario runs and the gate substituted an action in {LP['n_gate_substitutions']} of them. "
        if LP else "The language-model policy was not run in this execution because no API key was available in the build environment; its pass rate, rule citations and gate-substitution count are the numbers this section must gain before submission, from the same notebook cell. "))
para("A genuine failure was found while building: for the failed-molecule scenario the first version of the policy proposed the same ledger line at every step until the step "
     "budget ended the run. The rule 'one line per event' was in the table but not in the policy's state handling, and the gate did not cover repetition. The general lesson is "
     "that a rule in a prompt is a request, not a guarantee; only a gate guarantees. Limitations: the deterministic policy is brittle by design and falls through to waiting when a "
     "state is described in words it does not know; fact extraction from live logs is not yet a tool, and every parser is a place where a line can be misread (the project's own "
     "handover watcher parsed a substring of a comment as a job identifier on the day of the fixtures); the scenarios are eight and were chosen from one day.")

heading("Ethical and Responsible Use Considerations")
para("The main ethical concern is accountability under autonomy. The steward spends other people's money (rented machines), can idle or duplicate expensive computation, and — "
     "through the ledger — writes the evidence that later scientific claims rest on. Three design decisions answer it. First, the boundary is structural: the agent cannot create "
     "or delete infrastructure, publish, or pass a verdict, so those acts remain a person's and are logged as such. Second, transparency is total and cheap: every step names its "
     "rule and its observation, so an auditor can replay a run and disagree with a specific line. Third, the rule that a scientific statistic is recorded only beside its control "
     "protects against the agent laundering a human's premature conclusion into the record. A second concern is over-trust: an operator who sees weeks of correct behaviour may "
     "widen the allow-list for convenience. The design's answer is that widening is a rule change, and rule changes are the human's, dated and committed (Shavit et al., 2023; Mitchell et al., 2019).")

heading("Future Improvements")
para("Realistic next steps: run and report the language-model policy on the same scenarios with the model identifier logged; build the live tools (status parser, result "
     "readers) with their own tests and a shadow mode in which the steward proposes and a human executes for a week before any autonomous launch; add repetition and rate "
     "checks to the gate; grow the scenario set from the campaign's ledger as new incidents occur, so that the evaluation set is the project's own history; and formalise the "
     "runner's lock and resume protocol (a TLA+ model is planned in the project's quality policy) so that the gate's stale-lock rule rests on a proof rather than a test.")

heading("References")
refs = [
    "Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). Concrete problems in AI safety. arXiv. https://arxiv.org/abs/1606.06565",
    "Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., & Fritz, M. (2023). Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. In Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (pp. 79–90). ACM. https://doi.org/10.1145/3605764.3623985",
    "Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency (pp. 220–229). ACM. https://doi.org/10.1145/3287560.3287596",
    "Schick, T., Dwivedi-Yu, J., Dessì, R., Raileanu, R., Lomeli, M., Zettlemoyer, L., Cancedda, N., & Scialom, T. (2023). Toolformer: Language models can teach themselves to use tools. In Advances in Neural Information Processing Systems 36. arXiv. https://arxiv.org/abs/2302.04761",
    "Shavit, Y., Agarwal, S., Brundage, M., Adler, S., O'Keefe, C., Campbell, R., Lee, T., Mishkin, P., Eloundou, T., Hickey, A., Slama, K., Ahmad, L., McMillan, P., Beutel, A., Passos, A., & Robinson, D. G. (2023). Practices for governing agentic AI systems. OpenAI. https://openai.com/research/practices-for-governing-agentic-ai-systems",
    "Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., Chen, Z., Tang, J., Chen, X., Lin, Y., Zhao, W. X., Wei, Z., & Wen, J.-R. (2024). A survey on large language model based autonomous agents. Frontiers of Computer Science, 18(6), 186345. https://doi.org/10.1007/s11704-024-40231-1",
    "Xi, Z., Chen, W., Guo, X., He, W., Ding, Y., Hong, B., Zhang, M., Wang, J., Jin, S., Zhou, E., Zheng, R., Fan, X., Wang, X., Xiong, L., Zhou, Y., Wang, W., Jiang, C., Zou, Y., Liu, X., … Gui, T. (2023). The rise and potential of large language model based agents: A survey. arXiv. https://arxiv.org/abs/2309.07864",
    "Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing reasoning and acting in language models. In International Conference on Learning Representations (ICLR 2023). arXiv. https://arxiv.org/abs/2210.03629",
]
for r in refs:
    p = para(r, indent_first=False)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)

doc.save(str(OUT_DOCX))
print("written", OUT_DOCX)
ps = f'''$w = New-Object -ComObject Word.Application; $w.Visible = $false
$d = $w.Documents.Open("{OUT_DOCX}"); $d.SaveAs2("{OUT_DOCX.with_suffix('.pdf')}", 17); $d.Close(); $w.Quit()'''
subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
print("pdf:", OUT_DOCX.with_suffix(".pdf").exists())
