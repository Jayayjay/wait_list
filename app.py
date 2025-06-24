import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random

# Configure the page
st.set_page_config(
    page_title="Bandog Beta Access",
    page_icon="📊",
    layout="wide"
)

# Geeky finance-themed CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-bg: #0a0a0a;
        --secondary-bg: #1a1a1a;
        --accent-bg: #2a2a2a;
        --text-primary: #00ff88;
        --text-secondary: #88ff88;
        --text-muted: #666666;
        --border-color: #333333;
        --chart-green: #00ff88;
        --chart-red: #ff4444;
        --chart-blue: #4488ff;
    }
    
    .stApp {
        background: var(--primary-bg);
        color: var(--text-primary);
    }
    
    .main {
        padding: 1rem;
    }
    
    .terminal-header {
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 2rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .terminal-text {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-primary);
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .blink {
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    
    .metric-card {
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .form-section {
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .form-title {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-primary);
        font-size: 1.2rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .stTextInput > div > div > input {
        background: var(--accent-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--text-primary) !important;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2) !important;
    }
    
    .stTextInput label {
        color: var(--text-secondary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, var(--text-primary), var(--chart-blue)) !important;
        color: var(--primary-bg) !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.75rem 2rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3) !important;
    }
    
    .chart-container {
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .chart-title {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-primary);
        font-size: 1rem;
        margin-bottom: 1rem;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .status-bar {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin: 1rem 0;
    }
    
    .code-block {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin: 1rem 0;
        overflow-x: auto;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--primary-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-primary);
    }
</style>
""", unsafe_allow_html=True)

def get_brevo_config():
    """Get Brevo configuration from Streamlit secrets"""
    try:
        return {
            'api_key': st.secrets["brevo"]["api_key"],
            'list_id': st.secrets.get("brevo", {}).get("list_id", 1)
        }
    except KeyError:
        return None

def add_to_brevo(email, first_name, last_name, config):
    """Add subscriber to Brevo"""
    url = "https://api.brevo.com/v3/contacts"
    
    data = {
        "email": email,
        "attributes": {
            "FIRSTNAME": first_name,
            "LASTNAME": last_name
        },
        "listIds": [config['list_id']],
        "updateEnabled": True
    }
    
    headers = {
        "api-key": config['api_key'],
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.status_code, response.json()
    except Exception as e:
        return None, str(e)

def generate_mock_data():
    """Generate mock financial data for charts"""
    # Generate time series data
    dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='D')
    
    # Mock stock price data
    np.random.seed(42)
    price_data = []
    base_price = 100
    for i in range(len(dates)):
        change = np.random.normal(0, 2)
        base_price += change
        price_data.append(max(base_price, 10))  # Ensure positive prices
    
    # Mock portfolio data
    portfolio_value = [1000]
    for i in range(1, len(dates)):
        change = np.random.normal(0.05, 1.5)  # Daily return
        new_value = portfolio_value[-1] * (1 + change/100)
        portfolio_value.append(max(new_value, 1000))
    
    # Mock trading volume
    volume = np.random.lognormal(10, 1, len(dates))
    
    return pd.DataFrame({
        'date': dates,
        'price': price_data,
        'portfolio': portfolio_value,
        'volume': volume
    })

def create_terminal_header():
    """Create a terminal-style header"""
    st.markdown("""
    <div class="terminal-header">
        <div class="terminal-text">
            <span style="color: #666;">user@Bandog-beta:~$</span> ./initialize_access_portal.sh<br>
            <span style="color: #00ff88;">▶</span> Loading Bandog Beta Access Portal...<br>
            <span style="color: #00ff88;">▶</span> Establishing secure connection...<br>
            <span style="color: #00ff88;">▶</span> Market data feed: <span style="color: #4488ff;">ACTIVE</span><br>
            <span style="color: #00ff88;">▶</span> Authentication system: <span style="color: #4488ff;">READY</span><br>
            <span style="color: #00ff88;">▶</span> Status: <span style="color: #ffff00;">ACCEPTING BETA USERS</span><span class="blink">_</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_metrics_dashboard():
    """Create geeky financial metrics"""
    if 'metrics' not in st.session_state:
        st.session_state.metrics = {
            'beta_users': random.randint(17, 240),
            'api_calls': random.randint(1400, 1895),
            'uptime': random.uniform(80.7, 99.99),
            'latency': random.uniform(12, 45)
        }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.metrics['beta_users']:,}</div>
            <div class="metric-label">Beta Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.metrics['api_calls']:,}</div>
            <div class="metric-label">API Calls</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.metrics['uptime']:.2f}%</div>
            <div class="metric-label">Uptime</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.metrics['latency']:.0f}ms</div>
            <div class="metric-label">Latency</div>
        </div>
        """, unsafe_allow_html=True)

def create_financial_charts():
    """Create advanced interactive financial charts"""
    data = generate_mock_data()
    
    # Create subplots with enhanced layout
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('PORTFOLIO PERFORMANCE', 'PRICE & VOLUME'),
        vertical_spacing=0.15,
        row_heights=[0.7, 0.3]
    )
    
    # Portfolio performance
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['portfolio'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#00ff88', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 136, 0.1)'
        ),
        row=1, col=1
    )
    
    # Price data
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['price'],
            mode='lines',
            name='Price',
            line=dict(color='#4488ff', width=1.5),
            yaxis='y2'
        ),
        row=2, col=1
    )
    
    # Volume data
    fig.add_trace(
        go.Bar(
            x=data['date'],
            y=data['volume'],
            name='Volume',
            marker=dict(color='#666666', opacity=0.7),
            yaxis='y3'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='#00ff88', family='JetBrains Mono'),
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    
    # Update y-axes
    fig.update_yaxes(
        row=1, col=1,
        showgrid=False,
        zeroline=False,
        title_text="Value ($)"
    )
    
    fig.update_yaxes(
        row=2, col=1,
        showgrid=False,
        zeroline=False,
        title_text="Price ($)",
        side="left"
    )
    
    fig.update_yaxes(
        row=2, col=1,
        showgrid=False,
        zeroline=False,
        title_text="Volume",
        side="right",
        overlaying="y2"
    )
    
    return fig

def create_status_bar():
    """Create a geeky status bar"""
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="status-bar">
        <span style="color: #00ff88;">●</span> SYSTEM STATUS: OPERATIONAL | 
        <span style="color: #4488ff;">●</span> MARKET FEED: LIVE | 
        <span style="color: #ffff00;">●</span> TIME: {current_time} UTC | 
        <span style="color: #ff4444;">●</span> BETA SLOTS: LIMITED
    </div>
    """, unsafe_allow_html=True)

