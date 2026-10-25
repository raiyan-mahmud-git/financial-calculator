"""Integration tests for Streamlit pages using streamlit.testing.v1.AppTest."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT_DIR = Path(__file__).resolve().parent.parent


class TestStreamlitApp:
    """Test suite ensuring all Streamlit views and interactive flows run cleanly."""

    def test_main_app_navigation(self):
        """Verify the main entrypoint initializes without exceptions."""
        at = AppTest.from_file(str(ROOT_DIR / "app.py"), default_timeout=10)
        at.run()
        assert not at.exception
        # Home page title
        assert len(at.title) >= 1
        assert "Financial" in at.title[0].value

    def test_mortgage_page_loads_and_calculates(self):
        """Verify mortgage calculator renders metrics and amortization schedule."""
        at = AppTest.from_file(str(ROOT_DIR / "views" / "mortgage.py"), default_timeout=10)
        at.run()
        assert not at.exception
        # Check that metric cards exist
        assert len(at.metric) >= 4
        # Check that dataframe schedule exists
        assert len(at.dataframe) >= 1

    def test_retirement_page_loads_and_simulates(self):
        """Verify retirement planner renders portfolio milestones."""
        at = AppTest.from_file(str(ROOT_DIR / "views" / "retirement.py"), default_timeout=10)
        at.run()
        assert not at.exception
        assert len(at.metric) >= 4
        assert len(at.dataframe) >= 1

    def test_growth_page_loads(self):
        """Verify compound growth view renders calculations."""
        at = AppTest.from_file(str(ROOT_DIR / "views" / "growth.py"), default_timeout=10)
        at.run()
        assert not at.exception
        assert len(at.metric) >= 3

    def test_doubling_page_loads(self):
        """Verify doubling time view calculates all three models."""
        at = AppTest.from_file(str(ROOT_DIR / "views" / "doubling.py"), default_timeout=10)
        at.run()
        assert not at.exception
        assert len(at.metric) >= 3

    def test_logarithms_page_solves(self):
        """Verify logarithm view solves equation without exceptions."""
        at = AppTest.from_file(str(ROOT_DIR / "views" / "logarithms.py"), default_timeout=10)
        at.run()
        assert not at.exception
        assert len(at.success) >= 1

    def test_scientific_notation_converts(self):
        """Verify scientific notation conversion page works."""
        at = AppTest.from_file(str(ROOT_DIR / "views" / "scientific.py"), default_timeout=10)
        at.run()
        assert not at.exception
        assert len(at.success) >= 1

    def test_ph_page_calculates_and_handles_invalid_input(self):
        """Verify pH calculator and error handling on invalid concentration."""
        at = AppTest.from_file(str(ROOT_DIR / "views" / "ph.py"), default_timeout=10)
        at.run()
        assert not at.exception
        assert len(at.metric) == 3

        # Simulate invalid input
        at.text_input(key="ph_text_box").input("-0.05").run()
        assert not at.exception
        # Error alert
        assert len(at.error) >= 1
