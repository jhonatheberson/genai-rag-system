import streamlit as st
from datetime import datetime
import os
import pandas as pd
from db_service import db_service


def render_analytics_dashboard():
    # Set page title with neuai branding
    st.title("Analytics Dashboard")

    # Add back button
    if st.button("← Back to Chat", type="primary"):
        st.session_state.show_analytics = False
        st.rerun()

    # Document Statistics
    st.header("📊 Document Analytics")

    # Get document statistics
    doc_stats = db_service.get_document_stats()

    # Create metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documents", doc_stats["total_documents"])
    with col2:
        st.metric("Total Chunks", doc_stats["total_chunks"])
    with col3:
        avg_size = (
            round(doc_stats["total_size"] / 1024, 2)
            if doc_stats["total_documents"] > 0
            else 0
        )
        st.metric("Average File Size (KB)", avg_size)

    # Document formats distribution
    if doc_stats["formats"]:
        format_counts = {}
        for doc in db_service.documents.values():
            format_counts[doc.get("format", "Unknown")] = (
                format_counts.get(doc.get("format", "Unknown"), 0) + 1
            )

        # Create bar chart for format distribution
        st.subheader("Document Format Distribution")
        format_df = pd.DataFrame(
            {
                "Format": list(format_counts.keys()),
                "Count": list(format_counts.values()),
            }
        )
        st.bar_chart(format_df.set_index("Format"), color="#FFB81C")  # Yellow

    # Document Timeline
    st.subheader("Document Upload Timeline")
    if db_service.documents:
        timeline_data = pd.DataFrame(
            [
                {
                    "Document": doc.get("filename", "Unknown"),
                    "Upload Time": pd.to_datetime(
                        doc.get("upload_time", datetime.now())
                    ),
                    "Size (KB)": doc.get("file_size", 0) / 1024,
                }
                for doc in db_service.documents.values()
            ]
        )
        timeline_data = timeline_data.sort_values("Upload Time")

        # Create line chart for document uploads over time
        st.line_chart(
            timeline_data.set_index("Upload Time")["Size (KB)"],
            use_container_width=True,
            color="#00A1DE",
        )

    # Conversation Analytics
    st.header("💬 Conversation Analytics")

    # Prepare conversation data
    conv_data = []

    for session_id, session in db_service.conversations.items():
        messages = session.get("messages", [])
        if messages:
            conv_data.append(
                {
                    "session_id": session_id,
                    "message_count": len(messages),
                    "start_time": messages[0].get("timestamp"),
                    "last_activity": messages[-1].get("timestamp"),
                }
            )

    if conv_data:
        df_conv = pd.DataFrame(conv_data)

        # Session activity metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Sessions", len(df_conv))
        with col2:
            avg_messages = round(sum(df_conv["message_count"]) / len(df_conv), 2)
            st.metric("Average Messages/Session", avg_messages)

        # Message count distribution
        st.subheader("Messages per Session")
        message_counts = pd.DataFrame(
            {"Session": range(len(df_conv)), "Messages": df_conv["message_count"]}
        )
        st.bar_chart(message_counts.set_index("Session"), color="#FF6B00")  # Orange

    # Document Processing Performance
    st.header("⚡ Processing Performance")

    # Calculate average chunk size
    if doc_stats["total_chunks"] > 0:
        # total_chars = sum(len(chunk.get('text', '')) for chunk in db_service.chunks.values())
        total_chars = sum(
            len(chunk.get("text", "")) for chunk in db_service.chunks.find()
        )
        avg_chunk_size = total_chars / doc_stats["total_chunks"]
        st.metric("Average Chunk Size (characters)", round(avg_chunk_size, 2))

        # Chunk size distribution
        # chunk_sizes = [len(chunk.get('text', '')) for chunk in db_service.chunks.values()]
        chunk_sizes = [len(chunk.get("text", "")) for chunk in db_service.chunks.find()]
        st.subheader("Chunk Size Distribution")
        chunk_df = pd.DataFrame({"Chunk": range(len(chunk_sizes)), "Size": chunk_sizes})
        st.line_chart(chunk_df.set_index("Chunk"), color="#00A1DE")  # Pool Blue

    # Footer with Neuai branding and logo
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            "© 2024 Neuai Engineering and Software • [Neuaieng.com](https://www.Neuaieng.com)"
        )
    with col2:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "Neuai_logo.png")
            st.image(logo_path, width=100)  # Smaller logo
        except Exception as e:
            st.warning("Unable to load Neuai logo")
