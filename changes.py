import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
from datetime import datetime
import numpy as np

# ========================================================================================
# PAGE CONFIGURATION
# ========================================================================================

st.set_page_config(
    page_title="Entity Relationships v2.0",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================================================================================
# STYLING AND CSS
# ========================================================================================

def apply_custom_css():
    """Apply custom CSS styling for the application"""
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
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(45deg, #ffd700, #ffed4e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            text-align: center;
            font-size: 1rem;
            color: #cccccc;
            margin-bottom: 1.5rem;
        }
        
        .stSelectbox label {
            color: #ffd700 !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
        }
        
        .stSelectbox > div > div {
            background-color: rgba(255, 215, 0, 0.1) !important;
            border: 2px solid rgba(255, 215, 0, 0.3) !important;
            border-radius: 12px !important;
            font-size: 1.1rem !important;
            padding: 0.6rem !important;
            min-height: 50px !important;
        }
        
        .stSelectbox > div > div > div {
            color: #ffd700 !important;
            font-weight: 500 !important;
            font-size: 1.1rem !important;
        }
        
        .stButton button {
            background: linear-gradient(135deg, #ffd700, #ffed4e) !important;
            color: #000 !important;
            border: none !important;
            border-radius: 25px !important;
            font-weight: 700 !important;
            padding: 0.75rem 2.5rem !important;
            font-size: 1.1rem !important;
            min-height: 50px !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3) !important;
        }
        
        .stMetric {
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 8px;
            padding: 0.75rem;
            text-align: center;
        }
        
        .stMetric label {
            color: #ffd700 !important;
            font-weight: 600 !important;
        }
        
        .entity-card {
            background: rgba(255, 215, 0, 0.08);
            border: 1px solid rgba(255, 215, 0, 0.25);
            border-radius: 8px;
            padding: 0.75rem;
            margin-bottom: 0.75rem;
            border-left: 3px solid #ffd700;
        }
        
        .entity-card h4 {
            color: #ffd700;
            margin-bottom: 0.3rem;
            font-size: 1.1rem;
        }
        
        .entity-card p {
            color: #ccc;
            font-size: 0.85rem;
            margin-bottom: 0.3rem;
            line-height: 1.3;
        }
        
        .reference-card {
            background: rgba(255, 215, 0, 0.06);
            border: 1px solid rgba(255, 215, 0, 0.25);
            border-radius: 8px;
            padding: 0.75rem;
            margin-bottom: 0.75rem;
            border-left: 3px solid #ffed4e;
        }
        
        .reference-card h4, .reference-card h5 {
            color: #ffd700;
            margin-bottom: 0.3rem;
            font-size: 1rem;
        }
        
        .reference-card p {
            color: #ccc;
            font-size: 0.8rem;
            margin-bottom: 0.3rem;
            line-height: 1.3;
        }
        
        .strength-badge {
            background: #ffd700;
            color: #000;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .section-header {
            color: #ffd700;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
            border-bottom: 2px solid rgba(255, 215, 0, 0.3);
            padding-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

# ========================================================================================
# DATA MANAGEMENT
# ========================================================================================

@st.cache_data
def load_entity_data():
    """Load and return entity relationship data"""
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

# ========================================================================================
# VISUALIZATION FUNCTIONS
# ========================================================================================

def get_color_mapping():
    """Return color mapping for different entity types"""
    return {
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

def get_strength_properties():
    """Return strength-based styling properties"""
    return {
        'colors': {'High': '#FFD700', 'Medium': '#FF8C00', 'Low': '#666666'},
        'widths': {'High': 6, 'Medium': 4, 'Low': 2}
    }

def create_network_graph(entity_name, entity_data):
    """Create an enhanced 3D dynamic interactive network graph using Plotly"""
    
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
    
    # Generate 3D layout with better distribution
    pos_2d = nx.spring_layout(G, k=3, iterations=150, seed=42)
    
    # Convert to 3D with intelligent z-positioning
    pos_3d = {}
    center_node = entity_name
    
    for node in G.nodes():
        x, y = pos_2d[node]
        
        if node == center_node:
            # Center node at origin with slight elevation
            z = 0.2
        else:
            # Distribute other nodes in 3D space based on relationship strength
            edges = list(G.edges(node, data=True))
            if edges:
                strength = edges[0][2]['strength']
                if strength == 'High':
                    z = np.random.uniform(0.8, 1.2)
                elif strength == 'Medium':
                    z = np.random.uniform(-0.3, 0.3)
                else:
                    z = np.random.uniform(-0.8, -0.4)
            else:
                z = 0
                
        pos_3d[node] = (x * 2, y * 2, z)  # Scale up for better spacing
    
    # Get styling properties
    color_map = get_color_mapping()
    strength_props = get_strength_properties()
    
    # Create enhanced 3D edge traces with gradient effects
    edge_traces = []
    for edge in G.edges(data=True):
        node1, node2, data = edge
        x0, y0, z0 = pos_3d[node1]
        x1, y1, z1 = pos_3d[node2]
        strength = data['strength']
        
        # Create curved lines for more dynamic appearance
        num_points = 20
        t = np.linspace(0, 1, num_points)
        
        # Add slight curve to the connections
        mid_x = (x0 + x1) / 2 + np.random.uniform(-0.3, 0.3)
        mid_y = (y0 + y1) / 2 + np.random.uniform(-0.3, 0.3)
        mid_z = (z0 + z1) / 2 + np.random.uniform(-0.2, 0.5)
        
        # Bezier curve calculation
        x_curve = (1-t)**2 * x0 + 2*(1-t)*t * mid_x + t**2 * x1
        y_curve = (1-t)**2 * y0 + 2*(1-t)*t * mid_y + t**2 * z1
        z_curve = (1-t)**2 * z0 + 2*(1-t)*t * mid_z + t**2 * z1
        
        edge_trace = go.Scatter3d(
            x=x_curve,
            y=y_curve,
            z=z_curve,
            mode='lines',
            line=dict(
                width=strength_props['widths'].get(strength, 4) + 2,
                color=strength_props['colors'].get(strength, '#FFD700')
            ),
            opacity=0.7,
            hovertemplate=f'<b>{data["relationship_type"]}</b><br>' +
                         f'Strength: {strength}<br>' +
                         f'{data["description"]}<extra></extra>',
            name=f'{node1} ↔ {node2}',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Create enhanced 3D node trace with dynamic effects
    node_x, node_y, node_z = [], [], []
    node_text, node_colors, node_sizes, node_info = [], [], [], []
    
    for node in G.nodes():
        x, y, z = pos_3d[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        
        # Enhanced text with better formatting
        display_text = node if len(node) <= 10 else node[:10] + '...'
        node_text.append(display_text)
        
        node_type = G.nodes[node]['type']
        base_color = color_map.get(node_type, '#FFD700')
        
        # Add glow effect for center node
        if G.nodes[node].get('is_center', False):
            node_colors.append('#FFD700')
            node_sizes.append(25)
        else:
            node_colors.append(base_color)
            node_sizes.append(15)
        
        # Enhanced hover info
        node_info.append([
            G.nodes[node]['type'], 
            G.nodes[node].get('description', 'No description available')
        ])
    
    # Create main node trace
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        text=node_text,
        textposition='middle center',
        textfont=dict(
            color='white', 
            size=10, 
            family='Arial Black'
        ),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='rgba(255,255,255,0.8)'),
            opacity=0.9,
            symbol='circle'
        ),
        hovertemplate='<b>%{text}</b><br>Type: %{customdata[0]}<br>Description: %{customdata[1]}<extra></extra>',
        customdata=node_info,
        name='Network Nodes',
        showlegend=False
    )
    
    # Add center node with special glow effect
    center_x, center_y, center_z = pos_3d[entity_name]
    center_glow = go.Scatter3d(
        x=[center_x], y=[center_y], z=[center_z],
        mode='markers',
        marker=dict(
            size=35,
            color='#FFD700',
            line=dict(width=4, color='rgba(255,215,0,0.6)'),
            opacity=0.3,
            symbol='circle'
        ),
        hoverinfo='skip',
        showlegend=False,
        name='Center Glow'
    )
    
    # Create animated particle effects around center node
    particle_traces = []
    for i in range(8):
        angle = i * np.pi / 4
        radius = 0.5
        particle_x = center_x + radius * np.cos(angle)
        particle_y = center_y + radius * np.sin(angle)
        particle_z = center_z + np.random.uniform(-0.2, 0.2)
        
        particle_trace = go.Scatter3d(
            x=[particle_x], y=[particle_y], z=[particle_z],
            mode='markers',
            marker=dict(
                size=3,
                color='rgba(255,215,0,0.6)',
                opacity=0.6
            ),
            hoverinfo='skip',
            showlegend=False,
            name=f'Particle_{i}'
        )
        particle_traces.append(particle_trace)
    
    # Combine all traces
    all_traces = [center_glow, node_trace] + edge_traces + particle_traces
    
    # Create enhanced figure with 3D scene
    fig = go.Figure(data=all_traces)
    
    fig.update_layout(
        title=dict(
            text=f"🌐 {entity_name} Relationship Network",
            font=dict(color='#FFD700', size=22, family='Arial Black'),
            x=0.5, y=0.95
        ),
        showlegend=False,
        margin=dict(b=20, l=10, r=10, t=60),
        annotations=[
            dict(
                text="💡 Rotate & Zoom • Hover for details • 3D Dynamic Network",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.02,
                xanchor='center', yanchor='bottom',
                font=dict(color='#CCCCCC', size=11)
            )
        ],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=650,
        scene=dict(
            # Enhanced 3D scene configuration
            bgcolor='rgba(10,10,10,0.9)',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(255,215,0,0.1)',
                showbackground=True,
                backgroundcolor='rgba(20,20,20,0.3)',
                showticklabels=False,
                title='',
                showspikes=False
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(255,215,0,0.1)',
                showbackground=True,
                backgroundcolor='rgba(20,20,20,0.3)',
                showticklabels=False,
                title='',
                showspikes=False
            ),
            zaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(255,215,0,0.1)',
                showbackground=True,
                backgroundcolor='rgba(20,20,20,0.3)',
                showticklabels=False,
                title='',
                showspikes=False
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='cube'
        )
    )
    
    return fig

# ========================================================================================
# UI COMPONENTS
# ========================================================================================

def render_header():
    """Render the application header"""
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <h1 class="main-title">Entity Relationships v2.0</h1>
        <p class="subtitle">Discover complex connections with detailed references and citations</p>
    </div>
    """, unsafe_allow_html=True)

def render_search_section(entity_data):
    """Render the search and selection section"""
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
    
    return selected_entity

def render_metrics(data):
    """Render metrics section"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nodes", f"{len(data['relationships']) + 1}")
    with col2:
        st.metric("Connections", f"{len(data['relationships'])}")
    with col3:
        st.metric("References", f"{len(data['relationships'])}")

