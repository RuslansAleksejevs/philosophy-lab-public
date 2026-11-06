# Sources — essay-06-critic

This is the source record for the **critic** stage only. It covers what I retrieved and read
myself in order to check `draft-001.md` independently. It does not restate the author's
source record; where I checked one of the author's claims, the result is stated here and
the argumentative consequence is in `critique.md`.

All saved paths below are relative to the project root. The batch source directory for this
task is `batches/claude10-20260913/tasks/essay-06-critic/sources/`. Each retrieval has a
shared prefix with up to three files: `<prefix>.json` (extraction metadata),
`<prefix>.txt` (extracted text), and `<prefix>.original.html` or `.original.pdf` (raw bytes).
These retrievals are my own and are separate from the author's captures, even where the same
URL was fetched; the prefixes differ in their second component.

**Coverage vocabulary**

- **full** — I read the whole extracted text.
- **excerpt** — I read located portions and rely only on those. Line ranges are given.
- **summary** — I have only a WebFetch model summary; the extracted text was saved but I did
  not read it myself.
- **unavailable** — no retrieval established.

No OCR was available. No paywall was purchased or circumvented. Search-result summaries are
not sources and nothing in `critique.md` rests on one except where explicitly marked.

Line numbers below refer to the extractions saved under this task's prefixes. They will not
match the author's line numbers even for the same URL, because the extractions are separate
retrievals. Retrieval timestamps live in the `.json` metadata files and are not transcribed
here; native collection records them separately.

---

## A. Sources retrieved and read directly

### A1. *Stanford Encyclopedia of Philosophy*, "Coercion"

- URL: https://plato.stanford.edu/entries/coercion/
- Saved: `68958b608d7725bd5085-f09da0aba8a4.txt` / `.original.html` / `.json`
- Metadata inspected (the only `.json` I opened): `TEXT_EXTRACTED`, HTTP 200,
  `text/html`, 183,822 bytes, extraction method "HTML text nodes excluding
  head/script/style", final URL identical to requested URL.
- **Coverage: excerpt.** Read lines 180–300 (title block, opening, start of TOC),
  300–360 (rest of TOC), 430–540 and 600–720 (§§1.1–1.3, including the John Stuart Mill
  section), 1380–1500 (§2.4), 1620–1820 (end of §2.5 and §3.1), 1980–2180 (§3.2),
  2200–2500 (§3.3 and start of §3.4), 3400–3460 (bibliography sample), 4100–4170 and
  4250–4310 (acknowledgments, copyright block, footer).
- **Verifications obtained:**
  - Header, line 199: "First published Fri Feb 10, 2006; substantive revision Mon Jan 23,
    2023."
  - **Authorship and year confirmed**, lines 4141–4146: "Copyright © 2023 by / Scott
    Anderson / <scott.anderson@ubc.ca>". The essay's bibliography entry "Anderson, Scott.
    2023" is therefore correct, and the author's UNVERIFIED flag on this item can be closed.
  - Section titles confirmed from the TOC: "2.2 Threats and Baselines" (line 291),
    "2.3 Moralized vs. non-moralized baselines" (294), "2.4 Coercive Offers?" (297),
    "3.3 Coercion, freedom, and voluntariness" (314).
  - Zimmerman passage, lines 1413–1432, including "the appropriate baseline for evaluating
    the proposal is the state of affairs that the recipient would face in the absence of
    special interference by the proposal maker" (1426–1428). The essay's quotation is
    **verbatim**.
  - Lines 1440–1447: "If the offering party here has created the conditions that make even
    very unattractive offers still the best available, then the coercion, if there is any,
    seems to be vested in the offerer's actions that prevent the recipient from improving
    her situation or finding better offers elsewhere." The essay's quotation of the
    consequent is **verbatim**; the antecedent clause, which the essay omits, is the basis
    of my objection in `critique.md` §8.
  - Lines 1452–1469: Zimmerman grants that a non-causing offeror may still be guilty of
    exploitation, and the entry adds that "sometimes coercion is used to create or maintain
    one's bargaining advantages."
  - §3.3, lines 2323–2342: Olsaretti quoted — "A choice is voluntary if and only if it is not
    made because there is no acceptable alternative to it..." (Olsaretti 2004, 139).
  - §3.3, lines 2347–2380: Pettit-style non-domination, and Garnett's
    "freedom-as-nonsubjection" (Garnett 2018, 554), with the entry's note that "such
    subjection can be found in some cases of offers, where the offeror takes advantage of
    the offeree's lack of an acceptable alternative."
  - §3.2, lines 2162–2171: Galoob and Sheley 2021 on "coercive control" in long-term abusive
    relationships and usurped decisional authority.
  - §1.3, lines 635–713: the entry's own treatment of Mill on coercion and interference.

