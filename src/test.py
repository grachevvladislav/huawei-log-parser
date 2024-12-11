import pandas as pd
import numpy as np
import streamlit as st
test = [[['Feature Name', 'Snapshot'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['Feature Name', 'LUN Copy'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['Feature Name', 'Clone'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['Feature Name', 'LUN Migration'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['Feature Name', 'HyperMirror'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['License Status', 'Valiлллd'], ['Open Status', 'Open'], ['Detail', ''], ['Feature Name', 'SmartTier']], [['Feature Name', 'SmartThin'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['Feature Name', 'SmartErase'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['Feature Name', 'vStore'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['Feature Name', 'SmartMotion'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']], [['Feature Name', 'SmartCache'], ['License Status', 'Valid'], ['Open Status', 'Open'], ['Detail', '']]]

options = st.multiselect(
    "What are your favorite colors",
    ["Green", "Yellow", "Red", "Blue"],
    ["Yellow", "Red"],
)

st.write("You selected:", options)
