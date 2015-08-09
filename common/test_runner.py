from django.test.runner import DiscoverRunner

# No DB destroy
class VTSkipDBRunner(DiscoverRunner):
    """
    A Django test runner that skip test db create and discovery.
    """
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        return super(VTSkipDBRunner, self).run_tests(test_labels=test_labels, extra_tests=extra_tests, **kwargs)

    def setup_databases(self, **kwargs):
        return None

    def teardown_databases(self, old_config, **kwargs):
        """
        Skip destroys all the non-mirror databases.
        """
        pass