def render_entity_card(rel):
    """Render individual entity card"""
    st.markdown(f"""
    <div class="entity-card">
        <h4>{rel['name']}</h4>
        <p><strong>Type:</strong> {rel['type']}</p>
        <p><strong>Relationship:</strong> {rel['relationshipType']}</p>
        <p><strong>Strength:</strong> <span class="strength-badge">{rel['strength']}</span></p>
        <p>{rel['description']}</p>
        <p style="color: #ffed4e; font-size: 0.75rem;">📄 {rel['reference']} ({rel['year']})</p>
    </div>
    """, unsafe_allow_html=True)

def render_reference_card(title, description, reference, year):
    """Render individual reference card"""
    st.markdown(f"""
    <div class="reference-card">
        <h5>{title}</h5>
        <p>{description}</p>
        <p style="color: #ffed4e; font-size: 0.75rem;">📄 {reference} ({year})</p>
    </div>
    """, unsafe_allow_html=True)

def render_company_overview(selected_entity, data):
    """Render company overview section"""
    st.markdown(f"""
    <div class="reference-card">
        <h4>{selected_entity} - Company Overview</h4>
        <p>{data['description']}</p>
        <p style="color: #ffed4e; font-size: 0.75rem;">Founded: {data['founded']} | HQ: {data['headquarters']}</p>
    </div>
    """, unsafe_allow_html=True)

