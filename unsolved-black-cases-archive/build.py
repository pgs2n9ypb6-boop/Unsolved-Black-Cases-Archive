#!/usr/bin/env python3
"""
UNSOLVED BLACK CASES ARCHIVE — static site generator (v2 / dashboard redesign)
Single source of truth: the CASES list below. Running this script:
  1. Writes /data/cases.json (used client-side for search, timeline, map)
  2. Renders every HTML page (dashboard shell + document pages)
Run: python3 build.py
"""
import os, json, html, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT

CASH_URL = "https://cash.app/$ColdWorldPTS"
YT_URL = "https://youtube.com/@coldworldtone?si=KnIWozFL52ocj-TD"
SITE_NAME = "UNSOLVED BLACK CASES ARCHIVE"

# ---------------------------------------------------------------------------
# GOOGLE ADSENSE — placeholders only. Replace both values below with the
# real ones from your AdSense account before this does anything:
#   ADSENSE_CLIENT_ID: Settings -> Account information -> Publisher ID
#     (looks like "ca-pub-1234567890123456")
#   ADSENSE_SLOT_DEFAULT: Ads -> By ad unit -> (create a "Display ad") -> its
#     slot ID (a number like "1234567890")
# Until you do, the loader script below points at an invalid client ID, so
# it simply fails to load and no ads render — nothing here goes live by
# accident. Google also won't review/approve the site until it's hosted at
# a real, crawlable URL (see ads.txt note further down).
# ---------------------------------------------------------------------------
ADSENSE_CLIENT_ID = "ca-pub-XXXXXXXXXXXXXXXX"
ADSENSE_SLOT_DEFAULT = "0000000000"
ADSENSE_ENABLED = True  # set False to strip all AdSense code out of the build

# Used for canonical URLs and absolute Open Graph / Twitter Card image URLs.
# Update this if the site ever moves to a different domain.
SITE_URL = "https://unsolved-black-cases-archive.vercel.app"
SHORT_NAME = "UBCA"
TAGLINE = "A public-record research archive documenting unsolved cases involving Black victims."
ARCHIVE_NOTE = ("This archive summarizes publicly available information and does not conduct "
                 "independent criminal investigations.")

NAV_DOCS = [
    ("About", "about.html"),
    ("How We Research", "research.html"),
    ("Corrections & Updates", "updates.html"),
    ("Resources", "resources.html"),
    ("Submit a Tip", "submit.html"),
    ("Support", "support.html"),
    ("Contact", "contact.html"),
]

# ---------------------------------------------------------------------------
# CASE DATA — single source of truth. Fields left as None are unknown and
# rendered as "NOT AVAILABLE" rather than guessed. Source URLs are left
# blank (not fabricated) pending maintainer verification.
# ---------------------------------------------------------------------------
def src(name, url="", verified=False):
    return {"name": name, "url": url, "verified": verified}

DEFAULT_SOURCES = lambda: [src("Project Cold Case"), src("Murder Accountability Project"), src("NamUs")]

