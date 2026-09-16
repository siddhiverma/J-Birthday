from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    KeepTogether, Table, TableStyle, Preformatted, HRFlowable, Flowable,
    NextPageTemplate
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path('output/pdf/sliding_window_dsa_complete_guide.pdf')

NAVY = HexColor('#132238')
BLUE = HexColor('#176B87')
TEAL = HexColor('#18A999')
PALE = HexColor('#EAF6F5')
PALE_BLUE = HexColor('#EDF5FA')
ORANGE = HexColor('#F4A261')
RED = HexColor('#C44536')
INK = HexColor('#243447')
MUTED = HexColor('#607284')
LINE = HexColor('#D8E2E8')
PAPER = HexColor('#FCFDFE')
CODE_BG = HexColor('#F3F6F8')

PAGE_W, PAGE_H = A4


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return
        self.saveState()
        self.setFont('Helvetica', 8)
        self.setFillColor(MUTED)
        self.drawRightString(PAGE_W - 18 * mm, 11 * mm,
                             f'{self._pageNumber} / {page_count}')
        self.restoreState()


class GuideDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        frame = Frame(18 * mm, 17 * mm, PAGE_W - 36 * mm, PAGE_H - 34 * mm,
                      leftPadding=0, rightPadding=0, topPadding=10 * mm,
                      bottomPadding=7 * mm, id='body')
        self.addPageTemplates(PageTemplate(id='main', frames=frame,
                                           onPage=self._header))
        self._section = ''

    def _header(self, canv, doc):
        if doc.page == 1:
            return
        canv.saveState()
        canv.setStrokeColor(LINE)
        canv.setLineWidth(0.5)
        canv.line(18 * mm, PAGE_H - 14 * mm, PAGE_W - 18 * mm,
                  PAGE_H - 14 * mm)
        canv.setFont('Helvetica-Bold', 8)
        canv.setFillColor(NAVY)
        canv.drawString(18 * mm, PAGE_H - 10.5 * mm,
                        'SLIDING WINDOW - THE COMPLETE DSA GUIDE')
        canv.setFont('Helvetica', 8)
        canv.setFillColor(MUTED)
        label = self._section[:55]
        canv.drawRightString(PAGE_W - 18 * mm, PAGE_H - 10.5 * mm, label)
        canv.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style in ('Chapter', 'Section'):
                level = 0 if style == 'Chapter' else 1
                text = flowable.getPlainText()
                key = f'h{level}-{self.seq.nextf("heading")}'
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify('TOCEntry', (level, text, self.page, key))
                if style == 'Chapter':
                    self._section = text


class WindowDiagram(Flowable):
    def __init__(self, values, left, right, caption=None, cell=18 * mm):
        Flowable.__init__(self)
        self.values = values
        self.left = left
        self.right = right
        self.caption = caption
        self.cell = min(cell, 174 * mm / len(values))
        self.width = self.cell * len(values)
        self.height = 24 * mm if caption else 18 * mm

    def draw(self):
        c = self.canv
        y = 7 * mm
        for i, value in enumerate(self.values):
            x = i * self.cell
            active = self.left <= i <= self.right
            c.setFillColor(PALE if active else colors.white)
            c.setStrokeColor(TEAL if active else LINE)
            c.setLineWidth(1.6 if active else 0.8)
            c.roundRect(x, y, self.cell - 1.5, 10 * mm, 2, fill=1, stroke=1)
            c.setFillColor(NAVY if active else MUTED)
            c.setFont('Helvetica-Bold' if active else 'Helvetica', 9)
            c.drawCentredString(x + (self.cell - 1.5) / 2, y + 4 * mm,
                                str(value))
            c.setFont('Helvetica', 6.5)
            c.setFillColor(MUTED)
            c.drawCentredString(x + (self.cell - 1.5) / 2, y - 3 * mm,
                                str(i))
        if self.caption:
            c.setFont('Helvetica-Oblique', 8)
            c.setFillColor(MUTED)
            c.drawString(0, 0, self.caption)


class PointerFlow(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width = 174 * mm
        self.height = 38 * mm

    def draw(self):
        c = self.canv
        boxes = [
            (0, '1  EXPAND', 'Move right; add item'),
            (58 * mm, '2  REPAIR', 'While invalid, move left'),
            (116 * mm, '3  RECORD', 'Update answer / count'),
        ]
        for x, title, note in boxes:
            c.setFillColor(PALE_BLUE)
            c.setStrokeColor(BLUE)
            c.roundRect(x, 10 * mm, 50 * mm, 20 * mm, 4, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont('Helvetica-Bold', 9)
            c.drawCentredString(x + 25 * mm, 22 * mm, title)
            c.setFillColor(MUTED)
            c.setFont('Helvetica', 7.5)
            c.drawCentredString(x + 25 * mm, 15 * mm, note)
        c.setStrokeColor(TEAL)
        c.setFillColor(TEAL)
        for x in (52 * mm, 110 * mm):
            c.line(x, 20 * mm, x + 5 * mm, 20 * mm)
            c.line(x + 5 * mm, 20 * mm, x + 2 * mm, 22 * mm)
            c.line(x + 5 * mm, 20 * mm, x + 2 * mm, 18 * mm)
        c.setFont('Helvetica-Oblique', 8)
        c.setFillColor(MUTED)
        c.drawString(0, 2 * mm, 'The core variable-window control loop')


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitle', fontName='Helvetica-Bold',
                          fontSize=30, leading=34, textColor=colors.white,
                          alignment=TA_LEFT, spaceAfter=6 * mm))
styles.add(ParagraphStyle(name='CoverSub', fontName='Helvetica', fontSize=13,
                          leading=19, textColor=HexColor('#D9EEF3')))
styles.add(ParagraphStyle(name='Chapter', fontName='Helvetica-Bold',
                          fontSize=21, leading=25, textColor=NAVY,
                          spaceBefore=2 * mm, spaceAfter=5 * mm,
                          keepWithNext=True))
styles.add(ParagraphStyle(name='Section', fontName='Helvetica-Bold',
                          fontSize=14, leading=18, textColor=BLUE,
                          spaceBefore=5 * mm, spaceAfter=2.5 * mm,
                          keepWithNext=True))
styles.add(ParagraphStyle(name='Subsection', fontName='Helvetica-Bold',
                          fontSize=11, leading=14, textColor=NAVY,
                          spaceBefore=3.5 * mm, spaceAfter=1.5 * mm,
                          keepWithNext=True))
