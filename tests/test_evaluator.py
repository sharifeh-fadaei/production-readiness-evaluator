import pytest
from agents.target_agent import TargetAgent
from faults.taxonomy import FaultType
from faults.injector import FaultInjector
from faults.scenarios import FaultScenario, ExecutionLog, DetectionResult
from agents.detectors import DetectorSuite, HallucinationDetector, RoleConfusionDetector
from evaluator.runner import EvaluatorRunner
from evaluator.aggregator import MetricsAggregator
from evaluator.report_generator import ReportGenerator

class TestTargetAgent:
    """Test the target agent"""
    
    def test_agent_initialization(self):
        agent = TargetAgent()
        assert agent.name == "MultiAgentSystem"
    
    def test_agent_baseline_run(self):
        agent = TargetAgent()
        result = agent.run("What is Berlin?")
        assert result["status"] == "success"
        assert result["research_results"]
        assert result["analysis"]
        assert result["verification"]
    
    def test_agent_steps_executed(self):
        agent = TargetAgent()
        result = agent.run("What is Berlin?")
        assert "research" in result["steps_executed"]
        assert "analyze" in result["steps_executed"]
        assert "verify" in result["steps_executed"]

class TestFaultInjector:
    """Test fault injection"""
    
    def test_hallucination_injection(self):
        injector = FaultInjector(FaultType.HALLUCINATION)
        result = injector.inject("economic growth")
        assert "CORRUPTED" in result
        assert injector.injected is True
    
    def test_context_loss_injection(self):
        injector = FaultInjector(FaultType.CONTEXT_LOSS)
        text = "Line 1\nLine 2\nLine 3"
        result = injector.inject(text)
        assert len(result) < len(text)
    
    def test_role_ambiguity_injection(self):
        injector = FaultInjector(FaultType.ROLE_AMBIGUITY)
        result = injector.inject("researcher")
        assert "AND also" in result
    
    def test_message_cycle_injection(self):
        injector = FaultInjector(FaultType.MESSAGE_CYCLE)
        messages = ["msg1", "msg2"]
        result = injector.inject(messages)
        assert len(result) > len(messages)

class TestDetectors:
    """Test detection agents"""
    
    def test_hallucination_detector_positive(self):
        detector = HallucinationDetector()
        report = detector.detect("CORRUPTED data found")
        assert report.detected is True
        assert report.confidence > 0.5
    
    def test_hallucination_detector_negative(self):
        detector = HallucinationDetector()
        report = detector.detect("Normal economic growth")
        assert report.detected is False
    
    def test_role_confusion_detector_positive(self):
        detector = RoleConfusionDetector()
        report = detector.detect("researcher AND also be a critic")
        assert report.detected is True
    
    def test_role_confusion_detector_negative(self):
        detector = RoleConfusionDetector()
        report = detector.detect("researcher")
        assert report.detected is False
    
    def test_detector_suite_runs_all(self):
        suite = DetectorSuite()
        execution_log = {
            "final_output": "CORRUPTED analysis",
            "expected_output": "normal analysis",
            "steps_executed": ["research", "analyze", "verify"]
        }
        reports = suite.run_all(execution_log)
        assert len(reports) == 7
        assert "hallucination" in reports
        assert "role_confusion" in reports

class TestEvaluatorRunner:
    """Test the evaluation runner"""
    
    def test_baseline_run(self):
        agent = TargetAgent()
        runner = EvaluatorRunner(agent)
        baseline = runner.run_baseline("What is Berlin?")
        assert baseline["status"] == "success"
        assert baseline["baseline"] is True
    
    def test_fault_injection_run(self):
        agent = TargetAgent()
        runner = EvaluatorRunner(agent)
        logs = runner.run_with_fault(FaultType.HALLUCINATION, "What is Berlin?", num_runs=5)
        assert len(logs) == 5
        assert all(isinstance(log, ExecutionLog) for log in logs)
    
    def test_detection_metrics_calculation(self):
        agent = TargetAgent()
        runner = EvaluatorRunner(agent)
        logs = runner.run_with_fault(FaultType.HALLUCINATION, "What is Berlin?", num_runs=5)
        metrics = runner.calculate_detection_metrics(logs)
        assert metrics["total_runs"] == 5
        assert 0 <= metrics["detection_rate"] <= 1
        assert "hallucination" in metrics["per_detector"]

