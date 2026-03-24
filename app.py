import streamlit as st
from pydanticLayer import Recipe
from main import build_prompt, get_valid_recipe

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Cooking Assistant",
    page_icon="🍳",
    layout="centered"
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background-color: #0f0e0c; color: #f0ece4; }
#MainMenu, footer, header { visibility: hidden; }

.app-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #e8c97e;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.app-subtitle {
    font-size: 0.9rem;
    color: #7a7060;
    margin-top: 4px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.msg-user {
    background: #1e1c18;
    border: 1px solid #2e2b24;
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #f0ece4;
    font-size: 0.95rem;
    max-width: 78%;
    margin-left: auto;
    text-align: right;
}
.msg-ai {
    background: #181610;
    border: 1px solid #2e2b24;
    border-left: 3px solid #e8c97e;
    border-radius: 4px 16px 16px 16px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #d4cfc6;
    font-size: 0.95rem;
    max-width: 85%;
}

.recipe-card {
    background: linear-gradient(145deg, #1a1814, #141210);
    border: 1px solid #3a3528;
    border-top: 3px solid #e8c97e;
    border-radius: 16px;
    padding: 24px 28px;
    margin: 10px 0;
    max-width: 85%;
}
.recipe-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    color: #e8c97e;
    margin-bottom: 4px;
}
.recipe-meta {
    font-size: 0.8rem;
    color: #7a7060;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 16px;
}
.recipe-meta span { margin-right: 16px; }
.section-label {
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #e8c97e;
    border-bottom: 1px solid #2e2b24;
    padding-bottom: 6px;
    margin: 16px 0 10px 0;
}
.ingredient-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 5px 0;
    border-bottom: 1px dotted #2a2820;
    font-size: 0.9rem;
}
.ingredient-name { color: #d4cfc6; }
.ingredient-qty  { color: #e8c97e; font-size: 0.85rem; font-weight: 500; }
.ingredient-sub  { color: #5a5448; font-size: 0.78rem; font-style: italic; }
.step-row {
    display: flex;
    gap: 14px;
    padding: 8px 0;
    border-bottom: 1px dotted #2a2820;
    font-size: 0.9rem;
    align-items: flex-start;
}
.step-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #e8c97e;
    min-width: 24px;
    font-weight: 700;
}
.step-text { color: #c8c4bc; line-height: 1.5; }

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge-easy   { background: #1a2e1a; color: #6dbf6d; border: 1px solid #2a4a2a; }
.badge-medium { background: #2e2a1a; color: #c9a84c; border: 1px solid #4a401a; }
.badge-hard   { background: #2e1a1a; color: #cf6060; border: 1px solid #4a2a2a; }

.stTextInput > div > div > input {
    background-color: #1a1814 !important;
    border: 1px solid #3a3528 !important;
    border-radius: 12px !important;
    color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 14px 18px !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #e8c97e !important;
    box-shadow: 0 0 0 2px rgba(232, 201, 126, 0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: #4a4640 !important; }

.stButton > button {
    background: #e8c97e !important;
    color: #0f0e0c !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 12px 28px !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    background: #f0d898 !important;
    transform: translateY(-1px) !important;
}

[data-testid="stSidebar"] {
    background-color: #0c0b09 !important;
    border-right: 1px solid #2a2820 !important;
}
.sidebar-dish {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: #e8c97e;
    padding: 8px 0;
    border-bottom: 1px solid #2a2820;
}
.sidebar-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #5a5448;
    margin-bottom: 6px;
}
hr { border-color: #2a2820 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "state" not in st.session_state:
    st.session_state.state = {"dish": None, "recipe": None, "constraints": []}


# ─────────────────────────────────────────────
# Render helpers
# ─────────────────────────────────────────────

def render_recipe_card(recipe: Recipe) -> str:
    badge_class = f"badge-{recipe.difficulty.lower()}"

    ingredients_html = ""
    for ing in recipe.ingredients:
        sub_html = f"<br><span class='ingredient-sub'>sub: {ing.substitute}</span>" if ing.substitute else ""
        ingredients_html += (
            f'<div class="ingredient-row">'
            f'<span class="ingredient-name">{ing.name}</span>'
            f'<span><span class="ingredient-qty">{ing.quantity}</span>{sub_html}</span>'
            f'</div>'
        )

    steps_html = ""
    for step in recipe.steps:
        steps_html += (
            f'<div class="step-row">'
            f'<span class="step-num">{step.step_number}</span>'
            f'<span class="step-text">{step.instruction}</span>'
            f'</div>'
        )
    return f"""
    <div class="recipe-card">
      <div class="recipe-title">{recipe.dish_name}</div>
      <div class="recipe-meta">
        <span>⏱ {recipe.cooking_time}</span>
        <span class="badge {badge_class}">{recipe.difficulty}</span>
      </div>
      <div class="section-label">Ingredients</div>
      {ingredients_html}
      <div class="section-label">Method</div>
      {steps_html}
    </div>
    """


def render_messages():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg.get("type") == "recipe_html":
            # Pre-rendered HTML string — safe to render directly, no type reconstruction needed
            st.markdown(msg["content"], unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="app-title" style="font-size:1.4rem">🍳 Kitchen</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle" style="margin-bottom:20px">Current Session</div>', unsafe_allow_html=True)

    s = st.session_state.state
    if s["dish"]:
        st.markdown('<div class="sidebar-label">Active Dish</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-dish">{s["dish"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#3a3528;font-size:0.85rem">No dish yet — ask me to make something!</div>', unsafe_allow_html=True)

    if s["constraints"]:
        st.markdown('<div class="sidebar-label" style="margin-top:16px">Requests so far</div>', unsafe_allow_html=True)
        for c in s["constraints"][-6:]:
            st.markdown(
                f'<div style="color:#5a5448;font-size:0.8rem;padding:3px 0;border-bottom:1px dotted #2a2820">{c}</div>',
                unsafe_allow_html=True
            )

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🗑 Clear session"):
        st.session_state.messages = []
        st.session_state.state = {"dish": None, "recipe": None, "constraints": []}
        st.rerun()


# ─────────────────────────────────────────────
# Main layout
# ─────────────────────────────────────────────

st.markdown('<div class="app-title">AI Cooking Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Ask for a recipe, tweak it, or ask anything about cooking</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

render_messages()

col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        label="",
        placeholder="e.g. Make me a vegan pasta, no garlic...",
        key=f"user_input_{len(st.session_state.messages)}",  # resets input after each send
        label_visibility="collapsed"
    )
with col2:
    send = st.button("Send →")

# ─────────────────────────────────────────────
# Handle send — calls main.py logic directly
# ─────────────────────────────────────────────

if send and user_input.strip():
    query = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.state["constraints"].append(query)

    with st.spinner("Thinking..."):
        try:
            prompt = build_prompt(query, st.session_state.state)
            output = get_valid_recipe(prompt, st.session_state.state)
        except Exception as e:
            output = None
            st.error(f"Something went wrong: {e}")

    if output is None:
        st.session_state.messages.append({
            "role": "ai",
            "content": "Sorry, I couldn't generate a valid response after multiple attempts. Please try rephrasing."
        })
    elif isinstance(output, Recipe):
        st.session_state.state["recipe"] = output.dict()
        st.session_state.state["dish"] = output.dish_name
        html = render_recipe_card(output)
        st.session_state.messages.append({"role": "ai", "type": "recipe_html", "content": html})
    else:
        st.session_state.messages.append({"role": "ai", "content": output})

    st.rerun()