CASES = [
    dict(id="carol-denise-spinks", caseNumber="001", name="Carol Denise Spinks",
         status="unsolved", caseType="homicide", year=1971, age=13, gender="female",
         city="Washington", county=None, state="DC", caseSeries="Freeway Phantom",
         summary="Carol Denise Spinks, 13, was abducted in Southeast Washington, D.C. on April 25, 1971, "
                 "while walking home from a neighborhood store. Her body was found six days later along "
                 "I-295 near Suitland Parkway. Her case is treated as the first of six killings linked to "
                 "the unidentified offender the press dubbed the \u201cFreeway Phantom.\u201d",
         known=["Victim identity, age, and the April 25, 1971 abduction date, per the Metropolitan Police Department.",
                "Case is treated as the first in the linked Freeway Phantom series."],
         unknown=["No confirmed suspect has been named and convicted.",
                  "Full forensic and investigative case-file details are not comprehensively public."],
         unanswered=["What has been publicly confirmed about the timeline between when she was last seen and when she was found?",
                     "What forensic material, if any, has been preserved or re-tested in later decades?",
                     "What connects this case procedurally to the other five in the series?"],
         extraSources=[src("Metropolitan Police Department (MPDC) \u2014 official case page",
                            "https://mpdc.dc.gov/publication/%E2%80%9Cfreeway-phantom%E2%80%9D-homicide-victims", True),
                        src("Wikipedia \u2014 background reference", "https://en.wikipedia.org/wiki/Freeway_Phantom", True)]),
    dict(id="darlenia-denise-johnson", caseNumber="002", name="Darlenia Denise Johnson",
         status="unsolved", caseType="homicide", year=1971, age=16, gender="female",
         city="Washington", county=None, state="DC", caseSeries="Freeway Phantom",
         summary="Darlenia Denise Johnson, 16, of the Congress Heights neighborhood, was abducted on July 8, "
                 "1971 while on her way to her summer job at the Oxon Hill Recreation Center. A witness "
                 "reported seeing her in an old black car shortly afterward. Her body was found eleven days "
                 "later, only about 15 feet from where Carol Spinks had been found.",
         known=["Victim identity, age, and the July 8, 1971 abduction date, per the Metropolitan Police Department.",
                "A witness reported seeing her in a car shortly after her abduction."],
         unknown=["No confirmed suspect has been named and convicted.",
                  "Autopsy findings on cause of death were affected by a delayed police response to reports of the body, per public reporting."],
         unanswered=["What is publicly documented about where she was last seen?",
                     "What, if anything, distinguishes this case's evidence from the others in the series?",
                     "Has this case file been reviewed using modern forensic methods?"],
         extraSources=[src("Metropolitan Police Department (MPDC) \u2014 official case page",
                            "https://mpdc.dc.gov/publication/%E2%80%9Cfreeway-phantom%E2%80%9D-homicide-victims", True),
                        src("Wikipedia \u2014 background reference", "https://en.wikipedia.org/wiki/Freeway_Phantom", True)]),
    dict(id="brenda-faye-crockett", caseNumber="003", name="Brenda Faye Crockett",
         status="unsolved", caseType="homicide", year=1971, age=10, gender="female",
         city="Washington", county=None, state="DC", caseSeries="Freeway Phantom",
         summary="Brenda Faye Crockett, 10, disappeared on July 27, 1971 after her mother sent her to a "
                 "neighborhood store. Family members reported receiving two phone calls from Brenda after "
                 "she went missing, in which she described being taken by a man; her body was found the "
                 "next morning. She was the youngest of the six victims linked to the Freeway Phantom case.",
         known=["Victim identity, age, and the July 27, 1971 disappearance date, per public reporting and MPD records.",
                "Family members reported receiving phone calls from Brenda after her disappearance."],
         unknown=["No confirmed suspect has been named and convicted.",
                  "The identity of the caller and full circumstances of her death remain undisclosed in public records."],
         unanswered=["What is publicly known about the days immediately before she went missing?",
                     "What official statements exist specifically about the reported phone calls?",
                     "What remains unresolved about the discovery of her body?"],
         extraSources=[src("Metropolitan Police Department (MPDC) \u2014 official case page",
                            "https://mpdc.dc.gov/publication/%E2%80%9Cfreeway-phantom%E2%80%9D-homicide-victims", True)]),
    dict(id="nenomoshia-yates", caseNumber="004", name="Nenomoshia Yates",
         status="unsolved", caseType="homicide", year=1971, age=12, gender="female",
         city="Washington", county=None, state="DC", caseSeries="Freeway Phantom",
         summary="Nenomoshia Yates, 12, disappeared on October 1, 1971 while returning from a neighborhood "
                 "grocery store. She was the fourth victim linked to the Freeway Phantom case.",
         known=["Victim identity, age, and the October 1, 1971 disappearance date, per the Metropolitan Police Department."],
         unknown=["No confirmed suspect has been named and convicted.",
                  "Full circumstances remain undisclosed in public records."],
         unanswered=["What is publicly documented about her last known movements?",
                     "What links investigators drew between this case and the others at the time?",
                     "What case materials, if any, remain publicly accessible today?"],
         extraSources=[src("Metropolitan Police Department (MPDC) \u2014 official case page",
                            "https://mpdc.dc.gov/publication/%E2%80%9Cfreeway-phantom%E2%80%9D-homicide-victims", True)]),
    dict(id="brenda-denise-woodard", caseNumber="005", name="Brenda Denise Woodard",
         status="unsolved", caseType="homicide", year=1971, age=18, gender="female",
         city="Washington", county=None, state="DC", caseSeries="Freeway Phantom",
         summary="Brenda Denise Woodard, 18, was abducted on the night of November 15, 1971 after leaving "
                 "night school and stopping for dinner with a friend; she was the fifth victim linked to "
                 "the Freeway Phantom case in Washington, D.C. A note found in her coat pocket, reportedly "
                 "written in her own handwriting under apparent dictation, taunted police with the phrase "
                 "\u201cCatch me if you can.\u201d",
         known=["Victim identity, age, and the November 15, 1971 date, per public reporting.",
                "A note found with her body has been referenced in public reporting and by police."],
         unknown=["The note's full content and any forensic (e.g. handwriting) analysis are not fully detailed in public records.",
                  "No confirmed suspect has been named and convicted."],
         unanswered=["What has law enforcement publicly said about the note associated with this case?",
                     "Has handwriting or forensic analysis of the note been made public?",
                     "How does this case connect procedurally to the others in the series?"],
         extraSources=[src("Metropolitan Police Department (MPDC) \u2014 official case page",
                            "https://mpdc.dc.gov/publication/%E2%80%9Cfreeway-phantom%E2%80%9D-homicide-victims", True),
                        src("Wikipedia \u2014 background reference", "https://en.wikipedia.org/wiki/Freeway_Phantom", True)]),
    dict(id="diane-denise-williams", caseNumber="006", name="Diane Denise Williams",
         status="unsolved", caseType="homicide", year=1972, age=17, gender="female",
         city="Washington", county=None, state="DC", caseSeries="Freeway Phantom",
         summary="Diane Denise Williams, 17, a Ballou High School senior, was taken on September 5, 1972 "
                 "\u2014 the sixth and final victim linked to the Freeway Phantom case in Washington, D.C.",
         known=["Victim identity, age, and the September 5, 1972 date, per public reporting.",
                "Considered the final case in the series."],
         unknown=["No confirmed suspect has been named and convicted.",
                  "Full circumstances remain undisclosed in public records."],
         unanswered=["Why is this case considered the last in the series, and what evidence supports that?",
                     "What official review, if any, has this case received in recent decades?",
                     "What remains unclear about the timeline of her disappearance?"],
         extraSources=[src("Metropolitan Police Department (MPDC) \u2014 official case page",
                            "https://mpdc.dc.gov/publication/%E2%80%9Cfreeway-phantom%E2%80%9D-homicide-victims", True)]),
    dict(id="harry-and-harriette-moore", caseNumber="007", name="Harry T. Moore & Harriette Moore",
         status="unsolved", caseType="homicide", year=1951, age=None, gender=None,
         city="Mims", county="Brevard", state="FL", caseSeries=None,
         victimPhotos=[{"url": "https://www.floridamemory.com/fpc/prints/pr05145.jpg",
                         "caption": "Harry T. Moore (photo of Harriette not separately on file)",
                         "credit": "State Archives of Florida / Florida Memory \u2014 Public Domain"}],
         summary="Harry T. Moore, a founder of the Brevard County NAACP and executive secretary of the "
                 "Florida NAACP, and his wife Harriette Moore, a teacher and fellow organizer, were killed "
                 "when a bomb exploded under their bedroom floor on their 25th wedding anniversary, "
                 "Christmas night 1951. Harry died that night; Harriette died of her injuries nine days "
                 "later. A 2006 Florida Attorney General investigation concluded the bombing was carried "
                 "out by four Ku Klux Klan members \u2014 Earl J. Brooklyn, Tillman H. Belvin, Joseph N. "
                 "Cox, and Edward L. Spivey \u2014 all of whom had died before the finding was announced. "
                 "The FBI reviewed the case again in 2008 under the Emmett Till Unsolved Civil Rights Crime "
                 "Act; the U.S. Department of Justice formally closed the file in 2011, since the statute of "
                 "limitations had expired and all four men were dead.",
         known=["Both victims' identities and the date and location of the bombing.",
                "The 2006 state investigation's named findings, per the Florida Attorney General's executive summary.",
                "The DOJ's 2011 case closure, per its public Notice to Close File."],
         unknown=["No one was ever formally charged or convicted for the bombing.",
                  "Some case details remain disputed among historians and investigators."],
         unanswered=["What official documentation exists from the state's later investigative findings?",
                     "What forensic evidence from the bombing, if any, has survived and been reviewed?",
                     "What gaps remain between the state's findings and a formal prosecution?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/harry-t-moore-harriette-v-moore", True),
                        src("PBS FRONTLINE, \u201cUn(re)solved\u201d \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/harriette-v-moore/", True),
                        src("State Archives of Florida, Florida Memory \u2014 photograph record PR05145",
                            "https://www.floridamemory.com/items/show/4513", True)]),
    dict(id="roman-ducksworth-jr", caseNumber="008", name="Roman Ducksworth Jr.",
         status="unsolved", caseType="homicide", year=1962, age=27, gender="male",
         city="Taylorsville", county="Smith", state="MS", caseSeries=None,
         summary="Corporal Roman Ducksworth Jr., a 27-year-old U.S. Army military police officer, was "
                 "traveling home on emergency leave to see his wife, who was hospitalized with pregnancy "
                 "complications, when he was removed from a bus by Taylorsville, Mississippi police officer "
                 "William Kelly on April 9, 1962. Kelly shot Ducksworth twice, fatally wounding him. Kelly "
                 "was never charged; he claimed self-defense. The U.S. Department of Justice reviewed the "
                 "case under the Emmett Till Act and formally closed the file in 2010 without prosecution, "
                 "since Kelly had since died.",
         known=["Victim identity, age, and the April 9, 1962 date and circumstances, per the DOJ's public case file.",
                "Officer William Kelly's identity and role are part of the official record; he was never charged."],
         unknown=["Conflicting witness accounts exist about how the confrontation began.",
                  "The DOJ noted it could not locate the original 1962 investigative file when it reviewed the case in the 2000s."],
         unanswered=["What do the surviving witness statements from the bus say, and do they agree with the official account?",
                     "What became of the original 1962 state and local investigative records?",
                     "What, if anything, changed between the case's periodic reviews and its 2010 closure?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/roman-ducksworth-jr", True)]),
    dict(id="hattie-debardelaben", caseNumber="009", name="Hattie DeBardelaben",
         status="unsolved", caseType="homicide", year=1945, age=46, gender="female",
         city="Autaugaville", county="Autauga", state="AL", caseSeries=None,
         summary="Hattie DeBardelaben, a 46-year-old farmer and mother of eight, was killed on March 23, "
                 "1945 in Autaugaville, Alabama, after Autauga County Deputy Clyde White and three federal "
                 "officers \u2014 John Barrenbrugge and J.C. Moseley of the Alcohol Tax Unit, and L.O. Smith "
                 "of the Alabama Alcohol Beverage Control Board \u2014 conducted a warrantless search of her "
                 "home for illegal whiskey. Witnesses, including her children, said officers beat her; she "
                 "died in the back of the officers' car on the way to the county jail in Prattville. A "
                 "doctor attributed her death to a heart attack, though an undertaker reportedly noted "
                 "signs consistent with a broken neck. A state grand jury later declined to indict, and the "
                 "case was closed within months. Records released in 2024 under the Civil Rights Cold Case "
                 "Records Collection Act confirmed the officers' identities and the case's handling.",
         known=["Victim identity, age, and the March 23, 1945 date and location, per federal records released in 2024.",
                "The identities of Deputy Clyde White and the three federal officers present, per the same released records."],
         unknown=["No one was ever indicted for her death.",
                  "The full extent of what investigators privately concluded at the time, versus what was made public, remains debated by historians."],
         unanswered=["What do the newly released 2024 federal records say about how the case was closed?",
                     "What became of the officers involved in the years after the case was closed?",
                     "What further documentation might exist in state or local Alabama archives?"],
         extraSources=[src("Civil Rights Cold Case Records Review Board \u2014 official case summary",
                            "https://www.coldcaserecords.gov/content/cases/1945-03-23-hattie-debardelaben/", True),
                        src("Civil Rights and Restorative Justice Project (Northeastern Law) \u2014 case archive",
                            "https://www.crrjarchive.org/incidents/316", True)]),
    dict(id="edwin-pratt", caseNumber="010", name="Edwin Pratt",
         status="unsolved", caseType="homicide", year=1969, age=38, gender="male",
         city="Shoreline", county="King", state="WA", caseSeries=None,
         summary="Edwin T. Pratt, 38, executive director of the Seattle Urban League and a leading figure "
                 "in the city's civil rights movement, was shot and killed in the doorway of his Shoreline "
                 "home on the night of January 26, 1969. Two men were seen fleeing to a getaway car. No one "
                 "was ever charged. A 2022 U.S. Department of Justice notice closing the file names four "
                 "individuals \u2014 Thomas Kirk, Texas Barton Gray, Michael Jordan, and Guenter Mannhalt, "
                 "all since deceased \u2014 as subjects of the investigation, without a conclusive finding.",
         known=["Victim identity, role, and the January 26, 1969 date and circumstances, per the DOJ's public case file.",
                "The four subjects named in the DOJ's 2022 closure notice, all reported deceased."],
         unknown=["No one was ever charged, and the DOJ's file does not identify a definitive perpetrator or motive.",
                  "The extent to which the killing was financed or ordered by a third party remains publicly unresolved."],
         unanswered=["What evidence connects each of the four named subjects to the killing, according to the DOJ file?",
                     "What official case documentation from 1969, 1994, and 2019\u20132022 reviews is publicly accessible?",
                     "What investigative leads, if any, remain officially open?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/edwin-pratt", True),
                        src("HistoryLink.org \u2014 case summary", "https://www.historylink.org/File/4142", True)]),
    dict(id="alberta-jones", caseNumber="011", name="Alberta Jones",
         status="unsolved", caseType="homicide", year=1965, age=34, gender="female",
         city="Louisville", county="Jefferson", state="KY", caseSeries=None,
         summary="Alberta Odell Jones, 34, Louisville and Jefferson County's first Black woman prosecutor "
                 "and the attorney who negotiated a young Cassius Clay's (Muhammad Ali's) first professional "
                 "boxing contract, was found in the Ohio River near Fontaine Ferry Park on August 5, 1965. "
                 "Her rental car was found nearby with blood inside, and an autopsy found she had been "
                 "beaten with a brick before drowning. Witnesses reported seeing men force a woman into a "
                 "car earlier that night, and separately reported a car stopped on the Sherman Minton Bridge "
                 "around 4:35 a.m. The case was added to the DOJ's federal cold-case list in 2018; the DOJ "
                 "formally closed the file in August 2023, citing the loss of evidence and the deaths of "
                 "witnesses and original investigators, without identifying a suspect.",
         known=["Victim identity, professional background, and the August 5, 1965 date, per the DOJ's public case file.",
                "Her death was ruled a homicide caused by drowning after being beaten; the DOJ closed its cold-case review in August 2023."],
         unknown=["No one has been convicted in connection with her death.",
                  "A 2008 fingerprint match reported by press was, per the local prosecutor at the time, found insufficient to reopen the case."],
         unanswered=["What specific findings led the DOJ to close its file in 2023?",
                     "What became of the fingerprint evidence reported in 2008 press coverage?",
                     "What primary case documentation from 1965 remains accessible today?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/alberta-jones", True),
                        src("The Washington Post \u2014 case retrospective",
                            "https://www.washingtonpost.com/news/retropolis/wp/2017/10/09/who-killed-alberta-jones-louisvilles-first-black-woman-prosecutor/", True)]),
    dict(id="alonzo-brooks", caseNumber="012", name="Alonzo Brooks",
         status="unsolved", caseType="homicide", year=2004, age=23, gender="male",
         city="La Cygne", county="Linn", state="KS", caseSeries=None,
         victimPhotos=[{"url": "https://www.fbi.gov/wanted/seeking-info/alonzo-brooks/@@images/image/large",
                         "caption": "Alonzo Brooks", "credit": "FBI"}],
         summary="Alonzo Brooks, 23, who was Black and Mexican, disappeared after a party at a rural "
                 "farmhouse near La Cygne, Kansas on April 3, 2004, where he was one of only three Black "
                 "attendees among roughly 100 people. His body was found in nearby Middle Creek on May 1, "
                 "2004; the original coroner could not determine a cause of death. The FBI and U.S. "
                 "Attorney's Office reopened the case in 2019 as a suspected hate crime, exhumed his body "
                 "in 2020, and a 2021 federal forensic examination ruled the death a homicide. A $100,000 "
                 "reward remains unclaimed.",
         known=["Victim identity, age, and the April 3\u2013May 1, 2004 timeline, per FBI and DOJ statements.",
                "The 2021 federal forensic ruling of homicide, per the FBI's public press release."],
         unknown=["No one has been charged or convicted in connection with his death.",
                  "The FBI has not publicly named a suspect despite investigating the case as a potential hate crime."],
         unanswered=["What specific findings has the reopened FBI investigation made public since 2021?",
                     "What did the 2021 forensic examination identify as inconsistent with decomposition?",
                     "What official documentation from the party and its attendees has been made public?"],
         extraSources=[src("Federal Bureau of Investigation \u2014 seeking information listing",
                            "https://www.fbi.gov/wanted/seeking-info/alonzo-brooks", True),
                        src("Federal Bureau of Investigation \u2014 press release",
                            "https://www.fbi.gov/contact-us/field-offices/kansascity/news/press-releases/new-autopsy-determines-death-of-alonzo-brooks-was-a-homicide", True)]),
    dict(id="diamond-and-tionda-bradley", caseNumber="013", name="Diamond and Tionda Bradley",
         status="unsolved", caseType="missing_persons", year=2001, age=None, gender="female",
         city="Chicago", county="Cook", state="IL", caseSeries=None,
         victimPhotos=[
             {"url": "https://www.fbi.gov/wanted/kidnap/tionda-z.-bradley/@@images/image/large",
              "caption": "Tionda Z. Bradley", "credit": "FBI"},
             {"url": "https://www.fbi.gov/wanted/kidnap/diamond-yvette-bradley/@@images/image/large",
              "caption": "Diamond Yvette Bradley", "credit": "FBI"},
         ],
         summary="Sisters Tionda Bradley, 10, and Diamond Bradley, 3, went missing from their family's "
                 "apartment in the Bronzeville neighborhood of Chicago's South Side on July 6, 2001, while "
                 "their mother was at work. A note believed to be written by Tionda said the girls had gone "
                 "to a nearby school and store; family members have said the note's wording seemed too "
                 "advanced for Tionda's age. Chicago Police and the FBI conducted one of the largest search "
                 "efforts in city history. Neither sister has been found; the FBI is offering a reward of "
                 "up to $10,000 for information on their current whereabouts.",
         known=["Both victims' identities, ages at disappearance, and the July 6, 2001 date, per the FBI's public case listing.",
                "A note believed to be written by Tionda was recovered from the apartment."],
         unknown=["Neither sister has been located.",
                  "The note's authorship and full meaning remain publicly unresolved; several people who later claimed to be one of the sisters have been disproven."],
         unanswered=["What has renewed investigative attention in recent years established, if anything?",
                     "What has been publicly disclosed about the note found in the apartment?",
                     "What official tip-line or case-status updates are currently available?"],
         extraSources=[src("Federal Bureau of Investigation \u2014 Tionda Bradley case listing",
                            "https://www.fbi.gov/wanted/kidnap/tionda-z.-bradley", True),
                        src("Federal Bureau of Investigation \u2014 Diamond Bradley case listing",
                            "https://www.fbi.gov/wanted/kidnap/diamond-yvette-bradley", True)]),
]

