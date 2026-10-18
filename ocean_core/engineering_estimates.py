"""Consistency checks for engineering estimates; not a factual verification service."""
from __future__ import annotations

import ast
from decimal import Decimal
import re


ESTIMATE_POLICY = """
ENGINEERING ESTIMATION:
Preserve the team size given by the user. Separate sourced facts from assumptions.
Do not invent module scope, productivity, effort or delivery dates. A public-information
estimate needs traceable public sources and an explicit scope; internal service names
alone do not establish implementation effort. State missing evidence plainly instead
of attaching UNVERIFIED to an invented estimate. Label any workweek assumption.
Calculate person-days = engineers * working days, and elapsed working days =
person-days / engineers. Check all sums and products. Person-days are effort, not
calendar duration: dependencies, coordination and validation limit parallelism.
""".strip()

_TEAM = re.compile(
    r"\b(\d{1,5})\s+(?:(?:senior|experienced|full[- ]time)\s+)?"
    r"(?:engineers?|developers?|inxhinier\w*|ingenieur\w*)\b", re.I
)


def is_engineering_estimate(prompt: str) -> bool:
    sample = (prompt or "").casefold()
    return bool(
        re.search(r"\b(?:estimate|estimating|estimation|effort|vlerëso|vlereso|përpjekje|schätz\w*|aufwand)\b", sample)
        and re.search(r"\b(?:rebuild\w*|from scratch|rindërt\w*|rindert\w*|neu\s+aufbauen|nachbauen)\b", sample)
    )


def needs_public_estimate_evidence(prompt: str) -> bool:
    return bool(is_engineering_estimate(prompt) and re.search(
        r"public (?:information|sources|data)|informacion\w* publik|burim\w* publik|öffentlich\w*", prompt, re.I
    ))


def _arithmetic(expression: str) -> Decimal:
    """Evaluate only short literal sums/products, never executable model code."""
    if len(expression) > 300:
        raise ValueError("Expression too long")
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Decimal(str(node.value))
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
        raise ValueError("Unsupported arithmetic")

    return visit(tree.body)


def estimate_issues(prompt: str, response: str, *, public_evidence_available: bool = False) -> list[str]:
    if not is_engineering_estimate(prompt):
        return []
    issues = []
    teams = {int(match) for match in _TEAM.findall(prompt)}
    if len(teams) == 1:
        requested_team = next(iter(teams))
        if any(int(size) != requested_team for size in _TEAM.findall(response)):
            issues.append("team_size_changed")
    if "unverified" in response.casefold():
        issues.append("unverified_estimate")
    public_basis = needs_public_estimate_evidence(prompt)
    proposed_effort = re.search(r"\d[\d,.]*\s*(?:[-–]\s*\d+\s*)?(?:person[- ]days?|person[- ]months?|months?|years?|weeks?|ditë|muaj|vite|wochen|monate|jahre)\b", response, re.I)
    if public_basis and proposed_effort and not public_evidence_available:
        issues.append("missing_public_evidence")

    math_text = re.sub(r"\\text\{[^}]*\}", "", response)
    math_text = math_text.replace("\\times", "*").replace("×", "*")
    math_text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", math_text)
    equation = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?(?:\s*[+*\-]\s*\d+(?:\.\d+)?)+)\s*=\s*(\d+(?:\.\d+)?)")
    for expression, stated_result in equation.findall(math_text):
        try:
            if _arithmetic(expression) != Decimal(stated_result):
                issues.append("incorrect_arithmetic")
        except (ValueError, SyntaxError):
            issues.append("invalid_arithmetic")
    return sorted(set(issues))


def insufficient_estimate_response(prompt: str, language: str | None = None) -> str:
    teams = {int(match) for match in _TEAM.findall(prompt)}
    team = next(iter(teams)) if len(teams) == 1 else None
    if not language or language in {"auto", "detect"}:
        sample = prompt.casefold()
        language = "sq" if "inxhinier" in sample else "de" if "ingenieur" in sample else "en"
    if language == "sq":
        text = "Nuk ka një bazë të mjaftueshme të dokumentuar për të dhënë një afat të besueshëm rindërtimi."
        if team and team > 0:
            text += f" Me {team} inxhinierë dhe supozimin e 5 ditëve të punës në javë, kapaciteti nominal është {team} × 5 = {team * 5} ditë-inxhinieri në javë."
        return text + " Duhet një ndarje e punës sipas funksioneve, API-ve dhe integrimeve, si dhe kërkesat për siguri, testim e prodhim. Për çdo pjesë duhen burimi, supozimet dhe intervali i punës. Afati duhet të përfshijë varësitë dhe koordinimin; kapaciteti i ekipit nuk provon kohën e nevojshme."
    if language == "de":
        text = "Es fehlt eine ausreichend dokumentierte Grundlage für einen belastbaren Zeitplan zum Neuaufbau."
        if team and team > 0:
            text += f" Bei {team} Ingenieuren und einer angenommenen Fünftagewoche beträgt die nominale Kapazität {team} × 5 = {team * 5} Personentage pro Woche."
        return text + " Benötigt werden eine Aufteilung nach Funktionen, APIs und Integrationen sowie Anforderungen an Sicherheit, Tests und Produktion. Für jeden Teil müssen Quellen, Annahmen und Aufwandsspannen angegeben werden. Abhängigkeiten und Koordination begrenzen die Parallelisierung; Teamkapazität allein ergibt keinen Liefertermin."
    text = "There is not enough documented scope to give a defensible rebuild timeline."
    if team and team > 0:
        text += f" For {team} engineers, assuming a five-day workweek, nominal capacity is {team} × 5 = {team * 5} person-days per week."
    return text + " A credible estimate needs a work breakdown covering features, APIs, integrations, security, testing and production requirements. Each component needs a traceable source, explicit assumptions and an effort range. Dependencies and coordination limit parallelism; team capacity alone does not establish the rebuild effort or delivery date."


def review_engineering_estimate(prompt: str, response: str, language: str | None = None, *, public_evidence_available: bool = False) -> str:
    if estimate_issues(prompt, response, public_evidence_available=public_evidence_available):
        return insufficient_estimate_response(prompt, language)
    return response