class TestAggregator:
    """Test the metrics aggregator"""
    
    def test_aggregator_initialization(self):
        agg = MetricsAggregator()
        assert len(agg.fault_metrics) == 0
    
    def test_aggregator_overall_score_empty(self):
        agg = MetricsAggregator()
        score = agg.calculate_overall_score()
        assert score == 0.0
    
    def test_aggregator_critical_risks(self):
        agg = MetricsAggregator()
        # Add mock metrics with low detection rate
        agg.fault_metrics[FaultType.HALLUCINATION] = {
            "detection_rate": 0.3,
            "recovery_success_rate": 0.0,
            "per_detector": {}
        }
        risks = agg.identify_critical_risks()
        assert len(risks) > 0
        assert risks[0]["fault_type"] == "hallucination"
    
    def test_aggregator_summary(self):
        agg = MetricsAggregator()
        agg.fault_metrics[FaultType.HALLUCINATION] = {
             "detection_rate": 0.95,
             "recovery_success_rate": 0.8,
             "critical_failures": 0,
             "per_detector": {}
        }
        summary = agg.get_summary()
        assert "overall_reliability_score" in summary
        assert "total_fault_types_tested" in summary
        assert "critical_risks" in summary

class TestReportGenerator:
    """Test report generation"""
    
    def test_report_generator_initialization(self):
        gen = ReportGenerator()
        assert gen.timestamp is not None
    
    def test_report_generation(self):
        gen = ReportGenerator()
        summary = {
            "overall_reliability_score": 85,
            "total_fault_types_tested": 2,
            "metrics_per_fault": {
                "hallucination": {
                    "detection_rate": 0.9,
                    "recovery_rate": 0.8,
                    "critical_failures": 0
                }
            },
            "critical_risks": []
        }
        report = gen.generate_report(summary)
        assert report["overall_reliability_score"] == 85
        assert report["production_ready"] is True
    
    def test_report_not_production_ready(self):
        gen = ReportGenerator()
        summary = {
            "overall_reliability_score": 60,
            "total_fault_types_tested": 1,
            "metrics_per_fault": {},
            "critical_risks": []
        }
        report = gen.generate_report(summary)
        assert report["production_ready"] is False
    
    def test_get_status_pass(self):
        gen = ReportGenerator()
        assert gen._get_status(0.95) == "✓ PASS"
    
    def test_get_status_warn(self):
        gen = ReportGenerator()
        assert gen._get_status(0.75) == "⚠ WARN"
    
    def test_get_status_fail(self):
        gen = ReportGenerator()
        assert gen._get_status(0.5) == "✗ FAIL"

class TestIntegration:
    """Integration tests for full pipeline"""
    
    def test_full_evaluation_pipeline(self):
        """Test the complete evaluation flow"""
        agent = TargetAgent()
        runner = EvaluatorRunner(agent)
        aggregator = MetricsAggregator()
        
        # Run baseline
        baseline = runner.run_baseline("Test query")
        assert baseline["status"] == "success"
        
        # Run fault injection
        logs = runner.run_with_fault(FaultType.HALLUCINATION, "Test query", num_runs=3)
        assert len(logs) == 3
        
        # Aggregate
        summary = aggregator.aggregate(logs)
        assert len(summary) > 0
        
        # Generate report
        report_gen = ReportGenerator()
        full_summary = aggregator.get_summary()
        report = report_gen.generate_report(full_summary)
        assert "overall_reliability_score" in report