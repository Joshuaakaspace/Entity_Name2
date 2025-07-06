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
from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
from serpapi import GoogleSearch
import os

API_KEY = os.environ["GEM_API_KEY"]
SERP_API_KEY = os.environ["SERP_API_KEY"]


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
        
        .verification-progress {
            background: rgba(138, 43, 226, 0.1);
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            text-align: center;
            color: #8a2be2;
        }
        
        /* Improved form alignment */
        .stSelectbox label, .stTextInput label, .stRadio label {
            color: #ffd700 !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            margin-bottom: 0.5rem !important;
            display: block !important;
        }
        
        .stSelectbox > div > div, .stTextInput > div > div > input {
            background-color: rgba(255, 215, 0, 0.1) !important;
            border: 2px solid rgba(255, 215, 0, 0.3) !important;
            border-radius: 12px !important;
            font-size: 1.1rem !important;
            padding: 0.75rem 1rem !important;
            min-height: 50px !important;
            display: flex !important;
            align-items: center !important;
        }
        
        .stSelectbox > div > div > div {
            color: #ffd700 !important;
            font-weight: 500 !important;
            font-size: 1.1rem !important;
            line-height: 1.2 !important;
        }
        
        .stTextInput > div > div > input {
            color: #ffd700 !important;
            height: 50px !important;
            box-sizing: border-box !important;
        }
        
        /* Radio button alignment */
        .stRadio > div {
            display: flex !important;
            align-items: center !important;
            gap: 1rem !important;
            margin-top: 0.5rem !important;
        }
        
        .stRadio > div > label {
            display: flex !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0.5rem 1rem !important;
            background: rgba(255, 215, 0, 0.1) !important;
            border: 1px solid rgba(255, 215, 0, 0.3) !important;
            border-radius: 8px !important;
            font-size: 1rem !important;
        }
        
        /* Button styling and alignment */
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
            width: 100% !important;
            margin-top: 1.5rem !important;
        }
        
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3) !important;
        }
        
        /* Column alignment improvements */
        .stColumn {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
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
        
        .relevance-badge {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 8px;
        }
        
        .relevance-relevant {
            background: #00ff88;
            color: #000;
        }
        
        .relevance-less-relevant {
            background: #ff8c00;
            color: #000;
        }
        
        .relevance-unverified {
            background: #666;
            color: #fff;
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
        genai.configure(api_key=API_KEY)
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
    
    def verify_and_tag_relationships(self, entity_name: str, entity_data: Dict[str, Any], search_results: str) -> Dict[str, Any]:
        """Verify relationships and add relevance tags using Gemini"""
        
        relationships_json = json.dumps(entity_data.get('relationships', []), indent=2)
        
        verification_prompt = f"""
        You are an expert fact-checker analyzing entity relationships for relevance and accuracy.
        
        Given the entity "{entity_name}" and the following extracted relationships, verify each relationship and assign a relevance tag.
        
        Original search results for context:
        {search_results[:2000]}...
        
        Extracted relationships to verify:
        {relationships_json}
        
        For each relationship, analyze:
        1. Is it directly mentioned in the search results?
        2. Is it a primary/important relationship for this entity?
        3. Is the information accurate and well-sourced?
        
        Return ONLY a valid JSON array with this structure:
        [
            {{
                "name": "relationship name",
                "relevance": "relevant/less-relevant",
                "confidence": "high/medium/low",
                "reasoning": "Brief explanation of the relevance assessment"
            }}
        ]
        
        Tagging criteria:
        - "relevant": Direct family, primary business roles, major companies, key partnerships
        - "less-relevant": Minor investments, distant connections, speculative links
        
        Limit reasoning to 1-2 sentences each.
        """
        
        try:
            response = self.model.generate_content(verification_prompt)
            response_text = response.text.strip()
            
            # Clean the response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            verification_results = json.loads(response_text)
            
            # Apply verification results to relationships
            verified_data = entity_data.copy()
            for i, rel in enumerate(verified_data.get('relationships', [])):
                # Find matching verification result
                matching_verification = None
                for verification in verification_results:
                    if verification.get('name', '').lower() in rel.get('name', '').lower():
                        matching_verification = verification
                        break
                
                if matching_verification:
                    rel['relevance'] = matching_verification.get('relevance', 'unverified')
                    rel['confidence'] = matching_verification.get('confidence', 'medium')
                    rel['verification_reasoning'] = matching_verification.get('reasoning', 'No verification available')
                else:
                    rel['relevance'] = 'unverified'
                    rel['confidence'] = 'medium'
                    rel['verification_reasoning'] = 'Not verified in post-processing'
            
            return verified_data
            
        except Exception as e:
            st.warning(f"Verification failed: {str(e)}")
            # Add default tags if verification fails
            verified_data = entity_data.copy()
            for rel in verified_data.get('relationships', []):
                rel['relevance'] = 'unverified'
                rel['confidence'] = 'medium'
                rel['verification_reasoning'] = 'Verification process failed'
            
            return verified_data
    
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
                    "year": rel.get("year", "Current"),
                    "relevance": "unverified",  # Will be set during verification
                    "confidence": "medium",
                    "verification_reasoning": "Pending verification"
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
                        "year": "Current",
                        "relevance": "unverified",
                        "confidence": "low",
                        "verification_reasoning": "Basic pattern matching extraction"
                    })
        
        return relationships