def render_empty_state():
    """Render empty state when no entity is selected"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; color: #888;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
        <h3 style="color: #ffd700;">Select an entity above to explore relationships</h3>
        <p style="color: #ccc;">Available entities: Apple, Tesla, Microsoft, Google, OpenAI, Meta</p>
    </div>
    """, unsafe_allow_html=True)

# ========================================================================================
# MAIN APPLICATION
# ========================================================================================

def main():
    """Main application function"""
    # Apply styling
    apply_custom_css()
    
    # Load data
    entity_data = load_entity_data()
    
    # Render header
    render_header()
    
    # Render search section
    selected_entity = render_search_section(entity_data)
    
    if selected_entity and selected_entity != '':
        data = entity_data[selected_entity]
        
        # Metrics
        st.markdown("<br>", unsafe_allow_html=True)
        render_metrics(data)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Network Graph
        st.markdown('<div class="section-header">🌐 Relationship Network</div>', unsafe_allow_html=True)
        fig = create_network_graph(selected_entity, data)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Two columns for entities and references
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">📊 Connected Entities</div>', unsafe_allow_html=True)
            for rel in data['relationships']:
                render_entity_card(rel)
        
        with col2:
            st.markdown('<div class="section-header">📚 References & Sources</div>', unsafe_allow_html=True)
            
            # Company overview
            render_company_overview(selected_entity, data)
            
            # References
            for rel in data['relationships']:
                render_reference_card(
                    f"{rel['relationshipType']}: {rel['name']}",
                    rel['description'],
                    rel['reference'],
                    rel['year']
                )
    
    else:
        # Empty state
        render_empty_state()

if __name__ == "__main__":
    main()