styles.add(ParagraphStyle(name='BodyX', fontName='Helvetica', fontSize=9.3,
                          leading=14, textColor=INK, spaceAfter=2.6 * mm,
                          allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle(name='Small', fontName='Helvetica', fontSize=8,
                          leading=11, textColor=MUTED))
styles.add(ParagraphStyle(name='Callout', fontName='Helvetica', fontSize=9,
                          leading=13, textColor=INK))
styles.add(ParagraphStyle(name='BulletX', fontName='Helvetica', fontSize=9,
                          leading=13, textColor=INK, leftIndent=5 * mm,
                          firstLineIndent=-3.5 * mm, spaceAfter=1.3 * mm))
styles.add(ParagraphStyle(name='CodeX', fontName='Courier', fontSize=7.15,
                          leading=9.4, textColor=HexColor('#19324A'),
                          leftIndent=4 * mm, rightIndent=4 * mm,
                          borderColor=LINE, borderWidth=0.7,
                          borderPadding=4 * mm, backColor=CODE_BG,
                          spaceBefore=2 * mm, spaceAfter=3.5 * mm))
styles.add(ParagraphStyle(name='Quote', fontName='Helvetica-Oblique',
                          fontSize=11, leading=16, textColor=BLUE,
                          leftIndent=9 * mm, rightIndent=9 * mm,
                          spaceBefore=3 * mm, spaceAfter=4 * mm))

story = []


def P(text, style='BodyX'):
    story.append(Paragraph(text, styles[style]))


def chapter(title, intro=None):
    story.append(PageBreak())
    P(title, 'Chapter')
    story.append(HRFlowable(width='100%', thickness=1.4, color=TEAL,
                            spaceAfter=4 * mm))
    if intro:
        P(intro, 'Quote')


def section(title):
    P(title, 'Section')


def sub(title):
    P(title, 'Subsection')


def bullets(items):
    for x in items:
        P('&bull;&nbsp;&nbsp;' + x, 'BulletX')


def code(text):
    story.append(KeepTogether([Preformatted(text.strip('\n'), styles['CodeX'])]))


def callout(title, text, tone='teal'):
    color = {'teal': TEAL, 'orange': ORANGE, 'red': RED, 'blue': BLUE}[tone]
    bg = {'teal': PALE, 'orange': HexColor('#FFF4E8'),
          'red': HexColor('#FCEDEB'), 'blue': PALE_BLUE}[tone]
    t = Table([[Paragraph(f'<b>{title}</b><br/>{text}', styles['Callout'])]],
              colWidths=[174 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('BOX', (0, 0), (-1, -1), 0.8, color),
        ('LINEBEFORE', (0, 0), (0, -1), 4, color),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.extend([t, Spacer(1, 3 * mm)])


def table(headers, rows, widths=None, font=7.8):
    data = [[Paragraph(f'<b>{escape(str(x))}</b>', styles['Small']) for x in headers]]
    for row in rows:
        data.append([Paragraph(escape(str(x)), ParagraphStyle(
            'cell', parent=styles['Small'], fontSize=font, leading=font + 3,
            textColor=INK)) for x in row])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.45, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, PAPER]),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.extend([t, Spacer(1, 3 * mm)])


# Cover
cover = Table([[
    Paragraph('SLIDING<br/>WINDOW', styles['CoverTitle']),
    Paragraph('<b>DSA PATTERN</b><br/><br/>From first principles to advanced '
              'counting, monotonic structures, proofs, and interview mastery',
              styles['CoverSub'])
]], colWidths=[78 * mm, 86 * mm], rowHeights=[90 * mm])
cover.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), NAVY),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 10 * mm),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8 * mm),
    ('LINEAFTER', (0, 0), (0, 0), 2, TEAL),
]))
story.extend([Spacer(1, 37 * mm), cover, Spacer(1, 10 * mm)])
P('A one-stop C++ reference and learning path', 'Chapter')
P('Concepts  |  Recognition  |  Templates  |  Dry runs  |  Correctness  |  '
  'Pitfalls  |  30 practice problems', 'Quote')
story.append(Spacer(1, 18 * mm))
callout('How to use this guide',
        'Read Chapters 1-5 in order if you are new. Then learn the specialized '
        'data structures in Chapters 6-8. Use the template catalog and decision '
        'tree while solving. Finish with the graded practice set and solutions.')

# Front matter / TOC
chapter('Contents and learning roadmap')
callout('Three-stage roadmap',
        '<b>Basic:</b> fixed windows and incremental state. '
        '<b>Intermediate:</b> variable windows, frequency maps, counting. '
        '<b>Advanced:</b> deques, ordered structures, transformations, proofs, '
        'and knowing when the pattern is invalid.', 'blue')
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle(name='TOC0', fontName='Helvetica-Bold', fontSize=10,
                   leading=16, textColor=NAVY, leftIndent=0,
                   firstLineIndent=0, spaceBefore=2),
    ParagraphStyle(name='TOC1', fontName='Helvetica', fontSize=8.5,
                   leading=12, textColor=MUTED, leftIndent=8 * mm,
                   firstLineIndent=0),
]
story.append(toc)
story.append(Spacer(1, 5 * mm))

# Chapter 1
chapter('1. The core idea',
        'A sliding window reuses the work done for one contiguous range when '
        'moving to a nearby range.')
section('1.1 From brute force to reuse')
P('Many array and string problems ask about a <b>contiguous</b> subarray or '
  'substring. A brute-force solution chooses every left endpoint, every right '
  'endpoint, and often scans the range again. That can cost O(n^3), or O(n^2) '
  'if each range statistic is maintained incrementally.')
P('A sliding window stores exactly the information needed about one active '
  'range <b>[left, right]</b>. When <i>right</i> advances, one element enters. '
  'When <i>left</i> advances, one element leaves. If each update is cheap, all '
  'useful ranges can often be processed in O(n).')
story.append(WindowDiagram([2, 1, 5, 1, 3, 2], 1, 3,
             'Active window [1, 3] contains {1, 5, 1}; indices appear below.'))
sub('Vocabulary')
table(['Term', 'Meaning'], [
    ('Window', 'The current contiguous range [left, right].'),
    ('Expand', 'Move right forward and add a new element to the state.'),
    ('Shrink', 'Remove a[left], then move left forward.'),
    ('State', 'Sum, counts, distinct count, deque, multiset, or other summary.'),
    ('Invariant', 'A condition guaranteed at a specific point in the loop.'),
    ('Valid window', 'A range satisfying the problem constraint.'),
], [35 * mm, 139 * mm])

section('1.2 What makes sliding possible?')
bullets([
    '<b>Contiguity:</b> the object is a subarray or substring, not an arbitrary subsequence.',
    '<b>Local update:</b> adding or removing one boundary item updates the state cheaply.',
    '<b>Useful movement rule:</b> we know when and why to move left or right.',
    '<b>Monotonic feasibility for variable windows:</b> after a violation, removing '
    'items from the left moves toward validity and discarded starts never need to return.',
])
callout('Important distinction',
        'Sliding window is a specialized form of the two-pointer technique. All '
        'sliding windows use boundaries, but not every two-pointer algorithm '
        'maintains a contiguous interval. Pair-sum on a sorted array is two '
        'pointers, not usually called sliding window.', 'orange')

section('1.3 Complexity intuition: why nested loops can still be O(n)')
P('Variable-window code often contains a <code>for</code> loop and an inner '
  '<code>while</code>. It is not automatically O(n^2). The right pointer moves '
  'forward at most n times. The left pointer also moves forward at most n times. '
  'No pointer moves backward, so there are at most 2n boundary movements. This '
  'is aggregate or amortized analysis: O(n) movements total.')
P('The total complexity is O(n * U), where U is the cost of one state update. '
  'An array counter or hash map is expected O(1); a balanced tree or multiset '
  'makes the same traversal O(n log n).')

# Chapter 2
chapter('2. Recognition and classification',
        'Before writing code, identify the window type, validity rule, state, '
        'and answer event.')
section('2.1 Recognition signals')
bullets([
    'The statement says subarray, substring, contiguous segment, consecutive, '
    'or every block of size k.',
    'It asks for a longest, shortest, maximum, minimum, number of ranges, or '
    'whether any range satisfies a condition.',
    'Neighboring candidate ranges overlap heavily.',
    'The constraint can be repaired by moving the left boundary forward.',
])
P('These are clues, not proof. Always test whether discarding a left endpoint is '
  'safe. Negative values, exact-equality constraints, or non-monotone properties '
  'can invalidate the ordinary variable-window method.')

section('2.2 The main families')
table(['Family', 'Window size', 'Typical question', 'Core state'], [
    ('Fixed', 'Exactly k', 'Best/each block of length k', 'Sum or frequency'),
    ('Variable: longest', 'Changes', 'Longest range satisfying at most...', 'Validity state'),
    ('Variable: shortest', 'Changes', 'Shortest range reaching at least...', 'Validity state'),
    ('Counting', 'Changes', 'How many ranges satisfy...', 'At-most invariant'),
    ('Frequency matching', 'Fixed or variable', 'Permutation/anagram/cover', 'Counts + mismatch'),
    ('Order statistic', 'Usually fixed', 'Maximum, minimum, median', 'Deque/tree/heaps'),
], [31 * mm, 25 * mm, 62 * mm, 56 * mm], font=7.3)

