"""Evaluation harness: runs predefined test cases through the reasoning pipeline."""

from evaluation.test_cases import TestCase, get_test_cases
from evaluation.metrics import MetricsCalculator


class Evaluator:
    def __init__(self):
        try:
            from reasoning.consistency_engine import ConsistencyEngine
            from reasoning.evidence_fusion import EvidenceFusion
            from reasoning.confidence import ConfidenceEstimator
            from reasoning.explanation import ExplanationGenerator
            self.consistency_engine = ConsistencyEngine()
            self.fusion = EvidenceFusion()
            self.confidence = ConfidenceEstimator()
            self.explanation = ExplanationGenerator()
        except ImportError:
            self.consistency_engine = None
            self.fusion = None
            self.confidence = None
            self.explanation = None
        self.metrics = MetricsCalculator()

    def run_test_case(self, test_case: TestCase) -> dict:
        """Run a single test case through the reasoning pipeline."""
        if self.fusion is None or self.consistency_engine is None:
            return {
                'name': test_case.name,
                'test_case': test_case.name,
                'passed': False,
                'expected': test_case.expected_assessment,
                'predicted': 'PIPELINE UNAVAILABLE',
                'fusion_result': {},
                'explanation': {},
            }

        # Run consistency engine with claim + simulated analyzer outputs
        consistency_report = self.consistency_engine.analyze_consistency(
            test_case.claim, test_case.mock_results
        )

        # Run evidence fusion
        fused = self.fusion.fuse_evidence(test_case.mock_results, consistency_report)

        # Run confidence estimation
        confidence = self.confidence.estimate(
            test_case.mock_results, consistency_report, fused
        )

        # Generate explanation
        explanation = self.explanation.generate(
            test_case.mock_results, consistency_report, fused, confidence
        )

        predicted_assessment = fused.get('assessment', 'INSUFFICIENT EVIDENCE')
        passed = (predicted_assessment == test_case.expected_assessment)

        return {
            'name': test_case.name,
            'test_case': test_case.name,
            'passed': passed,
            'expected': test_case.expected_assessment,
            'predicted': predicted_assessment,
            'fusion_result': fused,
            'consistency': consistency_report,
            'confidence': confidence,
            'explanation': explanation,
        }

    def run_all_tests(self) -> dict:
        """Run all test cases and compute metrics."""
        cases = get_test_cases()
        results, predictions, ground_truths = [], [], []
        seen_preds, seen_gts, unseen_results = [], [], []

        for case in cases:
            res = self.run_test_case(case)
            results.append(res)
            predictions.append(res['predicted'])
            ground_truths.append(res['expected'])

            if case.category == 'seen':
                seen_preds.append(res['predicted'])
                seen_gts.append(res['expected'])
            else:
                unseen_results.append(res)

        metrics_all = self.metrics.calculate_metrics(predictions, ground_truths)
        seen_metrics = self.metrics.calculate_metrics(seen_preds, seen_gts)

        summary = (
            f"Evaluated {len(cases)} test cases. "
            f"Overall Accuracy: {metrics_all.get('accuracy', 0.0):.2f}"
        )

        return {
            'total_cases': len(cases),
            'results': results,
            'metrics': metrics_all,
            'seen_metrics': seen_metrics,
            'unseen_results': unseen_results,
            'summary': summary,
        }

    def run_generalization_test(self) -> dict:
        """Run only the unseen combination test cases."""
        cases = [c for c in get_test_cases() if c.category == 'unseen_combination']
        results, predictions, ground_truths = [], [], []

        for case in cases:
            res = self.run_test_case(case)
            results.append(res)
            predictions.append(res['predicted'])
            ground_truths.append(res['expected'])

        metrics = self.metrics.calculate_metrics(predictions, ground_truths)

        return {
            'type': 'Generalization Prototype Evaluation',
            'total_cases': len(cases),
            'results': results,
            'metrics': metrics,
            'summary': (
                f"Generalization test on {len(cases)} unseen cases. "
                f"Accuracy: {metrics.get('accuracy', 0.0):.2f}"
            ),
        }