for c in CASES:
    c["sources"] = c.pop("extraSources", []) + DEFAULT_SOURCES()
    # lastVerified reflects the date this build's research pass checked the
    # case against the sources above; None means not yet checked at all.
    c["lastVerified"] = "2026-08-21" if any(s["verified"] for s in c["sources"]) else None
    # dateAdded reflects when the case was added to THIS archive (not the
    # case's real-world date) — accurate as "today" for this initial batch.
    # Whoever adds a new case later should set this to the actual add date;
    # the homepage's "Latest Case Added" feature reads directly from it.
    c["dateAdded"] = "2026-08-21"

def latest_case():
    return sorted(CASES, key=lambda c: (c["dateAdded"], c["caseNumber"]))[-1]

# Case data is embedded inline on every page (see page_shell) rather than
# fetched from /data/cases.json at runtime. A plain fetch() of a local JSON
# file is blocked by the browser on the file:// scheme — which is exactly
# how someone opens this site straight out of the zip — so search, the
# timeline view, and the map view would silently return nothing. Inlining
# guarantees they work whether the site is opened directly or served over
# HTTP. /data/cases.json is still written as a portable copy of the same
# data for anyone who wants to consume it separately (e.g. a future backend).
CASES_JSON = json.dumps(CASES)

STATUS_LABEL = {"unsolved": "Unsolved", "cold": "Cold Case", "missing_persons": "Missing Persons"}
CASE_TYPE_LABEL = {"homicide": "Homicide", "missing_persons": "Missing Persons", None: None}

def na(val, upper=False):
    if val is None or val == "":
        return "NOT AVAILABLE" if upper else "Not available"
    return val

def location_str(c):
    parts = [p for p in [c.get("city"), c.get("state")] if p]
    return ", ".join(parts) if parts else "NOT AVAILABLE"

def adsense_head_tag():
    if not ADSENSE_ENABLED:
        return ""
    return (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
            f'?client={ADSENSE_CLIENT_ID}" crossorigin="anonymous"></script>\n')

def ad_slot(slot_id=None, label="Advertisement"):
    """A single clearly-labeled ad placement. Renders nothing visible beyond
    the label + empty box until ADSENSE_CLIENT_ID / the slot id are real —
    that's intentional, so the layout is correct and ready to go the moment
    real AdSense values are dropped in."""
    if not ADSENSE_ENABLED:
        return ""
    slot = slot_id or ADSENSE_SLOT_DEFAULT
    return f'''<div class="ad-slot">
  <span class="ad-slot-label">{label}</span>
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="{ADSENSE_CLIENT_ID}"
       data-ad-slot="{slot}"
       data-ad-format="auto"
       data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>'''

def initials_for(name):
    """First + last significant word of a name, for the placeholder avatar.
    Skips connectors/suffixes so 'Roman Ducksworth Jr.' -> RD, not RJ."""
    stop = {"and", "&", "jr", "sr", "iii", "ii"}
    tokens = [t.strip(".") for t in name.split() if t.strip(".").lower() not in stop and len(t.strip(".")) > 1]
    if not tokens:
        return "?"
    if len(tokens) == 1:
        return tokens[0][0].upper()
    return (tokens[0][0] + tokens[-1][0]).upper()