section('2.3 The four design questions')
P('<b>1. What does [left, right] mean?</b> State whether the interval is inclusive. '
  'Then length is <code>right - left + 1</code>.')
P('<b>2. What state summarizes it?</b> Examples: sum, number of zeros, character '
  'frequencies, distinct values, maximum-minimum, matched requirements.')
P('<b>3. What is invalid?</b> Write a Boolean predicate such as '
  '<code>sum &gt; limit</code>, <code>distinct &gt; k</code>, or '
  '<code>max - min &gt; limit</code>.')
P('<b>4. When is the answer recorded?</b> After reaching size k? After restoring '
  'validity? During shrinking? The location of this line is algorithmically important.')
story.append(PointerFlow())

section('2.4 A decision checklist')
table(['Question', 'If yes', 'If no'], [
    ('Must the range length equal k?', 'Use fixed window.', 'Consider variable window.'),
    ('Can invalidity be repaired by removing left items?', 'Use expand/repair.', 'Seek prefix sums, DP, binary search, etc.'),
    ('Are all valid suffixes ending at right countable?', 'Add window length.', 'Use another counting transform.'),
    ('Need max/min under deletions?', 'Monotonic deque.', 'Simple scalar state may work.'),
    ('Negative values affect a sum constraint?', 'Be suspicious.', 'Classic sum window may be valid.'),
], [66 * mm, 52 * mm, 56 * mm], font=7.4)

# Chapter 3
chapter('3. Fixed-size windows - the foundation',
        'Fixed windows have one deterministic movement: add the new item and '
        'remove the item that is now too old.')
section('3.1 Maximum sum of any length-k subarray')
P('Example: <code>[2, 1, 5, 1, 3, 2]</code>, k = 3. The length-3 sums are '
  '8, 7, 9, and 6. Instead of recomputing each sum, subtract the outgoing '
  'element and add the incoming element.')
code(r'''
long long maxSumK(const vector<int>& a, int k) {
    int n = (int)a.size();
    if (k <= 0 || k > n) throw invalid_argument("invalid k");

    long long sum = 0;
    for (int i = 0; i < k; ++i) sum += a[i];
    long long answer = sum;

    for (int right = k; right < n; ++right) {
        sum += a[right];       // incoming
        sum -= a[right - k];   // outgoing
        answer = max(answer, sum);
    }
    return answer;
}''')
P('<b>Invariant:</b> immediately before updating the answer, <code>sum</code> '
  'equals the sum of exactly the k elements ending at <code>right</code>. '
  'Time O(n), extra space O(1). Use <code>long long</code> when sums may overflow int.')

section('3.2 A universal fixed-window template')
code(r'''
State state;
int left = 0;
for (int right = 0; right < n; ++right) {
    add(state, a[right]);

    if (right - left + 1 > k) {
        remove(state, a[left]);
        ++left;
    }

    if (right - left + 1 == k) {
        consume(state);  // answer for this exact window
    }
}''')
P('This formulation is safer than manually computing outgoing indices and '
  'generalizes immediately from sums to maps, mismatch counters, and deques.')

section('3.3 First negative number in every window')
P('Maintain a deque of <b>indices</b> of negative values. Indices reveal whether '
  'an item has expired; storing only values cannot distinguish duplicates or age.')
code(r'''
vector<int> firstNegative(const vector<int>& a, int k) {
    deque<int> q;
    vector<int> ans;
    for (int right = 0; right < (int)a.size(); ++right) {
        if (a[right] < 0) q.push_back(right);
        int left = right - k + 1;
        while (!q.empty() && q.front() < left) q.pop_front();
        if (left >= 0) ans.push_back(q.empty() ? 0 : a[q.front()]);
    }
    return ans;
}''')

section('3.4 Count distinct values in each window')
code(r'''
vector<int> distinctPerWindow(const vector<int>& a, int k) {
    unordered_map<int, int> freq;
    vector<int> ans;
    for (int right = 0; right < (int)a.size(); ++right) {
        ++freq[a[right]];
        if (right >= k) {
            int out = a[right - k];
            if (--freq[out] == 0) freq.erase(out);
        }
        if (right >= k - 1) ans.push_back((int)freq.size());
    }
    return ans;
}''')
callout('Map hygiene',
        'Erase zero-frequency keys when map size represents the distinct count. '
        'A key with value zero still contributes to unordered_map::size().', 'orange')

section('3.5 Rolling product, average, and other aggregates')
P('Sums, counts, and XOR are easy to add and remove. Products require care: '
  'division fails with zeros, overflow is common, and modular division may not '
  'exist. An average is simply <code>sum / k</code>; keep the sum in an exact '
  'integer type and convert when producing the result. Some statistics, such as '
  'a maximum, cannot be maintained with one scalar because the outgoing maximum '
  'may expose an unknown second-best value. That motivates deques and trees.')

# Chapter 4
chapter('4. Variable windows - longest and shortest',
        'The right edge explores. The left edge repairs or optimizes.')
section('4.1 Longest subarray with sum at most S (non-negative values)')
P('With non-negative elements, expanding can only increase the sum and shrinking '
  'can only decrease it. This monotonic behavior makes discarded starts safe.')
code(r'''
int longestSumAtMost(const vector<int>& a, long long S) {
    int left = 0, answer = 0;
    long long sum = 0;
    for (int right = 0; right < (int)a.size(); ++right) {
        sum += a[right];
        while (left <= right && sum > S) {
            sum -= a[left++];
        }
        answer = max(answer, right - left + 1);
    }
    return answer;
}''')
P('<b>Loop invariant after the while loop:</b> [left, right] is valid, and every '
  'earlier left endpoint has been ruled out for this and all future right '
  'endpoints under the non-negative assumption. Therefore the current valid '
  'window is the longest valid one ending at right.')

section('4.2 Why <code>while</code>, not <code>if</code>?')
P('One incoming element may require removing several old elements. An '
  '<code>if</code> removes at most one, potentially leaving the window invalid. '
  'Use <code>while (invalid)</code> whenever validity is not restored by exactly '
  'one guaranteed removal.')

section('4.3 Minimum length with sum at least S (positive values)')
P('For a shortest-window problem, record an answer <b>while the window is valid</b> '
  'and keep shrinking to find a smaller valid range ending at the same right.')
code(r'''
int minLengthAtLeast(const vector<int>& a, long long S) {
    int left = 0, answer = INT_MAX;
    long long sum = 0;
    for (int right = 0; right < (int)a.size(); ++right) {
        sum += a[right];
        while (sum >= S) {
            answer = min(answer, right - left + 1);
            sum -= a[left++];
        }
    }
    return answer == INT_MAX ? 0 : answer;
}''')
callout('Answer placement',
        'Longest under an upper bound: repair invalidity, then record. Shortest '
        'reaching a lower bound: record while valid, then shrink. Memorizing the '
        'code is less reliable than understanding this event.', 'blue')

section('4.4 Max consecutive ones after flipping at most k zeros')
code(r'''
int longestOnes(vector<int>& a, int k) {
    int left = 0, zeros = 0, answer = 0;
    for (int right = 0; right < (int)a.size(); ++right) {
        zeros += (a[right] == 0);
        while (zeros > k) {
            zeros -= (a[left] == 0);
            ++left;
        }
        answer = max(answer, right - left + 1);
    }
    return answer;
}''')
P('The abstract pattern is not about zeros. It is: maintain a budget of at most '
  'k violations. The same idea solves longest substring after at most k '
  'replacements, at most k odd numbers, and at most k distinct categories.')

section('4.5 A subtle lazy-shrink variant')
P('Some longest-window solutions replace <code>while</code> with <code>if</code> '
  'and allow the maintained interval to remain notionally invalid, preserving '
  'only its maximum length. This can be correct for specific problems such as '
  'character replacement, but it changes the invariant and is easy to misuse. '
  'Prefer the fully valid template until you can prove the lazy version.')

