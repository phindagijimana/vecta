"""
Few-Shot Example Loader for Vecta AI Prompt Engineering
Loads curated clinical examples and guidelines for enhanced prompt construction
"""

import json
import os
import random
from typing import List, Dict, Optional, Any
from pathlib import Path


class FewShotExampleLoader:
    """Loads and manages few-shot examples for prompt engineering"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the loader
        
        Args:
            data_dir: Path to data directory containing examples and guidelines
        """
        if data_dir is None:
            # Default to data/ directory in project root
            self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.examples_path = self.data_dir / "few_shot_examples.json"
        self.guidelines_path = self.data_dir / "guidelines" / "neurology_guidelines.json"
        
        self.examples = None
        self.guidelines = None
        
        # Load data on initialization
        self._load_examples()
        self._load_guidelines()
    
    def _load_examples(self):
        """Load few-shot examples from JSON file"""
        if self.examples_path.exists():
            with open(self.examples_path, 'r') as f:
                data = json.load(f)
                self.examples = data.get('neurology_few_shot_examples', {})
        else:
            print(f"Warning: Few-shot examples not found at {self.examples_path}")
            self.examples = {}
    
    def _load_guidelines(self):
        """Load clinical guidelines from JSON file"""
        if self.guidelines_path.exists():
            with open(self.guidelines_path, 'r') as f:
                self.guidelines = json.load(f)
        else:
            print(f"Warning: Guidelines not found at {self.guidelines_path}")
            self.guidelines = {}
    
    def get_examples_by_condition(
        self, 
        condition: str, 
        n: int = 2, 
        analysis_type: Optional[str] = None,
        random_selection: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get few-shot examples for a specific condition
        
        Args:
            condition: Condition type (epilepsy, parkinsons, stroke, headache, dementia)
            n: Number of examples to return
            analysis_type: Optional filter by analysis type (classification, diagnosis, etc.)
            random_selection: If True, randomly select examples; if False, return first n
        
        Returns:
            List of example dictionaries
        """
        if not self.examples or condition not in self.examples:
            return []
        
        examples = self.examples[condition]
        
        # Filter by analysis type if specified
        if analysis_type:
            examples = [e for e in examples if e.get('analysis_type') == analysis_type]
        
        # Select examples
        if len(examples) <= n:
            return examples
        
        if random_selection:
            return random.sample(examples, n)
        else:
            return examples[:n]
    
    def get_guideline_context(self, condition: str, subtopic: Optional[str] = None) -> str:
        """
        Get clinical guideline context for a condition
        
        Args:
            condition: Condition category (epilepsy, parkinsons, stroke, headache)
            subtopic: Optional specific subtopic within condition
        
        Returns:
            Formatted guideline text
        """
        if not self.guidelines:
            return ""
        
        guideline_key = f"{condition}_guidelines"
        if guideline_key not in self.guidelines:
            return ""
        
        guidelines = self.guidelines[guideline_key]
        
        # If subtopic specified, try to get that section
        if subtopic and subtopic in guidelines:
            content = guidelines[subtopic]
        else:
            # Return entire guideline for condition
            content = guidelines
        
        # Format as readable text
        return self._format_guideline_content(content, condition)
    
    def _format_guideline_content(self, content: Any, condition: str, indent: int = 0) -> str:
        """Recursively format guideline content as readable text"""
        if isinstance(content, dict):
            lines = []
            for key, value in content.items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, (dict, list)):
                    lines.append(f"{'  ' * indent}{formatted_key}:")
                    lines.append(self._format_guideline_content(value, condition, indent + 1))
                else:
                    lines.append(f"{'  ' * indent}{formatted_key}: {value}")
            return '\n'.join(lines)
        elif isinstance(content, list):
            return '\n'.join([f"{'  ' * indent}- {item}" for item in content])
        else:
            return f"{'  ' * indent}{content}"
    
    def format_few_shot_examples_for_prompt(
        self, 
        examples: List[Dict[str, Any]], 
        analysis_type: str
    ) -> str:
        """
        Format examples for inclusion in prompt
        
        Args:
            examples: List of example dictionaries
            analysis_type: Type of analysis (classification, diagnosis, etc.)
        
        Returns:
            Formatted string for prompt injection
        """
        if not examples:
            return ""
        
        formatted = "EXAMPLE ANALYSES:\n\n"
        
        for i, example in enumerate(examples, 1):
            formatted += f"Example {i}:\n"
            formatted += f"Input: {example['input']}\n\n"
            
            output = example['expected_output']
            formatted += "Analysis:\n"
            
            # Format based on what fields are present
            if 'classification' in output:
                formatted += f"- Classification: {output['classification']}\n"
            if 'diagnosis_support' in output:
                formatted += f"- Diagnosis Support: {output['diagnosis_support']}\n"
            if 'information_extraction' in output:
                formatted += f"- Information Extraction: {output['information_extraction']}\n"
            if 'clinical_summary' in output:
                formatted += f"- Clinical Summary: {output['clinical_summary']}\n"
            
            formatted += f"- Clinical_Confidence: {output.get('clinical_confidence', 'N/A')}\n"
            formatted += f"- Evidence: {output.get('evidence', 'N/A')}\n"
            formatted += f"- Medication_Analysis: {output.get('medication_analysis', 'N/A')}\n"
            formatted += "\n"
        
        return formatted
    
    def get_enhanced_prompt_context(
        self,
        condition: str,
        analysis_type: str,
        n_examples: int = 2,
        include_guidelines: bool = True
    ) -> Dict[str, str]:
        """
        Get complete enhanced context for prompt engineering
        
        Args:
            condition: Condition type
            analysis_type: Analysis type
            n_examples: Number of few-shot examples
            include_guidelines: Whether to include guideline context
        
        Returns:
            Dictionary with 'examples' and 'guidelines' keys
        """
        result = {}
        
        # Get few-shot examples
        examples = self.get_examples_by_condition(
            condition, 
            n=n_examples, 
            analysis_type=analysis_type
        )
        result['examples'] = self.format_few_shot_examples_for_prompt(examples, analysis_type)
        
        # Get guidelines
        if include_guidelines:
            result['guidelines'] = self.get_guideline_context(condition)
        else:
            result['guidelines'] = ""
        
        return result
    
    def list_available_conditions(self) -> List[str]:
        """List all available condition types"""
        return list(self.examples.keys()) if self.examples else []
    
    def get_example_statistics(self) -> Dict[str, int]:
        """Get statistics about available examples"""
        if not self.examples:
            return {}
        
        stats = {}
        for condition, examples in self.examples.items():
            stats[condition] = len(examples)
        stats['total'] = sum(stats.values())
        return stats


# Convenience function for quick access
def load_few_shot_examples(condition: str, n: int = 2, analysis_type: Optional[str] = None) -> List[Dict]:
    """
    Quick function to load few-shot examples
    
    Args:
        condition: Condition type
        n: Number of examples
        analysis_type: Optional filter by analysis type
    
    Returns:
        List of examples
    """
    loader = FewShotExampleLoader()
    return loader.get_examples_by_condition(condition, n, analysis_type)


def load_guidelines(condition: str) -> str:
    """
    Quick function to load guideline context
    
    Args:
        condition: Condition type
    
    Returns:
        Formatted guideline text
    """
    loader = FewShotExampleLoader()
    return loader.get_guideline_context(condition)


if __name__ == "__main__":
    # Test the loader
    loader = FewShotExampleLoader()
    
    print("=== Few-Shot Example Loader Test ===\n")
    print(f"Available conditions: {loader.list_available_conditions()}")
    print(f"\nExample statistics: {loader.get_example_statistics()}\n")
    
    # Test epilepsy examples
    print("=== Epilepsy Classification Examples ===")
    examples = loader.get_examples_by_condition('epilepsy', n=2, analysis_type='classification')
    formatted = loader.format_few_shot_examples_for_prompt(examples, 'classification')
    print(formatted)
    
    # Test guideline loading
    print("\n=== Epilepsy Guidelines ===")
    guidelines = loader.get_guideline_context('epilepsy', 'ilae_2025_classification')
    print(guidelines[:500] + "...\n")
    
    # Test enhanced context
    print("=== Enhanced Context for Stroke ===")
    context = loader.get_enhanced_prompt_context('stroke', 'diagnosis', n_examples=1)
    print("Examples length:", len(context['examples']))
    print("Guidelines length:", len(context['guidelines']))