def avatar_block(c, size_class="lg"):
    """Renders real photo(s) if the case record has them (victimPhotos: a
    list of {url, caption, credit}), otherwise a plain initials placeholder.
    This archive does not fetch or guess at photographs of real people — a
    case only gets a photo once a maintainer adds a specific, rights-cleared
    image with a named source (e.g. an official FBI missing-persons photo,
    which is U.S. government work). Supports one photo or, for multi-victim
    cases, several shown side by side."""
    photos = c.get("victimPhotos") or ([{"url": c["victimPhoto"]}] if c.get("victimPhoto") else [])
    if photos:
        imgs = "".join(
            f'<div class="avatar-photo-item"><img class="avatar-photo {size_class}" '
            f'src="{html.escape(p["url"])}" alt="Photo of {html.escape(p.get("caption") or c["name"])}">'
            + (f'<span class="avatar-credit">{html.escape(p["credit"])}</span>' if p.get("credit") else "")
            + '</div>'
            for p in photos
        )
        return f'<div class="avatar-wrap avatar-multi">{imgs}</div>'
    return (f'<div class="avatar-wrap"><div class="avatar-placeholder {size_class}" aria-hidden="true">'
            f'<span>{initials_for(c["name"])}</span></div>'
            f'<span class="avatar-caption">No verified photo on file</span></div>')

# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------
ICON_CASHAPP = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5" stroke="currentColor" stroke-width="1.6"/><path d="M15.5 8.2c-.7-.7-1.8-1.1-3-1.1-2 0-3.3 1-3.3 2.4 0 1.3 1 1.9 2.6 2.3l1 .2c1.9.4 3.2 1.2 3.2 2.8 0 1.8-1.6 3-4 3-1.5 0-2.8-.5-3.6-1.3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M12 5.6v1.4M12 17v1.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
ICON_YOUTUBE = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="4" stroke="currentColor" stroke-width="1.6"/><path d="M10.5 9.3v5.4l4.8-2.7-4.8-2.7Z" fill="currentColor"/></svg>'

def support_buttons(size=""):
    cls = "btn-support small" if size == "small" else "btn-support"
    return (f'<a class="{cls} btn-cashapp" href="{CASH_URL}" target="_blank" rel="noopener noreferrer">{ICON_CASHAPP}<span>Donate with Cash App</span></a>'
            f'<a class="{cls} btn-youtube" href="{YT_URL}" target="_blank" rel="noopener noreferrer">{ICON_YOUTUBE}<span>Subscribe on YouTube</span></a>')

# ---------------------------------------------------------------------------
def rel(depth): return "../" * depth

SITEMAP_PATHS = []

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    if path.endswith(".html") and path != "404.html":
        SITEMAP_PATHS.append(path)
    print("wrote", path)

def top_header(depth, active=""):
    r = rel(depth)
    return f'''<a class="skip-link" href="#main">Skip to main content</a>
<header class="top-header">
  <div class="th-left">
    <button class="th-btn th-menu-btn" data-menu-toggle aria-expanded="false" aria-controls="case-files-panel">\u2261 FILES</button>
    <a class="th-logo" href="{r}index.html">
      <span class="th-monogram" aria-hidden="true">{SHORT_NAME}</span>
      <span class="th-name">{SITE_NAME}<small>Case Research System</small></span>
    </a>
  </div>
  <div class="th-center"><span class="dot" aria-hidden="true"></span> ARCHIVE ONLINE</div>
  <nav class="th-right" aria-label="Utility">
    <button class="th-btn" data-search-open>SEARCH</button>
    <a class="th-btn hide-sm" href="{r}cases/index.html">CASE INDEX</a>
    <a class="th-btn hide-sm" href="{r}about.html">ABOUT</a>
  </nav>
</header>
<div class="search-overlay" role="dialog" aria-modal="true" aria-label="Search archive">
  <div class="search-modal">
    <label class="visually-hidden" for="global-search-input">Search victims, locations, or case details</label>
    <input type="search" id="global-search-input" placeholder="Search victims, locations, or case details&hellip;">
    <div class="search-results"></div>
  </div>
</div>'''

def footer_html(depth):
    r = rel(depth)
    doc_links = "\n        ".join(f'<li><a href="{r}{href}">{label}</a></li>' for label, href in NAV_DOCS)
    return f'''<footer class="site-footer">
  <div class="footer-top">
    <div class="footer-col">
      <h4>{SHORT_NAME}</h4>
      <p style="font-size:.85rem; color:var(--text-dim); max-width:34ch;">{TAGLINE}</p>
    </div>
    <div class="footer-col">
      <h4>Archive</h4>
      <ul>
        <li><a href="{r}index.html">Dashboard</a></li>
        <li><a href="{r}cases/index.html">Case Index</a></li>
        <li><a href="{r}cases/freeway-phantom.html">Freeway Phantom Series</a></li>
        {doc_links}
      </ul>
    </div>
    <div class="footer-col">
      <h4>Support</h4>
      <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-start;">
        {support_buttons("small")}
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <span>&copy; {SITE_NAME}. Public-record research archive.</span>
    <span><a href="{r}privacy.html">Privacy Policy</a> \u00b7 <a href="{r}terms.html">Terms of Use</a> \u00b7 <a href="{r}disclaimer.html">Disclaimer</a></span>
  </div>
</footer>'''

def consent_banner_html(depth):
    r = rel(depth)
    if not ADSENSE_ENABLED:
        return ""
    return f'''<div class="consent-banner" id="consent-banner">
  <p>This site uses cookies, including to serve ads personalized to your interests via Google AdSense.
  See our <a href="{r}privacy.html">Privacy Policy</a> for details and opt-out options.</p>
  <div class="consent-actions">
    <button class="consent-btn" data-consent-decline>Decline</button>
    <button class="consent-btn primary" data-consent-accept>Accept</button>
  </div>
</div>'''

def page_shell(title, description, depth, body, data_root_depth=None, canonical_path="", og_image=None, og_type="website", og_title=None):
    r = rel(depth)
    dr = rel(data_root_depth if data_root_depth is not None else depth)
    full_title = f'{html.escape(title)} \u00b7 {SHORT_NAME}'
    share_title = html.escape(og_title) if og_title else full_title
    canonical_url = f'{SITE_URL}/{canonical_path}' if canonical_path else f'{SITE_URL}/'
    image_url = f'{SITE_URL}/{og_image}' if og_image else f'{SITE_URL}/og/site.png'
    og_tags = f'''<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SHORT_NAME}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:title" content="{share_title}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{share_title}">
<meta name="twitter:description" content="{html.escape(description)}">
<meta name="twitter:image" content="{image_url}">
'''
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{full_title}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical_url}">
<link rel="icon" type="image/svg+xml" href="{r}favicon.svg">
{og_tags}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}css/style.css">
{adsense_head_tag()}</head>
<body data-root="{dr}">
{body}
{consent_banner_html(depth)}
<script src="{r}js/cases-data.js"></script>
<script src="{r}js/main.js"></script>
</body>
</html>'''

# ---------------------------------------------------------------------------
# Left panel (Case Files)
# ---------------------------------------------------------------------------
def left_panel(depth, active_id=None):
    r = rel(depth)
    items = []
    for c in CASES:
        current = ' aria-current="page"' if c["id"] == active_id else ""
        search_blob = f'{c["name"]} {c.get("city") or ""} {c.get("state") or ""} {c["year"]}'
        is_series = "true" if c.get("caseSeries") == "Freeway Phantom" else "false"
        items.append(f'''<li class="pl-item" data-case-item data-case-id="{c['id']}" data-status="{c['status']}" data-case-type="{c.get('caseType') or ''}" data-series-flag="{is_series}" data-search="{html.escape(search_blob)}">
  <a href="{r}cases/{c['id']}.html"{current}>{html.escape(c['name'])}<span class="pi-meta">{c['caseNumber']} \u00b7 {c['year']} \u00b7 {STATUS_LABEL.get(c['status'],'').upper()}</span></a>
</li>''')
    items_html = "\n".join(items)
    return f'''<aside class="panel-left area-left" id="case-files-panel">
  <div class="pl-head"><h2>Case Files</h2><button class="pl-close" data-drawer-close aria-label="Close case files panel">&times;</button></div>
  <div class="pl-search">
    <label class="label" for="pl-search-input">Search Archive</label>
    <input type="search" id="pl-search-input" placeholder="Search victims, locations, or case details&hellip;">
  </div>
  <div class="pl-filters" role="group" aria-label="Filter case files">
    <button class="pl-chip" aria-pressed="true" data-filter="all">All Cases</button>
    <button class="pl-chip" aria-pressed="false" data-filter="unsolved">Unsolved</button>
    <button class="pl-chip" aria-pressed="false" data-filter="missing_persons">Missing Persons</button>
    <button class="pl-chip" aria-pressed="false" data-filter="cold">Cold Case</button>
    <button class="pl-chip" aria-pressed="false" data-filter="series">Case Series</button>
  </div>
  <div class="pl-series-link"><a href="{r}cases/freeway-phantom.html">Freeway Phantom \u2192</a></div>
  <div class="pl-list-head">Recent Cases</div>
  <ul class="pl-list">
    {items_html}
  </ul>
  <p class="no-results" style="display:none; padding:0 16px 16px; font-size:.8rem;">No matching cases.</p>
