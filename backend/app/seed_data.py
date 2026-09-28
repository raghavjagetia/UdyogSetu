"""Seeds the database with demo users, a rules-as-code library modeled on
Maharashtra's single-window (MAITRI) approval landscape, and a couple of
sample government schemes. Safe to re-run: it only inserts when tables are empty.
"""

import datetime as dt

from sqlalchemy.orm import Session

from . import models
from .auth import hash_password
from .routers.applications import _recompute_status
from .rules_engine.engine import generate_checklist

SECTORS = [
    "Manufacturing",
    "IT/ITES",
    "Food Processing",
    "Textile",
    "Chemical & Pharma",
    "Agro-Based",
    "Services",
]

LOCATIONS = [
    "Mumbai",
    "Pune",
    "Nagpur",
    "Nashik",
    "Chhatrapati Sambhajinagar",
    "Thane",
    "Kolhapur",
    "Amravati",
]

RULES = [
    dict(
        sector="All", location="All", min_size="Micro",
        approval_name="Udyam Registration",
        department="Ministry of MSME",
        clause_ref="MSME Development Act, 2006 - Sec 8",
        sla_days=1, mandatory=True,
    ),
    dict(
        sector="All", location="All", min_size="Micro",
        approval_name="GST Registration",
        department="GST Department",
        clause_ref="CGST Act, 2017 - Sec 22",
        sla_days=3, mandatory=True,
    ),
    dict(
        sector="All", location="All", min_size="Micro",
        approval_name="Shops & Establishment Registration",
        department="Labour Department",
        clause_ref="Maharashtra Shops and Establishments Act, 2017",
        sla_days=7, mandatory=True,
    ),
    dict(
        sector="All", location="All", min_size="Micro",
        approval_name="Building Plan Approval",
        department="Municipal Corporation / Gram Panchayat",
        clause_ref="Maharashtra Regional & Town Planning Act, 1966",
        sla_days=30, mandatory=True,
    ),
    dict(
        sector="All", location="All", min_size="Micro",
        approval_name="Electricity Connection NOC",
        department="MSEDCL",
        clause_ref="Electricity Act, 2003",
        sla_days=15, mandatory=True,
    ),
    dict(
        sector="All", location="All", min_size="Small",
        approval_name="Fire NOC",
        department="Maharashtra Fire Services",
        clause_ref="Maharashtra Fire Prevention & Life Safety Measures Act, 2006",
        sla_days=15, mandatory=True,
    ),
    dict(
        sector="All", location="All", min_size="Micro",
        approval_name="Trade License",
        department="Municipal Corporation",
        clause_ref="Maharashtra Municipal Corporation Act, 1949",
        sla_days=15, mandatory=True,
    ),
    dict(
        sector="Manufacturing", location="All", min_size="Small",
        approval_name="Consent to Establish (CTE)",
        department="Maharashtra Pollution Control Board",
        clause_ref="Water (P&CP) Act 1974 / Air (P&CP) Act 1981",
        sla_days=21, mandatory=True,
    ),
    dict(
        sector="Manufacturing", location="All", min_size="Small",
        approval_name="Consent to Operate (CTO)",
        department="Maharashtra Pollution Control Board",
        clause_ref="Water (P&CP) Act 1974 / Air (P&CP) Act 1981",
        sla_days=21, mandatory=True,
    ),
    dict(
        sector="Manufacturing", location="All", min_size="Small",
        approval_name="Factory License",
        department="Directorate of Industrial Safety & Health",
        clause_ref="Factories Act, 1948 - Sec 6",
        sla_days=30, mandatory=True,
    ),
    dict(
        sector="Manufacturing", location="All", min_size="Medium",
        approval_name="Boiler Registration",
        department="Directorate of Steam Boilers",
        clause_ref="Boilers Act, 1923",
        sla_days=15, mandatory=False,
    ),
    dict(
        sector="Manufacturing", location="All", min_size="Small",
        approval_name="Legal Metrology License",
        department="Legal Metrology Department",
        clause_ref="Legal Metrology Act, 2009",
        sla_days=10, mandatory=True,
    ),
    dict(
        sector="Chemical & Pharma", location="All", min_size="Small",
        approval_name="Consent to Establish (CTE)",
        department="Maharashtra Pollution Control Board",
        clause_ref="Water (P&CP) Act 1974 / Air (P&CP) Act 1981",
        sla_days=21, mandatory=True,
    ),
    dict(
        sector="Chemical & Pharma", location="All", min_size="Small",
        approval_name="Consent to Operate (CTO)",
        department="Maharashtra Pollution Control Board",
        clause_ref="Water (P&CP) Act 1974 / Air (P&CP) Act 1981",
        sla_days=21, mandatory=True,
    ),
    dict(
        sector="Chemical & Pharma", location="All", min_size="Small",
        approval_name="Factory License",
        department="Directorate of Industrial Safety & Health",
        clause_ref="Factories Act, 1948 - Sec 6",
        sla_days=30, mandatory=True,
    ),
    dict(
        sector="Chemical & Pharma", location="All", min_size="Large",
        approval_name="Environmental Clearance",
        department="SEIAA Maharashtra",
        clause_ref="EIA Notification, 2006",
        sla_days=45, mandatory=True,
    ),
    dict(
        sector="Chemical & Pharma", location="All", min_size="Medium",
        approval_name="Boiler Registration",
        department="Directorate of Steam Boilers",
        clause_ref="Boilers Act, 1923",
        sla_days=15, mandatory=False,
    ),
    dict(
        sector="Textile", location="All", min_size="Small",
        approval_name="Consent to Establish (CTE)",
        department="Maharashtra Pollution Control Board",
        clause_ref="Water (P&CP) Act 1974 / Air (P&CP) Act 1981",
        sla_days=21, mandatory=True,
    ),
    dict(
        sector="Textile", location="All", min_size="Small",
        approval_name="Factory License",
        department="Directorate of Industrial Safety & Health",
        clause_ref="Factories Act, 1948 - Sec 6",
        sla_days=30, mandatory=True,
    ),
    dict(
        sector="Textile", location="All", min_size="Medium",
        approval_name="Boiler Registration",
        department="Directorate of Steam Boilers",
        clause_ref="Boilers Act, 1923",
        sla_days=15, mandatory=False,
    ),
    dict(
        sector="Food Processing", location="All", min_size="Micro",
        approval_name="FSSAI License",
        department="Food Safety Department",
        clause_ref="Food Safety and Standards Act, 2006",
        sla_days=10, mandatory=True,
    ),
    dict(
        sector="Food Processing", location="All", min_size="Small",
        approval_name="Consent to Establish (CTE)",
        department="Maharashtra Pollution Control Board",
        clause_ref="Water (P&CP) Act 1974 / Air (P&CP) Act 1981",
        sla_days=21, mandatory=True,
    ),
    dict(
        sector="Food Processing", location="All", min_size="Small",
        approval_name="Factory License",
        department="Directorate of Industrial Safety & Health",
        clause_ref="Factories Act, 1948 - Sec 6",
        sla_days=30, mandatory=True,
    ),
    dict(
        sector="Food Processing", location="All", min_size="Small",
        approval_name="Legal Metrology License",
        department="Legal Metrology Department",
        clause_ref="Legal Metrology Act, 2009",
        sla_days=10, mandatory=True,
    ),
    dict(
        sector="IT/ITES", location="All", min_size="Micro",
        approval_name="STPI / SEZ Registration",
        department="Software Technology Parks of India",
        clause_ref="STPI Scheme Guidelines",
        sla_days=10, mandatory=False,
    ),
    dict(
        sector="Agro-Based", location="All", min_size="Micro",
        approval_name="FSSAI License",
        department="Food Safety Department",
        clause_ref="Food Safety and Standards Act, 2006",
        sla_days=10, mandatory=True,
    ),
    dict(
        sector="Agro-Based", location="All", min_size="Small",
        approval_name="Consent to Establish (CTE)",
        department="Maharashtra Pollution Control Board",
        clause_ref="Water (P&CP) Act 1974 / Air (P&CP) Act 1981",
        sla_days=21, mandatory=True,
    ),
]

