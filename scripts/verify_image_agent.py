
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from google.adk.runners import Runner
from agent_platform.config import PlatformConfig
from tools.dashboard.services import ImageGenerationService

# Mock Dependencies
def get_runner():
    from agent_platform.main import create_app
    # minimal setup to get a runner
    app = create_app()
    # finding the image generator runner from the app or recreating it logic
    # easier to just use the factory directly if possible, or replicate:
    from google.adk.runners import Runner
    
    # We need to point to the agent config
    agent_path = Path("domains/course_creator/image_generator")
    if not agent_path.exists():
        raise FileNotFoundError(f"Agent path not found: {agent_path}")
        
    # We need a Runner configured for this agent
    # The dashboard dependency does:
    # app = core_create_app()
    # runner = app.get_runner("image_generator") 
    # But that might be heavy to load.
    
    # Let's try to use the dashboard dependency logic if we can mock the request context or just import
    from tools.dashboard.dependencies import get_image_generator_runner
    # This dependency might rely on a global app instance or similar? 
    # Let's check tools/dashboard/dependencies.py first.
    pass

# Direct approach
async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("verify_image_agent")
    
    try:
        from tools.dashboard.dependencies import get_image_generator_runner
        
        logger.info("Getting runner...")
        runner = get_image_generator_runner()
        
        service = ImageGenerationService(runner)
        
        logger.info("Starting generation...")
        image_path = await service.generate_image(
            user_id="verification_script",
            session_id="verify_1",
            prompt="A futuristic city with flying cars, neon lights, cyberpunk style",
            model="models/gemini-2.5-flash-image"
        )
        
        logger.info(f"Success! Image generated at: {image_path}")
        
    except Exception as e:
        logger.error(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
