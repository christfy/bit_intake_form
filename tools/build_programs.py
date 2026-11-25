"""Builds data/programs.json: the "here's what we think" drafts for every BiT offering.

Every value carries a confidence:
  doc     - stated in BiT's own documents (source ids in src)
  guess   - our best reading; needs BiT's yes
  unknown - nothing written down; ask BiT
Run: python3 tools/build_programs.py
"""
import json, os

CONF = 'https://tulsaforyou.atlassian.net/wiki/spaces/IST/pages/'
SOURCES = {
    'HB':     {'title': 'Intake & Review Handbook (W.E. Build), Nov 20', 'url': ''},
    'INV':    {'title': 'Intake & Review Inventory / Workflow Intake Form (Gabe), Nov 24', 'url': ''},
    'BU-PM':  {'title': 'Build Up Program - Process Mapping Document', 'url': CONF + '326205447'},
    'BU-MTG': {'title': '2026-04-07 Build Up w/ Charmane Harris', 'url': CONF + '326270981'},
    'BU-T':   {'title': 'BIT Q&A - BUILD UP Tech', 'url': CONF + '466288641'},
    'BU-C':   {'title': 'BIT Q&A - BUILD UP CPG', 'url': CONF + '466714627'},
    'FORMS':  {'title': 'DD-Handoff-V4 · 6 · Every question we ask (live Typeform definitions)', 'url': CONF + '485392387'},
    'FF-PM':  {'title': 'DRAFT Process Mapping: Female Founders Pitch Night', 'url': CONF + '328433678'},
    'FF':     {'title': 'BIT Q&A - Female Founders Pitch Night', 'url': CONF + '466616355'},
    'PPN':    {'title': 'BIT Q&A - Product Pitch Night', 'url': CONF + '466812933'},
    '1921':   {'title': 'BIT Q&A - 1921 Award', 'url': CONF + '466616363'},
    'FFFM':   {'title': 'BIT Q&A - First Friday Founders Market', 'url': CONF + '466878470'},
    'QBIT':   {'title': 'Questions for Build in Tulsa - internal, with evidence', 'url': CONF + '473104407'},
    'LIFE':   {'title': 'BIT - Application lifecycle, review and conversion', 'url': CONF + '481951804'},
    'SC':     {'title': 'BIT - Service Catalog', 'url': CONF + '499384323'},
}

def f(v, conf='doc', src=(), note=''):
    d = {'v': v, 'conf': conf, 'src': list(src)}
    if note: d['note'] = note
    return d

def chk(id, text, effect, conf='doc', src=(), note=''):
    d = {'id': id, 'text': text, 'effect': effect, 'conf': conf, 'src': list(src)}
    if note: d['note'] = note
    return d

def step(id, kind, name, who, judge, outcomes, conf='doc', src=(), count=None, scale=None,
         criteria=None, groups=None, scheduled=False, rubric='', note=''):
    d = {'id': id, 'kind': kind, 'name': name, 'who': who, 'count': count, 'judge': judge,
         'scale': scale, 'criteria': criteria or [], 'outcomes': outcomes, 'scheduled': scheduled,
         'rubric': rubric, 'conf': conf, 'src': list(src), 'note': note}
    if groups: d['groups'] = groups
    return d

def after(id, text, conf='doc', src=()):
    return {'id': id, 'text': text, 'conf': conf, 'src': list(src)}

def q(id, text, why=''):
    return {'id': id, 'q': text, 'why': why}

WE_SCREEN = ['Tulsa location / relocation readiness', 'Company age (founded less than 5 years ago)',
             'Incorporated status', 'Number of paying clients, users or contracts', 'KPI tracking readiness',
             'Accelerator saturation (at most 1 prior accelerator)', 'Revenue generated (recent)',
             'Stage and product-market fit (in market, emerging or strong PMF)',
             'Recurring revenue / early revenue quality', 'Customer acquisition strategy clarity',
             'Commitment to 25% growth', 'Revenue']
WE_INTERVIEW = ['Founder / solution fit', 'Market and go-to-market strategy', 'Tulsa commitment', 'ICP clarity',
                'Traction proof', 'Sales process and pipeline', 'Business acumen', '25% growth potential']

programs = []

