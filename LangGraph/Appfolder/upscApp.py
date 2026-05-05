# ── Imports ──────────────────────────────────────────────────────────────────
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.output_parsers import StrOutputParser
from define_schema import ScoreClass, TopicClass, BaseStateClass
import numpy as np
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="UPSC Essay Evaluator", layout="wide", page_icon="📚")
st.title("📚 UPSC Essay Writing Assistant")
st.caption("An AI-powered tool to evaluate your UPSC essays | Maker: Kuntal Chakraborty")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    candidate_name = st.text_input("Your Name")
    if candidate_name:
        st.success(f"Welcome, {candidate_name}!")
    st.divider()
    api_key = st.text_input("OpenAI API Key", type="password")
    flag = False
    if api_key:
        if len(api_key) >= 40:
            st.success("✅ API Key Verified")
            flag = True
        else:
            st.error("❌ Invalid API Key")

# ── Session State Init ────────────────────────────────────────────────────────
if "topic" not in st.session_state:
    st.session_state.topic = None
if "response" not in st.session_state:
    st.session_state.response = None

# ── Main App ──────────────────────────────────────────────────────────────────
if flag:

    # ── LLM Setup ──
    llm = ChatOpenAI(model="gpt-4o-mini", max_completion_tokens=800, api_key=api_key)
    llm_with_structure_score = llm.with_structured_output(schema=ScoreClass)
    llm_with_structure_topic = llm.with_structured_output(schema=TopicClass)

    # ── Node: Topic Generator ──
    def topicNode(state: BaseStateClass):
        topic_prompt = PromptTemplate.from_template(
            "You are a topic generator for UPSC government exam. "
            "Search the internet and generate only 1 trending UPSC essay topic."
        )
        duck_tool = DuckDuckGoSearchResults()
        topic_agent = create_agent(model=llm, tools=[duck_tool])
        res = topic_agent.invoke({"messages": [HumanMessage(topic_prompt.format())]})
        topic_pre = res["messages"][-1].content
        topic = llm_with_structure_topic.invoke(topic_pre)
        return {"topic": topic.topic}

    # ── Node: Language Quality ──
    def LanguageQualityChecker(state: BaseStateClass):
        prompt = PromptTemplate.from_template(
            """You are a strict language quality evaluator for UPSC essays.
Evaluate the language quality and generate a score between 0-10 and feedback (max 100 words).

topic: {topic}
essay: {essay}

feedback:
score:"""
        )
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"topic": state["topic"], "essay": state["essay"]})
        structured = llm_with_structure_score.invoke(result)
        return {"language_score": structured.score, "language_feedback": structured.feedback}

    # ── Node: Thought Quality ──
    def ThoughtQualityChecker(state: BaseStateClass):
        prompt = PromptTemplate.from_template(
            """You are a strict clarity of thought evaluator for UPSC essays.
Evaluate the clarity of thought and generate a score between 0-10 and feedback (max 100 words).

topic: {topic}
essay: {essay}

feedback:
score:"""
        )
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"topic": state["topic"], "essay": state["essay"]})
        structured = llm_with_structure_score.invoke(result)
        return {"thought_score": structured.score, "thought_feedback": structured.feedback}

    # ── Node: Relevance Checker ──
    def RelevanceChecker(state: BaseStateClass):
        prompt = PromptTemplate.from_template(
            """You are a strict topic relevance evaluator for UPSC essays.
Evaluate the relevance with the topic and generate a score between 0-10 and feedback (max 100 words).

topic: {topic}
essay: {essay}

feedback:
score:"""
        )
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"topic": state["topic"], "essay": state["essay"]})
        structured = llm_with_structure_score.invoke(result)
        return {"relevance_score": structured.score, "relevance_feedback": structured.feedback}

    # ── Node: Overall Feedback ──
    def overallFeedback(state: BaseStateClass):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a UPSC essay evaluator.
Give overall consolidated feedback based on 3 evaluators.

topic: {topic}
language feedback: {language_feedback}
clarity of thought feedback: {thought_feedback}
relevance feedback: {relevance_feedback}

