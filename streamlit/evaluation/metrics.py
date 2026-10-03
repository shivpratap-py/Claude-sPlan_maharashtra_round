import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

class MetricsCalculator:
    ASSESSMENT_LABELS = ['AUTHENTIC', 'MANIPULATED', 'COORDINATED SYNTHETIC', 'INSUFFICIENT EVIDENCE']
    
    def calculate_metrics(self, predictions: list[str], ground_truths: list[str]) -> dict:
        labels = self.ASSESSMENT_LABELS
        if not predictions or not ground_truths:
            return {
                'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0,
                'confusion_matrix': [], 'per_class_metrics': {}, 'total_cases': 0, 'correct': 0
            }
            
        acc = accuracy_score(ground_truths, predictions)
        prec = precision_score(ground_truths, predictions, labels=labels, average='macro', zero_division=0)
        rec = recall_score(ground_truths, predictions, labels=labels, average='macro', zero_division=0)
        f1 = f1_score(ground_truths, predictions, labels=labels, average='macro', zero_division=0)
        cm = confusion_matrix(ground_truths, predictions, labels=labels)
        
        per_class_metrics = {}
        prec_per = precision_score(ground_truths, predictions, labels=labels, average=None, zero_division=0)
        rec_per = recall_score(ground_truths, predictions, labels=labels, average=None, zero_division=0)
        f1_per = f1_score(ground_truths, predictions, labels=labels, average=None, zero_division=0)
        
        for i, label in enumerate(labels):
            per_class_metrics[label] = {
                'precision': float(prec_per[i]),
                'recall': float(rec_per[i]),
                'f1': float(f1_per[i])
            }
            
        return {
            'accuracy': float(acc),
            'precision': float(prec),
            'recall': float(rec),
            'f1': float(f1),
            'confusion_matrix': cm.tolist(),
            'per_class_metrics': per_class_metrics,
            'total_cases': len(predictions),
            'correct': int(np.sum(np.array(predictions) == np.array(ground_truths)))
        }

    def format_confusion_matrix(self, cm: list[list[int]], labels: list[str]) -> str:
        """Return formatted text confusion matrix"""
        if not cm: return "Empty Confusion Matrix"
        res = "Confusion Matrix:\n"
        res += f"{'True \ Predicted':<25} | " + " | ".join(f"{l[:10]:<10}" for l in labels) + "\n"
        res += "-" * (28 + 13 * len(labels)) + "\n"
        for i, row in enumerate(cm):
            res += f"{labels[i]:<25} | " + " | ".join(f"{str(x):<10}" for x in row) + "\n"
        return res
    
    def create_confusion_matrix_figure(self, cm: list[list[int]], labels: list[str]):
        """Return Plotly heatmap of confusion matrix with dark theme"""
        if go is None:
            return None
        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=labels,
            y=labels,
            colorscale='Viridis'
        ))
        fig.update_layout(
            title='Confusion Matrix',
            xaxis_title='Predicted Label',
            yaxis_title='True Label',
            template='plotly_dark'
        )
        return fig
