from typing import List, Dict, Tuple

class AssessmentScorer:
    def __init__(self):
        # Style mapping from test metadata
        self.style_mapping = {
            "1": ["1A", "2D", "3C", "4B", "5C", "6B", "7A", "8C", "9C", "10B", "11A", "12C"],  # Stil 1 (Directiv)
            "2": ["1C", "2A", "3A", "4D", "5B", "6D", "7C", "8B", "9B", "10D", "11C", "12A"],  # Stil 2 (Persuasiv)
            "3": ["1B", "2C", "3D", "4A", "5D", "6A", "7B", "8D", "9D", "10A", "11B", "12D"],  # Stil 3 (Participativ)
            "4": ["1D", "2B", "3B", "4C", "5A", "6C", "7D", "8A", "9A", "10C", "11D", "12B"]   # Stil 4 (Delegativ)
        }
        
        # Adequacy mapping from test metadata
        self.adequacy_mapping = {
            "answers": {
                "a": ["1D", "2B", "3C", "4B", "5A", "6C", "7A", "8C", "9A", "10B", "11A", "12C"],
                "b": ["1B", "2D", "3B", "4D", "5D", "6A", "7C", "8B", "9D", "10C", "11C", "12A"],
                "c": ["1C", "2C", "3A", "4A", "5B", "6B", "7D", "8D", "9B", "10A", "11D", "12D"],
                "d": ["1A", "2A", "3D", "4C", "5C", "6D", "7B", "8A", "9C", "10D", "11B", "12B"]
            }
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
        
        # Calculate style scores
        for question, answer in responses.items():
            answer_key = f"{question}{answer}"
            for style, answers in self.style_mapping.items():
                if answer_key in answers:
                    style_counts[style] += 1
        
        # Sort styles by count and get primary and secondary styles
        sorted_styles = sorted(style_counts.items(), key=lambda x: (-x[1], x[0]))
        primary_style = self.style_names[sorted_styles[0][0]]
        secondary_style = self.style_names[sorted_styles[1][0]]
        
        return primary_style, secondary_style

    def get_all_style_scores(self, responses: List[Dict]) -> Dict[str, int]:
        style_scores = {
            "Directiv": 0,
            "Persuasiv": 0,
            "Participativ": 0,
            "Delegativ": 0
        }
        
        # Convert responses to the format needed for scoring
        response_dict = {r['question_id']: r['answer'] for r in responses}
        
        # Calculate points for each style
        for question, answer in response_dict.items():
            answer_key = f"{question}{answer}"
            for style_num, answers in self.style_mapping.items():
                if answer_key in answers:
                    style_scores[self.style_names[style_num]] += 1
        
        return style_scores

    def calculate_adequacy_score(self, responses: Dict[int, str]) -> Tuple[int, str]:
        total_score = 0
        
        for question, answer in responses.items():
            answer_key = f"{question}{answer}"
            
            # Find which adequacy category this answer belongs to
            for category, answers in self.adequacy_mapping["answers"].items():
                if answer_key in answers:
                    total_score += self.adequacy_coefficients[category]
                    break
        
        # Determine adequacy level based on score
        if total_score >= 20:
            level = "Excelent"
        elif total_score >= 10:
            level = "Bun"
        else:
            level = "Necesită dezvoltare"
            
        return total_score, level

    def get_style_description(self, style_name: str) -> str:
        style_descriptions = {
            "Directiv": "Stil orientat spre sarcini și control direct",
            "Persuasiv": "Stil orientat spre convingere și explicații",
            "Participativ": "Stil orientat spre colaborare și decizie comună",
            "Delegativ": "Stil orientat spre autonomie și delegare"
        }
        return style_descriptions.get(style_name, "")

    def get_adequacy_description(self, score: int) -> str:
        if score >= 20:
            return "Adaptabilitate foarte bună la context"
        elif score >= 10:
            return "Adaptabilitate moderată, cu potențial de dezvoltare"
        else:
            return "Adaptabilitate redusă, necesită îmbunătățire semnificativă"