### A2. *Stanford Encyclopedia of Philosophy*, "Dynamic Choice"

- URL: https://plato.stanford.edu/entries/dynamic-choice/
- Saved: `62757450323609bfdddd-cd002084b336.txt` / `.original.html` / `.json`
- **Coverage: excerpt.** Read lines 190–310 (header, abstract, full TOC, opening of §1),
  640–900 (§1.3 in full, into §1.4), 899–1079 (§1.4, §1.5, §2.1).
- **Verifications obtained:**
  - Header, line 199: "First published Mon Oct 15, 2007; substantive revision Mon May 12,
    2025." The essay's "Andreou 2023" does not match the version now served.
  - TOC, lines 230–274: §1.1 Incommensurable Alternatives; **§1.2 Time-Biased Preferences;
    §1.3 Intransitive Preferences; §1.4 Vague Goals and other Challenging Wholes; §1.5
    Autonomous Benefit Cases**; §§2.1–2.4; §3; §4.
  - **Confirmed error in the essay.** Both the money pump (lines 701–747) and Quinn's
    self-torturer (lines 752–821) are in **§1.3**, not §1.4. §1.4 is about vague goals
    (Tenenbaum and Raffman). The essay cites "Andreou 2023, §1.4" for both.
  - Self-torturer wording confirmed at lines 757–776, including "The device has 1001
    settings", "the increments in current are so small that the self-torturer cannot tell
    the difference between adjacent settings", the \$10,000 per advance, and the
    no-permanent-return condition. The entry attributes the case to "(1993)" and quotes
    Quinn 1993, 199.
  - Money pump attributed to "Donald Davidson, J. McKinsey, and Patrick Suppes (1955)" at
    line 702.
  - §2.4 "Plans and Resoluteness" noted from the TOC as the location of the
    precommitment/resolute-choice material I cite as an antecedent for the essay's
    Commitment Condition. I did **not** read §2.4 itself; my remark about it is a pointer,
    not a report of its content.

### A3. *Stanford Encyclopedia of Philosophy*, "The Ethics of Manipulation"

- URL: https://plato.stanford.edu/entries/ethics-manipulation/
- Saved: `97aee1e89ebead3d4f4b-4d2b0b84395f.txt` / `.original.html` / `.json`
- **Coverage: excerpt.** Read lines 190–310 (header, opening tactic list, framing questions),
  1900–1940 (§3.1 end, §3.2), 2290–2400 (§4.1), 2400–2440 and 2460–2580 (§4.2, start of
  §4.3), 2600–2670 (§4.3 end, start of bibliography), 3400–3460 and 3560–3577 (copyright
  block, footer).
- **Verifications obtained:**
  - Header, line 199: "First published Fri Mar 30, 2018; substantive revision Tue Mar 31,
    2026." Copyright block, lines 3416–3421: "Copyright © 2026 by / Robert Noggle". Author
    correct in the essay; **year is not**.
  - Section titles confirmed: **§2.1 Manipulation as Bypassing or Undermining Reason** and
    **§2.2 Manipulation as Trickery**. The essay's two section numbers are therefore
    **correct**.
  - The Susser et al. phrase, located in §2.1 by the fetch summary and confirmed in wording:
    "in a way they **couldn't** easily become aware of" (Susser et al., 2019: 4). The essay
    prints "could not easily become aware of" inside quotation marks — a silent
    normalisation. The words are Susser et al.'s as quoted by Noggle.
  - **§4.1 "Manipulating Persons versus Manipulating Situations"**, lines 2290–2393. This is
    the finding that contradicts the essay's §3. It contains Riker's "heresthetic",
    characterised as "structuring the world so you can win" (Riker 1986: ix, at lines
    2305–2313); Warwick and Kelman's "environmental" versus "psychic" manipulation and
    Faden, Beauchamp and King's parallel distinction (2318–2323); Barnhill's distinction
    between manipulation that "changes the options available to the person or changes the
    situation she's in, and thereby changes her attitudes" and manipulation that "changes a
    person's attitudes directly without changing the options available to her or the
    surrounding situation" (Barnhill 2014: 53, at lines 2324–2329); and the block quotation
    from Mills 1995: 97 on changing "the external or objective features of B's choice
    situation" (2337–2346).
  - §4.2, lines 2402–2439 and 2484–2534: Baron and Manne on manipulation without conscious
    intent; algorithmic and AI influence without designer intent.
  - §4.3, lines 2560–2569: "some forms of manipulation, like so-called 'negging' and
    gaslighting may work to increase the target's vulnerability to further manipulation."
  - Taken together these establish that the essay's claim — that the reviewed accounts are
    accounts of acts and influences and that manipulation "has not generally been theorised
    as a property of extended sequences" — is not supported by this entry.