# Chapter 5
chapter('5. Strings and frequency-state windows',
        'Most string windows are boundary movement plus a carefully designed '
        'frequency invariant.')
section('5.1 Longest substring without repeating characters')
sub('Frequency-count solution')
code(r'''
int lengthOfLongestSubstring(const string& s) {
    array<int, 256> freq{};
    int left = 0, answer = 0;
    for (int right = 0; right < (int)s.size(); ++right) {
        unsigned char in = s[right];
        ++freq[in];
        while (freq[in] > 1) {
            --freq[(unsigned char)s[left++]];
        }
        answer = max(answer, right - left + 1);
    }
    return answer;
}''')
P('Use <code>unsigned char</code> when indexing a 256-entry array because plain '
  '<code>char</code> may be signed. For lowercase English letters, 26 entries '
  'are sufficient. For Unicode text, bytes are not characters; decode code '
  'points and use a map.')

sub('Last-seen jump optimization')
code(r'''
int lengthNoRepeat(const string& s) {
    array<int, 256> last;
    last.fill(-1);
    int left = 0, answer = 0;
    for (int right = 0; right < (int)s.size(); ++right) {
        unsigned char c = s[right];
        left = max(left, last[c] + 1); // never move left backward
        last[c] = right;
        answer = max(answer, right - left + 1);
    }
    return answer;
}''')
P('The <code>max</code> is essential. A character last seen before the current '
  'window must not pull left backward.')

section('5.2 Find all anagrams of a pattern')
P('Every answer has fixed length |p|. Maintain a difference count. The '
  '<code>missing</code> value counts how many required character instances remain, '
  'not merely how many character types remain.')
code(r'''
vector<int> findAnagrams(const string& s, const string& p) {
    array<int, 256> need{};
    for (unsigned char c : p) ++need[c];
    int missing = (int)p.size();
    vector<int> ans;

    for (int right = 0, left = 0; right < (int)s.size(); ++right) {
        unsigned char in = s[right];
        if (need[in] > 0) --missing;
        --need[in];

        if (right - left + 1 > (int)p.size()) {
            unsigned char out = s[left++];
            ++need[out];
            if (need[out] > 0) ++missing;
        }
        if (missing == 0) ans.push_back(left);
    }
    return ans;
}''')
P('Here negative <code>need[c]</code> means the window contains extra copies. '
  'When an outgoing character makes <code>need[out]</code> positive, a required '
  'instance has become missing again.')

section('5.3 Minimum window substring')
P('This is a variable window with multiplicities. Expand until all required '
  'instances are covered. Then shrink while coverage remains complete, recording '
  'each improved minimum.')
code(r'''
string minWindow(const string& s, const string& t) {
    if (t.empty()) return "";
    array<int, 256> need{};
    for (unsigned char c : t) ++need[c];
    int missing = (int)t.size();
    int left = 0, bestL = 0, bestLen = INT_MAX;

    for (int right = 0; right < (int)s.size(); ++right) {
        unsigned char in = s[right];
        if (need[in] > 0) --missing;
        --need[in];

        while (missing == 0) {
            if (right - left + 1 < bestLen) {
                bestLen = right - left + 1;
                bestL = left;
            }
            unsigned char out = s[left++];
            ++need[out];
            if (need[out] > 0) ++missing;
        }
    }
    return bestLen == INT_MAX ? "" : s.substr(bestL, bestLen);
}''')

section('5.4 Replacement windows: longest repeating character')
P('Let <code>maxFreq</code> be the largest frequency of any character in the '
  'window. The number of replacements needed is '
  '<code>windowLength - maxFreq</code>. If this exceeds k, shrink.')
code(r'''
int characterReplacement(const string& s, int k) {
    array<int, 26> freq{};
    int left = 0, maxFreq = 0, answer = 0;
    for (int right = 0; right < (int)s.size(); ++right) {
        maxFreq = max(maxFreq, ++freq[s[right] - 'A']);
        while (right - left + 1 - maxFreq > k) {
            --freq[s[left++] - 'A'];
        }
        answer = max(answer, right - left + 1);
    }
    return answer;
}''')
P('<code>maxFreq</code> is intentionally not decreased during shrinking. It may '
  'be stale, but it is an upper bound representing a frequency achieved by some '
  'window of this size. This suffices for the maximum-length result. If you need '
  'the exact validity of the current window or its boundaries, recompute/maintain '
  'the true maximum instead.')

# Chapter 6
chapter('6. Counting subarrays correctly',
        'Counting windows is where a one-line combinatorial observation often '
        'replaces an extra loop.')
section('6.1 Count ranges with an at-most constraint')
P('After repairing the window, suppose [left, right] is valid and the property is '
  'hereditary under removing items from the left. Then every suffix ending at '
  'right is also valid: [left, right], [left+1, right], ..., [right, right]. '
  'There are exactly <code>right - left + 1</code> of them.')
code(r'''
long long countAtMostKDistinct(const vector<int>& a, int k) {
    if (k < 0) return 0;
    unordered_map<int, int> freq;
    int left = 0, distinct = 0;
    long long answer = 0;

    for (int right = 0; right < (int)a.size(); ++right) {
        if (freq[a[right]]++ == 0) ++distinct;
        while (distinct > k) {
            if (--freq[a[left]] == 0) {
                freq.erase(a[left]);
                --distinct;
            }
            ++left;
        }
        answer += right - left + 1;
    }
    return answer;
}''')
P('Counts of subarrays can reach n(n+1)/2, so use <code>long long</code>.')

section('6.2 Exactly k = atMost(k) - atMost(k - 1)')
P('The sets of ranges with at most k distinct values and at most k-1 distinct '
  'values differ by exactly the ranges with k distinct values.')
code(r'''
long long exactlyKDistinct(const vector<int>& a, int k) {
    return countAtMostKDistinct(a, k)
         - countAtMostKDistinct(a, k - 1);
}''')
P('This transformation also works for exactly k odd values, exactly k zeros, '
  'exactly k violations, and other integer-valued metrics whose at-most counts '
  'are easy to compute.')

section('6.3 Binary arrays with sum exactly goal')
P('For non-negative/binary arrays, use '
  '<code>count(sum == goal) = atMost(goal) - atMost(goal - 1)</code>.')
code(r'''
long long atMostSum(const vector<int>& a, int goal) {
    if (goal < 0) return 0;
    int left = 0, sum = 0;
    long long answer = 0;
    for (int right = 0; right < (int)a.size(); ++right) {
        sum += a[right];
        while (sum > goal) sum -= a[left++];
        answer += right - left + 1;
    }
    return answer;
}''')

section('6.4 Product less than k (positive values)')
code(r'''
long long numSubarrayProductLessThanK(const vector<int>& a, long long k) {
    if (k <= 1) return 0;
    long long product = 1, answer = 0;
    int left = 0;
    for (int right = 0; right < (int)a.size(); ++right) {
        product *= a[right];
        while (product >= k) product /= a[left++];
        answer += right - left + 1;
    }
    return answer;
}''')
P('This assumes positive values. Zeros, negatives, and overflow change the '
  'reasoning. Even with positive integers, ensure multiplication fits the chosen '
  'type or use a problem-specific overflow guard.')

section('6.5 A general counting theorem')
callout('Suffix-count theorem',
        'If, after repair, left is the smallest start such that [left, right] is '
        'valid, and validity is preserved when removing elements from the left, '
        'then exactly right-left+1 valid subarrays end at right. Summing this over '
        'all right endpoints counts each valid subarray once.', 'teal')

# Chapter 7
chapter('7. Monotonic deques for window extrema',
        'A deque compresses all candidates that might become the maximum or '
        'minimum of a future window.')
section('7.1 Sliding window maximum')
P('Maintain indices in decreasing order of their values. Before inserting a new '
  'value, remove smaller or equal values from the back: the newcomer is at least '
  'as good and expires later. Remove expired indices from the front. The front '
  'is always the maximum.')
