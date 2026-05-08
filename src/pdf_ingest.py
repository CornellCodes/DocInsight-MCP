from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import pdfplumber


@dataclass
class ParsedApplication:
    app_id: Optional[int] = None
    major: Optional[str] = None
    term: Optional[str] = None
    grad_type: Optional[int] = None
    admissions_status: Optional[str] = None
    student_type: Optional[str] = None
    gpa: Optional[float] = None
    missing_items: List[str] | None = None
    decision_status: Optional[str] = None
    decision_reason: Optional[str] = None
    applicant_name: Optional[str] = None
    muid: Optional[str] = None
    gender: Optional[str] = None
    email_address: Optional[str] = None
    phys_address: Optional[str] = None
    documents: List[Dict[str, Any]] | None = None
    courses: List[Dict[str, Any]] | None = None


def normalize_whitespace(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def normalize_date(date_str):
    if not date_str:
        return None

    parts = date_str.split("/")

    if len(parts) == 3:
        mm, dd, yyyy = parts
        return f"{mm.zfill(2)}{dd.zfill(2)}{yyyy}"

    return None


def extract_all_text(pdf_path: str | Path) -> List[str]:
    pages = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)

    return pages


def search(pattern: str, text: str, flags: int = 0):
    return re.search(pattern, text, flags)


def map_grad_type(text: Optional[str]) -> Optional[int]:
    if not text:
        return None

    lowered = text.lower()

    if "phd" in lowered or "ph.d" in lowered or "doctoral" in lowered:
        return 2

    if "graduate" in lowered or "master" in lowered or "ms" in lowered:
        return 1

    if "undergraduate" in lowered or "bachelor" in lowered:
        return 0

    return None


def extract_selected_decision_reason(page1: str) -> Optional[str]:
    lines = [line.strip() for line in page1.splitlines()]

    for i, line in enumerate(lines):

        if line.startswith("X Selected:"):

            reason_lines = []

            for next_line in lines[i + 1:]:

                next_line = next_line.strip()

                if not next_line:
                    continue

                if re.match(r"^(Dr\.|Mr\.|Mrs\.|Ms\.)\s+", next_line):
                    break

                if re.match(r"^\d{1,2}-[A-Za-z]+-\d{4}$", next_line):
                    break

                if next_line.startswith("[FORM FIELD]"):
                    break

                reason_lines.append(next_line)

            reason = " ".join(reason_lines)

            reason = re.sub(r"\s+", " ", reason).strip()

            return reason or None

    return None

def parse_page_one(page1: str) -> Dict[str, Any]:
    data = {}
    lower = page1.lower()

    missing = search(r"Missing:\s*(.+)", page1)

    if missing:
        items = [
            item.strip()
            for item in re.split(r",|;", missing.group(1))
            if item.strip()
        ]

        data["missing_items"] = items

    major = search(r"Major:\s*(.+?)\s+MUID", page1, re.S)

    if major:
        value = normalize_whitespace(major.group(1))

        if value:
            data["major"] = value

    applicant = search(
        r"Applicant[’']s Name:\s*(.+?)\s+Term applying for:",
        page1,
        re.S
    )

    if applicant:
        value = applicant.group(1).strip(" _")

        if value and "Graduate Admissions use only" not in value:
            data["applicant_name"] = normalize_whitespace(value)

    generated_name = search(
        r"Graduate Admissions use only\. Do not alter\.\s+"
        r"[A-Za-z]+\s+\d{1,2},\s+\d{4}\s+.+?\n"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+[A-Za-z]+\s+20\d{2}",
        page1,
        re.S
    )

    if generated_name:
        data["applicant_name"] = generated_name.group(1).strip()

    muid = search(r"\b(\d{9})\b", page1)

    if muid:
        data["muid"] = muid.group(1)

    if "x selected: full admission" in lower:
        data["decision_status"] = "Full Admission"

    elif "x selected: conditional admission" in lower:
        data["decision_status"] = "Conditional Admission"

    elif "x selected: provisional admission" in lower:
        data["decision_status"] = "Provisional Admission"

    elif "x selected: denial of admission" in lower:
        data["decision_status"] = "Not Admitted"

    elif "for: provisional admission" in lower and "bridge courses" in lower:
        data["decision_status"] = "Provisional Admission"

    elif "for: conditional or denied" in lower and "missing:" in lower:
        data["decision_status"] = "Conditional Admission"

    elif "for: full or provisional admission" in lower:
        data["decision_status"] = "Full Admission"

    selected_reason = extract_selected_decision_reason(page1)

    if selected_reason:

        if len(selected_reason) > 250:
            data["decision_reason"] = None

        elif "these credentials are being forwarded" in selected_reason.lower():
            data["decision_reason"] = None

        else:
            data["decision_reason"] = selected_reason

    else:
        old_checked_reason = search(
            r"✔\s*(.+?)\s+(?:Dr\.|Haroon Digitally signed)",
            page1,
            re.S
        )

        if old_checked_reason:

            reason = normalize_whitespace(old_checked_reason.group(1))
            reason = reason.replace("of of", "of")

            if len(reason) > 250:
                data["decision_reason"] = None
            else:
                data["decision_reason"] = reason

    return data


