import streamlit as st


def aplicar_estilos():
    st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.05rem;
        margin-bottom: 1.6rem;
    }

    .soft-card {
        background-color: #f8fafc;
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }

    .result-card {
        background-color: #ffffff;
        padding: 1.1rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    .state-good {
        background-color: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 0.9rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .state-risk {
        background-color: #fffbeb;
        border: 1px solid #fde68a;
        color: #92400e;
        padding: 0.9rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .state-bad {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 0.9rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.95rem;
    }
    </style>
    """, unsafe_allow_html=True)