code(r'''
vector<int> maxSlidingWindow(const vector<int>& a, int k) {
    deque<int> dq;
    vector<int> ans;
    for (int right = 0; right < (int)a.size(); ++right) {
        while (!dq.empty() && a[dq.back()] <= a[right]) dq.pop_back();
        dq.push_back(right);

        int left = right - k + 1;
        while (!dq.empty() && dq.front() < left) dq.pop_front();
        if (left >= 0) ans.push_back(a[dq.front()]);
    }
    return ans;
}''')

section('7.2 The two deque invariants')
bullets([
    '<b>Index order:</b> indices increase from front to back. Therefore expiration '
    'happens only at the front.',
    '<b>Value order:</b> values decrease from front to back. Therefore the front '
    'is the maximum.',
    '<b>Dominance:</b> an older value no larger than a new value can never win in '
    'a future window, so it is permanently removed.',
])
P('Each index is inserted once and removed at most once, giving O(n) time and '
  'O(k) space. For a minimum, reverse the comparison. Whether to remove equal '
  'values is a tie-policy choice; removing equals keeps the newer index, which '
  'usually expires later and is convenient.')

section('7.3 Longest subarray with max - min <= limit')
P('Use one decreasing deque for the maximum and one increasing deque for the '
  'minimum. Repair while their front values differ by more than the limit.')
code(r'''
int longestSubarray(vector<int>& a, int limit) {
    deque<int> mx, mn;
    int left = 0, answer = 0;
    for (int right = 0; right < (int)a.size(); ++right) {
        while (!mx.empty() && a[mx.back()] <= a[right]) mx.pop_back();
        while (!mn.empty() && a[mn.back()] >= a[right]) mn.pop_back();
        mx.push_back(right);
        mn.push_back(right);

        while ((long long)a[mx.front()] - a[mn.front()] > limit) {
            if (mx.front() == left) mx.pop_front();
            if (mn.front() == left) mn.pop_front();
            ++left;
        }
        answer = max(answer, right - left + 1);
    }
    return answer;
}''')

section('7.4 Deque versus heap versus multiset')
table(['Structure', 'Update/query', 'Strength', 'Limitation'], [
    ('Monotonic deque', 'Amortized O(1)', 'Fast max/min for FIFO windows', 'Only extrema; careful invariant'),
    ('Multiset', 'O(log k)', 'Simple exact min/max and duplicates', 'Slower, erase one occurrence'),
    ('Heap + lazy deletion', 'O(log k)', 'Useful for extrema/median components', 'Stale entries and bookkeeping'),
    ('Two multisets/heaps', 'O(log k)', 'Median and quantiles', 'Balancing is more complex'),
], [33 * mm, 30 * mm, 57 * mm, 54 * mm], font=7.2)

# Chapter 8
chapter('8. Ordered windows, medians, and richer state',
        'When add/remove is easy but the statistic is not a simple aggregate, '
        'choose a data structure that supports both boundaries.')
section('8.1 Fixed-window median with two multisets')
P('Maintain a lower half <code>lo</code> and upper half <code>hi</code>. Every '
  'value in lo is no greater than every value in hi. Keep '
  '<code>lo.size() == hi.size()</code> or exactly one larger. The median is the '
  'largest value in lo, or the average of both boundary values.')
code(r'''
class MedianWindow {
    multiset<long long> lo, hi;
    void rebalance() {
        while (lo.size() > hi.size() + 1) {
            hi.insert(*prev(lo.end())); lo.erase(prev(lo.end()));
        }
        while (lo.size() < hi.size()) {
            lo.insert(*hi.begin()); hi.erase(hi.begin());
        }
    }
public:
    void add(long long x) {
        if (lo.empty() || x <= *prev(lo.end())) lo.insert(x);
        else hi.insert(x);
        rebalance();
    }
    void remove(long long x) {
        auto it = lo.find(x);
        if (it != lo.end()) lo.erase(it);
        else hi.erase(hi.find(x));
        rebalance();
    }
    double median() const {
        if (lo.size() > hi.size()) return (double)*prev(lo.end());
        return ((double)*prev(lo.end()) + (double)*hi.begin()) / 2.0;
    }
};''')
P('Each insertion and deletion costs O(log k), so all medians cost O(n log k). '
  'With a multiset, <code>erase(value)</code> removes every equal occurrence; use '
  '<code>find</code> and erase the iterator to remove exactly one.')

section('8.2 Choosing the state representation')
table(['Need', 'Best first choice', 'Notes'], [
    ('Small known alphabet', 'array<int, 26/128/256>', 'Fast, deterministic, cache friendly'),
    ('Arbitrary sparse keys', 'unordered_map', 'Expected O(1); erase zeros when needed'),
    ('Ordered keys / min and max', 'map or multiset', 'O(log k), exact order'),
    ('One extreme', 'monotonic deque', 'O(n) total for FIFO movement'),
    ('Median', 'two multisets/heaps', 'Maintain balance and ordering invariants'),
    ('Bit presence for tiny universe', 'bitmask', 'Very compact; multiplicity still needs counts'),
], [55 * mm, 50 * mm, 69 * mm], font=7.3)

section('8.3 Coordinate compression')
P('If values are arbitrary but known in advance, sort unique values and map each '
  'to [0, m). Then a vector can replace a hash map. This improves predictability '
  'and can be useful when many window updates are performed. Compression preserves '
  'equality and order, not original distances unless handled separately.')

# Chapter 9
chapter('9. When ordinary sliding window fails',
        'The most advanced skill is recognizing when the left pointer cannot make '
        'an irreversible safe decision.')
section('9.1 Negative numbers break sum monotonicity')
P('Consider longest subarray with sum at most S. With non-negative values, if '
  'the sum is too large, future expansion cannot fix it, so shrinking is safe. '
  'With negative values, a future negative number could restore validity while '
  'preserving the old left endpoint. Shrinking now may discard the optimal answer.')
callout('Counterexample',
        'For a = [5, -10, 5] and S = 0, shrinking immediately after seeing 5 '
        'discards index 0. But the full length-3 subarray has sum 0 and is valid. '
        'The classic variable sum window is therefore incorrect.', 'red')

section('9.2 Exact sum with arbitrary integers: prefix frequencies')
P('Let prefix[j] be the sum of the first j elements. The sum of [i, j-1] is '
  '<code>prefix[j] - prefix[i]</code>. It equals target when an earlier prefix is '
  '<code>prefix[j] - target</code>. Count earlier prefix values in a hash map.')
code(r'''
long long subarraySumEqualsK(const vector<int>& a, long long k) {
    unordered_map<long long, long long> seen;
    seen[0] = 1;
    long long prefix = 0, answer = 0;
    for (int x : a) {
        prefix += x;
        if (auto it = seen.find(prefix - k); it != seen.end())
            answer += it->second;
        ++seen[prefix];
    }
    return answer;
}''')

section('9.3 Shortest sum at least K with arbitrary integers')
P('Use prefix sums plus a monotonic deque of candidate prefix indices. For '
  'current prefix i, if <code>prefix[i] - prefix[dq.front()] >= K</code>, update '
  'the answer and pop front because that start cannot produce a shorter future '
  'answer than the current one. Remove from the back while its prefix sum is no '
  'smaller than the current prefix: the newer, smaller prefix dominates it.')
code(r'''
int shortestSubarray(const vector<int>& a, long long K) {
    int n = (int)a.size(), answer = n + 1;
    vector<long long> pref(n + 1);
    for (int i = 0; i < n; ++i) pref[i + 1] = pref[i] + a[i];
    deque<int> dq;
    for (int i = 0; i <= n; ++i) {
        while (!dq.empty() && pref[i] - pref[dq.front()] >= K) {
            answer = min(answer, i - dq.front());
            dq.pop_front();
        }
        while (!dq.empty() && pref[dq.back()] >= pref[i]) dq.pop_back();
        dq.push_back(i);
    }
    return answer <= n ? answer : -1;
}''')

