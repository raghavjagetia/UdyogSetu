"""Seeds the database with demo users, a rules-as-code library modeled on
Maharashtra's single-window (MAITRI) approval landscape, and a couple of
sample government schemes. Safe to re-run: it only inserts when tables are empty.
"""

from sqlalchemy.orm import Session

from . import models
from .auth import hash_password

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

DEMO_PASSWORD = "password123"


def seed(db: Session) -> None:
    if db.query(models.Rule).count() == 0:
        for r in RULES:
            db.add(models.Rule(**r))

    if db.query(models.Scheme).count() == 0:
        for s in SCHEMES:
            db.add(models.Scheme(**s))

    if db.query(models.User).count() == 0:
        for u in DEMO_USERS:
            db.add(models.User(**u, password_hash=hash_password(DEMO_PASSWORD)))

    db.commit()
