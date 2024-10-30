from typing import List, Dict, Tuple

class AssessmentScorer:
    def __init__(self):
        self.style_mapping = {
            "1": ["1A", "2D", "5C", "7A", "10B", "11A"],
            "2": ["2A", "3A", "6D", "8B", "9B", "12A"],
            "3": ["1B", "3D", "4A", "6A", "10A", "12D"],
            "4": ["1D", "2B", "4C", "5A", "8A", "11D"]
        }
        
        self.adequacy_coefficients = {
            "a": -2,
            "b": -1,
            "c": 1,
            "d": 2
        }

        self.style_names = {
            "1": "Directiv",
            "2": "Persuasiv",
            "3": "Participativ",
            "4": "Delegativ"
        }

    def calculate_style_scores(self, responses: Dict[int, str]) -> Tuple[str, str]:
        style_counts = {style: 0 for style in self.style_mapping.keys()}
        
        for question, answer in responses.items():
            answer_key = f"{question}{answer}"
            for style, answers in self.style_mapping.items():
                if answer_key in answers:
                    style_counts[style] += 1
        
        sorted_styles = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)
        primary_style = self.style_names[sorted_styles[0][0]]
        secondary_style = self.style_names[sorted_styles[1][0]]
        
        return primary_style, secondary_style

    def calculate_adequacy_score(self, responses: Dict[int, str]) -> Tuple[int, str]:
        total_score = sum(self.adequacy_coefficients[answer.lower()] 
                         for answer in responses.values())
        
        if total_score >= 20:
            level = "Excelent"
        elif total_score >= 10:
            level = "Bun"
        else:
            level = "Necesită dezvoltare"
            
        return total_score, level