section('9.4 Other warning signs')
bullets([
    '<b>Subsequence rather than substring:</b> contiguity is absent; consider DP, greedy, or indexed positions.',
    '<b>Range must satisfy a non-hereditary property:</b> removing from the left '
    'may unpredictably destroy and restore validity.',
    '<b>Need arbitrary range queries:</b> prefix sums, sparse tables, Fenwick or segment trees may fit better.',
    '<b>Offline reordering is allowed:</b> Mo\'s algorithm moves both boundaries '
    'and answers queries, but it is not the classic one-pass sliding window.',
    '<b>Multiple independent intervals:</b> interval DP or sweep-line methods may be required.',
])

section('9.5 Sliding window versus related techniques')
table(['Technique', 'Use when', 'Key difference'], [
    ('Prefix sum', 'Associative range aggregate or exact sums', 'No validity repair; subtract prefixes'),
    ('Binary search + window', 'Feasibility is monotone in length/value', 'Window checks a guessed answer'),
    ('Two pointers on sorted data', 'Pairs/triples by value order', 'Pointers do not summarize a contiguous original range'),
    ('Monotonic stack', 'Next greater/smaller, spans', 'One directional dominance, not a moving interval'),
    ('Mo\'s algorithm', 'Many offline range queries', 'Boundary movement is reordered, about O((n+q)sqrt n)'),
    ('DP', 'Overlapping states without safe boundary discard', 'Stores more histories instead of one interval'),
], [38 * mm, 68 * mm, 68 * mm], font=7.1)

# Chapter 10
chapter('10. Proofs, invariants, and derivation',
        'A template becomes reliable when you can state why every pointer movement '
        'is safe.')
section('10.1 A proof recipe for variable windows')
P('<b>Step 1 - Define the state.</b> Prove add/remove operations make it exactly '
  'describe [left, right].')
P('<b>Step 2 - State the invariant.</b> Example: after the repair loop, the window '
  'contains at most k distinct values.')
P('<b>Step 3 - Prove safe shrinking.</b> Show that every removed start cannot lead '
  'to a better candidate for the current or any relevant future right endpoint.')
P('<b>Step 4 - Prove answer coverage.</b> Associate every optimal or counted range '
  'with the moment its right endpoint is processed.')
P('<b>Step 5 - Prove complexity.</b> Each boundary moves forward at most n times; '
  'multiply by the data-structure update cost.')

section('10.2 Proof sketch: longest at most k distinct')
bullets([
    'The frequency map and distinct counter exactly describe the active interval.',
    'The repair loop stops only when distinct <= k.',
    'When left advances because distinct > k, the discarded window is invalid. '
    'Any extension before enough categories disappear remains invalid.',
    'After repair, [left, right] is the longest valid suffix ending at right, so '
    'updating the global maximum examines an optimal endpoint-specific candidate.',
    'Both pointers only advance, and each hash update is expected O(1), so total '
    'expected time is O(n).',
])

section('10.3 Proof sketch: monotonic maximum deque')
P('When index i is removed from the back because a[j] >= a[i] and j > i, index '
  'i is dominated: in every future window containing i, j is also present until '
  'i expires, and j is at least as large. Thus i can never again be the maximum. '
  'Expired indices are removed from the front. What remains is ordered by value, '
  'so the front is the correct maximum.')

section('10.4 Derive rather than memorize')
table(['Question to ask', 'Example answer'], [
    ('What enters?', 'a[right] increments sum/frequency/deque.'),
    ('What leaves?', 'a[left] decrements state before left advances.'),
    ('What is invalid?', 'distinct > k, zeros > k, max-min > limit.'),
    ('Do I repair to valid or shrink while valid?', 'Depends on longest vs shortest objective.'),
    ('What candidates become known now?', 'Best ending at right, or all valid suffixes ending at right.'),
    ('What assumption makes discard safe?', 'Non-negativity, hereditary validity, or dominance.'),
], [70 * mm, 104 * mm], font=7.5)

# Chapter 11
chapter('11. Debugging and common mistakes',
        'Most bugs come from a broken invariant, an off-by-one boundary, or an '
        'unstated assumption.')
section('11.1 Off-by-one rules')
bullets([
    'Inclusive [left, right] length is <code>right - left + 1</code>.',
    'A fixed window becomes available when <code>right >= k - 1</code>.',
    'For a new fixed window ending at right, the expired index is '
    '<code>right - k</code> after adding, or anything smaller than '
    '<code>right - k + 1</code> for a deque.',
    'Decide whether comparisons are strict: sum < K versus sum <= K, product < K '
    'versus <= K, and max-min <= limit.',
])

section('11.2 Frequent implementation failures')
table(['Bug', 'Symptom', 'Fix'], [
    ('Use if instead of while', 'Window remains invalid', 'Shrink until invariant holds'),
    ('Update answer too early', 'Invalid ranges included', 'Record only at the proven event'),
    ('Forget outgoing update', 'State drifts from window', 'Remove before incrementing left'),
    ('Leave zero map entries', 'Wrong distinct count', 'Erase when frequency reaches zero'),
    ('Store deque values only', 'Cannot expire duplicates', 'Store indices'),
    ('Move left backward', 'Duplicate-window bug', 'Use max(left, last+1)'),
    ('Use int for totals', 'Overflow', 'Use long long for sums/counts/products'),
    ('Assume sum monotonic with negatives', 'Missed optimum', 'Use prefix-based method'),
    ('multiset.erase(value)', 'All duplicates erased', 'Erase one iterator'),
    ('k=0 / k>n unhandled', 'Undefined semantics', 'Validate constraints explicitly'),
], [47 * mm, 61 * mm, 66 * mm], font=7.1)

section('11.3 Trace table method')
P('For each right endpoint, write: incoming item, state after add, removals, final '
  'left, validity, and answer change. This exposes almost every pointer bug.')
table(['right', 'in', 'state after add', 'left removals', 'final [l,r]', 'answer'], [
    ('0', '2', 'sum=2', '-', '[0,0]', '1'),
    ('1', '1', 'sum=3', '-', '[0,1]', '2'),
    ('2', '5', 'sum=8', 'remove 2,1', '[2,2]', '2'),
    ('3', '1', 'sum=6', '-', '[2,3]', '2'),
    ('4', '1', 'sum=7', '-', '[2,4]', '3'),
], [17 * mm, 14 * mm, 34 * mm, 39 * mm, 34 * mm, 25 * mm], font=7.4)
P('Example assumes longest sum <= 7 with non-negative numbers.')

section('11.4 Edge-case test suite')
bullets([
    'Empty input; one element; all equal; all distinct; all zeros.',
    'k = 0, 1, n, n+1; target negative/zero; no valid window; whole array valid.',
    'Duplicate values at both boundaries; optimum at beginning or end.',
    'Large values causing overflow; characters outside expected alphabet.',
    'For monotonic deque: strictly increasing, strictly decreasing, and all equal.',
])

# Chapter 12
chapter('12. C++ template catalog',
        'Use these as skeletons. Replace State, validity, and answer logic only '
        'after writing the invariant.')
section('12.1 Fixed-size template')
code(r'''
int left = 0;
State state;
for (int right = 0; right < n; ++right) {
    add(state, a[right]);
    if (right - left + 1 > k) remove(state, a[left++]);
    if (right - left + 1 == k) record(state, left, right);
}''')

section('12.2 Longest valid template')
code(r'''
int left = 0, answer = 0;
State state;
for (int right = 0; right < n; ++right) {
    add(state, a[right]);
    while (invalid(state)) remove(state, a[left++]);
    answer = max(answer, right - left + 1);
}''')

section('12.3 Shortest valid template')
code(r'''
int left = 0, answer = INF;
State state;
for (int right = 0; right < n; ++right) {
    add(state, a[right]);
    while (valid(state)) {
        answer = min(answer, right - left + 1);
        remove(state, a[left++]);
    }
}''')

