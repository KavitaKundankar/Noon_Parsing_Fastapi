import json
import re

def extract_vessel_metadata(body):

    if isinstance(body, (dict, list)):
        text = json.dumps(body, indent=2)
    elif body is None:
        text = ""
    else:
        text = str(body)

# imo 

    imo_number = None

    imo_patterns = [
    r"imo\s*number\s*[:=]?\s*(\d+)",
    r"imo[_\s\-]*no\.?\s*[:=]?\s*(\d+)",
    r"imo[_\s\-]*number\s*[:=]?\s*(\d+)",
    r"imo\s*[:=]?\s*(\d+)",
    r"\bimo_no\s*[:=]?\s*(\d+)",
    r"\bimo\s*no\s*[:=]?\s*(\d+)"
    r"\[imo\s*number\s*:\s*(\d+)\]"
    ]

    for pattern in imo_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            imo_number = m.group(1).strip()
            break


# Extract Vessel Name

    vessel_name = None

    name_patterns = [
        r"vessel\s*[:\-]?\s*([A-Za-z0-9 \-_]+)",
        r"vessel Name\s*[:\-]?\s*([A-Za-z0-9 \-_]+)",
        r"Vessel Name\s*[:\-]?\s*([A-Za-z0-9 \-_]+)",
        r"Vessel\s*[:\-]?\s*([A-Za-z0-9 \-_]+)",
        r"ship Name\s*[:\-]?\s*([A-Za-z0-9 \-_]+)"
    ]

    for pattern in name_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            vessel_name = m.group(1).strip()
            vessel_name = re.split(r"[,/|()]+", vessel_name)[0].strip()
            break

# Extract Tenant 

    tenant = None

    tenant_keywords = {
        "misuga": "MISUGA-KAIUN",
        "misuga-kaiun": "MISUGA-KAIUN",
        "kitaura-kaiun": "KITAURA-KAIUN",
        "kitaura" : "KITAURA-KAIUN",
        "orion": "ORION",
    }

    for key, val in tenant_keywords.items():
        if key.lower() in text.lower():
            tenant = val
            break


# Extract Vessel ID

    vessel_id = None

    id_patterns = [
        r"Vessel ID\s*[:\-]?\s*(\w+)",
        r"Ship ID\s*[:\-]?\s*(\w+)",
        r"\bID\s*[:=]\s*(\w+)"
    ]

    for pattern in id_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            vessel_id = m.group(1).strip()
            break

# Return final result

    return {
        "imo_number": imo_number,
        "vessel_name": vessel_name,
        "tenant": tenant,
        "vessel_id": vessel_id
    }