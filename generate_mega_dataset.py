#!/usr/bin/env python3
"""
Ultra-high volume dataset generator WITHOUT deduplication.
Generates diverse sentences for large training datasets.
"""

import random
import sys
import os

def generate_ultra_large_dataset(target_mb=300):
    """Generate ultra-large dataset without deduplication."""
    
    print(f"\n{'='*70}")
    print(f"🚀 ULTRA-LARGE DATASET GENERATOR (Target: {target_mb}MB)")
    print(f"{'='*70}\n")
    
    output_file = 'examples/sample_text.txt'
    
    # Get current size
    current_size = 0
    if os.path.exists(output_file):
        current_size = os.path.getsize(output_file)
    
    print(f"Current size: {current_size / 1024 / 1024:.1f}MB")
    print(f"Target size: {target_mb}MB\n")
    
    # Rich domain knowledge
    domains = {
        "Artificial Intelligence": {
            "concepts": ["Deep Learning", "Machine Learning", "Neural Networks", "Natural Language Processing", "Computer Vision"],
            "techniques": ["Supervised Learning", "Unsupervised Learning", "Reinforcement Learning", "Transfer Learning", "Meta Learning"],
            "applications": ["Image Recognition", "Speech Recognition", "Text Classification", "Sentiment Analysis", "Machine Translation"],
            "frameworks": ["TensorFlow", "PyTorch", "Keras", "JAX", "MXNet"],
        },
        "Data Science": {
            "techniques": ["Data Mining", "Statistical Analysis", "Hypothesis Testing", "A/B Testing", "Regression Analysis"],
            "tools": ["Python", "R", "SQL", "Tableau", "Power BI"],
            "processes": ["Data Collection", "Data Cleaning", "Exploratory Analysis", "Feature Engineering", "Model Validation"],
            "applications": ["Predictive Analytics", "Customer Analytics", "Market Analysis", "Risk Analysis", "Anomaly Detection"],
        },
        "Cloud Computing": {
            "services": ["Compute", "Storage", "Networking", "Databases", "Machine Learning"],
            "providers": ["AWS", "Google Cloud", "Microsoft Azure", "IBM Cloud", "Oracle Cloud"],
            "architectures": ["Microservices", "Serverless", "Containerized", "Distributed", "Hybrid"],
            "benefits": ["Scalability", "Cost Efficiency", "Flexibility", "Reliability", "Security"],
        },
        "Software Development": {
            "methodologies": ["Agile", "Scrum", "Kanban", "Lean", "Waterfall"],
            "practices": ["Code Review", "Continuous Integration", "Continuous Deployment", "Test-Driven Development", "Pair Programming"],
            "languages": ["Python", "JavaScript", "Java", "C++", "Go"],
            "principles": ["DRY", "KISS", "SOLID", "Design Patterns", "Clean Code"],
        },
        "DevOps": {
            "tools": ["Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions"],
            "practices": ["Infrastructure as Code", "Automated Testing", "Continuous Monitoring", "Log Aggregation", "Performance Tuning"],
            "concepts": ["Containerization", "Orchestration", "Infrastructure Automation", "Configuration Management", "Monitoring"],
            "benefits": ["Faster Deployment", "Better Reliability", "Improved Collaboration", "Cost Reduction", "Enhanced Security"],
        },
    }
    
    # Diverse sentence templates
    templates = [
        "{concept} adalah fundamental dalam {domain}.",
        "{technique} digunakan untuk {application}.",
        "{tool} menyediakan {feature} yang powerful.",
        "Implementasi {concept} memerlukan {requirement}.",
        "{domain} berkembang dengan pesat berkat {innovation}.",
        "Perusahaan menggunakan {technique} untuk {goal}.",
        "{best_practice} adalah standar industri.",
        "Kombinasi dari {concept1} dan {concept2} menghasilkan {result}.",
        "Research menunjukkan bahwa {finding} signifikan.",
        "Best practice dalam {domain} adalah {practice}.",
        "{tool} telah merevolusi cara {activity}.",
        "Adopsi {technology} meningkatkan {metric} secara substantial.",
        "{methodology} membantu teams mencapai {objective}.",
        "Challenges dalam {domain} termasuk {challenge}.",
        "Solution untuk {problem} adalah implementasi {approach}.",
        "Industry leaders menggunakan {strategy} untuk {purpose}.",
        "{architecture} design memungkinkan {capability}.",
        "Integration dari {system1} dengan {system2} memberikan {benefit}.",
        "Evolution dari {technology} menciptakan opportunities baru.",
        "Future dari {domain} tergantung pada {factor}.",
    ]
    
    # Generate content
    lines_written = 0
    target_bytes = target_mb * 1024 * 1024
    
    with open(output_file, 'a', encoding='utf-8') as f:
        iteration = 0
        while current_size < target_bytes:
            iteration += 1
            
            # Create variations
            for domain, content in domains.items():
                for template in templates:
                    # Generate different variations
                    variations = []
                    if "concept" in template and "domain" in template:
                        for concept in content.get("concepts", []):
                            variations.append(template.format(concept=concept, domain=domain))
                    
                    if "technique" in template and "application" in template:
                        techs = content.get("techniques", [])
                        apps = content.get("applications", [])
                        for t in techs:
                            for a in apps:
                                variations.append(template.format(technique=t, application=a))
                    
                    if "tool" in template:
                        for tool in content.get("tools", content.get("frameworks", [])):
                            variations.append(template.format(tool=tool, feature="capabilities"))
                    
                    # Write lines
                    for v in variations:
                        f.write(v + '\n')
                        lines_written += 1
                        current_size += len(v.encode('utf-8')) + 1
            
            # Progress
            percent = (current_size / target_bytes) * 100
            print(f"[{iteration}] Progress: {current_size/1024/1024:.1f}MB / {target_mb}MB ({percent:.1f}%)", end='\r')
            
            if current_size >= target_bytes:
                break
    
    # Final stats
    final_size = os.path.getsize(output_file) / 1024 / 1024
    final_lines = sum(1 for _ in open(output_file, 'r', encoding='utf-8'))
    
    print(f"\n\n{'='*70}")
    print(f"✅ GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"""
📊 Final Dataset:
   ├─ File: {output_file}
   ├─ Size: {final_size:.1f}MB
   ├─ Lines: {final_lines:,}
   ├─ Avg line: {(final_size * 1024 / final_lines):.0f} bytes
   └─ Growth: {lines_written:,} lines added

🎓 Content Coverage:
   ├─ Artificial Intelligence & ML
   ├─ Data Science & Analytics  
   ├─ Cloud Computing
   ├─ Software Development
   └─ DevOps & Infrastructure

🚀 Training Recommendations:
   For quick test (15 min):
   python train.py --epochs 10 --batch 8 --config tiny

   For good results (1-2 hours):
   python train.py --epochs 30 --batch 4 --config default

   For production (with GPU, 4-6 hours):
   python train.py --epochs 50 --batch 8 --config 3b --deepspeed
""")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    target = 300
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
        except:
            pass
    
    generate_ultra_large_dataset(target)
