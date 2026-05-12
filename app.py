"""
app.py — Periodic Table Trainer Logic
======================================
All game logic lives here. The HTML file handles page structure only.
PyScript lets Python interact with the browser DOM using the `document`
object (same concept as JavaScript's document.getElementById etc.).

Key PyScript DOM calls used here:
  document.getElementById("some-id")          → get one element
  element.textContent = "text"                → set plain text
  element.innerHTML = "<b>html</b>"           → set HTML content
  element.style.display = "none"/"block"      → show/hide
  document.createElement("tag")              → make a new DOM element
  parent.appendChild(child)                  → add element to the page
  element.classList.add("cls")               → add a CSS class
  element.classList.remove("cls")            → remove a CSS class
  element.addEventListener("click", handler) → attach event listener
"""

import random
from js import document, console, window
import json
from pyodide.ffi import create_proxy


# ─────────────────────────────────────────────────────────────────────────────
# ELEMENT DATA
# Each element is a dict: number (int), symbol (str), name (str),
# and grid position: row and col in the 18-column periodic table.
# Lanthanides are placed in row 9, actinides in row 10.
# Row 8 is left empty as a visual gap above the f-block.
# ─────────────────────────────────────────────────────────────────────────────

ELEMENTS = [
    # period 1
    {"number":1,   "symbol":"H",  "name":"Hydrogen",      "row":1, "col":1},
    {"number":2,   "symbol":"He", "name":"Helium",         "row":1, "col":18},
    # period 2
    {"number":3,   "symbol":"Li", "name":"Lithium",        "row":2, "col":1},
    {"number":4,   "symbol":"Be", "name":"Beryllium",      "row":2, "col":2},
    {"number":5,   "symbol":"B",  "name":"Boron",          "row":2, "col":13},
    {"number":6,   "symbol":"C",  "name":"Carbon",         "row":2, "col":14},
    {"number":7,   "symbol":"N",  "name":"Nitrogen",       "row":2, "col":15},
    {"number":8,   "symbol":"O",  "name":"Oxygen",         "row":2, "col":16},
    {"number":9,   "symbol":"F",  "name":"Fluorine",       "row":2, "col":17},
    {"number":10,  "symbol":"Ne", "name":"Neon",           "row":2, "col":18},
    # period 3
    {"number":11,  "symbol":"Na", "name":"Sodium",         "row":3, "col":1},
    {"number":12,  "symbol":"Mg", "name":"Magnesium",      "row":3, "col":2},
    {"number":13,  "symbol":"Al", "name":"Aluminum",       "row":3, "col":13},
    {"number":14,  "symbol":"Si", "name":"Silicon",        "row":3, "col":14},
    {"number":15,  "symbol":"P",  "name":"Phosphorus",     "row":3, "col":15},
    {"number":16,  "symbol":"S",  "name":"Sulfur",         "row":3, "col":16},
    {"number":17,  "symbol":"Cl", "name":"Chlorine",       "row":3, "col":17},
    {"number":18,  "symbol":"Ar", "name":"Argon",          "row":3, "col":18},
    # period 4
    {"number":19,  "symbol":"K",  "name":"Potassium",      "row":4, "col":1},
    {"number":20,  "symbol":"Ca", "name":"Calcium",        "row":4, "col":2},
    {"number":21,  "symbol":"Sc", "name":"Scandium",       "row":4, "col":3},
    {"number":22,  "symbol":"Ti", "name":"Titanium",       "row":4, "col":4},
    {"number":23,  "symbol":"V",  "name":"Vanadium",       "row":4, "col":5},
    {"number":24,  "symbol":"Cr", "name":"Chromium",       "row":4, "col":6},
    {"number":25,  "symbol":"Mn", "name":"Manganese",      "row":4, "col":7},
    {"number":26,  "symbol":"Fe", "name":"Iron",           "row":4, "col":8},
    {"number":27,  "symbol":"Co", "name":"Cobalt",         "row":4, "col":9},
    {"number":28,  "symbol":"Ni", "name":"Nickel",         "row":4, "col":10},
    {"number":29,  "symbol":"Cu", "name":"Copper",         "row":4, "col":11},
    {"number":30,  "symbol":"Zn", "name":"Zinc",           "row":4, "col":12},
    {"number":31,  "symbol":"Ga", "name":"Gallium",        "row":4, "col":13},
    {"number":32,  "symbol":"Ge", "name":"Germanium",      "row":4, "col":14},
    {"number":33,  "symbol":"As", "name":"Arsenic",        "row":4, "col":15},
    {"number":34,  "symbol":"Se", "name":"Selenium",       "row":4, "col":16},
    {"number":35,  "symbol":"Br", "name":"Bromine",        "row":4, "col":17},
    {"number":36,  "symbol":"Kr", "name":"Krypton",        "row":4, "col":18},
    # period 5
    {"number":37,  "symbol":"Rb", "name":"Rubidium",       "row":5, "col":1},
    {"number":38,  "symbol":"Sr", "name":"Strontium",      "row":5, "col":2},
    {"number":39,  "symbol":"Y",  "name":"Yttrium",        "row":5, "col":3},
    {"number":40,  "symbol":"Zr", "name":"Zirconium",      "row":5, "col":4},
    {"number":41,  "symbol":"Nb", "name":"Niobium",        "row":5, "col":5},
    {"number":42,  "symbol":"Mo", "name":"Molybdenum",     "row":5, "col":6},
    {"number":43,  "symbol":"Tc", "name":"Technetium",     "row":5, "col":7},
    {"number":44,  "symbol":"Ru", "name":"Ruthenium",      "row":5, "col":8},
    {"number":45,  "symbol":"Rh", "name":"Rhodium",        "row":5, "col":9},
    {"number":46,  "symbol":"Pd", "name":"Palladium",      "row":5, "col":10},
    {"number":47,  "symbol":"Ag", "name":"Silver",         "row":5, "col":11},
    {"number":48,  "symbol":"Cd", "name":"Cadmium",        "row":5, "col":12},
    {"number":49,  "symbol":"In", "name":"Indium",         "row":5, "col":13},
    {"number":50,  "symbol":"Sn", "name":"Tin",            "row":5, "col":14},
    {"number":51,  "symbol":"Sb", "name":"Antimony",       "row":5, "col":15},
    {"number":52,  "symbol":"Te", "name":"Tellurium",      "row":5, "col":16},
    {"number":53,  "symbol":"I",  "name":"Iodine",         "row":5, "col":17},
    {"number":54,  "symbol":"Xe", "name":"Xenon",          "row":5, "col":18},
    # period 6
    {"number":55,  "symbol":"Cs", "name":"Cesium",         "row":6, "col":1},
    {"number":56,  "symbol":"Ba", "name":"Barium",         "row":6, "col":2},
    # La placeholder at col 3 — actual La is in row 9
    {"number":57,  "symbol":"La", "name":"Lanthanum",      "row":9, "col":3},
    {"number":58,  "symbol":"Ce", "name":"Cerium",         "row":9, "col":4},
    {"number":59,  "symbol":"Pr", "name":"Praseodymium",   "row":9, "col":5},
    {"number":60,  "symbol":"Nd", "name":"Neodymium",      "row":9, "col":6},
    {"number":61,  "symbol":"Pm", "name":"Promethium",     "row":9, "col":7},
    {"number":62,  "symbol":"Sm", "name":"Samarium",       "row":9, "col":8},
    {"number":63,  "symbol":"Eu", "name":"Europium",       "row":9, "col":9},
    {"number":64,  "symbol":"Gd", "name":"Gadolinium",     "row":9, "col":10},
    {"number":65,  "symbol":"Tb", "name":"Terbium",        "row":9, "col":11},
    {"number":66,  "symbol":"Dy", "name":"Dysprosium",     "row":9, "col":12},
    {"number":67,  "symbol":"Ho", "name":"Holmium",        "row":9, "col":13},
    {"number":68,  "symbol":"Er", "name":"Erbium",         "row":9, "col":14},
    {"number":69,  "symbol":"Tm", "name":"Thulium",        "row":9, "col":15},
    {"number":70,  "symbol":"Yb", "name":"Ytterbium",      "row":9, "col":16},
    {"number":71,  "symbol":"Lu", "name":"Lutetium",       "row":9, "col":17},
    {"number":72,  "symbol":"Hf", "name":"Hafnium",        "row":6, "col":4},
    {"number":73,  "symbol":"Ta", "name":"Tantalum",       "row":6, "col":5},
    {"number":74,  "symbol":"W",  "name":"Tungsten",       "row":6, "col":6},
    {"number":75,  "symbol":"Re", "name":"Rhenium",        "row":6, "col":7},
    {"number":76,  "symbol":"Os", "name":"Osmium",         "row":6, "col":8},
    {"number":77,  "symbol":"Ir", "name":"Iridium",        "row":6, "col":9},
    {"number":78,  "symbol":"Pt", "name":"Platinum",       "row":6, "col":10},
    {"number":79,  "symbol":"Au", "name":"Gold",           "row":6, "col":11},
    {"number":80,  "symbol":"Hg", "name":"Mercury",        "row":6, "col":12},
    {"number":81,  "symbol":"Tl", "name":"Thallium",       "row":6, "col":13},
    {"number":82,  "symbol":"Pb", "name":"Lead",           "row":6, "col":14},
    {"number":83,  "symbol":"Bi", "name":"Bismuth",        "row":6, "col":15},
    {"number":84,  "symbol":"Po", "name":"Polonium",       "row":6, "col":16},
    {"number":85,  "symbol":"At", "name":"Astatine",       "row":6, "col":17},
    {"number":86,  "symbol":"Rn", "name":"Radon",          "row":6, "col":18},
    # period 7
    {"number":87,  "symbol":"Fr", "name":"Francium",       "row":7, "col":1},
    {"number":88,  "symbol":"Ra", "name":"Radium",         "row":7, "col":2},
    # Ac placeholder at col 3 — actual Ac is in row 10
    {"number":89,  "symbol":"Ac", "name":"Actinium",       "row":10,"col":3},
    {"number":90,  "symbol":"Th", "name":"Thorium",        "row":10,"col":4},
    {"number":91,  "symbol":"Pa", "name":"Protactinium",   "row":10,"col":5},
    {"number":92,  "symbol":"U",  "name":"Uranium",        "row":10,"col":6},
    {"number":93,  "symbol":"Np", "name":"Neptunium",      "row":10,"col":7},
    {"number":94,  "symbol":"Pu", "name":"Plutonium",      "row":10,"col":8},
    {"number":95,  "symbol":"Am", "name":"Americium",      "row":10,"col":9},
    {"number":96,  "symbol":"Cm", "name":"Curium",         "row":10,"col":10},
    {"number":97,  "symbol":"Bk", "name":"Berkelium",      "row":10,"col":11},
    {"number":98,  "symbol":"Cf", "name":"Californium",    "row":10,"col":12},
    {"number":99,  "symbol":"Es", "name":"Einsteinium",    "row":10,"col":13},
    {"number":100, "symbol":"Fm", "name":"Fermium",        "row":10,"col":14},
    {"number":101, "symbol":"Md", "name":"Mendelevium",    "row":10,"col":15},
    {"number":102, "symbol":"No", "name":"Nobelium",       "row":10,"col":16},
    {"number":103, "symbol":"Lr", "name":"Lawrencium",     "row":10,"col":17},
    {"number":104, "symbol":"Rf", "name":"Rutherfordium",  "row":7, "col":4},
    {"number":105, "symbol":"Db", "name":"Dubnium",        "row":7, "col":5},
    {"number":106, "symbol":"Sg", "name":"Seaborgium",     "row":7, "col":6},
    {"number":107, "symbol":"Bh", "name":"Bohrium",        "row":7, "col":7},
    {"number":108, "symbol":"Hs", "name":"Hassium",        "row":7, "col":8},
    {"number":109, "symbol":"Mt", "name":"Meitnerium",     "row":7, "col":9},
    {"number":110, "symbol":"Ds", "name":"Darmstadtium",   "row":7, "col":10},
    {"number":111, "symbol":"Rg", "name":"Roentgenium",    "row":7, "col":11},
    {"number":112, "symbol":"Cn", "name":"Copernicium",    "row":7, "col":12},
    {"number":113, "symbol":"Nh", "name":"Nihonium",       "row":7, "col":13},
    {"number":114, "symbol":"Fl", "name":"Flerovium",      "row":7, "col":14},
    {"number":115, "symbol":"Mc", "name":"Moscovium",      "row":7, "col":15},
    {"number":116, "symbol":"Lv", "name":"Livermorium",    "row":7, "col":16},
    {"number":117, "symbol":"Ts", "name":"Tennessine",     "row":7, "col":17},
    {"number":118, "symbol":"Og", "name":"Oganesson",      "row":7, "col":18},
]