SCHEMES = [
    dict(
        name="PMEGP - Prime Minister's Employment Generation Programme",
        sector="All",
        description="Credit-linked subsidy scheme for setting up new micro-enterprises in the non-farm sector.",
        benefits="15-35% capital subsidy depending on category and location; margin money support.",
    ),
    dict(
        name="Maharashtra Industrial Policy - Package Scheme of Incentives (PSI)",
        sector="Manufacturing",
        description="Fiscal incentives for eligible manufacturing units set up in the state, tiered by district development level.",
        benefits="Stamp duty exemption, electricity duty exemption, industrial promotion subsidy on GST paid.",
    ),
    dict(
        name="Interest Subsidy Scheme for MSMEs",
        sector="All",
        description="Interest subvention on term loans availed by MSMEs for setting up or expanding units.",
        benefits="5% interest subsidy for up to 5 years, capped per unit.",
    ),
    dict(
        name="Maharashtra IT/ITES Policy Incentives",
        sector="IT/ITES",
        description="Incentives for IT/ITES units including SEZ/STPI registered units and data centres.",
        benefits="Electricity duty exemption, stamp duty concession, power tariff subsidy.",
    ),
    dict(
        name="Agro-Processing Cluster Scheme",
        sector="Food Processing",
        description="Support for common infrastructure in food processing / agro clusters.",
        benefits="Capital subsidy up to 35% for cluster infrastructure, cold-chain support.",
    ),
]