def main():
    # Terminal header
    create_terminal_header()
    
    # Status bar
    create_status_bar()
    
    # Metrics dashboard
    create_metrics_dashboard()
    
     # Beta access form 
    st.markdown('<div class="form-section"> BanDog: AI That Sniffs Out Market Moves Before They Happen Get real-time alerts on unusual stock volume surges—before the crowd notices. BanDog combines AI, sentiment analysis, and zero-lag market data to give traders and investors the unfair advantage they’ve been chasing. Built for speed. Trained for precision. Designed for alpha. <span class="blink">_</span> </div>', unsafe_allow_html=True)
    st.markdown('<div class="form-title">// REQUEST BETA ACCESS</div>', unsafe_allow_html=True)
    
    # Get Brevo configuration
    brevo_config = get_brevo_config()
    
    if not brevo_config:
        st.markdown("""
        <div class="code-block">
        ERROR: Missing API configuration
        
        # Add to .streamlit/secrets.toml
        [brevo]
        api_key = "your-brevo-api-key"
        list_id = 1
        
        # Get API key from: https://app.brevo.com/settings/keys/api
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with st.form("beta_access_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", placeholder="Enter first name")
        
        with col2:
            last_name = st.text_input("Last Name", placeholder="Enter last name")
        
        email = st.text_input("Email Address", placeholder="user@domain.com")
        
        submitted = st.form_submit_button("Initialize Beta Access")
        
        if submitted:
            if not all([first_name, last_name, email]) or "@" not in email:
                st.error("❌ VALIDATION FAILED: All fields required with valid email format")
            else:
                with st.spinner("🔄 Processing access request..."):
                    status_code, response = add_to_brevo(email, first_name, last_name, brevo_config)
                    
                    if status_code == 201:
                        st.success("✅ ACCESS GRANTED: Beta invitation sent to your email")
                        st.session_state.metrics['beta_users'] += 1
                        st.balloons()
                    elif status_code == 204:
                        st.info("ℹ️ DUPLICATE ENTRY: You're already registered for beta access")
                    else:
                        st.error("❌ SYSTEM ERROR: Unable to process request. Please retry.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    
    # Financial charts
    # st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    # fig = create_financial_charts()
    # st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    # st.markdown('</div>', unsafe_allow_html=True)
    
    # # Additional mini charts
    # col1, col2 = st.columns(2)
    
    # with col1:
    #     st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    #     st.markdown('<div class="chart-title">Real-Time P&L</div>', unsafe_allow_html=True)
        
    #     # Generate P&L data
    #     pnl_data = np.random.randn(100).cumsum()
    #     pnl_fig = go.Figure()
    #     pnl_fig.add_trace(go.Scatter(
    #         y=pnl_data,
    #         mode='lines',
    #         line=dict(color='#00ff88' if pnl_data[-1] > 0 else '#ff4444', width=2),
    #         fill='tozeroy'
    #     ))
    #     pnl_fig.update_layout(
    #         height=200,
    #         showlegend=False,
    #         plot_bgcolor='#1a1a1a',
    #         paper_bgcolor='#1a1a1a',
    #         font=dict(color='#00ff88', family='JetBrains Mono'),
    #         xaxis=dict(showgrid=False, showticklabels=False),
    #         yaxis=dict(showgrid=False),
    #         margin=dict(l=0, r=0, t=0, b=0)
    #     )
    #     st.plotly_chart(pnl_fig, use_container_width=True, config={'displayModeBar': False})
    #     st.markdown('</div>', unsafe_allow_html=True)
    
    # with col2:
    #     st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    #     st.markdown('<div class="chart-title">Risk Metrics</div>', unsafe_allow_html=True)
        
    #     # Risk gauge
    #     risk_value = random.uniform(20, 80)
    #     risk_fig = go.Figure(go.Indicator(
    #         mode = "gauge+number",
    #         value = risk_value,
    #         domain = {'x': [0, 1], 'y': [0, 1]},
    #         title = {'text': "Risk Level"},
    #         gauge = {
    #             'axis': {'range': [None, 100]},
    #             'bar': {'color': "#00ff88"},
    #             'steps': [
    #                 {'range': [0, 30], 'color': "#2a2a2a"},
    #                 {'range': [30, 70], 'color': "#1a1a1a"},
    #                 {'range': [70, 100], 'color': "#0a0a0a"}
    #             ],
    #             'threshold': {
    #                 'line': {'color': "red", 'width': 4},
    #                 'thickness': 0.75,
    #                 'value': 90
    #             }
    #         }
    #     ))
    #     risk_fig.update_layout(
    #         height=200,
    #         paper_bgcolor='#1a1a1a',
    #         font=dict(color='#00ff88', family='JetBrains Mono', size=10),
    #         margin=dict(l=0, r=0, t=0, b=0)
    #     )
    #     st.plotly_chart(risk_fig, use_container_width=True, config={'displayModeBar': False})
    #     st.markdown('</div>', unsafe_allow_html=True)
    
   
    # Footer with system info
    st.markdown("""
    <div class="code-block">
    SYSTEM INFO:
    ├── Platform: Bandog Beta v1.2.0
    ├── Environment: Production
    ├── Security: End-to-end encrypted
    ├── Compliance: SOC2, GDPR compliant
    └── Support: beta-support@Bandog.io
    
    © 2025 Bandog Labs. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