# Build a lookup from atomic number → element dict (used when highlighting cells)
BY_NUMBER = {e["number"]: e for e in ELEMENTS}


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ STATE
# These module-level variables hold the current question and history.
# ─────────────────────────────────────────────────────────────────────────────

current_element = None   # the element being quizzed on right now
history = []             # list of result dicts
revealed = set()         # atomic numbers of correctly answered elements

# Load included set from localStorage, falling back to all elements if nothing saved.
_saved = window.localStorage.getItem("included_elements")
if _saved:
    included = set(json.loads(_saved))
else:
    included = {el["number"] for el in ELEMENTS}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def save_included():
    """Persist the included set to localStorage so it survives page refreshes."""
    window.localStorage.setItem("included_elements", json.dumps(list(included)))


def get_checked_elements():
    """Return list of elements currently included in the quiz."""
    return [el for el in ELEMENTS if el["number"] in included]


def get_field_value(el, field):
    """Return the string value for a given field name ('number','symbol','name')."""
    if field == "number":
        return str(el["number"])
    elif field == "symbol":
        return el["symbol"]
    elif field == "name":
        return el["name"]


def cell_background(number):
    """Return the correct background colour for a quiz cell based on its state."""
    if number not in included:
        return "#ccc"       # unchecked — grey
    if number in revealed:
        return "#c8f0c8"    # correctly answered — green
    return ""               # active quiz cell — default