def parse_summary_page(page4: str) -> Dict[str, Any]:
    data = {}

    email = search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        page4
    )

    if email:
        data["email_address"] = email.group(0)

    app_id = search(r"App ID-(\d+)", page4)

    if app_id:
        data["app_id"] = int(app_id.group(1))

    generated_contact = search(
        r"Contact Details\s+First Name\s+Last Name\s+Gender\s+"
        r"([A-Z][A-Za-z'-]+)\s+([A-Z][A-Za-z'-]+)\s+(Male|Female|Other)",
        page4,
        re.S
    )

    if generated_contact:
        data["applicant_name"] = (
            generated_contact.group(1) + " " + generated_contact.group(2)
        )

        data["gender"] = generated_contact.group(3)

    term = search(
        r"Student Type\s+Term\s+(.+?)\s+([A-Za-z]+\s+20\d{2})",
        page4,
        re.S
    )

    if term:
        student_type = normalize_whitespace(term.group(1))

        data["student_type"] = student_type
        data["term"] = term.group(2)
        data["grad_type"] = map_grad_type(student_type)

    major_status = search(
        r"Major Admissions Status\s+(.+?)\s+"
        r"(Completed App|Incomplete App|Admitted|Denied)",
        page4,
        re.S
    )

    if major_status:
        data["major"] = normalize_whitespace(major_status.group(1))
        data["admissions_status"] = major_status.group(2)

    return data


def parse_documents_page(page5: str) -> List[Dict[str, Any]]:
    docs = []

    fee = search(
        r"Application Fee\s+Waived\s+(\d{2}/\d{2}/\d{4})",
        page5
    )

    if fee:
        docs.append({
            "display_name": "Application Fee",
            "status": "Waived",
            "date_received": normalize_date(fee.group(1)),
        })

    transcript = search(
        r"([A-Za-z\s]+University|Virginia Tech|Ohio University|Marshall University)"
        r"\s+Official Transcript\s+Received - Official(?:\s+(\d{2}/\d{2}/\d{4}))?",
        page5
    )

    if transcript:
        docs.append({
            "display_name": f"{transcript.group(1).strip()} Official Transcript",
            "status": "Received - Official",
            "date_received": normalize_date(transcript.group(2))
            if transcript.group(2) else None,
        })

    return docs


def parse_record_page(page6: str) -> Dict[str, Any]:
    data = {}

    name = search(
        r"EDU-\d+\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Application",
        page6
    )

    if name:
        data["applicant_name"] = name.group(1).strip()

    return data


def parse_transcript_page(page8: str) -> Dict[str, Any]:
    data = {}

    gpa = search(
        r"OVERALL\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+(\d+\.\d+)",
        page8
    )

    if gpa:
        data["gpa"] = float(gpa.group(1))

    return data


def parse_transcript_courses(*pages: str) -> Dict[str, Any]:
    courses = []
    current_term = None

    term_pattern = re.compile(r"^(Fall|Spring|Summer)\s+20\d{2}$")

    course_pattern = re.compile(
        r"^([A-Z]{2,4})\s+(\d{3})\s+(.+?)\s+"
        r"(\d+\.\d{2})\s+([A-F][+-]?)\s+(\d+\.\d{2})$"
    )

    for page in pages:
        for line in page.splitlines():
            line = line.strip()

            if term_pattern.match(line):
                current_term = line
                continue

            match = course_pattern.match(line)

            if match:
                courses.append({
                    "term": current_term,
                    "subject": match.group(1),
                    "course_number": match.group(2),
                    "course_title": match.group(3).strip(),
                    "credit_hours": float(match.group(4)),
                    "grade": match.group(5),
                    "quality_points": float(match.group(6)),
                })

    return {"courses": courses}


def parse_app_id(pages: List[str]) -> Optional[int]:
    for page in pages:
        match = search(r"App ID-(\d+)", page)

        if match:
            return int(match.group(1))

    return None


def parse_application_pdf(pdf_path: str | Path) -> Dict[str, Any]:
    pages = extract_all_text(pdf_path)

    if not pages:
        raise ValueError("No text could be extracted from the PDF.")

    data = ParsedApplication(
        missing_items=[],
        documents=[],
        courses=[]
    )

    data.app_id = parse_app_id(pages)

    parsers = [
        (0, parse_page_one),
        (3, parse_summary_page),
        (4, lambda text: {"documents": parse_documents_page(text)}),
        (5, parse_record_page),
        (7, parse_transcript_page),
    ]

    for index, parser in parsers:

        if index < len(pages):

            parsed = parser(pages[index])

            if parsed is None:
                continue

            for key, value in parsed.items():

                if value is None:
                    continue

                if key == "documents":
                    data.documents.extend(value)

                elif key == "missing_items":
                    data.missing_items.extend(value)

                elif key == "courses":
                    data.courses.extend(value)

                else:
                    setattr(data, key, value)

    if len(pages) > 7:
        parsed_courses = parse_transcript_courses(
            pages[6],
            pages[7]
        )

        for course in parsed_courses["courses"]:
            data.courses.append(course)

    if data.grad_type is None:
        data.grad_type = map_grad_type(data.major)

    return asdict(data)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("Usage: python pdf_ingest.py <pdf_path>")
        raise SystemExit(1)

    result = parse_application_pdf(sys.argv[1])

    print(json.dumps(result, indent=2))