section('12.4 Count all hereditary-valid windows')
code(r'''
int left = 0;
long long answer = 0;
State state;
for (int right = 0; right < n; ++right) {
    add(state, a[right]);
    while (invalid(state)) remove(state, a[left++]);
    answer += right - left + 1;
}''')

section('12.5 Exactly-k transform')
code(r'''
long long exactlyK(const Input& x, int k) {
    return atMost(x, k) - atMost(x, k - 1);
}''')

section('12.6 Monotonic deque template')
code(r'''
deque<int> dq;
for (int right = 0; right < n; ++right) {
    while (!dq.empty() && dominated(dq.back(), right)) dq.pop_back();
    dq.push_back(right);
    int left = right - k + 1;
    while (!dq.empty() && dq.front() < left) dq.pop_front();
    if (left >= 0) record(a[dq.front()]);
}''')

section('12.7 Binary search on answer plus fixed window')
P('Sometimes the question asks for the maximum feasible length and feasibility '
  'is monotone by length. Binary-search the length, and test each length with a '
  'fixed window. This often costs O(n log n). Before using it, check whether a '
  'direct variable window can already solve the problem in O(n).')

# Chapter 13
chapter('13. Advanced patterns and extensions',
        'Sliding window is a framework: boundary movement can be combined with '
        'transformations, deques, hashing, and binary search.')
section('13.1 Complement window: take from both ends')
P('If you must take exactly k items from the two ends of an array, choosing those '
  'items is equivalent to leaving one contiguous middle window of length n-k. '
  'Maximize taken sum by minimizing the sum of that fixed middle window. This '
  'complement transformation turns an awkward two-ended choice into a window.')

section('13.2 Circular arrays')
P('A circular window of length at most n can be processed over indices '
  '<code>0..2n-1</code> using <code>a[i % n]</code>, while preventing length from '
  'exceeding n. For fixed k <= n, scan only enough doubled positions to enumerate '
  'n starting points. Avoid physically duplicating a large array unless clarity '
  'matters more than memory.')

section('13.3 Multiple constraints')
P('Combine state components: sum plus distinct count, max/min deques plus a budget, '
  'or several character requirements. The invalid predicate becomes an OR of '
  'violations. Ordinary variable windows remain valid only if shrinking moves '
  'every violated constraint monotonically toward validity.')

section('13.4 Two windows in one pass for exactly-k counting')
P('Instead of calling atMost twice, maintain two left boundaries: one for at most '
  'k and one for at most k-1. At each right, the number of exactly-k ranges '
  'ending there is <code>leftKMinus1 - leftK</code>. This can reduce constant '
  'factors but is harder to reason about; the two-pass identity is usually cleaner.')

section('13.5 Frequency of the maximum element')
P('Problems may ask for subarrays where the global maximum appears at least k '
  'times. Once the active window contains k copies, every extension of its left '
  'boundary in the opposite direction may be counted. Carefully identify whether '
  'you are counting valid prefixes or valid suffixes; not every counting problem '
  'uses <code>right-left+1</code>. Derive the combinatorics from the endpoint fixed '
  'by the loop.')

section('13.6 Windows over streams')
P('A fixed window naturally supports streaming: keep only the last k items or the '
  'state needed to expire them. Time-based windows require timestamps and expire '
  'all events older than the cutoff. Out-of-order events need watermark/buffering '
  'semantics and go beyond the simple array model.')

section('13.7 2D sliding windows')
P('For matrix rectangle sums, a 2D prefix sum usually gives O(1) per rectangle. '
  'For row-wise/column-wise extrema, apply monotonic deques in two passes. A k by '
  'k maximum filter can compute row maxima of width k, then column maxima of '
  'height k, in O(rows * cols).')

section('13.8 Smallest range covering k sorted lists')
P('Merge all values with their list ID, sort them, then find the smallest window '
  'containing every list ID. This is minimum-window substring generalized from '
  'characters to categories. A heap-based k-way merge is another approach.')

section('13.9 Offline queries and Mo\'s algorithm')
P('Mo\'s algorithm orders arbitrary range queries so consecutive queries require '
  'few add/remove operations. Unlike the classic pattern, both boundaries may '
  'move in both directions, and correctness does not rely on monotone validity. '
  'It is useful when updates are cheap but no fast per-query data structure exists.')

# Chapter 14
chapter('14. Worked pattern map',
        'Different stories often reduce to the same invariant.')
table(['Problem phrase', 'Invariant / transformation', 'Answer event'], [
    ('Maximum average length k', 'Fixed size; rolling sum', 'When size == k'),
    ('Longest no repeats', 'Every frequency <= 1', 'After repair'),
    ('Longest at most k distinct', 'distinct <= k', 'After repair'),
    ('Shortest covering pattern', 'missing == 0', 'While valid'),
    ('Permutation in string', 'Fixed size + matching frequencies', 'When size == |p|'),
    ('Count exactly k odds', 'atMost(k) - atMost(k-1)', 'Add valid suffix count'),
    ('Max of every length k', 'Decreasing index deque', 'When size == k'),
    ('Longest max-min <= L', 'Two monotonic deques', 'After repair'),
    ('Exact sum, arbitrary ints', 'Prefix frequency map', 'At each prefix'),
    ('Shortest sum >= K, arbitrary ints', 'Prefix + monotonic deque', 'Pop valid fronts'),
    ('Take k cards from ends', 'Minimize complement window n-k', 'When size == n-k'),
    ('Cover k sorted lists', 'Window over merged (value, list)', 'While all lists present'),
], [52 * mm, 72 * mm, 50 * mm], font=7.2)

section('14.1 Interview communication script')
bullets([
    'State the brute force and its complexity.',
    'Point out the overlap between neighboring contiguous ranges.',
    'Define [left, right], the maintained state, and the validity predicate.',
    'Explain exactly when right expands and when left shrinks.',
    'State the invariant before coding.',
    'After coding, justify correctness, O(n) amortized movement, update cost, and space.',
    'Name assumptions explicitly: non-negative values, alphabet, k bounds, overflow type.',
])

# Chapter 15
chapter('15. Graded practice set',
        'Solve in order. For each problem, first write the family, state, invalid '
        'predicate, answer event, and complexity without code.')
section('15.1 Basic')
table(['#', 'Problem', 'Main lesson'], [
    ('1', 'Maximum sum subarray of size k', 'Rolling fixed state'),
    ('2', 'Average of every subarray of size k', 'Same state, different output'),
    ('3', 'First negative in every window', 'Queue indices and expiration'),
    ('4', 'Count distinct in each window', 'Frequency map lifecycle'),
    ('5', 'Maximum number of vowels in length k substring', 'Fixed violation counter'),
    ('6', 'Find all anagrams', 'Fixed frequency matching'),
], [10 * mm, 91 * mm, 73 * mm], font=7.5)

section('15.2 Intermediate')
table(['#', 'Problem', 'Main lesson'], [
    ('7', 'Longest substring without repeats', 'Repair duplicates'),
    ('8', 'Longest subarray with at most k zeros', 'Budget invariant'),
    ('9', 'Fruit into baskets / at most two types', 'At most k distinct'),
    ('10', 'Minimum size sum >= S, positive array', 'Shrink while valid'),
    ('11', 'Minimum window substring', 'Multiplicity and matched count'),
    ('12', 'Count product < k, positive array', 'Count valid suffixes'),
    ('13', 'Count exactly k distinct', 'Difference of at-most counts'),
    ('14', 'Binary subarrays with sum goal', 'Exactly via at-most transform'),
    ('15', 'Longest repeating character replacement', 'Dominant frequency'),
], [10 * mm, 91 * mm, 73 * mm], font=7.4)