Overall Feedback:""")
        ])
        chain = prompt | llm | StrOutputParser()
        feedback = chain.invoke({
            "topic": state["topic"],
            "language_feedback": state["language_feedback"],
            "thought_feedback": state["thought_feedback"],
            "relevance_feedback": state["relevance_feedback"],
        })
        overall_score = round(np.mean([
            state["language_score"],
            state["thought_score"],
            state["relevance_score"]
        ]), 1)
        return {"feed_back": feedback, "overall_score": overall_score}

    # ── Build Graph ──
    graph = StateGraph(BaseStateClass)
    graph.add_node("topicNode", topicNode)
    graph.add_node("LanguageQualityChecker", LanguageQualityChecker)
    graph.add_node("ThoughtQualityChecker", ThoughtQualityChecker)
    graph.add_node("RelevanceChecker", RelevanceChecker)
    graph.add_node("overallFeedback", overallFeedback)

    graph.add_edge(START, "topicNode")
    graph.add_edge("topicNode", "LanguageQualityChecker")
    graph.add_edge("topicNode", "ThoughtQualityChecker")
    graph.add_edge("topicNode", "RelevanceChecker")
    graph.add_edge("LanguageQualityChecker", "overallFeedback")
    graph.add_edge("ThoughtQualityChecker", "overallFeedback")
    graph.add_edge("RelevanceChecker", "overallFeedback")
    graph.add_edge("overallFeedback", END)

    work_flow = graph.compile()

    # ── Step 1: Generate Topic ──
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🎯 Generate Essay Topic", use_container_width=True):
            with st.spinner("Generating topic..."):
                res = work_flow.invoke({
                    "topic": None, "essay": "",
                    "language_score": 0.0, "language_feedback": "",
                    "thought_score": 0.0, "thought_feedback": "",
                    "relevance_score": 0.0, "relevance_feedback": "",
                    "overall_score": 0.0, "feed_back": ""
                })
                st.session_state.topic = res["topic"]

    if st.session_state.topic:
        st.info(f"📌 **Topic:** {st.session_state.topic}")

        # ── Step 2: Essay Input ──
        essay = st.text_area(
            "✍️ Write your essay here (word limit: 500)",
            height=300,
            placeholder="Start writing your essay here..."
        )
        word_count = len(essay.split()) if essay else 0
        st.caption(f"Word count: {word_count}/500")

        # ── Step 3: Evaluate ──
        if st.button("🔍 Evaluate My Essay", use_container_width=True, disabled=not essay):
            with st.spinner("Evaluating your essay..."):
                response = work_flow.invoke({
                    "topic": st.session_state.topic,
                    "essay": essay,
                    "language_score": 0.0, "language_feedback": "",
                    "thought_score": 0.0, "thought_feedback": "",
                    "relevance_score": 0.0, "relevance_feedback": "",
                    "overall_score": 0.0, "feed_back": ""
                })
                st.session_state.response = response

    # ── Step 4: Show Results ──
    if st.session_state.response:
        r = st.session_state.response
        st.divider()
        st.subheader("📊 Evaluation Results")

        # Overall Score
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏆 Overall Score", f"{r['overall_score']}/10")
        col2.metric("🔤 Language", f"{r['language_score']}/10")
        col3.metric("💡 Clarity", f"{r['thought_score']}/10")
        col4.metric("🎯 Relevance", f"{r['relevance_score']}/10")

        st.divider()

        # Detailed Feedback
        with st.expander("📝 Overall Feedback", expanded=True):
            st.write(r["feed_back"])

        col1, col2, col3 = st.columns(3)
        with col1:
            with st.expander("🔤 Language Feedback"):
                st.write(r["language_feedback"])
        with col2:
            with st.expander("💡 Clarity Feedback"):
                st.write(r["thought_feedback"])
        with col3:
            with st.expander("🎯 Relevance Feedback"):
                st.write(r["relevance_feedback"])

else:
    st.warning("⚠️ Please enter your OpenAI API Key in the sidebar to get started.")