# ---------------------------------------------------------------- W.E. Build (the template)
programs.append({
    'id': 'we-build', 'name': 'W.E. Build', 'group': 'main', 'kind': 'Accelerator', 'template': True,
    'short': 'Twelve-week, full-time, in-person accelerator for women founders who are already in market and ready to scale.',
    'basics': {
        'entry': f('applying online', 'doc', ['HB']),
        'form': f('W.E. Build Application 2026', 'doc', ['FORMS']),
        'first': f('an optional interest form', 'doc', ['HB', 'FORMS']),
        'rhythm': f('once a year', 'doc', ['HB']),
        'deadline': f('April 10, 2026', 'doc', ['QBIT']),
        'size': f('about 10 founders', 'doc', ['QBIT']),
        'decider': f('a selection committee of staff and community members', 'doc', ['HB']),
    },
    'checks': [
        chk('c1', 'Is in, or has finished, another accelerator (ACT Tulsa, BiT Techstars, Lightship)', 'disqualifies', 'guess', ['HB', 'FORMS'],
            'The handbook calls this the knock-out question. The screening rubric also scores "at most 1 prior accelerator", so which is it?'),
        chk('c2', 'Lives in Tulsa or will relocate for the program', 'noted', 'guess', ['QBIT', 'INV'], 'Scored in screening, not a hard no.'),
        chk('c3', 'Company is incorporated (LLC, S-Corp or C-Corp)', 'noted', 'guess', ['QBIT', 'INV']),
        chk('c4', 'Can commit 40 hours a week in person, Sept 1 to Nov 20', 'unknown', 'doc', ['FORMS']),
    ],
    'steps': [
        step('s1', 'screen', 'Application screening', ['staff'], 'scored', ['advance', 'hold', 'decline'], 'doc', ['HB', 'INV'],
             count=1, scale=4, criteria=WE_SCREEN, rubric='W.E. Build Screening',
             note='Nov 19: one person files the review for a stage. The older pages showed 3 screeners.'),
        step('s2', 'interview', 'First round interview', ['staff'], 'scored', ['advance', 'decline'], 'doc', ['HB', 'INV'],
             count=1, scale=4, criteria=WE_INTERVIEW, scheduled=True, rubric='Accelerator Interview'),
        step('s3', 'interview', 'Second round interview', ['committee', 'community'], 'scored', ['advance', 'decline'], 'doc', ['HB'],
             count=1, scale=4, criteria=WE_INTERVIEW, scheduled=True, rubric='Accelerator Interview',
             note='Same rubric as round one. Panel of 4 internal and 3 to 5 community members.'),
        step('s4', 'committee', 'Committee decision', ['committee'], 'discussion', ['advance', 'waitlist', 'decline'], 'doc', ['HB']),
    ],
    'after': [
        after('a1', 'Conditional offer', 'doc', ['HB']),
        after('a2', 'Reference check (a short questionnaire to referees)', 'doc', ['HB', 'LIFE']),
        after('a3', 'Background check', 'guess', ['HB']),
        after('a4', 'Agreements signed, then orientation', 'guess', ['HB']),
    ],
    'today': ['Accepted', 'Rejected', 'Accepted/Declined Offer', 'Active Cohort', 'Declination'],
    'todaySrc': ['LIFE'],
    'questions': [
        q('q1', 'Are the second interview and the committee decision really one step?', 'If yes, W.E. Build runs on three steps instead of four.'),
        q('q2', 'Do you screen applications as they come in, or all together after the deadline? Who assigns reviewers?'),
        q('q3', 'Which answers on the form are an automatic no?'),
        q('q4', 'After the committee says yes, what is the order: offer, reference check, background check, orientation? Does anything wait on the background check?'),
        q('q5', 'Do community reviewers enter their reviews in Salesforce?'),
    ],
    'pattern': 'Accelerator · 4-stage (v1)',
})

