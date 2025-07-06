import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Entity Relationships v2.0",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for black and golden theme
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main background and styling */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: #ffd700;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0 3rem 0;
        background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, transparent 100%);
        margin: -1rem -1rem 2rem -1rem;
        position: relative;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: radial-gradient(circle, rgba(255,215,0,0.1) 1px, transparent 1px);
        background-size: 20px 20px;
        opacity: 0.3;
    }
    
    .logo-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto 2rem auto;
        padding: 0 2rem;
    }
    
    .logo {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffd700;
        text-shadow: 2px 2px 4px rgba(255, 215, 0, 0.3);
    }
    
    .version-badge {
        background: linear-gradient(135deg, #ffd700, #ffed4e);
        color: #000;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-left: 12px;
        font-weight: 600;
    }
    
    .nav-links {
        display: flex;
        gap: 25px;
        list-style: none;
        margin: 0;
        padding: 0;
    }
    
    .nav-links a {
        color: #cccccc;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
        font-size: 0.95rem;
    }
    
    .nav-links a:hover,
    .nav-links a.active {
        color: #ffd700;
        text-shadow: 0 0 8px rgba(255, 215, 0, 0.5);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #ffd700, #ffed4e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        color: #cccccc;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Search section styling */
    .search-section {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #ffd700;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Content cards */
    .content-card {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #ffd700;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(255, 215, 0, 0.2);
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .card-title {
        font-size: 1.3rem;
        color: #ffd700;
        margin: 0;
        font-weight: 600;
    }
    
    .card-count {
        background: linear-gradient(135deg, #ffd700, #ffed4e);
        color: #000;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Entity items */
    .entity-item {
        background: rgba(255, 215, 0, 0.1);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #ffd700;
        transition: all 0.3s ease;
    }
    
    .entity-item:hover {
        background: rgba(255, 215, 0, 0.2);
        transform: translateX(5px);
        box-shadow: 0 3px 10px rgba(255, 215, 0, 0.3);
        border-left-width: 6px;
    }
    
    .entity-name {
        font-weight: 600;
        color: #ffd700;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    
    .entity-type {
        color: #ccc;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .relationship-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .relationship-type {
        background: rgba(255, 215, 0, 0.2);
        color: #ffd700;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .strength-high { background: #ffd700; color: #000; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .strength-medium { background: #ffed4e; color: #000; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .strength-low { background: #b8860b; color: #fff; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    
    .entity-description {
        font-size: 0.8rem;
        color: #ccc;
        line-height: 1.4;
        margin-bottom: 0.5rem;
    }
    
    .reference-link {
        color: #ffed4e;
        font-size: 0.75rem;
        text-decoration: none;
    }
    
    .reference-link:hover {
        color: #ffd700;
        text-decoration: underline;
    }
    
    /* Detail items */
    .detail-item {
        background: rgba(255, 215, 0, 0.08);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #ffed4e;
    }
    
    .detail-title {
        font-weight: 600;
        color: #ffd700;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .detail-description {
        font-size: 0.8rem;
        line-height: 1.4;
        color: #ccc;
        margin-bottom: 0.5rem;
    }
    
    .detail-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.7rem;
    }
    
    .detail-source {
        color: #ffed4e;
    }
    
    .detail-date {
        color: #888;
    }
    
    /* Streamlit specific overrides */
    .stSelectbox label, .stTextInput label {
        color: #ffd700 !important;
        font-weight: 600 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border: 2px solid #333 !important;
    }
    
    .stTextInput input {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border: 2px solid #333 !important;
        color: #ffd700 !important;
    }
    
    .stTextInput input:focus {
        border-color: #ffd700 !important;
        box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.2) !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #ffd700, #ffed4e) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4) !important;
    }
    
    /* Hide Streamlit elements */
    .css-1d391kg, .css-1v0mbdj {
        color: #ffd700;
    }
    
    .css-12oz5g7 {
        background: rgba(255, 215, 0, 0.1);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #ffd700;
    }
</style>
""", unsafe_allow_html=True)

# Entity data
@st.cache_data
def load_entity_data():
    return {
        "Apple": {
            "type": "Technology Company",
            "description": "Multinational technology corporation and one of the world's most valuable companies",
            "founded": "1976",
            "headquarters": "Cupertino, California",
            "relationships": [
                {
                    "name": "iPhone",
                    "type": "Product",
                    "relationshipType": "Core Product",
                    "strength": "High",
                    "description": "Apple's flagship smartphone product, accounting for majority of revenue",
                    "reference": "Apple Inc. Annual Report 2023",
                    "sourceUrl": "https://investor.apple.com",
                    "year": "2007-present"
                },
                {
                    "name": "Tim Cook",
                    "type": "Person",
                    "relationshipType": "CEO",
                    "strength": "High",
                    "description": "Chief Executive Officer since 2011, previously COO under Steve Jobs",
                    "reference": "Apple Leadership - Tim Cook Biography",
                    "sourceUrl": "https://apple.com/leadership",
                    "year": "2011-present"
                },
                {
                    "name": "TSMC",
                    "type": "Technology Company",
                    "relationshipType": "Supplier",
                    "strength": "High",
                    "description": "Primary semiconductor manufacturer for Apple's custom chips (A-series, M-series)",
                    "reference": "TSMC Q4 2023 Earnings Call",
                    "sourceUrl": "https://investor.tsmc.com",
                    "year": "2016-present"
                },
                {
                    "name": "Foxconn",
                    "type": "Manufacturing Company",
                    "relationshipType": "Contract Manufacturer",
                    "strength": "High",
                    "description": "Primary assembly partner for iPhone, iPad, and Mac products",
                    "reference": "Foxconn Technology Group Partnership Agreement",
                    "sourceUrl": "https://foxconn.com",
                    "year": "2000-present"
                },
                {
                    "name": "Samsung",
                    "type": "Technology Company",
                    "relationshipType": "Competitor/Supplier",
                    "strength": "Medium",
                    "description": "Competitor in smartphones while also supplying OLED displays and memory",
                    "reference": "Samsung Display Supply Agreement 2023",
                    "sourceUrl": "https://news.samsung.com",
                    "year": "2007-present"
                },
                {
                    "name": "App Store",
                    "type": "Platform",
                    "relationshipType": "Digital Platform",
                    "strength": "High",
                    "description": "Apple's digital distribution platform generating significant services revenue",
                    "reference": "App Store Ecosystem Study 2023",
                    "sourceUrl": "https://apple.com/app-store",
                    "year": "2008-present"
                }
            ]
        },
        "Tesla": {
            "type": "Automotive/Energy Company",
            "description": "Electric vehicle and clean energy company leading the transition to sustainable transport",
            "founded": "2003",
            "headquarters": "Austin, Texas",
            "relationships": [
                {
                    "name": "Elon Musk",
                    "type": "Person",
                    "relationshipType": "CEO/CTO",
                    "strength": "High",
                    "description": "CEO and product architect, joined as chairman in 2004, became CEO in 2008",
                    "reference": "Tesla SEC Filing 10-K 2023",
                    "sourceUrl": "https://ir.tesla.com",
                    "year": "2004-present"
                },
                {
                    "name": "Model S",
                    "type": "Product",
                    "relationshipType": "Flagship Vehicle",
                    "strength": "High",
                    "description": "Luxury electric sedan that established Tesla in premium EV market",
                    "reference": "Tesla Model S Launch Analysis",
                    "sourceUrl": "https://tesla.com",
                    "year": "2012-present"
                },
                {
                    "name": "Panasonic",
                    "type": "Technology Company",
                    "relationshipType": "Battery Partner",
                    "strength": "High",
                    "description": "Strategic partner for lithium-ion battery production at Gigafactory Nevada",
                    "reference": "Tesla-Panasonic Gigafactory Agreement",
                    "sourceUrl": "https://panasonic.com",
                    "year": "2014-present"
                },
                {
                    "name": "Supercharger Network",
                    "type": "Infrastructure",
                    "relationshipType": "Charging Infrastructure",
                    "strength": "High",
                    "description": "Proprietary fast-charging network, now opening to other manufacturers",
                    "reference": "Tesla Supercharger Expansion Report 2023",
                    "sourceUrl": "https://tesla.com/supercharger",
                    "year": "2012-present"
                },
                {
                    "name": "SpaceX",
                    "type": "Aerospace Company",
                    "relationshipType": "Sister Company",
                    "strength": "Medium",
                    "description": "Shared leadership and technology synergies through Elon Musk",
                    "reference": "SpaceX-Tesla Technology Sharing Analysis",
                    "sourceUrl": "https://spacex.com",
                    "year": "2002-present"
                },
                {
                    "name": "Full Self-Driving",
                    "type": "Technology",
                    "relationshipType": "Core Technology",
                    "strength": "High",
                    "description": "Autonomous driving technology using neural networks and computer vision",
                    "reference": "Tesla AI Day Presentation 2023",
                    "sourceUrl": "https://tesla.com/AI",
                    "year": "2016-present"
                }
            ]
        },
        "Microsoft": {
            "type": "Technology Company",
            "description": "Multinational technology corporation focused on software, cloud computing, and AI",
            "founded": "1975",
            "headquarters": "Redmond, Washington",
            "relationships": [
                {
                    "name": "Satya Nadella",
                    "type": "Person",
                    "relationshipType": "CEO",
                    "strength": "High",
                    "description": "CEO since 2014, led transformation to cloud-first, mobile-first strategy",
                    "reference": "Microsoft Leadership Profile",
                    "sourceUrl": "https://microsoft.com/leadership",
                    "year": "2014-present"
                },
                {
                    "name": "Azure",
                    "type": "Cloud Platform",
                    "relationshipType": "Core Service",
                    "strength": "High",
                    "description": "Microsoft's cloud computing platform, second largest globally after AWS",
                    "reference": "Microsoft Azure Market Share Report 2023",
                    "sourceUrl": "https://azure.microsoft.com",
                    "year": "2010-present"
                },
                {
                    "name": "OpenAI",
                    "type": "AI Company",
                    "relationshipType": "Strategic Partner",
                    "strength": "High",
                    "description": "Multi-billion dollar investment and exclusive cloud provider for ChatGPT",
                    "reference": "Microsoft-OpenAI Partnership Agreement",
                    "sourceUrl": "https://openai.com/microsoft",
                    "year": "2019-present"
                },
                {
                    "name": "GitHub",
                    "type": "Platform",
                    "relationshipType": "Subsidiary",
                    "strength": "High",
                    "description": "Acquired for $7.5 billion, leading platform for software development",
                    "reference": "Microsoft GitHub Acquisition SEC Filing",
                    "sourceUrl": "https://github.com",
                    "year": "2018-present"
                },
                {
                    "name": "Office 365",
                    "type": "Software Suite",
                    "relationshipType": "Core Product",
                    "strength": "High",
                    "description": "Subscription-based productivity software suite, major revenue driver",
                    "reference": "Microsoft 365 Subscriber Growth Report",
                    "sourceUrl": "https://microsoft.com/microsoft-365",
                    "year": "2011-present"
                },
                {
                    "name": "Xbox",
                    "type": "Gaming Console",
                    "relationshipType": "Gaming Division",
                    "strength": "Medium",
                    "description": "Gaming console brand competing with Sony PlayStation and Nintendo",
                    "reference": "Xbox Gaming Revenue Report 2023",
                    "sourceUrl": "https://xbox.com",
                    "year": "2001-present"
                }
            ]
        },
        "Google": {
            "type": "Technology Company",
            "description": "Multinational technology conglomerate specializing in Internet services and AI",
            "founded": "1998",
            "headquarters": "Mountain View, California",
            "relationships": [
                {
                    "name": "Sundar Pichai",
                    "type": "Person",
                    "relationshipType": "CEO",
                    "strength": "High",
                    "description": "CEO of Google and Alphabet, leading AI-first transformation",
                    "reference": "Alphabet Inc. Leadership Team",
                    "sourceUrl": "https://abc.xyz/leadership",
                    "year": "2015-present"
                },
                {
                    "name": "Search Engine",
                    "type": "Product",
                    "relationshipType": "Core Product",
                    "strength": "High",
                    "description": "Dominant search engine with over 90% global market share",
                    "reference": "Google Search Market Share Analysis 2023",
                    "sourceUrl": "https://google.com",
                    "year": "1998-present"
                },
                {
                    "name": "Android",
                    "type": "Operating System",
                    "relationshipType": "Mobile Platform",
                    "strength": "High",
                    "description": "Open-source mobile OS with largest global market share",
                    "reference": "Android Global Market Share Report",
                    "sourceUrl": "https://android.com",
                    "year": "2008-present"
                },
                {
                    "name": "YouTube",
                    "type": "Video Platform",
                    "relationshipType": "Subsidiary",
                    "strength": "High",
                    "description": "Acquired for $1.65 billion, now dominant video sharing platform",
                    "reference": "YouTube Revenue and Usage Statistics",
                    "sourceUrl": "https://youtube.com",
                    "year": "2006-present"
                },
                {
                    "name": "DeepMind",
                    "type": "AI Research Lab",
                    "relationshipType": "Subsidiary",
                    "strength": "High",
                    "description": "AI research company acquired for $500+ million, breakthrough in AGI research",
                    "reference": "DeepMind Research Publications",
                    "sourceUrl": "https://deepmind.com",
                    "year": "2014-present"
                },
                {
                    "name": "Waymo",
                    "type": "Autonomous Vehicle Company",
                    "relationshipType": "Subsidiary",
                    "strength": "Medium",
                    "description": "Self-driving car project spun out as separate Alphabet company",
                    "reference": "Waymo Autonomous Vehicle Testing Report",
                    "sourceUrl": "https://waymo.com",
                    "year": "2016-present"
                }
            ]
        },
        "OpenAI": {
            "type": "AI Research Company",
            "description": "AI research and deployment company focused on safe artificial general intelligence",
            "founded": "2015",
            "headquarters": "San Francisco, California",
            "relationships": [
                {
                    "name": "Sam Altman",
                    "type": "Person",
                    "relationshipType": "CEO",
                    "strength": "High",
                    "description": "CEO leading OpenAI's transition from non-profit to commercial success",
                    "reference": "OpenAI Leadership Team",
                    "sourceUrl": "https://openai.com/leadership",
                    "year": "2019-present"
                },
                {
                    "name": "ChatGPT",
                    "type": "AI Product",
                    "relationshipType": "Flagship Product",
                    "strength": "High",
                    "description": "Conversational AI that reached 100M users faster than any consumer app",
                    "reference": "ChatGPT Growth Statistics Report",
                    "sourceUrl": "https://openai.com/chatgpt",
                    "year": "2022-present"
                },
                {
                    "name": "Microsoft",
                    "type": "Technology Company",
                    "relationshipType": "Strategic Investor",
                    "strength": "High",
                    "description": "Multi-billion dollar investment and exclusive cloud computing provider",
                    "reference": "Microsoft-OpenAI Strategic Partnership",
                    "sourceUrl": "https://openai.com/microsoft",
                    "year": "2019-present"
                },
                {
                    "name": "GPT-4",
                    "type": "AI Model",
                    "relationshipType": "Core Technology",
                    "strength": "High",
                    "description": "Large multimodal model demonstrating human-level performance on many tasks",
                    "reference": "GPT-4 Technical Report",
                    "sourceUrl": "https://openai.com/research/gpt-4",
                    "year": "2023-present"
                },
                {
                    "name": "DALL-E",
                    "type": "AI Product",
                    "relationshipType": "Image Generation",
                    "strength": "Medium",
                    "description": "AI system for generating images from natural language descriptions",
                    "reference": "DALL-E 3 Research Paper",
                    "sourceUrl": "https://openai.com/dall-e-3",
                    "year": "2021-present"
                }
            ]
        },
        "Meta": {
            "type": "Technology Company",
            "description": "Social media conglomerate focused on connecting people and building the metaverse",
            "founded": "2004",
            "headquarters": "Menlo Park, California",
            "relationships": [
                {
                    "name": "Mark Zuckerberg",
                    "type": "Person",
                    "relationshipType": "CEO/Founder",
                    "strength": "High",
                    "description": "Founder and CEO, controlling majority voting shares in the company",
                    "reference": "Meta Platforms Inc. Proxy Statement",
                    "sourceUrl": "https://investor.fb.com",
                    "year": "2004-present"
                },
                {
                    "name": "Facebook",
                    "type": "Social Platform",
                    "relationshipType": "Core Product",
                    "strength": "High",
                    "description": "Primary social networking platform with 3+ billion monthly active users",
                    "reference": "Meta Q4 2023 Earnings Report",
                    "sourceUrl": "https://facebook.com",
                    "year": "2004-present"
                },
                {
                    "name": "Instagram",
                    "type": "Social Platform",
                    "relationshipType": "Subsidiary",
                    "strength": "High",
                    "description": "Photo and video sharing platform acquired for $1 billion",
                    "reference": "Instagram Acquisition Analysis",
                    "sourceUrl": "https://instagram.com",
                    "year": "2012-present"
                },
                {
                    "name": "WhatsApp",
                    "type": "Messaging Platform",
                    "relationshipType": "Subsidiary",
                    "strength": "High",
                    "description": "Messaging service acquired for $19 billion, 2+ billion users globally",
                    "reference": "WhatsApp User Statistics 2023",
                    "sourceUrl": "https://whatsapp.com",
                    "year": "2014-present"
                },
                {
                    "name": "Reality Labs",
                    "type": "VR/AR Division",
                    "relationshipType": "Metaverse Initiative",
                    "strength": "Medium",
                    "description": "VR/AR division developing metaverse technologies, significant R&D investment",
                    "reference": "Meta Reality Labs Financial Report",
                    "sourceUrl": "https://meta.com/quest",
                    "year": "2014-present"
                }
            ]
        }
    }

def create_network_graph(entity_name, entity_data):
    """Create an interactive network graph using Plotly"""
    
    # Create NetworkX graph
    G = nx.Graph()
    
    # Add center node
    G.add_node(entity_name, 
               type=entity_data['type'], 
               is_center=True,
               description=entity_data['description'])
    
    # Add relationship nodes and edges
    for rel in entity_data['relationships']:
        G.add_node(rel['name'], 
                   type=rel['type'], 
                   is_center=False,
                   description=rel['description'],
                   relationship_type=rel['relationshipType'])
        
        G.add_edge(entity_name, rel['name'], 
                   strength=rel['strength'],
                   relationship_type=rel['relationshipType'],
                   description=rel['description'])
    
    # Generate layout
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Color mapping
    color_map = {
        'Technology Company': '#ffd700',
        'Person': '#ffed4e', 
        'Product': '#daa520',
        'Platform': '#b8860b',
        'AI Company': '#f0e68c',
        'Cloud Platform': '#eee8aa',
        'Operating System': '#fafad2',
        'AI Product': '#fff8dc',
        'AI Model': '#fffacd',
        'Social Platform': '#ffffe0',
        'Messaging Platform': '#e6e600',
        'VR/AR Division': '#cccc00',
        'Manufacturing Company': '#b3b300',
        'Infrastructure': '#999900',
        'Automotive/Energy Company': '#808000',
        'Aerospace Company': '#666600',
        'Gaming Console': '#4d4d00',
        'Software Suite': '#ffd700',
        'AI Research Lab': '#ffed4e',
        'Video Platform': '#daa520',
        'Autonomous Vehicle Company': '#b8860b'
    }
    
    # Strength color mapping
    strength_colors = {'High': '#ffd700', 'Medium': '#ffed4e', 'Low': '#b8860b'}
    
    # Prepare node traces
    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode='markers+text',
        text=[node if len(node) <= 10 else node[:10] + '...' for node in G.nodes()],
        textposition='middle center',
        textfont=dict(color='#ffd700', size=10, family='Inter'),
        marker=dict(
            size=[35 if G.nodes[node].get('is_center', False) else 25 for node in G.nodes()],
            color=[color_map.get(G.nodes[node]['type'], '#ffd700') for node in G.nodes()],
            line=dict(width=2, color='#000'),
            opacity=0.9
        ),
        hovertemplate='<b>%{text}</b><br>' +
                     'Type: %{customdata[0]}<br>' +
                     'Description: %{customdata[1]}<extra></extra>',
        customdata=[[G.nodes[node]['type'], G.nodes[node].get('description', 'No description')] 
                   for node in G.nodes()],
        name='Entities'
    )
    
    # Prepare edge traces
    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        strength = G.edges[edge]['strength']
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(
                width=3 if strength == 'High' else 2 if strength == 'Medium' else 1,
                color=strength_colors.get(strength, '#ffd700')
            ),
            opacity=0.7,
            hovertemplate=f'<b>{G.edges[edge]["relationship_type"]}</b><br>' +
                         f'Strength: {strength}<br>' +
                         f'{G.edges[edge]["description"]}<extra></extra>',
            name=f'{edge[0]} - {edge[1]}'
        )
        edge_traces.append(edge_trace)
    
    # Create figure
    fig = go.Figure(data=[node_trace] + edge_traces)
    
    fig.update_layout(
        title=dict(
            text=f"🌐 {entity_name} Relationship Network",
            font=dict(color='#ffd700', size=20, family='Inter'),
            x=0.5
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[
            dict(
                text="Drag nodes to explore • Hover for details",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='#cccccc', size=12, family='Inter')
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    
    return fig

def display_entity_list(entity_data):
    """Display the entity list with styling"""
    entities_html = ""
    
    for i, rel in enumerate(entity_data['relationships']):
        strength_class = f"strength-{rel['strength'].lower()}"
        
        entities_html += f"""
        <div class="entity-item">
            <div class="entity-name">{rel['name']}</div>
            <div class="entity-type">{rel['type']}</div>
            <div class="relationship-info">
                <span class="relationship-type">{rel['relationshipType']}</span>
                <span class="{strength_class}">{rel['strength']}</span>
            </div>
            <div class="entity-description">{rel['description']}</div>
            <a href="{rel.get('sourceUrl', '#')}" class="reference-link" target="_blank">📄 {rel['reference']}</a>
        </div>
        """
    
    return entities_html

def display_references(entity_name, entity_data):
    """Display detailed references"""
    references_html = f"""
    <div class="detail-item">
        <div class="detail-title">{entity_name} - Company Overview</div>
        <div class="detail-description">{entity_data['description']}</div>
        <div class="detail-meta">
            <span class="detail-source">Founded: {entity_data['founded']} | HQ: {entity_data['headquarters']}</span>
            <span class="detail-date">Updated: 2024</span>
        </div>
    </div>
    """
    
    for rel in entity_data['relationships']:
        references_html += f"""
        <div class="detail-item">
            <div class="detail-title">{rel['relationshipType']}: {rel['name']}</div>
            <div class="detail-description">{rel['description']}</div>
            <div class="detail-meta">
                <a href="{rel.get('sourceUrl', '#')}" class="detail-source" target="_blank">{rel['reference']}</a>
                <span class="detail-date">{rel['year']}</span>
            </div>
        </div>
        """
    
    return references_html

# Main app
def main():
    # Load data
    entity_data = load_entity_data()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="logo-container">
            <div class="logo">
                Entity Relationships
                <span class="version-badge">v2.0</span>
            </div>
            <ul class="nav-links">
                <li><a href="#" class="active">Advanced Analysis</a></li>
                <li><a href="#">Network Insights</a></li>
                <li><a href="#">References</a></li>
                <li><a href="#">Data Sources</a></li>
            </ul>
        </div>
        <h1 class="main-title">Advanced Entity Relationships</h1>
        <p class="main-subtitle">Discover complex connections with detailed references and citations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search section
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        selected_entity = st.selectbox(
            "Search entities:",
            options=[''] + list(entity_data.keys()),
            format_func=lambda x: "Select an entity..." if x == '' else x,
            key="entity_selector"
        )
    
    with col2:
        analyze_btn = st.button("🔍 Analyze", key="analyze_btn")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results
    if selected_entity and selected_entity != '':
        data = entity_data[selected_entity]
        
        # Metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nodes", f"{len(data['relationships']) + 1}")
        with col2:
            st.metric("Connections", f"{len(data['relationships'])}")
        with col3:
            st.metric("References", f"{len(data['relationships'])}")
        
        # Main content layout
        col1, col2, col3 = st.columns([2.5, 1, 1])
        
        with col1:
            st.markdown("""
            <div class="content-card">
                <div class="card-header">
                    <h3 class="card-title">🌐 Relationship Network</h3>
                    <span class="card-count">{} nodes</span>
                </div>
            </div>
            """.format(len(data['relationships']) + 1), unsafe_allow_html=True)
            
            # Create and display network graph
            fig = create_network_graph(selected_entity, data)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            st.markdown("""
            <div class="content-card">
                <div class="card-header">
                    <h3 class="card-title">📊 Connected Entities</h3>
                    <span class="card-count">{} connections</span>
                </div>
            </div>
            """.format(len(data['relationships'])), unsafe_allow_html=True)
            
            # Display entity list
            entities_html = display_entity_list(data)
            st.markdown(f'<div style="max-height: 500px; overflow-y: auto;">{entities_html}</div>', 
                       unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="content-card">
                <div class="card-header">
                    <h3 class="card-title">📚 References & Sources</h3>
                    <span class="card-count">{} references</span>
                </div>
            </div>
            """.format(len(data['relationships'])), unsafe_allow_html=True)
            
            # Display references
            references_html = display_references(selected_entity, data)
            st.markdown(f'<div style="max-height: 500px; overflow-y: auto;">{references_html}</div>', 
                       unsafe_allow_html=True)
    
    else:
        # Empty state
        st.markdown("""
        <div style="text-align: center; padding: 4rem 0; color: #888;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🎯</div>
            <h3>Select an entity above to explore relationships</h3>
            <p>Available entities: Apple, Tesla, Microsoft, Google, OpenAI, Meta</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()