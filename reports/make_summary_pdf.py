"""Generate the team summary PDF (plain language, for paper writing)."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (CondPageBreak, Image, KeepTogether,
                                ListFlowable, ListItem, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
OUT = ROOT / "reports" / "DT_AI_project_summary.pdf"

NAVY = colors.HexColor("#1f3864")
ACCENT = colors.HexColor("#c00000")
GREY = colors.HexColor("#f2f2f2")
COUR = "Courier"

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=15, textColor=NAVY,
                    spaceBefore=16, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11.5, textColor=NAVY,
                    spaceBefore=11, spaceAfter=5)
BODY = ParagraphStyle("BODY", parent=ss["BodyText"], fontSize=9.7, leading=14.2,
                      alignment=TA_LEFT, spaceAfter=7)
SMALL = ParagraphStyle("SMALL", parent=BODY, fontSize=8.4, leading=11.6,
                       textColor=colors.HexColor("#444444"))
CAP = ParagraphStyle("CAP", parent=SMALL, spaceBefore=3, spaceAfter=12)
TITLE = ParagraphStyle("TITLE", parent=ss["Title"], fontSize=20, textColor=NAVY,
                       spaceAfter=4)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=11, leading=15,
                     textColor=colors.HexColor("#555555"), spaceAfter=16)
KEY = ParagraphStyle("KEY", parent=BODY, fontSize=10, leading=14.5,
                     leftIndent=9, borderPadding=7, backColor=GREY,
                     spaceBefore=6, spaceAfter=10)


def p(t, s=BODY):
    return Paragraph(t, s)


def bullets(items, style=BODY):
    return ListFlowable([ListItem(p(i, style), leftIndent=13) for i in items],
                        bulletType="bullet", start="•", leftIndent=13,
                        bulletFontSize=8, spaceAfter=8)


def table(data, widths, header=True, fs=8.6):
    """Cells must be Paragraphs, otherwise ReportLab will not wrap them and
    long text simply runs off the page."""
    cell = ParagraphStyle("cell", parent=BODY, fontSize=fs, leading=fs + 2.6,
                          spaceAfter=0, textColor=colors.black)
    head = ParagraphStyle("head", parent=cell, textColor=colors.white,
                          fontName="Helvetica-Bold")
    wrapped = []
    for ri, row in enumerate(data):
        out = []
        for c in row:
            if isinstance(c, str):
                txt = c.replace("\n", "<br/>")
                out.append(Paragraph(txt, head if (header and ri == 0) else cell))
            else:
                out.append(c)
        wrapped.append(out)
    t = Table(wrapped, colWidths=widths, hAlign="LEFT")
    st = [("FONTSIZE", (0, 0), (-1, -1), fs),
          ("LEADING", (0, 0), (-1, -1), fs + 3),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
          ("LEFTPADDING", (0, 0), (-1, -1), 5),
          ("RIGHTPADDING", (0, 0), (-1, -1), 5),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), NAVY),
               ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
               ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(st))
    return t


def fig(name, caption, width=16.6):
    """Figure plus its caption, kept on one page."""
    img = Image(str(FIG / name))
    iw, ih = img.imageWidth, img.imageHeight
    w = width * cm
    img.drawWidth, img.drawHeight = w, w * ih / iw
    return [KeepTogether([img, p(caption, CAP)])]


def mono(s):
    return '<font face="%s">%s</font>' % (COUR, s)


def build():
    doc = SimpleDocTemplate(str(OUT), pagesize=A4,
                            leftMargin=2.0 * cm, rightMargin=2.0 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="DT_AI Project Summary",
                            author="Victor Kanu")
    s = []

    # ---------------- cover / summary ----------------
    s.append(p("Detecting High-Demand Work States from Wearable Sensors", TITLE))
    s.append(p("What we did, what we found, and what we can honestly claim<br/>"
               "A plain-language summary for the team, to start writing the paper",
               SUB))
    s.append(p("<b>Prepared by:</b> Victor Kanu &nbsp;&middot;&nbsp; "
               "<b>Date:</b> 19 September 2026 &nbsp;&middot;&nbsp; "
               "<b>Code and data:</b> github.com/xaviwho/DT_AI", SMALL))
    s.append(Spacer(1, 10))
    s.append(p("<b>The one-paragraph version.</b> We set out to build an "
               "&quot;AI digital twin&quot; that predicts human error and "
               "performance under stress. We tested that on real wearable data "
               "from two groups: hospital nurses on shift, and students sitting "
               "exams. <b>We could not predict performance or stress</b> &mdash; "
               "and we show carefully why not. But we <b>can</b> reliably detect "
               "when someone is inside a demanding task episode, ranking task "
               "against rest correctly 93% of the time (AUROC 0.93) on people "
               "the model had never seen. That is a real, useful result, and it "
               "is what the paper should be about.", KEY))

    s.append(p("1. The original idea, and what it became", H1))
    s.append(p("The group's starting proposal was a <i>Neuro-AI digital twin "
               "for predicting human error in disaster and construction "
               "settings</i> &mdash; model a worker's stress and fatigue, then "
               "predict when they will make mistakes.", BODY))
    s.append(p("That idea has two separable parts:", BODY))
    s.append(bullets([
        "<b>Part A &mdash; can we tell what state a person is in?</b> "
        "(calm versus under load) from a wristband.",
        "<b>Part B &mdash; can we predict how well they will perform?</b> "
        "from that state.",
    ]))
    s.append(p("<b>Part A works. Part B does not &mdash; yet.</b> Most of this "
               "document explains how we established that, because the "
               "&quot;how we know&quot; is the part reviewers will judge.", BODY))

    # ---------------- data ----------------
    s.append(p("2. What data we could actually get", H1))
    s.append(p("This was the hardest part and it shaped everything. We verified "
               "every download against the publisher's official checksum, so we "
               "know no file was corrupted.", BODY))
    s.append(table([
        ["Dataset", "What it is", "Did we use it?"],
        ["Exam Stress\n(10 students)",
         "Wristband recordings during 3 real exams each, plus their actual "
         "grades. 30 sessions.",
         "YES — main dataset. The only one with an objective performance "
         "score."],
        ["Nurse Stress\n(15 nurses)",
         "1,252 hours of wristband data across real hospital shifts, with "
         "nurses logging their own stress levels.",
         "YES — second dataset, to check whether findings repeat."],
        ["MMASH\n(22 people)",
         "24-hour heart and sleep data, plus saliva cortisol.",
         "NO — only 2 saliva samples per person (44 in total). Far too "
         "thin to model."],
        ["DriveDB\n(14 drivers)",
         "Driving stress recordings.",
         "NO — the labels marking calm versus stressful driving are "
         "unusable."],
        ["EEGMAT\n(36 people)",
         "Brain (EEG) recordings during mental arithmetic.",
         "NO — only 60-second clips. Too short for our question."],
        ["TILES\n(212 workers)",
         "The ideal dataset: hospital staff, 10 weeks, with job performance "
         "measured twice daily.",
         "NO — needs a signed data agreement. An earlier request from our "
         "side went unanswered, so the team ruled it out."],
    ], [3.0 * cm, 6.3 * cm, 7.3 * cm]))
    s.append(Spacer(1, 4))
    s.append(p("<b>Why this matters for the paper.</b> No freely available "
               "dataset has both (a) continuous wearable data and (b) repeated "
               "objective performance scores. TILES had both. Without it, Part B "
               "of the idea cannot be properly tested &mdash; and that is a "
               "limitation of the available data, not a failure of our method. "
               "This belongs in the Limitations section, stated plainly.", BODY))

    s.append(CondPageBreak(9 * cm))

    # ---------------- approach ----------------
    s.append(p("3. How we did it (the approach)", H1))
    s.append(p("3.1 One pipeline for both datasets", H2))
    s.append(p("Both datasets use the same wristband (Empatica E4), so we wrote "
               "one processing pipeline serving both. From each time window it "
               "computes 19 numbers describing the body's state. Five were "
               "chosen <b>in advance</b> as our headline measures:", BODY))
    s.append(table([
        ["Measure", "In plain terms", "What it indicates"],
        ["HRV (RMSSD)", "How irregular the heartbeat timing is",
         "Higher = more relaxed (‘rest and digest’)"],
        ["Heart rate", "Beats per minute", "Higher = more aroused or more active"],
        ["SCR rate", "Bursts of sweat-gland activity per minute",
         "Higher = more emotional arousal"],
        ["EDA tonic", "Baseline skin moisture level", "Slow-moving arousal level"],
        ["Activity", "How much the wrist is moving", "Physical movement"],
    ], [3.0 * cm, 6.3 * cm, 7.3 * cm]))
    s.append(Spacer(1, 4))
    s.append(p("We deliberately avoided ready-made &quot;black box&quot; "
               "libraries and wrote every formula out, so a reviewer can check "
               "exactly what was computed.", SMALL))

    s.append(p("3.2 Three rules we followed to avoid fooling ourselves", H2))
    s.append(bullets([
        "<b>Test on people the model has never seen.</b> We train on 9 students "
        "and test on the 10th, rotating through all of them "
        "(&quot;leave-one-subject-out&quot;). A lot of published work splits "
        "data by time window instead, which lets the model see the same person "
        "in training and testing &mdash; and inflates the results.",
        "<b>Compare each person to themselves.</b> Some people are simply "
        "stronger students, or have naturally faster hearts. We measure each "
        "session against that person's own average, so the model cannot cheat "
        "by learning <i>who</i> someone is instead of <i>how they are doing</i>.",
        "<b>Choose the measures before looking at the answers.</b> With 30 "
        "sessions and 57 available measures, you can always find something that "
        "looks significant by chance. We fixed our five measures up front.",
    ]))
    s.append(p("We also checked every result two further ways: shuffling the "
               "answers at random 500+ times to see how often chance alone beats "
               "us (a <i>permutation test</i>), and re-running the analysis on "
               "random re-samples of the participants to get an honest error "
               "range (a <i>bootstrap confidence interval</i>).", BODY))

    # ---------------- results ----------------
    s.append(p("4. What we found", H1))
    s.append(p("4.1 Result 1 &mdash; the sensors do detect the exam "
               "(but read the caveat)", H2))
    s.append(p("Comparing each student's exam period against their own pre-exam "
               "period, all five measures changed significantly. This proves the "
               "pipeline works and the sensors are picking up something real.",
               BODY))
    s.append(p("<b>The catch:</b> heart rate went <i>down</i> during the exam, "
               "not up. That looks wrong for &quot;stress&quot; &mdash; until "
               "you notice that movement also dropped sharply. The pre-exam "
               "period included <b>walking to the exam hall</b>. So this "
               "comparison is largely measuring <b>sitting still versus walking "
               "around</b>, not calm versus stressed. We must say this clearly "
               "in the paper; otherwise a reviewer will assume our pipeline is "
               "broken.", BODY))
    s.extend(fig("fig1_manipulation_check.png",
                 "<b>Figure 1.</b> Each grey line is one exam session, moving "
                 "from that student's pre-exam period to their exam period; the "
                 "red line is the average. All five measures shift "
                 "significantly &mdash; but note that heart rate falls and "
                 "movement falls, which is the posture confound described above."))

    s.append(CondPageBreak(9 * cm))
    s.append(p("4.2 An error we caught, and how", H2))
    s.append(p("Our first version compared a 41&ndash;65 minute pre-exam window "
               "against a 90&ndash;180 minute exam window. Because skin-moisture "
               "readings <b>drift slowly upward</b> the longer a sensor is worn, "
               "the longer exam window looked more &quot;aroused&quot; purely "
               "because it was longer.", BODY))
    s.append(p("When we redid it with <b>equal 35-minute windows</b> either side "
               "of the exam start, both sweat-gland effects disappeared, while "
               "the heart and movement effects survived:", BODY))
    s.append(table([
        ["Measure", "Unequal windows", "Equal 35-min windows", "Verdict"],
        ["EDA tonic", "significant (p=.035)", "gone (p=.49)", "ARTEFACT"],
        ["SCR rate", "significant (p=.016)", "gone (p=.41)", "ARTEFACT"],
        ["Heart rate", "very strong", "still very strong", "Real"],
        ["Activity", "significant", "still significant", "Real"],
        ["HRV", "significant", "still significant", "Real"],
    ], [3.4 * cm, 4.2 * cm, 4.4 * cm, 2.6 * cm]))
    s.append(Spacer(1, 4))
    s.append(p("<b>This is a genuine contribution to the paper.</b> Comparing "
               "unequal windows is a common shortcut in wearable research, and "
               "we can show that it manufactures false findings.", BODY))

    s.append(p("4.3 Result 2 &mdash; the main positive finding", H2))
    s.append(p("Using the equal 35-minute windows, we asked the model a simple "
               "question: <i>is this window an exam or a pre-exam period?</i> "
               "Tested only on students it had never seen:", BODY))
    s.append(table([
        ["Measures used", "Accuracy (AUROC)", "Reliable?"],
        ["All five", "0.933  (range 0.885–0.973)",
         "YES — chance is 0.5; p = 0.002"],
        ["Sweat-gland only", "0.398", "No — worse than chance"],
        ["Sweat-gland, movement removed", "0.626",
         "Unclear — range includes chance"],
    ], [5.6 * cm, 5.2 * cm, 5.8 * cm]))
    s.append(Spacer(1, 4))
    s.append(p("AUROC of 0.93 means: pick one exam window and one rest window at "
               "random, and the model ranks them correctly 93% of the time. "
               "<b>That is a strong, deployable-quality result.</b>", BODY))
    s.append(p("<b>But be precise about what it detects.</b> Sweat-gland "
               "measures alone perform at chance, so the signal is coming from "
               "the heart and movement measures. The honest description is: "
               "<i>we can detect a seated, sustained-concentration episode "
               "versus an active pre-task period.</i> We should <b>not</b> call "
               "it &quot;stress detection&quot;. It is still genuinely useful "
               "&mdash; it is how a real monitor would automatically split a "
               "work shift into task episodes.", BODY))
    s.extend(fig("fig4_state_detection.png",
                 "<b>Figure 2.</b> Left: detection accuracy — red (all "
                 "measures) is far above the diagonal chance line, while grey "
                 "(sweat-gland only) sits on it. Middle: which effects survive "
                 "once windows are made equal in length. Right: the "
                 "sweat-gland/performance link, which does survive."))

    s.append(CondPageBreak(9 * cm))
    s.append(p("4.4 Result 3 &mdash; we could not predict performance", H2))
    s.append(p("On the students, we tried to predict who would score above or "
               "below their own average, from their physiology that day. The "
               "model performed <b>worse than simply guessing each student's own "
               "average</b> (negative R-squared; permutation p = 0.31).", BODY))
    s.append(p("One hint did survive: students showing <b>more sweat-gland "
               "arousal</b> during an exam tended to score <b>below their own "
               "average</b> (correlation &minus;0.44, p = .015). The direction "
               "makes biological sense, and it held up under our window "
               "correction. However, once we correct for having tested five "
               "measures, it is no longer statistically significant (p = .074). "
               "<b>It is a promising lead, not a finding.</b>", BODY))

    s.append(p("4.5 Result 4 &mdash; the nurses did not confirm it", H2))
    s.append(p("We ran the identical analysis on the nurses, predicting their "
               "self-reported low versus high stress. Result: AUROC 0.544, which "
               "is essentially chance (p = 0.30). No measure came close.", BODY))
    s.append(p("The sweat-gland lead from the students did <b>not</b> reappear. "
               "There are two possible reasons, and our data cannot tell them "
               "apart:", BODY))
    s.append(bullets([
        "The student lead was a false alarm — consistent with its failing "
        "the correction above.",
        "<b>Or</b> the two studies measure different things: exam <i>grades</i> "
        "are objective, whereas nurse stress is <i>self-reported</i>. It is well "
        "known that how stressed people feel and what their body does often "
        "disagree. Physiology could genuinely track performance without tracking "
        "self-reported feelings.",
    ]))
    s.append(p("Testing that second explanation needs a dataset with both kinds "
               "of outcome &mdash; which is exactly what TILES had, and why "
               "losing it cost us.", BODY))
    s.extend(fig("fig3_nurse_null.png",
                 "<b>Figure 3.</b> Left: how 358 nurse reports reduced to 129 "
                 "usable ones. Middle: the detection curve sits almost on the "
                 "chance diagonal. Right: no measure is significant."))

    s.append(p("4.6 Why the nurse numbers shrank so much", H2))
    s.append(p("Worth explaining in the paper, because it is a useful "
               "data-quality lesson:", BODY))
    s.append(table([
        ["Stage", "Reports left", "Nurses"],
        ["All stress reports submitted", "358", "15"],
        ["Had a stress level filled in (32% were blank)", "245", "15"],
        ["Wristband was actually recording at that time", "163", "12"],
        ["Was a clear low or high rating", "149", "12"],
        ["Nurse reported both low and high at least once", "129", "10"],
    ], [9.0 * cm, 3.6 * cm, 4.0 * cm]))
    s.append(Spacer(1, 4))
    s.append(p("Two details matter. The missing ratings were <b>not random</b> "
               "— one nurse left 65% blank while three left none — so "
               "simply dropping them quietly biases the sample toward a few "
               "nurses. And three nurses had ratings but no overlapping "
               "recording at all, including two of the best-recorded nurses "
               "overall, which means it was a scheduling mismatch rather than "
               "equipment failure.", BODY))

    s.append(CondPageBreak(9 * cm))

    # ---------------- claims ----------------
    s.append(p("5. What we can and cannot claim", H1))
    s.append(p("This is the most important page for writing. Please do not write "
               "beyond what column 2 allows.", BODY))
    def status(text, hexcol):
        return '<font color="%s"><b>%s</b></font>' % (hexcol, text)

    GOOD, WARN, BAD = "#006100", "#9c6500", "#c00000"
    t = table([
        ["Claim", "Status", "Evidence"],
        ["Wearables can detect high-demand task episodes",
         status("SUPPORTED", GOOD), "AUROC 0.93, unseen subjects, p=.002"],
        ["The detector works because of arousal, not posture",
         status("NOT SUPPORTED", BAD),
         "Sweat-gland measures alone at chance (0.40)"],
        ["Sweat-gland arousal relates to lower relative performance",
         status("SUGGESTIVE ONLY", WARN),
         "r=&minus;0.44, p=.015, but p=.074 after correction"],
        ["Physiology predicts performance in new people",
         status("NOT SUPPORTED", BAD),
         "Worse than predicting each person's own average"],
        ["Physiology detects self-reported stress",
         status("NOT SUPPORTED", BAD), "AUROC 0.544 in nurses"],
        ["A working &lsquo;digital twin&rsquo; of a worker",
         status("NOT DEMONSTRATED", BAD),
         "Needs repeated performance data we do not have"],
    ], [6.4 * cm, 3.4 * cm, 6.8 * cm])
    s.append(t)
    s.append(Spacer(1, 6))
    s.append(p("<b>An important framing point.</b> Both our studies were "
               "<b>too small</b> to detect effects of the size we actually "
               "observed. We would have needed a correlation of 0.49 to detect "
               "one reliably; we saw 0.44. So &quot;there is no effect&quot; and "
               "&quot;there is a real moderate effect we were too small to "
               "see&quot; are <b>both still possible</b>. We must not write our "
               "null result as proof of absence.", KEY))

    s.append(p("6. What the paper should be", H1))
    s.append(p("A <b>methods and honest-findings paper</b>, with three "
               "contributions:", BODY))
    s.append(bullets([
        "<b>A positive result:</b> detecting high-demand task episodes from a "
        "wristband, validated on unseen people (AUROC 0.93).",
        "<b>A methodological warning:</b> comparing unequal-length windows "
        "creates false sweat-gland findings, and pre-task baselines that include "
        "walking confound the comparison. We also show that the standard "
        "temperature-based &quot;is the device being worn?&quot; check wrongly "
        "rejected every Midterm 1 session simply because those rooms were colder.",
        "<b>A careful null across two independent datasets</b>, with a power "
        "analysis showing exactly what a future study would need.",
    ]))
    s.append(p("Suggested journals: <b>Sensors</b>, <b>IEEE JBHI</b> (as a short "
               "methods note), or <b>PLOS One</b>. We should drop "
               "<i>npj Digital Medicine</i> (it needed the cortisol work) and "
               "<i>IEEE THMS</i> (it needed the prediction result).", BODY))
    s.append(p("The digital-twin framing stays in the paper as an "
               "<b>architecture and roadmap</b>, with episode detection as its "
               "validated first stage &mdash; not as a working system.", BODY))

    s.append(p("7. The follow-up study that would settle it", H1))
    s.append(p("The good news is that the unanswered question is reachable. To "
               "detect the correlation we observed, we need about 47 sessions "
               "&mdash; we had 30. That is roughly <b>25 students sitting 3 "
               "exams = 75 sessions</b>: a semester-sized study, not a "
               "212-person programme.", BODY))
    s.append(p("Six things the current data taught us to do differently, all "
               "written up in " + mono("docs/STUDY_PROTOCOL.md") + ":", BODY))
    s.append(bullets([
        "Use equal-length windows before and after the task starts.",
        "Press the device's event button at the true start and end — never "
        "trust a timetable. (The public dataset's final exam did not start when "
        "its own documentation said it did.)",
        "Keep participants seated for the whole baseline, so we are not simply "
        "measuring walking.",
        "Decide &quot;was the device worn?&quot; from skin moisture, not "
        "temperature.",
        "Over-recruit: two students' grades barely varied, so they told us "
        "almost nothing.",
        "Register the five measures and the predicted direction in advance.",
    ]))

    s.append(p("8. Suggested next steps", H1))
    s.append(table([
        ["Who", "What"],
        ["Victor", "Methods and Results sections; the figures are done"],
        ["Evans",
         "Discussion: why heart and movement carry the signal while sweat-gland "
         "measures do not, and what that means for stress theory"],
        ["Maame Yaa",
         "Introduction and translation: what episode detection is and is not "
         "useful for in safety-critical work"],
        ["Barry / Calista",
         "Own the follow-up study: find a willing course, IRB application, "
         "devices, recruitment. (The cortisol work is cut — the data has "
         "only 2 samples per person.)"],
        ["Everyone",
         "Read section 5 before writing. Agree whether we publish the detection "
         "result now rather than waiting for the follow-up."],
    ], [3.4 * cm, 13.2 * cm]))
    s.append(Spacer(1, 8))
    s.append(p("<b>The one decision that blocks progress:</b> can we get access "
               "to a course willing to host the follow-up study? That, not "
               "analysis, is the real constraint.", KEY))

    s.append(p("Everything is reproducible", H2))
    s.append(p("All code, data notes and figures live at "
               + mono("github.com/xaviwho/DT_AI") + "<br/><br/>"
               + mono("docs/RESULTS.md")
               + " &mdash; every number in this document, with full statistics"
               "<br/>" + mono("docs/DATASETS.md")
               + " &mdash; where each dataset came from and its problems"
               "<br/>" + mono("docs/STUDY_PROTOCOL.md")
               + " &mdash; the follow-up study design"
               "<br/>" + mono("docs/PROJECT_PLAN.md")
               + " &mdash; revised plan, roles and claim status", SMALL))

    doc.build(s)
    return OUT


if __name__ == "__main__":
    out = build()
    print("wrote", out, "(%.0f KB)" % (out.stat().st_size / 1024))