def highlight_cell(element):
    """Restore all cells to their correct background, then highlight the target."""
    for el in ELEMENTS:
        cell = document.getElementById(f"quiz-cell-{el['number']}")
        if cell:
            cell.style.background = cell_background(el["number"])
    cell = document.getElementById(f"quiz-cell-{element['number']}")
    if cell:
        cell.style.background = "#ffe066"


def reveal_cell(element):
    """Show symbol and number on a quiz cell, marking it as permanently revealed."""
    revealed.add(element["number"])
    cell = document.getElementById(f"quiz-cell-{element['number']}")
    if cell:
        cell.innerHTML = f'<span class="el-sym">{element["symbol"]}</span><span class="el-num">{element["number"]}</span>'
        cell.style.background = "#c8f0c8"  # light green to distinguish revealed cells
        cell.title = element["name"]  # hover text now that it's revealed


def reset_quiz(event=None):
    """Clear all revealed cells and reset the quiz state."""
    global current_element
    revealed.clear()
    current_element = None
    # Redraw the quiz table from scratch
    build_quiz_table()
    document.getElementById("quiz-prompt").textContent = 'Press "New Question" to begin.'
    document.getElementById("quiz-answer-area").style.display = "none"
    document.getElementById("quiz-feedback").textContent = ""


