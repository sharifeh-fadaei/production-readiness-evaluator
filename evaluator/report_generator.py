from typing import Dict, Any, List
import json
from datetime import datetime

class ReportGenerator:
    """Generates production readiness reports"""
    
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
    
    def generate_report(self, summary: Dict[str, Any], system_name: str = "Target Agent System") -> Dict[str, Any]:
        """Generate full production readiness report"""
        
        overall_score = summary["overall_reliability_score"]
        production_ready = overall_score >= 80
        
        report = {
            "timestamp": self.timestamp,
            "system_name": system_name,
            "overall_reliability_score": overall_score,
            "production_ready": production_ready,
            "evaluation_summary": {
                "total_fault_types_tested": summary["total_fault_types_tested"],
                "status": "READY" if production_ready else "NOT READY"
            },
            "results_per_fault_type": {},
            "critical_risks": summary["critical_risks"],
            "recommendations": self._generate_recommendations(summary),
        }
        
        # Add detailed results per fault type
        for fault_name, metrics in summary["metrics_per_fault"].items():
            detection_rate = metrics["detection_rate"]
            status = self._get_status(detection_rate)
            
            report["results_per_fault_type"][fault_name] = {
                "detection_rate": round(detection_rate * 100, 1),
                "recovery_success_rate": round(metrics["recovery_rate"] * 100, 1),
                "critical_failures": metrics["critical_failures"],
                "status": status,
                "threshold": 80
            }
        
        return report
    
    def _get_status(self, detection_rate: float) -> str:
        """Determine status based on detection rate"""
        if detection_rate >= 0.90:
            return "✓ PASS"
        elif detection_rate >= 0.70:
            return "⚠ WARN"
        else:
            return "✗ FAIL"
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        risks = summary["critical_risks"]
        
        for i, risk in enumerate(risks, 1):
            fault_type = risk["fault_type"]
            detection_rate = risk["detection_rate"]
            
            if detection_rate < 0.3:
                recommendations.append(f"Priority {i}: Add robust detection for {fault_type}")
            elif detection_rate < 0.7:
                recommendations.append(f"Priority {i}: Improve {fault_type} detection accuracy")
        
        if summary["overall_reliability_score"] < 80:
            recommendations.append("Overall: System is not production-ready. Address critical risks first.")
        else:
            recommendations.append("Overall: System meets production readiness criteria.")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save report to JSON file"""
        if filename is None:
            filename = f"results/production_readiness_{self.timestamp.replace(':', '-')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename
    
    def print_report(self, report: Dict[str, Any]) -> None:
        """Print report in readable format"""
        print("\n" + "="*70)
        print("PRODUCTION READINESS REPORT")
        print("="*70)
        print(f"\nSystem: {report['system_name']}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"\nOVERALL RELIABILITY SCORE: {report['overall_reliability_score']}%")
        print(f"PRODUCTION READY: {report['production_ready']}")
        
        print("\n" + "-"*70)
        print("RESULTS BY FAULT TYPE")
        print("-"*70)
        
        for fault_type, metrics in report["results_per_fault_type"].items():
            status = metrics["status"]
            detection = metrics["detection_rate"]
            print(f"\n{fault_type.upper()}: {status}")
            print(f"  Detection Rate: {detection}%")
            print(f"  Recovery Rate: {metrics['recovery_success_rate']}%")
            print(f"  Critical Failures: {metrics['critical_failures']}")
        
        print("\n" + "-"*70)
        print("CRITICAL RISKS")
        print("-"*70)
        
        if report["critical_risks"]:
            for risk in report["critical_risks"]:
                print(f"\n⚠️  {risk['fault_type'].upper()}")
                print(f"   Issue: {risk['issue']}")
                print(f"   Recommendation: {risk['recommendation']}")
        else:
            print("\nNo critical risks identified.")
        
        print("\n" + "-"*70)
        print("RECOMMENDATIONS")
        print("-"*70)
        for rec in report["recommendations"]:
            print(f"• {rec}")
        
        print("\n" + "="*70 + "\n")