import pandas as pd
import re

def grade_acronyms(input_csv, output_csv):
    """
    Grade acronyms in a CSV file based on popularity and business relevance.
    
    Args:
        input_csv (str): Path to input CSV file
        output_csv (str): Path to output CSV file with updated grades
    """
    # Read the CSV file
    try:
        df = pd.read_csv(input_csv)
        print(f"Successfully loaded {len(df)} acronyms from {input_csv}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    
    # Define domain categories for recommendation #2
    domain_categories = {
        # Medical domain
        'medicine': {
            'keywords': ['medical', 'health', 'patient', 'disease', 'treatment', 'hospital', 
                        'doctor', 'clinic', 'therapy', 'diagnosis', 'pharmaceutical'],
            'acronyms': ['MRI', 'SSRI', 'TIA', 'HIPAA', 'DNA', 'TENS', 'ICU', 'CPR', 'FDA']
        },
        # Technology domain
        'technology': {
            'keywords': ['protocol', 'software', 'hardware', 'server', 'network', 'database', 
                        'programming', 'algorithm', 'interface', 'computing', 'digital'],
            'acronyms': ['HTML', 'HTTP', 'DHCP', 'TCP', 'FTP', 'USB', 'PDF', 'URL', 'API', 'SDK']
        },
        # Education domain
        'education': {
            'keywords': ['school', 'student', 'teacher', 'education', 'learning', 'academic', 
                        'university', 'college', 'curriculum', 'classroom'],
            'acronyms': ['UCLA', 'NEA', 'GPA', 'SAT', 'ACT', 'PhD', 'BA', 'MA', 'EdD']
        },
        # Aviation/Aerospace domain
        'aviation': {
            'keywords': ['aircraft', 'flight', 'aviation', 'pilot', 'airplane', 'aerospace', 
                        'rocket', 'space', 'orbit', 'satellite'],
            'acronyms': ['NASA', 'ICBM', 'FAA', 'TSA', 'ATC', 'JFK']
        },
        # Financial domain
        'finance': {
            'keywords': ['finance', 'investment', 'bank', 'money', 'fund', 'capital', 'stock', 
                        'trading', 'financial', 'economic', 'fiscal', 'revenue', 'accounting'],
            'acronyms': ['IPO', 'EBIDTA', 'GAAP', 'ROI', 'CEO', 'CFO', 'CPA', 'IRS', 'SEC']
        },
        # Sports domain
        'sports': {
            'keywords': ['sports', 'game', 'player', 'team', 'league', 'championship', 
                        'tournament', 'athlete', 'coach', 'scoring'],
            'acronyms': ['NFL', 'NBA', 'MLB', 'NHL', 'FIFA', 'MVP', 'RBI']
        },
        # Government domain
        'government': {
            'keywords': ['government', 'federal', 'agency', 'policy', 'regulation', 'law', 
                        'administration', 'congress', 'senate', 'legislation', 'national'],
            'acronyms': ['UN', 'FBI', 'CIA', 'NSA', 'DOD', 'EPA', 'NOAA', 'OHSA', 'DOJ']
        }
    }
    
    # Business utility technologies for recommendation #4
    business_utility_tech = {
        'high': ['PDF', 'HTML', 'URL', 'HTTP', 'USB', 'WIFI', 'CRM', 'SEO', 'ERP', 'SaaS', 
                'API', 'CEO', 'CFO', 'ROI', 'B2B', 'B2C', 'KPI', 'ASAP', 'ATM'],
        'medium': ['DHCP', 'TCP', 'FTP', 'SSH', 'SDK', 'RSS', 'SQL', 'VPN', 'CMS', 'LAN', 
                  'WAN', 'FAQ', 'MVP', 'SOP', 'IPO', 'LLC', 'PLC', 'GPS'],
        'low': ['ICBM', 'PTFE', 'TENS', 'SSRI', 'ICBM', 'OHSA', 'HIPAA', 'NOAA', 'NEA']
    }
    
    # Common/popular acronyms
    common_acronyms = [
        'ASAP', 'CEO', 'FAQ', 'PDF', 'SEO', 'URL', 'HTML', 'ATM', 'PIN', 'DIY', 'USB', 
        'LOL', 'DNA', 'NASA', 'FBI', 'CIA', 'UN', 'WHO', 'RSVP', 'FOMO', 'HTTP', 'WIFI', 
        'GPS', 'MBA', 'IRS', 'IQ', 'PhD', 'AM', 'PM', 'BYOB', 'ETA', 'HR', 'ID', 'IMAX', 
        'IPO', 'MRI', 'NBA', 'NFL', 'NHL', 'MLB', 'PC', 'PTSD', 'RSVP', 'TB', 'UFO', 
        'VIP', 'WWE', 'YMCA', 'ZIP'
    ]
    
    # Business and tech keywords
    business_keywords = [
        'business', 'marketing', 'sales', 'customer', 'product', 'service', 'management', 
        'finance', 'retail', 'commercial', 'trade', 'market', 'enterprise', 'corporate', 
        'revenue', 'profit', 'client', 'consumer', 'logistics', 'procurement', 'supply chain', 
        'ecommerce', 'advertising', 'brand', 'payment', 'investment', 'banking', 'accounting', 
        'seo', 'monetization'
    ]
    
    tech_keywords = [
        'technology', 'computer', 'web', 'software', 'programming', 'online', 'digital', 
        'internet', 'computing', 'networking', 'database', 'system', 'platform', 'application', 
        'device', 'server', 'code', 'data', 'algorithm', 'api', 'encryption', 'protocol', 
        'hardware', 'infrastructure'
    ]
    
    # Process each acronym
    results = []
    
    for _, row in df.iterrows():
        acronym = row.get('Acronym', '')
        definition = row.get('Definition', '')
        description = row.get('Description', '')
        tags = row.get('Tags', '')
        
        # Skip if no acronym
        if not acronym:
            continue
            
        # Combine text for analysis
        all_text = f"{definition} {description} {tags}".lower()
        
        # --- Popularity Score (0-5) ---
        popularity_score = 0
        
        # Common acronym check
        if acronym in common_acronyms:
            popularity_score = 5
        else:
            # Length heuristic (shorter acronyms often more common)
            if len(acronym) <= 3:
                popularity_score += 1
                
            # Communication acronyms
            if 'communication' in tags.lower() or 'social media' in tags.lower() or 'internet' in tags.lower():
                popularity_score += 2
                
            # Common domains check
            common_domains = ['technology', 'business', 'medicine', 'education']
            if any(domain in tags.lower() for domain in common_domains):
                popularity_score += 1
                
            # Popular industry check
            popular_industries = ['sports', 'media', 'entertainment', 'gaming']
            if any(industry in tags.lower() for industry in popular_industries):
                popularity_score += 2
                
            # Content-based popularity indicators
            popular_indicators = ['common', 'widely used', 'standard', 'popular']
            if any(indicator in all_text for indicator in popular_indicators):
                popularity_score += 2
                
            # Digital context
            digital_indicators = ['internet', 'online', 'digital', 'web']
            if any(indicator in all_text for indicator in digital_indicators):
                popularity_score += 1
                
            # Business/tech relevance boost
            is_business_related = any(keyword in all_text for keyword in business_keywords)
            is_tech_related = any(keyword in all_text for keyword in tech_keywords)
            
            if is_business_related and is_tech_related:
                popularity_score += 1
            elif is_business_related or is_tech_related:
                popularity_score += 0.5
        
        # --- Domain Importance Score (0-3) ---
        domain_importance_score = 0
        
        for domain, domain_info in domain_categories.items():
            # Check if acronym is explicitly listed for this domain
            if acronym in domain_info['acronyms']:
                domain_importance_score += 2
                
            # Check if text contains domain keywords
            if any(keyword in all_text for keyword in domain_info['keywords']):
                domain_importance_score += 1
                
            # Check if domain is in tags
            if domain in tags.lower():
                domain_importance_score += 1
        
        # Cap domain importance at 3
        domain_importance_score = min(round(domain_importance_score), 3)
        
        # Add portion of domain importance to popularity
        popularity_score += round(domain_importance_score / 2)
        
        # --- Business Relevance Score (0-5) ---
        business_relevance_score = 0
        
        # Basic business relevance checks
        if is_business_related:
            business_relevance_score += 2.5
            
        if is_tech_related:
            business_relevance_score += 1.5
            
        # Tag-specific business relevance
        high_business_tags = ['business', 'marketing', 'finance', 'sales', 'retail']
        if any(tag in tags.lower() for tag in high_business_tags):
            business_relevance_score += 2
            
        tech_business_tags = ['technology', 'computing', 'web development']
        if any(tag in tags.lower() for tag in tech_business_tags):
            business_relevance_score += 1
            
        business_industries = ['administration', 'banking', 'product management', 'international', 
                              'manufacturing', 'organizations', 'shipping']
        if any(industry in tags.lower() for industry in business_industries):
            business_relevance_score += 1
            
        # Special case: sports has commercial value
        if 'sports' in tags.lower():
            business_relevance_score += 1
            
        # --- Business Utility Technology Score (0-3) ---
        business_utility_score = 0
        
        if acronym in business_utility_tech['high']:
            business_utility_score = 3
        elif acronym in business_utility_tech['medium']:
            business_utility_score = 2
        elif acronym in business_utility_tech['low']:
            business_utility_score = 1
            
        # Add business utility to business relevance
        business_relevance_score += business_utility_score
        
        # Content-based business relevance
        business_op_terms = ['management', 'customer', 'financial', 'commercial', 'enterprise', 
                           'corporate', 'revenue', 'profit', 'service', 'product']
        if any(term in all_text for term in business_op_terms):
            business_relevance_score += 1
            
        # Cap scores
        popularity_score = min(round(popularity_score), 5)
        business_relevance_score = min(round(business_relevance_score), 5)
        
        # Calculate total score and final grade
        total_score = popularity_score + business_relevance_score
        
        if total_score <= 2:
            final_grade = 1
        elif total_score <= 4:
            final_grade = 2
        elif total_score <= 6:
            final_grade = 3
        elif total_score <= 8:
            final_grade = 4
        else:
            final_grade = 5
            
        # Create result with all scores for transparency
        result = {
            'Acronym': acronym,
            'Definition': definition,
            'Description': description,
            'Tags': tags,
            'PopularityScore': popularity_score,
            'BusinessRelevanceScore': business_relevance_score,
            'DomainImportanceScore': domain_importance_score,
            'BusinessUtilityScore': business_utility_score,
            'TotalScore': total_score,
            'Grade': final_grade
        }
        
        # Add original grade if present
        if 'Grade' in row:
            result['OriginalGrade'] = row['Grade']
            
        # Include other columns from original data
        for col in df.columns:
            if col not in result and col in row:
                result[col] = row[col]
                
        results.append(result)
    
    # Create output dataframe
    output_df = pd.DataFrame(results)
    
    # Save to CSV
    output_df.to_csv(output_csv, index=False)
    print(f"Successfully graded {len(output_df)} acronyms and saved to {output_csv}")
    
    # Print summary statistics
    if 'OriginalGrade' in output_df.columns:
        output_df['OriginalGrade'] = pd.to_numeric(output_df['OriginalGrade'], errors='coerce')
        changes = output_df['Grade'] - output_df['OriginalGrade']
        
        print("\nGRADE CHANGE STATISTICS:")
        print(f"Upgrades: {len(changes[changes > 0])} ({len(changes[changes > 0])/len(changes)*100:.1f}%)")
        print(f"Downgrades: {len(changes[changes < 0])} ({len(changes[changes < 0])/len(changes)*100:.1f}%)")
        print(f"No change: {len(changes[changes == 0])} ({len(changes[changes == 0])/len(changes)*100:.1f}%)")
        print(f"Average change: {changes.mean():.2f}")
        
        print("\nNEW GRADE DISTRIBUTION:")
        grade_counts = output_df['Grade'].value_counts().sort_index()
        for grade, count in grade_counts.items():
            print(f"Grade {grade}: {count} acronyms ({count/len(output_df)*100:.1f}%)")

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 acronym_grader.py input_file.csv output_file.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    grade_acronyms(input_file, output_file)