def normalize(text):
    """Lowercase and strip whitespace for answer comparison."""
    return text.strip().lower()


# ─────────────────────────────────────────────────────────────────────────────
# BUILD PERIODIC TABLES
# Renders element cells into a grid div. Called once on page load.
# show_labels=True  → reference table (shows symbol + number)
# show_labels=False → quiz table (blank cells)
# ─────────────────────────────────────────────────────────────────────────────

def build_quiz_table():
    """Draw the quiz table. Checked elements are blank; unchecked are greyed out
    and pre-revealed (since they are not part of the quiz). Already-revealed
    elements are shown in green."""
    container = document.getElementById("periodic-table-quiz")
    container.innerHTML = ""

    for el in ELEMENTS:
        cell = document.createElement("div")
        cell.className = "el-cell"
        cell.id = f"quiz-cell-{el['number']}"
        cell.setAttribute("style", f"grid-row:{el['row']}; grid-column:{el['col']}")

        if el["number"] not in included:
            cell.innerHTML = f'<span class="el-sym">{el["symbol"]}</span><span class="el-num">{el["number"]}</span>'
            cell.style.background = "#ccc"
            cell.title = el["name"]  # hover text for unchecked (already visible)
        elif el["number"] in revealed:
            cell.innerHTML = f'<span class="el-sym">{el["symbol"]}</span><span class="el-num">{el["number"]}</span>'
            cell.style.background = "#c8f0c8"
            cell.title = el["name"]  # hover text only after correctly answered
        # else: checked and not yet revealed — no title, no cheating!

        container.appendChild(cell)

    # Resize text to match current cell size after (re)building.
    # Guard: set_table_size is defined later in the file; on the very first
    # call (at startup) it doesn't exist yet, so we skip — it will be called
    # explicitly once defined.
    try:
        set_table_size()
    except NameError:
        pass


