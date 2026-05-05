### 1. Input Widgets

* st.text_input("Label")          # single line text
* st.text_area("Label")           # multi line text
* st.number_input("Label")        # number
* st.selectbox("Label", options)  # dropdown
* st.multiselect("Label", options) # multi select
* st.slider("Label", min, max)    # slider
* st.checkbox("Label")            # checkbox
* st.radio("Label", options)      # radio button
* st.file_uploader("Label")       # file upload
* st.button("Label")              # button
* st.date_input("Label")          # date picker

### 2. Display

* st.write("Text")                    # write anything
* st.markdown("# Markdown")          # markdown
* st.header("Header")               # header
* st.subheader("Subheader")           # subheader
* st.code("print('code')")         # code block
* st.dataframe(df)                 # dataframe
* st.table(df)                     # table
* st.metric("Label", 42)             # metric
* st.json(data)                    # JSON
* st.image("image.jpg")           # image
* st.audio("audio.mp3")             # audio
* st.video("video.mp4")             # video

# layout
* st.sidebar.write("Sidebar")       # sidebar
* st.columns([1, 2, 3])             # columns
* st.expander("Expander")          # expander
* st.empty()                         # placeholder

# chat elements (for chat apps)
* st.chat_message("user").write("Hello")
* st.chat_input("Ask a question...")

# styling
* st.success("Success!")
* st.info("Info!")
* st.warning("Warning!")
* st.error("Error!")


# charts
* st.line_chart(df)
* st.area_chart(df)
* st.bar_chart(df)
* st.map(df)
* st.pyplot(plt)
* st.plotly_chart(fig)


# other
* st.write("Progress:", bar)
* st.progress(50)
* st.spinner("Loading...")
* st.stop()
* st.balloons()
* st.snow()


# with syntax works for many elements
* with st.expander("More"):
    st.write("Hidden content")

# status (new)
* with st.status("Pending...", expanded=True) as status:
    st.write("Doing step 1...")
    st.write("Doing step 2...")
    st.write("Done!")
    status.update(label="Done!", state="complete")



# 1. Sidebar
* st.sidebar.header("Settings")

# Sidebar inputs
* api_key = st.sidebar.text_input("OpenAI Key", type="password")
* model_name = st.sidebar.selectbox(
    "Model", 
    ["gpt-3.5-turbo", "gpt-4.0", "gpt-4o", "gpt-5.1"]
)

# 2. Columns (side-by-side)
* col1, col2 = st.columns(2)

* with col1:
    st.header("Input")
    user_input = st.text_area("Ask something", height=200)
    submit_btn = st.button("Ask")

* with col2:
    st.header("Output")
    if submit_btn and user_input:
        st.write("Thinking...")
        # AI logic here
        response = f"AI response to: {user_input}"
        st.success(response)

# 3. Expanders (collapsible sections)
* with st.expander("Advanced Settings"):
    st.slider("Temperature", 0.0, 2.0, 0.7)
    st.checkbox("Enable Debug Mode")

# 4. Status spinner (shows when working)
* if submit_btn:
    with st.spinner("Processing..."):
        # Imagine heavy computation here
        import time
        time.sleep(2)  # simulate work
        st.success("Done!")

# 5. Chat interface (very popular!)
* if "messages" not in st.session_state:
    * st.session_state.messages = []

* for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

* if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response =* "Your AI response"
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# 6. Alerts
* if api_key == "":
    st.warning("Please enter API key in sidebar")


# Page Config
* st.set_page_config(page_title="Math Agent", layout="wide", page_icon="🤖")

# Color 
* CSS_STYLES = """
    <style>
        /* 1. Adjust the container to remove extra padding */
        .main {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* 2. Make the "Thinking..." box smaller and white */
        div[data-testid="stStatusText"] {
            font-size: 0.85rem;
            color: #ffffff;
        }
        
        /* 3. Style the "Thinking..." spinning wheel */
        div[data-testid="stStatus"] > div {
            color: #ffffff;
            background: transparent;
            border-color: #ffffff; /* White border for the spinner */
        }
        
        /* 4. Style the spinner animation itself if needed */
        div[data-testid="stStatus"] > div > div {
            border-top-color: #005fcc; /* Blue color for the spinner arc */
        }
    </style>
    """
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

# 4. Status spinner (shows when working)
* if submit_btn:
    with st.status("Thinking...", expanded=True) as status:
        st.write("Processing your request...")
        # Your AI logic here
        time.sleep(3)
        st.success("Done!")
