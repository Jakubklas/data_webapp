side_bar_buttons = """
<style>
  /* Target all buttons inside the sidebar and make them full-width */
  [data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
  }
</style>
"""

wide_page = """
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



overrides_widget_styling ="""
    <style>
      /* 1) Bold the header text and give a pale‐blue background when closed */
      div[role="button"][aria-expanded="false"] {
        font-weight: bold !important;
        background-color: #D9EAF7 !important;  /* pale blue */
      }
      /* 2) When open, use a slightly darker blue for the header */
      div[role="button"][aria-expanded="true"] {
        font-weight: bold !important;
        background-color: #A9CCE3 !important;  /* a deeper pastel blue */
      }
      /* 3) Style the expander body: very pale blue, padding, rounded corners */
      div[data-testid="stExpanderContent"] {
        background-color: #EBF5FB !important;   /* very pale blue */
        padding: 0.75rem !important;            /* ~12px padding */
        border-radius: 0.25rem !important;      /* small rounded corners */
      }
    </style>
"""