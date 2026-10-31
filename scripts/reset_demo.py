"""Emergency demo database reset script for CanopyAI.

Clears all analysis records from Supabase (or in-memory repository),
re-seeds 10 canonical demo analyses, and verifies repository state.
"""

import logging
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.cache_service import cache_service
from app.services.database_service import TABLE_NAME, database_service
from app.services.mock_service import mock_repository
from scripts.seed_demo_data import seed_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("canopyai.reset")


def reset_demo() -> bool:
    """Clear repository, invalidate caches, re-seed canonical analyses, and verify state."""
    logger.info("Initiating CanopyAI Emergency Demo Reset...")

    # 1. Clear database / in-memory store
    logger.info("[Step 1/4] Clearing repository records...")
    mock_repository.clear()

    if database_service.is_connected:
        try:
            # Delete records from Supabase analyses table
            database_service._supabase_client.table(TABLE_NAME).delete().neq("analysis_id", "0").execute()
            logger.info("  Supabase table '%s' purged successfully", TABLE_NAME)
        except Exception as e:
            logger.warning("  Could not truncate Supabase table (%s). In-memory repository cleared.", e)
    else:
        logger.info("  In-memory repository cleared.")

    # 2. Invalidate all performance caches
    logger.info("[Step 2/4] Clearing in-memory response caches...")
    cache_service.clear()

    # 3. Re-seed demo database
    logger.info("[Step 3/4] Re-seeding canonical demo analyses...")
    seeded_count = seed_database()

    # 4. Verify results
    logger.info("[Step 4/4] Verifying database state...")
    current_count = database_service.count_analyses()
    logger.info("  Total active analyses verified: %d", current_count)

    if current_count >= seeded_count:
        logger.info("DEMO RESET SUCCESSFUL: Database restored with %d clean analyses.", current_count)
        return True
    else:
        logger.warning("DEMO RESET INCOMPLETE: Expected >= %d analyses, found %d", seeded_count, current_count)
        return False


if __name__ == "__main__":
    success = reset_demo()
    sys.exit(0 if success else 1)

