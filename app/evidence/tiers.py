import re
from dataclasses import dataclass
from app.schemas.claim import Claim, SourceSpan

__all__ = ["assign_tier", "assign_tiers", "TierRule"]


@dataclass(frozen=True)
class TierRule:
    """A rule mapping a pattern to a specific evidence tier."""
    tier: str
    name: str
    pattern: re.Pattern[str]
    description: str


# Define rules as a cascade - first match wins
_TIER_RULES: list[TierRule] = [
    # T1: Client outcomes, reviews, ratings, feedback
    TierRule("T1", "client_review", re.compile(r"(client|customer)\s*(review|feedback|testimonial|rating|outcome|result|satisfaction)", re.I), "Client outcome or review"),
    TierRule("T1", "star_rating", re.compile(r"(\d(\.\d)?\s*(star|/5|out of 5)|rated\s*\d)", re.I), "Star rating or score"),
    TierRule("T1", "revenue_impact", re.compile(r"(revenue|sales|conversion|retention|growth)\s*(increas|improv|boost|grew|reduc)", re.I), "Revenue/business impact"),
    TierRule("T1", "job_success", re.compile(r"(job success|success score|top rated|rising talent)", re.I), "Platform success metric"),
    
    # T2: Shipped software, live repos, deployed endpoints
    TierRule("T2", "github_repo", re.compile(r"(github\.com|gitlab\.com|bitbucket\.org)/[\w-]+/[\w-]+", re.I), "Live repository URL"),
    TierRule("T2", "huggingface", re.compile(r"huggingface\.co/", re.I), "Hugging Face endpoint"),
    TierRule("T2", "deployed_app", re.compile(r"(deployed|launched|shipped|released|live|production)\s*(app|application|system|platform|service|api|endpoint|website|site)", re.I), "Shipped/deployed software"),
    TierRule("T2", "app_store", re.compile(r"(app store|play store|google play|apple store)", re.I), "App store listing"),
    TierRule("T2", "open_source", re.compile(r"(open.source|stars?\s*:\s*\d|fork|contributor)", re.I), "Open source contribution"),
    
    # T3: Proctored assessments, verified system tests
    TierRule("T3", "assessment", re.compile(r"(proctored|supervised)\s*(assessment|exam|test|evaluation)", re.I), "Proctored assessment"),
    TierRule("T3", "system_test", re.compile(r"(system|integration|load|stress|performance)\s*test\s*(result|score|pass)", re.I), "Verified system test"),
    TierRule("T3", "upwork_test", re.compile(r"(upwork|freelancer)\s*(skill|proficiency)\s*test", re.I), "Platform skill test"),
    
    # T4: Industry certifications
    TierRule("T4", "cert_aws", re.compile(r"(AWS|Amazon Web Services)\s*(certified|certification|associate|professional|specialty)", re.I), "AWS Certification"),
    TierRule("T4", "cert_gcp", re.compile(r"(Google Cloud|GCP)\s*(certified|certification|professional|associate)", re.I), "GCP Certification"),
    TierRule("T4", "cert_azure", re.compile(r"(Azure|Microsoft)\s*(certified|certification|associate|expert)", re.I), "Azure Certification"),
    TierRule("T4", "cert_generic", re.compile(r"(certified|certification|credential)\s*(by|from|issued)\s*(\w+)", re.I), "Industry certification"),
    TierRule("T4", "cert_proctored", re.compile(r"(proctored|verified|credential-verified)\s*(cert|certification)", re.I), "Proctored certification"),
    
    # T5: Self-paced online courses
    TierRule("T5", "coursera", re.compile(r"coursera", re.I), "Coursera certificate"),
    TierRule("T5", "udemy", re.compile(r"udemy", re.I), "Udemy certificate"),
    TierRule("T5", "udacity", re.compile(r"udacity", re.I), "Udacity certificate"),
    TierRule("T5", "edx", re.compile(r"edx", re.I), "edX certificate"),
    TierRule("T5", "pluralsight", re.compile(r"pluralsight", re.I), "Pluralsight certificate"),
    TierRule("T5", "online_course", re.compile(r"(online\s*(course|certificate|program)|self.paced|completed\s*course)", re.I), "Online course"),
    
    # T7: LinkedIn exports, peer endorsements
    TierRule("T7", "linkedin", re.compile(r"(linkedin|linked-in)", re.I), "LinkedIn export"),
    TierRule("T7", "endorsement", re.compile(r"(endorsed|endorsement|recommendation)\s*(by|from|peer)", re.I), "Peer endorsement"),
    TierRule("T7", "skill_endorsement", re.compile(r"(\d+)\s*(endorsement|people endorse)", re.I), "Skill endorsement count"),
]


def assign_tier(claim: Claim) -> Claim:
    """
    Run cascade on the claim's source_span text or claim_text and assign tier.
    
    Args:
        claim: The claim to assign an evidence tier.
        
    Returns:
        A new Claim instance with the assigned tier and tier rule.
    """
    text = claim.claim_text or ""
    
    # Prefer source_span text if available, prepend it
    if hasattr(claim, "source_span") and claim.source_span and claim.source_span.text:
        text = claim.source_span.text + " " + text

    for rule in _TIER_RULES:
        if rule.pattern.search(text):
            try:
                # Pydantic v2 compatible
                return claim.model_copy(update={"evidence_tier": rule.tier, "tier_rule": rule.name})
            except AttributeError:
                # Fallback if Claim is not a Pydantic model
                claim.evidence_tier = rule.tier
                claim.tier_rule = rule.name
                return claim
                
    try:
        return claim.model_copy(update={"evidence_tier": "T8", "tier_rule": "self_declared"})
    except AttributeError:
        claim.evidence_tier = "T8"
        claim.tier_rule = "self_declared"
        return claim


def assign_tiers(claims: list[Claim]) -> list[Claim]:
    """
    Apply assign_tier to all claims.
    
    Args:
        claims: A list of Claim objects.
        
    Returns:
        A new list of Claim objects with updated tiers.
    """
    return [assign_tier(c) for c in claims]