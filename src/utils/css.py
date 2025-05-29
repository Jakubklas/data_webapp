side_bar_buttons = """
<style>
  /* Target all buttons inside the sidebar and make them full-width */
  [data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
  }
</style>
"""

wide_page =     """
<style>
  /* only bump the MAIN content area, not the sidebar */
  [data-testid="stAppViewContainer"] > [data-testid="stMain"] {
    max-width: 60% !important;   /* 80% of the browser width */
    margin: 0 auto;              /* centre it */
    padding-left: 2rem;
    padding-right: 2rem;
  }
</style>
"""