def build_ref_table():
    """Draw the static reference table with all labels."""
    container = document.getElementById("periodic-table-ref")
    container.innerHTML = ""
    for el in ELEMENTS:
        cell = document.createElement("div")
        cell.className = "el-cell"
        cell.setAttribute("style", f"grid-row:{el['row']}; grid-column:{el['col']}")
        url = f'https://en.wikipedia.org/wiki/{el["name"]}'
        name = el["name"]
        sym = el["symbol"]
        num = el["number"]
        cell.innerHTML = (
            f'<a class="el-link" href="{url}" target="_blank" title="{name}"><span class="el-sym">{sym}</span><span class="el-num">{num}</span></a>'
        )
        container.appendChild(cell)


build_quiz_table()
build_ref_table()


# ─────────────────────────────────────────────────────────────────────────────
# BUILD ELEMENTS LIST (Elements page)
# ─────────────────────────────────────────────────────────────────────────────

def build_element_list():
    tbody = document.getElementById("element-table-body")
    tbody.innerHTML = ""

    for el in ELEMENTS:
        row = document.createElement("tr")
        num = el["number"]
        row.innerHTML = (
            f'<td><input type="checkbox" id="check-{num}"'
            + (' checked' if num in included else '')
            + ' /></td>'
            f'<td>{num}</td>'
            f'<td>{el["symbol"]}</td>'
            f'<td>{el["name"]}</td>'
        )
        tbody.appendChild(row)
        # Wire the checkbox change event directly in Python
        cb = document.getElementById(f"check-{num}")
        def make_toggle(n):
            def handler(event):
                if n in included:
                    included.discard(n)
                else:
                    included.add(n)
                save_included()
                build_quiz_table()
            return handler
        cb.addEventListener("change", create_proxy(make_toggle(num)))


