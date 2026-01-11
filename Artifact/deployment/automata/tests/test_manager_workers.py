import asyncio
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from automata.core.manager import EnterpriseManager


def test_manager_workers_start_stop():
    import os
    os.environ['AI_PROVIDER'] = 'dummy'
    mgr = EnterpriseManager()
    # Provide minimal valid configuration for tests
    mgr.config.set("business.name", "Test Business")
    mgr.config.set("dashboard.admin_password", "testpassword")

    # Shorten worker intervals for test responsiveness
    if mgr.editorial_worker:
        mgr.editorial_worker.interval = 0.1
    if mgr.publish_worker:
        mgr.publish_worker.interval = 0.1

    # Start manager (this will start content generator and workers)
    asyncio.run(mgr.start())

    # Wait briefly for worker threads to spin up
    import time
    end = time.time() + 1.0
    while time.time() < end:
        if mgr.editorial_worker and mgr.editorial_worker._thread and mgr.editorial_worker._thread.is_alive():
            break
        time.sleep(0.05)

    # Workers should be present and started
    assert hasattr(mgr, 'editorial_worker')
    assert hasattr(mgr, 'publish_worker')
    if mgr.editorial_worker:
        assert mgr.editorial_worker._thread and mgr.editorial_worker._thread.is_alive()
    if mgr.publish_worker:
        assert mgr.publish_worker._thread and mgr.publish_worker._thread.is_alive()

    # Stop manager
    asyncio.run(mgr.stop())

    # Wait for threads to stop
    end = time.time() + 1.0
    while time.time() < end:
        alive = False
        if mgr.editorial_worker and mgr.editorial_worker._thread and mgr.editorial_worker._thread.is_alive():
            alive = True
        if mgr.publish_worker and mgr.publish_worker._thread and mgr.publish_worker._thread.is_alive():
            alive = True
        if not alive:
            break
        time.sleep(0.05)

    if mgr.editorial_worker:
        assert not (mgr.editorial_worker._thread and mgr.editorial_worker._thread.is_alive())
    if mgr.publish_worker:
        assert not (mgr.publish_worker._thread and mgr.publish_worker._thread.is_alive())