### A4. *Stanford Encyclopedia of Philosophy*, "Informed Consent"

- URL: https://plato.stanford.edu/entries/informed-consent/
- Saved: `04ed0fcb8eee755001f3-8a2a8e0851f9.txt` / `.original.html` / `.json`
- **Coverage: excerpt.** Read lines 280–370 (TOC tail and the whole of §1's opening),
  1180–1330 (§4, §4.1, §4.2), 1470–1650 (§5.2 end, **§5.3 in full**, §6, start of §7).
- **Verifications obtained:**
  - Author confirmed as Nir Eyal by the fetch of the same URL; the copyright block itself was
    not in the range I read, so I treat authorship as confirmed by summary and the entry's
    substance as confirmed by my own reading. Current version: "substantive revision Thu Feb
    20, 2025" (from the fetch summary, not from a line I read).
  - §1, lines 363–369: "Informed consent is shorthand for informed, voluntary, and
    decisionally-capacitated consent..." The essay's §1 gloss is accurate to this.
  - **§5.3 "'No choice' situations"**, lines 1477–1550. Cites Wertheimer 1987 p. 13 for the
    "no choice" label, Cohen 1979, Millum and Garnett 2019 on "independent decisionmaking",
    and Feinberg 1986, 233–244. Contains the proposal that "consent is insufficiently
    voluntary only when the patient's options are unfairly curtailed **by the offer itself**"
    (Miller and Wertheimer 2010, 92, 97), at lines 1532–1538. This is the passage I rely on
    in `critique.md` §8 for the charge that §1 of the essay overstates the synchronic
    orthodoxy.
  - §6, lines 1599–1609: advance directives binding one's future self described as
    "perfectly consensual and autonomous"; the right not to become a slave described as
    inalienable.

### A5. *Stanford Encyclopedia of Philosophy*, "Exploitation"

- URL: https://plato.stanford.edu/entries/exploitation/
- Saved: `f1c310a4b5d12fa805a7-c65c901dfcca.txt` / `.original.html` / `.json`
- **This entry is not cited in the essay.** I retrieved it because it is the standing
  reference work for the literature the essay's §3 characterises.
- **Coverage: excerpt.** Read lines 980–1200 (§2 opening, §2.1, §2.1.1, §2.1.2, start of
  §2.1.3), 1430–1630 (§2.2.1.2 basic needs, §2.2.1.3 bargaining solutions), 1640–1860
  (Nash solution critique, §2.2.2, §2.2.2.1 fair market value, start of §2.2.2.2),
  1860–2100 (§2.2.2.2 Roemer, Steiner, Sample, Goodin, Vrousalis, Zwolinski), 2099–2330
  (responses, §2.3, §2.3.1), 2480–2680 (§3 moral weight and force, start of §4).
- Dates from the fetch summary, not from a line I read: first published 20 December 2001;
  substantive revision 3 October 2022.
- **Verifications obtained:**
  - **Non-worseness claim**, lines 2498–2502: "NWC: Interaction between A and B cannot be
    worse than non-interaction **when A has a right not to interact with B at all**, and when
    the interaction is mutually advantageous, consensual, and free from negative
    externalities (Wertheimer 1996, 2011; Zwolinski 2009; Powell and Zwolinski 2012)."
    The essay omits the first condition and credits the claim to Wertheimer alone.
  - Line 2507: "Most exploitation theorists are skeptical that the NWC is correct"
    (Wertheimer 1996; Bailey 2010; Arneson 2013; Barnes 2013; Malmqvist 2016). This tells
    against the essay's description of the NWC as dominating the discussion.
  - **Steiner's historical account**, lines 1976–1996: exploitation occurs when A gains more
    and B less "than they would have were it not for the existence of a prior injustice"
    (Steiner 1984), illustrated by A paying B \$2/hour "only because A (or someone else) has
    previously unjustly deprived B of alternative sources of labor." This is the closest
    structural analogue to the essay's thesis that I located.
  - Lines 2001–2046: Sample 2003 on taking advantage of past injustice; Goodin 1987, 187 on
    vulnerability "regardless of the particular source of their vulnerability"; Vrousalis
    2013, 148–149 and Zwolinski 2012, 171–172 against the necessity of antecedent injustice.
    A live, named debate on precisely the question the essay says the literature does not ask.
  - Lines 1676–1694: the objection that bargaining solutions "take the pre-bargaining status
    quo as given", and that "this contextual insensitivity to the sources of bargaining power
    undermines the sufficiency of bargaining solutions as criteria for fair transaction."
  - Lines 1811–1823: "both the degree and source of these factors influences our willingness
    to say that effects they have on the terms of a transaction are unfair."
  - **Wertheimer's fair market value test**, lines 1759–1768: fair prices are those at which
    "neither party takes special unfair advantage of the other party's decision-making
    capacity or special vulnerabilities in the other party's situation" (Wertheimer 1996,
    232). The basis for my claim that the essay's §5 remedy re-enacts the account its §3
    dismisses.
  - §2.1.1, lines 1036–1079: Zwolinski, McKeowan and Wollner on structural exploitation,
    including systems that "create the conditions that allow A to exploit B."
  - §2.3.1, lines 2292–2310: Vrousalis's domination-based account.
  - Wood 1995 is quoted by this entry at p. 154 and p. 156 (lines 2555–2558, 2618–2624), on
    interference versus redistribution and on "consigning the vulnerable person to an even
    worse fate than being exploited." **Nothing resembling the wording the essay attributes
    to Wood in §3 appears in anything I retrieved.**