section('15.3 Advanced')
table(['#', 'Problem', 'Main lesson'], [
    ('16', 'Sliding window maximum', 'Monotonic deque'),
    ('17', 'Longest range with max-min <= limit', 'Two deques'),
    ('18', 'Sliding window median', 'Balanced ordered halves'),
    ('19', 'Shortest subarray sum >= K with negatives', 'Prefix monotonic deque'),
    ('20', 'Smallest range covering k lists', 'Merged categorical window'),
    ('21', 'Subarrays with exactly k odd numbers', 'Exactly transform'),
    ('22', 'Maximum points from taking k ends', 'Complement window'),
    ('23', 'Substring concatenation of all words', 'Multiple offset windows'),
    ('24', 'Minimum operations to reduce x to zero', 'Longest complement sum'),
    ('25', 'Count complete subarrays', 'At-most or ending-point count'),
], [10 * mm, 91 * mm, 73 * mm], font=7.3)

section('15.4 Expert extensions')
table(['#', 'Problem', 'Direction'], [
    ('26', '2D k x k maximum filter', 'Two-pass monotonic deques'),
    ('27', 'Time-based event-rate window', 'Timestamp deque and expiry'),
    ('28', 'Median absolute deviation in fixed windows', 'Ordered partitions + sums'),
    ('29', 'Many offline distinct-range queries', 'Mo\'s algorithm'),
    ('30', 'Design a generic reusable window aggregator', 'Interfaces, invariants, tests'),
], [10 * mm, 91 * mm, 73 * mm], font=7.3)

# Chapter 16
chapter('16. Hints and compact solutions',
        'Use these only after attempting the classification and invariant yourself.')
section('16.1 Problems 1-6')
P('<b>1-2.</b> Initialize the first k sum or use the universal fixed template. '
  'For averages, divide only when emitting. <b>3.</b> Store negative indices; '
  'expire indices smaller than left. <b>4.</b> Increment incoming, decrement '
  'outgoing, erase zero. <b>5.</b> Track a vowel count. <b>6.</b> Maintain a '
  'difference array or missing-instance counter over exact-size windows.')
section('16.2 Problems 7-15')
P('<b>7.</b> Frequency repair or last-seen jump. <b>8.</b> Invalid when zeros > k. '
  '<b>9.</b> Invalid when map size > 2. <b>10.</b> Record while sum >= S, then '
  'shrink; positivity is required. <b>11.</b> Count missing required instances. '
  '<b>12.</b> Repair product >= k and add window length. <b>13.</b> atMost(k) - '
  'atMost(k-1). <b>14.</b> Same transform because binary values are non-negative. '
  '<b>15.</b> replacements = length - largest frequency.')
section('16.3 Problems 16-25')
P('<b>16.</b> Decreasing deque of indices. <b>17.</b> Decreasing max deque plus '
  'increasing min deque. <b>18.</b> Two balanced multisets or heaps with lazy '
  'deletion. <b>19.</b> Prefix sums in an increasing deque. <b>20.</b> Sort merged '
  '(value,listID) pairs, then cover all IDs. <b>21.</b> Treat odd as 1, even as '
  '0; use at-most difference. <b>22.</b> total minus minimum length n-k middle sum. '
  '<b>23.</b> Run one word-aligned window per offset modulo word length. '
  '<b>24.</b> Find longest subarray with sum total-x; positivity enables a normal '
  'window. <b>25.</b> Count windows containing all globally distinct values by '
  'shrinking while complete and counting possible starts.')
section('16.4 Problems 26-30')
P('<b>26.</b> Compute width-k row maxima, then height-k column maxima. '
  '<b>27.</b> Expire timestamps earlier than now-duration. Define inclusive cutoff '
  'precisely. <b>28.</b> Median minimizes absolute deviation; maintain two ordered '
  'halves plus sums of each half. <b>29.</b> Sort queries by blocks and update '
  'frequency state as boundaries move. <b>30.</b> Expose add/remove/query, document '
  'valid movement directions, and property-test against brute force.')

section('16.5 A reusable brute-force oracle')
P('For small random arrays, compare your optimized result with an obviously '
  'correct O(n^2) implementation. This is one of the fastest ways to validate '
  'window invariants and boundary conditions.')
code(r'''
// Example oracle: longest subarray with sum <= S.
int brute(const vector<int>& a, long long S) {
    int ans = 0;
    for (int l = 0; l < (int)a.size(); ++l) {
        long long sum = 0;
        for (int r = l; r < (int)a.size(); ++r) {
            sum += a[r];
            if (sum <= S) ans = max(ans, r - l + 1);
        }
    }
    return ans;
}''')

# Chapter 17
chapter('17. Final cheat sheet',
        'The whole pattern, compressed into one reference page.')
section('Recognition')
P('Contiguous range + overlapping candidates + cheap add/remove + safe monotone '
  'boundary movement. If any part is missing, reconsider the technique.')
section('Core formulas')
table(['Idea', 'Formula / rule'], [
    ('Inclusive length', 'right - left + 1'),
    ('Valid suffixes ending at right', 'right - left + 1'),
    ('Exactly k', 'atMost(k) - atMost(k - 1)'),
    ('Fixed outgoing index after adding right', 'right - k'),
    ('Replacement cost', 'window length - maximum frequency'),
    ('Subarray sum by prefixes', 'prefix[r + 1] - prefix[l]'),
    ('All subarrays count', 'n(n + 1) / 2'),
], [75 * mm, 99 * mm], font=7.8)
section('Answer-event map')
table(['Goal', 'When to update'], [
    ('Best exact length k', 'After the active size becomes k'),
    ('Longest under an upper bound', 'After repairing invalidity'),
    ('Shortest reaching a lower bound', 'Inside the while-valid shrink loop'),
    ('Count hereditary-valid ranges', 'After repair: add current window length'),
    ('Minimum cover', 'Inside the complete-cover shrink loop'),
], [75 * mm, 99 * mm], font=7.8)
section('Complexity')
P('Classic window: O(n) boundary movements. With state update U: O(nU). '
  'Hash/array state usually O(n) total; ordered state O(n log k); monotonic deque '
  'O(n) amortized. Space ranges from O(1) to O(k) or O(alphabet).')
callout('The one sentence to remember',
        'Expand to explore, shrink to restore or optimize, maintain only what the '
        'active interval needs, and never discard a boundary unless you can prove '
        'it cannot matter later.', 'teal')
section('Mastery test')
P('You have mastered sliding window when you can: recognize it without keywords; '
  'derive rather than memorize the loop; state the invariant; explain answer '
  'placement; prove pointer movements; identify negative-number failures; choose '
  'the right state structure; and reduce a new story to a known window family.')

section('Seven-day mastery plan')
table(['Day', 'Focus', 'Deliverable'], [
    ('1', 'Core idea + fixed windows', 'Solve practice 1-5 and trace two by hand'),
    ('2', 'Variable longest/shortest', 'Solve 7-10; write the invariant first'),
    ('3', 'String frequency state', 'Solve 6, 11, and 15 without copying templates'),
    ('4', 'Counting transformations', 'Solve 12-14 and explain right-left+1'),
    ('5', 'Monotonic deques', 'Solve 16-17; prove every deque pop is safe'),
    ('6', 'Failure cases + advanced state', 'Solve 18-20 and compare alternatives'),
    ('7', 'Mixed timed revision', 'Pick six unseen problems; classify before coding'),
], [14 * mm, 57 * mm, 103 * mm], font=7.4)

section('Before submitting any window solution')
bullets([
    'Check empty input, k bounds, strict versus non-strict comparisons, and overflow.',
    'Verify state exactly matches [left, right] after every add and remove.',
    'Confirm the answer line occurs only when its candidate is mathematically known.',
    'State the assumption that makes moving left irreversible and safe.',
    'Test against a brute-force oracle on small random and adversarial inputs.',
])


doc = GuideDocTemplate(
    str(OUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
    topMargin=17 * mm, bottomMargin=17 * mm,
    title='Sliding Window DSA Pattern - Complete Guide',
    author='OpenAI Codex', subject='Data Structures and Algorithms',
)
doc.multiBuild(story, canvasmaker=NumberedCanvas)
print(OUT.resolve())