DEMO_USERS = [
    dict(name="Asha Entrepreneur", email="entrepreneur@demo.com", role="entrepreneur", department=None),
    dict(name="Rahul Officer", email="officer@demo.com", role="officer", department="Maharashtra Pollution Control Board"),
    dict(name="Priya Admin", email="admin@demo.com", role="admin", department=None),
]

DEMO_USERS += [
    dict(name="Sunita DISH Officer", email="dish.officer@demo.com", role="officer", department="Directorate of Industrial Safety & Health"),
    dict(name="Vikram Fire Officer", email="fire.officer@demo.com", role="officer", department="Maharashtra Fire Services"),
    dict(name="Meera FSSAI Officer", email="fssai.officer@demo.com", role="officer", department="Food Safety Department"),
    dict(name="Kiran GST Officer", email="gst.officer@demo.com", role="officer", department="GST Department"),
    dict(name="Arjun MSME Officer", email="msme.officer@demo.com", role="officer", department="Ministry of MSME"),
    dict(name="Deepa Labour Officer", email="labour.officer@demo.com", role="officer", department="Labour Department"),
    dict(name="Ravi Municipal Officer", email="municipal.officer@demo.com", role="officer", department="Municipal Corporation / Gram Panchayat"),
    dict(name="Trade License Officer", email="trade.officer@demo.com", role="officer", department="Municipal Corporation"),
    dict(name="Anil Power Officer", email="msedcl.officer@demo.com", role="officer", department="MSEDCL"),
    dict(name="Sneha Metrology Officer", email="metrology.officer@demo.com", role="officer", department="Legal Metrology Department"),
    dict(name="Farhan SEIAA Officer", email="seiaa.officer@demo.com", role="officer", department="SEIAA Maharashtra"),
]

DEMO_PASSWORD = "password123"

