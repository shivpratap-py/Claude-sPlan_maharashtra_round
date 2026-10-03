from typing import List, Dict, Any, Optional

class TestCase:
    def __init__(self, name: str, description: str, claim: str, 
                 mock_results: dict, expected_assessment: str,
                 expected_contradictions: list[str], category: str):
        self.name = name
        self.description = description
        self.claim = claim
        self.mock_results = mock_results  # simulated analyzer outputs
        self.expected_assessment = expected_assessment
        self.expected_contradictions = expected_contradictions
        self.category = category  # 'seen' or 'unseen_combination'

def get_test_cases() -> list[TestCase]:
    cases = []
    
    # Case 1: All Authentic
    cases.append(TestCase(
        name="Case 1: All Authentic",
        description="Authentic image and audio consistent with claim",
        claim="Meeting at the office on Monday in New York",
        mock_results={
            'image': {
                'modality': 'image', 'status': 'success', 'classification': 'likely_authentic',
                'fake_probability': 0.1, 'confidence': 0.8, 'evidence': ['No manipulation detected'],
                'metadata': {'dimensions': '1920x1080', 'creation_date': '2024-02-12', 'location': 'New York'},
                'error': None
            },
            'audio': {
                'modality': 'audio', 'status': 'success', 'classification': 'likely_authentic',
                'fake_probability': 0.1, 'confidence': 0.9, 'evidence': ['Natural voice patterns'],
                'transcript': 'Meeting at the office on Monday', 'language': 'en',
                'audio_info': {'duration': 30.0, 'sample_rate': 44100}, 'metadata': {}, 'error': None
            },
            'text': {
                'modality': 'text', 'status': 'success', 'classification': 'likely_authentic',
                'fake_probability': 0.05, 'confidence': 0.9, 'evidence': [],
                'extracted_text': 'Meeting at the office on Monday in New York',
                'entities': {'persons': [], 'locations': ['New York'], 'dates': ['Monday'], 'organizations': []},
                'metadata': {}, 'error': None
            }
        },
        expected_assessment="AUTHENTIC",
        expected_contradictions=[],
        category="seen"
    ))

    # Case 2: Manipulated Image + Authentic Audio
    cases.append(TestCase(
        name="Case 2: Manipulated Image + Authentic Audio",
        description="Image has strong synthetic indicators, but audio is authentic and matches claim",
        claim="Statement made in London yesterday",
        mock_results={
            'image': {
                'modality': 'image', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.85, 'confidence': 0.7, 'evidence': ['Image shows strong synthetic indicators'],
                'metadata': {'dimensions': '1024x1024', 'creation_date': '2024-02-10', 'software_detected': ['Stable Diffusion']},
                'error': None
            },
            'audio': {
                'modality': 'audio', 'status': 'success', 'classification': 'likely_authentic',
                'fake_probability': 0.1, 'confidence': 0.8, 'evidence': [],
                'transcript': 'Statement made in London yesterday', 'language': 'en',
                'audio_info': {'duration': 15.0, 'sample_rate': 44100}, 'metadata': {}, 'error': None
            }
        },
        expected_assessment="MANIPULATED",
        expected_contradictions=[],
        category="seen"
    ))

    # Case 3: Authentic Image + Synthetic Audio
    cases.append(TestCase(
        name="Case 3: Authentic Image + Synthetic Audio",
        description="Authentic image with claim matching image context, but audio is synthetic",
        claim="Press conference regarding new policy",
        mock_results={
            'image': {
                'modality': 'image', 'status': 'success', 'classification': 'likely_authentic',
                'fake_probability': 0.1, 'confidence': 0.8, 'evidence': [],
                'metadata': {'creation_date': '2024-03-01'}, 'error': None
            },
            'audio': {
                'modality': 'audio', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.75, 'confidence': 0.8, 'evidence': ['Unnatural prosody'],
                'transcript': 'We are changing the policy', 'language': 'en',
                'audio_info': {'duration': 10.0, 'sample_rate': 16000}, 'metadata': {}, 'error': None
            }
        },
        expected_assessment="MANIPULATED",
        expected_contradictions=[],
        category="seen"
    ))

    # Case 4: Both Manipulated (Coordinated)
    cases.append(TestCase(
        name="Case 4: Both Manipulated (Coordinated)",
        description="Image and Audio are manipulated. Metadata and location mismatch.",
        claim="Event in Paris on 2024-05-01",
        mock_results={
            'image': {
                'modality': 'image', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.8, 'confidence': 0.75, 'evidence': ['Deepfake artifacts in face'],
                'metadata': {'creation_date': '2024-01-01', 'location': 'Berlin'}, 'error': None
            },
            'audio': {
                'modality': 'audio', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.7, 'confidence': 0.8, 'evidence': ['AI generated voice'],
                'transcript': 'Welcome to our event in Berlin', 'language': 'en',
                'audio_info': {'duration': 20.0, 'sample_rate': 24000}, 'metadata': {}, 'error': None
            }
        },
        expected_assessment="COORDINATED SYNTHETIC",
        expected_contradictions=['location', 'date'],
        category="seen"
    ))

    # Case 5: Authentic Evidence + Conflicting Metadata
    cases.append(TestCase(
        name="Case 5: Authentic Evidence + Conflicting Metadata",
        description="Evidence authentic but temporal contradiction",
        claim="Event happened in 2026",
        mock_results={
            'image': {
                'modality': 'image', 'status': 'success', 'classification': 'likely_authentic',
                'fake_probability': 0.15, 'confidence': 0.9, 'evidence': [],
                'metadata': {'creation_date': '2024-10-01'}, 'error': None
            },
            'audio': {
                'modality': 'audio', 'status': 'success', 'classification': 'likely_authentic',
                'fake_probability': 0.1, 'confidence': 0.85, 'evidence': [],
                'transcript': 'Event happened', 'language': 'en',
                'audio_info': {'duration': 5.0, 'sample_rate': 44100}, 'metadata': {}, 'error': None
            }
        },
        expected_assessment="MANIPULATED",
        expected_contradictions=['date'],
        category="seen"
    ))

    # Case 6: Full Coordinated Manipulation
    cases.append(TestCase(
        name="Case 6: Full Coordinated Manipulation",
        description="Highly synthetic across all modalities, with extreme contradictions",
        claim="Event in Delhi, 2025 with John Doe",
        mock_results={
            'image': {
                'modality': 'image', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.9, 'confidence': 0.85, 'evidence': ['GAN artifacts'],
                'metadata': {'creation_date': '2024-05-05'}, 'error': None
            },
            'audio': {
                'modality': 'audio', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.8, 'confidence': 0.8, 'evidence': ['TTS artifacts'],
                'transcript': 'Welcome to Mumbai', 'language': 'en',
                'audio_info': {'duration': 40.0, 'sample_rate': 44100}, 'metadata': {}, 'error': None
            },
            'text': {
                'modality': 'text', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.8, 'confidence': 0.8, 'evidence': ['LLM generated'],
                'extracted_text': 'Mumbai event with Jane Doe',
                'entities': {'persons': ['Jane Doe'], 'locations': ['Mumbai'], 'dates': [], 'organizations': []},
                'metadata': {}, 'error': None
            }
        },
        expected_assessment="COORDINATED SYNTHETIC",
        expected_contradictions=['location', 'date', 'entity'],
        category="seen"
    ))

    # Case 7: Incomplete Evidence
    cases.append(TestCase(
        name="Case 7: Incomplete Evidence",
        description="Only low confidence image available",
        claim="Random claim",
        mock_results={
            'image': {
                'modality': 'image', 'status': 'success', 'classification': 'unavailable',
                'fake_probability': 0.5, 'confidence': 0.2, 'evidence': ['Too blurry'],
                'metadata': {}, 'error': None
            }
        },
        expected_assessment="INSUFFICIENT EVIDENCE",
        expected_contradictions=[],
        category="seen"
    ))

    # Case 8: Unseen Combination (held-out)
    cases.append(TestCase(
        name="Case 8: Unseen Combination",
        description="Manipulated image + synthetic audio + date conflict",
        claim="Event in 2025",
        mock_results={
            'image': {
                'modality': 'image', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.75, 'confidence': 0.7, 'evidence': ['Edited'],
                'metadata': {'creation_date': '2023-01-01'}, 'error': None
            },
            'audio': {
                'modality': 'audio', 'status': 'success', 'classification': 'suspicious',
                'fake_probability': 0.7, 'confidence': 0.75, 'evidence': ['Voice clone'],
                'transcript': 'Event in 2023', 'language': 'en',
                'audio_info': {'duration': 15.0, 'sample_rate': 44100}, 'metadata': {}, 'error': None
            }
        },
        expected_assessment="COORDINATED SYNTHETIC",
        expected_contradictions=['date'],
        category="unseen_combination"
    ))
    
    return cases
