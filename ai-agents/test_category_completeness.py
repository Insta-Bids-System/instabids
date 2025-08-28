"""
Test script to verify the completeness of all 14 work-type categories
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from project_categorization.project_types import PROJECT_TYPE_MAPPING, SYNONYM_MAPPING

def analyze_category_completeness():
    """Analyze the completeness of each category implementation"""
    
    print("=" * 80)
    print("CATEGORIZATION SYSTEM COMPLETENESS ANALYSIS")
    print("=" * 80)
    
    # Summary statistics
    total_project_types = sum(len(types) for types in PROJECT_TYPE_MAPPING.values())
    total_synonyms = len(SYNONYM_MAPPING)
    
    print(f"\n[STATS] OVERALL STATISTICS:")
    print(f"  - Total Categories: {len(PROJECT_TYPE_MAPPING)}")
    print(f"  - Total Project Types: {total_project_types}")
    print(f"  - Total Synonym Mappings: {total_synonyms}")
    
    print("\n" + "=" * 80)
    print("CATEGORY-BY-CATEGORY ANALYSIS:")
    print("=" * 80)
    
    # Analyze each category
    for category_name, project_types in PROJECT_TYPE_MAPPING.items():
        print(f"\n[{category_name.upper()}]")
        print(f"  - Project Types: {len(project_types)}")
        
        # Count how many have synonym mappings
        synonyms_count = 0
        missing_synonyms = []
        for proj_type in project_types:
            if proj_type in SYNONYM_MAPPING:
                synonyms_count += 1
            else:
                missing_synonyms.append(proj_type)
        
        coverage = (synonyms_count / len(project_types)) * 100 if project_types else 0
        print(f"  - Synonym Coverage: {synonyms_count}/{len(project_types)} ({coverage:.1f}%)")
        
        # Flag completeness
        if coverage == 100:
            status = "[COMPLETE]"
        elif coverage >= 80:
            status = "[MOSTLY COMPLETE]"
        elif coverage >= 50:
            status = "[PARTIAL]"
        else:
            status = "[NEEDS WORK]"
        
        print(f"  - Status: {status}")
        
        # Show missing synonyms for incomplete categories
        if missing_synonyms and len(missing_synonyms) <= 10:
            print(f"  - Missing Synonyms: {', '.join(missing_synonyms[:5])}")
            if len(missing_synonyms) > 5:
                print(f"    ... and {len(missing_synonyms) - 5} more")
        elif missing_synonyms:
            print(f"  - Missing Synonyms: {len(missing_synonyms)} items need synonym mappings")
    
    print("\n" + "=" * 80)
    print("IMPLEMENTATION STATUS BY CATEGORY:")
    print("=" * 80)
    
    # Check which categories are fully ready for production
    production_ready = []
    needs_synonyms = []
    needs_project_types = []
    
    for category, types in PROJECT_TYPE_MAPPING.items():
        if len(types) == 0:
            needs_project_types.append(category)
        else:
            # Check synonym coverage
            coverage = sum(1 for t in types if t in SYNONYM_MAPPING) / len(types) * 100
            if coverage >= 80:
                production_ready.append(category)
            else:
                needs_synonyms.append((category, coverage))
    
    print(f"\n[PRODUCTION READY] ({len(production_ready)} categories):")
    for cat in production_ready:
        types_count = len(PROJECT_TYPE_MAPPING[cat])
        print(f"  - {cat}: {types_count} project types")
    
    if needs_synonyms:
        print(f"\n[NEEDS SYNONYMS] ({len(needs_synonyms)} categories):")
        for cat, coverage in needs_synonyms:
            types_count = len(PROJECT_TYPE_MAPPING[cat])
            print(f"  - {cat}: {types_count} types, {coverage:.1f}% synonym coverage")
    
    if needs_project_types:
        print(f"\n[NEEDS PROJECT TYPES] ({len(needs_project_types)} categories):")
        for cat in needs_project_types:
            print(f"  - {cat}: No project types defined")
    
    # Special categories analysis
    print("\n" + "=" * 80)
    print("SPECIAL CATEGORIES ANALYSIS:")
    print("=" * 80)
    
    # Check categories with specific implementation needs
    special_categories = {
        "AI Solutions": "Needs AI-specific project types and capabilities",
        "Professional/Digital": "Needs business/tech service definitions",
        "Lifestyle & Wellness": "Needs health/comfort project mappings",
        "Events": "Needs one-time event service definitions",
        "Consultation": "Needs professional service mappings"
    }
    
    for category, notes in special_categories.items():
        if category in PROJECT_TYPE_MAPPING:
            count = len(PROJECT_TYPE_MAPPING[category])
            if count > 10:
                status = "[Well Defined]"
            elif count > 5:
                status = "[Partially Defined]"
            else:
                status = "[Under-Defined]"
            print(f"\n{category}:")
            print(f"  - Status: {status} ({count} types)")
            print(f"  - Notes: {notes}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY:")
    print("=" * 80)
    
    complete_categories = len(production_ready)
    total_categories = len(PROJECT_TYPE_MAPPING)
    completion_rate = (complete_categories / total_categories) * 100
    
    print(f"\n[Overall Completion]: {complete_categories}/{total_categories} ({completion_rate:.1f}%)")
    print(f"[Total Project Types]: {total_project_types}")
    print(f"[Average Types per Category]: {total_project_types/total_categories:.1f}")
    
    # Recommendations
    print("\n[RECOMMENDATIONS]:")
    if needs_synonyms:
        print("1. Add synonym mappings for categories with low coverage")
    if needs_project_types:
        print("2. Define project types for empty categories")
    if completion_rate < 80:
        print("3. Focus on completing partial categories before adding new ones")
    else:
        print(">>> System is mostly complete and ready for production use!")

if __name__ == "__main__":
    analyze_category_completeness()