# Sample applications filed by the demo entrepreneur. Checklists come from the
# real rules engine; `approved` / `rejected` / `overdue` name checklist items by
# approval_name ("ALL" approves every mandatory item). Everything else stays pending.
DEMO_APPLICATIONS = [
    dict(project_name="Shree Processing Unit", sector="Manufacturing", location="Mumbai", size="Micro", stage="New",
         age_days=1, approved=[], rejected=[],
         overdue=["GST Registration", "Shops & Establishment Registration", "Electricity Connection NOC"]),
    dict(project_name="Konkan Spice Foods", sector="Food Processing", location="Kolhapur", size="Small", stage="New",
         age_days=9, approved="ALL", rejected=[], overdue=[]),
    dict(project_name="Vidarbha Textiles Ltd", sector="Textile", location="Nagpur", size="Medium", stage="Expansion",
         age_days=6, approved=["GST Registration", "Fire NOC", "Consent to Establish (CTE)", "Factory License"],
         rejected=["Udyam Registration"], overdue=["Boiler Registration"]),
    dict(project_name="Sahyadri Auto Components", sector="Manufacturing", location="Pune", size="Medium", stage="New",
         age_days=8, approved=["Udyam Registration", "Consent to Establish (CTE)", "Consent to Operate (CTO)"],
         rejected=[], overdue=["GST Registration", "Fire NOC", "Factory License", "Legal Metrology License"]),
    dict(project_name="NeoWave IT Solutions", sector="IT/ITES", location="Pune", size="Micro", stage="New",
         age_days=12, approved="ALL", rejected=[], overdue=[]),
    dict(project_name="Deccan AgroChem Pvt Ltd", sector="Chemical & Pharma", location="Nashik", size="Large", stage="New",
         age_days=5, approved=["GST Registration", "Fire NOC", "Consent to Operate (CTO)", "Factory License"],
         rejected=["Udyam Registration"], overdue=[]),
    dict(project_name="Godavari Agro Exports", sector="Agro-Based", location="Chhatrapati Sambhajinagar", size="Small", stage="Existing",
         age_days=15, approved="ALL", rejected=[], overdue=[]),
    dict(project_name="Mumbai Precision Tools", sector="Manufacturing", location="Thane", size="Small", stage="Expansion",
         age_days=3, approved=["Udyam Registration", "Consent to Establish (CTE)", "Consent to Operate (CTO)"],
         rejected=[], overdue=[]),
    dict(project_name="Amravati Organic Foods", sector="Food Processing", location="Amravati", size="Micro", stage="New",
         age_days=4, approved=["Udyam Registration", "GST Registration", "FSSAI License"],
         rejected=[], overdue=["Shops & Establishment Registration"]),
    dict(project_name="Nagpur Logistics Hub", sector="Services", location="Nagpur", size="Medium", stage="New",
         age_days=10, approved="ALL", rejected=[], overdue=[]),
    dict(project_name="Pune Pharma Labs", sector="Chemical & Pharma", location="Pune", size="Medium", stage="Expansion",
         age_days=7, approved=["Udyam Registration", "GST Registration", "Consent to Establish (CTE)"],
         rejected=["Fire NOC"], overdue=["Factory License"]),
    dict(project_name="Nashik Grape Wines", sector="Agro-Based", location="Nashik", size="Small", stage="New",
         age_days=2, approved=[], rejected=[], overdue=[]),
    dict(project_name="Thane Garment Works", sector="Textile", location="Thane", size="Small", stage="New",
         age_days=11, approved=["Udyam Registration", "GST Registration", "Shops & Establishment Registration", "Trade License"],
         rejected=[], overdue=["Electricity Connection NOC"]),
    dict(project_name="Kolhapur Foundry Co", sector="Manufacturing", location="Kolhapur", size="Medium", stage="Existing",
         age_days=14, approved="ALL", rejected=[], overdue=[]),
    dict(project_name="Sambhajinagar Auto Ancillaries", sector="Manufacturing", location="Chhatrapati Sambhajinagar", size="Large", stage="New",
         age_days=6, approved=["Udyam Registration", "GST Registration"],
         rejected=["Consent to Establish (CTE)"], overdue=["Fire NOC"]),
    dict(project_name="Mumbai FinServe Tech", sector="IT/ITES", location="Mumbai", size="Small", stage="New",
         age_days=3, approved=["Udyam Registration", "GST Registration"], rejected=[], overdue=[]),
    dict(project_name="Nagpur Cotton Mills", sector="Textile", location="Nagpur", size="Large", stage="Expansion",
         age_days=13, approved=["Udyam Registration", "GST Registration", "Fire NOC", "Consent to Operate (CTO)"],
         rejected=["Factory License"], overdue=[]),
    dict(project_name="Pune Cloud Kitchens", sector="Food Processing", location="Pune", size="Micro", stage="New",
         age_days=5, approved=["Udyam Registration", "GST Registration", "FSSAI License"], rejected=[], overdue=[]),
    dict(project_name="Amravati Agro Processing", sector="Agro-Based", location="Amravati", size="Micro", stage="Expansion",
         age_days=8, approved="ALL", rejected=[], overdue=[]),
    dict(project_name="Nashik Specialty Chemicals", sector="Chemical & Pharma", location="Nashik", size="Large", stage="New",
         age_days=9, approved=["Udyam Registration", "GST Registration", "Fire NOC", "Consent to Establish (CTE)"],
         rejected=[], overdue=["Environmental Clearance"]),
]