build_element_list()


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def new_question(event=None, keep_feedback=False):
    global current_element

    checked = get_checked_elements()
    if not checked:
        document.getElementById("quiz-prompt").textContent = (
            "No elements selected. Go to the Elements page and check some."
        )
        document.getElementById("quiz-answer-area").style.display = "none"
        return

    # Exclude already-revealed elements from the pool
    pool = [e for e in checked if e["number"] not in revealed]
    if not pool:
        document.getElementById("quiz-prompt").textContent = (
            "All selected elements revealed! Press Reset to start over."
        )
        document.getElementById("quiz-answer-area").style.display = "none"
        return
    # Avoid repeating the same element, unless it is the only one left
    if len(pool) > 1 and current_element in pool:
        pool.remove(current_element)
    current_element = random.choice(pool)

    prompt_field  = document.getElementById("prompt-field").value
    answer_field  = document.getElementById("answer-field").value

    # Guard against same field for prompt and answer
    if prompt_field == answer_field:
        document.getElementById("quiz-prompt").textContent = (
            "Prompt and Answer fields are the same — please choose different fields."
        )
        return

    prompt_value = get_field_value(current_element, prompt_field)

    document.getElementById("quiz-prompt").textContent = (
        f"{prompt_field.capitalize()}: {prompt_value}"
    )
    if not keep_feedback:
        document.getElementById("quiz-feedback").textContent = ""
    document.getElementById("quiz-input").value = ""
    document.getElementById("quiz-answer-area").style.display = "block"
    document.getElementById("quiz-input").focus()

    highlight_cell(current_element)


def submit_answer(event=None):
    if current_element is None:
        return

    given    = document.getElementById("quiz-input").value
    prompt_f = document.getElementById("prompt-field").value
    answer_f = document.getElementById("answer-field").value
    expected = get_field_value(current_element, answer_f)
    correct  = normalize(given) == normalize(expected)

    # Show feedback
    feedback = document.getElementById("quiz-feedback")
    if correct:
        feedback.textContent = "✓ Correct!"
        feedback.style.color = "green"
    else:
        feedback.textContent = f"✗ Wrong. Answer: {expected}"
        feedback.style.color = "red"

    # Record in history
    history.append({
        "element":      current_element,
        "prompt_field": prompt_f,
        "answer_field": answer_f,
        "expected":     expected,
        "given":        given,
        "correct":      correct,
    })

    if correct:
        reveal_cell(current_element)
        new_question(keep_feedback=True)

    update_progress()


def on_input_keydown(event):
    """Allow pressing Enter to submit."""
    if event.key == "Enter":
        submit_answer()


# ─────────────────────────────────────────────────────────────────────────────
# ELEMENTS PAGE — check/uncheck all
# ─────────────────────────────────────────────────────────────────────────────

def check_all(event=None):
    for el in ELEMENTS:
        included.add(el["number"])
        cb = document.getElementById(f"check-{el['number']}")
        if cb:
            cb.checked = True
    save_included()
    build_quiz_table()

def uncheck_all(event=None):
    for el in ELEMENTS:
        included.discard(el["number"])
        cb = document.getElementById(f"check-{el['number']}")
        if cb:
            cb.checked = False
    save_included()
    build_quiz_table()


# ─────────────────────────────────────────────────────────────────────────────
# PROGRESS PAGE
# ─────────────────────────────────────────────────────────────────────────────

def update_progress():
    """Rebuild the progress table and success rate. Called after each answer."""
    total   = len(history)
    correct = sum(1 for h in history if h["correct"])
    pct     = int(100 * correct / total) if total else 0

    document.getElementById("progress-rate").textContent = (
        f"Success rate: {correct}/{total} ({pct}%)"
    )

    tbody = document.getElementById("progress-body")
    tbody.innerHTML = ""

    # Show most recent attempts first
    for h in reversed(history):
        el = h["element"]
        row = document.createElement("tr")
        result_text = "✓" if h["correct"] else "✗"
        result_class = "result-correct" if h["correct"] else "result-wrong"
        row.innerHTML = (
            f'<td>{el["name"]} ({el["symbol"]})</td>'
            f'<td>{h["prompt_field"]}</td>'
            f'<td>{h["expected"]}</td>'
            f'<td>{h["given"]}</td>'
            f'<td class="{result_class}">{result_text}</td>'
        )
        tbody.appendChild(row)


# ─────────────────────────────────────────────────────────────────────────────
# WIRE UP EVENT LISTENERS
# ─────────────────────────────────────────────────────────────────────────────

