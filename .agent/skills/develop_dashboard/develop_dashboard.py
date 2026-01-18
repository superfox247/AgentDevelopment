import argparse
import logging
import sys
import os
import subprocess
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent.parent
DASHBOARD_DIR = ROOT_DIR / "tools" / "dashboard"
COMPONENTS_DIR = DASHBOARD_DIR / "src" / "components"

TEMPLATE = """import { useState } from 'react';
import { ArrowRight } from 'lucide-react';

export function {{ComponentName}}() {
    return (
        <div className="space-y-6">
            <div className="glass-panel p-6 rounded-xl">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white">{{ComponentName}}</h2>
                    <p className="text-gray-400">Description of {{ComponentName}} functionality.</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Example Card */}
                    <div className="glass-card p-5 rounded-xl border-l-2 border-l-indigo-500 relative overflow-hidden group">
                        <h3 className="text-lg font-semibold text-white mb-2">Feature Card</h3>
                        <p className="text-zinc-400 text-sm mb-4">Sample content for this component.</p>
                        <button className="flex items-center space-x-2 text-indigo-400 hover:text-indigo-300 transition-colors text-sm font-medium">
                            <span>Action</span>
                            <ArrowRight size={14} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default {{ComponentName}};
"""

def create_component(name):
    """Creates a new React component with standard styling."""
    if not COMPONENTS_DIR.exists():
        logger.error(f"Components directory not found: {COMPONENTS_DIR}")
        sys.exit(1)

    filename = f"{name}.jsx"
    file_path = COMPONENTS_DIR / filename
    
    if file_path.exists():
        logger.warning(f"Component {name} already exists at {file_path}")
        return

    content = TEMPLATE.replace("{{ComponentName}}", name)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"✅ Created component: {file_path}")
    except Exception as e:
        logger.error(f"Failed to create component: {e}")
        sys.exit(1)

def verify_dashboard():
    """Runs lint and build checks for the dashboard."""
    logger.info("🔍 Verifying Dashboard...")
    
    try:
        # 1. Lint
        logger.info("   Running ESLint...")
        subprocess.run(["npm", "run", "lint"], cwd=DASHBOARD_DIR, check=True, shell=True)
        
        # 2. Build
        logger.info("   Running Vite Build...")
        subprocess.run(["npm", "run", "build"], cwd=DASHBOARD_DIR, check=True, shell=True)
        
        logger.info("✅ Verification Passed: Dashboard is healthy.")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Verification Failed: {e}")
        sys.exit(1)

def develop_dashboard_action(args):
    if args.component:
        create_component(args.component)
    
    if args.verify:
        verify_dashboard()

    if not args.component and not args.verify:
        logger.info("No action specified. Use --component [Name] or --verify")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated skill for building and extending the Antigravity Dashboard.")
    
    parser.add_argument("--component", type=str, help="Name of the new component to create (e.g. SettingsView)")
    parser.add_argument("--verify", action="store_true", help="Run lint and build verification")
    
    args = parser.parse_args()
    
    develop_dashboard_action(args)