def _seed_demo_applications(db: Session) -> None:
    applicant = db.query(models.User).filter_by(email="entrepreneur@demo.com").first()
    admin = db.query(models.User).filter_by(email="admin@demo.com").first()
    if not applicant or not admin:
        return

    officers = {u.department: u for u in db.query(models.User).filter_by(role="officer") if u.department}
    now = dt.datetime.utcnow()

    for spec in DEMO_APPLICATIONS:
        created = now - dt.timedelta(days=spec["age_days"])
        application = models.Application(
            applicant_id=applicant.id,
            project_name=spec["project_name"],
            sector=spec["sector"],
            location=spec["location"],
            size=spec["size"],
            stage=spec["stage"],
            status="submitted",
            created_at=created,
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        for item in generate_checklist(db, application):
            item.created_at = created
            item.due_at = created + dt.timedelta(days=item.sla_days)

            outcome = None
            if item.approval_name in spec["rejected"]:
                outcome = "rejected"
            elif spec["approved"] == "ALL":
                outcome = "approved" if item.mandatory else None
            elif item.approval_name in spec["approved"]:
                outcome = "approved"

            if outcome:
                reviewer = officers.get(item.department, admin)
                action = "reject" if outcome == "rejected" else "approve"
                item.status = outcome
                item.remarks = (
                    "Submitted documents do not match site inspection. Please resubmit."
                    if outcome == "rejected"
                    else "Verified against submitted documents."
                )
                item.reviewed_by = reviewer.id
                item.reviewed_at = created + dt.timedelta(days=1)
                db.add(models.ApprovalLog(
                    checklist_item_id=item.id, actor_id=reviewer.id, action=action,
                    remarks=item.remarks, created_at=item.reviewed_at,
                ))
            elif item.approval_name in spec["overdue"]:
                item.due_at = now - dt.timedelta(days=2 + item.sla_days % 5)

        db.refresh(application)
        _recompute_status(application)
        application.updated_at = now
        db.commit()


def seed(db: Session) -> None:
    if db.query(models.Rule).count() == 0:
        for r in RULES:
            db.add(models.Rule(**r))

    if db.query(models.Scheme).count() == 0:
        for s in SCHEMES:
            db.add(models.Scheme(**s))

    existing_emails = {email for (email,) in db.query(models.User.email)}
    for u in DEMO_USERS:
        if u["email"] not in existing_emails:
            db.add(models.User(**u, password_hash=hash_password(DEMO_PASSWORD)))

    db.commit()

    if db.query(models.Application).count() == 0:
        _seed_demo_applications(db)