# Quiz page buttons
document.getElementById("new-question-btn").addEventListener("click", create_proxy(new_question))
document.getElementById("submit-btn").addEventListener("click", create_proxy(submit_answer))
document.getElementById("quiz-input").addEventListener("keydown", create_proxy(on_input_keydown))
document.getElementById("reset-btn").addEventListener("click", create_proxy(reset_quiz))

# Elements page buttons
document.getElementById("check-all-btn").addEventListener("click", create_proxy(check_all))
document.getElementById("uncheck-all-btn").addEventListener("click", create_proxy(uncheck_all))

# ─────────────────────────────────────────────────────────────────────────────
# MOBILE / RESPONSIVE LAYOUT
# MOBILE_BREAKPOINT is the single source of truth for when mobile mode kicks in.
# Python adds/removes the "mobile" class on <body>; CSS rules keyed on
# "body.mobile" activate accordingly. This avoids duplicating the value in CSS.
# MAX_CELL_SIZE caps the table on wide desktop screens.
# ─────────────────────────────────────────────────────────────────────────────

MOBILE_BREAKPOINT = 600   # px — change here to adjust everywhere
MAX_CELL_SIZE     = 40    # px — table stops growing beyond this cell size


def close_sidebar(event=None):
    document.getElementById("sidebar").classList.remove("open")
    document.getElementById("sidebar-overlay").style.display = "none"


def toggle_sidebar(event=None):
    """Open the sidebar if closed, close it if open."""
    sidebar = document.getElementById("sidebar")
    if "open" in sidebar.classList:
        close_sidebar()
    else:
        sidebar.classList.add("open")
        document.getElementById("sidebar-overlay").style.display = "block"


document.getElementById("hamburger").addEventListener("click", create_proxy(toggle_sidebar))
document.getElementById("sidebar-overlay").addEventListener("click", create_proxy(close_sidebar))


def set_table_size():
    """Resize the periodic table cells to fit the available width.
    Also applies or removes mobile layout based on MOBILE_BREAKPOINT."""
    is_mobile = window.innerWidth < MOBILE_BREAKPOINT

    # Apply or remove mobile CSS class on <body>
    if is_mobile:
        document.body.classList.add("mobile")
    else:
        document.body.classList.remove("mobile")
        close_sidebar()  # ensure sidebar is closed if window is widened

    sidebar_w = 0 if is_mobile else 120   # sidebar not in flow on mobile
    padding   = 24 if not is_mobile else 24
    available = window.innerWidth - sidebar_w - padding

    # The table is 18 columns + 17 gaps of 2px each.
    # Solve: 18*cell + 17*2 = available  →  cell = (available - 34) / 18
    cell_size = int((available - 34) / 18)
    cell_size = max(8, min(cell_size, MAX_CELL_SIZE))  # clamp to [8, MAX_CELL_SIZE]

    # Font sizes scale proportionally to cell size.
    # At cell=40: sym=12px (ratio 0.30), num=9px (ratio 0.22).
    sym_size = max(5, round(cell_size * 0.30))
    num_size = max(4, round(cell_size * 0.22))

    for table_id in ["periodic-table-quiz", "periodic-table-ref"]:
        table = document.getElementById(table_id)
        if table:
            table.style.setProperty("--cell-size", f"{cell_size}px")

    for span in document.querySelectorAll(".el-sym"):
        span.style.fontSize = f"{sym_size}px"
    for span in document.querySelectorAll(".el-num"):
        span.style.fontSize = f"{num_size}px"


set_table_size()
# Recalculate on window resize (catches phone rotation too)
window.addEventListener("resize", create_proxy(lambda e: set_table_size()))

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────

def show_page(page_id):
    for div in ["quiz", "elements", "reference", "progress"]:
        document.getElementById(f"page-{div}").style.display = "none" if div != page_id else "block"

def make_nav(page_id):
    def handler(event):
        event.preventDefault()
        close_sidebar()  # auto-close sidebar after navigation on mobile
        show_page(page_id)
    return handler

for page in ["quiz", "elements", "reference", "progress"]:
    document.getElementById(f"nav-{page}").addEventListener("click", create_proxy(make_nav(page)))
