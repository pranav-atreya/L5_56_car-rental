# Lab 5 — Reflection

Replace or adapt these draft answers after running the tools and observing your actual results. Do not claim that a tool reported a finding unless it appears in your report.

## 1. What is static code analysis, and how is it useful?

Static code analysis examines source code without executing the program. It helps identify likely bugs, unsafe patterns, maintainability problems, and style violations early. In this lab, Pylint checks general code quality, Bandit focuses on security-related patterns, and Flake8 checks style and linting rules. The tools complement one another and do not guarantee that a program is completely correct or secure.

## 2. What issues did you identify and fix?

The original car-rental script contains several source-level issues. Customer registration and lookup build SQL statements from input strings, and promotion handling uses `exec` on a supplied rule string. Receipt creation uses `tempfile.mktemp()` and changes permissions to `0o777`. The program also has a mutable list default, a bare exception handler, accepts invalid rental dates and negative rates, and allows the same car to be rented repeatedly because availability is not updated. The revised version replaces unsafe SQL construction, removes dynamic code execution, hardens receipt creation, validates inputs and rental state, and improves naming and structure. Add the exact tool codes from your local reports to this answer.

## 3. What was challenging, and how did you address it?

A key challenge is distinguishing a style warning from a real functional or security problem. For example, a negative rental duration is not merely a formatting issue; it produces an invalid negative price. Another challenge is validating the effect of a fix rather than assuming that changing a line solves the problem. I addressed these by inspecting the relevant functions, making targeted changes, running the program, and rerunning all three static-analysis tools. Replace this paragraph with the actual errors or difficulties you encountered.

## 4. How does static analysis improve software quality and maintainability?

Static analysis makes code review more systematic and repeatable. It can find suspicious patterns before deployment, gives developers concrete locations to inspect, and helps teams adopt consistent style and security practices. However, the findings require human judgement: some findings may be false positives, and static analysis cannot prove that every execution path works correctly. Unit tests, code review, secure design, and runtime verification are still necessary.