# ---------------------------------------------------------------- BUILD UP
programs.append({
    'id': 'build-up', 'name': 'BUILD UP', 'group': 'main', 'kind': 'Pre-accelerator',
    'short': 'Four-week pre-accelerator for early founders, with a Tech track and a CPG (consumer product) track.',
    'basics': {
        'entry': f('applying online', 'doc', ['BU-PM']),
        'form': f('BUILD UP Application 2026 (one form for both tracks)', 'doc', ['FORMS', 'BU-C'],
                  'Three different application links are live on the website.'),
        'first': f('an optional info session on Eventbrite', 'doc', ['BU-T']),
        'rhythm': f('once a year', 'guess', ['BU-T']),
        'deadline': f('Feb 22 or Mar 1, 2026 (both are on the site)', 'guess', ['QBIT', 'BU-T']),
        'size': f('up to 35 Tech and at least 15 CPG founders', 'doc', ['BU-T', 'BU-C']),
        'decider': f('the program coordinator and program manager, in a weekly meeting', 'doc', ['BU-PM', 'BU-MTG']),
    },
    'checks': [
        chk('c1', 'Based in Tulsa or committed to building here', 'unknown', 'doc', ['BU-T'], 'Is this checked, or self-declared?'),
        chk('c2', 'Picks a track: Tech or CPG', 'noted', 'doc', ['FORMS', 'BU-PM']),
        chk('c3', 'Is early-stage', 'unknown', 'doc', ['BU-PM']),
        chk('c4', 'Willing to do customer interviews, assignments and coaching', 'unknown', 'doc', ['FORMS']),
    ],
    'steps': [
        step('s1', 'check', 'Eligibility check', ['pc'], 'checklist', ['advance', 'decline'], 'doc', ['BU-PM'],
             count=1, note='The coordinator checks location, track and stage in the Google Sheet.'),
        step('s2', 'interview', 'Interview', ['pc', 'pm'], 'scored', ['advance', 'decline'], 'doc', ['BU-PM', 'FORMS'],
             count=1, scheduled=True, rubric='BUILD UP Intake Summary',
             groups=[
                 {'label': 'Tech track', 'items': ['Problem clarity and relevance', 'Customer understanding and discovery readiness',
                                                   'Product approach and validation fit', 'Coachability and learning orientation',
                                                   'Commitment and program fit']},
                 {'label': 'CPG track', 'items': ['Buyer / consumer problem clarity', 'Customer discovery and demand signals',
                                                  'Product concept readiness', 'Coachability and learning orientation',
                                                  'Commitment and program fit']},
             ],
             note='On Zoom, booked through Calendly. The coordinator or manager fills in the intake summary and gives a recommendation.'),
        step('s3', 'committee', 'Weekly decision meeting', ['pc', 'pm'], 'discussion', ['advance', 'waitlist', 'decline'], 'doc', ['BU-PM', 'BU-MTG']),
    ],
    'after': [
        after('a1', 'Welcome email and onboarding forms (onboarding, marketing release, knowledge check)', 'doc', ['BU-PM']),
        after('a2', 'To complete: 4 workshops, at least 1 coaching session and a finished data room', 'doc', ['BU-T']),
        after('a3', '$100 completion payment', 'doc', ['SC']),
    ],
    'today': ['New Lead', 'Incomplete', 'Submitted', 'Eligible', 'Ineligible', 'Ready for Interview', 'Interview Scheduled',
              'Interview Complete', 'Accepted', 'Waitlisted', 'Declined'],
    'todaySrc': ['BU-PM'],
    'questions': [
        q('q1', 'Is BUILD UP one program with two tracks, or two separate programs?', 'This decides how it is set up and reported.'),
        q('q2', 'Which application link is the live one, and which close date is right: Feb 22 or Mar 1?'),
        q('q3', 'Are CPG applicants decided in the same weekly meeting as Tech?'),
        q('q4', 'Does every eligible applicant get an interview?'),
        q('q5', 'How are the interview ratings scored? 1 to 4, like W.E. Build?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- Female Founders Pitch Night
programs.append({
    'id': 'ffpn', 'name': 'Female Founders Pitch Night', 'group': 'main', 'kind': 'Pitch program',
    'short': 'Six-week cohort for female-identifying founders with a tech product, ending in a live Pitch Night with cash prizes.',
    'basics': {
        'entry': f('applying online', 'doc', ['FF-PM']),
        'form': f('Female Founders Pitch Night 2026 Application', 'doc', ['FORMS']),
        'first': f('', 'doc'),
        'rhythm': f('once a year (it has run up to three times a year before)', 'guess', ['FF']),
        'deadline': f('March 27, 2026 (extended from March 6)', 'doc', ['FF']),
        'size': f('7 to 9 founders', 'doc', ['FF']),
        'decider': f('a screening committee of staff and panelists', 'doc', ['FF', 'FF-PM']),
    },
    'checks': [
        chk('c1', 'Startup is based in Tulsa', 'disqualifies', 'guess', ['FF'], 'The website says Tulsa. Confluence says Tulsa or Oklahoma.'),
        chk('c2', 'Product is tech or tech-enabled', 'disqualifies', 'guess', ['FF', 'FORMS']),
        chk('c3', 'Already has an MVP', 'disqualifies', 'guess', ['FF', 'FORMS']),
        chk('c4', 'Company is under 5 years old', 'unknown', 'doc', ['FF']),
        chk('c5', 'Is in a prohibited industry', 'disqualifies', 'doc', ['FF'], 'No list of industries is written down.'),
        chk('c6', 'Applied before with the same company', 'disqualifies', 'doc', ['FF']),
        chk('c7', 'Is currently in an accelerator (ACT Tulsa, W.E. Build, Lightship)', 'unknown', 'doc', ['FORMS']),
    ],
    'steps': [
        step('s1', 'check', 'Eligibility check', ['staff'], 'checklist', ['advance', 'decline'], 'doc', ['FF-PM'],
             note='Checks location, prior participation and industry. A no reads "did not meet criteria".'),
        step('s2', 'screen', 'Application scoring', ['staff', 'judges'], 'scored', ['advance', 'decline'], 'doc', ['FF-PM', 'FF'],
             scale=4, rubric='FFPN Screening',
             criteria=['Founder', 'Product (problem and solution)', 'Business model', 'Traction', 'Market', 'Team',
                       'Need for the Female Founders Pitch Night workshops'],
             note='Staff and/or panelists score in Google Sheets or the 2026 Airtable base.'),
        step('s3', 'interview', 'Interview', ['committee'], 'scored', ['advance', 'decline'], 'doc', ['FF-PM', 'FF'],
             scale=4, scheduled=True, rubric='FFPN Screening',
             note='Booked on Calendly, held on Zoom. Panelists fill in scorecards and a recommendation for the cohort. No-shows are recorded.'),
        step('s4', 'committee', 'Final selection', ['committee'], 'discussion', ['advance', 'decline'], 'guess', ['FF-PM'],
             note='"Scores are aggregated for final selection." Is this a meeting, or does the top score win a place?'),
    ],
    'after': [
        after('a1', 'Onboarding and marketing forms, then orientation', 'doc', ['FF-PM', 'FF']),
        after('a2', 'Workshops (six or seven; the sources differ), weekly coaching and pitch practices', 'guess', ['FF']),
        after('a3', 'Only founders who complete the full program can pitch', 'doc', ['FF']),
        after('a4', 'Pitch Night: judges hear a 5-minute pitch and 3 minutes of Q&A. Prizes $10,000, $5,000, $2,500 and $1,000 Audience Choice; $100 to everyone else', 'doc', ['FF']),
        after('a5', 'W-9 collected so prizes and stipends can be paid', 'doc', ['FF-PM']),
    ],
    'today': ['Interested', 'Applied', 'Eligible', 'Ineligible', 'Under Review', 'Reviewed', 'Disqualified', 'Scheduled',
              'Completed', 'No Show', 'Selected To Participate', 'Not Selected To Participate'],
    'todaySrc': ['FF-PM', 'LIFE'],
    'questions': [
        q('q1', 'Who sits on the screening committee, and is there a cut-off score?'),
        q('q2', 'When are interviews held now that the deadline moved to March 27?', 'The website still lists March 9 to 13.'),
        q('q3', 'Is eligibility Tulsa-based, or anywhere in Oklahoma?'),
        q('q4', 'What does "complete the full program" mean, so a founder can pitch?'),
        q('q5', 'Which is the record: Typeform, the FFPN Airtable base, or Google Sheets?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- Product Pitch Night
programs.append({
    'id': 'ppn', 'name': 'Product Pitch Night', 'group': 'main', 'kind': 'Pitch program',
    'short': 'Eight-week training for founders building physical products, ending in a Pitch Night with cash prizes. 2026 is the fourth cohort.',
    'basics': {
        'entry': f('applying online', 'doc', ['PPN']),
        'form': f('Product Pitch Night 2026 Application', 'doc', ['FORMS']),
        'first': f('', 'doc'),
        'rhythm': f('once a year', 'guess', ['PPN']),
        'deadline': f('August 21, 2026, with founders picked by September 11', 'doc', ['PPN', 'QBIT']),
        'size': f('', 'unknown'),
        'decider': f('a screening committee', 'doc', ['PPN']),
    },
    'checks': [
        chk('c1', 'Startup in Tulsa or the surrounding Oklahoma area, and founder lives in Oklahoma', 'disqualifies', 'doc', ['PPN']),
        chk('c2', 'Has a functioning MVP', 'disqualifies', 'doc', ['PPN', 'FORMS']),
        chk('c3', 'Physical product, not software alone', 'disqualifies', 'guess', ['PPN'], 'The form still offers "Software" as a product category.'),
        chk('c4', 'Team of up to three founders', 'disqualifies', 'doc', ['PPN']),
        chk('c5', 'Cannabis, tobacco, alcohol or adult entertainment, or a registered nonprofit', 'disqualifies', 'doc', ['PPN']),
        chk('c6', 'Works for TCF or GKFF, or is family of someone who does', 'disqualifies', 'doc', ['PPN']),
        chk('c7', 'Is or was in ACT House, BiT Techstars, Lightship or W.E. Build', 'unknown', 'doc', ['FORMS', 'PPN']),
    ],
    'steps': [
        step('s1', 'check', 'Eligibility check', ['staff'], 'checklist', ['advance', 'decline'], 'guess', ['PPN']),
        step('s2', 'interview', 'Screening committee interview', ['committee'], 'scored', ['advance', 'hold', 'decline'], 'doc', ['PPN'],
             rubric='PPN Screening', scheduled=True,
             criteria=['Problem-solution fit and value proposition', 'Target customer / market opportunity',
                       'Team - product/service fit', 'Traction', 'Pitch deck / pitch', 'Need for the Product Pitch Night workshops'],
             note='Each committee record has interview notes, an interview summary and a final score.'),
        step('s3', 'committee', 'Final selection', ['committee'], 'discussion', ['advance', 'decline'], 'guess', ['PPN']),
    ],
    'after': [
        after('a1', 'One-on-one coaching and workshops (Sept 22 to Oct 15)', 'doc', ['PPN']),
        after('a2', 'Four hours of in-person pitch practice and a dress rehearsal', 'doc', ['PPN']),
        after('a3', 'Introductions to Tulsa and Oklahoma manufacturing partners', 'doc', ['PPN']),
        after('a4', 'Pitch Night prizes: $10,000, $5,000, $2,500 and $1,000 Audience Choice', 'doc', ['SC']),
    ],
    'today': ['Contestant', 'On Hold', 'Rejected', 'Winner'],
    'todaySrc': ['LIFE'],
    'questions': [
        q('q1', 'Does the committee score the written application before the interview, or only after it?'),
        q('q2', 'Who sits on the screening committee?'),
        q('q3', 'Is software-only eligible?', 'The website says no; the form lists Software as a category.'),
        q('q4', 'Does a "yes" to "are you in an accelerator?" rule someone out?'),
        q('q5', 'Must founders complete the program to pitch?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- 1921 Award
programs.append({
    'id': 'award-1921', 'name': '1921 Award', 'group': 'main', 'kind': 'Award',
    'short': 'Award honoring eight Tulsans who carry the spirit of Black Wall Street. People nominate themselves or someone else.',
    'basics': {
        'entry': f('being nominated, by themselves or someone else', 'doc', ['FORMS', '1921']),
        'form': f('1921 Application 2026', 'doc', ['FORMS']),
        'first': f('', 'doc'),
        'rhythm': f('once a year', 'doc', ['FORMS']),
        'deadline': f('April 3, 2026', 'doc', ['1921']),
        'size': f('8 awardees', 'doc', ['1921']),
        'decider': f('a committee of BiT team members and Tulsa community leaders', 'doc', ['1921']),
    },
    'checks': [
        chk('c1', 'Born in Tulsa, or has lived here 10+ years', 'disqualifies', 'doc', ['1921', 'FORMS'], 'The form asks "half their life"; the website says 10+ years.'),
        chk('c2', 'Nominee is 18 or older', 'disqualifies', 'doc', ['1921']),
        chk('c3', 'Runs a for-profit business that has operated 3+ years, with a legal structure', 'disqualifies', 'doc', ['1921']),
        chk('c4', 'Past participant of W.E. Build, BiT Techstars or ACT House, or a pitch-night winner', 'disqualifies', 'doc', ['1921']),
        chk('c5', 'Cannabis, adult industry or nonprofit; or works for TCF/GKFF or is family of someone who does', 'disqualifies', 'doc', ['1921']),
        chk('c6', 'Eligible to work in the U.S.', 'unknown', 'doc', ['QBIT'], 'Published, but the form does not ask it.'),
    ],
    'steps': [
        step('s1', 'check', 'Eligibility check', ['staff'], 'checklist', ['advance', 'decline'], 'guess', ['1921'],
             note='Nobody is named as checking nominees against past BiT programs.'),
        step('s2', 'committee', 'Selection committee', ['committee', 'community'], 'scored', ['advance', 'decline'], 'guess', ['1921'],
             rubric='1921 Award',
             criteria=['Business success and impact', 'Commitment to the Tulsa community',
                       'Embodies the resilient, innovative spirit of Black Wall Street'],
             note='The three criteria are published. Whether they are scored is not, and no scores are kept today.'),
    ],
    'after': [
        after('a1', 'Awardees notified', 'guess'),
        after('a2', 'Award ceremony (late May or early June); attendance is required', 'doc', ['1921']),
        after('a3', 'Permission to share the awardee\'s story, photos and testimonials', 'unknown', ['1921']),
    ],
    'today': ['Awarded', 'Rejected'],
    'todaySrc': ['LIFE'],
    'questions': [
        q('q1', 'Are nominees interviewed, or chosen from the nomination alone?'),
        q('q2', 'Are the three criteria scored? If so, where do the scores go?'),
        q('q3', 'Who checks a nominee against past BiT programs?'),
        q('q4', 'Is it always eight awardees?'),
        q('q5', 'Do you collect permission to publicize awardees and testimonials?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- First Friday Founders Market
programs.append({
    'id': 'first-friday', 'name': 'First Friday Founders Market', 'group': 'main', 'kind': 'Market',
    'short': 'Evening market at BiT HQ (6 to 9 PM) where selected local businesses get free vending space.',
    'basics': {
        'entry': f('applying online for a market date', 'doc', ['FFFM']),
        'form': f('First Friday application (Typeform)', 'doc', ['FFFM', 'FORMS']),
        'first': f('', 'doc'),
        'rhythm': f('monthly, on a rolling basis (five dates are published for 2026)', 'guess', ['FFFM']),
        'deadline': f('the 3rd Friday of the month before the market', 'guess', ['FFFM']),
        'size': f('', 'unknown'),
        'decider': f('', 'unknown'),
    },
    'checks': [
        chk('c1', 'Is a licensed business in Tulsa', 'unknown', 'doc', ['FORMS'], 'The form asks; nothing says what a "no" does.'),
        chk('c2', 'December Holiday Market is invite-only', 'noted', 'doc', ['FFFM']),
    ],
    'steps': [
        step('s1', 'screen', 'Vendor selection', ['staff'], 'unknown', ['advance', 'decline'], 'guess', ['FFFM'],
             note='"Businesses are selected each month on a rolling basis." Nothing else is written down.'),
    ],
    'after': [
        after('a1', 'Vendor confirmed for a market date', 'guess'),
        after('a2', 'Sets up and sells, 6 to 9 PM at BiT HQ', 'doc', ['FFFM']),
    ],
    'today': [],
    'todaySrc': [],
    'questions': [
        q('q1', 'Who picks vendors each month, and what do they look for?'),
        q('q2', 'How many booths are there, and is there a waitlist?'),
        q('q3', 'Do vendors apply again every month?'),
        q('q4', 'How does someone get invited to the December Holiday Market?'),
        q('q5', 'Is it every month, or only the published dates?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- Future CEO Camp
programs.append({
    'id': 'future-ceo', 'name': 'Future CEO Camp', 'group': 'main', 'kind': 'Youth camp',
    'short': 'Week-long summer camp for students entering grades 6 to 12, ending in a Saturday showcase. A parent or guardian applies.',
    'basics': {
        'entry': f('a parent or guardian applying online', 'doc', ['FORMS']),
        'form': f('Future CEO Camp 2026 Participant Application', 'doc', ['FORMS']),
        'first': f('', 'doc'),
        'rhythm': f('once a year, in July', 'doc', ['FORMS']),
        'deadline': f('', 'unknown'),
        'size': f('', 'unknown'),
        'decider': f('', 'unknown'),
    },
    'checks': [
        chk('c1', 'Student attends a school in Tulsa County', 'disqualifies', 'guess', ['FORMS']),
        chk('c2', 'Student is entering grades 6 to 12', 'disqualifies', 'guess', ['FORMS']),
        chk('c3', 'Can attend the full camp week and the Saturday showcase', 'unknown', 'doc', ['FORMS']),
        chk('c4', 'Parent works for GKFF, TCF or an affiliate (W-2)', 'unknown', 'doc', ['FORMS']),
    ],
    'steps': [
        step('s1', 'check', 'Eligibility check', ['staff'], 'checklist', ['advance', 'decline'], 'guess', ['FORMS']),
        step('s2', 'screen', 'Application review', ['staff'], 'unknown', ['advance', 'decline'], 'guess', ['LIFE'],
             note='The CRM list only records Accepted or Rejected.'),
    ],
    'after': [
        after('a1', 'Family gets camp details', 'guess'),
        after('a2', 'Camp week, then the Saturday showcase', 'doc', ['FORMS']),
    ],
    'today': ['Accepted', 'Rejected'],
    'todaySrc': ['LIFE'],
    'questions': [
        q('q1', 'Is there a selection, or is it first come, first served?'),
        q('q2', 'How many spots are there?'),
        q('q3', 'Who decides, and what do you look for in the student\'s answers?'),
        q('q4', 'Does working for GKFF or TCF rule a family out?'),
    ],
    'pattern': '',
    'note': 'Camp facilitators apply on a separate form. That is staffing, so it is listed under sign-up forms.',
})

# ---------------------------------------------------------------- Post-Accelerator Support
programs.append({
    'id': 'post-accelerator', 'name': 'Post-Accelerator Support', 'group': 'main', 'kind': 'Post-accelerator',
    'short': 'Six to twelve months of support for founders who finished an accelerator and stay in Tulsa: coaching, desk space and stipends.',
    'basics': {
        'entry': f('applying online', 'doc', ['FORMS']),
        'form': f('2026 Post-Accelerator Support Program Application', 'doc', ['FORMS']),
        'first': f('an optional interest form', 'doc', ['FORMS']),
        'rhythm': f('', 'unknown'),
        'deadline': f('', 'unknown'),
        'size': f('', 'unknown'),
        'decider': f('', 'unknown'),
    },
    'checks': [
        chk('c1', 'Finished an eligible accelerator cohort (the form names ACT Tulsa Cohort 6 and BiT Techstars Cohort 6)', 'disqualifies', 'guess', ['FORMS']),
        chk('c2', 'Will stay in Tulsa for 12 months after Demo Day', 'unknown', 'doc', ['FORMS']),
        chk('c3', 'Can meet a business coach at least 4 hours a month', 'unknown', 'doc', ['FORMS']),
    ],
    'steps': [
        step('s1', 'check', 'Eligibility check', ['staff'], 'checklist', ['advance', 'decline'], 'guess', ['FORMS']),
        step('s2', 'screen', 'Application review', ['staff'], 'unknown', ['advance', 'decline'], 'guess', [],
             note='We found the form and very little else.'),
    ],
    'after': [
        after('a1', 'Coaching at least 4 hours a month, and desk space if needed', 'doc', ['FORMS']),
        after('a2', 'A completed data room unlocks stipends', 'doc', ['SC']),
    ],
    'today': ['New'],
    'todaySrc': ['LIFE'],
    'questions': [
        q('q1', 'Is this still running in 2026, and which cohorts can apply?'),
        q('q2', 'Who reviews applications? Is there an interview or a pitch?'),
        q('q3', 'Is it scored, and who makes the final call?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- ARCH Accelerator
programs.append({
    'id': 'arch', 'name': 'ARCH Accelerator', 'group': 'main', 'kind': 'Accelerator',
    'short': 'Accelerator with a 2027 application: 20 hours a week in person in Tulsa from March 30. Its form closely mirrors W.E. Build\'s.',
    'basics': {
        'entry': f('applying online', 'doc', ['FORMS']),
        'form': f('ARCH Accelerator Application 2027', 'doc', ['FORMS']),
        'first': f('the Universal Interest Form', 'guess', ['FORMS']),
        'rhythm': f('', 'unknown'),
        'deadline': f('', 'unknown'),
        'size': f('', 'unknown'),
        'decider': f('a selection committee', 'guess', ['FORMS']),
    },
    'checks': [
        chk('c1', 'Is in, or has finished, an accelerator (ACT Tulsa, BiT Techstars, W.E. Build, Lightship)', 'disqualifies', 'guess', ['FORMS'],
            'Same question as W.E. Build\'s knock-out.'),
        chk('c2', 'Lives in Tulsa', 'unknown', 'doc', ['FORMS']),
        chk('c3', 'Can commit 20 hours a week in person from March 30', 'unknown', 'doc', ['FORMS']),
    ],
    'steps': [
        step('s1', 'screen', 'Application screening', ['staff'], 'scored', ['advance', 'hold', 'decline'], 'guess', ['HB'],
             scale=4, criteria=WE_SCREEN, rubric='W.E. Build Screening', note='Assumed to work like W.E. Build.'),
        step('s2', 'interview', 'First round interview', ['staff'], 'scored', ['advance', 'decline'], 'guess', ['HB'],
             scale=4, criteria=WE_INTERVIEW, scheduled=True, rubric='Accelerator Interview'),
        step('s3', 'interview', 'Second round interview', ['committee'], 'scored', ['advance', 'decline'], 'guess', ['HB'],
             scale=4, criteria=WE_INTERVIEW, scheduled=True, rubric='Accelerator Interview'),
        step('s4', 'committee', 'Committee decision', ['committee'], 'discussion', ['advance', 'waitlist', 'decline'], 'guess', ['HB']),
    ],
    'after': [after('a1', 'Assumed to match W.E. Build: offer, checks, agreements, orientation', 'guess', ['HB'])],
    'today': [],
    'todaySrc': [],
    'questions': [
        q('q1', 'Is ARCH the next version of W.E. Build, or a separate program?'),
        q('q2', 'Does it use W.E. Build\'s scoring and interview rounds?'),
        q('q3', 'Do ARCH advisors sit on the selection committee?'),
    ],
    'pattern': 'Accelerator · 4-stage (v1)',
})

# ---------------------------------------------------------------- AfroTech Scholarship
programs.append({
    'id': 'afrotech', 'name': 'AfroTech Scholarship', 'group': 'main', 'kind': 'Scholarship',
    'short': 'A paid conference ticket for BiT founders to attend AfroTech and act as BiT ambassadors there.',
    'basics': {
        'entry': f('applying online', 'doc', ['FORMS']),
        'form': f('AfroTech 2026 Scholarship Application', 'doc', ['FORMS']),
        'first': f('', 'doc'),
        'rhythm': f('once a year', 'doc', ['FORMS']),
        'deadline': f('', 'unknown'),
        'size': f('', 'unknown'),
        'decider': f('', 'unknown'),
    },
    'checks': [
        chk('c1', 'Was in a BiT program in the last 12 months', 'disqualifies', 'guess', ['FORMS']),
        chk('c2', 'Agrees to attend the BiT happy hour at the conference', 'noted', 'doc', ['FORMS']),
    ],
    'steps': [
        step('s1', 'screen', 'Staff review', ['staff'], 'unknown', ['advance', 'decline'], 'guess', ['FORMS']),
    ],
    'after': [
        after('a1', 'BiT pays the ticket; the founder covers travel, hotel and meals', 'doc', ['FORMS']),
        after('a2', 'Serves as a BiT ambassador at the conference', 'doc', ['FORMS']),
    ],
    'today': [],
    'todaySrc': [],
    'questions': [
        q('q1', 'Who chooses, and how many tickets are there?'),
        q('q2', 'What makes a strong application?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- Business Coaching
programs.append({
    'id': 'business-coaching', 'name': 'Business Coaching', 'group': 'main', 'kind': 'Service',
    'short': 'Free coaching: eight sessions over three months, entered through its own intake form.',
    'basics': {
        'entry': f('filling in an intake form', 'doc', ['SC']),
        'form': f('', 'unknown'),
        'first': f('', 'doc'),
        'rhythm': f('any time (rolling)', 'guess', ['SC']),
        'deadline': f('', 'unknown'),
        'size': f('', 'unknown'),
        'decider': f('', 'unknown'),
    },
    'checks': [],
    'steps': [
        step('s1', 'screen', 'Intake review', ['staff'], 'unknown', ['advance', 'hold', 'decline'], 'guess', ['LIFE'],
             note='The CRM list uses Accepted, On Hold and Rejected.'),
    ],
    'after': [
        after('a1', 'Matched with a coach for eight sessions over three months', 'doc', ['SC']),
    ],
    'today': ['Accepted', 'Completed', 'On Hold', 'Rejected'],
    'todaySrc': ['LIFE'],
    'questions': [
        q('q1', 'Who reviews intake forms, and what makes someone a fit?'),
        q('q2', 'What puts someone "On Hold"?'),
        q('q3', 'Is EIR coaching part of this, or separate?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- Bookkeeping Services
programs.append({
    'id': 'bookkeeping', 'name': 'Bookkeeping Services', 'group': 'main', 'kind': 'Service',
    'short': 'Bookkeeping help for Tulsa entrepreneurs, through a short application.',
    'basics': {
        'entry': f('applying online', 'doc', ['FORMS']),
        'form': f('Bookkeeping Services Application', 'doc', ['FORMS']),
        'first': f('', 'doc'),
        'rhythm': f('', 'unknown'),
        'deadline': f('', 'unknown'),
        'size': f('', 'unknown'),
        'decider': f('', 'unknown'),
    },
    'checks': [
        chk('c1', 'Entrepreneur in the Tulsa area with an existing or planned business', 'unknown', 'doc', ['FORMS']),
    ],
    'steps': [
        step('s1', 'screen', 'Review', ['staff'], 'unknown', ['advance', 'decline'], 'guess', []),
    ],
    'after': [],
    'today': [],
    'todaySrc': [],
    'questions': [
        q('q1', 'Is this a BiT program, a partner service, or part of Business Coaching?'),
        q('q2', 'Who decides, and is it still running?'),
    ],
    'pattern': '',
})

# ---------------------------------------------------------------- forms that likely lead to no review
signups = [
    {'id': 'venture-summit', 'name': 'BUILD Venture Summit', 'what': 'Investors register for the summit (plus an interest form).', 'answer': 'signup'},
    {'id': 'turkey-drive', 'name': 'BiT Turkey Drive', 'what': 'BiT participants sign up for one of 10 holiday baskets.', 'answer': 'signup'},
    {'id': 'mlk-volunteers', 'name': 'MLK Day Parade volunteers', 'what': 'Volunteer sign-up, 2026 and 2027.', 'answer': 'signup'},
    {'id': 'universal-interest', 'name': 'Universal Interest Form', 'what': 'One front door: people pick the programs they are interested in.', 'answer': 'signup'},
    {'id': 'ce-interest', 'name': 'CE: General Interest Form', 'what': 'General interest, 7 questions.', 'answer': 'signup'},
    {'id': 'community-partner', 'name': 'Community Partnership Interest Form', 'what': 'Organizations that want to partner.', 'answer': 'signup'},
    {'id': 'webuild-interest', 'name': 'W.E. Build Cohort 4 Interest Form', 'what': 'Interest before the W.E. Build application opens.', 'answer': 'signup'},
    {'id': 'pas-interest', 'name': 'Post-Accelerator Support Interest Form', 'what': 'Interest before the full application.', 'answer': 'signup'},
    {'id': 'arch-advisors', 'name': 'ARCH Advisor sign-up', 'what': 'Advisors offer their time to ARCH.', 'answer': 'signup'},
    {'id': 'fceo-facilitators', 'name': 'Future CEO Camp facilitators', 'what': 'Adults apply to teach at the camp.', 'answer': 'unsure'},
]

dormant = [
    {'id': 'boost', 'name': 'BOOST Awards', 'what': 'CRM list records Awarded $2,500, Awarded $5,000 or Rejected. No 2026 form found.'},
    {'id': 'techstars', 'name': 'BiT Techstars Accelerator', 'what': 'Named on forms (Cohort 6) and in the CRM. No current form found.'},
    {'id': 'blueprint', 'name': 'Blueprint: Tulsa', 'what': 'Run by Visible Hands. No BiT form or CRM list found.'},
    {'id': 'act-house', 'name': 'ACT House / ACT Tulsa', 'what': 'Named as a past accelerator on several forms and in the CRM.'},
    {'id': 'lightship', 'name': 'Lightship Bootcamp', 'what': 'A CRM list exists with no statuses beyond "New".'},
    {'id': 'eir', 'name': 'EIR (entrepreneur in residence)', 'what': 'Coaching for W.E. Build and BUILD UP participants, valued at $75 an hour.'},
]

out = {
    'version': '2026-11-25',
    'org': 'Build in Tulsa',
    'sources': SOURCES,
    'programs': programs,
    'signups': signups,
    'dormant': dormant,
}
path = os.path.join(os.path.dirname(__file__), '..', 'data', 'programs.json')
with open(path, 'w') as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
print('wrote', os.path.abspath(path), len(programs), 'programs', sum(len(p['steps']) for p in programs), 'steps')