### A6. G. A. Cohen, "The Structure of Proletarian Unfreedom"

- *Philosophy & Public Affairs* 12(1) (Winter 1983): 3–33.
- Retrieved from:
  https://www.uvm.edu/~fmagdoff/employment%20Jan.12.11/structure%20of%20proletarian%20unfreedom.pdf
- Saved: `9abebd04804e14208dd0-82ef618d52ff.txt` / `.original.pdf` / `.json`
- The WebFetch summariser could not parse the scanned PDF and said so; the separately saved
  extraction parsed and is what I read. As the author noted, the text layer drops many
  inter-word spaces; I restored spacing when transcribing and altered no wording.
- **Coverage: excerpt.** Read lines 240–295 (end of §V, §VI, the two-temporal-indices
  argument) and 290–420 (§VII and §VIII, the locked-room case through collective unfreedom).
- **Page attribution is determinable from the extraction because the scan preserves the
  journal's running heads**, which appear as standalone lines: "8" at line 242, "9" at line
  285, "Io" (i.e. 10) at line 330, "II" (11) at line 374, "I2" (12) at line 416. Text between
  two heads sits on the page named by the preceding head.
- **Verifications:**
  - Two temporal indices — "fully explicit attributions of freedom and constraint contain two
    temporal indexes" — lines 257–281, i.e. **p. 8**. The essay cites p. 8. **Correct.**
  - Locked room, single heavy key, photoelectric devices installed by a jailer — lines
    305–313, i.e. **p. 9**. The essay's quotation and its ellipses are accurate, and the
    page is **correct**.
  - "It follows that, whatever happens, at least nine people will remain in the room." —
    lines 314–315, still **p. 9**.
  - "even though necessarily at least nine will remain in the room, and in fact all will" —
    lines 351–352, i.e. **p. 10**. The essay cites this as p. 9. **Confirmed error**, as the
    author's own audit reported.
  - "each is free only on condition that the others do not exercise their similarly
    conditional freedom" — lines 401–403, **p. 11**. Cited as p. 11. **Correct.**
  - "Though each is individually free to leave, he suffers with the rest from what I shall
    call collective unfreedom" — lines 408–409, **p. 11**. Cited as p. 11. **Correct.**

