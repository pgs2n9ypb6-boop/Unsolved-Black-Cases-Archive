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
SITE_URL = "https://unsolved-black-cases-archive-jet.vercel.app"
SHORT_NAME = "UBCA"
TAGLINE = "A public-record research archive documenting unsolved cases involving Black victims."
ARCHIVE_NOTE = ("This archive summarizes publicly available information and does not conduct "
                 "independent criminal investigations.")

NAV_DOCS = [
    ("About", "about.html"),
    ("My Saved Cases", "saved.html"),
    ("Archive Statistics", "statistics.html"),
    ("Cold Case Quiz", "quiz.html"),
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
    dict(id="wharlest-jackson-sr", caseNumber="014", name="Wharlest Jackson Sr.",
         status="unsolved", caseType="homicide", year=1967, age=36, gender="male",
         city="Natchez", county="Adams", state="MS", caseSeries="Silver Dollar Group",
         summary="Wharlest Jackson Sr., 36, a Korean War veteran, father of five, and treasurer of the "
                 "Natchez NAACP, was killed on February 27, 1967 when a bomb planted under his truck "
                 "exploded, reportedly triggered by his turn signal, as he drove home from his first shift "
                 "in a new position at the Armstrong Tire and Rubber plant \u2014 a role that had previously "
                 "been held only by white employees. Two years earlier, NAACP president George Metcalfe had "
                 "survived a similar car bombing at the same plant. The FBI's main suspect was Raleigh "
                 "\"Red\" Glover, leader of a Klan offshoot known as the Silver Dollar Group; Glover was "
                 "never charged and died in 1984. The DOJ's Civil Rights Division has since closed its "
                 "investigation without prosecution.",
         known=["Victim identity, role, and the February 27, 1967 date and circumstances, per the DOJ's public case file.",
                "The FBI's identification of Raleigh \"Red\" Glover as its main suspect, per public reporting on the released FBI files; Glover was never charged."],
         unknown=["No one was ever charged or convicted in the bombing.",
                  "The exact type of explosive material used was never identified."],
         unanswered=["What do the released FBI files say about why Glover was never charged despite being the lead suspect?",
                     "What connection, if any, does this case have to the 1965 bombing of George Metcalfe?",
                     "What became of the broader Silver Dollar Group investigation?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/wharlest-jackson", True),
                        src("PBS FRONTLINE, \u201cAmerican Reckoning\u201d \u2014 documentary",
                            "https://www.pbs.org/wgbh/frontline/documentary/american-reckoning/", True)]),
    dict(id="frank-morris", caseNumber="015", name="Frank Morris",
         status="unsolved", caseType="homicide", year=1964, age=51, gender="male",
         city="Ferriday", county="Concordia", state="LA", caseSeries="Silver Dollar Group",
         summary="Frank Morris, 51, the Black owner of a shoe repair shop in Ferriday that served both "
                 "Black and white customers, was killed after two unidentified white men set fire to his "
                 "shop in the early hours of December 10, 1964 while he slept in a back room. One of the "
                 "men held Morris at gunpoint and forced him back inside as the fire spread. Morris escaped "
                 "but suffered burns over 100% of his body and died four days later. He told the FBI his "
                 "attackers were \"two white friends,\" accompanied by a third man he did not see, but he "
                 "was never able to identify them by name. The DOJ's file states that FBI informants in "
                 "1967 identified the attack as the work of the Silver Dollar Group, a secretive Klan cell "
                 "formed in the Natchez\u2013Ferriday area around 1964, and named four of its members \u2014 "
                 "E.D. Morace, Tommie Lee Jones, Thor Lee Torgersen, and James Lee Scarborough \u2014 as "
                 "responsible; all four denied involvement when interviewed, and the FBI found no "
                 "independent evidence to corroborate the informants' accounts. No one was ever charged, "
                 "and the DOJ closed the case without reaching a conclusion.",
         known=["Victim identity, age, and the December 10\u201314, 1964 timeline, per the DOJ's public case file.",
                "The DOJ's file names four Silver Dollar Group members identified by FBI informants; all four denied involvement, and the FBI could not independently corroborate the informants' accounts."],
         unknown=["No one was ever charged in the arson.",
                  "The DOJ's file states it found no independent basis to confirm the informants' identification of the four named men."],
         unanswered=["What became of the two men a friend of Morris's said he believed had been \"taken care of\" by fellow Klansmen shortly after the killing?",
                     "What additional informant reporting, if any, remains undisclosed in the FBI's files?",
                     "What role, if any, did local law enforcement play, as alleged by some witnesses?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/frank-morris-notice-close-file", True),
                        src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/frank-morris/", True)]),
    dict(id="george-lee", caseNumber="016", name="Rev. George Lee",
         status="unsolved", caseType="homicide", year=1955, age=51, gender="male",
         city="Belzoni", county="Humphreys", state="MS", caseSeries=None,
         summary="Rev. George W. Lee, 51, a Baptist minister, grocer, and co-founder of the Belzoni NAACP "
                 "branch, was shot and killed while driving in Belzoni on the night of May 7, 1955. Lee was "
                 "the first Black resident to register to vote in Humphreys County since Reconstruction, "
                 "and had helped register roughly 90 other Black voters despite repeated threats. His car "
                 "crashed after gunmen in a passing car fired into it; he died shortly after reaching a "
                 "hospital. The local sheriff publicly claimed the lead pellets found in Lee's jaw were "
                 "dental fillings; FBI testing later confirmed they were buckshot. No one was ever "
                 "prosecuted. FBI files released in 2000 named two White Citizens' Council members, Peck "
                 "Ray and Joe David Watson Sr., as suspects; both had died in the 1970s.",
         known=["Victim identity, role, and the May 7, 1955 date and circumstances, per the DOJ's public case file.",
                "FBI files released in 2000 named two suspects, both reported deceased, per public reporting on those files."],
         unknown=["No one was ever charged or convicted.",
                  "The local district attorney's specific reasons for declining to prosecute were not fully documented publicly."],
         unanswered=["What do the released 2000 FBI files say about the evidence against the two named suspects?",
                     "Why did the local prosecutor decline to pursue the case despite an FBI investigation?",
                     "What connection, if any, exists between this case and the broader White Citizens' Council activity in Humphreys County at the time?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/george-lee", True),
                        src("Southern Poverty Law Center \u2014 case summary",
                            "https://www.splcenter.org/rev-george-lee", True)]),
    dict(id="johnnie-mae-chappell", caseNumber="017", name="Johnnie Mae Chappell",
         status="unsolved", caseType="homicide", year=1964, age=35, gender="female",
         city="Jacksonville", county="Duval", state="FL", caseSeries=None,
         summary="Johnnie Mae Chappell, 35, a domestic worker and mother of ten, was shot and killed on "
                 "the night of March 23, 1964 while retracing her steps along New Kings Road in "
                 "Jacksonville's Pickettville neighborhood, searching with two neighbors for a wallet she "
                 "had dropped, during a night of racial unrest in the city. A car carrying four white men "
                 "drove past; one of them, J.W. Rich, fired a .22-caliber pistol, fatally wounding her. The "
                 "case went unsolved for five months until one of the men, Wayne Chessman, approached "
                 "detectives and confessed, naming Rich as the shooter along with Elmer Kato and James Alex "
                 "Davis. All four were indicted for first-degree murder, but only Rich stood trial; an "
                 "all-white jury convicted him of the lesser charge of manslaughter, and he served about "
                 "three years. The murder weapon went missing before trial. The three other men were never "
                 "tried; Florida later granted them immunity. The DOJ's Civil Rights Division formally "
                 "closed its file on August 18, 2014, citing insufficient federal evidence and the state's "
                 "grant of immunity to the surviving subjects.",
         known=["Victim identity, age, and the March 23, 1964 date and circumstances, per the DOJ's public case file and its 2014 Notice to Close File.",
                "J.W. Rich's manslaughter conviction, and the identities of the three other men indicted but never tried, per the same records and public reporting."],
         unknown=["What became of the murder weapon, which went missing before trial.",
                  "The full circumstances under which Florida granted immunity to the three uncharged men."],
         unanswered=["What specific evidence did the 2014 DOJ review weigh before closing the federal file?",
                     "What happened to the detectives, Lee Cody and Donald Coleman Sr., who said they were pushed off the case and later lost their jobs?",
                     "What additional documentation exists in the state's earlier reviews under Governor Jeb Bush?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/johnnie-m-chappell-notice-close-file", True),
                        src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/johnnie-mae-chappell/", True)]),
    dict(id="louis-allen", caseNumber="018", name="Louis Allen",
         status="unsolved", caseType="homicide", year=1964, age=44, gender="male",
         city="Liberty", county="Amite", state="MS", caseSeries=None,
         summary="Louis Allen, 44, a WWII veteran, logger, and landowner, was shot to death with a shotgun "
                 "at his own gate in Liberty on January 31, 1964, the night before he was set to leave "
                 "Mississippi for good. Allen had witnessed the 1961 murder of NAACP voter-registration "
                 "activist Herbert Lee by state legislator E.H. Hurst, and after initially being coerced "
                 "into corroborating a self-defense account, later told the FBI that Hurst had shot Lee in "
                 "cold blood. Word spread that Allen had cooperated with federal investigators, and he was "
                 "harassed and repeatedly jailed on false charges over the following two years by Amite "
                 "County Sheriff Daniel Jones, who once broke Allen's jaw with a flashlight. The DOJ's "
                 "Civil Rights Division formally closed its file on the case in 2015, naming Jones \u2014 by "
                 "then deceased \u2014 as its subject.",
         known=["Victim identity, background, and the January 31, 1964 date and circumstances, per the DOJ's public case file.",
                "The DOJ's 2015 Notice to Close File names Sheriff Daniel Jones, reported deceased, as its subject."],
         unknown=["No one was ever charged in Allen's killing.",
                  "The exact circumstances of the ambush, including how many people were involved, were never conclusively established."],
         unanswered=["What evidence did the DOJ's file compile against Sheriff Jones specifically before closing the case?",
                     "What became of the federal grand jury testimony Allen gave regarding his harassment?",
                     "What became of the other witnesses, beyond Allen, who corroborated Hurst's self-defense account at Herbert Lee's 1961 inquest \u2014 documented separately in this archive \u2014 before Allen recanted his own testimony to the FBI?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/louis-allen", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/daniel-jones-louis-allen-deceased-notice-close-file", True)]),
    dict(id="oneal-moore", caseNumber="019", name="Oneal Moore",
         status="unsolved", caseType="homicide", year=1965, age=34, gender="male",
         city="Varnado", county="Washington", state="LA", caseSeries=None,
         summary="Oneal Moore, 34, an Army veteran and one of the first two Black deputy sheriffs in "
                 "Washington Parish, was shot and killed while on patrol near Varnado on the night of June "
                 "2, 1965 \u2014 one year and a day after he and partner David \"Creed\" Rogers, also Black, "
                 "were sworn in. A pickup truck with a Confederate flag decal pulled alongside their patrol "
                 "car and its occupants opened fire; Moore was killed instantly and Rogers was blinded in "
                 "one eye but survived and radioed a description of the truck. About an hour later, a "
                 "matching truck was stopped in Tylertown, Mississippi and its driver, known Klansman "
                 "Ernest Rayford \"Ray\" McElveen, was arrested and charged with murder, but released after "
                 "nine days on bond raised by fellow Klan members; the charge was ultimately dropped for "
                 "lack of evidence. McElveen died in 2003. The case remains unsolved.",
         known=["Victim identity, role, and the June 2, 1965 date and circumstances, per the DOJ's public case file.",
                "Ernest Rayford McElveen's arrest and release, per the same file and public reporting; McElveen died in 2003."],
         unknown=["No one was ever convicted in Moore's killing.",
                  "The identities of any other occupants of the truck beyond McElveen were not publicly confirmed."],
         unanswered=["Why was the murder charge against McElveen ultimately dropped?",
                     "What did the FBI's repeated reviews (1990, 2001, 2009) each establish or fail to establish?",
                     "What became of the firearms and rope found in McElveen's truck at the time of his arrest?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/oneal-moore", True),
                        src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/oneal-moore", True)]),
    dict(id="clifton-walker", caseNumber="020", name="Clifton Walker",
         status="unsolved", caseType="homicide", year=1964, age=37, gender="male",
         city="Woodville", county="Wilkinson", state="MS", caseSeries=None,
         summary="Clifton Walker, 37, a World War II veteran and father of five, was shot to death in his "
                 "car on Poor House Road outside Woodville late on the night of February 28, 1964, while "
                 "driving home from his late shift at the International Paper Company plant in Natchez. His "
                 "car was ambushed and riddled with close-range shotgun blasts; he was found dead in the "
                 "vehicle the next afternoon. The killing is believed to be among the first carried out by "
                 "the newly formed White Knights of the Ku Klux Klan, which was responsible for several "
                 "other Mississippi civil-rights-era murders. Mississippi Highway Patrol investigators "
                 "recommended two suspects for arrest in 1964, but the local district attorney declined to "
                 "prosecute, citing insufficient evidence. The DOJ's Civil Rights Division formally closed "
                 "its file in 2013, naming three men \u2014 Prentiss Mathis, Carl Cavin, and Red Metcalf, "
                 "all reported deceased \u2014 as subjects.",
         known=["Victim identity, background, and the February 28\u201329, 1964 date and circumstances, per the DOJ's public case file.",
                "The DOJ's 2013 Notice to Close File names three subjects, all reported deceased."],
         unknown=["No one was ever charged in Walker's killing.",
                  "The relationship, if any, between the two suspects Mississippi Highway Patrol recommended in 1964 and the three subjects later named in the DOJ's 2013 closure has not been publicly reconciled."],
         unanswered=["Why did the local district attorney decline to prosecute despite the Highway Patrol's 1964 recommendation?",
                     "What evidence connected each of the three subjects named in the 2013 DOJ file to the killing?",
                     "What became of the .38 revolver found in Walker's car, and what did it indicate about the circumstances of the attack?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/clifford-clifton-walker", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/clifford-clifton-walker", True)]),
    dict(id="willie-edwards-jr", caseNumber="021", name="Willie Edwards Jr.",
         status="unsolved", caseType="homicide", year=1957, age=24, gender="male",
         city="Montgomery", county="Montgomery", state="AL", caseSeries=None,
         summary="Willie Edwards Jr., 24, a Winn-Dixie truck driver and father of two, disappeared on the "
                 "evening of January 22, 1957 after being called back to work to cover another driver's "
                 "shift in Montgomery. Klansmen, who mistook him for a different Black man they believed "
                 "was involved with a white woman, pulled him from his truck at gunpoint and forced him, "
                 "under threat of being shot, to jump from the Tyler-Goodwyn Bridge into the Alabama River. "
                 "Fishermen found his body three months later; the medical examiner could not determine a "
                 "cause of death due to decomposition. The case sat dormant until 1976, when a witness "
                 "named three men \u2014 Henry Alexander, Jimmy York, and Raymond Britt \u2014 as having "
                 "forced Edwards to jump; two received immunity for their testimony, but repeated attempts "
                 "at indictment failed. In 1997, at the family's request, Edwards's body was exhumed and "
                 "his cause of death was reclassified as homicide by drowning; a 1999 grand jury agreed he "
                 "was killed by Klan members but still declined to indict, citing insufficient evidence "
                 "tied to problems in the 1970s investigation. The DOJ closed its file in 2013; all three "
                 "named men were by then deceased.",
         known=["Victim identity, employer, and the January 22, 1957 date and circumstances, per the DOJ's public case file.",
                "The 1976 witness account naming Henry Alexander, Jimmy York, and Raymond Britt, and the 1997 reclassification of the cause of death as homicide, per the same file and public reporting."],
         unknown=["No one was ever indicted or convicted.",
                  "The identity of the man the Klansmen were actually looking for, whom Edwards was mistaken for, was never publicly confirmed."],
         unanswered=["What specific evidence problems from the 1970s investigation caused the 1999 grand jury to decline to indict?",
                     "What did Henry Alexander's 1993 confession add to the record?",
                     "Why did Alabama officials decline to authorize a third prosecution attempt against the one still-living suspect before the DOJ's 2013 closure?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/willie-edwards-jr", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/willie-edwards-jr-notice-close-file", True)]),
    dict(id="isadore-banks", caseNumber="022", name="Isadore Banks",
         status="unsolved", caseType="homicide", year=1954, age=58, gender="male",
         city="Marion", county="Crittenden", state="AR", caseSeries=None,
         summary="Isadore Banks, 58, a World War I veteran and one of the wealthiest Black landowners in "
                 "the Arkansas Delta, left home on June 4, 1954 to pay his farmhands and never returned. "
                 "Four days later, his truck was found abandoned nearby with his shotgun and coat still "
                 "inside; his body was discovered chained to a tree in a wooded area, burned beyond "
                 "recognition, with a wound the coroner attributed to a knife or gunshot. There was no sign "
                 "of robbery or struggle at the scene, and the coroner believed Banks \u2014 who weighed "
                 "nearly 300 pounds \u2014 had been killed elsewhere and his body moved, likely by more than "
                 "one person. A Black-owned cooperative offered a $1,000 reward; no one came forward. "
                 "Unlike most cases on this archive, no suspect was ever named by investigators at any "
                 "point \u2014 local law enforcement conducted little investigation, and the FBI at the "
                 "time initially declined to open a file, stating it saw no clear federal jurisdiction.",
         known=["Victim identity, background, and the June 4\u20138, 1954 timeline, per the DOJ's public case file.",
                "No suspect has ever been named in connection with the killing, per the same file and public reporting."],
         unknown=["The motive for the killing was never established; several theories circulated locally but none were substantiated.",
                  "What became of Banks's more than 1,000 acres of land after his death was not fully documented."],
         unanswered=["What, if anything, do surviving FBI records \u2014 some reportedly destroyed by 1992 \u2014 still contain?",
                     "Why did local authorities conduct so little investigation despite the case's extensive contemporary press coverage?",
                     "What did the DOJ's Cold Case Initiative review conclude when it reexamined the file?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/isadore-banks", True),
                        src("Encyclopedia of Arkansas \u2014 case summary",
                            "https://encyclopediaofarkansas.net/entries/isadore-banks-6425/", True)]),
    dict(id="mack-charles-parker", caseNumber="023", name="Mack Charles Parker",
         status="unsolved", caseType="homicide", year=1959, age=23, gender="male",
         city="Poplarville", county="Pearl River", state="MS", caseSeries=None,
         summary="Mack Charles Parker, 23, an Army veteran and truck driver, was lynched three days before "
                 "he was scheduled to stand trial on charges of raping a white woman \u2014 charges he "
                 "denied in a letter written from jail, and which rested on an identification the accuser "
                 "herself said she could not be certain of. Late on April 24, 1959, eight to ten hooded men "
                 "broke into the Pearl River County jail in Poplarville, reportedly aided by a jailer who "
                 "provided the keys, and dragged Parker from his cell. He was beaten, driven away, and "
                 "shot; his body was recovered from the Pearl River on May 4, 1959. An FBI investigation "
                 "identified more than twenty men involved, several of whom confessed and named other "
                 "participants, and the FBI turned a full dossier over to Mississippi officials. An "
                 "all-white county grand jury declined to indict, as did a subsequent federal grand jury, "
                 "by a single vote. No one was ever charged. Historian Howard Smead has called it \"the "
                 "last classic lynching in America.\"",
         known=["Victim identity, background, and the April 24\u201325, 1959 date and circumstances, per contemporaneous FBI reporting and public records.",
                "The FBI's investigation identified more than twenty participants through witness statements and confessions, though no state or federal grand jury returned an indictment."],
         unknown=["No one was ever charged, tried, or convicted.",
                  "Parker's guilt in the underlying rape accusation was never established in court; his accuser could not confirm his identity with certainty."],
         unanswered=["What specific evidence did the FBI's dossier, handed to Mississippi officials in 1959, contain?",
                     "Why did the federal grand jury in Biloxi fall one vote short of indicting?",
                     "What has the DOJ's ongoing review under the Emmett Till Act, reopened in 2009, established since?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/mack-charles-parker/", True),
                        src("Mississippi Today \u2014 case retrospective",
                            "https://mississippitoday.org/2025/04/25/1959-mack-charles-parker-lynched-poplarville/", True)]),
    dict(id="joseph-edwards", caseNumber="024", name="Joseph Edwards",
         status="unsolved", caseType="missing_persons", year=1964, age=None, gender="male",
         city="Vidalia", county="Concordia", state="LA", caseSeries="Silver Dollar Group",
         summary="Joseph \"Joe-Ed\" Edwards, a porter at the Shamrock Motel in Vidalia in his early 20s, "
                 "disappeared in the early morning hours of July 12, 1964. His car was found abandoned near "
                 "a local bowling alley days later with a necktie tied into a noose on the steering wheel "
                 "and blood inside. The FBI later concluded Edwards had likely been targeted after he was "
                 "seen kissing a white coworker; the woman's boyfriend reported the incident to the Vidalia "
                 "police chief, who is believed to have alerted a Klan offshoot called the Silver Dollar "
                 "Group. A witness told the FBI he saw a car matching the group's leader's description "
                 "stop Edwards's Buick near the bowling alley on the night he vanished. His body has never "
                 "been found \u2014 the only Civil Rights-era case in Louisiana the FBI investigated in "
                 "which this remains true. The DOJ's Civil Rights Division closed its file in 2013, naming "
                 "seven subjects, including several Concordia Parish sheriff's deputies and the Silver "
                 "Dollar Group's leader, all reported deceased.",
         known=["Victim's identity, employer, and the July 12, 1964 disappearance date, per the DOJ's public case file.",
                "The DOJ's 2013 Notice to Close File names seven subjects, all reported deceased, including law enforcement officers."],
         unknown=["Edwards's body has never been recovered, and his exact cause of death is unknown.",
                  "No one was ever charged in connection with his disappearance."],
         unanswered=["What did the FBI's search of Deer Park Lake and other locations for Edwards's remains ultimately establish?",
                     "What role did each of the seven named subjects play, according to the DOJ's file?",
                     "What became of the white Oldsmobile the FBI investigation connected to a witness account of the night Edwards disappeared?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/joseph-joed-edwards", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/joseph-joed-edwards-notice-close-file", True)]),
    dict(id="samuel-oquinn", caseNumber="025", name="Samuel O'Quinn",
         status="unsolved", caseType="homicide", year=1959, age=58, gender="male",
         city="Centreville", county="Wilkinson", state="MS", caseSeries=None,
         summary="Samuel O'Quinn, 58, a businessman who ran a funeral home, a cafe, and farmland in "
                 "Centreville, was shot twice in the back with a shotgun on the night of August 14, 1959 "
                 "as he opened the gates to his property; he died on the way to the hospital. No witnesses "
                 "were identified, and neither state police nor the FBI's investigation at the time named a "
                 "suspect. Local media reported at the time that O'Quinn was active with the NAACP and "
                 "speculated his death was politically motivated; a white glove found at the scene was "
                 "later thought by family to be a White Citizens' Council calling card. A 2012 DOJ memo "
                 "reviewing the case reached a different conclusion, stating that the limited surviving "
                 "investigative material \"indicates that O'Quinn may have been murdered by a person or "
                 "persons interested in obtaining his land\" rather than for political activity \u2014 a "
                 "reminder that even the motive behind a killing can remain genuinely disputed decades "
                 "later. The DOJ closed its file in 2012 without identifying a suspect.",
         known=["Victim identity, background, and the August 14, 1959 date and circumstances, per the DOJ's public case file.",
                "No suspect was ever identified by state or federal investigators, per the same file."],
         unknown=["The motive remains genuinely disputed: contemporary reporting pointed to O'Quinn's NAACP activity, while the DOJ's 2012 review pointed to a land dispute instead.",
                  "A secondhand deathbed confession the family later learned of, alleging the killer was paid $500 and a car, was never independently verified."],
         unanswered=["What specific evidence led the DOJ's 2012 review to favor a land-dispute motive over the politically-motivated account?",
                     "What became of the white glove found at the scene?",
                     "What, if anything, came of the two interviewees who shared secondhand information about a possible suspect during the FBI's 2008 review?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/samuel-o-quinn-notice-close-file", True),
                        src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/samuel-oquinn", True)]),
    dict(id="claude-neal", caseNumber="026", name="Claude Neal",
         status="unsolved", caseType="homicide", year=1934, age=23, gender="male",
         city="Greenwood", county="Jackson", state="FL", caseSeries=None,
         summary="Claude Neal, 23, a farmhand, was lynched near Marianna on the night of October 25\u201326, "
                 "1934, days after being arrested and accused of the murder of a young white woman. Fearing "
                 "mob violence, Sheriff Flake Chambliss moved Neal between several jails, eventually "
                 "hiding him roughly 200 miles away in Brewton, Alabama. In the early morning hours of "
                 "October 26, a mob broke into the Brewton jail and abducted him, driving him back to "
                 "Jackson County on back roads to avoid law enforcement. Neal was killed hours later; his "
                 "body was then displayed publicly, hanged from a tree at the Jackson County courthouse in "
                 "Marianna. When the sheriff cut the body down the next morning and refused demands to "
                 "rehang it, a mob numbering in the thousands rioted through Marianna for days, attacking "
                 "Black residents and property; the governor deployed the National Guard to restore order. "
                 "The lynching had been publicized in advance and drew national attention, becoming a "
                 "catalyst for the NAACP's campaign for federal anti-lynching legislation. No one was ever "
                 "charged; the DOJ reopened the case for review in 2011 under the Emmett Till Unsolved "
                 "Civil Rights Crime Act, by which point all identified participants were deceased.",
         known=["Victim identity, background, and the October 1934 timeline, per the DOJ's public case file.",
                "The lynching was extensively documented by contemporary press and NAACP investigators, and is widely credited with advancing the national anti-lynching legislative campaign of the 1930s."],
         unknown=["No one was ever charged, tried, or convicted.",
                  "The full circumstances of Neal's initial confession, obtained without legal counsel present, were never independently tested in court."],
         unanswered=["What did the FBI's 2011 review, opened under the Emmett Till Act, establish or conclude?",
                     "What became of the NAACP's contemporaneous investigative file compiled by Walter White?",
                     "What formal accounting, if any, has Jackson County given of the riot's estimated 200 injuries and property destruction?"],
         extraSources=[src("U.S. Department of Justice \u2014 Civil Rights Division case page",
                            "https://www.justice.gov/crt/case/claude-neal", True),
                        src("Explore Southern History \u2014 case summary",
                            "https://www.exploresouthernhistory.com/claudeneal.html", True)]),
    dict(id="brandon-mcclelland", caseNumber="027", name="Brandon McClelland",
         status="unsolved", caseType="homicide", year=2008, age=24, gender="male",
         city="Paris", county="Lamar", state="TX", caseSeries=None,
         summary="Brandon McClelland, 24, was struck and dragged roughly 70 feet beneath a pickup truck on "
                 "a rural road outside Paris in the early hours of September 16, 2008; his body was found "
                 "the next morning. He had been on a late-night beer run across the Oklahoma state line "
                 "with two white acquaintances, Shannon Finley and Charles Ryan Crostley, and an argument "
                 "reportedly broke out on the drive back over whether Finley was too drunk to keep driving; "
                 "McClelland got out of the vehicle to walk. A grand jury indicted both Finley and Crostley "
                 "on murder charges, and Finley was separately indicted for evidence tampering, accused of "
                 "washing blood from the truck's undercarriage. The case unraveled over the following year "
                 "amid a lack of eyewitnesses and forensic evidence \u2014 no DNA tying McClelland to the "
                 "truck was ever found \u2014 and a separate driver came forward with a sworn statement "
                 "acknowledging he might have accidentally struck McClelland himself. Prosecutors moved to "
                 "dismiss the murder charges in 2009, and both men were released. McClelland's family and "
                 "local civil rights advocates have maintained the killing was a racially motivated hate "
                 "crime, drawing comparisons to the 1998 dragging death of James Byrd Jr. in nearby Jasper, "
                 "Texas; no one has ever been convicted.",
         known=["Victim identity and the September 16, 2008 date and circumstances, per contemporaneous news reporting and court records.",
                "Shannon Finley and Charles Ryan Crostley were indicted by a grand jury on murder charges, which were later formally dismissed before trial; per the same records, no one has been convicted."],
         unknown=["Whether McClelland's death was an intentional act or the accidental result of impaired driving was never resolved in court.",
                  "The credibility and outcome of the competing sworn statement from a gravel truck driver who said he may have struck McClelland was never fully adjudicated."],
         unanswered=["What specific forensic findings led prosecutors to conclude the case could not proceed to trial?",
                     "Did the Department of Justice ever formally open or close a federal civil rights review of the case, as local activists requested?",
                     "What, if anything, has come of the case since the 2009 dismissal?"],
         extraSources=[src("Wikipedia \u2014 \u201cDeath of Brandon McClelland\u201d, background reference",
                            "https://en.wikipedia.org/wiki/Death_of_Brandon_McClelland", True),
                        src("CBS News \u2014 case report on the dismissal of charges",
                            "https://www.cbsnews.com/news/charges-dropped-in-texas-dragging-death", True)]),
    dict(id="john-allen", caseNumber="028", name="John Allen",
         status="unsolved", caseType="homicide", year=1864, age=None, gender="male",
         city="Des Moines", county="Polk", state="IA", caseSeries=None,
         summary="John Allen, an employee of the Demoine House hotel described by contemporary newspapers "
                 "as \u201cpeaceable,\u201d was shot in the head and killed instantly on a Des Moines "
                 "sidewalk in front of Ensign's Livery Stable on July 8, 1864. Private John McRoberts, a "
                 "26-year-old Union soldier on furlough from the 10th Iowa Volunteer Infantry, had been "
                 "drunk and looking for a fight; witnesses in broad daylight saw him hail Allen, who "
                 "stopped, then moved on \u2014 at which point McRoberts drew his pistol and shot him "
                 "without provocation. McRoberts was arrested and indicted by a grand jury for murder, but "
                 "according to an 1898 county history, he \u201cwas never placed on trial\u201d and was "
                 "instead quietly released and sent back to his regiment, which shipped out for Georgia "
                 "less than a month later. McRoberts survived the Civil War, married, and lived the rest of "
                 "his life free, dying in Idaho in 1908.",
         known=["Victim identity, occupation, and the July 8, 1864 date and circumstances, per contemporary newspaper accounts and an 1898 county history.",
                "The identity of the shooter, John McRoberts, who was arrested and indicted but never tried, per the same sources."],
         unknown=["Little else is known about John Allen's life, including his birth year or burial place.",
                  "The exact circumstances of McRoberts's release from custody were not fully documented in surviving records."],
         unanswered=["What became of the grand jury indictment against McRoberts after his release?",
                     "Why were military authorities able to take custody of a man indicted for murder by a civilian grand jury?",
                     "What further records, if any, survive in Polk County court archives from 1864?"],
         extraSources=[src("Iowa Unsolved Murders: Historic Cases \u2014 case summary by Nancy Bowers",
                            "https://iowaunsolvedmurders.com/the-murders/the-peaceable-negro-murder-of-john-allen-1864/", True)]),
    dict(id="nicholas-a-brown", caseNumber="029", name="Nicholas A. Brown",
         status="unsolved", caseType="homicide", year=2021, age=33, gender="male",
         city="Davenport", county="Scott", state="IA", caseSeries=None,
         summary="Nicholas A. Brown, 33, was shot on January 30, 2021 after Davenport police responded to a "
                 "report of a domestic disturbance in the 600 block of Fillmore Street. Officers found "
                 "Brown with life-threatening gunshot wounds; he was taken to a hospital, where he later "
                 "died of his injuries. The Iowa Attorney General's office, which tracks intimate-partner "
                 "homicides statewide, listed Brown among the men killed in such circumstances and noted "
                 "that no arrests had been made in the case. He was survived by eight children.",
         known=["Victim identity and the January 30, 2021 date and circumstances, per contemporaneous news reporting.",
                "The Iowa Attorney General's office's official tracking confirms no arrests had been made in the case as of its report."],
         unknown=["No suspect has been publicly identified.",
                  "The specific nature of the domestic disturbance that preceded the shooting was not detailed in available public reporting."],
         unanswered=["What has the Davenport Police Department's investigation established since 2021?",
                     "Has any suspect been identified or charged in the years since the shooting?",
                     "What connection, if any, did the domestic disturbance have to Brown's own household versus a neighboring one?"],
         extraSources=[src("Iowa Attorney General's Office \u2014 Iowa Men Killed by Their Intimate Partners report",
                            "https://www.iowaattorneygeneral.gov/media/cms/DV_Homicide_List_93018_014CDC2E8DA89.pdf", True),
                        src("Quad-City Times \u2014 case report",
                            "https://qctimes.com/news/local/crime-and-courts/man-shot-during-davenport-domestic-disturbance-has-died-of-injuries/article_0c7f628b-0436-5a59-82f0-82ac71687bfe.html", True)]),
    dict(id="isaiah-nixon", caseNumber="030", name="Isaiah Nixon",
         status="unsolved", caseType="homicide", year=1948, age=28, gender="male",
         city="Alston", county="Montgomery", state="GA", caseSeries=None,
         summary="Isaiah Nixon, 28, a farmer, turpentine worker, and WWII veteran, was shot three times in "
                 "his own front yard in Alston on the evening of September 8, 1948, in front of his wife "
                 "and six children, hours after voting in the Georgia Democratic primary; he died two days "
                 "later in a hospital in neighboring Laurens County. Two white brothers, Jim A. Johnson and "
                 "Johnnie Johnson, drove to the Nixon home and ordered him to come with them; when he "
                 "refused, Jim Johnson shot him. A local grand jury charged Jim Johnson with murder and "
                 "Johnnie Johnson as an accessory, and the case drew national NAACP attention, but an "
                 "all-white jury acquitted Jim Johnson, and prosecutors then dropped the case against his "
                 "brother. The Nixon family fled to Florida after the killing, and their father's grave in "
                 "a remote cemetery went unmarked and lost to underbrush for 67 years, until Emory "
                 "University researchers located it in 2015 with the help of Nixon's daughter, Dorothy "
                 "Nixon Williams, who was six years old when she witnessed her father's death.",
         known=["Victim identity and the September 8, 1948 date and circumstances, per the Georgia Civil Rights Cold Cases Project at Emory University and the federal Civil Rights Cold Case Records Review Board.",
                "Jim A. Johnson was tried for murder and acquitted by an all-white jury; the accessory charge against Johnnie Johnson was subsequently dropped."],
         unknown=["No one was ever held criminally responsible for the killing.",
                  "The full contents of the FBI's contemporaneous investigation into the case were not made public."],
         unanswered=["What specific evidence and testimony led the all-white jury to acquit Jim Johnson?",
                     "What became of the FBI's 1948 investigative file on the case?",
                     "What connection, if any, does this case have to Maceo Snipes's killing two years earlier in nearby Taylor County, documented separately in this archive \u2014 both men killed for voting-related activity, both cases ending in acquittal, both driving their families out of the region?"],
         extraSources=[src("Georgia Civil Rights Cold Cases Project, Emory University \u2014 case summary",
                            "https://coldcases.emory.edu/isaiah-nixon/", True),
                        src("Civil Rights Cold Case Records Review Board \u2014 official case file",
                            "https://www.coldcaserecords.gov/content/cases/1948-09-08-isaiah-nixon-and-dover-carter/", True)]),
    dict(id="orangeburg-massacre", caseNumber="031", name="Samuel Hammond, Henry Smith & Delano Middleton",
         status="unsolved", caseType="homicide", year=1968, age=None, gender="male",
         city="Orangeburg", county="Orangeburg", state="SC", caseSeries=None,
         summary="Samuel Hammond Jr., 18, Henry Smith, 18, and Delano Middleton, 17, were shot and killed "
                 "by South Carolina Highway Patrol officers on the campus of South Carolina State College "
                 "on the night of February 8, 1968, during the third night of student protests against the "
                 "segregation of a local bowling alley. Officers fired shotguns loaded with buckshot into a "
                 "crowd of roughly 200 unarmed students; 27 more were wounded, many shot in the back or "
                 "through the soles of their feet as they fled. Middleton was a local high school student "
                 "who had come to the campus to walk his mother, a cafeteria worker, home from work. Nine "
                 "officers were identified and tried on federal charges of using excessive force; all nine "
                 "were acquitted. The only person convicted in connection with the events of that week was "
                 "Cleveland Sellers, a civil rights organizer and one of the wounded, who was convicted of "
                 "inciting a riot and served time in prison; he received a pardon decades later. The FBI "
                 "declined to reopen the case when asked in 2007. It is considered the first fatal shooting "
                 "of student protesters on a U.S. college campus, predating the 1970 Kent State shootings.",
         known=["The victims' identities, ages, and the February 8, 1968 date and circumstances, per multiple contemporaneous and historical accounts.",
                "Nine South Carolina Highway Patrol officers were identified and tried on federal excessive-force charges; all nine were acquitted."],
         unknown=["No officer was ever convicted in the deaths.",
                  "Which specific officers fired the fatal shots was not conclusively established at trial."],
         unanswered=["Why did the FBI decline to reopen the case when formally asked to in 2007?",
                     "What became of the multiple state legislative proposals to formally investigate or compensate the victims' families, none of which passed?",
                     "What additional documentation, if any, exists in South Carolina state archives regarding the incident?"],
         extraSources=[src("BlackPast.org \u2014 case summary",
                            "https://blackpast.org/african-american-history/orangeburg-massacre-1968/", True),
                        src("Lowcountry Digital History Initiative, College of Charleston \u2014 case summary",
                            "https://ldhi.library.cofc.edu/exhibits/show/orangeburg-massacre/oburg-intro", True)]),
    dict(id="henry-marrow", caseNumber="032", name="Henry \"Dickie\" Marrow Jr.",
         status="unsolved", caseType="homicide", year=1970, age=23, gender="male",
         city="Oxford", county="Granville", state="NC", caseSeries=None,
         summary="Henry \"Dickie\" Marrow Jr., 23, an Army veteran, walked to Robert Teel's store in Oxford "
                 "on the evening of May 11, 1970 to buy a Coca-Cola. When Marrow spoke to a young white "
                 "woman near the store, Teel and two other family members interpreted it as offensive, "
                 "chased Marrow into the parking lot, beat him, and shot him; he died the next day. At "
                 "trial that July, an all-white jury heard eyewitnesses identify Larry Teel as the shooter, "
                 "but a defense witness, Roger Oakley, unexpectedly testified that he had fired the fatal "
                 "shot himself, by accident. All three men \u2014 Robert Teel, Larry Teel, and Oakley \u2014 "
                 "were acquitted on all counts; the prosecutor called the verdict \"absolutely the worst "
                 "miscarriage of justice I have ever seen.\" The killing and acquittal set off riots and "
                 "arson in Oxford and led to an 18-month boycott of white-owned businesses, organized by "
                 "Marrow's cousin Benjamin Chavis, that eventually forced the desegregation of the town's "
                 "public facilities. The case is the subject of Timothy B. Tyson's book \"Blood Done Sign "
                 "My Name\" and its 2010 film adaptation.",
         known=["Victim identity, background, and the May 11\u201312, 1970 date and circumstances, per the DOJ's public case file and extensive contemporaneous and historical reporting.",
                "Robert Teel, Larry Teel, and Roger Oakley were tried on murder and related charges in July 1970 and acquitted on all counts by an all-white jury."],
         unknown=["No one was ever convicted in the killing.",
                  "Which of the men actually fired the fatal shot was disputed at trial and never resolved; eyewitnesses and a defendant's own testimony gave conflicting accounts."],
         unanswered=["Why did the defense wait until the final day of trial to introduce Oakley's account of firing the fatal shot?",
                     "What specific findings, if any, came from a DOJ review of the case under the Emmett Till Act?",
                     "What became of the wrongful-death civil suit Marrow's widow filed against the Teels later in 1970?"],
         extraSources=[src("U.S. Department of Justice \u2014 case file",
                            "https://www.justice.gov/crt/case/henry-d-dickie-marrow-jr-deceased", True),
                        src("North Carolina Department of Natural and Cultural Resources \u2014 case summary",
                            "https://www.dncr.nc.gov/blog/2016/05/11/1970-oxford-murder-sparked-violent-protests", True)]),
    dict(id="donna-ann-reason", caseNumber="033", name="Donna Ann Reason",
         status="unsolved", caseType="homicide", year=1970, age=9, gender="female",
         city="Chester", county="Delaware", state="PA", caseSeries=None,
         summary="Donna Ann Reason, 9, was killed just after midnight on May 19, 1970 when someone threw a "
                 "Molotov cocktail through the living room window of her family's newly purchased home in "
                 "Chester, setting it ablaze; two of her siblings escaped through an upstairs window, but "
                 "Donna did not survive the fire. Her parents, Gloria and Robert Reason, were a mixed-race "
                 "couple living in an integrated neighborhood, though her father told a local newspaper he "
                 "did not believe the family's race played a role, noting other interracial couples lived "
                 "nearby. Police told reporters at the time that a nearby home belonging to a district "
                 "justice of the peace, which officers had been assigned to guard, may have been the "
                 "attack's actual intended target. A coroner's jury ordered homicide charges against "
                 "whoever was responsible, but no one was ever charged. The FBI reviewed the case under the "
                 "Emmett Till Unsolved Civil Rights Crime Act following a referral; the DOJ's Civil Rights "
                 "Division closed its file in February 2025, stating it found no evidence the crime was "
                 "racially motivated and that the statute of limitations had run on any federal hate crime "
                 "charges in any case. A state homicide investigation reportedly remains open.",
         known=["Victim identity and the May 19, 1970 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "The DOJ's 2025 closing file states it found no evidence the attack was racially motivated, and that Pennsylvania has an open state homicide investigation into the case."],
         unknown=["No one was ever charged in the firebombing.",
                  "Whether the attack was actually intended for the Reason home or a neighboring home, as police speculated at the time, was never resolved."],
         unanswered=["What became of the reward fund Donna's father tried to raise for information in the case?",
                     "What, if anything, has Pennsylvania's ongoing state homicide investigation established in the decades since?",
                     "What specific evidence did the DOJ's 2025 review examine before concluding a racial motive could not be established?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/media/1408741/dl", True),
                        src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/donna-ann-reason/", True)]),
    dict(id="elbert-williams", caseNumber="034", name="Elbert Williams",
         status="unsolved", caseType="homicide", year=1940, age=31, gender="male",
         city="Brownsville", county="Haywood", state="TN", caseSeries=None,
         summary="Elbert Williams, 31, a laundry worker and charter member of the NAACP's newly formed "
                 "Brownsville branch, was abducted from his home on the night of June 20, 1940 by Haywood "
                 "County Sheriff Samuel \"Tip\" Hunter, along with fellow NAACP member Thomas Davis, and "
                 "taken to the local jail for questioning about the chapter's activities \u2014 weeks after "
                 "Williams and other members had attempted, unsuccessfully, to register to vote. Davis was "
                 "released into a waiting mob but escaped unharmed; Williams was never seen alive again. His "
                 "mutilated body was pulled from the Hatchie River three days later and buried in an "
                 "unmarked grave. A six-member, all-white coroner's jury refused to return any indictments, "
                 "and no cause of death was ever officially determined. In the following months, as many as "
                 "40 Black families fled Brownsville under threat of violence, Black residents were barred "
                 "from meeting even for church services, and two more Black men were beaten to death by the "
                 "same night marshal involved in Williams's abduction; the local NAACP branch dissolved and "
                 "did not reorganize until 1961. NAACP Special Counsel Thurgood Marshall personally "
                 "investigated and was sharply critical of the federal government's investigation and its "
                 "failure to prosecute. Williams is considered the first known NAACP member killed for his "
                 "civil rights activism, and his killing is regarded as the last documented lynching in "
                 "Tennessee history. Haywood County reopened a state investigation into the case in 2018.",
         known=["Victim identity, background, and the June 20\u201323, 1940 timeline, per the DOJ's public case file and the Equal Justice Initiative.",
                "The DOJ's case file states Sheriff Samuel \"Tip\" Hunter personally abducted Williams from his home; no cause of death was ever officially determined, and no indictments were ever returned."],
         unknown=["No one was ever charged or convicted in Williams's death.",
                  "The circumstances of his final three days, between his abduction and the recovery of his body, were never established."],
         unanswered=["What did Thurgood Marshall's contemporaneous investigation uncover that the official inquiry did not?",
                     "What has Haywood County's state investigation, reopened in 2018, established since?",
                     "Why did the FBI decline the family's 2017 request to reopen a federal review, and what specifically did that decision rely on?"],
         extraSources=[src("U.S. Department of Justice \u2014 case file",
                            "https://www.justice.gov/crt/case/elbert-williams", True),
                        src("BlackPast.org \u2014 case summary",
                            "https://www.blackpast.org/african-american-history/williams-elbert-1908-1940/", True)]),
    dict(id="eddie-cook", caseNumber="035", name="Eddie Cook",
         status="unsolved", caseType="homicide", year=1965, age=53, gender="male",
         city="Detroit", county="Wayne", state="MI", caseSeries=None,
         summary="Eddie Cook, 53, a city sanitation worker, father of three, and grandfather, was shot in "
                 "the chest before dawn on November 7, 1965, while walking near his home in midtown "
                 "Detroit after stopping in the area for coffee. A car carrying four or five white youths "
                 "pulled alongside and someone inside fired a shotgun blast at him before speeding away; "
                 "Cook died at the hospital within the hour. Police at the time theorized the shooting may "
                 "have been retaliation for an unrelated incident earlier that day, or an accidental hit "
                 "during a fight between rival gangs. Detroit's mayor publicly condemned the killing and "
                 "Cook's union offered a reward, and homicide detectives logged more than 1,000 "
                 "investigative hours interviewing dozens of young people who claimed to have information "
                 "\u2014 but by their own account, none of it led anywhere. No one was ever identified as a "
                 "suspect, and the DOJ closed its file in 2020 without identifying who fired the shot or "
                 "who else was in the car.",
         known=["Victim identity, background, and the November 7, 1965 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "The Detroit Police Department's contemporaneous investigation did not identify a suspect, per the same records."],
         unknown=["No suspect was ever identified in the shooting.",
                  "Whether the shooting was a case of mistaken identity, gang retaliation, or a racially motivated attack was never conclusively determined."],
         unanswered=["What became of the more than 1,000 hours of leads Detroit homicide detectives logged without result?",
                     "Who were the young men interviewed by police who claimed knowledge of the shooting, and why did none of the leads hold up?",
                     "What did the DOJ's 2020 review find, if anything, beyond the original 1965 investigation?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/eddie-cook-notice-close-file", True),
                        src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/eddie-cook/", True)]),
    dict(id="lee-edward-culbreath", caseNumber="036", name="Lee Edward Culbreath",
         status="unsolved", caseType="homicide", year=1965, age=14, gender="male",
         city="Portland", county="Ashley", state="AR", caseSeries=None,
         summary="Lee Edward Culbreath, 14, was shot and killed outside a caf\u00e9 in Portland on December "
                 "5, 1965, while waiting for a friend who had gone to look at a Christmas tree at a nearby "
                 "store. Ed Vail, a white man who had been drinking heavily with his brother James, fired "
                 "three shots at Culbreath through the open window of their pickup truck as they drove by; "
                 "Culbreath was struck once in the chest and managed to run inside the caf\u00e9 before "
                 "collapsing, dying of internal bleeding. Both brothers were arrested about 20 minutes "
                 "later at a state trooper's roadblock; troopers testified both men admitted to being Klan "
                 "members, though both later denied it. Ed Vail was tried, and a jury of eleven white men "
                 "and one Black man found him guilty of second-degree murder; he was sentenced to 21 years. "
                 "Arkansas declined to prosecute James Vail the following year, and no charges were ever "
                 "brought against him. Neither newspaper reports nor the DOJ's later review identified any "
                 "specific reason for the attack.",
         known=["Victim identity and the December 5, 1965 date and circumstances, per the DOJ's public case file, the Encyclopedia of Arkansas, and contemporaneous trial coverage.",
                "Ed Vail was convicted of second-degree murder and sentenced to 21 years; Arkansas declined to prosecute his brother James, who was never charged."],
         unknown=["No specific motive for the shooting was ever established.",
                  "James Vail's exact role, beyond driving the truck, was never resolved in court."],
         unanswered=["Why did Arkansas decline to prosecute James Vail in 1966 despite his arrest and initial murder charge?",
                     "What became of the .22 revolver FBI analysis confirmed as the murder weapon?",
                     "What did Ed Vail's own account, that he was too intoxicated to recall being in Portland that day, leave unexplained about the shooting itself?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/lee-edward-culbreath-notice-close-file", True),
                        src("Encyclopedia of Arkansas \u2014 case summary",
                            "https://encyclopediaofarkansas.net/entries/lee-edward-culbreath-13888/", True)]),
    dict(id="james-powell", caseNumber="037", name="James Powell",
         status="unsolved", caseType="homicide", year=1964, age=15, gender="male",
         city="New York", county="New York", state="NY", caseSeries=None,
         summary="James Powell, 15, was shot and killed on East 76th Street in Manhattan on the morning of "
                 "July 16, 1964, by off-duty NYPD Lieutenant Thomas Gilligan. A building superintendent had "
                 "sprayed a hose at a group of Black students, including Powell, gathered near a summer "
                 "school; when Powell followed the superintendent into the building, Gilligan, who was "
                 "nearby in plainclothes, intervened. Gilligan said Powell lunged at him with a knife and "
                 "fired three shots, killing him in front of his classmates and roughly a dozen other "
                 "witnesses; several witnesses said Powell was unarmed, and no knife matching Gilligan's "
                 "account was recovered at the scene. A grand jury declined to indict Gilligan, who was "
                 "cleared by the department. The shooting, and the community's outrage over it, set off six "
                 "consecutive nights of rioting across Harlem and Bedford-Stuyvesant \u2014 one of the "
                 "first major uprisings of the era.",
         known=["Victim identity, age, and the July 16, 1964 date and circumstances, per extensive contemporaneous and historical reporting.",
                "NYPD Lieutenant Thomas Gilligan was identified as the shooter; a grand jury declined to indict him, and he was never charged."],
         unknown=["No knife matching Gilligan's account of the encounter was ever recovered.",
                  "Whether Powell posed any actual threat to Gilligan was disputed by eyewitnesses at the time and was never resolved through prosecution."],
         unanswered=["What specific evidence did the grand jury weigh before declining to indict Gilligan?",
                     "What became of the building superintendent, Patrick Lynch, whose actions preceded the encounter?",
                     "What official department review, if any, followed the riots regarding the department's own protocols?"],
         extraSources=[src("Equal Justice Initiative \u2014 background reference",
                            "https://eji.org/", True),
                        src("Rutgers University \u2014 \u201cInside the Harlem Uprising of 1964\u201d",
                            "https://www.rutgers.edu/news/inside-harlem-uprising-1964", True)]),
    dict(id="rogers-hamilton", caseNumber="038", name="Rogers Hamilton",
         status="unsolved", caseType="homicide", year=1957, age=18, gender="male",
         city="Hayneville", county="Lowndes", state="AL", caseSeries=None,
         summary="Rogers Hamilton, 18, was abducted from his home near Hayneville at about 1:30 a.m. on "
                 "October 22, 1957. According to his mother, Beatrice Hamilton, one or two white men drove "
                 "up in a pickup truck and called Hamilton's name several times; he went outside, spoke "
                 "with one of the men, then got into the truck with him. His mother followed on foot and "
                 "watched as the truck stopped a short distance away, where she said a white man standing "
                 "outside it drew a pistol and shot her son in the face. Some accounts report Hamilton had "
                 "recently been seen waving at a white girl in town, which relatives believe may have "
                 "prompted the killing. The Lowndes County sheriff's office investigated but never "
                 "identified a suspect, and a later reporter found the sheriff had privately dismissed "
                 "Beatrice Hamilton's eyewitness account as implausible. No one was ever arrested. The DOJ "
                 "closed its file in 2016, citing the lack of any identified subject and the destruction of "
                 "the original Lowndes County sheriff's office records.",
         known=["Victim identity and the October 22, 1957 date and circumstances, per the DOJ's public case file and his mother's eyewitness account.",
                "No suspect was ever identified, and the original county investigative records were later destroyed, per the same file."],
         unknown=["No motive for the killing was ever officially confirmed.",
                  "The identity of the man or men who abducted Hamilton was never established."],
         unanswered=["What did the FBI's own 1957 report, which reportedly contained additional detail on a possible motive, ultimately conclude?",
                     "Why did the Lowndes County sheriff dismiss Beatrice Hamilton's direct eyewitness account rather than pursue it as a lead?",
                     "What became of the original Lowndes County Sheriff's Office investigative records before their destruction?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/rogers-hamilton-notice-close-file", True),
                        src("Alabama Reporter \u2014 \u201cRogers Hamilton: No justice for murdered Black teen\u201d",
                            "https://www.alreporter.com/2025/04/02/rogers-hamilton-no-justice-for-murdered-black-teen/", True)]),
    dict(id="matthew-williams", caseNumber="039", name="Matthew Williams",
         status="unsolved", caseType="homicide", year=1931, age=23, gender="male",
         city="Salisbury", county="Wicomico", state="MD", caseSeries=None,
         summary="Matthew Williams, 23, a laborer at a local box factory, was lynched by a mob of more "
                 "than 2,000 people in Salisbury on the evening of December 4, 1931. Earlier that day, "
                 "Williams's longtime employer, Daniel J. Elliott, was shot dead in his office; Williams "
                 "was found badly wounded nearby, and the official account at the time held that he had "
                 "shot Elliott over a wage dispute and then tried to take his own life, though some "
                 "contemporaries considered it more plausible that Elliott's own son had fired the shots. "
                 "That evening, while Williams was recovering under police guard at a segregated hospital "
                 "ward, a mob stormed the building, dragged him from his bed, and threw him from a window "
                 "into the crowd below. He was hanged from a tree at the courthouse square, his body cut "
                 "down and dragged through Salisbury's Black neighborhoods behind a car, and then burned; "
                 "spectators took pieces of his body and the rope as souvenirs. In the same wave of "
                 "violence, an unidentified Black man was separately killed nearby by members of the same "
                 "mob. No one was ever identified or prosecuted for either killing. The Justice Department "
                 "funded a renewed investigation into the case beginning in 2019 under the Emmett Till Act.",
         known=["Victim identity, background, and the December 4, 1931 date and circumstances, per the Maryland State Archives and extensive contemporary press coverage.",
                "No one was ever identified or prosecuted for the lynching, per the same records."],
         unknown=["The circumstances of Elliott's shooting \u2014 whether Williams or Elliott's son fired the fatal shots \u2014 were never resolved.",
                  "The identity of the second Black man killed by the mob that same night has never been publicly established."],
         unanswered=["What has the DOJ's Emmett Till Act-funded investigation, opened in 2019, established since?",
                     "Who was the unidentified second victim killed the same night, and what became of any records of his death?",
                     "What role, if any, did local law enforcement play in allowing the mob access to the hospital ward?"],
         extraSources=[src("Maryland State Archives \u2014 biography and case summary",
                            "https://msa.maryland.gov/megafile/msa/speccol/sc3500/sc3520/013700/013749/html/13749bio.html", True),
                        src("International Center for Transitional Justice \u2014 case summary",
                            "https://www.ictj.org/latest-news/ghosts-racial-violence-maryland", True)]),
    dict(id="carl-hampton", caseNumber="040", name="Carl Hampton",
         status="unsolved", caseType="homicide", year=1970, age=21, gender="male",
         city="Houston", county="Harris", state="TX", caseSeries=None,
         summary="Carl Hampton, 21, founder and chairman of the People's Party II \u2014 a Houston "
                 "organization modeled on the Black Panther Party \u2014 was shot and killed on the night of "
                 "July 26, 1970, the tenth day of a standoff between his group and Houston police that had "
                 "begun after officers were seen harassing a member selling the group's newspaper. Houston "
                 "police officers, positioned with rifles on the roof of a nearby church, fired on Hampton "
                 "and others outside the group's headquarters on Dowling Street; Hampton was hit in the "
                 "stomach and chest and died at the hospital hours later. Police said the shooting was in "
                 "self-defense, responding to gunfire from the headquarters; community members and later "
                 "researchers disputed that account, and the circumstances remain contested. A Harris "
                 "County grand jury declined to indict any of the officers involved.",
         known=["Victim identity, role, and the July 26, 1970 date and circumstances, per multiple contemporaneous and historical accounts.",
                "A Harris County grand jury reviewed the shooting in late 1970 and declined to indict any of the officers involved."],
         unknown=["Who fired first has never been independently established; police and community accounts directly conflict.",
                  "Which specific officers fired the fatal shots was not made public."],
         unanswered=["What evidence did the grand jury weigh in declining to indict, and has that record ever been made public?",
                     "What became of the claim, raised by community sources at the time, that a reporter present on the church roof assisted in identifying Hampton before the shooting?",
                     "What internal HPD records, if any, survive from the ten-day standoff that preceded the shooting?"],
         extraSources=[src("Houston Chronicle \u2014 \u201cRemembering Houston's Black Panthers\u201d",
                            "https://www.houstonchronicle.com/local/gray-matters/article/The-Black-Panthers-The-original-Black-Lives-6833943.php", True),
                        src("Liberation News \u2014 case summary",
                            "https://liberationnews.org/black-liberation-leader-commemorated-52-years-after-assassination-by-houston-police/", True)]),
    dict(id="lester-mitchell", caseNumber="041", name="Lester Mitchell",
         status="unsolved", caseType="homicide", year=1966, age=None, gender="male",
         city="Dayton", county="Montgomery", state="OH", caseSeries=None,
         summary="Lester Mitchell, a West Dayton business owner, was shot in the face with a shotgun just "
                 "after 3 a.m. on September 1, 1966, while sweeping the sidewalk outside his bar on West "
                 "Fifth Street. Witnesses said a red car pulled up and a white man fired from inside it "
                 "before driving off; accounts differed on whether one man or several were involved. "
                 "Mitchell was taken to the hospital, where he later died of his wounds. The killing, in a "
                 "city where discriminatory housing policy had crowded some 60,000 Black residents into a "
                 "segregated west side with underfunded schools and city services, triggered one of the "
                 "worst riots in Dayton's history; Ohio's governor deployed roughly 1,000 National "
                 "Guardsmen, who remained in the city for five days. Months later, Dayton's police chief "
                 "told reporters an informant had identified the shooter as a man who had since died in an "
                 "unrelated shootout, but a retired detective who later reexamined the case found little "
                 "evidence police had done much to confirm that account. No one was ever charged.",
         known=["Victim identity, background, and the September 1, 1966 date and circumstances, per extensive contemporaneous and historical reporting.",
                "No one was ever arrested or charged in the killing, per the same reporting."],
         unknown=["The identity of the shooter, and whether one or more people were in the car, was never confirmed.",
                  "Whether the police chief's later claim that an informant identified a (by then deceased) suspect was ever meaningfully investigated remains disputed."],
         unanswered=["What specific evidence, if any, supported the informant's claim that the shooter had died in an unrelated shootout?",
                     "What became of the retired detective's later re-investigation of the case?",
                     "What police records survive from the original 1966 investigation?"],
         extraSources=[src("Dayton Daily News \u2014 \u201cLasting Scars: the 1966 Dayton riot\u201d",
                            "https://www.daytondailynews.com/news/lasting-scars-the-1966-dayton-riot-and-west-dayton-today/fROse29JYZcC9roAMSpqfK/", True),
                        src("BlackPast.org \u2014 case summary",
                            "https://blackpast.org/african-american-history/the-1966-dayton-ohio-uprising/", True)]),
    dict(id="timothy-thomas", caseNumber="042", name="Timothy Thomas",
         status="unsolved", caseType="homicide", year=2001, age=19, gender="male",
         city="Cincinnati", county="Hamilton", state="OH", caseSeries=None,
         summary="Timothy Thomas, 19, was shot and killed by Cincinnati Police Officer Stephen Roach in a "
                 "dark alley in the Over-the-Rhine neighborhood in the early hours of April 7, 2001, while "
                 "fleeing on foot from officers attempting to arrest him on a series of misdemeanor traffic "
                 "warrants. Thomas was unarmed; Roach said he believed Thomas was reaching for a weapon. "
                 "Thomas was the fifteenth Black man to die in a confrontation with Cincinnati police since "
                 "1995, and his death set off three nights of rioting, the city's worst racial unrest since "
                 "1968, with hundreds arrested. A grand jury indicted Roach on misdemeanor charges of "
                 "negligent homicide and obstructing official business; at a bench trial that September, a "
                 "judge acquitted him on both counts, ruling the shooting was a reasonable split-second "
                 "reaction to a dangerous situation. Roach remained a police officer for years afterward.",
         known=["Victim identity and the April 7, 2001 date and circumstances, per extensive contemporaneous news coverage and court records.",
                "Officer Stephen Roach was identified, indicted on misdemeanor charges, and acquitted of both at a September 2001 bench trial."],
         unknown=["Whether Thomas made a threatening movement, as Roach claimed, was disputed and never independently confirmed.",
                  "The grand jury's specific reasoning for returning only misdemeanor charges, rather than more serious ones, was not made public."],
         unanswered=["What did the Collaborative Agreement reforms that followed the riots ultimately change about Cincinnati policing in practice?",
                     "What became of the broader pattern-or-practice concerns the incident raised about the department?",
                     "What, if anything, has the city or department done since to revisit the case?"],
         extraSources=[src("The Washington Post \u2014 \u201cOfficer Is Acquitted in Killing That Led to Riots in Cincinnati\u201d",
                            "https://www.washingtonpost.com/archive/politics/2001/09/27/officer-is-acquitted-in-killing-that-led-to-riots-in-cincinnati/a678d262-f020-4766-998d-d1f27eed6e3b/", True),
                        src("IAED Journal \u2014 case retrospective",
                            "https://www.iaedjournal.org/officer-involved-project", True)]),
    dict(id="whitfield-and-whitney", caseNumber="043", name="Ed Whitfield & Earl Whitney",
         status="unsolved", caseType="homicide", year=1919, age=None, gender="male",
         city="Chapmanville", county="Logan", state="WV", caseSeries=None,
         summary="Ed Whitfield and Earl Whitney, two Black coal miners employed by the Island Creek "
                 "Colliery Company, were seized by a white mob on December 15, 1919 while being transported "
                 "by deputies from Chapmanville to Huntington. The two had been accused of killing E.D. "
                 "Meek, a white construction foreman. The mob took them from custody, backed them against a "
                 "rail car, and shot them, then threw their bodies into the Guyandotte River. Logan County "
                 "Sheriff Don Chafin \u2014 who would later organize the armed force that fought striking "
                 "miners at the Battle of Blair Mountain in 1921 \u2014 declined to investigate the "
                 "killings. It was the only lynching recorded in West Virginia's southern coalfields during "
                 "the nationwide wave of racial violence in the summer and fall of 1919 known as Red "
                 "Summer. No one was ever charged.",
         known=["The victims' identities, occupation, and the December 15, 1919 date and circumstances, per the West Virginia Encyclopedia and multiple historical accounts.",
                "Sheriff Don Chafin declined to investigate the killings, per the same sources; no one was ever charged."],
         unknown=["Whether Whitfield and Whitney had any actual connection to Meek's killing was never established in any court.",
                  "The identities of the individual mob members were never publicly documented."],
         unanswered=["What became of the original murder investigation into E.D. Meek's death?",
                     "What, if anything, do surviving Logan County records from December 1919 show about the case?",
                     "Why did West Virginia authorities take no action against Sheriff Chafin for declining to investigate?"],
         extraSources=[src("West Virginia Encyclopedia (e-WV) \u2014 \u201cAfrican American Heritage\u201d",
                            "https://www.wvencyclopedia.org/entries/18", True),
                        src("The Clio \u2014 \u201cWhitfield and Whitney Lynching Site\u201d",
                            "https://theclio.com/entry/47848", True)]),
    dict(id="will-brown", caseNumber="044", name="Will Brown",
         status="unsolved", caseType="homicide", year=1919, age=40, gender="male",
         city="Omaha", county="Douglas", state="NE", caseSeries=None,
         summary="Will Brown, 40, a meatpacking plant worker later regarded by historians as innocent, was "
                 "lynched by a mob in Omaha on the night of September 28, 1919, four days after a white "
                 "woman accused him of assault. Brown was being held in the Douglas County Courthouse jail "
                 "when a mob of thousands surrounded the building, set it on fire, and battled police for "
                 "hours; when Omaha's mayor tried to intervene he was nearly lynched himself before being "
                 "rescued. The mob eventually seized Brown, beat him, hanged him from a lamp pole outside "
                 "the courthouse, shot his body more than one hundred times, then burned it and dragged the "
                 "remains behind a car through the streets. A newspaper photograph of the burned body "
                 "became one of the most widely reproduced images of the Red Summer of 1919, a nationwide "
                 "wave of racial violence. Federal troops were called in to restore order. No one was ever "
                 "charged in Brown's killing.",
         known=["Victim identity, background, and the September 28, 1919 date and circumstances, per History Nebraska (the state historical society) and PBS's American Experience.",
                "No one was ever charged or prosecuted for the lynching, per the same sources."],
         unknown=["The underlying assault accusation against Brown was never tested in any court, and historians have since characterized him as innocent.",
                  "The identity of at least one other Black Omaha resident reportedly killed by the same mob that night has never been established."],
         unanswered=["What became of the original assault investigation and accusation against Brown?",
                     "Who was the second victim some accounts describe the mob killing that same night, and what happened to any record of that death?",
                     "What specific accountability, if any, was ever pursued against identifiable mob participants?"],
         extraSources=[src("History Nebraska \u2014 \u201cA Horrible Lynching\u201d",
                            "https://www.nebraskastudies.org/en/1900-1924/racial-tensions/a-horrible-lynching/", True),
                        src("PBS American Experience \u2014 \u201cRed Summer: When Racist Mobs Ruled\u201d",
                            "https://www.pbs.org/wgbh/americanexperience/features/t-town-red-summer-racist-mobs/", True)]),
    dict(id="duluth-lynchings", caseNumber="045", name="Elias Clayton, Elmer Jackson & Isaac McGhie",
         status="unsolved", caseType="homicide", year=1920, age=None, gender="male",
         city="Duluth", county="St. Louis", state="MN", caseSeries=None,
         summary="Elias Clayton, Elmer Jackson, and Isaac McGhie, three Black men in their early twenties "
                 "working as laborers for a traveling circus, were lynched by a mob in Duluth on the night "
                 "of June 15, 1920. The night before, two white teenagers claimed that Black circus workers "
                 "had robbed them at gunpoint and raped the young woman; a doctor's examination later found "
                 "no evidence a rape had occurred. Police arrested six Black circus workers regardless. "
                 "That evening, a mob estimated at 5,000 to 10,000 people gathered outside the jail, seized "
                 "three of the men, beat them, and hanged them from a light pole in downtown Duluth. The "
                 "Minnesota National Guard arrived the next morning to protect the three men who survived. "
                 "No one was ever charged with the lynchings themselves; three white men were later "
                 "convicted of rioting, a lesser charge. A fourth accused man, Max Mason, was the only "
                 "person convicted in connection with the underlying accusation and served time in prison; "
                 "he was granted the state's first posthumous pardon in 2020, a century after the killings.",
         known=["The victims' identities, ages, and the June 15, 1920 date and circumstances, per the Minnesota Historical Society.",
                "A doctor's examination found no medical evidence supporting the rape accusation, and no one was ever charged with the lynchings themselves, per the same source."],
         unknown=["The specific individuals who carried out the lynchings were never identified or charged.",
                  "What actually occurred between the accusers and the circus workers the night before was never established beyond dispute."],
         unanswered=["What specific evidence, if any, supported the rioting convictions of the three white men who were charged?",
                     "What became of the three surviving arrested men after the National Guard secured the jail?",
                     "What additional documentation survives in Duluth police and court records from 1920?"],
         extraSources=[src("Minnesota Historical Society \u2014 \u201cThe Lynchings\u201d",
                            "https://www.mnhs.org/duluthlynchings/lynchings", True),
                        src("Smithsonian Magazine \u2014 case retrospective",
                            "https://www.smithsonianmag.com/history/one-hundred-years-ago-mob-white-rioters-lynched-three-men-minnesota-180975062/", True)]),
    dict(id="wade-hampton", caseNumber="046", name="Wade Hampton",
         status="unsolved", caseType="homicide", year=1917, age=50, gender="male",
         city="Rock Springs", county="Sweetwater", state="WY", caseSeries=None,
         summary="Wade Hampton, 50, was taken from his cell at the Rock Springs city jail at gunpoint by "
                 "three armed men shortly after midnight on December 12, 1917, and shot to death within the "
                 "hour after an attempt to hang him from a railroad bridge failed. Hampton had been arrested "
                 "the day before on charges of attempting to assault three women, held on $5,000 bond, and "
                 "had appeared before a justice of the peace for a preliminary hearing \u2014 he was never "
                 "tried. The three men broke into the jail office, took the absent jailer's keys, and led "
                 "Hampton away in handcuffs; when the rope broke during the failed hanging, Hampton tried "
                 "to flee along a creek bed before his captors caught up to him and shot him. A coroner's "
                 "inquest, which heard from only two witnesses, neither of whom had been present during the "
                 "abduction, ruled his death was caused by \u201cparty or parties unknown.\u201d Wyoming's "
                 "acting governor personally urged the county attorney to offer a reward, and a $500 reward "
                 "was published, but no one was ever identified or charged. Hampton was buried at the "
                 "county's expense.",
         known=["Victim identity, background, and the December 11\u201312, 1917 date and circumstances, per WyoHistory.org's account, drawn from the original coroner's inquest transcript and contemporary newspapers.",
                "The coroner's inquest concluded Hampton's death came at the hands of \u201cparty or parties unknown\u201d; no one was ever charged despite a published reward.",],
         unknown=["The identities of the three men who abducted and killed Hampton were never established.",
                  "The underlying assault accusations against Hampton were never tested at trial, since he was killed before one could occur."],
         unanswered=["Why did the coroner's inquest call only two witnesses, neither of whom was present during the actual abduction?",
                     "What became of the $500 reward Wyoming's acting governor pushed the county to offer?",
                     "What connection, if any, exists between this case and the similar unsolved 1918 lynching of Edward Woodson in the same county?"],
         extraSources=[src("WyoHistory.org \u2014 \u201cA Lynching in Rock Springs\u201d",
                            "https://www.wyohistory.org/encyclopedia/lynching-rock-springs", True)]),
    dict(id="tulsa-race-massacre", caseNumber="047", name="Tulsa Race Massacre",
         status="unsolved", caseType="homicide", year=1921, age=None, gender=None,
         city="Tulsa", county="Tulsa", state="OK", caseSeries=None,
         summary="On May 31 and June 1, 1921, a white mob of up to 10,000 people attacked Greenwood, "
                 "Tulsa's prosperous Black district known as \u201cBlack Wall Street,\u201d in what the "
                 "DOJ's own 2025 review called a \u201ccoordinated, military-style attack\u201d rather than "
                 "spontaneous mob violence. As many as 300 residents were killed and more than 1,200 homes, "
                 "businesses, schools, and churches were burned; survivors were rounded up and held in "
                 "internment camps, and insurance companies later denied claims under \u201criot "
                 "clause\u201d exclusions. City officials claimed at the time that only 36 people had died; "
                 "historians have since estimated the toll at 75 to 300, and unmarked mass graves "
                 "identified in Tulsa in recent years are still being excavated and their occupants "
                 "identified. The Justice Department's Civil Rights Division formally reviewed the massacre "
                 "under the Emmett Till Unsolved Civil Rights Crime Act and released a 120-plus page report "
                 "in January 2025 \u2014 the federal government's first official accounting of the event "
                 "\u2014 finding that the Tulsa Police Department, the Tulsa County sheriff, the Oklahoma "
                 "National Guard, and then-Mayor T.D. Evans each played a role, either through direct "
                 "participation or by failing to act. The report also found that federal investigative "
                 "reports written within days of the massacre in 1921 were apparently never evaluated by "
                 "any prosecutor. No one was ever charged, and the DOJ concluded that no avenue for "
                 "prosecution remains today.",
         known=["The massacre's May 31\u2013June 1, 1921 date and scope, per the DOJ's 2025 Civil Rights Division review.",
                "The DOJ's report found the Tulsa Police Department, county sheriff, National Guard, and mayor each played a role, and that no federal prosecutor is known to have evaluated investigative reports written in 1921; no one was ever charged."],
         unknown=["The exact death toll has never been established; estimates range from 75 to as many as 300, and unmarked mass graves are still being excavated and identified.",
                  "Why federal reports written within days of the massacre were apparently never evaluated by any prosecutor at the time was never explained in any surviving record."],
         unanswered=["What further identifications will ongoing mass grave excavations in Tulsa establish?",
                     "What became of the individual insurance claims Black Tulsans filed and were denied?",
                     "What, if anything, might further public records requests reveal about the 1921 federal investigative reports the DOJ says were never acted on?"],
         extraSources=[src("U.S. Department of Justice, Civil Rights Division \u2014 \u201cReview and Evaluation: Tulsa Race Massacre\u201d",
                            "https://www.justice.gov/crt/media/1383756/dl", True),
                        src("Associated Press \u2014 case report on the DOJ's findings",
                            "https://www.yahoo.com/news/federal-probe-1921-tulsa-race-223155119.html", True)]),
    dict(id="john-henry-james", caseNumber="048", name="John Henry James",
         status="unsolved", caseType="homicide", year=1898, age=None, gender="male",
         city="Charlottesville", county="Albemarle", state="VA", caseSeries=None,
         summary="John Henry James was lynched at Wood's Crossing outside Charlottesville on July 12, 1898, "
                 "the day after Julia Hotopp, a white woman, reported being assaulted near her family's "
                 "estate. James was arrested the same day and, given fears for his safety, was being "
                 "transported by train toward a jail in Staunton when a mob of about 150 people stopped the "
                 "train and seized him. He was hanged from a locust tree and his body was shot repeatedly. A "
                 "coroner's jury found only that James \u201ccame to his death by the hands of persons "
                 "unknown.\u201d A grand jury then took the unusual step of posthumously indicting the dead "
                 "man for the assault, a charge he was never able to answer in life. That indictment stood "
                 "on the books for 125 years until Albemarle County's prosecutor asked a circuit court to "
                 "dismiss it; a judge did so on July 12, 2023, the anniversary of James's death. In 2019, "
                 "Charlottesville-area residents collected soil from the lynching site as part of the Equal "
                 "Justice Initiative's national memorial project.",
         known=["Victim identity and the July 11\u201312, 1898 date and circumstances, per Encyclopedia Virginia.",
                "The coroner's jury found James's killers were \u201cpersons unknown\u201d; the posthumous indictment against James himself was formally dismissed in 2023, per the same source and contemporaneous reporting."],
         unknown=["No one involved in the lynching was ever identified or charged.",
                  "The underlying assault allegation against James was never tested in any court during his lifetime."],
         unanswered=["What, if any, surviving Albemarle County records document the mob's composition or planning?",
                     "What prompted the original grand jury's decision to posthumously indict a man it knew was already dead?",
                     "What further local reckoning, if any, has followed the 2023 dismissal of the indictment?"],
         extraSources=[src("Encyclopedia Virginia \u2014 \u201cThe Lynching of John Henry James (1898)\u201d",
                            "https://encyclopediavirginia.org/entries/lynching-of-john-henry-james-1898-the/", True)]),
    dict(id="james-t-scott", caseNumber="049", name="James T. Scott",
         status="unsolved", caseType="homicide", year=1923, age=None, gender="male",
         city="Columbia", county="Boone", state="MO", caseSeries=None,
         summary="James T. Scott, a World War I veteran, firefighter, and janitor at the University of "
                 "Missouri, was lynched from Stewart Bridge in Columbia in the early hours of April 29, "
                 "1923, in front of more than a thousand onlookers. He had been arrested a week earlier "
                 "after Regina Almstedt, the 14-year-old daughter of a university professor, identified him "
                 "as the man who assaulted her on the same bridge, though two white coworkers were prepared "
                 "to testify that Scott had been working alongside them at the time of the attack. A mob "
                 "used a blowtorch to break into his jail cell while police and county officials looked on "
                 "without intervening by force, then hanged him. The night he died, Scott named his "
                 "cellmate, Ollie Watson, as the actual attacker; bloodhounds had independently tracked a "
                 "scent from the crime scene to where Watson normally parked, and Watson was separately "
                 "found to have raped another girl the week before the Almstedt assault. A grand jury "
                 "indicted five men suspected of leading the mob, but only one, George Barkwell, was tried; "
                 "despite eyewitness testimony from two student journalists that they saw him push Scott "
                 "from the bridge, a jury acquitted Barkwell after eleven minutes of deliberation, and "
                 "charges against the other four men were dropped the same day.",
         known=["Victim identity, background, and the April 28\u201329, 1923 date and circumstances, per the State Historical Society of Missouri.",
                "George Barkwell was tried for murder and acquitted; charges against four other indicted men were dropped the same day, per the same source."],
         unknown=["No one was ever convicted in Scott's killing.",
                  "Whether Scott or his cellmate Ollie Watson actually assaulted Regina Almstedt was never resolved in any court, though contemporaneous evidence pointed toward Watson."],
         unanswered=["Why did Columbia police and county officials decline to use force against the mob despite being present throughout the night?",
                     "What became of Ollie Watson after Scott's death?",
                     "What specific evidence led the grand jury to indict five men, when only one was ultimately tried?"],
         extraSources=[src("State Historical Society of Missouri \u2014 \u201cThe Lynching of James T. Scott\u201d",
                            "https://missouriencyclopedia.org/events/scott-james-t", True)]),
    dict(id="george-tompkins", caseNumber="050", name="George Tompkins",
         status="unsolved", caseType="homicide", year=1922, age=19, gender="male",
         city="Indianapolis", county="Marion", state="IN", caseSeries=None,
         summary="George Tompkins, 19, left his aunt and uncle's Indianapolis home on the morning of March "
                 "16, 1922, and never returned; his body was found that afternoon hanging from a sapling in "
                 "what is now Riverside Park, his hands tied behind his back. Marion County Coroner Dr. Paul "
                 "Robinson examined the body and told reporters at the time that \u201cthere could be no "
                 "question that the man had been murdered and his body then tied to the tree,\u201d and that "
                 "Tompkins was \u201cdead or almost dead when he was hanged.\u201d Despite this, and despite "
                 "initial police reports treating the death as a lynching, detectives reversed course two "
                 "days later; the word \u201chomicide\u201d on the death certificate was crossed out in "
                 "pencil and \u201csuicide\u201d written in its place, and no further investigation followed. "
                 "Tompkins had never been accused of any crime, and no motive for his killing was ever "
                 "established. He was buried in an unmarked grave. In March 2022, a century after his "
                 "death, the Indiana Remembrance Coalition petitioned Marion County to review the case; "
                 "Deputy Chief Coroner Alfie McGinty formally corrected Tompkins's manner of death to "
                 "homicide, and a historical marker was later placed at the site where his body was found.",
         known=["Victim identity and the March 16, 1922 date and circumstances, per the Indiana Remembrance Coalition and the original coroner's contemporaneous statement to the press.",
                "Marion County formally corrected Tompkins's death certificate from suicide to homicide in March 2022, per multiple news organizations that covered the correction."],
         unknown=["No one was ever arrested or charged in Tompkins's death.",
                  "No motive for the killing was ever established, and Tompkins was never accused of any crime."],
         unanswered=["Who altered Tompkins's death certificate from homicide to suicide two days after his death, and why?",
                     "What became of the original 1922 police investigation records, if they survive?",
                     "What further review, if any, might a modern homicide investigation of the case yield?"],
         extraSources=[src("CNN \u2014 case report on the 2022 death certificate correction",
                            "https://www.cnn.com/2022/03/16/us/lynching-victim-george-tompkins-death-indiana-homicide/index.html", True),
                        src("Wikipedia \u2014 \u201cLynching of George Tompkins\u201d, background reference",
                            "https://en.wikipedia.org/wiki/Lynching_of_George_Tompkins", True)]),
    dict(id="george-white", caseNumber="051", name="George White",
         status="unsolved", caseType="homicide", year=1903, age=24, gender="male",
         city="Wilmington", county="New Castle", state="DE", caseSeries=None,
         summary="George White, 24, a Black farm laborer, was arrested June 16, 1903 and accused of "
                 "killing Helen Bishop, a white woman, near Wilmington. He denied any involvement and was "
                 "held at the New Castle County Workhouse to await a September trial. Two lynch mobs "
                 "attempted to abduct him from the workhouse within a week of his arrest, and on June 21 a "
                 "local white pastor, Robert Elwood, urged a crowd to carry out swift vengeance rather than "
                 "wait for the courts. The following night, a mob of thousands stormed the workhouse and "
                 "seized White; he was taken to Price's Corner, tied to a stake, and burned to death on "
                 "June 23 in front of a crowd variously estimated at several hundred to several thousand "
                 "people, some of whom took pieces of his remains afterward. No one was ever convicted. It "
                 "is generally regarded as the only documented lynching in Delaware's history. A state "
                 "historical marker was dedicated at the site in 2019 after a local high school student's "
                 "research prompted the Delaware Public Archives to install it; the marker was stolen that "
                 "August and replaced two months later.",
         known=["Victim identity, background, and the June 16\u201323, 1903 date and circumstances, per the Delaware Public Archives' official historical marker.",
                "No one was ever convicted in the lynching, per the same source; a state historical marker commemorating the case was dedicated in 2019."],
         unknown=["The identities of individual mob participants were never prosecuted despite widespread contemporary knowledge of who was involved.",
                  "The full circumstances of Helen Bishop's death, and White's actual connection to it, were never tested in any court."],
         unanswered=["What became of Pastor Robert Elwood after being called before the New Castle Presbytery for his role in inciting the mob?",
                     "Why did Delaware's courts decline to move White's trial date earlier despite the escalating risk to his life?",
                     "What further documentation, if any, survives regarding the two earlier attempts to lynch White before June 23?"],
         extraSources=[src("Delaware Public Archives \u2014 official historical marker text",
                            "https://archives.delaware.gov/delaware-historical-markers/the-lynching-of-george-white/", True),
                        src("Equal Justice Initiative \u2014 case summary",
                            "https://calendar.eji.org/racial-injustice/jun/23", True)]),
    dict(id="preston-porter-jr", caseNumber="052", name="Preston Porter Jr.",
         status="unsolved", caseType="homicide", year=1900, age=15, gender="male",
         city="Limon", county="Lincoln", state="CO", caseSeries=None,
         summary="Preston Porter Jr., 15, was burned to death by a mob near Limon on November 16, 1900. "
                 "Porter, his father, and his brother had come to Colorado from Kansas earlier that year for "
                 "railroad work; after an 11-year-old white girl, Louise Frost, was found murdered near "
                 "Limon on November 8, the three were stopped and arrested on suspicion while passing "
                 "through Denver, despite no evidence connecting them to the crime. Held for four days under "
                 "coercive interrogation, Porter confessed after being told his father and brother would "
                 "likely be lynched if he did not. As he was being transported by train toward the county "
                 "jail, an armed mob stopped the train at Limon \u2014 which was not a scheduled stop \u2014 "
                 "and removed him over the protests of the deputy escorting him. Several hundred spectators, "
                 "some arriving by train from Denver and Colorado Springs, gathered to watch as the mob "
                 "chained Porter to a railroad stake and burned him alive. A coroner's inquest concluded he "
                 "died \u201cat the hands of parties unknown,\u201d despite extensive newspaper coverage that "
                 "identified mob participants by name. No one was ever charged.",
         known=["Victim identity, background, and the November 8\u201316, 1900 date and circumstances, per History Colorado and the Colorado Encyclopedia.",
                "A coroner's inquest concluded Porter's death came at the hands of \u201cparties unknown\u201d despite press coverage naming mob participants; no one was ever charged, per the same sources."],
         unknown=["Whether Porter's coerced confession bore any relationship to the actual circumstances of Louise Frost's death was never tested in any court.",
                  "The identities of the mob members who stopped the train and carried out the killing, though reported by name in contemporary newspapers, were never formally prosecuted."],
         unanswered=["What became of the newspaper accounts that reportedly named mob participants, and why did the coroner's inquest not act on them?",
                     "What happened to Porter's father and brother after they left Colorado following the lynching?",
                     "What role, if any, did the deputy escorting Porter face for failing to prevent the train from being stopped?"],
         extraSources=[src("History Colorado \u2014 \u201cA Lynching in Limon\u201d",
                            "https://www.historycolorado.org/lost-highways/2022/01/18/lynching-limon", True),
                        src("Colorado Encyclopedia \u2014 case summary",
                            "https://coloradoencyclopedia.org/article/preston-porter-jr", True)]),
    dict(id="samuel-johnson", caseNumber="053", name="Samuel Johnson (\u201cMingo Jack\u201d)",
         status="unsolved", caseType="homicide", year=1886, age=66, gender="male",
         city="Eatontown", county="Monmouth", state="NJ", caseSeries=None,
         summary="Samuel Johnson, 66, a former slave known locally as \u201cMingo Jack\u201d for his years as "
                 "a jockey, was lynched in Eatontown on the night of March 5, 1886, hours after being "
                 "arrested on a rape accusation. Constable Hermann Liebenthal arrested Johnson at his home "
                 "that afternoon, then told people around town he wouldn't be surprised if Johnson were "
                 "lynched before morning, and went home to sleep. That night, a mob of as many as 75 men "
                 "broke into the jail, beat Johnson severely, and lynched him; a medical examiner concluded "
                 "he had likely died from the beating before the hanging itself. At the coroner's inquest, "
                 "ninety witnesses testified, and the prosecutor, James Steen, pursued the case despite "
                 "being threatened with death \u2014 eliciting testimony suggesting Johnson probably was not "
                 "the rapist at all, since witnesses placed him elsewhere and the accuser's description of "
                 "the attacker's clothing didn't match his. Six men were eventually arrested in connection "
                 "with the lynching; all were released on bail and never prosecuted. Two later confessions "
                 "to the underlying rape, given years apart by different men, left the identity of the "
                 "actual attacker unresolved. Johnson's killing is described as the first lynching in New "
                 "Jersey since the Revolutionary War. A historical marker was dedicated at the site in 2022.",
         known=["Victim identity, background, and the March 5, 1886 date and circumstances, per research by local historian Gary Saretzky, published by the New Jersey Social Justice Remembrance Committee.",
                "Six men were arrested in connection with the lynching but released on bail and never prosecuted, per the same source; inquest testimony suggested Johnson was likely not the actual rapist."],
         unknown=["No one was ever convicted in Johnson's killing.",
                  "The identity of the man who actually assaulted Angelina Herbert was never conclusively established, despite two later, conflicting confessions from other men."],
         unanswered=["What became of the two men, Joseph Anderson and William Kelly, who fled to New York before they could be arrested?",
                     "Why did authorities release all six arrested men on bail without ever bringing the case to trial?",
                     "What did the coroner's rebuke of the local newspaper editor for condoning mob violence lead to, if anything?"],
         extraSources=[src("New Jersey Social Justice Remembrance Committee \u2014 \u201cThe Murder of Mingo Jack\u201d by Gary Saretzky",
                            "https://www.njremembrance.org/about/the-murder-of-mingo-jack", True)]),
    dict(id="jeffery-zolliecoffer", caseNumber="054", name="Jeffery \u201cJo Jo\u201d Zolliecoffer",
         status="unsolved", caseType="homicide", year=1989, age=23, gender="male",
         city="Waterloo", county="Black Hawk", state="IA", caseSeries=None,
         summary="Jeffery \u201cJo Jo\u201d Howard Zolliecoffer, 23, was last seen alive late on the evening "
                 "of September 7, 1989, at Goodies II, a bar formerly on Sumner Street in Waterloo; "
                 "witnesses gave conflicting accounts of whether he left on his own or was forced out by "
                 "several men. He was reported missing on September 9. On September 15, a child playing "
                 "along the Cedar River discovered his body, wrapped in a quilted blanket, bound with "
                 "copper wiring, and weighted down with two cement blocks; police believe it took several "
                 "days for the body to rise to the surface. An autopsy found Zolliecoffer had been shot "
                 "three times, including a fatal shotgun blast to the back of the head. Investigators have "
                 "pursued numerous leads over the years without making an arrest; Zolliecoffer's family has "
                 "been divided over the motive, with some believing it was drug-related and others "
                 "insisting he was firmly against drug use. A $1,500 reward remains active through Cedar "
                 "Valley Crime Stoppers.",
         known=["Victim identity, age, and the September 7\u201315, 1989 timeline, per Iowa Cold Cases and the Iowa Attorney General's cold case files.",
                "No arrests have ever been made in the case, per the same sources.",
                "A news photograph published as part of the 2015 \u201cGone Cold: Exploring Iowa's Unsolved Murders\u201d statewide newspaper project identifies Zolliecoffer."],
         unknown=["Whether Zolliecoffer left the bar willingly or was forced out was never resolved; witness accounts conflicted.",
                  "The motive for the killing remains disputed even within Zolliecoffer's own family."],
         unanswered=["What became of the conflicting witness accounts of Zolliecoffer's final hours at Goodies II?",
                     "What specific leads have Waterloo police pursued over the decades, and why has none led to an arrest?",
                     "What forensic evidence, if any, survives from the recovered blanket, wiring, and cement blocks for modern re-testing?"],
         extraSources=[src("Iowa Cold Cases \u2014 case summary",
                            "https://iowacoldcases.org/case-summaries/jeffery-zolliecoffer/", True),
                        src("Iowa Attorney General's Office \u2014 Unresolved cold case bulletin",
                            "https://www.iowaattorneygeneral.gov/browse/files/8da497e85c2d4d698341ab118d9ab709/embed", True),
                        src("North Platte Telegraph, reprinting \u201cGone Cold\u201d \u2014 \u201cWaterloo murder from 1989 remains unsolved\u201d",
                            "https://nptelegraph.com/news/iowa/article_3addadcd-2852-5014-9994-d697d2bb5f43.html", True)]),
    dict(id="darrion-carrington", caseNumber="055", name="Darrion \u201cPritz\u201d Carrington",
         status="unsolved", caseType="homicide", year=2008, age=18, gender="male",
         city="Boston", county="Suffolk", state="MA", caseSeries=None,
         summary="Darrion \u201cPritz\u201d Carrington, 18, was shot multiple times at close range inside the "
                 "lobby of the Canton House, a fast-food Chinese restaurant on Dorchester Avenue, around "
                 "11:40 p.m. on January 7, 2008, while he waited for a late-night order and talked to a "
                 "friend on his cellphone. He was rushed to Boston Medical Center and died of his wounds the "
                 "next day. Carrington, raised at St. John's Missionary Baptist Church and a regular at the "
                 "Roxbury Boys and Girls Club, had dreamed of playing basketball professionally. The Boston "
                 "Police Department still lists his death among the city's unsolved 2008 homicides; no "
                 "arrest has ever been made. His mother, Natasha Carrington, has since become an advocate "
                 "for other families of unsolved homicide victims through the Louis D. Brown Peace "
                 "Institute. A 2025 analysis by WBUR found that families of Black and Hispanic unsolved "
                 "homicide victims in Massachusetts are more likely than others to be denied basic case "
                 "updates by prosecutors citing open-investigation exemptions, even years after a case has "
                 "gone cold.",
         known=["Victim identity, age, and the January 7\u20138, 2008 date and circumstances, per the Boston Police Department's official unsolved homicides list and contemporaneous news coverage.",
                "No arrest has ever been made in the case, per the same sources."],
         unknown=["No suspect has ever been publicly identified.",
                  "The motive for the shooting was never established in any public account."],
         unanswered=["What specific leads, if any, has the Boston Police Department pursued in the 17 years since the shooting?",
                     "Why have Carrington's family reported difficulty obtaining case updates despite repeated requests?",
                     "What became of the other two unsolved shootings along Dorchester Avenue in the days immediately following Carrington's death?"],
         extraSources=[src("Boston Police Department \u2014 official 2008 Unsolved Homicides list",
                            "https://police.boston.gov/2008-unsolved-homicides/", True),
                        src("Boston 25 News \u2014 \u201cNew England's Unsolved: Who shot and killed Darrion Carrington?\u201d",
                            "https://www.boston25news.com/news/local/new-englands-unsolved-who-shot-killed-darrion-carrington/5KZVGMAUVVAPFA5HOJKPFLPRME/", True)]),
    dict(id="carol-jenkins", caseNumber="056", name="Carol Jenkins",
         status="unsolved", caseType="homicide", year=1968, age=21, gender="female",
         city="Martinsville", county="Morgan", state="IN", caseSeries=None,
         summary="Carol Jenkins, 21, an aspiring fashion model, was stabbed once through the heart with a "
                 "screwdriver on East Morgan Street in Martinsville on the night of September 16, 1968, "
                 "while selling encyclopedias door to door. Jenkins had reported being followed and "
                 "harassed by two white men in a car and sought help at a stranger's home; police searched "
                 "but could not find the vehicle, and Jenkins, not wanting to further inconvenience the "
                 "family who had taken her in, continued on her route. The men returned roughly half an "
                 "hour later; one held her while the other stabbed her. The killing, in a town with a "
                 "longstanding reputation as a \u201csundown town,\u201d went unsolved for more than three "
                 "decades. In 2002, an anonymous letter to police named Kenneth Clay Richmond as the "
                 "killer; his daughter, seven years old at the time of the murder, confirmed she had "
                 "witnessed her father stab Jenkins from the back seat of the family car while a second, "
                 "still-unidentified man held her down, and that her father had paid her seven dollars "
                 "never to speak of it. Richmond was arrested and charged with murder in 2002, but was "
                 "found incompetent to stand trial due to cognitive decline; he died of cancer later that "
                 "year, maintaining his innocence to the end. The second man was never identified.",
         known=["Victim identity, background, and the September 16, 1968 date and circumstances, per PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "Kenneth Clay Richmond was identified in 2002 through his daughter's eyewitness testimony, arrested, and charged with murder, but was found incompetent to stand trial and died later that year before any trial occurred."],
         unknown=["No one was ever convicted in Jenkins's killing.",
                  "The identity of the second man involved in the attack was never established."],
         unanswered=["Who was the second, unidentified man who held Jenkins down during the attack?",
                     "What became of the private investigation Jenkins's stepfather commissioned decades before the 2002 break in the case?",
                     "What specific cognitive decline led the court to find Richmond incompetent to stand trial in 2002?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/carol-jenkins", True),
                        src("African American Registry \u2014 case summary",
                            "https://aaregistry.org/story/the-murder-of-carol-m-jenkins-occurs/", True)]),
    dict(id="john-wesley-wilder", caseNumber="057", name="John Wesley Wilder",
         status="unsolved", caseType="homicide", year=1965, age=32, gender="male",
         city="Ruston", county="Lincoln", state="LA", caseSeries=None,
         summary="John Wesley Wilder, 32, was shot five times and killed by Ruston Police Officer Edward "
                 "Nugent outside a cafe on Jones Street around 2 a.m. on July 17, 1965. Nugent said he "
                 "stopped to question Wilder and another Black man, Billy Williams, after hearing shouting "
                 "from the group; when Wilder allegedly refused to give his name and a struggle followed, "
                 "Nugent drew his pistol and fired. The Ruston Police Department said Wilder had attacked "
                 "Nugent while resisting arrest, and a coroner's inquest \u2014 which the coroner said was "
                 "based on interviews with unidentified officers and three Black witnesses \u2014 ruled the "
                 "shooting justifiable self-defense; no charges were ever filed. Wilder's brother Emzie "
                 "disputed the official account, saying witnesses described only about 15 bystanders "
                 "present, far fewer than police suggested, and warned he would seek help from the NAACP "
                 "and CORE if Ruston authorities failed to act. A 1965 civil suit by Wilder's family did not "
                 "succeed. The FBI reopened the case in 2008 under the Emmett Till Act; after three years, "
                 "during which the Bureau was unable to locate some potential witnesses and others could "
                 "not recall the incident, the case was closed again in 2011 without further action.",
         known=["Victim identity and the July 17, 1965 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "Officer Edward Nugent was never charged; a coroner's inquest ruled the shooting justifiable self-defense, and the DOJ's 2011 review closed the case without further action."],
         unknown=["Whether Wilder actually attacked Nugent, as police claimed, was disputed by his family and community witnesses at the time.",
                  "The exact number of bystanders present, and what they told investigators, was never made fully public."],
         unanswered=["What specific witnesses did the FBI's 2008\u20132011 review attempt to locate, and why were some unreachable?",
                     "What became of the 1965 civil suit Wilder's family brought, and why did it not succeed?",
                     "What records, if any, survive from the original coroner's inquest beyond the brief newspaper account?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/file/892376/dl", True),
                        src("Type Investigations \u2014 \u201cA Death Ruled \u2018Justifiable\u2019: The Killing of John Wesley Wilder\u201d",
                            "https://www.typeinvestigations.org/investigation/2023/07/24/a-death-ruled-justifiable-the-killing-of-john-wesley-wilder/", True)]),
    dict(id="clinton-melton", caseNumber="058", name="Clinton Melton",
         status="unsolved", caseType="homicide", year=1955, age=33, gender="male",
         city="Glendora", county="Tallahatchie", state="MS", caseSeries=None,
         summary="Clinton Melton, 33, a gas station attendant and father of four, was shot and killed at "
                 "the station where he worked in Glendora on December 3, 1955 \u2014 four months after "
                 "Emmett Till was murdered twenty miles away, and in the same county. Melton had argued "
                 "with a white customer, Elmer Otis Kimbell, over how much gas Kimbell had been pumped; a "
                 "witness said Kimbell announced he was going home to get a shotgun and would return to "
                 "kill Melton. The station owner told Melton to leave before Kimbell came back, but Kimbell "
                 "returned first and shot Melton, who was unarmed and sitting in his own car, in the hand "
                 "and head. Kimbell, who was using the car of his close friend J.W. Milam \u2014 one of the "
                 "two men who had killed Till and been acquitted weeks earlier in the same courthouse "
                 "\u2014 was tried for murder before another all-white Tallahatchie County jury and "
                 "acquitted, despite the testimony of witnesses who saw the shooting and a doctor whose "
                 "exam of Kimbell's own wound cast doubt on his self-defense claim. Less than three weeks "
                 "after the shooting and just before the trial, Melton's widow Beulah drowned when her car "
                 "went into Black Bayou with two of their children in the back seat; a family member said "
                 "everyone in the community believed her car had been forced off the road. The DOJ's Civil "
                 "Rights Division reviewed the case decades later and closed it, since Kimbell, by then "
                 "deceased, had already stood trial and been acquitted at the state level.",
         known=["Victim identity, background, and the December 3, 1955 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "Elmer Otis Kimbell was tried for murder and acquitted by an all-white jury; the DOJ's later review closed the case without further action since Kimbell was deceased and had already faced state trial."],
         unknown=["No one was ever convicted in Melton's killing.",
                  "The circumstances of Beulah Melton's fatal car crash, widely believed in the community to have been no accident, were never formally investigated as connected to her husband's case."],
         unanswered=["What specific evidence led the community to believe Beulah Melton's car had been deliberately forced off the road?",
                     "What did the doctor's examination of Kimbell's shoulder wound actually establish about the sequence of the shooting?",
                     "What connection, if any, did Kimbell's presence in J.W. Milam's car that day have to the broader circle involved in Till's murder?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/d9/144_40_2146_melton.pdf", True),
                        src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/clinton-melton/", True)]),
    dict(id="alonzo-tucker", caseNumber="059", name="Alonzo Tucker",
         status="unsolved", caseType="homicide", year=1902, age=28, gender="male",
         city="Coos Bay", county="Coos", state="OR", caseSeries=None,
         summary="Alonzo Tucker, 28, a married boxer who ran a small gym called the School of Physical "
                 "Culture and also worked as a boot black and mail carrier, was lynched in Marshfield "
                 "(now Coos Bay) on September 18, 1902, the day after a white woman accused him of "
                 "assaulting her near the 7th Street bridge. Tucker was arrested without resistance that "
                 "evening, but as word spread, an armed mob of as many as 200 men formed. While being "
                 "moved to keep him from the mob, Tucker escaped and spent the night hiding under the "
                 "town's docks. He was found the next day and shot; the mob then put a noose around his "
                 "neck and began dragging him toward the site of the alleged assault, but he died of his "
                 "wounds along the way. His body was hanged from a light pole on the bridge in broad "
                 "daylight before roughly 300 spectators, none of them masked. Local newspapers described "
                 "the mob approvingly and no one was ever indicted; Coos Bay's small Black community "
                 "largely fled the area afterward out of fear. In 1974, a local newspaper reporter located "
                 "and interviewed three elderly men who had witnessed the lynching as boys; all three said "
                 "they believed Tucker's relationship with his accuser had actually been consensual. It "
                 "remains the only documented lynching of a Black person in Oregon's history. A historical "
                 "marker was dedicated at the site in 2021 following a multi-year memorialization effort.",
         known=["Victim identity, background, and the September 17\u201318, 1902 date and circumstances, per the Equal Justice Initiative's historical marker and the Oregon Remembrance Project.",
                "No one was ever indicted for the lynching; three eyewitnesses interviewed in 1974 said they believed the underlying relationship had been consensual, per the same sources."],
         unknown=["The identities of individual mob members were never formally investigated or prosecuted, despite the lynching occurring in broad daylight before hundreds of unmasked witnesses.",
                  "What became of Tucker's accuser and her family, who left the area for California shortly after the lynching, was never documented."],
         unanswered=["What specific testimony did the three 1974 eyewitnesses give about the night of the lynching?",
                     "What connection, if any, exists between this case and the 1924 killing of Timothy Pettis, another Black Marshfield resident found murdered in the same bay, which prompted the NAACP to publicly declare the town \u201cinfested with the Ku Klux Klan\u201d?",
                     "What additional documentation survives in period newspaper archives beyond the accounts already collected?"],
         extraSources=[src("Equal Justice Initiative \u2014 historical marker, \u201cLynching in Coos County\u201d",
                            "https://www.hmdb.org/m.asp?m=176959", True),
                        src("Oregon Remembrance Project \u2014 case summary",
                            "https://oregonremembrance.org/alonzo-tucker/", True)]),
    dict(id="timothy-pettis", caseNumber="060", name="Timothy Pettis",
         status="unsolved", caseType="homicide", year=1924, age=None, gender="male",
         city="Coos Bay", county="Coos", state="OR", caseSeries=None,
         summary="Timothy Pettis, a Black resident of Marshfield (now Coos Bay) and a veteran of the "
                 "all-Black 24th Infantry Regiment, was murdered and castrated in July 1924; his body was "
                 "left in the waters of Coos Bay, the same body of water where Alonzo Tucker had been "
                 "lynched twenty-two years earlier. Black community members in Marshfield and Portland, "
                 "along with members of the NAACP, believed the Ku Klux Klan was responsible and offered "
                 "rewards for information; the Portland NAACP publicly declared that \u201cMarshfield is "
                 "infested with the Ku Klux Klan.\u201d Oregon is believed to have had the highest "
                 "per-capita Klan membership of any state in the country during the 1920s, with the "
                 "organization's influence reaching into city, county, and state government and law "
                 "enforcement. No one was ever charged in Pettis's killing.",
         known=["Victim identity, background, and the July 1924 date and circumstances, per Oregon Historical Quarterly and OPB's \u201cOregon Experience\u201d documentary.",
                "Black community members and the NAACP publicly attributed the killing to the Klan and offered rewards for information; no one was ever charged, per the same sources."],
         unknown=["No suspect was ever identified or charged in Pettis's death.",
                  "The full circumstances of how Pettis's body came to be found in the bay were not detailed in available public accounts."],
         unanswered=["What specific evidence led Black community members and the NAACP to attribute the killing to the Klan?",
                     "What became of the reward offered for information in the case?",
                     "What connection, if any, exists between this case and the broader pattern of Klan-linked violence documented elsewhere in Coos County during the 1920s?"],
         extraSources=[src("Oregon Historical Quarterly \u2014 \u201cGendering White Supremacy\u201d by Kimberly Jensen",
                            "https://www.ohs.org/oregon-historical-quarterly/upload/Jensen-KKK_OHQ-125_1_spring-2024_web.pdf", True),
                        src("OPB / Oregon Experience \u2014 \u201cOregon's Klan in the 1920s: The Rise of Hate\u201d",
                            "https://www.pbs.org/video/the-rise-of-hate-oregons-klan-in-the-1920s-uotkln/", True)]),
    dict(id="william-harvey", caseNumber="061", name="William \u201cSam Joe\u201d Harvey",
         status="unsolved", caseType="homicide", year=1883, age=35, gender="male",
         city="Salt Lake City", county="Salt Lake", state="UT", caseSeries=None,
         summary="William \u201cSam Joe\u201d Harvey, about 35, an Army veteran who had recently arrived in "
                 "Salt Lake City seeking work and set up a bootblack stand downtown, was lynched by a mob "
                 "of up to 2,000 people on August 25, 1883, hours after his arrest. Harvey had argued with "
                 "the owner of a restaurant over a job offer; when police arrived to investigate, Harvey "
                 "reportedly fired a gun, killing Police Chief Andrew H. Burt and wounding another "
                 "official. Officers took Harvey into custody and beat him severely at police headquarters "
                 "\u2014 striking him, kicking him, and beating him with billy clubs, brass knuckles, and "
                 "shackles \u2014 before a growing mob outside began chanting for him to be handed over. "
                 "The Salt Lake Tribune itself reported at the time that police \u201cgave up their victim "
                 "to the crowd, which proceeded to hang him.\u201d The mob beat Harvey further, hanged him "
                 "from a shed's roof-beam near the jail, and when he tried to hold onto the rope to avoid "
                 "strangling, a mob member kicked his hands loose. After he died, the mob cut down his "
                 "body and dragged it through the streets until the mayor personally intervened and broke "
                 "up the crowd. A coroner's jury convened that same afternoon and, despite the public, "
                 "unmasked lynching, ruled that Harvey died \u201cby means of hanging with a rope by an "
                 "infuriated mob whose names were to the jury unknown.\u201d No one was ever charged, "
                 "including the officers who turned him over.",
         known=["Victim identity, background, and the August 25, 1883 date and circumstances, per the University of Utah's Marriott Library exhibit on racial lynching in Utah, drawing on contemporaneous newspaper accounts and a 1985 academic study of the case.",
                "A coroner's jury the same day ruled Harvey's killers \u201cunknown\u201d despite the lynching occurring in public before an unmasked mob; no one, including the complicit police officers, was ever charged."],
         unknown=["Harvey's exact birth name and background before arriving in Salt Lake City were never reliably documented; a man identifying himself as Harvey's half-brother told a local paper his birth name was Joseph Samuels, a native of Louisiana.",
                  "The identities of individual mob participants, though numbering close to 2,000 and unmasked, were never formally investigated."],
         unanswered=["What became of the police officers who beat Harvey and then handed him to the mob \u2014 were any ever disciplined internally?",
                     "What additional detail might the cited 1985 academic study by Larry Gerlach add beyond what the newspaper record shows?",
                     "What connection, if any, exists between this case and the 1866 killing of Thomas Coleman, an earlier unsolved killing of a Black man in the same city?"],
         extraSources=[src("University of Utah, J. Willard Marriott Library \u2014 \u201cRacial Lynching in Utah\u201d exhibit",
                            "https://exhibits.lib.utah.edu/s/utah-lynching/page/william-sam-joe-harvey", True),
                        src("Utah State Historical Society \u2014 \u201cAfrican Americans and Salt Lake's West Side\u201d",
                            "https://heritageandarts.utah.gov/african-americans-and-salt-lakes-west-side/", True)]),
    dict(id="thomas-coleman", caseNumber="062", name="Thomas Coleman",
         status="unsolved", caseType="homicide", year=1866, age=34, gender="male",
         city="Salt Lake City", county="Salt Lake", state="UT", caseSeries=None,
         summary="Thomas Coleman, about 34, a formerly enslaved man who worked as an attendant at The "
                 "Salt Lake House hotel, was murdered on the night of December 10, 1866, on a hill "
                 "overlooking the city that is now the site of the Utah State Capitol; his body, "
                 "bludgeoned with a large rock and cut across the throat, was found the next morning near "
                 "the U.S. Arsenal. A local newspaper reported Coleman had been \u201cfound in company of a "
                 "white woman\u201d and speculated he was killed in revenge by a rival for her affection, "
                 "framing the murder as retribution for crossing racial lines. A sign left on his body was "
                 "cited by the Daily Union Vedette, a newspaper run by soldiers at nearby Fort Douglas, as "
                 "evidence the killing had been planned in advance; the Vedette openly criticized the "
                 "official investigation as inadequate. A coroner's jury nonetheless concluded that "
                 "\u201csaid murder to the jury are unknown,\u201d and no one was ever held accountable. "
                 "Despite being a member of the church that had once enslaved him, Coleman was buried in a "
                 "pauper's field rather than a standard cemetery plot. In 2022, the University of Utah, the "
                 "Sema Hadithi African American Heritage and Culture Foundation, and the Equal Justice "
                 "Initiative held a joint soil-collection ceremony at Coleman's murder site and at the site "
                 "where William \u201cSam Joe\u201d Harvey was lynched seventeen years later in the same "
                 "city, memorializing both men together.",
         known=["Victim identity, background, and the December 10\u201311, 1866 date and circumstances, per the University of Utah's Marriott Library exhibits \u201cRacial Lynching in Utah\u201d and \u201cCentury of Black Mormons.\u201d",
                "A coroner's jury concluded Coleman's killers were \u201cunknown\u201d despite a contemporary newspaper's own skepticism of the investigation; no one was ever held accountable, per the same sources."],
         unknown=["The identity of the person or people responsible for Coleman's murder was never established.",
                  "Whether the killing was actually motivated by a relationship with a white woman, as one contemporary newspaper speculated, or by some other cause, was never confirmed."],
         unanswered=["What did the sign left on Coleman's body actually say, and what became of it as physical evidence?",
                     "Why did the coroner's jury reach a conclusion of \u201cunknown\u201d despite the Daily Union Vedette's public criticism of the investigation's thoroughness?",
                     "What connection, if any, exists between this case and the 1883 lynching of William \u201cSam Joe\u201d Harvey in the same city?"],
         extraSources=[src("University of Utah, J. Willard Marriott Library \u2014 \u201cRacial Lynching in Utah\u201d exhibit",
                            "https://exhibits.lib.utah.edu/s/utah-lynching/page/thomas-coleman", True),
                        src("University of Utah, J. Willard Marriott Library \u2014 \u201cCentury of Black Mormons\u201d exhibit",
                            "https://exhibits.lib.utah.edu/s/century-of-black-mormons/page/coleman-thomas", True)]),
    dict(id="leonard-mccowin", caseNumber="063", name="Leonard McCowin",
         status="unsolved", caseType="homicide", year=1947, age=21, gender="male",
         city="Center", county="Shelby", state="TX", caseSeries=None,
         summary="Leonard McCowin, 21, a World War II Army veteran who worked on a farm and at a cafe in "
                 "Center, was struck with the butt of a rifle by City Marshal Bryan McCallum on November "
                 "4, 1947, and died of the injury; his death certificate recorded the cause as homicide. A "
                 "contemporaneous Black newspaper reported that McCallum had likely mistaken McCowin for "
                 "his brother, who had recently been beaten by a mob following an altercation with a white "
                 "man. The Shelby County sheriff required only a $2,500 bond from McCallum, and a grand "
                 "jury investigated but declined to indict him; an attorney representing McCowin's family "
                 "reported to the NAACP that jurors felt indicting McCallum \u201cwould give the Negroes too "
                 "much leeway in that community.\u201d The FBI declined to investigate. In April 1948, "
                 "McCowin's father Ezekiel, represented by attorney W.N. Harkness with NAACP support, filed "
                 "a wrongful death civil suit against McCallum, his bondsman, and the city; a district "
                 "court judge dismissed the case that November, reportedly due to a misspelling of "
                 "McCallum's name in the court filing. McCowin's descendants have since sought a historical "
                 "marker at the site; his sister, who was 12 when his body was brought home, was still "
                 "alive as of a 2025 news account.",
         known=["Victim identity, background, and the November 4, 1947 date and circumstances, per the Civil Rights Cold Case Records Review Board's official case file and contemporaneous NAACP investigative correspondence.",
                "City Marshal Bryan McCallum was investigated by a grand jury, which declined to indict him; a subsequent civil suit against him was dismissed in 1948, per the same records and 2025 reporting by Capital B News."],
         unknown=["No one was ever criminally charged or held liable in McCowin's death.",
                  "Whether McCallum genuinely mistook McCowin for his brother, as contemporaneous press reported, or acted for some other reason, was never resolved."],
         unanswered=["What specific reasoning led the grand jury to decline an indictment, beyond the attorney's secondhand account?",
                     "Was the misspelling that led to the 1948 civil suit's dismissal an error, or a deliberate maneuver, and by whom?",
                     "What became of the campaign by McCowin's descendants to have a historical marker placed at the site of his death?"],
         extraSources=[src("Civil Rights Cold Case Records Review Board \u2014 official case file",
                            "https://www.coldcaserecords.gov/content/cases/1947-11-04-leonard-mccowin/", True),
                        src("Capital B News \u2014 \u201cTexas Man's Fight to Move a Lynching Marker Sparks New Battle for Truth\u201d",
                            "https://capitalbnews.org/texas-lynching-marker-black-history/", True)]),
    dict(id="felix-hall", caseNumber="064", name="Felix Hall",
         status="unsolved", caseType="homicide", year=1941, age=19, gender="male",
         city="Fort Benning", county="Chattahoochee", state="GA", caseSeries=None,
         summary="Pvt. Felix Hall, 19, a Black soldier from rural Alabama serving in the segregated 24th "
                 "Infantry Regiment, disappeared at Fort Benning on the afternoon of February 12, 1941, "
                 "after finishing a shift at the base sawmill and telling two friends he was heading to the "
                 "Post Exchange \u2014 the only place on the segregated base where a Black soldier could get "
                 "a hot meal. He never arrived. Six weeks later, an engineer unit found his body hanging "
                 "from a tree in a ravine near the Chattahoochee River, his hands tied behind his back and "
                 "his feet bound with baling wire. A military doctor ruled the death a homicide, but for "
                 "four months the War Department and base authorities publicly suggested to the press that "
                 "Hall may have died by suicide, contradicting their own examiner's finding, until the "
                 "NAACP demanded a real investigation. The FBI and War Department identified suspects, "
                 "including two military men, but never charged anyone, and appear to have ignored a report "
                 "that Hall's white civilian supervisor at the sawmill had threatened to kill him the day "
                 "before he disappeared. It remains the only known lynching to have occurred on a U.S. "
                 "military base. The case went cold until 2014, when Northeastern University students began "
                 "investigating it, leading to a 2016 Washington Post exposé built on a previously "
                 "undisclosed 130-page FBI file. In 2021, the Army dedicated a memorial plaque at Fort "
                 "Benning; the plaque itself states that Hall's death was among the events that helped "
                 "convince President Truman to order the full integration of the U.S. armed forces in 1948.",
         known=["Victim identity, background, and the February 12\u2013March 28, 1941 timeline, per the Washington Post's 2016 investigation and the U.S. Army's 2021 memorial plaque text.",
                "A military doctor ruled Hall's death a homicide; the FBI and War Department identified suspects but never charged anyone, per the same sources."],
         unknown=["No one was ever charged or convicted in Hall's killing.",
                  "Why the FBI and War Department did not pursue the reported threat from Hall's civilian supervisor, or fully investigate the two military suspects identified, was never explained in the released case file."],
         unanswered=["What additional detail does the full 130-page FBI file, first disclosed by the Washington Post in 2016, contain that has not yet been publicly analyzed?",
                     "What became of the two military suspects the FBI identified but never charged?",
                     "What connection did Army and War Department officials at the time see, if any, between Hall's case and the broader pattern of violence against Black servicemen during the era?"],
         extraSources=[src("The Washington Post \u2014 \u201cThe story of the only known lynching on a U.S. military base in American history\u201d",
                            "https://www.washingtonpost.com/sf/national/2016/09/02/the-story-of-the-only-known-lynching-on-a-u-s-military-base/", True),
                        src("Army Times \u2014 \u201cFort Benning memorializes Black soldier lynched in 1941\u201d",
                            "https://www.armytimes.com/news/your-army/2021/08/03/fort-benning-memorializes-black-soldier-lynched-80-years-ago-as-post-awaits-renaming-effort/", True)]),
    dict(id="dan-carter-sanders", caseNumber="065", name="Dan Carter Sanders",
         status="unsolved", caseType="homicide", year=1946, age=26, gender="male",
         city="Cleveland Township", county="Johnston", state="NC", caseSeries=None,
         summary="Dan Carter Sanders, 26, a married World War II veteran, was shot and killed on November "
                 "18, 1946, after a group of white men in Cleveland Township accused him and another man "
                 "of stealing foxhounds from a local farm. The DOJ's file identifies the shooter as Robert "
                 "\u201cBobby\u201d H. Johnson Jr., who was 16 years old at the time, and names his father, "
                 "Robert H. Johnson Sr., along with three other men present, Russell Hatcher, Lester "
                 "Phillips, and R.H. Stephenson, as subjects. No federal hate-crime law existed in 1946, "
                 "and the statute of limitations on any potential criminal case had long since expired by "
                 "the time the DOJ reviewed the case decades later; the Department also declined to refer "
                 "the matter to North Carolina for state prosecution, citing the lack of any living "
                 "subjects or likely surviving witnesses. All five men named in the file were deceased by "
                 "the time it was closed on March 5, 2019.",
         known=["Victim identity, background, and the November 18, 1946 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "The DOJ's file names five subjects, including the 16-year-old shooter, all reported deceased by the time of the 2019 closure; no one was ever charged."],
         unknown=["No criminal charges were ever filed against anyone in Sanders's death.",
                  "Whether the underlying accusation of stealing foxhounds had any factual basis was never established."],
         unanswered=["What became of the local investigation, if any, conducted in 1946 at the time of the killing?",
                     "Why the DOJ's file lists five named subjects present but does not specify each individual's role in the shooting itself.",
                     "What, if any, records survive documenting how the incident was reported or discussed locally at the time?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/dan-carter-sanders/", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/dan-carter-sanders-notice-close-file", True)]),
    dict(id="charles-brown", caseNumber="066", name="Charles Brown",
         status="unsolved", caseType="homicide", year=1957, age=20, gender="male",
         city="Benton", county="Yazoo", state="MS", caseSeries=None,
         summary="Charles Brown, 20, a Black U.S. Air Force airman home on a month-long leave, was fatally "
                 "shot in the heart at close range on June 18, 1957, while sitting at the dinner table of a "
                 "neighboring family in Benton. He had accepted a dinner invitation from a white woman he "
                 "had long known; her brother, 50-year-old farmer Raiford Walton, left the house, returned "
                 "with a shotgun, and shot Brown, later telling investigators he believed Brown had "
                 "gotten \u201ctoo friendly\u201d with his sister while he was out of town. Walton, who had a "
                 "prior manslaughter conviction for killing his own son-in-law, called the police himself "
                 "after the shooting and admitted to it; murder charges were filed, but a local grand jury "
                 "declined to indict him. When the FBI reopened the case decades later under the Emmett "
                 "Till Act, one witness alleged Walton had actually planned the killing in advance, luring "
                 "Brown to the house after catching him \u201cin some action\u201d beforehand \u2014 though "
                 "this could not be independently corroborated. Walton died in 1965, and the case was "
                 "formally closed in 2010.",
         known=["Victim identity, background, and the June 18, 1957 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "Raiford Walton admitted to the shooting and was charged with murder, but a local grand jury declined to indict him, per the same sources."],
         unknown=["No one was ever convicted in Brown's death despite the shooter's own admission.",
                  "Whether Walton planned the killing in advance, as one witness later alleged to the FBI, was never independently corroborated."],
         unanswered=["What specific evidence or testimony led the 1957 grand jury to decline an indictment despite Walton's admission?",
                     "What became of the witness who told the FBI decades later that Walton had planned the killing, and what more did they know?",
                     "Why did no local or state authority maintain surviving records of the case by the time of the FBI's 2008 review?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/charles-brown/", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/charles-brown", True)]),
    dict(id="willie-countryman", caseNumber="067", name="Willie Countryman",
         status="unsolved", caseType="homicide", year=1958, age=32, gender="male",
         city="Dawson", county="Terrell", state="GA", caseSeries=None,
         summary="Willie \u201cWootie\u201d Countryman, 32, a Black Army veteran and truck driver, was shot "
                 "and killed in his own backyard in Dawson just after 1:30 a.m. on May 25, 1958. Dawson "
                 "Police officers Weyman Cherry and Robert Hancock said they had entered Countryman's yard "
                 "to investigate a noise, and claimed Countryman attacked Cherry with a knife; Cherry shot "
                 "him in the stomach, and he died at the hospital. Countryman's girlfriend, who had been "
                 "talking with him moments before, and other family and friends disputed the officers' "
                 "account at every point. A coroner's inquest the next day acquitted Cherry, ruling he had "
                 "acted in self-defense. It was Cherry's second fatal or near-fatal use of force against a "
                 "Black resident within a matter of weeks \u2014 he had fatally beaten another Black man, "
                 "James Brazier, about a month earlier, and would go on to serve as Dawson's police chief "
                 "for a decade afterward. Terrified Black residents organized under the name \u201cLaw, "
                 "Justice, Order\u201d and sent an urgent plea for outside help, writing, \u201cWe can't hold "
                 "these people much longer.\u201d The FBI investigated but found no living subjects by the "
                 "time of a later federal review, and the case was formally closed in 2009.",
         known=["Victim identity, background, and the May 25, 1958 date and circumstances, per the DOJ's public case file, the Georgia Civil Rights Cold Cases Project at Emory University, and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "A coroner's inquest acquitted Officer Weyman Cherry the day after the shooting, ruling it self-defense; the same officer had fatally beaten another Black man about a month earlier, per the same sources."],
         unknown=["No one was ever criminally held accountable for Countryman's death.",
                  "Countryman's girlfriend and other community members directly disputed the officers' account of the confrontation, and that conflict was never resolved through any trial."],
         unanswered=["What became of the James Brazier case, the fatal beating by the same officer roughly a month earlier?",
                     "Why was Cherry permitted to remain on the force, and later become police chief, despite two fatal or near-fatal incidents with Black residents in such close succession?",
                     "What response, if any, did the FBI give to the Law, Justice, Order group's urgent 1958 appeal for help?"],
         extraSources=[src("Georgia Civil Rights Cold Cases Project, Emory University \u2014 case summary",
                            "https://coldcases.emory.edu/willie-countryman/", True),
                        src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/willie-countryman", True)]),
    dict(id="donald-raspberry", caseNumber="068", name="Donald Raspberry",
         status="unsolved", caseType="homicide", year=1965, age=19, gender="male",
         city="Okolona", county="Chickasaw", state="MS", caseSeries=None,
         summary="Donald Raspberry, 19, was shot and killed inside the home of his employer, Garland H. "
                 "\u201cDick\u201d Anderson, in Okolona on February 27, 1965. Anderson said he had come to "
                 "suspect someone was breaking into his house and stayed home that day to catch the thief; "
                 "he claimed that when Raspberry removed a window screen and entered, he shot him in "
                 "self-defense. Anderson was the only known witness to the shooting. He was charged by the "
                 "state, and at a preliminary hearing in Chickasaw County Justice Court a week later, he "
                 "maintained his self-defense account. No further prosecution followed. The DOJ's Civil "
                 "Rights Division reviewed the case decades later and closed it in 2010 after determining "
                 "Anderson had since died.",
         known=["Victim identity and the February 27, 1965 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "Garland Anderson was charged by the state and gave a self-defense account at a preliminary hearing; no further prosecution occurred, per the same sources."],
         unknown=["Whether Anderson's account of Raspberry breaking into the house was accurate was never tested at trial.",
                  "Why the case did not proceed beyond the preliminary hearing stage was not fully documented in the available record."],
         unanswered=["What became of the case after the March 1965 preliminary hearing, and why did it not advance further?",
                     "What did the removed back porch window screen, cited as evidence of a break-in, actually indicate about the sequence of events?",
                     "What additional local investigative records, if any, survive from 1965?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/donald-raspberry/", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/donald-raspberry-notice-close-file", True)]),
    dict(id="william-henry-lee", caseNumber="069", name="William Henry Lee",
         status="unsolved", caseType="homicide", year=1965, age=None, gender="male",
         city="Goshen Springs", county="Rankin", state="MS", caseSeries=None,
         summary="William Henry Lee was last seen leaving his job at the Storkline Factory in Jackson at "
                 "11:30 p.m. on February 24, 1965, during a night of rain and snow, on his way home to "
                 "Goshen Springs roughly an hour away. He never arrived; his body was found beside a road "
                 "the following afternoon, fully clothed with only a small amount of blood on his lip and "
                 "no other visible injury. A flashlight matching one Lee normally kept in his car was found "
                 "nearby. The Rankin County Sheriff's Department moved his car before it could be examined "
                 "for evidence, and his body was embalmed after only a 15-minute coroner's inquest, before "
                 "any autopsy could be performed. A civil rights organization later complained that a "
                 "second autopsy, conducted after embalming, listed the cause of death as strangulation, "
                 "likely from inhaling gasoline \u2014 a finding that conflicted with the original "
                 "examiner's report of no visible injury. The complaint also noted that Lee had attended "
                 "civil rights meetings. Neither the original local investigation nor a later FBI inquiry "
                 "found evidence of a civil rights violation, and the case was closed without identifying a "
                 "suspect.",
         known=["Victim identity and the February 24\u201325, 1965 timeline, per the DOJ's public case file.",
                "A civil rights organization's contemporaneous complaint alleged investigative failures, including the car being moved before evidence collection and embalming occurring before a full autopsy, per the same file."],
         unknown=["The cause of death itself is disputed between two conflicting post-mortem examinations.",
                  "No suspect was ever identified in the case."],
         unanswered=["Why do the two post-mortem examinations \u2014 one finding no visible injury, the other citing strangulation from gasoline inhalation \u2014 conflict so directly?",
                     "What specifically happened to Lee between leaving his job at 11:30 p.m. and his body being found the next afternoon?",
                     "What became of the Scott County Movement's April 1965 complaint requesting a federal investigation?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/william-henry-lee-notice-close-file", True)]),
    dict(id="ed-smith", caseNumber="070", name="Ed Smith",
         status="unsolved", caseType="homicide", year=1958, age=None, gender="male",
         city="State Line", county="Wayne", state="MS", caseSeries=None,
         summary="Ed Smith was fatally shot in the chest in the front yard of his own home in State Line "
                 "on April 27, 1958, by his neighbor, Lawrence David Clark. Smith's wife, Daisy Bell "
                 "Smith, witnessed the shooting. The NAACP's Medgar Evers personally urged prosecution. "
                 "Clark was arrested, and at a preliminary hearing was released on a $5,000 bond pending a "
                 "grand jury hearing. Two weeks later, a local grand jury declined to indict him. According "
                 "to contemporaneous news reports, Clark later bragged openly about the shooting. He died "
                 "in 1992, decades before the DOJ formally closed the file in 2009.",
         known=["Victim identity and the April 27, 1958 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "Lawrence David Clark was arrested and released on bond, but a grand jury declined to indict him two weeks later; contemporaneous reports say he later bragged about the killing, per the same sources."],
         unknown=["No one was ever convicted in Smith's death.",
                  "The specific underlying dispute between Smith and Clark, as neighbors, was never fully documented in the surviving record."],
         unanswered=["What specific evidence or testimony led the 1958 grand jury to decline an indictment despite an eyewitness?",
                     "What became of Medgar Evers's personal involvement in pushing for prosecution?",
                     "What did the contemporaneous reports of Clark \u201cbragging\u201d about the shooting actually describe, and who reported them?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/ed-smith/", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/ed-smith-notice-close-file", True)]),
    dict(id="lamar-smith", caseNumber="071", name="Lamar Smith",
         status="unsolved", caseType="homicide", year=1955, age=63, gender="male",
         city="Brookhaven", county="Lincoln", state="MS", caseSeries=None,
         summary="Lamar \u201cDitney\u201d Smith, 63, a World War I veteran, farmer, and voter registration "
                 "organizer with the Regional Council of Negro Leadership, was shot to death on the lawn of "
                 "the Lincoln County courthouse in Brookhaven at around 10 a.m. on August 13, 1955, while "
                 "helping other Black residents complete absentee ballots ahead of a runoff election. He "
                 "was killed in broad daylight before dozens of witnesses, including the local sheriff, who "
                 "watched a blood-covered white man walk away from the scene without arresting him; it "
                 "took eight days before three white men \u2014 Noah Smith, Mack Smith, and Charles Falvey "
                 "\u2014 were arrested. A state grand jury heard from as many as 75 witnesses in September "
                 "1955 but adjourned without returning any indictment, after witnesses who had stood within "
                 "30 feet of the killing told the panel they had seen nothing. Decades later, an FBI "
                 "interview suggested Smith may have been deliberately lured to the courthouse. Smith's "
                 "killing was cited in the NAACP's own 1955 pamphlet documenting racial violence in "
                 "Mississippi, alongside the killings of Rev. George Lee and Emmett Till. The Mississippi "
                 "Department of Archives and History approved a historical marker for Smith in 2026.",
         known=["Victim identity, background, and the August 13, 1955 date and circumstances, per the DOJ's public case file, PBS FRONTLINE's \u201cUn(re)solved\u201d case summary, and the Equal Justice Initiative.",
                "Three men were arrested but never indicted after a September 1955 grand jury heard dozens of witnesses and adjourned without action, per the same sources."],
         unknown=["No one was ever convicted in Smith's killing.",
                  "Whether Smith was deliberately lured to the courthouse, as one witness later suggested to the FBI decades afterward, was never independently confirmed."],
         unanswered=["Why did dozens of witnesses who stood close to the killing tell the grand jury they saw nothing?",
                     "What became of the local notary public who said he was warned to stop assisting Black voters \u201clest he wind up like Ditney Smith\u201d?",
                     "What additional detail does Keith Beauchamp's documentary film on the case add beyond the official record?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/lamar-smith", True),
                        src("Equal Justice Initiative \u2014 case summary",
                            "https://calendar.eji.org/racial-injustice/aug/13", True)]),
    dict(id="joseph-dumas", caseNumber="072", name="Joseph Dumas",
         status="unsolved", caseType="homicide", year=1962, age=19, gender="male",
         city="Perry", county="Taylor", state="FL", caseSeries=None,
         summary="Joseph Dumas, 19, was fatally shot by Taylor County Constable Henry Sauls during a "
                 "traffic stop on May 5, 1962. Dumas's own family members, who witnessed the shooting, told "
                 "investigators that Sauls shot him in the back while Dumas stood still with his hands "
                 "raised. Sauls gave a different account, saying he was removing a switchblade from Dumas's "
                 "pocket when Dumas lunged at him and the gun discharged accidentally. A local grand jury "
                 "declined to indict Sauls later that year, but he was separately tried in federal court "
                 "under the federal civil rights statute and acquitted in September 1962. Sauls died in "
                 "1974. The DOJ's Civil Rights Division reopened the case under its Cold Case Initiative in "
                 "2008 and closed it again in 2010.",
         known=["Victim identity and the May 5, 1962 date and circumstances, per the DOJ's public case file.",
                "Constable Henry Sauls was tried in federal court under 18 U.S.C. \u00a7 242 and acquitted in September 1962, after a local grand jury had already declined to indict him, per the same file."],
         unknown=["No one was ever convicted in Dumas's death despite two separate legal proceedings.",
                  "The directly conflicting accounts \u2014 Dumas's family describing an execution-style shooting of a compliant, unarmed man, versus Sauls's claim of an accidental discharge during a struggle \u2014 were never resolved."],
         unanswered=["What specific evidence was presented at the 1962 federal trial that led to Sauls's acquittal?",
                     "What became of the switchblade Sauls said he was removing from Dumas's pocket at the time of the shooting?",
                     "What additional detail, if any, survives in Taylor County's own local investigative records from 1962?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/file/949606/dl", True)]),
    dict(id="vincent-dahmon", caseNumber="073", name="Vincent Dahmon",
         status="unsolved", caseType="homicide", year=1966, age=65, gender="male",
         city="Natchez", county="Adams", state="MS", caseSeries=None,
         summary="Vincent Dahmon, 65, of Natchez, was shot and killed by Ku Klux Klan members during the "
                 "period of the 1966 \u201cMarch Against Fear,\u201d the roughly 220-mile walk from Memphis, "
                 "Tennessee to Jackson, Mississippi that James Meredith began to encourage Black voter "
                 "registration and that continued after he was shot and wounded on its second day. Dahmon's "
                 "killing first came to the FBI's attention not through a contemporaneous police "
                 "investigation, but through a 1966 article by Lincoln Lynch, then a national director of "
                 "the Congress of Racial Equality, describing it to fellow CORE members. No specific "
                 "suspects were ever identified. When the DOJ's Civil Rights Division reopened the case "
                 "decades later, the FBI contacted Mississippi state agencies, the Southern Poverty Law "
                 "Center, the NAACP, the Mississippi Crime Laboratory, and local newspapers, and issued a "
                 "public press release seeking information; nothing further surfaced, and the case was "
                 "closed in 2010.",
         known=["Victim identity and the general 1966 timeframe of the killing, per the DOJ's public case file, drawing on a contemporaneous CORE publication.",
                "No suspects were ever identified, despite an extensive later FBI outreach campaign including a public press release, per the same file."],
         unknown=["No specific date, location details, or suspects for the killing were ever documented beyond the general connection to the March Against Fear.",
                  "Why local law enforcement at the time did not generate any investigative record that survived to the DOJ's later review was never explained."],
         unanswered=["What additional detail, if any, does the original 1966 CORE article by Lincoln Lynch contain beyond what the DOJ's file cites?",
                     "Why did contemporaneous Natchez or Adams County authorities apparently keep no investigative record of the killing?",
                     "What connection, if any, exists between this case and the broader wave of Klan violence in the Natchez area documented elsewhere in this archive, including the Silver Dollar Group's activities in the same period?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/file/953461/dl", True)]),
    dict(id="jimmie-lee-jackson", caseNumber="074", name="Jimmie Lee Jackson",
         status="unsolved", caseType="homicide", year=1965, age=26, gender="male",
         city="Marion", county="Perry", state="AL", caseSeries=None,
         summary="Jimmie Lee Jackson, 26, was fatally shot in the abdomen by Alabama State Trooper James "
                 "Bonard Fowler on the night of February 18, 1965, in Marion, after state troopers broke up "
                 "a nighttime civil rights march and chased demonstrators into nearby businesses. Jackson "
                 "had gone into a caf\u00e9 trying to protect his mother and elderly grandfather from being "
                 "beaten by troopers when he was shot at close range; he died eight days later of an "
                 "abdominal infection from the wound. Fowler was not charged for more than four decades, "
                 "until a grand jury indicted him for murder in 2007. In 2010, he pleaded guilty to the "
                 "lesser charge of manslaughter and served roughly six months in jail \u2014 the only "
                 "conviction the Emmett Till Act's cold case review process has produced since the law was "
                 "signed in 2008. Jackson's death directly inspired the Selma to Montgomery march that "
                 "began three weeks later, which state troopers violently broke up on the Edmund Pettus "
                 "Bridge in an event that became known as Bloody Sunday.",
         known=["Victim identity and the February 18\u201326, 1965 date and circumstances, per the DOJ's public case file and extensive contemporaneous and historical reporting.",
                "James Bonard Fowler was indicted for murder in 2007 and pleaded guilty to manslaughter in 2010, serving roughly six months \u2014 the only conviction the Emmett Till Act's review process has produced to date."],
         unknown=["Why Fowler was never charged for more than four decades after the shooting was never fully explained in the public record.",
                  "The full circumstances inside the caf\u00e9 in the moments before the shooting were disputed between Fowler's account and witness statements."],
         unanswered=["Why did it take until 2007 for a grand jury to indict Fowler, and what specific new evidence or pressure led to that outcome?",
                     "What connection does Jackson's death have to the broader chain of events, including Bloody Sunday, that followed three weeks later?",
                     "What became of the other troopers present at the caf\u00e9 that night, and were any of them ever investigated?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/jimmie-lee-jackson-notice-close-file", True)]),
    dict(id="thomas-brewer", caseNumber="075", name="Dr. Thomas Brewer",
         status="unsolved", caseType="homicide", year=1956, age=None, gender="male",
         city="Columbus", county="Muscogee", state="GA", caseSeries=None,
         summary="Dr. Thomas Brewer, a prominent Black physician and founder of the Columbus NAACP "
                 "chapter, was fatally shot on the evening of February 18, 1956, inside the F&B Department "
                 "Store owned by Luico Flowers. Tension between the two men had been building for years; "
                 "Brewer had asked Flowers to report a white police officer's arrest of a Black man in "
                 "front of Flowers's store as excessive force, which Flowers refused to do, and Brewer had "
                 "separately threatened to organize a boycott of the store after Flowers declined to "
                 "support a candidate Brewer favored in a city commission race. Flowers said he shot Brewer "
                 "when Brewer reached into his pocket as though drawing a gun. The shooting was "
                 "investigated locally by the Columbus Police Department and presented to a Muscogee "
                 "County grand jury. No one was ever convicted.",
         known=["Victim identity, background, and the February 18, 1956 date and circumstances, per the DOJ's public case file.",
                "Luico Flowers acknowledged shooting Brewer and claimed self-defense; the matter was presented to a local grand jury, per the same file."],
         unknown=["Whether Brewer actually reached for a weapon, as Flowers claimed, was never resolved.",
                  "The specific outcome of the Muscogee County grand jury's review of the case was not detailed in the available public record."],
         unanswered=["What testimony did the grand jury actually hear, and why did it not result in an indictment?",
                     "What became of the underlying police brutality complaint Brewer had asked Flowers to help report?",
                     "What connection, if any, existed between this case and the broader campaign against NAACP organizing in Georgia during the period?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/thomas-brewer-notice-close-file", True)]),
    dict(id="ernest-jells", caseNumber="076", name="Ernest Jells",
         status="unsolved", caseType="homicide", year=1963, age=21, gender="male",
         city="Clarksdale", county="Coahoma", state="MS", caseSeries=None,
         summary="Ernest Jells, 21, was shot and killed by Clarksdale Police Department Lieutenant Henry "
                 "Petty and Patrolman B.F. Moore Jr. on September 20, 1963. According to contemporaneous "
                 "local newspaper coverage, Jells had been accused of trying to steal bananas from a "
                 "grocery store; the store owner's son confronted him and a scuffle followed, during which "
                 "officers said Jells reached back as though to grab a weapon. No one was ever charged in "
                 "connection with his death. The DOJ's Civil Rights Division closed the case in 2010, after "
                 "confirming both officers were deceased.",
         known=["Victim identity and the September 20, 1963 date and circumstances, per the DOJ's public case file, drawing on contemporaneous Clarksdale Press Register coverage.",
                "No one was ever charged in Jells's death; both officers involved were confirmed deceased by the time of the DOJ's 2010 closure, per the same file."],
         unknown=["Whether Jells actually reached for a weapon, as the officers claimed, was never independently confirmed.",
                  "The full circumstances of the confrontation inside the store before Jells was shot were not fully documented beyond the officers' own account."],
         unanswered=["What did the store owner's son's account of the initial confrontation actually establish?",
                     "Why no formal charges were ever pursued against either officer at the time?",
                     "What additional local investigative or coroner's records, if any, survive from 1963?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/ernest-jells-notice-close-file", True)]),
    dict(id="benjamin-brown", caseNumber="077", name="Benjamin Brown",
         status="unsolved", caseType="homicide", year=1967, age=None, gender="male",
         city="Jackson", county="Hinds", state="MS", caseSeries=None,
         summary="Benjamin Brown was fatally shot during unrest connected to a civil rights protest in "
                 "Jackson on May 11, 1967. Initial eyewitnesses identified Jackson Police Department Major "
                 "Anthony \u201cBuddy\u201d Kane Sr. as the shooter, while other witnesses said the shooters "
                 "were not in police uniform but wearing white shirts, pointing toward Mississippi Highway "
                 "Safety Patrol detectives who were also on the scene that night. A later ballistics "
                 "analysis found that the buckshot pellets recovered from Brown's fatal head wound and body "
                 "matched ammunition used by the Highway Safety Patrol, not the type carried by Jackson "
                 "police, leading investigators to conclude decades later that Brown's shooter was most "
                 "likely a Highway Safety Patrol officer rather than a city officer, effectively clearing "
                 "the originally accused JPD officers. No one was ever charged, and all identified subjects "
                 "were confirmed deceased by the time the DOJ closed the case.",
         known=["Victim identity and the May 11, 1967 date and circumstances, per the DOJ's public case file.",
                "A later ballistics analysis of the recovered buckshot pointed toward a Mississippi Highway Safety Patrol officer rather than the Jackson Police Department officer originally accused by eyewitnesses, per the same file; no one was ever charged."],
         unknown=["The specific individual who fired the fatal shot was never conclusively identified, despite the ballistics analysis narrowing the likely agency involved.",
                  "Why witnesses' original identification of a Jackson police officer as the shooter conflicted so directly with the later ballistics findings was never fully resolved."],
         unanswered=["Who were the Mississippi Highway Safety Patrol officers present at the scene the ballistics analysis pointed toward, and were any of them ever directly questioned?",
                     "What became of the original 1967 Jackson Police Department investigation before it was reopened decades later?",
                     "What broader protest or unrest was occurring in Jackson that night, and what connection did it have to the citywide tensions of the period?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/benjamin-brown-notice-close-file", True)]),
    dict(id="larry-payne", caseNumber="078", name="Larry Payne",
         status="unsolved", caseType="homicide", year=1968, age=16, gender="male",
         city="Memphis", county="Shelby", state="TN", caseSeries=None,
         summary="Larry Payne, 16, was fatally shot with a shotgun by a Memphis police officer on the "
                 "afternoon of March 28, 1968, during widespread unrest connected to the city's sanitation "
                 "workers' strike \u2014 the same strike that had brought Martin Luther King Jr. to Memphis, "
                 "where he was assassinated exactly one week later. Payne had been seen removing "
                 "televisions from a Sears store amid the disorder; an officer pursued him on foot to a "
                 "housing complex, where Payne entered a basement boiler room. The officer said that when "
                 "Payne partially opened the door, he raised one hand but kept a knife in his lowered other "
                 "hand, and that he fired in self-defense, striking Payne once in the abdomen. Hours "
                 "earlier, Payne had been photographed elsewhere in the city watching an officer strike his "
                 "friend with a baton. A large, hostile crowd gathered at the scene of the shooting. No one "
                 "was ever charged.",
         known=["Victim identity and the March 28, 1968 date and circumstances, per the DOJ's public case file.",
                "No criminal charges were ever filed against the officer involved, per the same file."],
         unknown=["Whether Payne actually held a knife in a threatening manner, as the officer claimed, was never independently tested at trial.",
                  "The full sequence of events inside the boiler room, witnessed only by Payne and the officer, was never independently corroborated."],
         unanswered=["What became of the photograph taken of Payne hours before the shooting, and what broader context does it provide about that day's unrest?",
                     "What connection, if any, did local officials at the time draw between this shooting and the escalating tensions that preceded Dr. King's assassination one week later?",
                     "What internal Memphis Police Department review, if any, followed the shooting?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/larry-payne-notice-close-file", True)]),
    dict(id="herbert-lee", caseNumber="079", name="Herbert Lee",
         status="unsolved", caseType="homicide", year=1961, age=52, gender="male",
         city="Liberty", county="Amite", state="MS", caseSeries=None,
         summary="Herbert Lee, 52, a farmer and NAACP voter-registration organizer who worked closely "
                 "with SNCC activist Bob Moses, was shot and killed at Westbrook's Cotton Gin in Liberty on "
                 "September 25, 1961, by Mississippi state representative E.H. Hurst. Hurst said the two "
                 "men argued over a debt and that Lee swung a tire iron at him, prompting Hurst to strike "
                 "him with a pistol, which discharged and killed him. A coroner's inquest, held inside the "
                 "cotton gin office within an hour of the shooting, found Hurst acted in self-defense; "
                 "witnesses, including Lee's friend Louis Allen, corroborated Hurst's account under oath. "
                 "Two justices of the peace subsequently declined to send the case to a grand jury, and "
                 "Hurst was released the same day he was charged. Louis Allen later told the FBI he had "
                 "lied at the inquest out of fear, and that Lee had not actually threatened Hurst. Allen "
                 "was harassed for years afterward and was murdered in 1964, shortly before he planned to "
                 "leave Mississippi \u2014 a killing documented separately in this archive.",
         known=["Victim identity, background, and the September 25, 1961 date and circumstances, per the DOJ's public case file.",
                "A coroner's inquest and two justices of the peace concluded Hurst acted in self-defense and declined to refer the case to a grand jury; the corroborating witness, Louis Allen, later told the FBI he had lied out of fear, per the same file."],
         unknown=["Whether Lee actually threatened Hurst with a tire iron, as multiple witnesses testified under oath at the time, was directly contradicted by at least one of those same witnesses years later.",
                  "No one was ever convicted in Lee's death."],
         unanswered=["What specifically caused Louis Allen to recant his corroborating testimony to the FBI, and what protection, if any, was he offered in exchange?",
                     "What connection exists between this case and Louis Allen's own unsolved 1964 murder, committed after he began cooperating with federal investigators?",
                     "What became of the other witnesses who testified alongside Allen at the original 1961 inquest?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/herbert-lee", True)]),
    dict(id="samuel-younge-jr", caseNumber="080", name="Samuel Younge Jr.",
         status="unsolved", caseType="homicide", year=1966, age=21, gender="male",
         city="Tuskegee", county="Macon", state="AL", caseSeries=None,
         summary="Samuel Younge Jr., 21, a Navy veteran, civil rights activist, and freshman at Tuskegee "
                 "Institute, was fatally shot beneath the left eye by 68-year-old gas station attendant "
                 "Marvin Segrest just before midnight on January 3, 1966, after an argument over Younge's "
                 "use of a whites-only restroom. Segrest was arrested the next day, indicted for "
                 "second-degree murder by a Macon County grand jury, and released on $20,000 bond. His "
                 "shooting set off a demonstration in Tuskegee attended by roughly 2,000 students and "
                 "faculty. At trial in December 1966, forensic testimony indicated the fatal shot had been "
                 "fired from several feet away, contradicting any claim of a close struggle. An all-white "
                 "jury in Lee County acquitted Segrest after deliberating for 71 minutes.",
         known=["Victim identity, background, and the January 3, 1966 date and circumstances, per the DOJ's public case file.",
                "Marvin Segrest was indicted for second-degree murder and tried, but was acquitted by an all-white jury after 71 minutes of deliberation in December 1966, per the same file."],
         unknown=["No one was ever convicted in Younge's death.",
                  "The medical examiner's finding that the fatal shot came from several feet away was never reconciled with any account of a close physical struggle."],
         unanswered=["What specific evidence or arguments led the jury to acquit despite the forensic distance findings?",
                     "What became of the roughly 2,000-person demonstration's broader effect on civil rights organizing at Tuskegee Institute?",
                     "What additional trial transcript detail, if any, has been preserved beyond the summary in the DOJ's file?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/marvin-l-segrest-samuel-l-younge-jr-notice-close-file", True)]),
    dict(id="isaiah-taylor", caseNumber="081", name="Isaiah Taylor",
         status="unsolved", caseType="homicide", year=1964, age=None, gender="male",
         city="Ruleville", county="Sunflower", state="MS", caseSeries=None,
         summary="Isaiah Taylor, who had a documented history of mental health problems, was shot and "
                 "killed on the side of Highway 49 near Ruleville on the afternoon of June 26, 1964, by "
                 "Mississippi Highway Patrol Patrolman Robert Wallace. Wallace said he and a local constable "
                 "were searching for an escaped state penitentiary inmate when they came upon Taylor "
                 "standing beside the road, covering his face with his hands. According to Wallace's "
                 "account, when he approached and questioned him, a confrontation followed that ended in "
                 "the shooting. No independent civilian witnesses to the encounter were ever identified. "
                 "No charges were ever filed against Wallace, and the case was closed decades later after "
                 "the DOJ determined both Wallace and the constable present were deceased.",
         known=["Victim identity and the June 26, 1964 date and circumstances, per the DOJ's public case file.",
                "No independent civilian witnesses to the shooting were ever identified, and no charges were filed against Patrolman Robert Wallace, per the same file."],
         unknown=["The specific sequence of events between Wallace's approach and the shooting itself rests entirely on Wallace's own account.",
                  "Whether Taylor's documented mental health history played any role in the encounter was never independently examined."],
         unanswered=["What became of the escaped penitentiary inmate Wallace and the constable were reportedly searching for that day?",
                     "Why were no independent witnesses to the roadside encounter ever located, given the highway setting?",
                     "What internal Mississippi Highway Patrol review, if any, followed the shooting?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/file/950762/dl", True)]),
    dict(id="maceo-snipes", caseNumber="082", name="Maceo Snipes",
         status="unsolved", caseType="homicide", year=1946, age=37, gender="male",
         city="Butler", county="Taylor", state="GA", caseSeries=None,
         summary="Maceo Snipes, 37, a World War II veteran who had fought in New Guinea, was shot in the "
                 "back on July 18, 1946, one day after becoming the first and only Black resident of "
                 "Taylor County to vote in that year's Georgia Democratic primary, despite explicit threats "
                 "from the Ku Klux Klan and a public warning from a former governor that \u201cwise "
                 "Negroes will stay away from the white folks' ballot boxes.\u201d Four white men, led by "
                 "Edward Williamson, drove to the farmhouse where Snipes lived with his mother and "
                 "grandfather and called him outside; Williamson shot him and the men drove away. Snipes "
                 "died two days later after the hospital treating him said no blood was available for a "
                 "needed transfusion. A coroner's jury acquitted Williamson on a self-defense claim, "
                 "despite Snipes's own deathbed statement and his mother's witness testimony contradicting "
                 "it. Fearing retaliation, the family buried him secretly at night in a grave whose "
                 "location remains unknown to his surviving relatives, and much of the family fled the "
                 "county. Snipes's killing, alongside the Moore's Ford lynchings that occurred in Georgia "
                 "just one week later, prompted a young Morehouse College student, Martin Luther King Jr., "
                 "to write a public letter condemning the state's racial violence. No one was ever held "
                 "accountable.",
         known=["Victim identity, background, and the July 17\u201320, 1946 timeline, per the DOJ's public case file, PBS FRONTLINE's \u201cUn(re)solved\u201d case summary, and the Georgia Civil Rights Cold Cases Project at Emory University.",
                "A coroner's jury acquitted Edward Williamson on a self-defense claim on July 29, 1946, despite contradicting deathbed and eyewitness testimony; no one was ever held accountable, per the same sources."],
         unknown=["No one was ever convicted in Snipes's death.",
                  "The exact location of Snipes's grave, buried secretly at night out of fear for the family's safety, remains unknown even to his surviving relatives."],
         unanswered=["What did the FBI's investigation, requested by the DOJ after Williamson's acquittal, ultimately establish?",
                     "What connection, if any, exists between this case and Isaiah Nixon's killing two years later in nearby Montgomery County, documented separately in this archive \u2014 both killings tied to voting, both resulting in acquittals, both driving surviving families out of the region?",
                     "What became of the 2006 push by the NAACP and the Prison & Jail Project for a renewed federal investigation?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/maceo-snipes/", True),
                        src("Georgia Civil Rights Cold Cases Project, Emory University \u2014 case summary",
                            "https://coldcases.emory.edu/maceo-snipes/", True)]),
    dict(id="james-earl-motley", caseNumber="083", name="James Earl Motley",
         status="unsolved", caseType="homicide", year=1966, age=27, gender="male",
         city="Wetumpka", county="Elmore", state="AL", caseSeries=None,
         summary="James Earl Motley, 27, died from head injuries in the Elmore County jail around 3:30 "
                 "a.m. on November 20, 1966, hours after Deputy Harvey Conner stopped the car he was riding "
                 "in for a traffic violation. When Motley told Conner he lacked jurisdiction because the "
                 "stop had occurred in a different county, Conner ordered him out of the car; witnesses "
                 "said Conner then struck Motley repeatedly in the head with a slapjack, and that state "
                 "troopers who arrived as backup held Motley by the arms while he was beaten. Conner took "
                 "the bleeding Motley to the county jail, where local authorities said he fell twice and "
                 "struck his head before losing consciousness. An autopsy found multiple skull fractures "
                 "and brain hemorrhage; a coroner concluded the fatal injury could have come from the "
                 "beating, the falls, or some combination, and classified the death as \u201caccidental.\u201d "
                 "A state grand jury declined to indict Conner on a homicide charge in January 1967. He was "
                 "separately tried in federal court for violating Motley's civil rights; an all-white jury "
                 "with one Black member returned a not-guilty verdict on April 12, 1967.",
         known=["Victim identity and the November 20, 1966 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "A state grand jury declined to indict Deputy Harvey Conner, and a subsequent federal jury acquitted him in April 1967; the coroner classified Motley's death as accidental, per the same sources."],
         unknown=["No one was ever held criminally accountable for Motley's death.",
                  "Whether the fatal head injury resulted from the beating, the falls at the jail, or some combination was never conclusively determined."],
         unanswered=["What specific testimony from the two incarcerated men who carried Motley into his cell was presented at either the grand jury or the federal trial?",
                     "What became of the state troopers who reportedly held Motley by the arms during the beating?",
                     "What additional detail, if any, survives in the original 1966 Alabama Department of Public Safety investigative file?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/james-earl-motley/", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/james-earl-motley-notice-close-file", True)]),
    dict(id="thad-christian", caseNumber="084", name="Thad Christian",
         status="unsolved", caseType="homicide", year=1965, age=54, gender="male",
         city="Anniston", county="Calhoun", state="AL", caseSeries=None,
         summary="Thad Christian, 54, was fatally shot in the abdomen with a shotgun on August 30, 1965, "
                 "while fishing with a friend at a creek in the rural community of Central City, west of "
                 "Anniston. Robert Haynes, 41, had earlier told the two men to leave the area without "
                 "saying whether he owned the property, then returned and shot Christian as they loaded "
                 "their fishing gear into their car. Haynes was arrested and charged with murder, but "
                 "pleaded guilty to the lesser charge of first-degree manslaughter and was sentenced to "
                 "five years at a prison camp; how much of that sentence he actually served was not "
                 "documented. Haynes died in a car accident three years later, in 1968. When the FBI "
                 "reopened the case decades afterward, it found most surviving local records had been "
                 "damaged by water and were illegible; one salvaged 1965 file noted a claim that several "
                 "other Black men had also been at the creek that afternoon, a detail never further "
                 "investigated.",
         known=["Victim identity, background, and the August 30, 1965 date and circumstances, per the DOJ's public case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary.",
                "Robert Haynes pleaded guilty to first-degree manslaughter and was sentenced to five years, a fraction of the murder charge originally filed; he died in 1968, per the same sources."],
         unknown=["How much of his five-year sentence Haynes actually served before his 1968 death was never documented.",
                  "The identities of the other Black men reportedly present at the creek that afternoon, referenced in a 1965 FBI file, were never established."],
         unanswered=["Why was a murder charge reduced to first-degree manslaughter, and what plea negotiation led to that outcome?",
                     "Who were the other men reportedly at the creek, and might any of them have left surviving accounts?",
                     "What became of the original Calhoun County court records before they were damaged beyond legibility?"],
         extraSources=[src("PBS FRONTLINE Un(re)solved \u2014 case summary",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/thad-christian/", True),
                        src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/thad-christian-notice-close-file", True)]),
    dict(id="isaiah-henry", caseNumber="085", name="Isaiah Henry",
         status="unsolved", caseType="homicide", year=1954, age=38, gender="male",
         city="Greensburg", county="St. Helena Parish", state="LA", caseSeries=None,
         summary="Isaiah Henry, 38, a school bus driver and farmer who helped his Black neighbors prepare "
                 "for voter registration tests, was found severely beaten on the side of a road in St. "
                 "Helena Parish on July 28, 1954, one day after he voted in the Democratic primary. "
                 "Unidentified men had called on him that morning and he left with them; he was later "
                 "taken to a hospital in New Orleans. In early August 1954, sheriff's office deputies "
                 "arrested a local police juror, Lester Hornsby, and a sheriff's deputy, Carl Womak, on "
                 "charges of simple kidnapping and attempted murder; Womak had been the deputy assigned to "
                 "the polling place where Henry voted. A contemporaneous news article quoted the assistant "
                 "district attorney saying the two men were held because he believed they knew something "
                 "about the beating, but no record indicates either man was ever indicted. Local jail "
                 "logbooks, arrest warrants, and prosecutorial files from the case no longer exist. One of "
                 "Henry's sons later said his father was likely beaten because of his political "
                 "involvement.",
         known=["Victim identity, background, and the July 27\u201328, 1954 date and circumstances, per the DOJ's public case file, drawing on a 2007 article in The Advocate.",
                "Lester Hornsby and Carl Womak were arrested on kidnapping and attempted murder charges in connection with the case, but no record indicates either was ever indicted, per the same file."],
         unknown=["No one was ever convicted in connection with Henry's beating.",
                  "The full circumstances of his abduction that morning, and what happened to him before he was found on the roadside, were never documented."],
         unanswered=["Why were Hornsby and Womak never indicted despite being arrested and held specifically because officials believed they knew something about the beating?",
                     "What became of the original St. Helena Parish jail logbooks and investigative files before they were lost?",
                     "What connection, if any, existed between Henry's beating and his broader work helping neighbors prepare for voter registration tests?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/isaiah-henry-notice-close-file", True)]),
    dict(id="john-earl-reese", caseNumber="086", name="John Earl Reese",
         status="unsolved", caseType="homicide", year=1955, age=16, gender="male",
         city="Mayflower", county="Rusk", state="TX", caseSeries=None,
         summary="John Earl Reese, 16, was shot and killed on the night of October 22, 1955, while dancing "
                 "with his cousins in a caf\u00e9 in Mayflower, a small Black community near Longview. Perry "
                 "Dean Ross, driving roughly 85 miles per hour, fired nine shots from a rifle into the "
                 "caf\u00e9 window as his car passed; Reese was killed, and two of his cousins were wounded. "
                 "The same night, gunmen fired into at least one other home in the area where Black "
                 "residents lived. The attacks were tied to local anger over a bond election to build a new "
                 "school for Black children following the Brown v. Board of Education decision; Ross later "
                 "admitted his anger over the new school had \u201ca great deal\u201d to do with the "
                 "shooting. The local sheriff initially refused to investigate, insisting Black residents "
                 "were responsible for their own community's shooting. Texas Rangers eventually "
                 "interviewed over 300 people and identified Ross and a second man, Joe Simpson, both of "
                 "whom confessed. Simpson's charges were dropped in exchange for his testimony against "
                 "Ross, who was convicted of murder in April 1957 and given a two-to-five-year sentence "
                 "that was immediately suspended; Simpson later pleaded guilty to the same charge and "
                 "received an identical suspended sentence. Neither man served any time in prison.",
         known=["Victim identity and the October 22, 1955 date and circumstances, per the DOJ's public case file and extensive contemporaneous and historical reporting.",
                "Perry Dean Ross and Joe Simpson both confessed and were convicted, but both received fully suspended sentences and served no prison time, per the same sources."],
         unknown=["Whether the other shootings that same night at additional homes were connected to the same group of men was never conclusively established.",
                  "The full scope of who else may have been involved in planning the night's attacks beyond Ross and Simpson was never investigated."],
         unanswered=["Why did the local sheriff initially refuse to investigate despite the shooting's obvious severity?",
                     "What became of the broader dispute over the new school's location that the Texas Rangers identified as the underlying motive?",
                     "Why were fully suspended sentences considered appropriate for two confessed killers in a case the district attorney himself urged the jury to punish severely?"],
         extraSources=[src("U.S. Department of Justice \u2014 Notice to Close File",
                            "https://www.justice.gov/crt/case-document/john-earl-reese", True),
                        src("The Dallas Morning News \u2014 \u201cFBI takes new look at white men's killing of black teen in 1955\u201d",
                            "https://www.dallasnews.com/news/crime/2010/02/09/fbi-takes-new-look-at-white-men-s-killing-of-black-teen-in-1955/", True)]),
    dict(id="frank-andrews", caseNumber="087", name="Frank Andrews",
         status="unsolved", caseType="homicide", year=1964, age=27, gender="male",
         city="Lisman", county="Choctaw County", state="AL", caseSeries=None,
         dateAdded="2026-08-26",
         summary="Frank Andrews, 27, was shot in the back and killed on November 28, 1964 outside Smith's "
                 "Caf\u00e9 in Lisman, Alabama, by Quinnie Donald, a white Choctaw County sheriff's chief deputy. "
                 "Donald and another deputy said they were at the caf\u00e9, which served the local Black "
                 "community, investigating illegal whiskey; Donald claimed Andrews advanced on a fellow deputy "
                 "with a knife, a claim disputed by witness accounts. A local grand jury declined to indict, and "
                 "no one was ever prosecuted for his death.",
         known=["Victim identity, age, and the November 28, 1964 shooting outside Smith's Caf\u00e9 in Lisman, "
                "per the Department of Justice's Cold Case closing memorandum.",
                "The shooter, sheriff's chief deputy Quinnie Donald, was publicly identified in the DOJ memo and "
                "in FBI records reviewed by PBS Frontline's Unresolved project.",
                "A local grand jury declined to indict Donald in 1964, and no state or federal charges were "
                "ever brought."],
         unknown=["Whether Andrews in fact drew a knife, as Donald claimed, is disputed \u2014 the three "
                  "eyewitnesses identified in 1964 gave factually inconsistent accounts, per the DOJ memo.",
                  "In a 2008 re-interview under the Till Act, Donald reportedly gave an account of the shooting "
                  "that conflicted with what he told investigators in 1964; the full substance of that shift is "
                  "not detailed in the public record."],
         unanswered=["What specifically changed between Donald's 1964 and 2008 accounts of the shooting, and why?",
                     "Why did the three 1964 eyewitness accounts conflict, and was that inconsistency investigated "
                     "further at the time?",
                     "What led the FBI and DOJ to close the reopened case in 2013 without prosecution, given the "
                     "disputed record?"],
         extraSources=[src("U.S. Department of Justice, Civil Rights Division \u2014 Frank Andrews closing memorandum",
                            "https://www.justice.gov/crt/case-document/frank-andrews-notice-close-file", True),
                        src("PBS Frontline \u2014 \u201cUnresolved\u201d, Frank Andrews case profile",
                            "https://www.pbs.org/wgbh/frontline/interactive/unresolved/cases/frank-andrews/", True),
                        src("Alabama Reflector \u2014 \u201cNo justice in 1964 slaying by sheriff's deputy\u201d",
                            "https://www.alreporter.com/2026/06/05/no-justice-in-1964-slaying-by-sheriffs-deputy/", True)]),
    dict(id="alexis-patterson", caseNumber="088", name="Alexis Patterson",
         status="unsolved", caseType="missing_persons", year=2002, age=7, gender="female",
         city="Milwaukee", county="Milwaukee County", state="WI", caseSeries=None,
         dateAdded="2026-08-26",
         victimPhotos=[
             {"url": "https://www.fbi.gov/wanted/kidnap/alexis-s.-patterson/@@images/image/large",
              "caption": "Alexis S. Patterson", "credit": "FBI"},
         ],
         summary="Alexis Patterson, 7, disappeared on the morning of May 3, 2002 after her stepfather walked "
                 "her to a crosswalk roughly half a block from Hi-Mount Community School in Milwaukee, "
                 "Wisconsin, and a crossing guard escorted her across the street. She never arrived in her "
                 "first-grade classroom; classmates later reported seeing her crying on the playground before "
                 "and after the school day. Her disappearance prompted one of the largest search efforts in "
                 "Milwaukee police history, but no arrests have ever been made and Alexis has never been found.",
         known=["Victim identity, age, and the May 3, 2002 disappearance near Hi-Mount Community School, per "
                "the FBI's public case listing and the Milwaukee Police Department.",
                "Her stepfather told police he watched her cross the street toward the school playground before "
                "he walked home; the school reported she never attended class that day.",
                "The Milwaukee County Sheriff's Office has offered a $10,000 reward for information leading to "
                "her return, and the FBI continues to list her as an open case."],
         unknown=["What happened to Alexis between being seen on the playground and her confirmed absence from "
                  "class has never been publicly established.",
                  "No suspect has ever been officially named by police.",
                  "Full results of the searches of the Milwaukee River and other sites are not comprehensively "
                  "public."],
         unanswered=["What, if anything, did the reported 2003 John Doe investigation \u2014 never officially "
                     "confirmed by police \u2014 establish?",
                     "What has the Milwaukee Police Department's cold case unit found in its ongoing review, if "
                     "anything?",
                     "Why does a documented gap remain between witness accounts of Alexis's morning and her "
                     "confirmed disappearance?"],
         extraSources=[src("Federal Bureau of Investigation \u2014 Alexis S. Patterson case listing",
                            "https://www.fbi.gov/wanted/kidnap/alexis-s.-patterson", True),
                        src("Milwaukee Police Department, via Solve the Case \u2014 official case narrative",
                            "https://www.solvethecase.org/case/2002-11/alexis-patterson", True),
                        src("WUWM (Milwaukee NPR) \u2014 \u201cMilwaukee Police Department is still looking for "
                            "Alexis Patterson, 20 years later\u201d",
                            "https://www.wuwm.com/2022-05-03/milwaukee-police-department-is-still-looking-for-alexis-patterson-20-years-later", True)]),
    dict(id="nacomie-freeman", caseNumber="089", name="Nacomie Freeman",
         status="unsolved", caseType="homicide", year=2004, age=24, gender="female",
         city="Phoenix", county="Maricopa County", state="AZ", caseSeries=None,
         dateAdded="2026-08-26",
         summary="Nacomie Freeman, 24, was shot in the stomach and pushed out of a moving truck in the 1600 "
                 "block of West Denton Avenue in Phoenix, Arizona, on June 24, 2004. Witnesses reported seeing "
                 "her pushed from a dark-colored, late-1990s-model short-bed truck; she was pronounced dead at "
                 "the scene. The Maricopa County Sheriff's Office has said investigators developed some leads "
                 "but have never made an arrest.",
         known=["Victim identity, age, and the June 24, 2004 date and location, per the Maricopa County "
                "Sheriff's Office and Project Cold Case's case record.",
                "Witnesses reported the truck she was pushed from as a dark-colored, late-1990s-model "
                "short-bed truck with the partial license plate letters \u201cJ, T, L,\u201d per contemporaneous "
                "reporting."],
         unknown=["No arrest has ever been made.",
                  "The relationship, if any, between Freeman and the occupants of the truck has not been "
                  "publicly disclosed.",
                  "The full license plate and the truck's owner or driver have never been publicly identified."],
         unanswered=["What specific leads have investigators developed, and why have they not resulted in an "
                     "arrest?",
                     "Has the truck described by witnesses ever been located or identified?",
                     "What, if anything, has advances in forensic technology contributed to the case since 2004?"],
         extraSources=[src("Maricopa County Sheriff's Office, via Project Cold Case \u2014 case record and spotlight",
                            "https://projectcoldcase.org/victim-detail/nacomie-freeman-351/", True),
                        src("The Arizona Republic \u2014 \u201cKiller sought in death of Phoenix woman\u201d (2004)",
                            "https://www.newspapers.com/article/arizona-republic/200158960/", True)]),
    dict(id="quincy-booker", caseNumber="090", name="Quincy Booker",
         status="unsolved", caseType="homicide", year=2011, age=36, gender="male",
         city="Albuquerque", county="Bernalillo County", state="NM", caseSeries=None,
         dateAdded="2026-08-26",
         summary="Quincy Booker, 36, was shot and killed in a drive-by shooting near the intersection of Arno "
                 "Avenue and Santa Fe Avenue Southeast in Albuquerque, New Mexico, on July 17, 2011. Witnesses "
                 "said four men got out of a blue Dodge Neon and opened fire, hitting him more than a dozen "
                 "times, next to a church filled with people on a Sunday. The attackers fled immediately, and "
                 "the case has remained unsolved since.",
         known=["Victim identity, age, and the July 17, 2011 shooting near Arno Avenue and Santa Fe Avenue SE, "
                "per the Albuquerque Police Department's case record via Project Cold Case.",
                "Witnesses described four men exiting a blue Dodge Neon and firing on Booker before fleeing."],
         unknown=["No arrest has ever been made.",
                  "The identities of the four men described by witnesses have not been publicly disclosed.",
                  "The motive for the shooting has not been made public."],
         unanswered=["What, if anything, connected Booker to the men who attacked him?",
                     "Has the blue Dodge Neon described by witnesses ever been identified or located?",
                     "What leads, if any, have Albuquerque police developed since 2011?"],
         extraSources=[src("Albuquerque Police Department, via Project Cold Case \u2014 case record",
                            "https://projectcoldcase.org/victim-detail/quincy-booker-1863/", True),
                        src("KOAT \u2014 \u201cMan gunned down in SE Albuquerque, police say\u201d (2011)",
                            "https://www.koat.com/article/man-gunned-down-in-se-albuquerque-police-say/5036927", True)]),
]



# Slug (and thus filename, cases/<slug>.html) for each named case series. Any
# case whose caseSeries matches a key here gets linked into that series page;
# order here controls display order in nav links and the left panel.
SERIES_SLUGS = {
    "Freeway Phantom": "freeway-phantom",
    "Silver Dollar Group": "silver-dollar-group",
}

for c in CASES:
    c["sources"] = c.pop("extraSources", []) + DEFAULT_SOURCES()
    # lastVerified reflects the date this build's research pass checked the
    # case against the sources above; None means not yet checked at all.
    c["lastVerified"] = "2026-08-21" if any(s["verified"] for s in c["sources"]) else None
    # dateAdded reflects when the case was added to THIS archive (not the
    # case's real-world date). Respects a per-case "dateAdded" already set
    # on the dict (e.g. a case added after the initial batch); otherwise
    # falls back to the initial batch's date. The homepage's "Latest Case
    # Added" feature reads this field directly.
    c.setdefault("dateAdded", "2026-08-21")

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
    # NAV_DOCS is split across two footer columns so the list stays readable
    # as more pages get added — first half stays with core site navigation,
    # second half groups the more secondary/support-adjacent pages.
    docs_first, docs_second = NAV_DOCS[:3], NAV_DOCS[3:]
    docs_first_links = "\n        ".join(f'<li><a href="{r}{href}">{label}</a></li>' for label, href in docs_first)
    docs_second_links = "\n        ".join(f'<li><a href="{r}{href}">{label}</a></li>' for label, href in docs_second)
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
        {"".join(f'<li><a href="{r}cases/{SERIES_SLUGS[name]}.html">{html.escape(name)} Series</a></li>' for name in SERIES_SLUGS if any(c.get("caseSeries") == name for c in CASES))}
        {docs_first_links}
      </ul>
    </div>
    <div class="footer-col">
      <h4>More</h4>
      <ul>
        {docs_second_links}
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
    <span id="site-visit-counter" style="color:var(--text-dim); font-size:.8rem;">Site visits: <span id="site-visit-count">\u2026</span></span>
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
<script src="{r}js/us-states-paths.js"></script>
<script src="{r}js/main.js"></script>
<script src="{r}js/quiz.js"></script>
<script src="{r}js/saved-cases.js"></script>
<script src="{r}js/submit-form.js"></script>
</body>
</html>'''

# ---------------------------------------------------------------------------
# Left panel (Case Files)
# ---------------------------------------------------------------------------
def series_nav_links(r):
    """Renders one 'Series Name →' link per distinct case series actually
    present in CASES, in SERIES_SLUGS order, so this scales automatically
    as more series get added — never needs a manual per-series edit here."""
    present = [name for name in SERIES_SLUGS if any(c.get("caseSeries") == name for c in CASES)]
    return "\n".join(
        f'<a href="{r}cases/{SERIES_SLUGS[name]}.html">{html.escape(name)} \u2192</a>' for name in present
    )

def left_panel(depth, active_id=None):
    r = rel(depth)
    items = []
    for c in CASES:
        current = ' aria-current="page"' if c["id"] == active_id else ""
        search_blob = f'{c["name"]} {c.get("city") or ""} {c.get("state") or ""} {c["year"]}'
        is_series = "true" if c.get("caseSeries") else "false"
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
  <div class="pl-series-link">{series_nav_links(r)}<a href="{r}quiz.html">\U0001F9E0 Cold Case Quiz \u2192</a></div>
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
    return f'''<aside class="panel-profile area-profile" id="case-profile">
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
  <div class="pp-notes" id="research-notes-panel">
    <div class="pp-notes-head">Your Research Notes</div>
    <p class="pp-notes-hint">Saved only in this browser \u2014 never sent anywhere, never visible to anyone else. Add as many notes as you want; they'll be here next time you open this case.</p>
    <div class="research-notes-list" data-research-notes-list="{c['id']}"></div>
    <button type="button" class="btn-add-note" data-add-research-note="{c['id']}">+ Add a note</button>
  </div>
</aside>'''

def sources_panel(c):
    return f'''<aside class="panel-sources area-sources" id="case-sources">
  <div class="pp-head">Source Records</div>
  {source_records_html(c)}
  <div class="last-verified"><strong>Last Verified:</strong> {c['lastVerified'] or 'NOT YET VERIFIED'}</div>
  <div class="archive-note">&ldquo;{ARCHIVE_NOTE}&rdquo;</div>
  {ad_slot(label="Advertisement")}
</aside>'''

def questions_panel(c):
    items = "\n".join(f'<div class="pq-item">{html.escape(q)}</div>' for q in c.get("unanswered", []))
    return f'''<section class="panel-questions area-questions" id="case-questions">
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

    jump_nav = f'''<nav class="case-jump-nav" aria-label="Jump to section">
    <a href="#case-board">Summary</a>
    <a href="#case-profile">Profile</a>
    <a href="#case-sources">Sources</a>
    <a href="#case-questions">Unanswered Questions</a>
    <button type="button" class="case-save-btn" data-save-case-btn="{c['id']}">\u2606 Save This Case</button>
  </nav>'''
    body = f'''{top_header(depth)}
<div class="app-shell">
  {left_panel(depth, active_id=c["id"])}
  <section class="panel-board area-board" id="case-board">
    <div class="board-head">
      <div>
        <span class="board-file-no">CASE FILE #{c['caseNumber']}</span>
        <h1>{html.escape(c['name'])}</h1>
      </div>
      {board_toolbar()}
    </div>
    {jump_nav}
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

def build_silver_dollar_group():
    depth = 1
    victims = [c for c in CASES if c.get("caseSeries") == "Silver Dollar Group"]
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
        <h1>The Silver Dollar Group</h1>
      </div>
    </div>
    <div style="padding:20px;">
      <p>The Silver Dollar Group was a secretive Klan cell formed around 1964 at the Shamrock Motor Hotel
      in Vidalia, Louisiana, reportedly by Raleigh Jackson "Red" Glover out of frustration that existing
      Klan groups in the area were not violent enough. Members, estimated at ten to twenty, each carried a
      silver dollar as a mark of identification. The group operated across Concordia Parish, Louisiana and
      Adams County, Mississippi \u2014 the Natchez\u2013Ferriday area \u2014 roughly between 1964 and 1967,
      and retired FBI agents have since confirmed its existence and its suspected role in a string of
      unsolved killings and bombings in the region, including the three cases documented here. Glover died
      in 1984 without ever being charged.</p>
      <div class="callout warn"><strong>Disclaimer:</strong> This page summarizes publicly reported
      information, including named subjects and suspects from official DOJ case files, for research and
      awareness. It does not itself accuse any individual of a crime beyond what those official records
      state, and does not claim new evidence.</div>
      <h2 style="margin-top:24px;">Documented Victims</h2>
      <div class="related-grid" style="margin-top:12px;">{cards}</div>
    </div>
  </section>
  <aside class="panel-profile area-profile">
    <div class="pp-head">Series Profile</div>
    <div class="pp-grid">
      <div class="pp-row"><span class="label">Status</span><span class="status-badge status-unsolved">Unsolved</span></div>
      <div class="pp-row"><span class="label">Cases in Series</span><span class="value">{len(victims)}</span></div>
      <div class="pp-row"><span class="label">Span</span><span class="value">1964&ndash;1967</span></div>
      <div class="pp-row"><span class="label">Location</span><span class="value">Concordia Parish, LA &amp; Adams County, MS</span></div>
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
        <div class="pq-item">What is the complete membership of the Silver Dollar Group, and how many were ever formally investigated?</div>
        <div class="pq-item">What connection, if any, links this group to the 1965 car bombing of George Metcalfe, who survived and is not documented as a standalone case in this archive?</div>
        <div class="pq-item">What undisclosed FBI informant material, if any, remains in the Bureau's files on the group?</div>
      </div>
    </details>
  </section>
</div>
{footer_html(depth)}'''
    write("cases/silver-dollar-group.html", page_shell("The Silver Dollar Group", "Series page linking three cases in this archive to a Klan cell active in Concordia Parish, Louisiana and Adams County, Mississippi, 1964-1967.", depth, body,
          canonical_path="cases/silver-dollar-group.html", og_image="og/silver-dollar-group.png", og_type="article"))

def build_case_index():
    depth = 1
    grid_cards = "\n".join(
        f'<a class="related-card" data-case-item data-case-id="{c["id"]}" data-status="{c["status"]}" data-case-type="{c.get("caseType") or ""}" '
        f'data-series-flag="{"true" if c.get("caseSeries") else "false"}" '
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
    series_present = [name for name in SERIES_SLUGS if any(c.get("caseSeries") == name for c in CASES)]
    series_tracked_str = ", ".join(
        f'{name} ({sum(1 for c in CASES if c.get("caseSeries") == name)} cases)' for name in series_present
    )
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
    <div class="overview-card"><span class="num">{len(series_present)}</span><span class="cap">Case Series Tracked</span></div>
  </div>
  <div style="padding:0 20px 24px;">
    <p>This archive organizes publicly reported information on unsolved cases involving Black victims. It
    does not conduct original investigations and does not accuse any individual of a crime. Select a case
    from the Case Files panel, or open the full <a href="cases/index.html">Case Index</a> to search by
    timeline or location.</p>
  </div>'''
    recent_n = 6
    recent_cases = sorted(CASES, key=lambda c: c["caseNumber"], reverse=True)[:recent_n]
    recent_cards = "\n".join(
        f'<a class="related-card" href="cases/{c["id"]}.html"><span class="rc-name">{html.escape(c["name"])}</span>'
        f'<span class="rc-meta">{c["year"]} \u00b7 {location_str(c)}</span></a>' for c in recent_cases)
    recent_section = f'''<div style="padding:4px 20px 26px;">
    <h2 style="margin-bottom:4px;">Recently Added</h2>
    <p style="margin-bottom:16px; font-size:.88rem;">The {recent_n} most recently documented cases in this archive.</p>
    <div class="related-grid">{recent_cards}</div>
  </div>'''

    decade_buckets = {}
    for c in CASES:
        decade_buckets.setdefault((c["year"] // 10) * 10, []).append(c)
    decade_blocks = []
    for decade in sorted(decade_buckets, reverse=True):
        cases_in_decade = sorted(decade_buckets[decade], key=lambda c: c["year"])
        cards = "\n".join(
            f'<a class="related-card" href="cases/{c["id"]}.html"><span class="rc-name">{html.escape(c["name"])}</span>'
            f'<span class="rc-meta">{c["year"]} \u00b7 {location_str(c)}</span></a>' for c in cases_in_decade)
        decade_blocks.append(f'''<details class="pq-details">
      <summary class="pq-head">{decade}s <span style="color:var(--text-faint); text-transform:none; letter-spacing:0;">&mdash; {len(cases_in_decade)} case{"s" if len(cases_in_decade) != 1 else ""}</span></summary>
      <div class="related-grid" style="margin-top:10px;">{cards}</div>
    </details>''')
    decade_section = f'''<div style="padding:4px 20px 26px;">
    <h2 style="margin-bottom:4px;">Browse by Decade</h2>
    <p style="margin-bottom:16px; font-size:.88rem;">Open a decade to see the cases documented from that period.</p>
    <div style="display:flex; flex-direction:column; gap:8px;">{"".join(decade_blocks)}</div>
  </div>'''
    map_section = '''<div style="padding:4px 20px 26px;">
    <h2 style="margin-bottom:4px;">Browse by State</h2>
    <p style="margin-bottom:16px; font-size:.88rem;">Click a highlighted state to jump straight to its cases.</p>
    <div id="home-map"></div>
  </div>'''
    body = f'''{top_header(depth)}
<div class="app-shell">
  {left_panel(depth)}
  <section class="panel-board area-board">
    <div class="board-head">
      <div><span class="board-file-no">DASHBOARD</span><h1>Archive Overview</h1></div>
    </div>
    <div style="padding:20px 20px 0;">{featured}</div>
    {recent_section}
    {map_section}
    {decade_section}
    {overview}
  </section>
  <aside class="panel-profile area-profile">
    <div class="pp-head">Collection Profile</div>
    <div class="pp-grid">
      <div class="pp-row"><span class="label">Scope</span><span class="value">Unsolved homicides &amp; missing-persons cases involving Black victims</span></div>
      <div class="pp-row"><span class="label">Method</span><span class="value">Public-record research only</span></div>
      <div class="pp-row"><span class="label">Series Tracked</span><span class="value">{series_tracked_str}</span></div>
    </div>
  </aside>
  <aside class="panel-sources area-sources">
    <div class="pp-head">Getting Started</div>
    <div class="pq-list" style="grid-template-columns:1fr;">
      <div class="pq-item">Use SEARCH (top right, or press &ldquo;/&rdquo;) to find a case by name, city, state, or year &mdash; or anything written inside a case file.</div>
      <div class="pq-item">Open the Case Index to browse by timeline or geography.</div>
      <div class="pq-item">Select any case in the left panel to open its investigation board.</div>
    </div>
    <a href="quiz.html" class="quiz-callout">
      <span class="quiz-callout-eyebrow">\U0001F9E0 Test Yourself</span>
      <span class="quiz-callout-title">Take the Cold Case Quiz</span>
      <span class="quiz-callout-sub">6 questions on the law behind these cases &mdash; the Emmett Till Act, statutes of limitations, what &ldquo;closed&rdquo; really means.</span>
    </a>
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

STATE_NAMES = {
    "AL": "Alabama", "AR": "Arkansas", "CO": "Colorado", "DC": "Washington, D.C.", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "IA": "Iowa", "IL": "Illinois", "IN": "Indiana", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "MA": "Massachusetts", "MD": "Maryland", "MI": "Michigan", "MN": "Minnesota", "MO": "Missouri", "MS": "Mississippi", "NC": "North Carolina",
    "NE": "Nebraska", "NJ": "New Jersey", "NY": "New York", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "SC": "South Carolina", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WY": "Wyoming",
}

def bar_row(label, count, max_count, extra=""):
    pct = round((count / max_count) * 100) if max_count else 0
    return (f'<div class="stat-row"><span class="stat-label">{html.escape(str(label))}</span>'
            f'<span class="stat-bar-track"><span class="stat-bar-fill" style="width:{pct}%"></span></span>'
            f'<span class="stat-count">{count}{extra}</span></div>')

def build_statistics():
    depth = 0
    total = len(CASES)
    states = sorted(set(c["state"] for c in CASES))

    # Cases per decade, computed directly from each case's year.
    decade_counts = {}
    for c in CASES:
        decade = (c["year"] // 10) * 10
        decade_counts[decade] = decade_counts.get(decade, 0) + 1
    decades_sorted = sorted(decade_counts.items())
    max_decade = max(decade_counts.values())
    decade_rows = "\n".join(bar_row(f"{d}s", n, max_decade) for d, n in decades_sorted)

    # Cases per state, ranked.
    state_counts = {}
    for c in CASES:
        state_counts[c["state"]] = state_counts.get(c["state"], 0) + 1
    states_sorted = sorted(state_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    max_state = max(state_counts.values())
    state_rows = "\n".join(bar_row(STATE_NAMES.get(s, s), n, max_state) for s, n in states_sorted)

    # Case type and status breakdowns.
    type_counts = {}
    for c in CASES:
        t = c.get("caseType") or "unknown"
        type_counts[t] = type_counts.get(t, 0) + 1
    max_type = max(type_counts.values())
    type_rows = "\n".join(bar_row(STATUS_LABEL.get(t, t).title(), n, max_type) for t, n in sorted(type_counts.items(), key=lambda kv: -kv[1]))

    # How long cases have gone unresolved, computed from each case's year to now.
    current_year = 2026
    years_open = [current_year - c["year"] for c in CASES]
    avg_years = round(sum(years_open) / len(years_open))
    oldest = min(CASES, key=lambda c: c["year"])
    newest = max(CASES, key=lambda c: c["year"])

    series_count = sum(1 for c in CASES if c.get("caseSeries"))

    body = f'''<p>These figures are computed directly from the {total} cases currently documented in this
    archive &mdash; they describe this archive's coverage, not a comprehensive accounting of every unsolved
    case involving a Black victim in the United States. Coverage here reflects what has been researched and
    verified so far, not the true scale of these cases nationally.</p>

    <div class="overview-grid" style="padding:0; margin:20px 0;">
      <div class="overview-card"><span class="num">{total}</span><span class="cap">Cases Documented</span></div>
      <div class="overview-card"><span class="num">{len(states)}</span><span class="cap">States Represented</span></div>
      <div class="overview-card"><span class="num">{avg_years}</span><span class="cap">Avg. Years Unresolved</span></div>
      <div class="overview-card"><span class="num">{series_count}</span><span class="cap">Cases Linked to a Series</span></div>
    </div>

    <h2>Cases by Decade</h2>
    <p>The killing or disappearance date for each case, grouped by decade.</p>
    <div class="stat-chart">{decade_rows}</div>

    <h2>Cases by State</h2>
    <p>Where each case took place, ranked by count.</p>
    <div class="stat-chart">{state_rows}</div>

    <h2>Case Type</h2>
    <div class="stat-chart">{type_rows}</div>

    <h2>Timespan</h2>
    <p>The earliest case currently documented is <a href="cases/{oldest["id"]}.html">{html.escape(oldest["name"])}</a>
    ({oldest["year"]}, {STATE_NAMES.get(oldest["state"], oldest["state"])}). The most recent is
    <a href="cases/{newest["id"]}.html">{html.escape(newest["name"])}</a> ({newest["year"]},
    {STATE_NAMES.get(newest["state"], newest["state"])}) &mdash; a span of {newest["year"] - oldest["year"]} years.</p>

    <div class="callout">These numbers update automatically as new cases are added to the archive. If you
    notice a discrepancy, use the <a href="submit.html">Submit a Case or Tip</a> page to flag it.</div>'''
    write("statistics.html", page_shell("Archive Statistics", f"Data and figures computed from the {total} cases currently documented in this archive.", depth,
          doc_page(depth, "Data", "Archive Statistics", body), canonical_path="statistics.html"))

def build_saved_cases():
    depth = 0
    body = '''<p>Cases you\u2019ve saved for later, stored privately in this browser only. Nothing here is
    sent anywhere or visible to anyone but you \u2014 not the site owner, not other visitors. This list (and
    any private notes you\u2019ve added) will disappear if you clear your browser\u2019s site data, and won\u2019t
    show up if you open this site on a different device or browser.</p>
    <div id="saved-cases-list" class="related-grid" style="margin-top:20px;"></div>'''
    write("saved.html", page_shell("My Saved Cases", "Cases you've bookmarked for later, stored privately in your own browser.", depth,
          doc_page(depth, "Private", "My Saved Cases", body), canonical_path="saved.html"))

def build_quiz():
    depth = 0
    body = f'''<p>A short, self-scoring quiz about the <strong>legal system</strong> around cases like the
    ones in this archive &mdash; not about any individual victim. Every answer here is grounded in facts
    encountered while researching the {len(CASES)} cases documented on this site.</p>
    <form id="quiz-form"></form>
    <p id="quiz-result" class="quiz-result" hidden></p>
    <div class="callout" style="margin-top:24px;">Get something wrong here? That's the point of the quiz,
    not a flaw in it &mdash; most of these facts run against what people assume about how "cold case" review
    actually works.</div>'''
    write("quiz.html", page_shell("Civil Rights Cold Case Quiz", "A short quiz about the legal history and process behind civil rights cold case review \u2014 the Emmett Till Act, statutes of limitations, and what case closure actually means.", depth,
          doc_page(depth, "Learn", "Civil Rights Cold Case Quiz", body), canonical_path="quiz.html"))

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
    r = rel(depth)
    body = '''<h2>Guidelines before you submit</h2>
    <ul>
      <li>Share information you can point to a public source for wherever possible.</li>
      <li>If you have information about an active investigation, also contact the relevant law-enforcement agency directly.</li>
      <li>Do not submit unverified accusations against a named individual &mdash; we will not publish them.</li>
      <li>If you are a family member, you're welcome to note that so we can prioritize sensitivity in how the case is presented.</li>
    </ul>
    <form class="form-grid" id="tip-form" data-tip-form action="https://formspree.io/f/xnpqaddo" method="POST" aria-label="Submit a case or tip">
      <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">
      <div class="field"><label for="case-name">Case or victim name</label><input type="text" id="case-name" name="case_name" required></div>
      <div class="field"><label for="case-year">Year (approximate is fine)</label><input type="text" id="case-year" name="year"></div>
      <div class="field"><label for="case-location">Location</label><input type="text" id="case-location" name="location"></div>
      <div class="field"><label for="case-type">Submission type</label>
        <select id="case-type" name="submission_type">
          <option>New case suggestion</option>
          <option>Correction or update to an existing case</option>
          <option>Source or citation to add</option>
          <option>Other</option>
        </select>
      </div>
      <div class="field"><label for="case-details">Details &amp; sources</label>
        <textarea id="case-details" name="details" required placeholder="What you know, and where it's documented (links welcome)."></textarea>
        <p class="hint">Please avoid pasting unsourced accusations against a named individual.</p>
      </div>
      <div class="field"><label for="contact-email">Your email (optional)</label><input type="email" id="contact-email" name="email"></div>
      <div class="checkbox-row"><input type="checkbox" id="family-member" name="family_member"><label for="family-member" style="margin:0; font-weight:400;">I am a family member of the person in this case</label></div>
      <button class="btn-primary" type="submit" data-tip-submit-btn>Submit</button>
      <div class="tip-form-status" data-tip-form-status role="status" aria-live="polite"></div>
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
      <li>Nothing at this time via the Submit a Tip form &mdash; it is currently a static template not
      connected to any backend, so information entered into it is not transmitted, stored, or collected
      anywhere. This section will be updated to describe what is collected and how it is handled once (and
      if) the form is connected to a live submission service.</li>
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
    dict(date="2026-08-26", case_id="isaiah-henry",
         text="New case added to the archive: Isaiah Henry (Greensburg, Louisiana, 1954), sourced from "
              "the DOJ's Notice to Close File."),
    dict(date="2026-08-26", case_id="john-earl-reese",
         text="New case added to the archive: John Earl Reese (Mayflower, Texas, 1955), sourced from the "
              "DOJ's Notice to Close File and The Dallas Morning News."),
    dict(date="2026-08-26", case_id="james-earl-motley",
         text="New case added to the archive: James Earl Motley (Wetumpka, Alabama, 1966), sourced from "
              "PBS FRONTLINE's \u201cUn(re)solved\u201d case summary and the DOJ's Notice to Close File."),
    dict(date="2026-08-26", case_id="thad-christian",
         text="New case added to the archive: Thad Christian (Anniston, Alabama, 1965), sourced from PBS "
              "FRONTLINE's \u201cUn(re)solved\u201d case summary and the DOJ's Notice to Close File."),
    dict(date="2026-08-26", case_id="maceo-snipes",
         text="New case added to the archive: Maceo Snipes (Butler, Georgia, 1946), sourced from PBS "
              "FRONTLINE's \u201cUn(re)solved\u201d case summary and the Georgia Civil Rights Cold Cases "
              "Project at Emory University. This case directly connects to Isaiah Nixon's case, "
              "documented in this archive as case #030 \u2014 both men were killed for voting-related "
              "activity in the same Georgia region two years apart."),
    dict(date="2026-08-26", case_id="isaiah-nixon",
         text="Updated the case's unanswered questions to reference Maceo Snipes's case, newly added to "
              "this archive, which shares the same regional and thematic connection."),
    dict(date="2026-08-26", case_id="herbert-lee",
         text="New case added to the archive: Herbert Lee (Liberty, Mississippi, 1961), sourced from "
              "the DOJ's Notice to Close File. This case directly connects to Louis Allen's case, "
              "documented in this archive as case #018 \u2014 Allen witnessed Lee's killing, later "
              "recanted his corroborating testimony to the FBI, and was himself murdered in 1964."),
    dict(date="2026-08-26", case_id="louis-allen",
         text="Updated the case's unanswered questions to reference Herbert Lee's case, newly added to "
              "this archive, which Allen witnessed and later gave conflicting testimony about."),
    dict(date="2026-08-26", case_id="samuel-younge-jr",
         text="New case added to the archive: Samuel Younge Jr. (Tuskegee, Alabama, 1966), sourced from "
              "the DOJ's Notice to Close File."),
    dict(date="2026-08-26", case_id="isaiah-taylor",
         text="New case added to the archive: Isaiah Taylor (Ruleville, Mississippi, 1964), sourced from "
              "the DOJ's Notice to Close File."),
    dict(date="2026-08-26", case_id="jimmie-lee-jackson",
         text="New case added to the archive: Jimmie Lee Jackson (Marion, Alabama, 1965), sourced from "
              "the DOJ's Notice to Close File. This case produced the only conviction the Emmett Till "
              "Act's cold case review process has generated since 2008, and is directly referenced in "
              "this archive's Cold Case Quiz."),
    dict(date="2026-08-26", case_id="thomas-brewer",
         text="New case added to the archive: Dr. Thomas Brewer (Columbus, Georgia, 1956), sourced from "
              "the DOJ's Notice to Close File."),
    dict(date="2026-08-26", case_id="ernest-jells",
         text="New case added to the archive: Ernest Jells (Clarksdale, Mississippi, 1963), sourced from "
              "the DOJ's 2010 Notice to Close File."),
    dict(date="2026-08-26", case_id="benjamin-brown",
         text="New case added to the archive: Benjamin Brown (Jackson, Mississippi, 1967), sourced from "
              "the DOJ's Notice to Close File."),
    dict(date="2026-08-26", case_id="larry-payne",
         text="New case added to the archive: Larry Payne (Memphis, Tennessee, 1968), sourced from the "
              "DOJ's Notice to Close File."),
    dict(date="2026-08-26", case_id="joseph-dumas",
         text="New case added to the archive: Joseph Dumas (Perry, Florida, 1962), sourced from the "
              "DOJ's 2010 Notice to Close File."),
    dict(date="2026-08-26", case_id="vincent-dahmon",
         text="New case added to the archive: Vincent Dahmon (Natchez, Mississippi, 1966), sourced from "
              "the DOJ's 2010 Notice to Close File. His killing occurred during the period of James "
              "Meredith's 1966 March Against Fear."),
    dict(date="2026-08-26", case_id="ed-smith",
         text="New case added to the archive: Ed Smith (State Line, Mississippi, 1958), sourced from PBS "
              "FRONTLINE's \u201cUn(re)solved\u201d case summary and the DOJ's 2009 Notice to Close File."),
    dict(date="2026-08-26", case_id="lamar-smith",
         text="New case added to the archive: Lamar Smith (Brookhaven, Mississippi, 1955), sourced from "
              "PBS FRONTLINE's \u201cUn(re)solved\u201d case summary and the Equal Justice Initiative. His "
              "killing was cited in the NAACP's own 1955 pamphlet alongside the killings of Rev. George "
              "Lee and Emmett Till, both also documented in this archive."),
    dict(date="2026-08-26", case_id="willie-countryman",
         text="New case added to the archive: Willie Countryman (Dawson, Georgia, 1958), sourced from "
              "the Georgia Civil Rights Cold Cases Project at Emory University and PBS FRONTLINE's "
              "\u201cUn(re)solved\u201d case summary."),
    dict(date="2026-08-26", case_id="donald-raspberry",
         text="New case added to the archive: Donald Raspberry (Okolona, Mississippi, 1965), sourced "
              "from PBS FRONTLINE's \u201cUn(re)solved\u201d case summary and the DOJ's 2010 Notice to "
              "Close File."),
    dict(date="2026-08-26", case_id="william-henry-lee",
         text="New case added to the archive: William Henry Lee (Goshen Springs, Mississippi, 1965), "
              "sourced from the DOJ's Civil Rights Division case file."),
    dict(date="2026-08-26", case_id="charles-brown",
         text="New case added to the archive: Charles Brown (Benton, Mississippi, 1957), sourced from "
              "PBS FRONTLINE's \u201cUn(re)solved\u201d case summary and the DOJ's 2010 Notice to Close "
              "File."),
    dict(date="2026-08-26", case_id="dan-carter-sanders",
         text="New case added to the archive: Dan Carter Sanders (Cleveland Township, North Carolina, "
              "1946), sourced from PBS FRONTLINE's \u201cUn(re)solved\u201d case summary and the DOJ's "
              "2019 Notice to Close File."),
    dict(date="2026-08-26", case_id="felix-hall",
         text="New case added to the archive: Felix Hall (Fort Benning, Georgia, 1941), sourced from The "
              "Washington Post's 2016 investigation and the U.S. Army's 2021 memorial plaque text. This "
              "remains the only known lynching to have occurred on a U.S. military base."),
    dict(date="2026-08-26", case_id="leonard-mccowin",
         text="New case added to the archive: Leonard McCowin (Center, Texas, 1947), sourced from the "
              "Civil Rights Cold Case Records Review Board's official federal case file and Capital B "
              "News's 2025 investigative reporting."),
    dict(date="2026-08-26", case_id="thomas-coleman",
         text="New case added to the archive: Thomas Coleman (Salt Lake City, Utah, 1866), sourced from "
              "the University of Utah's \u201cRacial Lynching in Utah\u201d and \u201cCentury of Black "
              "Mormons\u201d exhibits. This case is directly connected to William \u201cSam Joe\u201d "
              "Harvey's case, documented in this archive as case #061 \u2014 both men were killed in Salt "
              "Lake City, 17 years apart, and were jointly memorialized in a 2022 ceremony."),
    dict(date="2026-08-26", case_id="william-harvey",
         text="New case added to the archive: William \u201cSam Joe\u201d Harvey (Salt Lake City, Utah, "
              "1883), sourced from the University of Utah's Marriott Library exhibit on racial lynching "
              "in Utah and the Utah State Historical Society. This is the first Utah case documented in "
              "the archive."),
    dict(date="2026-08-26", case_id="timothy-pettis",
         text="New case added to the archive: Timothy Pettis (Coos Bay, Oregon, 1924), sourced from "
              "Oregon Historical Quarterly and OPB's \u201cOregon Experience\u201d documentary. This case "
              "directly connects to Alonzo Tucker's case, documented in this archive as case #059 \u2014 "
              "both men were killed in the same Coos Bay waters, twenty-two years apart."),
    dict(date="2026-08-26", case_id="alonzo-tucker",
         text="New case added to the archive: Alonzo Tucker (Coos Bay, Oregon, 1902), sourced from the "
              "Equal Justice Initiative's historical marker and the Oregon Remembrance Project. This is "
              "the first Oregon case documented in the archive, and remains the only documented lynching "
              "of a Black person in the state's history."),
    dict(date="2026-08-26", case_id="clinton-melton",
         text="New case added to the archive: Clinton Melton (Glendora, Mississippi, 1955), sourced from "
              "the DOJ's Civil Rights Division case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case "
              "summary."),
    dict(date="2026-08-26", case_id="carol-jenkins",
         text="New case added to the archive: Carol Jenkins (Martinsville, Indiana, 1968), sourced from "
              "PBS FRONTLINE's \u201cUn(re)solved\u201d case summary and the African American Registry."),
    dict(date="2026-08-26", case_id="john-wesley-wilder",
         text="New case added to the archive: John Wesley Wilder (Ruston, Louisiana, 1965), sourced from "
              "the DOJ's 2011 Notice to Close File and Type Investigations' 2023 investigative report."),
    dict(date="2026-08-26", case_id="darrion-carrington",
         text="New case added to the archive: Darrion \u201cPritz\u201d Carrington (Boston, Massachusetts, "
              "2008), sourced from the Boston Police Department's official unsolved homicides list and "
              "Boston 25 News. This is the first Massachusetts case documented in the archive."),
    dict(date="2026-08-26", case_id="jeffery-zolliecoffer",
         text="New case added to the archive: Jeffery \u201cJo Jo\u201d Zolliecoffer (Waterloo, Iowa, 1989), "
              "sourced from Iowa Cold Cases, the Iowa Attorney General's cold case files, and a "
              "contemporaneous news photograph from the 2015 \u201cGone Cold: Exploring Iowa's Unsolved "
              "Murders\u201d statewide newspaper project."),
    dict(date="2026-08-25", case_id="samuel-johnson",
         text="New case added to the archive: Samuel Johnson, known as \u201cMingo Jack\u201d (Eatontown, New "
              "Jersey, 1886), sourced from research by local historian Gary Saretzky, published by the New "
              "Jersey Social Justice Remembrance Committee. This is the first New Jersey case documented "
              "in the archive."),
    dict(date="2026-08-25", case_id="george-white",
         text="New case added to the archive: George White (Wilmington, Delaware, 1903), sourced from "
              "the Delaware Public Archives' official historical marker and the Equal Justice Initiative. "
              "This is the first Delaware case documented in the archive, and is generally regarded as the "
              "only documented lynching in the state's history."),
    dict(date="2026-08-25", case_id="preston-porter-jr",
         text="New case added to the archive: Preston Porter Jr. (Limon, Colorado, 1900), sourced from "
              "History Colorado and the Colorado Encyclopedia. This is the first Colorado case documented "
              "in the archive."),
    dict(date="2026-08-25", case_id="james-t-scott",
         text="New case added to the archive: James T. Scott (Columbia, Missouri, 1923), sourced from the "
              "State Historical Society of Missouri. This is the first Missouri case documented in the "
              "archive."),
    dict(date="2026-08-25", case_id="george-tompkins",
         text="New case added to the archive: George Tompkins (Indianapolis, Indiana, 1922), sourced from "
              "CNN and Wikipedia. This is the first Indiana case documented in the archive; his death "
              "certificate was formally corrected from suicide to homicide in 2022."),
    dict(date="2026-08-25", case_id="tulsa-race-massacre",
         text="New case added to the archive: Tulsa Race Massacre (Tulsa, Oklahoma, 1921), sourced from "
              "the DOJ Civil Rights Division's January 2025 review and evaluation, released under the "
              "Emmett Till Unsolved Civil Rights Crime Act. This is the first Oklahoma case documented in "
              "the archive, and represents an estimated 75 to 300 victims rather than a single named "
              "individual."),
    dict(date="2026-08-25", case_id="john-henry-james",
         text="New case added to the archive: John Henry James (Charlottesville, Virginia, 1898), sourced "
              "from Encyclopedia Virginia. This is the first Virginia case documented in the archive."),
    dict(date="2026-08-25", case_id="duluth-lynchings",
         text="New case added to the archive: Elias Clayton, Elmer Jackson & Isaac McGhie (Duluth, "
              "Minnesota, 1920), sourced from the Minnesota Historical Society and Smithsonian Magazine. "
              "This is the first Minnesota case documented in the archive."),
    dict(date="2026-08-25", case_id="wade-hampton",
         text="New case added to the archive: Wade Hampton (Rock Springs, Wyoming, 1917), sourced from "
              "WyoHistory.org's account drawn from the original coroner's inquest transcript. This is the "
              "first Wyoming case documented in the archive."),
    dict(date="2026-08-25", case_id="whitfield-and-whitney",
         text="New case added to the archive: Ed Whitfield & Earl Whitney (Chapmanville, West Virginia, "
              "1919), sourced from the West Virginia Encyclopedia and The Clio. This is the first West "
              "Virginia case documented in the archive."),
    dict(date="2026-08-25", case_id="will-brown",
         text="New case added to the archive: Will Brown (Omaha, Nebraska, 1919), sourced from History "
              "Nebraska (the state historical society) and PBS's American Experience. This is the first "
              "Nebraska case documented in the archive."),
    dict(date="2026-08-25", case_id="lester-mitchell",
         text="New case added to the archive: Lester Mitchell (Dayton, Ohio, 1966), sourced from the "
              "Dayton Daily News and BlackPast.org. This is the first Ohio case documented in the "
              "archive."),
    dict(date="2026-08-25", case_id="timothy-thomas",
         text="New case added to the archive: Timothy Thomas (Cincinnati, Ohio, 2001), sourced from The "
              "Washington Post and the IAED Journal's case retrospective."),
    dict(date="2026-08-25", case_id="matthew-williams",
         text="New case added to the archive: Matthew Williams (Salisbury, Maryland, 1931), sourced from "
              "the Maryland State Archives and the International Center for Transitional Justice. This is "
              "the first Maryland case documented in the archive."),
    dict(date="2026-08-25", case_id="carl-hampton",
         text="New case added to the archive: Carl Hampton (Houston, Texas, 1970), sourced from the "
              "Houston Chronicle and Liberation News."),
    dict(date="2026-08-25", case_id="james-powell",
         text="New case added to the archive: James Powell (Manhattan, New York, 1964), sourced from "
              "extensive contemporaneous and historical reporting on the Harlem riot of 1964. This is the "
              "first New York case documented in the archive."),
    dict(date="2026-08-25", case_id="rogers-hamilton",
         text="New case added to the archive: Rogers Hamilton (Hayneville, Alabama, 1957), sourced from "
              "the DOJ's 2016 Notice to Close File and Alabama Reporter's 2025 investigative follow-up."),
    dict(date="2026-08-25", case_id="eddie-cook",
         text="New case added to the archive: Eddie Cook (Detroit, Michigan, 1965), sourced from the DOJ's "
              "2020 Notice to Close File and PBS FRONTLINE's \u201cUn(re)solved\u201d case summary. This is "
              "the first Michigan case documented in the archive."),
    dict(date="2026-08-25", case_id="lee-edward-culbreath",
         text="New case added to the archive: Lee Edward Culbreath (Portland, Arkansas, 1965), sourced "
              "from the DOJ's 2019 Notice to Close File and the Encyclopedia of Arkansas."),
    dict(date="2026-08-25", case_id="elbert-williams",
         text="New case added to the archive: Elbert Williams (Brownsville, Tennessee, 1940), sourced from "
              "the DOJ's Civil Rights Division case file and BlackPast.org. This is the first Tennessee "
              "case documented in the archive, and the earliest case tied to formal NAACP civil rights "
              "organizing."),
    dict(date="2026-08-25", case_id="henry-marrow",
         text="New case added to the archive: Henry \u201cDickie\u201d Marrow Jr. (Oxford, North Carolina, "
              "1970), sourced from the DOJ's Civil Rights Division case file and the North Carolina "
              "Department of Natural and Cultural Resources. This is the first North Carolina case "
              "documented in the archive."),
    dict(date="2026-08-25", case_id="donna-ann-reason",
         text="New case added to the archive: Donna Ann Reason (Chester, Pennsylvania, 1970), sourced from "
              "the DOJ's February 2025 Notice to Close File and PBS FRONTLINE's \u201cUn(re)solved\u201d "
              "case summary. This is the first Pennsylvania case documented in the archive."),
    dict(date="2026-08-25", case_id="isaiah-nixon",
         text="New case added to the archive: Isaiah Nixon (Alston, Georgia, 1948), sourced from the "
              "Georgia Civil Rights Cold Cases Project at Emory University and the federal Civil Rights "
              "Cold Case Records Review Board. This is the first Georgia case documented in the archive."),
    dict(date="2026-08-25", case_id="orangeburg-massacre",
         text="New case added to the archive: Samuel Hammond, Henry Smith & Delano Middleton (Orangeburg, "
              "South Carolina, 1968), sourced from BlackPast.org and the Lowcountry Digital History "
              "Initiative. This is the first South Carolina case documented in the archive."),
    dict(date="2026-08-24", case_id="frank-morris",
         text="Expanded the case summary with detail from the DOJ's Notice to Close File: the file names "
              "four Silver Dollar Group members \u2014 E.D. Morace, Tommie Lee Jones, Thor Lee Torgersen, "
              "and James Lee Scarborough \u2014 identified by FBI informants, and links this case to the "
              "same Klan cell as Wharlest Jackson Sr. and Joseph Edwards. Previously this connection was "
              "not named."),
    dict(date="2026-08-24", case_id="john-allen",
         text="New case added to the archive: John Allen (Des Moines, Iowa, 1864), sourced from Iowa "
              "Unsolved Murders: Historic Cases, drawing on contemporary newspaper accounts and an 1898 "
              "county history. This is the first Iowa case documented in the archive."),
    dict(date="2026-08-24", case_id="nicholas-a-brown",
         text="New case added to the archive: Nicholas A. Brown (Davenport, Iowa, 2021), sourced from the "
              "Iowa Attorney General's office and the Quad-City Times."),
    dict(date="2026-08-24", case_id="brandon-mcclelland",
         text="New case added to the archive: Brandon McClelland (Paris, Texas, 2008), sourced from "
              "contemporaneous news reporting and court records. This is currently the most recent case "
              "documented in the archive after Alonzo Brooks (2004), filling a gap in the archive's "
              "1970s\u20132000s coverage."),
    dict(date="2026-08-24", case_id="claude-neal",
         text="New case added to the archive: Claude Neal (Greenwood, Florida, 1934), sourced from the "
              "DOJ's Civil Rights Division case file and Explore Southern History. This is currently the "
              "earliest case documented in the archive."),
    dict(date="2026-08-24", case_id="samuel-oquinn",
         text="New case added to the archive: Samuel O'Quinn (Centreville, Mississippi, 1959), sourced "
              "from the DOJ's 2012 Notice to Close File and PBS FRONTLINE's \u201cUn(re)solved\u201d case "
              "summary."),
    dict(date="2026-08-24", case_id="willie-edwards-jr",
         text="New case added to the archive: Willie Edwards Jr. (Montgomery, Alabama, 1957), sourced "
              "from the DOJ's Civil Rights Division case file and its 2013 Notice to Close File."),
    dict(date="2026-08-24", case_id="isadore-banks",
         text="New case added to the archive: Isadore Banks (Marion, Arkansas, 1954), sourced from the "
              "DOJ's Civil Rights Division case file and the Encyclopedia of Arkansas."),
    dict(date="2026-08-24", case_id="mack-charles-parker",
         text="New case added to the archive: Mack Charles Parker (Poplarville, Mississippi, 1959), "
              "sourced from PBS FRONTLINE's \u201cUn(re)solved\u201d case summary and Mississippi Today."),
    dict(date="2026-08-24", case_id="joseph-edwards",
         text="New case added to the archive: Joseph Edwards (Vidalia, Louisiana, 1964), sourced from the "
              "DOJ's Civil Rights Division case file and its 2013 Notice to Close File."),
    dict(date="2026-08-24", case_id="louis-allen",
         text="New case added to the archive: Louis Allen (Liberty, Mississippi, 1964), sourced from the "
              "DOJ's Civil Rights Division case file and its 2015 Notice to Close File."),
    dict(date="2026-08-24", case_id="oneal-moore",
         text="New case added to the archive: Oneal Moore (Varnado, Louisiana, 1965), sourced from the "
              "DOJ's Civil Rights Division case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case "
              "summary."),
    dict(date="2026-08-24", case_id="clifton-walker",
         text="New case added to the archive: Clifton Walker (Woodville, Mississippi, 1964), sourced from "
              "the DOJ's Civil Rights Division case file and its 2013 Notice to Close File."),
    dict(date="2026-08-24", case_id="johnnie-mae-chappell",
         text="New case added to the archive: Johnnie Mae Chappell (Jacksonville, Florida, 1964), sourced "
              "from the DOJ's 2014 Notice to Close File and PBS FRONTLINE's \u201cUn(re)solved\u201d case "
              "summary."),
    dict(date="2026-08-24", case_id="wharlest-jackson-sr",
         text="New case added to the archive: Wharlest Jackson Sr. (Natchez, Mississippi, 1967), sourced "
              "from the DOJ's Civil Rights Division case file and PBS FRONTLINE's \u201cAmerican "
              "Reckoning.\u201d"),
    dict(date="2026-08-24", case_id="frank-morris",
         text="New case added to the archive: Frank Morris (Ferriday, Louisiana, 1964), sourced from the "
              "DOJ's Civil Rights Division case file and PBS FRONTLINE's \u201cUn(re)solved\u201d case "
              "summary."),
    dict(date="2026-08-24", case_id="george-lee",
         text="New case added to the archive: Rev. George Lee (Belzoni, Mississippi, 1955), sourced from "
              "the DOJ's Civil Rights Division case file and the Southern Poverty Law Center's case "
              "summary."),
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
    build_statistics()
    build_quiz()
    build_saved_cases()
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
    build_silver_dollar_group()
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