</aside>
<div class="panel-scrim"></div>'''

def source_records_html(c):
    items = []
    for s in c["sources"]:
        link = f'<a class="slink" href="{s["url"]}" target="_blank" rel="noopener noreferrer">View Source \u2192</a>' if s["url"] else '<span class="slink disabled">SOURCE LINK NOT AVAILABLE</span>'
        items.append(f'''<div class="source-item">
  <span class="sname">{html.escape(s['name'])}</span>
  {link}
  <span class="sverified">{'VERIFIED' if s['verified'] else 'UNVERIFIED'}</span>
</div>''')
    return "\n".join(items)

def profile_panel(c):
    series_row = f'''<div class="pp-row"><span class="label">Case Series</span><span class="value">{html.escape(c["caseSeries"])}</span></div>''' if c.get("caseSeries") else ""
    age_row = f'''<div class="pp-row"><span class="label">Age</span><span class="value">{c["age"]}</span></div>''' if c.get("age") is not None else ""
    case_type = CASE_TYPE_LABEL.get(c.get("caseType")) or na(c.get("caseType"), upper=True)
    return f'''<aside class="panel-profile area-profile">
  <div class="pp-head">Case Profile</div>
  <div class="pp-grid">
    <div class="pp-row"><span class="label">Status</span><span class="status-badge status-{c['status']}">{STATUS_LABEL.get(c['status'],'Unsolved')}</span></div>
    <div class="pp-row"><span class="label">Victim</span><span class="value">{html.escape(c['name'])}</span></div>
    {age_row}
    <div class="pp-row"><span class="label">Year</span><span class="value">{c['year'] if c['year'] else 'NOT AVAILABLE'}</span></div>
    <div class="pp-row"><span class="label">Location</span><span class="value">{location_str(c)}</span></div>
    <div class="pp-row"><span class="label">Case Type</span><span class="value">{case_type}</span></div>
    {series_row}
  </div>
</aside>'''

def sources_panel(c):
    return f'''<aside class="panel-sources area-sources">
  <div class="pp-head">Source Records</div>
  {source_records_html(c)}
  <div class="last-verified"><strong>Last Verified:</strong> {c['lastVerified'] or 'NOT YET VERIFIED'}</div>
  <div class="archive-note">&ldquo;{ARCHIVE_NOTE}&rdquo;</div>
  {ad_slot(label="Advertisement")}
</aside>'''

def questions_panel(c):
    items = "\n".join(f'<div class="pq-item">{html.escape(q)}</div>' for q in c.get("unanswered", []))
    return f'''<section class="panel-questions area-questions">
  <details class="pq-details" open>
    <summary class="pq-head">Unanswered Questions</summary>
    <div class="pq-list">
      {items}
    </div>
  </details>
</section>'''

def board_card(label, title, body_html, hub=False, list_items=None):
    cls = "board-card hub" if hub else "board-card"
    inner = body_html
    if list_items is not None:
        if list_items:
            inner = '<ul class="bc-list">' + "".join(f"<li>{html.escape(i)}</li>" for i in list_items) + "</ul>"
        else:
            inner = '<p class="bc-body unavailable">NOT AVAILABLE IN CURRENT RECORD</p>'
    return f'''<div class="{cls}">
  <span class="bc-label">{label}</span>
  {f'<h3 class="bc-title">{title}</h3>' if title else ''}
  {inner}
</div>'''

def case_board(c):
    cards = []
    hub_meta = f'{c["year"] or "NOT AVAILABLE"}{" \u00b7 Age " + str(c["age"]) if c.get("age") is not None else ""} \u00b7 {location_str(c)}'
    hub_body = avatar_block(c, size_class="sm") + f'<p class="bc-body">{hub_meta}</p>'
    cards.append(board_card("Victim", c["name"], hub_body, hub=True))
    lki = c.get("summary") or None
    cards.append(board_card("Last Known Information", None,
        f'<p class="bc-body">{html.escape(lki)}</p>' if lki else '<p class="bc-body unavailable">NOT AVAILABLE IN CURRENT RECORD</p>'))
    cards.append(board_card("Location", None,
        f'<p class="bc-body">{location_str(c)}{" \u00b7 " + c["county"] + " County" if c.get("county") else ""}</p>'))
    cards.append(board_card("Discovery / Timeline", None, None, list_items=[
        f"{c['year']}: Case opens \u2014 victim reported missing or found." if c["year"] else "Date not available.",
        "Documented milestones (renewed investigation, media coverage, family advocacy) to be added as sourced.",
        "Present: case remains unresolved. No named suspect has been convicted."
    ]))
    cards.append(board_card("Investigation", None, None, list_items=c.get("known", [])))
    cards.append(board_card("What Remains Unknown", None, None, list_items=c.get("unknown", [])))
    cards.append(board_card("Sources", None, None, list_items=[s["name"] for s in c["sources"]]))
    return "\n".join(cards)

def board_toolbar():
    return '''<div class="board-toolbar">
    <button class="bt-btn" data-board-zoom-out>\u2212 ZOOM</button>
    <button class="bt-btn" data-board-zoom-in>+ ZOOM</button>
    <button class="bt-btn" data-board-reset>RESET VIEW</button>
  </div>'''

def build_case_page(c):
    depth = 1
    related = [x for x in CASES if x.get("caseSeries") == c.get("caseSeries") and x["id"] != c["id"] and c.get("caseSeries")]
    related_html = ""
    if related:
        cards = "\n".join(
            f'<a class="related-card" href="{r["id"]}.html"><span class="rc-name">{html.escape(r["name"])}</span>'
            f'<span class="rc-meta">{r["year"]} \u00b7 {STATUS_LABEL.get(r["status"],"").upper()}</span></a>'
            for r in related)
        related_html = f'''<section class="panel-questions" style="border-top:1px solid var(--border);">
  <div class="pq-head">Related Cases</div>
  <div class="related-grid">{cards}</div>
</section>'''

    body = f'''{top_header(depth)}
<div class="app-shell">
  {left_panel(depth, active_id=c["id"])}
  <section class="panel-board area-board">
    <div class="board-head">
      <div>
        <span class="board-file-no">CASE FILE #{c['caseNumber']}</span>
        <h1>{html.escape(c['name'])}</h1>
      </div>
      {board_toolbar()}
    </div>
    <div class="board-viewport">
      <div class="board-canvas">
        <svg class="connectors"></svg>
        {case_board(c)}
      </div>
    </div>
  </section>
  {profile_panel(c)}
  {sources_panel(c)}
  {questions_panel(c)}
</div>
{related_html}
<p style="text-align:center; padding:18px;"><a href="index.html" style="font-family:var(--mono); font-size:.75rem; letter-spacing:.06em; text-transform:uppercase; color:var(--cyan);">\u2190 Return to Case Board</a></p>
{footer_html(depth)}'''
    html_out = page_shell(c["name"], f"Unsolved case: {c['name']}, {c['year']}, {location_str(c)}.", depth, body,
                          canonical_path=f"cases/{c['id']}.html", og_image=f"og/cases/{c['id']}.png", og_type="article")
    write(f"cases/{c['id']}.html", html_out)

def build_freeway_phantom():
    depth = 1
    victims = [c for c in CASES if c.get("caseSeries") == "Freeway Phantom"]
    cards = "\n".join(
        f'<a class="related-card" href="{v["id"]}.html"><span class="rc-name">{html.escape(v["name"])}</span>'
        f'<span class="rc-meta">{v["year"]} \u00b7 AGE {v["age"] or "N/A"}</span></a>' for v in victims)
    body = f'''{top_header(depth)}
<div class="app-shell">
  {left_panel(depth)}
  <section class="panel-board area-board">
    <div class="board-head">
      <div>
        <span class="board-file-no">CASE SERIES</span>
        <h1>The Freeway Phantom</h1>
      </div>
    </div>
    <div style="padding:20px;">
      <p>Six young Black women and girls were killed in Washington, D.C. between April 1971 and September
      1972. Press coverage at the time linked the deaths and gave the unidentified offender the name
      &ldquo;Freeway Phantom.&rdquo; The case remains unsolved. No one has ever been charged.</p>
      <div class="callout warn"><strong>Disclaimer:</strong> This page summarizes publicly reported
      information for research and awareness. It does not accuse any individual of a crime and does not
      claim new evidence.</div>
      <h2 style="margin-top:24px;">Documented Victims</h2>
      <div class="related-grid" style="margin-top:12px;">{cards}</div>
    </div>
  </section>
  <aside class="panel-profile area-profile">
    <div class="pp-head">Series Profile</div>
    <div class="pp-grid">
      <div class="pp-row"><span class="label">Status</span><span class="status-badge status-unsolved">Unsolved</span></div>
      <div class="pp-row"><span class="label">Cases in Series</span><span class="value">{len(victims)}</span></div>
      <div class="pp-row"><span class="label">Span</span><span class="value">1971&ndash;1972</span></div>
      <div class="pp-row"><span class="label">Location</span><span class="value">Washington, D.C.</span></div>
    </div>
  </aside>
  <aside class="panel-sources area-sources">
    <div class="pp-head">Source Records</div>
    {source_records_html({"sources": DEFAULT_SOURCES()})}
    <div class="last-verified"><strong>Last Verified:</strong> NOT YET VERIFIED</div>
    <div class="archive-note">&ldquo;{ARCHIVE_NOTE}&rdquo;</div>
  </aside>
  <section class="panel-questions area-questions">
    <details class="pq-details" open>
      <summary class="pq-head">Unanswered Questions</summary>
      <div class="pq-list">
        <div class="pq-item">What links, beyond geography and timeframe, were officially drawn between the six cases?</div>
        <div class="pq-item">What forensic re-examination, if any, has been conducted in recent decades?</div>
        <div class="pq-item">What case materials remain accessible to researchers and family members today?</div>
      </div>
    </details>
  </section>
