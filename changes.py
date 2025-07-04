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

# Simple CSS for black and golden theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: #ffd700;
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #ffd700, #ffed4e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #cccccc;
        margin-bottom: 2rem;
    }
    
    .stSelectbox label {
        color: #ffd700 !important;
        font-weight: 600 !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #ffd700, #ffed4e) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        padding: 0.5rem 2rem !important;
    }
    
    .stMetric {
        background: rgba(255, 215, 0, 0.1);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    .stMetric label {
        color: #ffd700 !important;
        font-weight: 600 !important;
    }
    
    .entity-card {
        background: rgba(255, 215, 0, 0.1);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #ffd700;
    }
    
    .reference-card {
        background: rgba(255, 215, 0, 0.08);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #ffed4e;
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
                },
                {
                    "name": "Steve Jobs",
                    "type": "Person",
                    "relationshipType": "Co-Founder",
                    "strength": "High",
                    "description": "Co-founder and former CEO who transformed Apple into a consumer technology leader",
                    "reference": "Steve Jobs Biography - Walter Isaacson",
                    "sourceUrl": "https://apple.com/leadership",
                    "year": "1976-2011"
                },
                {
                    "name": "iOS",
                    "type": "Operating System",
                    "relationshipType": "Core Technology",
                    "strength": "High",
                    "description": "Mobile operating system powering iPhone, iPad, and other Apple devices",
                    "reference": "iOS Development Documentation",
                    "sourceUrl": "https://developer.apple.com",
                    "year": "2007-present"
                },
                {
                    "name": "M1 Chip",
                    "type": "Hardware",
                    "relationshipType": "Core Technology",
                    "strength": "High",
                    "description": "Apple's custom silicon chip revolutionizing Mac performance and efficiency",
                    "reference": "Apple M1 Chip Technical Specifications",
                    "sourceUrl": "https://apple.com/mac",
                    "year": "2020-present"
                },
                {
                    "name": "Qualcomm",
                    "type": "Technology Company",
                    "relationshipType": "Legal Disputes/Partner",
                    "strength": "Medium",
                    "description": "Patent disputes and licensing agreements for cellular technology",
                    "reference": "Apple-Qualcomm Settlement Agreement 2019",
                    "sourceUrl": "https://qualcomm.com",
                    "year": "2017-present"
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
                },
                {
                    "name": "Gigafactory",
                    "type": "Manufacturing Facility",
                    "relationshipType": "Production Infrastructure",
                    "strength": "High",
                    "description": "Global network of integrated manufacturing facilities for batteries and vehicles",
                    "reference": "Tesla Gigafactory Production Report",
                    "sourceUrl": "https://tesla.com/gigafactory",
                    "year": "2016-present"
                },
                {
                    "name": "CATL",
                    "type": "Technology Company",
                    "relationshipType": "Battery Supplier",
                    "strength": "Medium",
                    "description": "Chinese battery manufacturer providing LFP batteries for Tesla vehicles",
                    "reference": "CATL Tesla Supply Agreement 2020",
                    "sourceUrl": "https://catl.com",
                    "year": "2020-present"
                },
                {
                    "name": "Tesla Energy",
                    "type": "Business Division",
                    "relationshipType": "Energy Storage",
                    "strength": "High",
                    "description": "Solar panels, solar roof tiles, and energy storage solutions for homes and utilities",
                    "reference": "Tesla Energy Business Report 2023",
                    "sourceUrl": "https://tesla.com/energy",
                    "year": "2015-present"
                },
                {
                    "name": "Neuralink",
                    "type": "Neurotechnology Company",
                    "relationshipType": "Sister Company",
                    "strength": "Low",
                    "description": "Brain-computer interface company also founded by Elon Musk",
                    "reference": "Neuralink Progress Update 2023",
                    "sourceUrl": "https://neuralink.com",
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
                },
                {
                    "name": "Windows",
                    "type": "Operating System",
                    "relationshipType": "Core Product",
                    "strength": "High",
                    "description": "Dominant desktop operating system with billions of users worldwide",
                    "reference": "Windows Market Share Analysis 2023",
                    "sourceUrl": "https://microsoft.com/windows",
                    "year": "1985-present"
                },
                {
                    "name": "LinkedIn",
                    "type": "Social Platform",
                    "relationshipType": "Subsidiary",
                    "strength": "Medium",
                    "description": "Professional networking platform acquired for $26.2 billion",
                    "reference": "Microsoft LinkedIn Integration Strategy",
                    "sourceUrl": "https://linkedin.com",
                    "year": "2016-present"
                },
                {
                    "name": "Teams",
                    "type": "Software Suite",
                    "relationshipType": "Communication Platform",
                    "strength": "High",
                    "description": "Collaboration platform competing with Slack and Zoom",
                    "reference": "Microsoft Teams Usage Statistics 2023",
                    "sourceUrl": "https://microsoft.com/teams",
                    "year": "2017-present"
                },
                {
                    "name": "Activision Blizzard",
                    "type": "Gaming Company",
                    "relationshipType": "Acquisition",
                    "strength": "High",
                    "description": "Gaming giant acquired for $68.7 billion, largest Microsoft acquisition",
                    "reference": "Microsoft Activision Blizzard Acquisition 2023",
                    "sourceUrl": "https://activisionblizzard.com",
                    "year": "2023-present"
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
                },
                {
                    "name": "Google Cloud",
                    "type": "Cloud Platform",
                    "relationshipType": "Core Service",
                    "strength": "Medium",
                    "description": "Third-largest cloud provider globally, growing rapidly in enterprise",
                    "reference": "Google Cloud Platform Market Analysis",
                    "sourceUrl": "https://cloud.google.com",
                    "year": "2008-present"
                },
                {
                    "name": "Pixel",
                    "type": "Product",
                    "relationshipType": "Hardware Division",
                    "strength": "Medium",
                    "description": "Google's flagship smartphone line showcasing Android capabilities",
                    "reference": "Google Pixel Sales Analysis 2023",
                    "sourceUrl": "https://store.google.com/pixel",
                    "year": "2016-present"
                },
                {
                    "name": "Chrome",
                    "type": "Software Suite",
                    "relationshipType": "Core Product",
                    "strength": "High",
                    "description": "Dominant web browser with over 60% global market share",
                    "reference": "Browser Market Share Statistics 2023",
                    "sourceUrl": "https://google.com/chrome",
                    "year": "2008-present"
                },
                {
                    "name": "Larry Page",
                    "type": "Person",
                    "relationshipType": "Co-Founder",
                    "strength": "High",
                    "description": "Co-founder of Google and former CEO, current Alphabet board member",
                    "reference": "Google Founders History",
                    "sourceUrl": "https://abc.xyz/leadership",
                    "year": "1998-present"
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
    """Create an enhanced interactive network graph using Plotly"""
    
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
    
    # Generate better layout with more spacing
    pos = nx.spring_layout(G, k=4, iterations=100, seed=42)
    
    # Enhanced color mapping with better contrast
    color_map = {
        'Technology Company': '#FFD700',     # Bright Gold
        'Person': '#FF6B35',                 # Orange-Red  
        'Product': '#4ECDC4',                # Teal
        'Platform': '#45B7D1',               # Sky Blue
        'AI Company': '#96CEB4',             # Mint Green
        'Cloud Platform': '#FECA57',         # Yellow
        'Operating System': '#FF9FF3',       # Pink
        'AI Product': '#54A0FF',             # Blue
        'AI Model': '#5F27CD',               # Purple
        'Social Platform': '#00D2D3',        # Cyan
        'Messaging Platform': '#FF9F43',     # Orange
        'VR/AR Division': '#A55EEA',         # Violet
        'Manufacturing Company': '#26DE81',  # Green
        'Infrastructure': '#FD79A8',         # Light Pink
        'Automotive/Energy Company': '#FDCB6E', # Light Orange
        'Aerospace Company': '#6C5CE7',      # Purple Blue
        'Gaming Console': '#A29BFE',         # Light Purple
        'Software Suite': '#FD79A8',         # Pink
        'AI Research Lab': '#00B894',        # Dark Teal
        'Video Platform': '#E17055',         # Coral
        'Autonomous Vehicle Company': '#81ECEC', # Light Cyan
        'Hardware': '#FF7675',               # Light Red
        'Business Division': '#74B9FF',      # Light Blue
        'Neurotechnology Company': '#00CEC9', # Dark Cyan
        'Manufacturing Facility': '#55A3FF'  # Medium Blue
    }
    
    # Strength color mapping with thicker lines
    strength_colors = {
        'High': '#FFD700',    # Gold
        'Medium': '#FF8C00',  # Dark Orange  
        'Low': '#666666'      # Gray
    }
    
    strength_widths = {
        'High': 6,
        'Medium': 4,
        'Low': 2
    }
    
    # Create enhanced edge traces
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
                width=strength_widths.get(strength, 3),
                color=strength_colors.get(strength, '#FFD700')
            ),
            opacity=0.8,
            hovertemplate=f'<b>{G.edges[edge]["relationship_type"]}</b><br>' +
                         f'Strength: {strength}<br>' +
                         f'{G.edges[edge]["description"]}<extra></extra>',
            name=f'{edge[0]} ↔ {edge[1]}',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Enhanced node trace with larger, more readable nodes
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    node_info = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Larger, more readable text
        display_text = node if len(node) <= 12 else node[:12] + '...'
        node_text.append(display_text)
        
        # Enhanced colors and sizes
        node_type = G.nodes[node]['type']
        node_colors.append(color_map.get(node_type, '#FFD700'))
        
        # Larger nodes for better visibility
        if G.nodes[node].get('is_center', False):
            node_sizes.append(60)  # Much larger center node
        else:
            node_sizes.append(40)  # Larger peripheral nodes
        
        # Enhanced hover info
        node_info.append([
            G.nodes[node]['type'], 
            G.nodes[node].get('description', 'No description available')
        ])
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='middle center',
        textfont=dict(
            color='white',  # White text for better contrast
            size=14,        # Larger font size
            family='Arial Black'  # Bold font for readability
        ),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=3, color='white'),  # White border for contrast
            opacity=0.9
        ),
        hovertemplate='<b>%{text}</b><br>' +
                     'Type: %{customdata[0]}<br>' +
                     'Description: %{customdata[1]}<extra></extra>',
        customdata=node_info,
        name='Network Nodes',
        showlegend=False
    )
    
    # Create enhanced figure
    fig = go.Figure(data=[node_trace] + edge_traces)
    
    fig.update_layout(
        title=dict(
            text=f"🌐 {entity_name} Relationship Network",
            font=dict(color='#FFD700', size=24, family='Arial Black'),
            x=0.5,
            y=0.95
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=40, l=20, r=20, t=60),
        annotations=[
            dict(
                text="💡 Drag nodes to explore • Hover for detailed information • Larger nodes = stronger connections",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.02,
                xanchor='center', yanchor='bottom',
                font=dict(color='#CCCCCC', size=12, family='Arial')
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(20,20,20,0.8)',  # Darker background for contrast
        paper_bgcolor='rgba(0,0,0,0)',
        height=600  # Taller graph for better visibility
    )
    
    # Add subtle background grid for better visual structure
    fig.add_shape(
        type="rect",
        x0=-1.2, y0=-1.2, x1=1.2, y1=1.2,
        line=dict(color="rgba(255,215,0,0.1)", width=1),
        fillcolor="rgba(255,215,0,0.02)"
    )
    
    return fig

# Main app
def main():
    # Load data
    entity_data = load_entity_data()
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 class="main-title">Entity Relationships v2.0</h1>
        <p class="subtitle">Discover complex connections with detailed references and citations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search section
    col1, col2 = st.columns([4, 1])
    
    with col1:
        selected_entity = st.selectbox(
            "Search entities:",
            options=[''] + list(entity_data.keys()),
            format_func=lambda x: "Select an entity..." if x == '' else x,
            key="entity_selector"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze", key="analyze_btn")
    
    if selected_entity and selected_entity != '':
        data = entity_data[selected_entity]
        
        # Metrics row
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nodes", f"{len(data['relationships']) + 1}")
        with col2:
            st.metric("Connections", f"{len(data['relationships'])}")
        with col3:
            st.metric("References", f"{len(data['relationships'])}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Network Graph
        st.markdown("### 🌐 Relationship Network")
        fig = create_network_graph(selected_entity, data)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Two columns for entities and references
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Connected Entities")
            
            for rel in data['relationships']:
                with st.container():
                    st.markdown(f"""
                    <div class="entity-card">
                        <h4 style="color: #ffd700; margin-bottom: 0.5rem;">{rel['name']}</h4>
                        <p style="color: #ccc; font-size: 0.9rem; margin-bottom: 0.5rem;"><strong>Type:</strong> {rel['type']}</p>
                        <p style="color: #ccc; font-size: 0.9rem; margin-bottom: 0.5rem;"><strong>Relationship:</strong> {rel['relationshipType']}</p>
                        <p style="color: #ccc; font-size: 0.9rem; margin-bottom: 0.5rem;"><strong>Strength:</strong> 
                            <span style="background: #ffd700; color: #000; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">{rel['strength']}</span>
                        </p>
                        <p style="color: #ccc; font-size: 0.85rem; margin-bottom: 0.5rem;">{rel['description']}</p>
                        <p style="color: #ffed4e; font-size: 0.8rem;">📄 {rel['reference']} ({rel['year']})</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📚 References & Sources")
            
            # Company overview
            st.markdown(f"""
            <div class="reference-card">
                <h4 style="color: #ffd700; margin-bottom: 0.5rem;">{selected_entity} - Company Overview</h4>
                <p style="color: #ccc; font-size: 0.9rem; margin-bottom: 0.5rem;">{data['description']}</p>
                <p style="color: #ffed4e; font-size: 0.8rem;">Founded: {data['founded']} | HQ: {data['headquarters']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # References
            for rel in data['relationships']:
                st.markdown(f"""
                <div class="reference-card">
                    <h5 style="color: #ffd700; margin-bottom: 0.5rem;">{rel['relationshipType']}: {rel['name']}</h5>
                    <p style="color: #ccc; font-size: 0.85rem; margin-bottom: 0.5rem;">{rel['description']}</p>
                    <p style="color: #ffed4e; font-size: 0.8rem;">📄 {rel['reference']} ({rel['year']})</p>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Empty state
        st.markdown("""
        <div style="text-align: center; padding: 4rem 0; color: #888;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🎯</div>
            <h3 style="color: #ffd700;">Select an entity above to explore relationships</h3>
            <p style="color: #ccc;">Available entities: Apple, Tesla, Microsoft, Google, OpenAI, Meta</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()