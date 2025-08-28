#!/usr/bin/env python3
"""
System Verification Script
Comprehensive verification of all system components
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

class SystemVerifier:
    def __init__(self):
        self.results = {
            'prerequisites': {},
            'python_setup': {},
            'docker': {},
            'kubernetes': {},
            'application': {},
            'overall': 'PENDING'
        }
        
    def run_command(self, command, capture_output=True):
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True, 
                timeout=30
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout.strip() if result.stdout else '',
                'stderr': result.stderr.strip() if result.stderr else '',
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def check_prerequisites(self):
        """Check if all prerequisites are installed"""
        print("🔍 Checking Prerequisites...")
        
        # Check Python
        python_result = self.run_command('python3 --version')
        self.results['prerequisites']['python'] = {
            'status': '✅' if python_result['success'] else '❌',
            'version': python_result['stdout'] if python_result['success'] else 'Not found',
            'details': python_result
        }
        
        # Check Docker
        docker_result = self.run_command('docker --version')
        self.results['prerequisites']['docker'] = {
            'status': '✅' if docker_result['success'] else '❌',
            'version': docker_result['stdout'] if docker_result['success'] else 'Not found',
            'details': docker_result
        }
        
        # Check kubectl
        kubectl_result = self.run_command('kubectl version --client')
        self.results['prerequisites']['kubectl'] = {
            'status': '✅' if kubectl_result['success'] else '❌',
            'version': kubectl_result['stdout'].split('\n')[0] if kubectl_result['success'] else 'Not found',
            'details': kubectl_result
        }
        
        # Check Minikube
        minikube_result = self.run_command('minikube version')
        self.results['prerequisites']['minikube'] = {
            'status': '✅' if minikube_result['success'] else '❌',
            'version': minikube_result['stdout'] if minikube_result['success'] else 'Not found',
            'details': minikube_result
        }
        
        # Check Git
        git_result = self.run_command('git --version')
        self.results['prerequisites']['git'] = {
            'status': '✅' if git_result['success'] else '❌',
            'version': git_result['stdout'] if git_result['success'] else 'Not found',
            'details': git_result
        }
        
        # Check GitHub CLI
        gh_result = self.run_command('gh --version')
        self.results['prerequisites']['github_cli'] = {
            'status': '✅' if gh_result['success'] else '❌',
            'version': gh_result['stdout'].split('\n')[0] if gh_result['success'] else 'Not found',
            'details': gh_result
        }
    
    def check_python_setup(self):
        """Check Python environment and dependencies"""
        print("🐍 Checking Python Setup...")
        
        # Check virtual environment
        venv_path = Path('venv')
        if venv_path.exists():
            self.results['python_setup']['virtual_env'] = {
                'status': '✅',
                'details': f'Virtual environment found at {venv_path.absolute()}'
            }
        else:
            self.results['python_setup']['virtual_env'] = {
                'status': '❌',
                'details': 'Virtual environment not found'
            }
        
        # Check requirements.txt
        req_path = Path('requirements.txt')
        if req_path.exists():
            self.results['python_setup']['requirements'] = {
                'status': '✅',
                'details': f'Requirements file found with {len(req_path.read_text().splitlines())} dependencies'
            }
        else:
            self.results['python_setup']['requirements'] = {
                'status': '❌',
                'details': 'Requirements file not found'
            }
        
        # Check if dependencies can be imported
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
            
            # Test imports
            from celery_app import app
            from metrics import metrics
            from custom_metrics_adapter import app as metrics_app
            
            self.results['python_setup']['imports'] = {
                'status': '✅',
                'details': 'All application modules imported successfully'
            }
        except ImportError as e:
            self.results['python_setup']['imports'] = {
                'status': '❌',
                'details': f'Import error: {e}'
            }
        except Exception as e:
            self.results['python_setup']['imports'] = {
                'status': '❌',
                'details': f'Unexpected error: {e}'
            }
    
    def check_docker(self):
        """Check Docker status and images"""
        print("🐳 Checking Docker...")
        
        # Check Docker daemon
        docker_status = self.run_command('docker ps')
        self.results['docker']['daemon'] = {
            'status': '✅' if docker_status['success'] else '❌',
            'details': 'Docker daemon running' if docker_status['success'] else 'Docker daemon not accessible'
        }
        
        # Check if we can build images
        if docker_status['success']:
            # Check if images exist
            celery_image = self.run_command('docker images | grep celery-autoscaling')
            metrics_image = self.run_command('docker images | grep custom-metrics-adapter')
            
            self.results['docker']['celery_image'] = {
                'status': '✅' if celery_image['success'] else '❌',
                'details': 'Celery image found' if celery_image['success'] else 'Celery image not built'
            }
            
            self.results['docker']['metrics_image'] = {
                'status': '✅' if metrics_image['success'] else '❌',
                'details': 'Metrics adapter image found' if metrics_image['success'] else 'Metrics adapter image not built'
            }
        else:
            self.results['docker']['celery_image'] = {'status': '❌', 'details': 'Docker not accessible'}
            self.results['docker']['metrics_image'] = {'status': '❌', 'details': 'Docker not accessible'}
    
    def check_kubernetes(self):
        """Check Kubernetes cluster status"""
        print("☸️  Checking Kubernetes...")
        
        # Check cluster status
        cluster_status = self.run_command('kubectl cluster-info')
        self.results['kubernetes']['cluster'] = {
            'status': '✅' if cluster_status['success'] else '❌',
            'details': 'Cluster accessible' if cluster_status['success'] else 'Cluster not accessible'
        }
        
        if cluster_status['success']:
            # Check nodes
            nodes = self.run_command('kubectl get nodes')
            self.results['kubernetes']['nodes'] = {
                'status': '✅' if nodes['success'] else '❌',
                'details': nodes['stdout'] if nodes['success'] else 'Cannot get nodes'
            }
            
            # Check if deployments exist
            deployments = self.run_command('kubectl get deployments')
            self.results['kubernetes']['deployments'] = {
                'status': '✅' if deployments['success'] else '❌',
                'details': deployments['stdout'] if deployments['success'] else 'Cannot get deployments'
            }
            
            # Check if services exist
            services = self.run_command('kubectl get services')
            self.results['kubernetes']['services'] = {
                'status': '✅' if services['success'] else '❌',
                'details': services['stdout'] if services['success'] else 'Cannot get services'
            }
            
            # Check if HPA exists
            hpa = self.run_command('kubectl get hpa')
            self.results['kubernetes']['hpa'] = {
                'status': '✅' if hpa['success'] else '❌',
                'details': hpa['stdout'] if hpa['success'] else 'Cannot get HPA'
            }
        else:
            self.results['kubernetes']['nodes'] = {'status': '❌', 'details': 'Cluster not accessible'}
            self.results['kubernetes']['deployments'] = {'status': '❌', 'details': 'Cluster not accessible'}
            self.results['kubernetes']['services'] = {'status': '❌', 'details': 'Cluster not accessible'}
            self.results['kubernetes']['hpa'] = {'status': '❌', 'details': 'Cluster not accessible'}
    
    def check_application(self):
        """Check application components"""
        print("🚀 Checking Application...")
        
        # Check file structure
        required_files = [
            'app/celery_app.py',
            'app/metrics.py',
            'app/worker.py',
            'app/task_submitter.py',
            'app/custom_metrics_adapter.py',
            'k8s/redis-deployment.yaml',
            'k8s/celery-worker-deployment.yaml',
            'k8s/custom-metrics-adapter.yaml',
            'k8s/hpa.yaml',
            'Dockerfile',
            'Dockerfile.metrics-adapter',
            'deploy.sh',
            'README.md',
            'ANALYSIS_REPORT.md'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.results['application']['files'] = {
                'status': '❌',
                'details': f'Missing files: {", ".join(missing_files)}'
            }
        else:
            self.results['application']['files'] = {
                'status': '✅',
                'details': f'All {len(required_files)} required files present'
            }
        
        # Check if deployment script is executable
        deploy_script = Path('deploy.sh')
        if deploy_script.exists() and os.access(deploy_script, os.X_OK):
            self.results['application']['deploy_script'] = {
                'status': '✅',
                'details': 'Deployment script is executable'
            }
        else:
            self.results['application']['deploy_script'] = {
                'status': '❌',
                'details': 'Deployment script not executable or missing'
            }
    
    def generate_report(self):
        """Generate comprehensive system report"""
        print("\n" + "="*60)
        print("📊 SYSTEM VERIFICATION REPORT")
        print("="*60)
        
        # Prerequisites
        print("\n🔍 PREREQUISITES:")
        for tool, info in self.results['prerequisites'].items():
            print(f"  {tool.title():<15} {info['status']} {info['version']}")
        
        # Python Setup
        print("\n🐍 PYTHON SETUP:")
        for component, info in self.results['python_setup'].items():
            print(f"  {component.replace('_', ' ').title():<20} {info['status']}")
            if 'details' in info:
                print(f"    └─ {info['details']}")
        
        # Docker
        print("\n🐳 DOCKER:")
        for component, info in self.results['docker'].items():
            print(f"  {component.replace('_', ' ').title():<20} {info['status']}")
            if 'details' in info:
                print(f"    └─ {info['details']}")
        
        # Kubernetes
        print("\n☸️  KUBERNETES:")
        for component, info in self.results['kubernetes'].items():
            print(f"  {component.title():<15} {info['status']}")
            if 'details' in info and len(info['details']) < 100:
                print(f"    └─ {info['details']}")
        
        # Application
        print("\n🚀 APPLICATION:")
        for component, info in self.results['application'].items():
            print(f"  {component.replace('_', ' ').title():<20} {info['status']}")
            if 'details' in info:
                print(f"    └─ {info['details']}")
        
        # Overall Status
        print("\n" + "="*60)
        self._calculate_overall_status()
        print(f"OVERALL STATUS: {self.results['overall']}")
        print("="*60)
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        self._generate_recommendations()
    
    def _calculate_overall_status(self):
        """Calculate overall system status"""
        all_checks = []
        
        for category in ['prerequisites', 'python_setup', 'docker', 'kubernetes', 'application']:
            for component, info in self.results[category].items():
                if info['status'] == '✅':
                    all_checks.append(True)
                else:
                    all_checks.append(False)
        
        success_rate = sum(all_checks) / len(all_checks) if all_checks else 0
        
        if success_rate >= 0.9:
            self.results['overall'] = '🟢 EXCELLENT'
        elif success_rate >= 0.7:
            self.results['overall'] = '🟡 GOOD'
        elif success_rate >= 0.5:
            self.results['overall'] = '🟠 FAIR'
        else:
            self.results['overall'] = '🔴 NEEDS ATTENTION'
    
    def _generate_recommendations(self):
        """Generate recommendations based on check results"""
        recommendations = []
        
        # Check prerequisites
        if self.results['prerequisites']['minikube']['status'] == '❌':
            recommendations.append("Install Minikube: brew install minikube")
        
        if self.results['prerequisites']['docker']['status'] == '❌':
            recommendations.append("Install Docker Desktop")
        
        # Check Python setup
        if self.results['python_setup']['virtual_env']['status'] == '❌':
            recommendations.append("Create virtual environment: python3 -m venv venv")
        
        if self.results['python_setup']['imports']['status'] == '❌':
            recommendations.append("Install dependencies: pip install -r requirements.txt")
        
        # Check Docker
        if self.results['docker']['celery_image']['status'] == '❌':
            recommendations.append("Build Docker images: docker build -t celery-autoscaling:latest .")
        
        # Check Kubernetes
        if self.results['kubernetes']['cluster']['status'] == '❌':
            recommendations.append("Start Minikube: minikube start --cpus=4 --memory=8192")
        
        if not recommendations:
            recommendations.append("🎉 System is ready for deployment!")
            recommendations.append("Run: ./deploy.sh")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    def run_all_checks(self):
        """Run all system checks"""
        print("🚀 Starting System Verification...")
        print("This will check all components of the Celery Task Queue Autoscaling System")
        print()
        
        self.check_prerequisites()
        self.check_python_setup()
        self.check_docker()
        self.check_kubernetes()
        self.check_application()
        
        self.generate_report()
        
        return self.results

def main():
    """Main function"""
    verifier = SystemVerifier()
    results = verifier.run_all_checks()
    
    # Save results to file
    with open('system_verification_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: system_verification_report.json")
    
    return 0 if results['overall'] in ['🟢 EXCELLENT', '🟡 GOOD'] else 1

if __name__ == '__main__':
    sys.exit(main())
