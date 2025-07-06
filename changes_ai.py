import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
from datetime import datetime
import numpy as np
import requests
import json
import re
from typing import Dict, List, Any, Optional
import time
import google.generativeai as genai

# ========================================================================================
# PAGE CONFIGURATION
# ========================================================================================

st.set_page_config(
    page_title="Entity Relationships v3.0 - Dynamic Search",
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
        
        .search-status {
            background: rgba(255, 215, 0, 0.1);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            text-align: center;
            color: #ffd700;
        }
        
        .search-progress {
            background: rgba(0, 150, 255, 0.1);
            border: 1px solid rgba(0, 150, 255, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            text-align: center;
            color: #0096ff;
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
        
        .stTextInput label {
            color: #ffd700 !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
        }
        
        .stTextInput > div > div > input {
            background-color: rgba(255, 215, 0, 0.1) !important;
            border: 2px solid rgba(255, 215, 0, 0.3) !important;
            border-radius: 12px !important;
            color: #ffd700 !important;
            font-size: 1.1rem !important;
            padding: 0.6rem !important;
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
        
        .new-entity-badge {
            background: #00ff88;
            color: #000;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

# ========================================================================================
# GOOGLE GEMINI API INTEGRATION
# ========================================================================================

class GeminiEntityExtractor:
    """Class to handle entity relationship extraction using Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Initialize Gemini
        genai.configure(api_key="AIzaSyBV7UuuEVccI6NwYSRXHPzMRXCF9zyPM5M")
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def extract_relationships(self, entity_name: str, search_results: str) -> Dict[str, Any]:
        """Extract structured relationship data from search results using Gemini"""
        
        prompt = f"""
        You are an expert at extracting structured relationship data from web search results.
        
        Analyze the following search results about "{entity_name}" and extract relationship information.
        
        Return ONLY a valid JSON object with this exact structure (no markdown formatting, no extra text):
        {{
            "type": "Person/Company/Organization",
            "description": "Brief description of the entity",
            "founded": "Year founded or birth year",
            "headquarters": "Location or residence",
            "relationships": [
                {{
                    "name": "Related entity name",
                    "type": "Person/Company/Product/Platform/Foundation",
                    "relationshipType": "Family Member/CEO/Founder/Owner/Investor/Board Member/Spouse/Child/Parent",
                    "strength": "High/Medium/Low",
                    "description": "Brief description of the relationship",
                    "reference": "Source of information",
                    "sourceUrl": "URL if available or 'Web Search'",
                    "year": "Time period or year"
                }}
            ]
        }}
        
        Focus on extracting:
        1. Family relationships (spouse, children, parents, siblings)
        2. Business relationships (companies owned, founded, invested in, CEO of)
        3. Professional roles and partnerships
        4. Major assets, foundations, or initiatives
        
        Rules:
        - Extract only factual, verifiable relationships
        - Use "High" strength for direct family/ownership, "Medium" for professional roles, "Low" for investments
        - Keep descriptions concise but informative
        - Limit to maximum 10 most significant relationships
        - If entity type is unclear, default to "Person"
        
        Search Results:
        {search_results}
        """
        
        try:
            # Make API call to Gemini
            response = self.model.generate_content(prompt)
            
            # Clean the response text
            response_text = response.text.strip()
            
            # Remove any markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Parse JSON response
            extracted_data = json.loads(response_text)
            
            # Validate and clean the data
            return self._validate_and_clean_data(entity_name, extracted_data)
            
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse Gemini response: {e}")
            return self._fallback_extraction(entity_name, search_results)
        
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            return self._fallback_extraction(entity_name, search_results)
    
    def _validate_and_clean_data(self, entity_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the extracted data"""
        
        # Ensure required fields exist
        cleaned_data = {
            "type": data.get("type", "Person"),
            "description": data.get("description", f"Information about {entity_name}"),
            "founded": data.get("founded", "Unknown"),
            "headquarters": data.get("headquarters", "Unknown"),
            "relationships": []
        }
        
        # Clean and validate relationships
        relationships = data.get("relationships", [])
        for rel in relationships[:10]:  # Limit to 10 relationships
            if isinstance(rel, dict) and rel.get("name"):
                cleaned_rel = {
                    "name": rel.get("name", "Unknown").strip(),
                    "type": rel.get("type", "Unknown"),
                    "relationshipType": rel.get("relationshipType", "Unknown"),
                    "strength": rel.get("strength", "Medium"),
                    "description": rel.get("description", "No description available"),
                    "reference": rel.get("reference", "Gemini AI Analysis"),
                    "sourceUrl": rel.get("sourceUrl", "Web Search"),
                    "year": rel.get("year", "Current")
                }
                
                # Validate strength values
                if cleaned_rel["strength"] not in ["High", "Medium", "Low"]:
                    cleaned_rel["strength"] = "Medium"
                
                cleaned_data["relationships"].append(cleaned_rel)
        
        return cleaned_data
    
    def _fallback_extraction(self, entity_name: str, search_results: str) -> Dict[str, Any]:
        """Fallback extraction method if Gemini fails"""
        
        # Basic entity type detection
        entity_type = "Person"
        if any(word in entity_name.lower() for word in ["inc", "corp", "company", "ltd", "llc"]):
            entity_type = "Company"
        
        # Extract basic information from search results
        relationships = self._extract_basic_relationships(entity_name, search_results)
        
        return {
            "type": entity_type,
            "description": f"Information about {entity_name} extracted from web search (fallback mode)",
            "founded": "Unknown",
            "headquarters": "Unknown",
            "relationships": relationships
        }
    
    def _extract_basic_relationships(self, entity_name: str, search_results: str) -> List[Dict[str, Any]]:
        """Basic relationship extraction from search results"""
        relationships = []
        
        # Common relationship patterns
        patterns = {
            "CEO": r"CEO of ([A-Z][a-zA-Z\s&]+)",
            "Founded": r"founded ([A-Z][a-zA-Z\s&]+)",
            "Owns": r"owns ([A-Z][a-zA-Z\s&]+)",
            "Married": r"married to ([A-Z][a-zA-Z\s]+)",
            "Spouse": r"(?:wife|husband|spouse) ([A-Z][a-zA-Z\s]+)",
            "Child": r"(?:son|daughter|child) ([A-Z][a-zA-Z\s]+)",
            "Parent": r"(?:father|mother|parent) ([A-Z][a-zA-Z\s]+)",
            "Company": r"([A-Z][a-zA-Z\s&]+) (?:Inc|Corp|Company|Ltd|LLC)"
        }
        
        for rel_type, pattern in patterns.items():
            matches = re.findall(pattern, search_results, re.IGNORECASE)
            for match in matches[:2]:  # Limit to 2 matches per type
                if match.strip() and len(match.strip()) > 2:
                    relationships.append({
                        "name": match.strip(),
                        "type": "Person" if rel_type in ["Married", "Spouse", "Child", "Parent"] else "Company",
                        "relationshipType": rel_type,
                        "strength": "High" if rel_type in ["Married", "Spouse", "Child"] else "Medium",
                        "description": f"{rel_type} relationship with {entity_name}",
                        "reference": "Pattern Matching Analysis",
                        "sourceUrl": "Web Search",
                        "year": "Current"
                    })
        
        return relationships

# ========================================================================================
# WEB SEARCH AND DATA EXTRACTION
# ========================================================================================

class DynamicEntitySearcher:
    """Class to handle dynamic entity searching and data extraction"""
    
    def __init__(self):
        self.gemini_extractor = GeminiEntityExtractor()
        
    def search_entity_relationships(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Search for entity relationships using web search"""
        
        try:
            # Multiple search queries for comprehensive information
            search_queries = [
                f"{entity_name} family relationships biography",
                f"{entity_name} companies owned business ventures",
                f"{entity_name} personal life spouse children",
                f"{entity_name} professional background career"
            ]
            
            all_search_results = ""
            
            for query in search_queries:
                # Simulate web search (replace with actual web search API)
                search_result = self._perform_web_search(query)
                all_search_results += f"\n\n--- Search for: {query} ---\n{search_result}"
                time.sleep(1)  # Rate limiting
            
            # Extract structured data using Gemini
            entity_data = self.gemini_extractor.extract_relationships(entity_name, all_search_results)
            
            return entity_data
            
        except Exception as e:
            st.error(f"Error searching for {entity_name}: {str(e)}")
            return None
    
    def _perform_web_search(self, query: str) -> str:
        """Perform web search for the given query"""
        
        # Enhanced simulated results with more comprehensive data
        simulated_results = {
            "elon musk": """
            Elon Musk is the CEO of Tesla Inc and SpaceX. He was previously married to Talulah Riley (2010-2012, 2013-2016) and Justine Wilson (2000-2008).
            He has multiple children including X Æ A-Xii Musk with Claire Boucher (Grimes), Nevada Alexander Musk, Griffin Musk, Xavier Musk, Damian Musk, Saxon Musk, and Kai Musk.
            His father is Errol Musk and his mother is Maye Musk. He has siblings Kimbal Musk and Tosca Musk.
            He founded Tesla Motors, SpaceX, Neuralink, and The Boring Company. He also co-founded PayPal and OpenAI.
            He acquired Twitter in 2022 for $44 billion and renamed it to X. He owns significant stakes in Tesla and SpaceX.
            He was born in Pretoria, South Africa and later moved to Canada and then the United States.
            He is currently one of the world's richest people with a net worth over $200 billion.
            He studied at the University of Pennsylvania and briefly attended Stanford University.
            """,
            "jeff bezos": """
            Jeff Bezos is the founder and executive chairman of Amazon.com Inc. He was married to MacKenzie Scott (1993-2019).
            He has four children: Preston Bezos, and three other children with MacKenzie Scott.
            He is currently in a relationship with Lauren Sanchez. His parents are Ted Jorgensen and Jacklyn Gise Bezos.
            He founded Amazon in 1994 from his garage in Bellevue, Washington. He also founded Blue Origin aerospace company in 2000.
            He owns The Washington Post, which he purchased in 2013 for $250 million.
            He stepped down as CEO of Amazon in 2021 but remains executive chairman.
            He is one of the world's wealthiest individuals with a net worth over $170 billion.
            He owns multiple properties including a $165 million mansion in Beverly Hills and a ranch in Texas.
            He studied at Princeton University and worked on Wall Street before founding Amazon.
            """,
            "bill gates": """
            Bill Gates co-founded Microsoft Corporation with Paul Allen in 1975. He was married to Melinda French Gates (1994-2021).
            He has three children: Jennifer Katharine Gates, Rory John Gates, and Phoebe Adele Gates.
            His parents are William H. Gates Sr. and Mary Maxwell Gates. He has two sisters: Kristianne Gates and Libby Gates.
            He co-founded Microsoft and served as CEO until 2000, then as chairman until 2014.
            He runs the Bill & Melinda Gates Foundation, one of the world's largest private foundations.
            He has invested in numerous companies including Berkshire Hathaway, where he serves on the board.
            He stepped down from Microsoft's board in 2020 to focus on philanthropy.
            He is known for his work in global health, education, and climate change through his foundation.
            He owns significant real estate including a $127 million mansion in Medina, Washington.
            He studied at Harvard University but dropped out to focus on Microsoft.
            """,
            "warren buffett": """
            Warren Buffett is the CEO and chairman of Berkshire Hathaway Inc. He was married to Susan Thompson Buffett (1952-2004) and later married Astrid Menks in 2006.
            He has three children: Susan Alice Buffett, Howard Graham Buffett, and Peter Andrew Buffett.
            His father was Howard Buffett, a U.S. Congressman. His mother was Leila Stahl Buffett.
            He is known as the "Oracle of Omaha" and is one of the most successful investors in history.
            Berkshire Hathaway owns significant stakes in Apple Inc, Coca-Cola Company, Bank of America, and many other major corporations.
            He has pledged to give away 99% of his wealth through The Giving Pledge, which he co-founded with Bill Gates.
            He studied at the University of Nebraska and Columbia Business School under Benjamin Graham.
            He lives in the same house in Omaha, Nebraska that he bought in 1958 for $31,500.
            He is known for his frugal lifestyle despite being one of the world's richest people.
            He has been CEO of Berkshire Hathaway since 1970 and has generated exceptional returns for shareholders.
            """,
            "tim cook": """
            Tim Cook is the CEO of Apple Inc since August 2011. He succeeded Steve Jobs as CEO.
            He is openly gay and has been in a long-term relationship, though he keeps his personal life private.
            He was born in Mobile, Alabama and raised in nearby Robertsdale. His father Donald Cook was a shipyard worker and his mother Geraldine Cook was a pharmacy worker.
            He joined Apple in 1998 as Senior Vice President for Worldwide Operations and became COO in 2005.
            Before Apple, he worked at IBM, Intelligent Electronics, and Compaq Computer Corporation.
            Under his leadership, Apple has launched products like the Apple Watch, AirPods, and various iPhone and iPad models.
            He studied at Auburn University and Duke University's Fuqua School of Business.
            He has been recognized as one of the most powerful people in business and technology.
            He is known for his operational expertise and supply chain management skills.
            He has advocated for privacy rights, environmental sustainability, and LGBTQ+ rights.
            """,
            "mark zuckerberg": """
            Mark Zuckerberg is the co-founder, chairman, and CEO of Meta Platforms Inc (formerly Facebook Inc).
            He is married to Priscilla Chan since 2012. They have two daughters: Maxima Chan Zuckerberg and August Chan Zuckerberg.
            His parents are Karen Kempner Zuckerberg and Edward Zuckerberg. He has three sisters: Randi, Donna, and Arielle Zuckerberg.
            He founded Facebook in 2004 while studying at Harvard University with co-founders Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, and Chris Hughes.
            Meta owns Facebook, Instagram, WhatsApp, and is developing virtual reality technology through Reality Labs.
            He and his wife founded the Chan Zuckerberg Initiative, focusing on education, science, and justice & opportunity.
            He dropped out of Harvard in his sophomore year to focus on Facebook.
            He has been involved in various controversies related to privacy, misinformation, and antitrust issues.
            He owns significant real estate in California and Hawaii, including a 1,400-acre compound in Hawaii.
            He is one of the youngest billionaires in the world and has signed The Giving Pledge.
            """
        }
        
        # Check if we have simulated data for this entity
        query_lower = query.lower()
        for entity, data in simulated_results.items():
            if entity in query_lower:
                return data
        
        # Extract entity name from query for generic response
        entity_words = query.split()
        entity_name = " ".join([word for word in entity_words if word.lower() not in ['family', 'relationships', 'biography', 'companies', 'owned', 'business', 'ventures', 'personal', 'life', 'spouse', 'children', 'professional', 'background', 'career']])
        
        # Generic response for unknown entities
        return f"""
        Search results for {entity_name}: This person or entity may be less widely documented online.
        Additional information may be available through specialized databases or recent news sources.
        Common relationship types to look for include family members, business partnerships, 
        professional roles, and organizational affiliations.
        """

# ========================================================================================
# DATA MANAGEMENT
# ========================================================================================

@st.cache_data
def load_entity_data():
    """Load and return static entity relationship data"""
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
                    "description": "Primary semiconductor manufacturer for Apple's custom chips",
                    "reference": "TSMC Q4 2023 Earnings Call",
                    "sourceUrl": "https://investor.tsmc.com",
                    "year": "2016-present"
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
                }
            ]
        }
    }

def get_dynamic_entity_data():
    """Get cached dynamic entity data"""
    if 'dynamic_entities' not in st.session_state:
        st.session_state.dynamic_entities = {}
    return st.session_state.dynamic_entities

def cache_dynamic_entity(entity_name: str, entity_data: Dict[str, Any]):
    """Cache dynamically searched entity data"""
    if 'dynamic_entities' not in st.session_state:
        st.session_state.dynamic_entities = {}
    st.session_state.dynamic_entities[entity_name] = entity_data

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
        'Company': '#96CEB4',                # Mint Green
        'Automotive/Energy Company': '#FDCB6E', # Light Orange
        'Unknown': '#888888'                 # Gray for unknown types
    }

def get_strength_properties():
    """Return strength-based styling properties"""
    return {
        'colors': {'High': '#FFD700', 'Medium': '#FF8C00', 'Low': '#666666'},
        'widths': {'High': 6, 'Medium': 4, 'Low': 2}
    }

def create_network_graph(entity_name, entity_data, is_dynamic=False):
    """Create an enhanced 3D dynamic interactive network graph using Plotly"""
    
    # Create NetworkX graph
    G = nx.Graph()
    
    # Add center node
    G.add_node(entity_name, 
               type=entity_data['type'], 
               is_center=True,
               is_dynamic=is_dynamic,
               description=entity_data['description'])
    
    # Add relationship nodes and edges
    for rel in entity_data['relationships']:
        G.add_node(rel['name'], 
                   type=rel['type'], 
                   is_center=False,
                   is_dynamic=is_dynamic,
                   description=rel['description'],
                   relationship_type=rel['relationshipType'])
        
        G.add_edge(entity_name, rel['name'], 
                   strength=rel['strength'],
                   relationship_type=rel['relationshipType'],
                   description=rel['description'])
    
    # Generate 3D layout
    pos_2d = nx.spring_layout(G, k=3, iterations=150, seed=42)
    
    # Convert to 3D with intelligent positioning
    pos_3d = {}
    center_node = entity_name
    
    for node in G.nodes():
        x, y = pos_2d[node]
        
        if node == center_node:
            z = 0.2
        else:
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
                
        pos_3d[node] = (x * 2, y * 2, z)
    
    # Get styling properties
    color_map = get_color_mapping()
    strength_props = get_strength_properties()
    
    # Create edge traces
    edge_traces = []
    for edge in G.edges(data=True):
        node1, node2, data = edge
        x0, y0, z0 = pos_3d[node1]
        x1, y1, z1 = pos_3d[node2]
        strength = data['strength']
        
        edge_trace = go.Scatter3d(
            x=[x0, x1, None],
            y=[y0, y1, None],
            z=[z0, z1, None],
            mode='lines',
            line=dict(
                width=strength_props['widths'].get(strength, 4),
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
    
    # Create node trace
    node_x, node_y, node_z = [], [], []
    node_text, node_colors, node_sizes, node_info = [], [], [], []
    
    for node in G.nodes():
        x, y, z = pos_3d[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        
        display_text = node if len(node) <= 15 else node[:15] + '...'
        node_text.append(display_text)
        
        node_type = G.nodes[node]['type']
        base_color = color_map.get(node_type, '#FFD700')
        
        if G.nodes[node].get('is_center', False):
            node_colors.append('#FFD700' if not is_dynamic else '#00FF88')
            node_sizes.append(25)
        else:
            node_colors.append(base_color)
            node_sizes.append(15)
        
        node_info.append([
            G.nodes[node]['type'], 
            G.nodes[node].get('description', 'No description available'),
            'Dynamic Search' if is_dynamic else 'Static Data'
        ])
    
    # Create node trace
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        text=node_text,
        textposition='middle center',
        textfont=dict(color='white', size=10, family='Arial Black'),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='rgba(255,255,255,0.8)'),
            opacity=0.9,
            symbol='circle'
        ),
        hovertemplate='<b>%{text}</b><br>Type: %{customdata[0]}<br>%{customdata[1]}<br>Source: %{customdata[2]}<extra></extra>',
        customdata=node_info,
        name='Network Nodes',
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=[node_trace] + edge_traces)
    
    title_suffix = " (Dynamic Search)" if is_dynamic else ""
    title_color = "#00FF88" if is_dynamic else "#FFD700"
    
    fig.update_layout(
        title=dict(
            text=f"🌐 {entity_name} Relationship Network{title_suffix}",
            font=dict(color=title_color, size=22, family='Arial Black'),
            x=0.5, y=0.95
        ),
        showlegend=False,
        margin=dict(b=20, l=10, r=10, t=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=650,
        scene=dict(
            bgcolor='rgba(10,10,10,0.9)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,215,0,0.1)', showticklabels=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,215,0,0.1)', showticklabels=False),
            zaxis=dict(showgrid=True, gridcolor='rgba(255,215,0,0.1)', showticklabels=False),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
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
        <h1 class="main-title">Entity Relationships v3.0</h1>
        <p class="subtitle">Discover complex connections with Google Gemini AI-powered dynamic search</p>
    </div>
    """, unsafe_allow_html=True)

def render_search_section(static_entities, dynamic_entities):
    """Render the enhanced search section"""
    # Search mode selection
    search_mode = st.radio(
        "Search Mode:",
        ["Select from Database", "Search New Entity"],
        horizontal=True,
        key="search_mode"
    )
    
    if search_mode == "Select from Database":
        # Combine static and dynamic entities
        all_entities = list(static_entities.keys()) + list(dynamic_entities.keys())
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            selected_entity = st.selectbox(
                "Select entity:",
                options=[''] + all_entities,
                format_func=lambda x: "Select an entity..." if x == '' else f"{x}{'🔍' if x in dynamic_entities else ''}",
                key="entity_selector"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_btn = st.button("🔍 Analyze", key="analyze_btn")
        
        return selected_entity, False
        
    else:
        # New entity search
        col1, col2 = st.columns([4, 1])
        
        with col1:
            new_entity = st.text_input(
                "Enter entity name to search:",
                placeholder="e.g., Elon Musk, Jeff Bezos, Bill Gates...",
                key="new_entity_input"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            search_btn = st.button("🔍 Search Web", key="search_btn")
        
        return new_entity if search_btn else None, True

def render_search_progress(entity_name: str):
    """Render search progress indicator"""
    progress_container = st.empty()
    
    steps = [
        "🔍 Searching for family relationships...",
        "🏢 Finding business connections...",
        "🤖 Analyzing with Gemini AI...",
        "📊 Extracting structured data...",
        "🌐 Building network graph...",
        "✅ Search complete!"
    ]
    
    progress_bar = st.progress(0)
    
    for i, step in enumerate(steps):
        progress_container.markdown(f"""
        <div class="search-progress">
            <h4>Searching: {entity_name}</h4>
            <p>{step}</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(1.2)  # Simulate processing time
    
    progress_container.empty()
    progress_bar.empty()

def render_entity_card(rel, is_dynamic=False):
    """Render individual entity card"""
    badge = '<span class="new-entity-badge">NEW</span>' if is_dynamic else ''
    
    st.markdown(f"""
    <div class="entity-card">
        <h4>{rel['name']}{badge}</h4>
        <p><strong>Type:</strong> {rel['type']}</p>
        <p><strong>Relationship:</strong> {rel['relationshipType']}</p>
        <p><strong>Strength:</strong> <span class="strength-badge">{rel['strength']}</span></p>
        <p>{rel['description']}</p>
        <p style="color: #ffed4e; font-size: 0.75rem;">📄 {rel['reference']} ({rel['year']})</p>
    </div>
    """, unsafe_allow_html=True)

def render_metrics(data, is_dynamic=False):
    """Render metrics section"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nodes", f"{len(data['relationships']) + 1}")
    with col2:
        st.metric("Connections", f"{len(data['relationships'])}")
    with col3:
        st.metric("References", f"{len(data['relationships'])}")
    with col4:
        source_label = "Dynamic" if is_dynamic else "Static"
        st.metric("Source", source_label)

def render_empty_state():
    """Render empty state when no entity is selected"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; color: #888;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
        <h3 style="color: #ffd700;">Explore Entity Relationships</h3>
        <p style="color: #ccc;">Select from database or search for any person/company online</p>
        <p style="color: #aaa; font-size: 0.9rem;">Try searching: Elon Musk, Jeff Bezos, Bill Gates, Warren Buffett</p>
    </div>
    """, unsafe_allow_html=True)

# ========================================================================================
# MAIN APPLICATION
# ========================================================================================

def main():
    """Main application function"""
    # Apply styling
    apply_custom_css()
    
    # Initialize searcher
    searcher = DynamicEntitySearcher()
    
    # Load data
    static_entities = load_entity_data()
    dynamic_entities = get_dynamic_entity_data()
    
    # Render header
    render_header()
    
    # Render search section
    selected_entity, is_search_mode = render_search_section(static_entities, dynamic_entities)
    
    if selected_entity:
        if is_search_mode:
            # Dynamic search mode
            st.markdown(f'<div class="search-status">🔍 Searching for relationships: <strong>{selected_entity}</strong></div>', unsafe_allow_html=True)
            
            # Check if already cached
            if selected_entity in dynamic_entities:
                data = dynamic_entities[selected_entity]
                is_dynamic = True
            else:
                # Perform search
                render_search_progress(selected_entity)
                
                with st.spinner("Analyzing search results..."):
                    data = searcher.search_entity_relationships(selected_entity)
                
                if data:
                    # Cache the results
                    cache_dynamic_entity(selected_entity, data)
                    is_dynamic = True
                    
                    # Check if data was extracted by Gemini or fallback
                    gemini_used = any("Gemini AI Analysis" in rel.get("reference", "") for rel in data.get("relationships", []))
                    if gemini_used:
                        print(f"Gemini Used: {gemini_used}")
                        st.success(f"🤖 Gemini AI found {len(data['relationships'])} relationships for {selected_entity}")
                    else:
                        st.info(f"🔍 Pattern matching found {len(data['relationships'])} relationships for {selected_entity} (fallback mode)")
                else:
                    st.error("❌ Could not find sufficient information for this entity")
                    return
        else:
            # Static database mode
            if selected_entity in static_entities:
                data = static_entities[selected_entity]
                is_dynamic = False
            elif selected_entity in dynamic_entities:
                data = dynamic_entities[selected_entity]
                is_dynamic = True
            else:
                st.error("Entity not found")
                return
        
        # Display results
        st.markdown("<br>", unsafe_allow_html=True)
        render_metrics(data, is_dynamic)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Network Graph
        graph_title = "🌐 Relationship Network (Dynamic Search)" if is_dynamic else "🌐 Relationship Network"
        st.markdown(f'<div class="section-header">{graph_title}</div>', unsafe_allow_html=True)
        
        fig = create_network_graph(selected_entity, data, is_dynamic)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Two columns for entities and references
        col1, col2 = st.columns(2)
        
        with col1:
            entities_title = "📊 Connected Entities (AI Discovered)" if is_dynamic else "📊 Connected Entities"
            st.markdown(f'<div class="section-header">{entities_title}</div>', unsafe_allow_html=True)
            
            for rel in data['relationships']:
                render_entity_card(rel, is_dynamic)
        
        with col2:
            refs_title = "📚 AI-Generated References" if is_dynamic else "📚 References & Sources"
            st.markdown(f'<div class="section-header">{refs_title}</div>', unsafe_allow_html=True)
            
            # Entity overview
            badge = '<span class="new-entity-badge">DISCOVERED</span>' if is_dynamic else ''
            st.markdown(f"""
            <div class="reference-card">
                <h4>{selected_entity} - Overview{badge}</h4>
                <p>{data['description']}</p>
                <p style="color: #ffed4e; font-size: 0.75rem;">
                    {"🤖 AI-powered web search" if is_dynamic else f"📊 Static database"}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Individual references
            for rel in data['relationships']:
                st.markdown(f"""
                <div class="reference-card">
                    <h5>{rel['relationshipType']}: {rel['name']}</h5>
                    <p>{rel['description']}</p>
                    <p style="color: #ffed4e; font-size: 0.75rem;">📄 {rel['reference']} ({rel['year']})</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Add clear cache option for dynamic entities
        if is_dynamic:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Clear Search Cache", help="Remove this entity from cache and search again"):
                if selected_entity in st.session_state.dynamic_entities:
                    del st.session_state.dynamic_entities[selected_entity]
                st.rerun()
    
    else:
        # Empty state
        render_empty_state()
    
    # Display cache info and setup instructions in sidebar
    with st.sidebar:
        st.markdown("### 🔧 Setup Requirements")
        st.markdown("""
        **Install Required Package:**
        ```bash
        pip install google-generativeai
        ```
        
        **API Key Configuration:**
        - Get your Gemini API key from Google AI Studio
        - Update the API key in the code
        """)
        
        st.markdown("### 🤖 AI Integration")
        st.markdown("""
        - **Google Gemini 1.5 Flash** for relationship extraction
        - **Pattern Matching** as fallback
        - **Structured JSON** output parsing
        - **Error Handling** for robust operation
        """)
        
        st.markdown("### 📊 Search Cache")
        if dynamic_entities:
            st.markdown("**Dynamic Entities:**")
            for entity in dynamic_entities.keys():
                st.markdown(f"• {entity} 🔍")
        else:
            st.markdown("*No dynamic searches yet*")
        
        st.markdown("### 💡 How it works")
        st.markdown("""
        1. **Select Mode**: Choose database or web search
        2. **Enter Entity**: Type any person/company name  
        3. **Web Search**: Multiple queries for comprehensive data
        4. **Gemini AI**: Structures raw search results
        5. **Visualize**: Interactive 3D network graph
        6. **Cache**: Saves results for faster access
        """)
        
        st.markdown("### 🎯 Try These Entities")
        st.markdown("""
        - **Tech Leaders**: Elon Musk, Bill Gates, Tim Cook
        - **Business**: Jeff Bezos, Warren Buffett  
        - **Social Media**: Mark Zuckerberg
        - **Any Person/Company**: Custom search
        """)

if __name__ == "__main__":
    main()