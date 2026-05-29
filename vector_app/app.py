# vector_app/app.py
#
# Streamlit UI for the Yelp RAG app.
# Run it with:   streamlit run app.py     (NOT python app.py)
#
# Mental model: Streamlit re-runs this whole file top-to-bottom every time
# you interact with a widget. So we cache the expensive call (ask) to avoid
# re-hitting the APIs on every rerun.

import streamlit as st
from ask import ask


# --- page setup -------------------------------------------------------------
st.set_page_config(page_title="Yelp Review RAG", page_icon="🍴")
st.title("🍴 Yelp Review RAG")
st.caption("Ask a question about New Orleans restaurants. Answers are grounded in real Yelp reviews.")


# --- cached wrapper ---------------------------------------------------------
# @st.cache_data remembers the return value for a given (question, k).
# Re-ask the same thing -> instant, no API spend. Change either arg -> real call.
@st.cache_data(show_spinner=False)
def cached_ask(question, k):
    return ask(question, k)


# --- sidebar controls -------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    k = st.slider("Reviews to retrieve (k)", min_value=1, max_value=10, value=5)


# --- input form -------------------------------------------------------------
# A form batches the input + button so the script only reruns (and only calls
# Claude) when you hit Submit — not on every keystroke.
with st.form("ask_form"):
    question = st.text_input("Your question", placeholder="What do customers say about beignets?")
    submitted = st.form_submit_button("Ask")


# --- run + display ----------------------------------------------------------
if submitted and question:
    with st.spinner("Retrieving reviews and asking Claude..."):
        answer, sources = cached_ask(question, k)

    st.markdown("### Answer")
    st.markdown(answer)        # renders the [1] [2] citations as text

    with st.expander(f"Sources ({len(sources)} reviews)"):
        for i, r in enumerate(sources, start=1):
            # r = (review_id, business_name, city, stars, text)
            st.markdown(f"**[{i}] {r[3]}⭐ {r[1]} ({r[2]})**")
            st.write(r[4])
            st.divider()