# ========================================================================================
# WEB SEARCH AND DATA EXTRACTION
# ========================================================================================

class WebSearchEngine:
    """Class to handle different web search methods"""
    
    def __init__(self):
        self.serp_api_key = SERP_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search(self, query: str, method: str = "auto") -> str:
        """Perform web search using specified method"""
        
        if method == "auto":
            # Try SerpAPI first, then fallback to web scraping
            if self.serp_api_key:
                try:
                    return self._search_serpapi(query)
                except Exception as e:
                    st.warning(f"SerpAPI failed, using web scraping: {str(e)}")
                    return self._search_web_scraping(query)
            else:
                return self._search_web_scraping(query)
        
        elif method == "serpapi":
            return self._search_serpapi(query)
        elif method == "scraping":
            return self._search_web_scraping(query)
        elif method == "duckduckgo":
            return self._search_duckduckgo(query)
        else:
            raise ValueError(f"Unknown search method: {method}")
    
    def _search_serpapi(self, query: str) -> str:
        """Search using SerpAPI"""
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.serp_api_key,
                "num": 10,
                "gl": "us",
                "hl": "en"
            })
            
            results = search.get_dict()
            
            if "organic_results" in results:
                search_text = ""
                for result in results["organic_results"][:5]:  # Top 5 results
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    search_text += f"{title}\n{snippet}\n\n"
                
                return search_text.strip()
            else:
                raise Exception("No organic results found")
                
        except Exception as e:
            raise Exception(f"SerpAPI search failed: {str(e)}")
    
    def _search_web_scraping(self, query: str) -> str:
        """Search using web scraping (DuckDuckGo)"""
        try:
            # Use DuckDuckGo search (no API key required)
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search results
            results = []
            for result_div in soup.find_all('div', class_='result__body')[:5]:
                title_elem = result_div.find('a', class_='result__a')
                snippet_elem = result_div.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    results.append(f"{title}\n{snippet}")
            
            if results:
                return "\n\n".join(results)
            else:
                # Fallback to basic Wikipedia search
                return self._search_wikipedia_fallback(query)
                
        except Exception as e:
            st.warning(f"Web scraping failed: {str(e)}")
            return self._search_wikipedia_fallback(query)
    
    def _search_duckduckgo(self, query: str) -> str:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            search_text = ""
            
            # Extract abstract
            if data.get("Abstract"):
                search_text += f"Overview: {data['Abstract']}\n\n"
            
            # Extract related topics
            if data.get("RelatedTopics"):
                for topic in data["RelatedTopics"][:3]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        search_text += f"{topic['Text']}\n\n"
            
            # Extract answer
            if data.get("Answer"):
                search_text += f"Answer: {data['Answer']}\n\n"
            
            return search_text.strip() if search_text else self._search_wikipedia_fallback(query)
            
        except Exception as e:
            st.warning(f"DuckDuckGo API failed: {str(e)}")
            return self._search_wikipedia_fallback(query)
    
    def _search_wikipedia_fallback(self, query: str) -> str:
        """Fallback search using Wikipedia API"""
        try:
            # Search Wikipedia
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(query.replace(" ", "_"))
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "")
                if extract:
                    return f"Wikipedia Summary: {extract}"
            
            # If direct lookup fails, try search
            search_api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit=1"
            
            response = self.session.get(search_api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("query", {}).get("search"):
                    page_title = data["query"]["search"][0]["title"]
                    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_title)}"
                    
                    response = self.session.get(summary_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        extract = data.get("extract", "")
                        if extract:
                            return f"Wikipedia Summary for {page_title}: {extract}"
            
            return f"Limited information found for {query}. This entity may require specialized search."
            
        except Exception as e:
            return f"Search failed for {query}: {str(e)}"

# ========================================================================================
# DYNAMIC ENTITY SEARCHER
# ========================================================================================

class DynamicEntitySearcher:
    """Class to handle dynamic entity searching and data extraction"""
    
    def __init__(self):
        self.gemini_extractor = GeminiEntityExtractor()
        self.search_engine = WebSearchEngine()
        
    def search_entity_relationships(self, entity_name: str, search_method: str = "auto") -> Optional[Dict[str, Any]]:
        """Search for entity relationships using web search"""
        
        try:
            # Multiple search queries for comprehensive information
            search_queries = [
                f"{entity_name} biography family personal life",
                f"{entity_name} companies founded business ventures",
                f"{entity_name} spouse children family members",
                f"{entity_name} professional career background"
            ]
            
            all_search_results = ""
            
            for i, query in enumerate(search_queries):
                try:
                    st.write(f"🔍 Searching: {query}")
                    search_result = self.search_engine.search(query, method=search_method)
                    all_search_results += f"\n\n--- Search Query {i+1}: {query} ---\n{search_result}"
                    time.sleep(2)  # Rate limiting between searches
                except Exception as e:
                    st.warning(f"Search failed for '{query}': {str(e)}")
                    continue
            
            if not all_search_results.strip():
                st.error("All search queries failed. Please check your internet connection or API keys.")
                return None
            
            # Extract structured data using Gemini
            st.write("🤖 Processing with Gemini AI...")
            entity_data = self.gemini_extractor.extract_relationships(entity_name, all_search_results)
            
            # NEW: Verification step
            st.write("🔍 Verifying relationships and adding relevance tags...")
            verified_data = self.gemini_extractor.verify_and_tag_relationships(entity_name, entity_data, all_search_results)
            
            return verified_data
            
        except Exception as e:
            st.error(f"Error searching for {entity_name}: {str(e)}")
            return None

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
                    "year": "2007-present",
                    "relevance": "relevant",
                    "confidence": "high",
                    "verification_reasoning": "Primary product line for Apple"
                },
                {
                    "name": "Tim Cook",
                    "type": "Person",
                    "relationshipType": "CEO",
                    "strength": "High",
                    "description": "Chief Executive Officer since 2011, previously COO under Steve Jobs",
                    "reference": "Apple Leadership - Tim Cook Biography",
                    "sourceUrl": "https://apple.com/leadership",
                    "year": "2011-present",
                    "relevance": "relevant",
                    "confidence": "high",
                    "verification_reasoning": "Current CEO and key executive"
                },
                {
                    "name": "TSMC",
                    "type": "Technology Company",
                    "relationshipType": "Supplier",
                    "strength": "High",
                    "description": "Primary semiconductor manufacturer for Apple's custom chips",
                    "reference": "TSMC Q4 2023 Earnings Call",
                    "sourceUrl": "https://investor.tsmc.com",
                    "year": "2016-present",
                    "relevance": "relevant",
                    "confidence": "high",
                    "verification_reasoning": "Critical supplier relationship"
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
                    "year": "2004-present",
                    "relevance": "relevant",
                    "confidence": "high",
                    "verification_reasoning": "Founder and current CEO"
                },
                {
                    "name": "Model S",
                    "type": "Product",
                    "relationshipType": "Flagship Vehicle",
                    "strength": "High",
                    "description": "Luxury electric sedan that established Tesla in premium EV market",
                    "reference": "Tesla Model S Launch Analysis",
                    "sourceUrl": "https://tesla.com",
                    "year": "2012-present",
                    "relevance": "relevant",
                    "confidence": "high",
                    "verification_reasoning": "Core product offering"
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
                   relationship_type=rel['relationshipType'],
                   relevance=rel.get('relevance', 'unverified'))
        
        G.add_edge(entity_name, rel['name'], 
                   strength=rel['strength'],
                   relationship_type=rel['relationshipType'],
                   description=rel['description'],
                   relevance=rel.get('relevance', 'unverified'))
    
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
                relevance = edges[0][2].get('relevance', 'unverified')
                
                # Adjust z-position based on relevance and strength
                if relevance == 'relevant':
                    if strength == 'High':
                        z = np.random.uniform(0.8, 1.2)
                    elif strength == 'Medium':
                        z = np.random.uniform(0.3, 0.7)
                    else:
                        z = np.random.uniform(-0.2, 0.2)
                else:  # less-relevant or unverified
                    if strength == 'High':
                        z = np.random.uniform(-0.4, 0.0)
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
        relevance = data.get('relevance', 'unverified')
        
        # Adjust edge styling based on relevance
        edge_color = strength_props['colors'].get(strength, '#FFD700')
        if relevance == 'less-relevant':
            edge_color = '#FF8C00'
        elif relevance == 'unverified':
            edge_color = '#666666'
        
        edge_trace = go.Scatter3d(
            x=[x0, x1, None],
            y=[y0, y1, None],
            z=[z0, z1, None],
            mode='lines',
            line=dict(
                width=strength_props['widths'].get(strength, 4),
                color=edge_color
            ),
            opacity=0.8 if relevance == 'relevant' else 0.5,
            hovertemplate=f'<b>{data["relationship_type"]}</b><br>' +
                         f'Strength: {strength}<br>' +
                         f'Relevance: {relevance}<br>' +
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
            # Adjust color based on relevance
            relevance = G.nodes[node].get('relevance', 'unverified')
            if relevance == 'relevant':
                node_colors.append(base_color)
            elif relevance == 'less-relevant':
                node_colors.append('#FF8C00')
            else:
                node_colors.append('#666666')
            node_sizes.append(15)
        
        node_info.append([
            G.nodes[node]['type'], 
            G.nodes[node].get('description', 'No description available'),
            'Dynamic Search' if is_dynamic else 'Static Data',
            G.nodes[node].get('relevance', 'N/A')
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
        hovertemplate='<b>%{text}</b><br>Type: %{customdata[0]}<br>%{customdata[1]}<br>Source: %{customdata[2]}<br>Relevance: %{customdata[3]}<extra></extra>',
        customdata=node_info,
        name='Network Nodes',
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=[node_trace] + edge_traces)
    
    title_suffix = " (Dynamic Search + AI Verified)" if is_dynamic else ""
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
        <p class="subtitle">Discover complex connections with Google Gemini AI-powered dynamic search + verification</p>
    </div>
    """, unsafe_allow_html=True)

def render_search_section(static_entities, dynamic_entities):
    """Render the enhanced search section with improved alignment"""
    # Search mode selection
    st.markdown("### 🎯 Search Configuration")
    search_mode = st.radio(
        "Choose your search approach:",
        ["Select from Database", "Search New Entity"],
        horizontal=True,
        key="search_mode"
    )
    
    if search_mode == "Select from Database":
        # Combine static and dynamic entities
        all_entities = list(static_entities.keys()) + list(dynamic_entities.keys())
        
        # Better column layout for alignment
        col1, col2 = st.columns([5, 2])
        
        with col1:
            selected_entity = st.selectbox(
                "Select entity to analyze:",
                options=[''] + all_entities,
                format_func=lambda x: "Select an entity..." if x == '' else f"{x}{'🔍' if x in dynamic_entities else ''}",
                key="entity_selector"
            )
        
        with col2:
            analyze_btn = st.button("🔍 Analyze Entity", key="analyze_btn")
        
        return selected_entity, False, "auto"
        
    else:
        # New entity search with search method selection
        st.markdown("#### 🔍 Web Search Configuration")
        
        # Search method selection with better alignment
        col1, col2 = st.columns([4, 2])
        
        with col1:
            search_method = st.selectbox(
                "Select search method:",
                ["auto", "serpapi", "scraping", "duckduckgo"],
                format_func=lambda x: {
                    "auto": "🤖 Auto (SerpAPI → Scraping → Wikipedia)",
                    "serpapi": "🔑 SerpAPI (Requires API Key)",
                    "scraping": "🌐 Web Scraping (DuckDuckGo)",
                    "duckduckgo": "🦆 DuckDuckGo API"
                }.get(x, x),
                key="search_method"
            )
        
        with col2:
            if search_method == "serpapi":
                # serp_key_status = "✅" if st.secrets.get("SERP_API_KEY") else "❌"
                # st.metric("API Key", serp_key_status)
                st.metric("API Key",SERP_API_KEY)
        
        # Entity input with improved alignment
        col1, col2 = st.columns([5, 2])
        
        with col1:
            new_entity = st.text_input(
                "Enter entity name to search:",
                placeholder="e.g., Elon Musk, Jeff Bezos, Any Person/Company...",
                key="new_entity_input"
            )
        
        with col2:
            search_btn = st.button("🔍 Search & Verify", key="search_btn")
        
        return (new_entity, True, search_method) if search_btn else (None, False, search_method)

def render_search_progress(entity_name: str):
    """Render enhanced search progress indicator with verification step"""
    progress_container = st.empty()
    
    steps = [
        "🔍 Searching for biographical information...",
        "🏢 Finding business and professional connections...",
        "👥 Discovering family relationships...",
        "💼 Analyzing career and investments...",
        "🤖 Processing with Gemini AI...",
        "🔍 Verifying relationships and adding relevance tags...",
        "📊 Structuring verified relationship data...",
        "🌐 Building enhanced network visualization...",
        "✅ Analysis and verification complete!"
    ]
    
    progress_bar = st.progress(0)
    
    for i, step in enumerate(steps):
        if i == 5:  # Verification step
            progress_container.markdown(f"""
            <div class="verification-progress">
                <h4>🔍 AI Verification Process: {entity_name}</h4>
                <p>{step}</p>
                <p style="font-size: 0.8rem; color: #888;">Analyzing relevance and accuracy - Step {i+1} of {len(steps)}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            progress_container.markdown(f"""
            <div class="search-progress">
                <h4>🔍 Web Search Analysis: {entity_name}</h4>
                <p>{step}</p>
                <p style="font-size: 0.8rem; color: #888;">Step {i+1} of {len(steps)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(1.2 if i == 5 else 1.0)  # Longer time for verification step
    
    progress_container.empty()
    progress_bar.empty()

def render_entity_card(rel, is_dynamic=False):
    """Render individual entity card with relevance badges"""
    badge = '<span class="new-entity-badge">NEW</span>' if is_dynamic else ''
    
    # Relevance badge
    relevance = rel.get('relevance', 'unverified')
    if relevance == 'relevant':
        relevance_badge = '<span class="relevance-badge relevance-relevant">RELEVANT</span>'
    elif relevance == 'less-relevant':
        relevance_badge = '<span class="relevance-badge relevance-less-relevant">LESS RELEVANT</span>'
    else:
        relevance_badge = '<span class="relevance-badge relevance-unverified">UNVERIFIED</span>'
    
    confidence = rel.get('confidence', 'medium').upper()
    verification_reasoning = rel.get('verification_reasoning', 'No verification details available')
    
    st.markdown(f"""
    <div class="entity-card">
        <h4>{rel['name']}{badge}{relevance_badge}</h4>
        <p><strong>Type:</strong> {rel['type']}</p>
        <p><strong>Relationship:</strong> {rel['relationshipType']}</p>
        <p><strong>Strength:</strong> <span class="strength-badge">{rel['strength']}</span> | <strong>Confidence:</strong> {confidence}</p>
        <p>{rel['description']}</p>
        <p style="color: #8a2be2; font-size: 0.75rem; font-style: italic;">🤖 Verification: {verification_reasoning}</p>
        <p style="color: #ffed4e; font-size: 0.75rem;">📄 {rel['reference']} ({rel['year']})</p>
    </div>
    """, unsafe_allow_html=True)

def render_metrics(data, is_dynamic=False):
    """Render enhanced metrics section with verification stats"""
    relationships = data.get('relationships', [])
    relevant_count = sum(1 for rel in relationships if rel.get('relevance') == 'relevant')
    less_relevant_count = sum(1 for rel in relationships if rel.get('relevance') == 'less-relevant')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Nodes", f"{len(relationships) + 1}")
    with col2:
        st.metric("Connections", f"{len(relationships)}")
    with col3:
        st.metric("Relevant", f"{relevant_count}", delta=f"+{relevant_count - less_relevant_count}" if relevant_count > less_relevant_count else None)
    with col4:
        st.metric("Less Relevant", f"{less_relevant_count}")
    with col5:
        source_label = "AI Verified" if is_dynamic else "Static"
        st.metric("Source", source_label)

def render_empty_state():
    """Render enhanced empty state"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; color: #888;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
        <h3 style="color: #ffd700;">Explore Entity Relationships with AI-Verified Web Search</h3>
        <p style="color: #ccc;">Select from database or search for any person/company with real-time verification</p>
        <p style="color: #aaa; font-size: 0.9rem;">⚡ Powered by Google Gemini AI + Multi-Source Web Search + AI Verification</p>
        <br>
        <div style="background: rgba(255, 215, 0, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem auto; max-width: 600px;">
            <h4 style="color: #ffd700; margin-bottom: 0.5rem;">🔍 New AI Verification Features:</h4>
            <p style="color: #ccc; font-size: 0.85rem; line-height: 1.4;">
                • <strong>Relevance Tagging</strong>: AI categorizes relationships as relevant/less relevant<br>
                • <strong>Confidence Scoring</strong>: High/medium/low confidence ratings<br>
                • <strong>Verification Reasoning</strong>: Explanation for each relevance assessment<br>
                • <strong>Enhanced Visualization</strong>: Color-coded nodes based on verification results
            </p>
        </div>
        <div style="background: rgba(138, 43, 226, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem auto; max-width: 600px;">
            <h4 style="color: #8a2be2; margin-bottom: 0.5rem;">🔍 Search Methods Available:</h4>
            <p style="color: #ccc; font-size: 0.85rem; line-height: 1.4;">
                • <strong>SerpAPI</strong>: Premium Google search results<br>
                • <strong>Web Scraping</strong>: DuckDuckGo search with BeautifulSoup<br>
                • <strong>DuckDuckGo API</strong>: Free instant answers<br>
                • <strong>Wikipedia Fallback</strong>: Reliable biographical data
            </p>
        </div>
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
    search_result = render_search_section(static_entities, dynamic_entities)
    selected_entity, is_search_mode, search_method = search_result if len(search_result) == 3 else (*search_result, "auto")
    
    if selected_entity:
        if is_search_mode:
            # Dynamic search mode
            st.markdown(f'<div class="search-status">🔍 Searching and verifying relationships for: <strong>{selected_entity}</strong> using <strong>{search_method}</strong></div>', unsafe_allow_html=True)
            
            # Check if already cached
            if selected_entity in dynamic_entities:
                data = dynamic_entities[selected_entity]
                is_dynamic = True
            else:
                # Perform search with enhanced progress
                render_search_progress(selected_entity)
                
                with st.spinner("Finalizing AI verification process..."):
                    data = searcher.search_entity_relationships(selected_entity, search_method)
                
                if data:
                    # Cache the results
                    cache_dynamic_entity(selected_entity, data)
                    is_dynamic = True
                    
                    # Enhanced success message with verification stats
                    total_relationships = len(data.get('relationships', []))
                    relevant_count = sum(1 for rel in data.get('relationships', []) if rel.get('relevance') == 'relevant')
                    less_relevant_count = sum(1 for rel in data.get('relationships', []) if rel.get('relevance') == 'less-relevant')
                    
                    st.success(f"🤖 AI Analysis Complete! Found {total_relationships} relationships for {selected_entity}")
                    st.info(f"📊 Verification Results: {relevant_count} relevant, {less_relevant_count} less relevant relationships")
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
        graph_title = "🌐 AI-Verified Relationship Network" if is_dynamic else "🌐 Relationship Network"
        st.markdown(f'<div class="section-header">{graph_title}</div>', unsafe_allow_html=True)
        
        fig = create_network_graph(selected_entity, data, is_dynamic)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Two columns for entities and references
        col1, col2 = st.columns(2)
        
        with col1:
            entities_title = "📊 AI-Verified Connected Entities" if is_dynamic else "📊 Connected Entities"
            st.markdown(f'<div class="section-header">{entities_title}</div>', unsafe_allow_html=True)
            
            # Sort relationships by relevance for better display
            sorted_relationships = sorted(
                data['relationships'], 
                key=lambda x: (x.get('relevance') == 'relevant', x.get('strength') == 'High'), 
                reverse=True
            )
            
            for rel in sorted_relationships:
                render_entity_card(rel, is_dynamic)
        
        with col2:
            refs_title = "📚 AI-Generated References & Verification" if is_dynamic else "📚 References & Sources"
            st.markdown(f'<div class="section-header">{refs_title}</div>', unsafe_allow_html=True)
            
            # Entity overview
            badge = '<span class="new-entity-badge">AI DISCOVERED</span>' if is_dynamic else ''
            st.markdown(f"""
            <div class="reference-card">
                <h4>{selected_entity} - Overview{badge}</h4>
                <p>{data['description']}</p>
                <p style="color: #ffed4e; font-size: 0.75rem;">
                    {"🤖 AI-powered web search + verification" if is_dynamic else f"📊 Static database"}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Verification summary for dynamic entities
            if is_dynamic:
                relationships = data.get('relationships', [])
                relevant_count = sum(1 for rel in relationships if rel.get('relevance') == 'relevant')
                less_relevant_count = sum(1 for rel in relationships if rel.get('relevance') == 'less-relevant')
                unverified_count = sum(1 for rel in relationships if rel.get('relevance') == 'unverified')
                
                st.markdown(f"""
                <div class="reference-card">
                    <h4>🔍 AI Verification Summary</h4>
                    <p><strong>Relevant:</strong> {relevant_count} relationships</p>
                    <p><strong>Less Relevant:</strong> {less_relevant_count} relationships</p>
                    <p><strong>Unverified:</strong> {unverified_count} relationships</p>
                    <p style="color: #8a2be2; font-size: 0.75rem;">🤖 Powered by Gemini AI verification engine</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Individual references
            for rel in sorted_relationships:
                relevance = rel.get('relevance', 'unverified')
                confidence = rel.get('confidence', 'medium')
                verification_reasoning = rel.get('verification_reasoning', 'No verification available')
                
                relevance_color = "#00ff88" if relevance == 'relevant' else "#ff8c00" if relevance == 'less-relevant' else "#666"
                
                st.markdown(f"""
                <div class="reference-card">
                    <h5>{rel['relationshipType']}: {rel['name']}</h5>
                    <p>{rel['description']}</p>
                    <p style="color: {relevance_color}; font-size: 0.75rem;">🔍 Relevance: {relevance.title()} (Confidence: {confidence.title()})</p>
                    <p style="color: #8a2be2; font-size: 0.7rem; font-style: italic;">💭 {verification_reasoning}</p>
                    <p style="color: #ffed4e; font-size: 0.75rem;">📄 {rel['reference']} ({rel['year']})</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Add clear cache option for dynamic entities
        if is_dynamic:
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Search Cache", help="Remove this entity from cache and search again"):
                    if selected_entity in st.session_state.dynamic_entities:
                        del st.session_state.dynamic_entities[selected_entity]
                    st.rerun()
            with col2:
                if st.button("🔄 Re-verify Relationships", help="Run verification process again with updated data"):
                    if selected_entity in st.session_state.dynamic_entities:
                        del st.session_state.dynamic_entities[selected_entity]
                    st.rerun()
    
    else:
        # Empty state
        render_empty_state()
    
    # Enhanced sidebar with verification info
    with st.sidebar:
        st.markdown("### 🔧 Setup Requirements")
        st.markdown("""
        **Install Required Packages:**
        ```bash
        pip install google-generativeai
        pip install beautifulsoup4
        pip install google-search-results
        pip install requests
        ```
        
        **API Keys Configuration:**
        - **Gemini API**: Get from Google AI Studio
        - **SerpAPI**: Get from serpapi.com (optional)
        """)
        
        st.markdown("### 🔍 Search Methods")
        
        # Check API availability
        serp_available = SERP_API_KEY
        
        search_status = {
            "🤖 Auto": "✅ Available",
            "🔑 SerpAPI": "✅ Ready" if serp_available else "❌ API Key Required", 
            "🌐 Web Scraping": "✅ Available",
            "🦆 DuckDuckGo": "✅ Available"
        }
        
        for method, status in search_status.items():
            st.markdown(f"**{method}**: {status}")
        
        st.markdown("### 🤖 AI Integration & Verification")
        st.markdown("""
        - **Google Gemini 1.5 Flash** for relationship extraction
        - **AI Verification Engine** for relevance assessment
        - **Multi-source web search** for comprehensive data
        - **Intelligent fallbacks** for reliability
        - **Confidence scoring** for result quality
        - **Rate limiting** for responsible usage
        """)
        
        st.markdown("### 📊 Search Cache")
        if dynamic_entities:
            st.markdown("**Dynamic Entities (AI Verified):**")
            for entity in dynamic_entities.keys():
                st.markdown(f"• {entity} 🔍✅")
        else:
            st.markdown("*No dynamic searches yet*")
        
        st.markdown("### 💡 Enhanced Workflow")
        st.markdown("""
        1. **Choose Search Method**: SerpAPI, Web Scraping, or Auto
        2. **Enter Entity Name**: Any person/company
        3. **Multi-Query Search**: 4 targeted searches per entity
        4. **Gemini AI Extraction**: Structure raw data into relationships
        5. **AI Verification**: Analyze relevance and add confidence scores
        6. **Enhanced Visualization**: 3D network with verification colors
        7. **Smart Caching**: Store verified results for faster access
        """)
        
        st.markdown("### 🎯 Try These Entities")
        st.markdown("""
        - **Tech CEOs**: Sundar Pichai, Satya Nadella
        - **Entrepreneurs**: Richard Branson, Jack Ma
        - **Investors**: Ray Dalio, Carl Icahn
        - **Politicians**: Any world leader
        - **Celebrities**: Any public figure
        - **Companies**: Any major corporation
        """)
        
        st.markdown("### ⚠️ Rate Limits & AI Usage")
        st.markdown("""
        - **2 second delay** between searches
        - **5 results per query** maximum
        - **4 queries per entity** for comprehensive data
        - **2 AI calls per entity**: extraction + verification
        - **Respectful scraping** with proper headers
        """)

if __name__ == "__main__":
    main()