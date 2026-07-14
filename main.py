from agents.target_agent import TargetAgent
from evaluator.runner import EvaluatorRunner
from evaluator.aggregator import MetricsAggregator
from evaluator.report_generator import ReportGenerator
from faults.taxonomy import FaultType

def main():
    """Run complete evaluation pipeline"""
    
    print("\n" + "="*70)
    print("PRODUCTION READINESS EVALUATOR")
    print("="*70)
    
    # Initialize components
    target_agent = TargetAgent(name="Research-Analyzer-Verifier")
    runner = EvaluatorRunner(target_agent)
    aggregator = MetricsAggregator()
    report_gen = ReportGenerator()
    
    # Test task
    task = "What is the population of Berlin?"
    
    print(f"\nTarget System: {target_agent.name}")
    print(f"Test Task: {task}")
    
    # Step 1: Run baseline (no faults)
    print("\n" + "-"*70)
    print("STEP 1: Baseline (no faults)")
    print("-"*70)
    baseline = runner.run_baseline(task)
    print(f"Baseline status: {baseline['status']}")
    print(f"Baseline output: {baseline['verification'][:80]}...")
    
    # Step 2: Run fault injections
    print("\n" + "-"*70)
    print("STEP 2: Fault Injection & Detection")
    print("-"*70)
    
    fault_types_to_test = [
    FaultType.HALLUCINATION,
    FaultType.PARAMETER_ERROR,
    FaultType.CONTEXT_LOSS,
    FaultType.ROLE_AMBIGUITY,
    FaultType.BLIND_TRUST,
    FaultType.INSTRUCTION_CONFLICT,
    FaultType.INEXECUTABLE_PLAN,
    FaultType.MESSAGE_CYCLE,
]
    
    all_logs = []
    for fault_type in fault_types_to_test:
        print(f"\nTesting {fault_type.value}...")
        logs = runner.run_with_fault(fault_type, task, num_runs=10)
        metrics = runner.calculate_detection_metrics(logs)
        
        detection_rate = metrics["detection_rate"] * 100
        print(f"  → Detection rate: {detection_rate:.0f}%")
        print(f"  → Detected: {metrics['detected']}/{metrics['total_runs']}")
        
        all_logs.extend(logs)
    
    # Step 3: Aggregate results
    print("\n" + "-"*70)
    print("STEP 3: Aggregation & Analysis")
    print("-"*70)
    summary = aggregator.aggregate(all_logs)
    overall_score = aggregator.calculate_overall_score()
    print(f"Overall Reliability Score: {overall_score}%")
    
    # Step 4: Generate report
    print("\n" + "-"*70)
    print("STEP 4: Report Generation")
    print("-"*70)
    
    full_summary = aggregator.get_summary()
    report = report_gen.generate_report(full_summary, system_name=target_agent.name)
    
    # Print and save report
    report_gen.print_report(report)
    
    filename = report_gen.save_report(report)
    print(f"Report saved to: {filename}")
    
    return report

if __name__ == "__main__":
    main()