</div>
{footer_html(depth)}'''
    write("cases/freeway-phantom.html", page_shell("The Freeway Phantom", "Series page for the six Freeway Phantom cases, Washington D.C., 1971-1972.", depth, body,
          canonical_path="cases/freeway-phantom.html", og_image="og/freeway-phantom.png", og_type="article"))

def build_case_index():
    depth = 1
    grid_cards = "\n".join(
        f'<a class="related-card" data-case-item data-case-id="{c["id"]}" data-status="{c["status"]}" data-case-type="{c.get("caseType") or ""}" '
        f'data-series-flag="{"true" if c.get("caseSeries")=="Freeway Phantom" else "false"}" '
        f'data-search="{html.escape(c["name"] + " " + (c.get("city") or "") + " " + (c.get("state") or "") + " " + str(c["year"]))}" '
        f'href="{c["id"]}.html"><span class="rc-name">{html.escape(c["name"])}</span>'
        f'<span class="rc-meta">{c["year"]} \u00b7 {STATUS_LABEL.get(c["status"],"").upper()}</span></a>' for c in CASES)
    body = f'''{top_header(depth)}
<div class="app-shell">
  {left_panel(depth)}
  <section class="panel-board area-board span-right">
    <div class="board-head">
      <div><span class="board-file-no">ARCHIVE</span><h1>Case Index</h1></div>
    </div>
    <div class="view-tabs" role="group" aria-label="View mode">
      <button class="bt-btn" data-view-tab="board" aria-pressed="true">BOARD</button>
      <button class="bt-btn" data-view-tab="timeline" aria-pressed="false">TIMELINE</button>
      <button class="bt-btn" data-view-tab="map" aria-pressed="false">MAP</button>
    </div>
    <div style="padding:20px 20px 0;">{ad_slot(label="Advertisement")}</div>
    <div class="view-panel active" id="view-board"><div class="related-grid" style="padding:20px 0;">{grid_cards}</div><p class="no-results" style="display:none;">No cases match your search or filter.</p></div>
    <div class="view-panel" id="view-timeline"></div>
    <div class="view-panel" id="view-map"></div>
  </section>
</div>
{footer_html(depth)}'''
    write("cases/index.html", page_shell("Case Index", "Search, browse by timeline, or view cases geographically.", depth, body,
          canonical_path="cases/index.html"))

def build_home():
    depth = 0
    total = len(CASES)
    unsolved_ct = sum(1 for c in CASES if c["status"] in ("unsolved", "missing_persons"))
    span = f'{min(c["year"] for c in CASES)}\u2013{max(c["year"] for c in CASES)}'
    latest = latest_case()
    excerpt = latest.get("summary") or ""
    if len(excerpt) > 220:
        excerpt = excerpt[:217].rsplit(" ", 1)[0] + "\u2026"
    featured = f'''<div class="featured-case">
    {avatar_block(latest)}
    <div class="fc-body">
      <span class="fc-eyebrow">Latest Case Added</span>
      <h2>{html.escape(latest['name'])}</h2>
      <div class="fc-meta">
        <span class="status-badge status-{latest['status']}">{STATUS_LABEL.get(latest['status'],'Unsolved')}</span>
        <span>{latest['year'] or 'NOT AVAILABLE'} \u00b7 {location_str(latest)}</span>
      </div>
      <p class="fc-excerpt">{html.escape(excerpt)}</p>
      <a class="fc-link" href="cases/{latest['id']}.html">View Full Case File \u2192</a>
    </div>
  </div>'''
    overview = f'''<div class="overview-grid">
    <div class="overview-card"><span class="num">{total}</span><span class="cap">Cases Documented</span></div>
    <div class="overview-card"><span class="num">{unsolved_ct}</span><span class="cap">Unsolved / Missing</span></div>
    <div class="overview-card"><span class="num">{span}</span><span class="cap">Span of Cases</span></div>
    <div class="overview-card"><span class="num">1</span><span class="cap">Case Series Tracked</span></div>
  </div>
  <div style="padding:0 20px 24px;">
    <p>This archive organizes publicly reported information on unsolved cases involving Black victims. It
    does not conduct original investigations and does not accuse any individual of a crime. Select a case
    from the Case Files panel, or open the full <a href="cases/index.html">Case Index</a> to search by
    timeline or location.</p>
  </div>'''
    body = f'''{top_header(depth)}
<div class="app-shell">
  {left_panel(depth)}
  <section class="panel-board area-board">
    <div class="board-head">
      <div><span class="board-file-no">DASHBOARD</span><h1>Archive Overview</h1></div>
    </div>
    <div style="padding:20px 20px 0;">{featured}</div>
    {overview}
  </section>
  <aside class="panel-profile area-profile">
    <div class="pp-head">Collection Profile</div>
    <div class="pp-grid">
      <div class="pp-row"><span class="label">Scope</span><span class="value">Unsolved homicides &amp; missing-persons cases involving Black victims</span></div>
      <div class="pp-row"><span class="label">Method</span><span class="value">Public-record research only</span></div>
      <div class="pp-row"><span class="label">Series Tracked</span><span class="value">Freeway Phantom (6 cases)</span></div>
    </div>
  </aside>
  <aside class="panel-sources area-sources">
    <div class="pp-head">Getting Started</div>
    <div class="pq-list" style="grid-template-columns:1fr;">
      <div class="pq-item">Use SEARCH (top right, or press &ldquo;/&rdquo;) to find a case by name, city, state, or year &mdash; or anything written inside a case file.</div>
      <div class="pq-item">Open the Case Index to browse by timeline or geography.</div>
      <div class="pq-item">Select any case in the left panel to open its investigation board.</div>
    </div>
    {ad_slot(label="Advertisement")}
  </aside>
  <section class="panel-questions area-questions">
    <details class="pq-details" open>
      <summary class="pq-head">About This Archive</summary>
      <div class="pq-list">
        <div class="pq-item">A public-record research archive documenting unsolved cases involving Black victims.</div>
        <div class="pq-item">Does not conduct original investigations, and does not accuse any individual of a crime.</div>
        <div class="pq-item">Read the full <a href="about.html">mission</a> or <a href="research.html">research standards</a>.</div>
      </div>
    </details>
  </section>
</div>
{footer_html(depth)}'''
    write("index.html", page_shell("Dashboard", TAGLINE, depth, body, canonical_path="", og_title=SITE_NAME.title()))

# ---------------------------------------------------------------------------
# Document pages (About, Research, Resources, Submit, Support, Contact, Legal)
# ---------------------------------------------------------------------------
def doc_page(depth, eyebrow, h1, body_inner):
    return f'''{top_header(depth)}
<main id="main" class="doc-shell">
  <div class="doc-header"><span class="label">{eyebrow}</span><h1>{h1}</h1></div>
  <div class="doc-body">
    {body_inner}
  </div>
  {ad_slot(label="Advertisement")}
</main>
{footer_html(depth)}'''

def support_section(heading="Support the Archive"):
    return f'''<div class="support-panel" style="margin-top:24px;">
  <span class="label">Independently maintained</span>
  <h2>{heading}</h2>
  <p>This archive is free to use and independently maintained. If it's useful to you, you can help keep it going and help these stories reach more people.</p>
  <div class="support-buttons">{support_buttons()}</div>
