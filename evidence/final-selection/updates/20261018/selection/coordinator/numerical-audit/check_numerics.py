#!/usr/bin/env python3
"""Read-only exact arithmetic audit of five frozen manuscripts; no model calls.

Run once in this directory, or rerun with --output-dir NEW_DIRECTORY. Existing
reports are never overwritten. Only the five declared manuscript files are read.
All model probabilities and losses use fractions.Fraction, never binary floats.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
RUN = HERE.parent.parent
INPUTS = {
    "M02": ("F02", "e6badc41a13f407d5ce9660772ff018d0ebbf109f5c8570a0659c612cb217a2d"),
    "M04": ("E039", "37f240addafd761d1d361ce9c0ac1aeb3ba6997eed5b936f9386c11bd09c1a59"),
    "M10": ("E079", "f640e52f1fbccb6a085f1703c912f07b5084336ea5b52de5b15ec49e6e2e775a"),
    "M13": ("F03", "42accea7f8647e8de5dac9d6c55e834e2b62c07d6655730ec6e7948eff9319b5"),
    "M19": ("S02", "0ff5fb0984993915d9fd049be178d5c4bd2c50893353b5e8758996d795fd1056"),
}
LINES: dict[str, list[str]] = {}
MANIFEST: list[dict] = []
CHECKS: list[dict] = []
ENUMERATIONS: dict[str, dict] = {}


def encoded(value: F | int) -> dict:
    value = F(value)
    with localcontext() as ctx:
        ctx.prec = 30
        decimal = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {"fraction": f"{value.numerator}/{value.denominator}",
            "numerator": value.numerator, "denominator": value.denominator,
            "decimal": decimal}


def evidence(mid: str, *numbers: int) -> list[dict]:
    return [{"path": f"blind/{mid}.md", "line": n, "exact_line": LINES[mid][n - 1]}
            for n in numbers]


def result(label: str, actual: F, printed: str, places: int | None = None) -> dict:
    """places means printed rounding; otherwise equality is exact."""
    actual, target = F(actual), F(printed)
    matched = actual == target if places is None else abs(actual - target) <= F(1, 2 * 10**places)
    return {"quantity": label, "computed": encoded(actual), "printed": printed,
            "comparison": "exact" if places is None else f"rounded_to_{places}_decimal_places",
            "rounding_tolerance": None if places is None else encoded(F(1, 2 * 10**places)),
            "matches": matched}


def check(mid: str, suffix: str, title: str, locations: tuple[int, ...],
          premises: tuple[int, ...], computation: str, results: list[dict],
          *, conditional: str | None = None, limits: str | None = None) -> None:
    status = "MISMATCH" if any(not r["matches"] for r in results) else "CONDITIONAL" if conditional else "MATCH"
    CHECKS.append({"id": f"{mid}-{suffix}", "blind_id": mid, "essay_id": INPUTS[mid][0],
                   "title_ru": title, "status": status, "location": evidence(mid, *locations),
                   "explicit_printed_premises": evidence(mid, *premises),
                   "exact_computation": computation, "results": results,
                   "conditional_boundary": conditional, "limits": limits})


def mass(rows: list, predicate=lambda s: True) -> F:
    return sum((w for s, w in rows if predicate(s)), F())


def posterior(rows: list, event, given=lambda s: True) -> F:
    denominator = mass(rows, given)
    if not denominator:
        raise ValueError("Attempted conditioning on zero-probability event")
    return mass(rows, lambda s: event(s) and given(s)) / denominator


def same_fields(state: dict, fields: tuple[str, ...]):
    return lambda other: all(other[k] == state[k] for k in fields)


def predictions(rows: list, fields: tuple[str, ...]) -> list[F]:
    return [posterior(rows, lambda t: t["truth"] == 1, same_fields(s, fields)) for s, _ in rows]


def loss(rows: list, predictions_: list[F], given=lambda s: True) -> F:
    return sum((w * (p - s["truth"])**2 for (s, w), p in zip(rows, predictions_)
                if given(s)), F()) / mass(rows, given)


def keep_enumeration(name: str, rows: list, description: str) -> None:
    if mass(rows) != 1 or any(w <= 0 for _, w in rows):
        raise ValueError("Invalid exact probability enumeration")
    ENUMERATIONS[name] = {"description": description, "total_mass": encoded(mass(rows)),
                          "positive_probability_states": len(rows),
                          "states": [{"state": s, "probability": encoded(w)} for s, w in rows]}


def sensors(full_audit: bool = False, shared_condition: bool = False) -> list:
    rows = []
    for truth, source, a_sound, b_sound, report in product((0, 1), ("A", "B"), (0, 1), (0, 1) if full_audit else (None,), (0, 1)):
        base = F(1, 2) * F(1, 2) * (F(4, 5) if a_sound else F(1, 5))
        if full_audit:
            base *= F(4, 5) if b_sound else F(1, 5)
        if source == "A" or shared_condition:
            reliability = F(1) if a_sound else F(1, 2)
        elif full_audit:
            reliability = F(1) if b_sound else F(1, 2)
        else:
            reliability = F(9, 10)
        weight = base * (reliability if report == truth else 1 - reliability)
        if weight:
            rows.append(({"truth": truth, "source": source, "a_sound": a_sound,
                          "b_sound": b_sound, "report": report}, weight))
    return rows


def audit_f02() -> None:
    m, rows = "M02", sensors()
    keep_enumeration("F02_main", rows, "Only A's condition is disclosed; B reliability is 9/10 conditional on either A condition.")
    blue = lambda s: s["report"] == 1
    check(m, "01", "Исходная надёжность и вероятность после синего сигнала", (40, 47, 57), (35, 37, 43),
          "P(correct|A)=4/5+(1/5)(1/2); Bayes over truth × source × A condition × selected report.",
          [result("A reliability", F(4, 5) + F(1, 5)*F(1, 2), ".9"),
           result("P(blue)", mass(rows, blue), ".5"),
           *[result(f"P(truth=1|source={source},blue)", posterior(rows, lambda s:s["truth"]==1, lambda s:s["source"]==source and blue(s)), ".9") for source in ("A", "B")],
           result("P(truth=1|blue,erased)", posterior(rows, lambda s:s["truth"]==1, blue), ".9")])
    table = []
    for condition in (0, 1):
        given = lambda s: s["a_sound"] == condition and blue(s)
        table.append(result(f"P(source=A|A_sound={condition},blue)", posterior(rows, lambda s:s["source"]=="A", given), ".5"))
        for source in ("A", "B", None):
            g = lambda s: given(s) and (source is None or s["source"]==source)
            target = (".5" if condition == 0 else "1") if source == "A" else ".9" if source == "B" else ".7" if condition == 0 else ".95"
            table.append(result(f"P(truth=1|blue,A_sound={condition},source={source or 'erased'})", posterior(rows, lambda s:s["truth"]==1, g), target))
    check(m, "02", "Все значения таблицы после проверки A", (57, 61, 62, 63), (35, 37, 43, 45),
          "Exact conditional sums of F02_main; erased posterior is equal-weight mean of the two source posteriors.", table)
    before = predictions(rows, ("source", "report"))
    keep = predictions(rows, ("source", "a_sound", "report"))
    erase = predictions(rows, ("a_sound", "report"))
    check(m, "03", "Квадратичные потери 0.09, 0.07 и 0.08", (69, 72, 73, 79, 82), (35, 37, 43, 45, 69),
          "Enumerate sum P(state)*(posterior-truth)^2. Keep=(1/5)((1/4+9/100)/2)+(4/5)((0+9/100)/2)=7/100. Erase=(1/5)(7/10)(3/10)+(4/5)(19/20)(1/20)=2/25.",
          [result("before", loss(rows, before), ".09"), result("Keep, conditional blue", loss(rows, keep, blue), ".07"),
           result("Erase, conditional blue", loss(rows, erase, blue), ".08"), result("Keep, unconditional", loss(rows, keep), ".07"),
           result("Erase, unconditional", loss(rows, erase), ".08")])
    accuracy = lambda ps: sum((w*max(p, 1-p) for (_, w),p in zip(rows, ps)), F())
    check(m, "04", "Вероятность правильной двоичной классификации", (86,), (35, 37, 43, 45, 86),
          "Sum over each posterior information state of max(posterior,1-posterior); ties at 1/2 have accuracy 1/2.",
          [result("Keep classification accuracy", accuracy(keep), ".9"), result("Erase classification accuracy", accuracy(erase), ".9")])
    alt = sensors(shared_condition=True)
    keep_enumeration("F02_shared_condition_alternative", alt, "Printed alternative: both sources perfect if A sound, fair random if A faulty.")
    check(m, "05", "Альтернативная общая неисправность: потери 0.05", (88,), (35, 37, 88),
          "(4/5)*0+(1/5)*(1/4)=1/20; independent enumeration with the printed alternative B condition dependence.",
          [result("Keep alternative loss", loss(alt, predictions(alt, ("source", "a_sound", "report"))), ".05"),
           result("Erase alternative loss", loss(alt, predictions(alt, ("a_sound", "report"))), ".05")],
          limits="This is a separately printed alternative model, not a replacement assumption for the main 0.07/0.08 calculation.")
    variance = sum((w*(q-r)**2 for (_,w),q,r in zip(rows, keep, erase)), F())
    cross = sum((w*(r-q)*(q-s["truth"]) for (s,w),q,r in zip(rows, keep, erase)), F())
    check(m, "06", "Проверка тождества потерь в данном конечном примере", (101, 107, 108, 111), (35, 37, 43, 45, 95),
          "Enumerate E[(q-r)^2] and E[(r-q)(q-X)]; compare the former with loss(Erase)-loss(Keep).",
          [result("variance equals loss difference", variance, str(loss(rows, erase)-loss(rows, keep))), result("cross term", cross, "0")],
          limits="Only substitution in this finite model is tested; this record is not an independent proof of the general theorem.")


def audit_e039() -> None:
    m, rows = "M04", sensors(full_audit=True)
    keep_enumeration("E039_full_audit", rows, "Both independently sound channels are audited; each is sound with probability 4/5.")
    blue = lambda s:s["report"]==1
    check(m, "01", "Исходные вероятности отчёта и уверенность", (15, 17), (13, 15),
          "P(+|H)=4/5+(1/5)(1/2)=9/10; P(+|not H)=(1/5)(1/2)=1/10; equal priors yield posterior 9/10.",
          [result("P(+|H)", posterior(rows, blue, lambda s:s["truth"]==1), ".9"),
           result("P(+|not H)", posterior(rows, blue, lambda s:s["truth"]==0), ".1"),
           *[result(f"P(H|+,source={source})", posterior(rows, lambda s:s["truth"]==1, lambda s:blue(s) and s["source"]==source), ".9") for source in ("A", "B")]])
    results = []
    for source, expected in (("A", ".5"),("B", "1"),(None, ".75")):
        given=lambda s:blue(s) and s["a_sound"]==0 and s["b_sound"]==1 and (source is None or s["source"]==source)
        results.append(result(f"P(H|+,A random,B sound,source={source or 'erased'})", posterior(rows, lambda s:s["truth"]==1, given), expected))
    check(m, "02", "Полный аудит: 0.5, 1 и 0.75", (19, 21), (13, 15, 19),
          "Exact conditional sums for A random/B sound; positive-report source weights remain 1/2 each.", results)
    states = []
    for count, expected in ((2, ".64"),(0, ".04"),(1, ".32")):
        event=lambda s:s["a_sound"]+s["b_sound"]==count
        states.extend([result(f"P({count} sound)", mass(rows,event), expected), result(f"P({count} sound|+)", posterior(rows,event,blue),expected)])
    check(m, "03", "Вероятности состояний двух каналов", (63,), (13, 15),
          "Both sound=(4/5)^2=16/25; both random=(1/5)^2=1/25; exactly one=2*(4/5)*(1/5)=8/25. Enumerate also conditional on positive report.", states)
    before=predictions(rows,("source","report"))
    keep=predictions(rows,("source","a_sound","b_sound","report"))
    erase=predictions(rows,("a_sound","b_sound","report"))
    variance=sum((w*(q-r)**2 for (_,w),q,r in zip(rows,keep,erase)),F())
    check(m, "04", "Квадратичные потери 0.09, 0.05 и 0.07; разность 0.02", (61, 63, 67, 71), (13, 15, 19, 61),
          "Keep=(4/5)*0+(1/5)*(1/4)=1/20. Erase=(16/25)*0+(1/25)*(1/4)+(8/25)*(3/16)=7/100. Exact enumeration separately verifies conditional and unconditional losses and E[(q-r)^2]=1/50.",
          [result("before",loss(rows,before),".09"),result("Keep conditional +",loss(rows,keep,blue),".05"),
           result("Erase conditional +",loss(rows,erase,blue),".07"),result("Keep unconditional",loss(rows,keep),".05"),
           result("Erase unconditional",loss(rows,erase),".07"),result("loss difference",loss(rows,erase)-loss(rows,keep),".02"),
           result("variance identity in this example",variance,".02")],
          limits="This model audits both channels, unlike F02's audit of A alone; its inputs are not interchanged with F02's.")


def audit_e079() -> None:
    m="M10"
    check(m,"01","Проценты из напечатанных чисел участников",(15,),(15,),
          "27/55*100; 7/35*100; 1/13*100. Check percentages at their printed precision, not exact equality of rounded decimals.",
          [result("27/55 percent",F(27,55)*100,"49.1",1),result("7/35 percent",F(7,35)*100,"20"),result("1/13 percent",F(1,13)*100,"7.7",1)],
          limits="Only arithmetic on the printed counts is checked; the external experiment and source transcription are not verified.")
    probabilities={k:F(comb(35,k)*comb(13,8-k),comb(48,8)) for k in range(9)}
    observed=probabilities[7]
    included=[k for k,v in probabilities.items() if v<=observed]
    fisher=sum((probabilities[k] for k in included),F())
    ENUMERATIONS["E079_Fisher_fixed_margins"]={"description":"Tables with fixed row sizes 35/13 and total eight convictions; k convictions in row of 35.",
        "observed_k":7,"two_sided_included_k":included,"total_mass":encoded(sum(probabilities.values(),F())),
        "tables":[{"k":k,"probability":encoded(v),"included":k in included} for k,v in probabilities.items()]}
    check(m,"02","Fisher p = 0.42 при обычном двустороннем подсчёте",(15,),(15,),
          "For [[7,28],[1,12]], P(k)=C(35,k)C(13,8-k)/C(48,8). Sum all tables with probability <= the observed k=7 table.",
          [result("two-sided Fisher p",fisher,".42",2)],
          conditional="The text does not specify a two-sided convention. This calculation uses the probability-ordering definition with fixed margins; it does not reconstruct the source software or verify the experiment.")
    lower,upper=F("-.509"),F(".491")
    width=upper-lower
    prob=lambda discount:max(F(),min(width,upper-discount))/width
    check(m,"03","Равномерная модель: 49.1%, 7.7% и 20%",(23,25,37),(19,23,25,37),
          "Interval width=.491-(-.509)=1; P(X>d)=max(0,min(1,.491-d))/1. Substitutions d=0,.414,.291.",
          [result("width",width,"1"),result("no discount",prob(F()),".491"),result("full discount .414",prob(F(".414")),".077"),
           result("partial discount .291",prob(F(".291")),".200")],
          limits="As explicitly stipulated at line 19, rounded empirical rates become exact hypothetical probabilities; no empirical equality is inferred. Interval endpoints have zero mass.")
    q=F(".123")/F(".414")
    k=1-q
    check(m,"04","Доля q и смесь с результатом 20%",(33,35),(19,23,25,31),
          "q=(.200-.077)/(.491-.077)=.123/.414=41/138; q*.491+(1-q)*.077=1/5.",
          [result("q",q,".2971",4),result("q percentage",q*100,"29.7",1),result("mixture conviction",q*F(".491")+(1-q)*F(".077"),".200")])
    check(m,"05","Интервал изменившегося решения: 12.3%",(54,),(23,25,37,54),
          "P(.291<X<.414)=(.414-.291)/1=.123.",
          [result("interval fraction",(F(".414")-F(".291"))/width,".123"),result("interval percentage",(F(".414")-F(".291"))*100,"12.3")])
    # Affine functions are identical if their exact intercepts and coefficients match.
    a_intercept=q*upper+(1-q)*upper
    a_slope=-(1-q)
    check(m,"06","Тождество расширений при 0 ≤ d ≤ 0.491",(70,72,74),(23,31,35,70),
          "Compare exact affine coefficients: q*.491+(1-q)*(.491-d) has intercept .491 and coefficient -(1-q)=-97/138, identical to .491-k*d. Domain 0<=d<=.491 keeps both thresholds inside the uniform interval.",
          [result("intercept",a_intercept,".491"),result("coefficient of d",a_slope,str(-k)),result("k*.414",k*F(".414"),".291")],
          limits="This verifies the printed stable-parameter extension only; changing the model's parameters is not covered.")
    check(m,"07","Расширение при d = 0.6",(78,),(23,31,35,70,78),
          "d=.6>.491 gives zero convictions among full-discount agents. Model A=q*.491+(1-q)*0=20131/138000. Model B=.491-(3/5)*(97/138)=1593/23000.",
          [result("Model A",q*upper+(1-q)*prob(F(".6")),".1459",4),result("Model B",prob(F(".6")*k),".0693",4)],
          limits="The printed passage labels these as added stable-parameter assumptions, not a validated experimental design.")


def audit_f03() -> None:
    m="M13"
    rows=[]
    for account,process,j,e in product(("F","M"),("R","H"),(0,1),(0,1)):
        pj=F(".8") if process=="R" and account=="F" else F(".2") if process=="R" else F(".5")
        pe=F(".1") if process=="R" else F(".8")
        weight=F(1,4)*(pj if j else 1-pj)*(pe if e else 1-pe)
        rows.append(({"account":account,"process":process,"J":j,"E":e},weight))
    keep_enumeration("F03_account_process_reports",rows,"Equal account priors; equal process priors under either account; J and E independent given both.")
    j=lambda s:s["J"]==1
    e=lambda s:s["E"]==1
    je=lambda s:j(s) and e(s)
    results=[]
    for account,pj,pe in (("F",".65",".45"),("M",".35",".45")):
        given=lambda s:s["account"]==account
        results.extend([result(f"P(J|{account})",posterior(rows,j,given),pj),result(f"P(E|{account})",posterior(rows,e,given),pe)])
    results.append(result("P(F|J)",posterior(rows,lambda s:s["account"]=="F",j),".65"))
    check(m,"01","Исходные вероятности: 0.65, 0.35 и 0.45",(62,),(53,57,58,60),
          "P(J|F)=(.8+.5)/2=.65; P(J|M)=(.2+.5)/2=.35; P(E|each)=(.1+.8)/2=.45. Bayes with equal account priors gives P(F|J)=.65.",results)
    jf=posterior(rows,je,lambda s:s["account"]=="F")
    jm=posterior(rows,je,lambda s:s["account"]=="M")
    check(m,"02","Совместные вероятности 0.24 и 0.21",(66,68),(53,57,58,60),
          "P(J,E|F)=.5*.8*.1+.5*.5*.8=6/25; P(J,E|M)=.5*.2*.1+.5*.5*.8=21/100.",
          [result("P(J,E|F)",jf,".24"),result("P(J,E|M)",jm,".21")])
    check(m,"03","Переход от 0.65 к примерно 0.5333",(70,),(53,57,58,60,66,68),
          "P(F|J,E)=(.5*.24)/(.5*.24+.5*.21)=.24/(.24+.21)=8/15.",
          [result("P(F|J,E)",posterior(rows,lambda s:s["account"]=="F",je),".5333",4)],
          limits="This is conditional on invented likelihoods and conditional independence, explicitly not a psychological or metaphysical probability estimate.")
    check(m,"04","Вероятности E при уже известном J",(72,),(53,57,58,60,62,66,68),
          "P(E|F,J)=.24/.65=24/65; P(E|M,J)=.21/.35=3/5; difference=3/13, so they are unequal.",
          [result("P(E|F,J)",posterior(rows,e,lambda s:s["account"]=="F" and j(s)),str(F(".24")/F(".65"))),
           result("P(E|M,J)",posterior(rows,e,lambda s:s["account"]=="M" and j(s)),str(F(".21")/F(".35")))])


def sequences(p:F) -> list:
    return [({"sequence":list(seq)},p**sum(seq)*(1-p)**(3-sum(seq))) for seq in product((0,1),repeat=3)]


def audit_s02() -> None:
    m="M19"
    low,high=sequences(F(1,4)),sequences(F(3,4))
    keep_enumeration("S02_p_1_4",low,"Eight independent three-panel sequences with approval probability 1/4.")
    keep_enumeration("S02_p_3_4",high,"Eight independent three-panel sequences with approval probability 3/4.")
    any_approval=lambda s:any(s["sequence"])
    last_approval=lambda s:s["sequence"][-1]==1
    rra=lambda s:s["sequence"]==[0,0,1]
    first=lambda s:s["sequence"][0]==1
    pl,ph=mass(low,any_approval),mass(high,any_approval)
    check(m,"01","Первое одобрение в трёх попытках: 37/64",(74,76,78),(69,71,72),
          "Enumerate all 2^3 sequences; any approval=1-(1-p)^3. At p=1/4, 1-(3/4)^3=37/64; fixed-last approval=p=1/4.",
          [result("first approval within cap",pl,"37/64"),result("approximate",pl,".578",3),result("fixed last",mass(low,last_approval),".25")])
    check(m,"02","Одобрение при условии существования назначенного отчёта",(78,),(69,72,78),
          "Under the printed alternative rule 'no report if all reject', report-exists equals any-approval, so P(approval|report exists)=(37/64)/(37/64)=1.",
          [result("conditional approval",posterior(low,any_approval,any_approval),"1")],
          limits="Only the explicitly printed alternative non-reporting rule has this conditional probability.")
    check(m,"03","Неограниченные независимые попытки",(78,),(69,78),
          "For each finite n, P(no approval by n)=(1-p)^n. For constant 0<p<=1, lim_(n->infinity)(1-p)^n=0; hence eventual approval probability is 1.",[],
          conditional="This is a limit under infinitely many independent attempts and constant p>0, not a finite enumeration or an empirical prediction.")
    # In the perfectly correlated alternative there are only 000 and 111 histories.
    correlated=[({"sequence":[0,0,0]},F(3,4)),({"sequence":[1,1,1]},F(1,4))]
    check(m,"04","Напечатанный случай полной корреляции",(80,),(80,),
          "In the perfectly correlated alternative all reports agree. For p=1/4, assign P(000)=3/4, P(111)=1/4; both rules approve exactly on 111.",
          [result("first approval",mass(correlated,any_approval),"1/4"),result("fixed last",mass(correlated,last_approval),"1/4")],
          limits="This is the printed alternative dependence structure, not a change to the independent main model.")
    table=[]
    for label,event,lo,hi,ratio in (("single",first,"1/4","3/4","3"),("approval within three",any_approval,"37/64","63/64","63/37"),("first approval at third",rra,"9/64","3/64","1/3")):
        a,b=mass(low,event),mass(high,event)
        table.extend([result(f"{label}: low",a,lo),result(f"{label}: high",b,hi),result(f"{label}: likelihood ratio",b/a,ratio)])
    check(m,"05","Все три строки отношений правдоподобия",(90,91,92),(69,71,72,86),
          "Single approval: p. Approval within three: 1-(1-p)^3. First approval exactly third: (1-p)^2*p. Divide high-p probability by low-p probability for each specified observation.",table,
          limits="Ratios are likelihood ratios only. The text supplies no prior for these two propensity hypotheses; no posterior is calculated.")
    two_reject=lambda s:s["sequence"][:2]==[0,0]
    ratio=posterior(high,last_approval,two_reject)/posterior(low,last_approval,two_reject)
    check(m,"06","Третье одобрение после двух отказов: множитель 3",(98,),(69,86,96,98),
          "For RRA, both protocols have likelihood (1-p)^2*p. After conditioning on RR, third-approval probability is p; (3/4)/(1/4)=3.",
          [result("RRA low, either protocol",mass(low,rra),"9/64"),result("RRA high, either protocol",mass(high,rra),"3/64"),result("conditional likelihood ratio",ratio,"3")])
    def stopped(seq):
        for bit in seq:
            if bit:
                return 1
        return 0
    agreements=sum(stopped(s["sequence"])==int(any(s["sequence"])) for s,_ in low)
    check(m,"07","Совпадение двоичного итога двух процедур",(128,),(71,72,128),
          "Enumerate every sequence in {0,1}^3. First-approval-with-final-rejection and collect-all/any-approval return the same result on all eight sequences.",
          [result("agreeing sequences",F(agreements),"8")])
    lossresults=[]
    for label,rule,printed in (("any approval",any_approval,"47/128"),("one panel",first,"11/8"),("majority of three",lambda s:sum(s["sequence"])>=2,"55/64")):
        false_reject_good=mass(high,lambda s:not rule(s))
        false_approve_bad=mass(low,rule)
        expected=F(1,2)*10*false_reject_good+F(1,2)*false_approve_bad
        r=result(label,expected,printed)
        r["false_reject_good"]=encoded(false_reject_good)
        r["false_approve_bad"]=encoded(false_approve_bad)
        lossresults.append(r)
    check(m,"08","Потери 47/128, 11/8 и 55/64",(130,),(130,),
          "Each loss=(1/2)*10*P(reject|good)+(1/2)*1*P(approve|bad). Any: (1/2)*10*(1/64)+(1/2)*(37/64)=47/128. One: (1/2)*10*(1/4)+(1/2)*(1/4)=11/8. Majority: (1/2)*10*(5/32)+(1/2)*(5/32)=55/64. Eight sequences enumerated separately at p=3/4 and p=1/4.",lossresults,
          limits="Good/bad priors, conditional independence, approval likelihoods and error costs are extra printed toy-model assumptions. This arithmetic does not assess real assemblies or legitimacy.")


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=HERE,help="New output location; refuses to overwrite reports")
    args=parser.parse_args()
    output=args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=True)
    for name in ("REPORT.json","REPORT_RU.txt"):
        if (output/name).exists():
            parser.error(f"Refusing to overwrite {output/name}; use --output-dir NEW_DIRECTORY")
    for mid,(essay,expected) in INPUTS.items():
        path=RUN/"blind"/f"{mid}.md"
        data=path.read_bytes()
        actual=sha256(data).hexdigest()
        if actual!=expected:
            raise ValueError(f"Frozen input changed: {mid}; expected {expected}; actual {actual}")
        LINES[mid]=data.decode("utf-8").splitlines()
        MANIFEST.append({"blind_id":mid,"essay_id":essay,"path":str(path),"bytes":len(data),"sha256":actual})
    for audit in (audit_f02,audit_e039,audit_e079,audit_f03,audit_s02):
        audit()
    counts={s:sum(c["status"]==s for c in CHECKS) for s in ("MATCH","MISMATCH","CONDITIONAL")}
    report={"schema":"printed-numerical-audit-v1","created_at":datetime.now(timezone.utc).isoformat(),
            "scope":"Mechanical verification of printed numerical premises only; no philosophical review, vote, score, ranking, novelty search or empirical validation.",
            "status":"MISMATCH_FOUND" if counts["MISMATCH"] else "ARITHMETIC_REPRODUCED_WITH_RECORDED_LIMITS",
            "script":{"path":str(Path(__file__).resolve()),"sha256":sha256(Path(__file__).read_bytes()).hexdigest()},
            "inputs":MANIFEST,"counts":counts,"checks":CHECKS,"exact_enumerations":ENUMERATIONS,
            "global_limits":["All calculations are conditional on the printed model premises; matching arithmetic does not make those premises empirically true.",
                             "No manuscripts, frozen files or review results were changed; real evaluator reviews were not read.",
                             "No model, web or archive calls; no ranking, selection recommendation or philosophical verdict.",
                             "Exact rational arithmetic is used throughout. Decimal comparisons distinguish printed rounding from exact equality.",
                             "The general probability identities are checked by substitution in the stated finite examples, not claimed as newly proved general theorems."]}
    text=["Проверка напечатанной арифметики пяти рукописей", "", f"Итог: {counts['MATCH']} MATCH; {counts['CONDITIONAL']} CONDITIONAL; {counts['MISMATCH']} MISMATCH.",
          "Расхождений в проверенных числах не найдено." if not counts["MISMATCH"] else "Найдены расхождения: см. записи MISMATCH.",
          "Это арифметика условных моделей, а не подтверждение их эмпирической истинности.", "",
          "F02 / M02: проверяется только состояние A; потери Keep = 7/100, Erase = 2/25.",
          "E039 / M04: проверяются оба канала; потери Keep = 1/20, Erase = 7/100. Условия моделей не смешивались.",
          "E079 / M10: 27/55, 7/35 и 1/13 дают напечатанные округления 49.1%, 20% и 7.7%. В модели q = 41/138, изменившийся интервал = 123/1000. При d = 0.6 получены 20131/138000 и 1593/23000.",
          "F03 / M13: совместные вероятности 6/25 и 21/100 дают 8/15, то есть примерно 0.5333 после исходных 0.65.",
          "S02 / M19: перебор восьми последовательностей подтверждает 37/64, отношения 63/37 и 1/3, потери 47/128, 11/8 и 55/64.", "",
          "Две явно условные записи:",
          "— Fisher p = 0.4184395997 округляется до 0.42 при двустороннем суммировании таблиц с вероятностью не выше наблюдаемой. Текст не уточняет двустороннюю конвенцию; внешняя статья не проверялась.",
          "— Вероятность 1 при неограниченных попытках является пределом при независимости и постоянном p > 0; это не конечный перебор и не прогноз реальных панелей.", "",
          "Все исходные строки, номера строк, хеши рукописей, точные дроби, формулы и полные конечные переборы: REPORT.json.",
          "Ни оценок, ни сравнения философского качества, ни выбора кандидатов здесь нет.", "", "Проверенные расчёты:"]
    for c in CHECKS:
        lines=", ".join(str(ref["line"]) for ref in c["location"])
        text.append(f"{c['id']} [{c['status']}] {c['title_ru']} — blind/{c['blind_id']}.md, строки {lines}.")
        for r in c["results"]:
            text.append(f"  {r['quantity']}: {r['computed']['fraction']} ≈ {r['computed']['decimal']}; в тексте {r['printed']} ({r['comparison']}).")
        if c["conditional_boundary"]:
            text.append("  Условие: "+c["conditional_boundary"])
    with (output/"REPORT.json").open("x",encoding="utf-8") as file:
        json.dump(report,file,ensure_ascii=False,indent=2)
        file.write("\n")
    with (output/"REPORT_RU.txt").open("x",encoding="utf-8") as file:
        file.write("\n".join(text)+"\n")
    print(json.dumps({"status":report["status"],"counts":counts,"output_dir":str(output)},ensure_ascii=False))
    return 1 if counts["MISMATCH"] else 0


if __name__=="__main__":
    raise SystemExit(main())