### A7. John Stuart Mill, *On Liberty* (1859)

- Edition retrieved: Project Gutenberg EBook #34901.
- URL: https://www.gutenberg.org/files/34901/34901-h/34901-h.htm
- Saved: `0e226c46af44b1006c61-373de7bba35f.txt` / `.original.html` / `.json`
- The WebFetch summariser reported that the content it received ended in Chapter II and
  declined to answer; the separately saved extraction contains the whole book, and Chapter V
  is what I read.
- **Coverage: excerpt.** Read lines 4675–4735 only: the end of the engagements discussion,
  the self-enslavement paragraph, the necessities-of-life clause, the Humboldt passage, and
  the reliance passage that follows it.
- **Verifications:**
  - The essay's block quotation is **verbatim**, lines 4689–4704.
  - The page marker `[Pg 195]` occurs mid-sentence at line 4691 ("consideration for
    his[Pg 195] liberty"), so the quotation spans pp. 194–195. The essay's "pp. 194–95" is
    **correct**.
  - "yet a limit is everywhere set to them by the necessities of life..." — lines 4704–4707,
    before `[Pg 196]` at line 4710, so **p. 195**. Cited as p. 195. **Correct.** Note that
    this clause is joined to the preceding "of far wider application" by a semicolon within
    one sentence, which bears on the essay's "and then immediately retreats".
  - **Finding not in the author's record.** Lines 4728–4733, immediately after the Humboldt
    passage the author set aside: "When a person, either by express promise or by conduct,
    has[Pg 197] encouraged another to rely upon his continuing to act in a certain way—to
    build expectations and calculations, and stake any part of his plan of life upon that
    supposition, a new series of moral obligations arises on his part towards that person,
    which may possibly be overruled, but cannot be ignored." Straddles pp. 196–197. This is
    the passage on which `critique.md` §7 turns.

### A8. Japa Pallikkathayil, "Consent and the Formula of Humanity"

- Retrieved from: https://philosophy.northwestern.edu/community/nustep/07/Consent.pdf
- Saved: `e169e892fe4022b4ebc3-f00b3ed70151.txt` / `.original.pdf` / `.json`
- Again the WebFetch summariser could not parse the PDF; the saved extraction parsed cleanly.
- **Coverage: excerpt.** Read lines 1–100: title, author, abstract, and Section I through the
  Korsgaard block quotation and the start of the four Kantian cases of permissible force.
- **Verifications:**
  - Title and author confirmed on the first page (lines 1–3). **No date, journal or venue
    appears on the first page.** The essay's description of it as a manuscript is honest;
    whether a published version exists I did not establish.
  - Korsgaard's criterion, lines 61–63, as quoted by Pallikkathayil: "you treat someone as a
    mere means whenever you treat him in a way to which he could not possibly consent
    (G 430)." The essay's quotation is **verbatim** and its practice of quoting it *as quoted*
    is correct.
  - Abstract, lines 15–29: the paper argues that the possible-consent interpretation "has
    implausible implications that have thus far gone unnoticed" and "articulates a view that
    is fundamentally misguided." The essay does not note that its source is a refutation of
    the criterion it uses as a foil.

---

## B. Failed retrieval

1. https://philarchive.org/archive/LAINPA — Arto Laitinen, "Normative Powers, Agency, and
   Time." **HTTP 403 Forbidden**, the same result the author reported. No source established.
   My remarks about this chapter in `critique.md` §11 rest solely on the search-result and
   catalogue summaries recorded in §C below, which are **not** a source. The author's top
   priority risk therefore remains formally open, though the summary evidence points to low
   overlap.

No paywall was approached or circumvented, and no access was purchased.

---

## C. Web searches run

Queries, in order. These produced leads and, in two marked cases, the only information I have
about works I could not retrieve. Search summaries are not sources.

1. `Allen Wood "Exploitation" 1995 "background conditions" exploited "acceptable
   alternatives"` — confirmed the article's existence and venue; **did not** surface the
   wording the essay attributes to Wood. Inconclusive, and consistent with the author's own
   conclusion that the quotation is not Wood's.
2. `philosophy consent "who created the alternatives" exploiter creates vulnerability rather
   than finds it exploitation "created the conditions"` — returned the *SEP* "Exploitation"
   entry repeatedly, which prompted retrieval A5.
3. `"sequence" of individually permissible consensual transactions "cumulatively" wrong
   philosophy consent diachronic "bargaining power" endogenous outside option` — returned
   economics work on endogenous outside options and general exploitation-problem material;
   nothing addressing the essay's specific combination.
4. `Olsaretti "Liberty, Desert and the Market" voluntariness acceptable alternatives Mill
   slavery contract degrees gradient Feinberg "Harm to Self" voluntariness variable` — I use
   the Olsaretti formulation only as quoted in A1, not from this search.
5. `Arto Laitinen "Normative Powers, Agency, and Time" abstract` — **the only information I
   have about this chapter.** Reported as published in Carla Bagnoli (ed.), *Time in Action:
   The Temporal Structure of Rational Agency and Practical Thought* (Routledge, 2022), and as
   arguing that agents have powers to bring about normative change directly, against
   challenges from institutionalism, supervenience, and a generalisation of Hurtig's challenge
   about consent. Marked in `critique.md` as summary-derived.
6. `Japa Pallikkathayil "Consent and the Formula of Humanity" published version journal` —
   did not establish a published venue for that title. Surfaced the existence of a *SEP*
   entry "Treating Persons as Means" and a reference to Pallikkathayil 2010.
7. `philosophy ethics "hold-up problem" relation-specific investment lock-in employer moral
   "consent" exploitation normative` — confirmed the hold-up problem as the economics
   antecedent the author concedes in `process.md` §5.2; surfaced no philosophical treatment
   joining it to the justificatory force of consent.

---

## D. Works discussed but not retrieved (unavailable)

Everything I say about the following rests on the *SEP* entries in §A, which I cite as
reporters and never as substitutes. I cannot certify any bibliographic detail for them, and
I did not attempt to.

Wertheimer, *Coercion* (1987) and *Exploitation* (1996); Wood, "Exploitation" (1995);
Steiner (1984); Roemer (1982a,b); Sample (2003); Vrousalis (2013, 2021); Goodin (1987);
Zwolinski (2009, 2012); Powell and Zwolinski (2012); Arneson (2013, 2016); Ferguson (2016a,
2016b, 2020); Quinn (1990/1993); Parfit (1984); Nozick (1969); Zimmerman (1981); Davidson,
McKinsey and Suppes (1955); Feinberg (1986); Olsaretti (2004, 2009); Pettit (1996); Garnett
(2018); Riker (1986); Warwick and Kelman (1973); Faden, Beauchamp and King (1986); Barnhill
(2014); Mills (1995); Baron (2014); Manne (2014); Susser, Roessler and Nissenbaum (2019);
Galoob and Sheley (2021); Millum and Garnett (2019); Miller and Wertheimer (2010);
Tenenbaum and Raffman (2012); Kavka (1983); Schelling (1960); McClennen; Elster; Laitinen
(2022).

---

## E. Summary of what the verification established

**Correct in the manuscript, and independently confirmed:** the Scott Anderson authorship and
2023 date for *Coercion*; both Zimmerman quotations; the *Coercion* section numbers §2.2 and
§2.4; the Mill block quotation and its pagination; the "necessities of life" page; three of
the four Cohen page references (pp. 8, 9, 11, 11); the Cohen quotations themselves; the
Korsgaard-via-Pallikkathayil quotation; the *Ethics of Manipulation* section numbers §2.1 and
§2.2 and Robert Noggle's authorship; Nir Eyal's authorship; the §1 gloss on informed consent.

**Errors independently confirmed:** the Cohen p. 9 / p. 10 slip; "Andreou 2023, §1.4" (wrong
section, twice, and wrong year); "Noggle 2022" (wrong year); "Eyal 2019" (wrong year for the
version served); the altered "could not"/"couldn't" inside quotation marks; the unverifiable
Wood quotation; the incomplete NWC statement and attribution.

**Claims about the literature that verification contradicts:** that manipulation has not been
theorised as situational or sequential; that the exploitation literature treats the victim's
lack of alternatives as something the exploiter merely finds; that the NWC dominates the
exploitation discussion; and, by implication from *Informed Consent* §5.3, that the standard
picture ignores option-poverty.