</div>'''

def build_about():
    depth = 0
    body = f'''<h2>Mission</h2>
    <p>{SITE_NAME} is a respectful, research-based archive of publicly reported unsolved homicides and
    missing-persons cases involving Black victims. Many of these cases receive far less sustained media
    attention than comparable cases involving white victims &mdash; a pattern researchers and journalists
    have documented for decades. This archive exists to keep these names, and the facts already on the
    public record about them, visible and searchable in one place.</p>
    <h2>What we do</h2>
    <ul>
      <li>Collect and summarize information that is already public: news coverage, official statements, court records, and documented investigative journalism.</li>
      <li>Organize cases so family members, researchers, journalists, and the public can find them.</li>
      <li>Attribute information to named source databases (Project Cold Case, Murder Accountability Project, NamUs) rather than presenting it as UBCA's own findings.</li>
      <li>Provide a way for people with documented information to submit it for review.</li>
    </ul>
    <h2>What we don't do</h2>
    <ul>
      <li>We do not conduct original investigations.</li>
      <li>We do not name or accuse any individual as a suspect unless that has been done in an official, publicly documented capacity.</li>
      <li>We do not claim to possess new evidence, and we do not imply UBCA is a law-enforcement body.</li>
      <li>We do not sensationalize. Case files are written in plain, factual language.</li>
    </ul>
    <p>Read more on the <a href="research.html">How We Research</a> page.</p>
    {support_section()}'''
    write("about.html", page_shell("About", "Mission and scope of the archive.", depth, doc_page(depth, "About", "About the Archive", body), canonical_path="about.html"))

def build_research():
    depth = 0
    body = '''<h2>Our standards</h2>
    <p>Every case file in this archive is built from publicly available material.</p>
    <h3>1. Public record only</h3>
    <p>We draw from published news reporting, official law-enforcement statements, court filings, and documented investigative journalism &mdash; never rumor or unverified claims.</p>
    <h3>2. No accusations without official basis</h3>
    <p>We do not name a person as a suspect or perpetrator unless that determination was made through an official process. Where a name has circulated publicly but has no official basis, we omit it.</p>
    <h3>3. Distinguishing fact from source, from the unconfirmed</h3>
    <p>Case boards separate <strong>documented fact</strong>, <strong>source information</strong> (attributed to Project Cold Case, Murder Accountability Project, or NamUs), and clearly marked <strong>unconfirmed information</strong> or <strong>unknown</strong> fields. Fields without a verified source read &ldquo;NOT AVAILABLE IN CURRENT RECORD&rdquo; rather than being filled with a guess.</p>
    <h3>4. Respectful language</h3>
    <p>We write about victims as people, not case numbers, and avoid graphic or speculative framing.</p>
    <h3>5. Corrections</h3>
    <p>Use the <a href="submit.html">Submit a Case or Tip</a> page to flag an error or contribute a documented source.</p>
    <div class="callout"><strong>Scope:</strong> This archive is a reference tool, not an investigative body. If you have information relevant to an active case, contact the relevant law-enforcement agency directly in addition to reaching out to us.</div>'''
    write("research.html", page_shell("How We Research", "Our sourcing and research standards.", depth, doc_page(depth, "Methodology", "How We Research", body), canonical_path="research.html"))

def build_resources():
    depth = 0
    body = '''<h2>National databases</h2>
    <ul>
      <li><strong>NamUs</strong> &mdash; the U.S. Department of Justice's National Missing and Unidentified Persons System.</li>
      <li><strong>Murder Accountability Project</strong> &mdash; a nonprofit tracking unsolved-homicide data nationally.</li>
      <li><strong>Project Cold Case</strong> &mdash; an independent cold-case research initiative.</li>
      <li><strong>Black and Missing Foundation</strong> &mdash; a nonprofit focused on raising the profile of missing persons of color.</li>
    </ul>
    <h2>For families</h2>
    <ul>
      <li>Consider requesting your case file's status directly from the investigating agency.</li>
      <li>Victim-advocacy organizations in your state can help navigate law-enforcement communication.</li>
      <li>Local NAACP chapters and civil-rights legal organizations have supported family advocacy in several of the cases documented here.</li>
    </ul>
    <div class="callout warn"><strong>If you are in immediate danger or have information about an active crime</strong>, contact local law enforcement or emergency services directly.</div>'''
    write("resources.html", page_shell("Resources", "Databases, organizations, and reading for families and researchers.", depth, doc_page(depth, "Resources", "Resources", body), canonical_path="resources.html"))

def build_submit():
    depth = 0
    body = '''<h2>Guidelines before you submit</h2>
    <ul>
      <li>Share information you can point to a public source for wherever possible.</li>
      <li>If you have information about an active investigation, also contact the relevant law-enforcement agency directly.</li>
      <li>Do not submit unverified accusations against a named individual &mdash; we will not publish them.</li>
      <li>If you are a family member, you're welcome to note that so we can prioritize sensitivity in how the case is presented.</li>
    </ul>
    <form class="form-grid" onsubmit="return false;" aria-label="Submit a case or tip">
      <div class="field"><label for="case-name">Case or victim name</label><input type="text" id="case-name" required></div>
      <div class="field"><label for="case-year">Year (approximate is fine)</label><input type="text" id="case-year"></div>
      <div class="field"><label for="case-location">Location</label><input type="text" id="case-location"></div>
      <div class="field"><label for="case-type">Submission type</label>
        <select id="case-type">
          <option>New case suggestion</option>
          <option>Correction or update to an existing case</option>
          <option>Source or citation to add</option>
          <option>Other</option>
        </select>
      </div>
      <div class="field"><label for="case-details">Details &amp; sources</label>
        <textarea id="case-details" placeholder="What you know, and where it's documented (links welcome)."></textarea>
        <p class="hint">Please avoid pasting unsourced accusations against a named individual.</p>
      </div>
      <div class="field"><label for="contact-email">Your email (optional)</label><input type="email" id="contact-email"></div>
      <div class="checkbox-row"><input type="checkbox" id="family-member"><label for="family-member" style="margin:0; font-weight:400;">I am a family member of the person in this case</label></div>
      <button class="btn-primary" type="submit">Submit</button>
      <p class="hint">Template form &mdash; connect to a backend (Formspree, Netlify Forms, custom endpoint) before publishing.</p>
    </form>'''
    write("submit.html", page_shell("Submit a Case or Tip", "Submit a new case or documented information about an existing case.", depth, doc_page(depth, "Contribute", "Submit a Case or Tip", body), canonical_path="submit.html"))

def build_support():
    depth = 0
    body = f'''<p>{SITE_NAME} is independently maintained and free to use. There's no paywall and no ads.</p>
    {support_section("Two ways to help")}
    <h2 style="margin-top:32px;">Other ways to help</h2>
    <ul>
      <li>Share a case page with someone who might have information.</li>
      <li>Submit a correction or documented source via <a href="submit.html">Submit a Tip</a>.</li>
      <li>Follow and share the coverage on YouTube.</li>
    </ul>'''
    write("support.html", page_shell("Support the Archive", "Support the archive via Cash App or YouTube.", depth, doc_page(depth, "Support", "Support the Archive", body), canonical_path="support.html"))

def build_contact():
    depth = 0
    body = '''<p>For tips, corrections, sourcing, press, or family inquiries, please use the
    <a href="submit.html">Submit a Case or Tip</a> form, or replace this paragraph with a direct
    contact email once one is set up for the site.</p>
    <p class="hint">Placeholder: add a monitored contact email or contact form service here before launch.</p>'''
    write("contact.html", page_shell("Contact", "Contact the archive.", depth, doc_page(depth, "Contact", "Contact", body), canonical_path="contact.html"))

def build_privacy():
    depth = 0
    ad_section = '''<h2>Advertising &amp; cookies</h2>
    <p>This site displays advertisements served by Google AdSense. Google and its advertising partners use
    cookies (including the DoubleClick DART cookie) and similar technologies to serve ads based on your
    prior visits to this site or other sites on the internet.</p>
    <ul>
      <li>You can opt out of personalized advertising by visiting Google's <a href="https://adssettings.google.com" target="_blank" rel="noopener noreferrer">Ads Settings</a>.</li>
      <li>You can also opt out of a third-party vendor's use of cookies for personalized advertising by visiting <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener noreferrer">aboutads.info</a>.</li>
      <li>On your first visit, a banner lets you accept or decline non-essential cookies; your choice is stored in your browser only, not on our servers.</li>
      <li>Google's use of advertising cookies enables it and its partners to serve ads based on your visits to this site and/or other sites on the internet, in line with <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener noreferrer">Google's Partner Sites policy</a>.</li>
    </ul>''' if ADSENSE_ENABLED else ""
    body = f'''<p><em>Placeholder policy &mdash; review with counsel before publishing.</em></p>
    <h2>What we collect</h2>
    <ol>
      <li>Information you voluntarily submit through the Submit a Tip form.</li>
      <li>Basic, aggregated site-usage data if analytics are added (none are included by default).</li>
      <li>Cookies set by third-party advertising and analytics providers, described below.</li>
    </ol>
    <h2>What we don't do</h2>
    <ol>
      <li>We do not sell or share submitted information with third parties.</li>
      <li>We do not publish a submitter's contact information without permission.</li>
    </ol>
    {ad_section}
    <h2>Third-party links</h2>
    <p>This site links to third-party services (including Cash App, YouTube, Google AdSense, and the source databases referenced on case pages) that have their own privacy practices.</p>'''
    write("privacy.html", page_shell("Privacy Policy", "Privacy policy for the archive.", depth, doc_page(depth, "Legal", "Privacy Policy", body), canonical_path="privacy.html"))

def build_terms():
    depth = 0
    body = '''<p><em>Placeholder terms &mdash; review with counsel before publishing.</em></p>
    <ol>
      <li><strong>Purpose.</strong> This site is a research and awareness archive of publicly reported, unsolved cases, provided for informational purposes only.</li>
      <li><strong>No legal advice or investigative service.</strong> The site does not conduct investigations and is not a law-enforcement body.</li>
      <li><strong>Accuracy.</strong> Information may be incomplete or later corrected; see each case file's sourcing status.</li>
      <li><strong>No accusations.</strong> Content should not be read as an accusation against any named or unnamed individual.</li>
      <li><strong>User submissions.</strong> By submitting via the Submit a Tip form, you confirm the information is true to the best of your knowledge.</li>
      <li><strong>External links.</strong> We are not responsible for third-party content or practices.</li>
    </ol>'''
    write("terms.html", page_shell("Terms of Use", "Terms of use for the archive.", depth, doc_page(depth, "Legal", "Terms of Use", body), canonical_path="terms.html"))

# ---------------------------------------------------------------------------
# CORRECTIONS LOG — a real, dated record of substantive factual changes made
# to case files after their initial publication. This is not a changelog of
# every edit (wording, formatting) — only corrections, additions, or status
# changes that affect what a reader would understand about a case. Newest
# first. `case_id` links the entry to that case's file when applicable.
# ---------------------------------------------------------------------------
CORRECTIONS = [
    dict(date="2026-08-22", case_id="harry-and-harriette-moore",
         text="Added a verified, public-domain photograph of Harry T. Moore, sourced directly from the "
              "State Archives of Florida (Florida Memory). No verified photograph of Harriette Moore "
              "alone has been located yet."),
    dict(date="2026-08-21", case_id="darlenia-denise-johnson",
         text="Corrected the location of her summer job, previously conflated with her home neighborhood. "
              "She lived in Congress Heights; she was on her way to work at the Oxon Hill Recreation "
              "Center, a separate location, when she was abducted."),
    dict(date="2026-08-21", case_id="brenda-faye-crockett",
         text="Added her exact disappearance date, July 27, 1971, previously recorded only as \u201cJuly "
              "1971.\u201d"),
    dict(date="2026-08-21", case_id="brenda-denise-woodard",
         text="Added her exact abduction date and circumstances \u2014 the night of November 15, 1971, "
              "after leaving night school \u2014 which were not previously on record."),
    dict(date="2026-08-21", case_id="harry-and-harriette-moore",
         text="Added that the FBI reviewed the case again in 2008 under the Emmett Till Unsolved Civil "
              "Rights Crime Act, and that the DOJ formally closed the file in 2011."),
    dict(date="2026-08-21", case_id="hattie-debardelaben",
         text="Added the names of the three federal officers present at the search, previously described "
              "only generically as \u201cthree federal officers.\u201d Also added that an undertaker "
              "reportedly found signs consistent with a broken neck, contradicting the officially recorded "
              "cause of death (heart attack)."),
    dict(date="2026-08-21", case_id="alberta-jones",
         text="Corrected case status. This file previously stated the DOJ's cold-case review "
              "\u201cremains open\u201d; the DOJ in fact formally closed the file in August 2023 without "
              "identifying a suspect. Updated the summary accordingly."),
    dict(date="2026-08-21", case_id="alonzo-brooks",
         text="Corrected status from Cold Case to Unsolved to reflect the active federal hate-crime "
              "investigation. Added the exact body-recovery date, May 1, 2004, previously recorded only "
              "as \u201cabout a month later.\u201d Added a verified FBI photograph."),
    dict(date="2026-08-21", case_id="diamond-and-tionda-bradley",
         text="Added verified FBI photographs of both sisters, and the FBI's specific published reward "
              "amount ($10,000), previously described only as \u201ca reward.\u201d"),
]

def build_updates():
    depth = 0
    case_by_id = {c["id"]: c for c in CASES}
    entries_by_date = {}
    for e in CORRECTIONS:
        entries_by_date.setdefault(e["date"], []).append(e)
    dates_sorted = sorted(entries_by_date.keys(), reverse=True)
    sections = []
    for d in dates_sorted:
        items = []
        for e in entries_by_date[d]:
            prefix = ""
            if e.get("case_id"):
                c = case_by_id[e["case_id"]]
                prefix = f'<a href="cases/{c["id"]}.html">Case #{c["caseNumber"]} \u2014 {html.escape(c["name"])}</a>: '
            items.append(f'<li>{prefix}{e["text"]}</li>')
        heading = (f'<h2 style="font-size:1.05rem; font-family:var(--mono); letter-spacing:.04em; '
                   f'border-top:1px solid var(--border); margin-top:2em; padding-top:.6em;">{d}</h2>')
        sections.append(heading + "<ul>" + "\n".join(items) + "</ul>")
    body = f'''<p>{SITE_NAME} corrects case files when new sourcing, official records, or documented errors
    come to light. This page is a dated, public record of substantive corrections and additions \u2014 not
    routine copyediting, but changes that affect what a reader would understand about a case: a corrected
    date, a status update, a name added or removed, a source verified. Nothing is corrected quietly.</p>
    <p>See <a href="research.html">How We Research</a> for our sourcing standards, or
    <a href="submit.html">Submit a Tip</a> to flag something that needs review.</p>
    {"".join(sections)}'''
    write("updates.html", page_shell("Corrections & Updates", "A dated public record of substantive corrections made to case files.", depth,
          doc_page(depth, "Accountability", "Corrections & Updates", body), canonical_path="updates.html", og_image="og/updates.png"))

def build_disclaimer():
    depth = 0
    body = f'''<p>{SITE_NAME} is an independent, publicly-sourced research and awareness archive.</p>
    <ol>
      <li>This site does not investigate cases; it organizes publicly available information.</li>
      <li>This site does not claim to possess new evidence in any case.</li>
      <li>This site does not accuse any named or unnamed individual of any crime.</li>
      <li>Case statuses reflect publicly reported information at time of writing and may change.</li>
      <li>If you have information about an active or unsolved case, contact the relevant law-enforcement agency directly.</li>
      <li>Family members may request a case file be corrected, amended, or removed via <a href="submit.html">Submit a Tip</a>; such requests are prioritized.</li>
    </ol>'''
    write("disclaimer.html", page_shell("Disclaimer", "Site-wide disclaimer.", depth, doc_page(depth, "Legal", "Disclaimer", body), canonical_path="disclaimer.html"))

def build_404():
    depth = 0
    body = f'''{top_header(depth)}
<main id="main" class="doc-shell" style="text-align:center; padding-top:100px;">
  <span class="label">Case File Not Found</span>
  <h1 style="font-size:3rem; margin:14px 0 10px;">404</h1>
  <p style="max-width:44ch; margin:0 auto 28px; color:var(--text-dim);">
    This page isn't in the archive &mdash; it may have moved, or the link may be out of date.
  </p>
  <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
    <a class="bt-btn" href="index.html" style="text-decoration:none; padding:10px 18px;">Return to Dashboard</a>
    <a class="bt-btn" href="cases/index.html" style="text-decoration:none; padding:10px 18px;">Browse Case Index</a>
  </div>
</main>
{footer_html(depth)}'''
    # Not added to the sitemap (write() already skips 404.html by name) since
    # it isn't a real content page — Vercel serves this automatically for
    # any unmatched route on a static deployment.
    write("404.html", page_shell("Page Not Found", "This page could not be found.", depth, body, canonical_path="404.html"))

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    write("data/cases.json", json.dumps(CASES, indent=2))
    # Shared, browser-cacheable copy for the actual UI to read (see the
    # comment above CASES_JSON) — loaded via <script src> rather than
    # duplicated inline on every page, and via <script src> rather than
    # fetch() so it also works when the site is opened straight from disk.
    write("js/cases-data.js", "window.__UBCA_CASES__ = " + CASES_JSON + ";")
    if ADSENSE_ENABLED:
        # AdSense requires ads.txt at the site root once you have a real
        # Publisher ID (Settings -> Account information in AdSense), in the
        # format: google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
        # The line below is a placeholder — Google will flag it as invalid
        # until you swap in your real ID (same one used in ADSENSE_CLIENT_ID
        # above, just without the "ca-" prefix).
        pub_id = ADSENSE_CLIENT_ID.replace("ca-", "")
        write("ads.txt",
              f"# Replace {pub_id} with your real AdSense Publisher ID before deploying.\n"
              f"google.com, {pub_id}, DIRECT, f08c47fec0942fa0\n")
    build_home()
    build_about()
    build_research()
    build_resources()
    build_submit()
    build_support()
    build_contact()
    build_privacy()
    build_terms()
    build_disclaimer()
    build_updates()
    build_case_index()
    build_freeway_phantom()
    for c in CASES:
        build_case_page(c)
    build_404()

    # robots.txt + sitemap.xml — generated last so SITEMAP_PATHS has every
    # page write() has recorded above.
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    today = datetime.date.today().isoformat()
    urls = "\n".join(
        f'  <url><loc>{SITE_URL}/{p if p != "index.html" else ""}</loc><lastmod>{today}</lastmod></url>'
        for p in SITEMAP_PATHS
    )
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f'{urls}\n'
          '</urlset>\n')

    print("\nDone. Pages written to", OUT)
