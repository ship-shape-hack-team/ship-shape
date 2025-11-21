"""Unit tests for data models."""

from datetime import datetime
from pathlib import Path

import pytest

from agentready.models.assessment import Assessment
from agentready.models.attribute import Attribute
from agentready.models.config import Config
from agentready.models.finding import Citation, Finding, Remediation
from agentready.models.repository import Repository


class TestRepository:
    """Test Repository model."""

    def test_repository_creation(self, tmp_path):
        """Test creating a valid repository."""
        # Create a fake git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        repo = Repository(
            path=tmp_path,
            name="test-repo",
            url="https://github.com/test/repo",
            branch="main",
            commit_hash="abc123",
            languages={"Python": 10},
            total_files=15,
            total_lines=500,
        )

        assert repo.name == "test-repo"
        assert repo.total_files == 15
        assert "Python" in repo.languages

    def test_repository_invalid_path(self):
        """Test repository with invalid path."""
        with pytest.raises(ValueError, match="does not exist"):
            Repository(
                path=Path("/nonexistent"),
                name="test",
                url=None,
                branch="main",
                commit_hash="abc",
                languages={},
                total_files=0,
                total_lines=0,
            )

    def test_repository_to_dict(self, tmp_path):
        """Test repository serialization."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        repo = Repository(
            path=tmp_path,
            name="test",
            url=None,
            branch="main",
            commit_hash="abc123",
            languages={"Python": 5},
            total_files=10,
            total_lines=200,
        )

        data = repo.to_dict()
        assert data["name"] == "test"
        assert data["languages"] == {"Python": 5}


class TestAttribute:
    """Test Attribute model."""

    def test_attribute_creation(self):
        """Test creating a valid attribute."""
        attr = Attribute(
            id="test_attr",
            name="Test Attribute",
            category="Testing",
            tier=1,
            description="A test attribute",
            criteria="Must pass test",
            default_weight=0.10,
        )

        assert attr.id == "test_attr"
        assert attr.tier == 1
        assert attr.default_weight == 0.10

    def test_attribute_invalid_tier(self):
        """Test attribute with invalid tier."""
        with pytest.raises(ValueError, match="Tier must be"):
            Attribute(
                id="test",
                name="Test",
                category="Test",
                tier=5,  # Invalid
                description="Test",
                criteria="Test",
                default_weight=0.10,
            )

    def test_attribute_invalid_weight(self):
        """Test attribute with invalid weight."""
        with pytest.raises(ValueError, match="weight must be"):
            Attribute(
                id="test",
                name="Test",
                category="Test",
                tier=1,
                description="Test",
                criteria="Test",
                default_weight=1.5,  # Invalid
            )


class TestFinding:
    """Test Finding model."""

    def test_finding_pass(self):
        """Test creating a passing finding."""
        attr = Attribute(
            id="test",
            name="Test",
            category="Test",
            tier=1,
            description="Test",
            criteria="Test",
            default_weight=0.10,
        )

        finding = Finding(
            attribute=attr,
            status="pass",
            score=100.0,
            measured_value="present",
            threshold="present",
            evidence=["File found"],
            remediation=None,
            error_message=None,
        )

        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_finding_fail_with_remediation(self):
        """Test creating a failing finding with remediation."""
        attr = Attribute(
            id="test",
            name="Test",
            category="Test",
            tier=1,
            description="Test",
            criteria="Test",
            default_weight=0.10,
        )

        remediation = Remediation(
            summary="Fix the issue",
            steps=["Step 1", "Step 2"],
            tools=["tool1"],
            commands=["command1"],
            examples=["example1"],
            citations=[],
        )

        finding = Finding(
            attribute=attr,
            status="fail",
            score=0.0,
            measured_value="missing",
            threshold="present",
            evidence=["File not found"],
            remediation=remediation,
            error_message=None,
        )

        assert finding.status == "fail"
        assert finding.remediation is not None
        assert len(finding.remediation.steps) == 2

    def test_finding_invalid_status(self):
        """Test finding with invalid status."""
        attr = Attribute(
            id="test",
            name="Test",
            category="Test",
            tier=1,
            description="Test",
            criteria="Test",
            default_weight=0.10,
        )

        with pytest.raises(ValueError, match="Status must be"):
            Finding(
                attribute=attr,
                status="invalid",  # Invalid status
                score=50.0,
                measured_value="test",
                threshold="test",
                evidence=[],
                remediation=None,
                error_message=None,
            )


class TestConfig:
    """Test Config model."""

    def test_config_creation(self):
        """Test creating a valid config."""
        config = Config(
            weights={"attr1": 0.5, "attr2": 0.5},
            excluded_attributes=[],
            language_overrides={},
            output_dir=None,
        )

        assert len(config.weights) == 2
        assert config.get_weight("attr1", 0.0) == 0.5

    def test_config_invalid_weights_sum(self):
        """Test config with weights that don't sum to 1.0."""
        with pytest.raises(ValueError, match="sum to 1.0"):
            Config(
                weights={"attr1": 0.3, "attr2": 0.3},  # Only sums to 0.6
                excluded_attributes=[],
                language_overrides={},
                output_dir=None,
            )

    def test_config_is_excluded(self):
        """Test excluded attribute check."""
        config = Config(
            weights={},
            excluded_attributes=["attr1"],
            language_overrides={},
            output_dir=None,
        )

        assert config.is_excluded("attr1")
        assert not config.is_excluded("attr2")


class TestAssessment:
    """Test Assessment model."""

    def test_assessment_creation(self, tmp_path):
        """Test creating a valid assessment."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        repo = Repository(
            path=tmp_path,
            name="test",
            url=None,
            branch="main",
            commit_hash="abc",
            languages={},
            total_files=10,
            total_lines=100,
        )

        # Create dummy findings to match total
        attr = Attribute(
            id="test",
            name="Test",
            category="Test",
            tier=1,
            description="Test",
            criteria="Test",
            default_weight=0.04,
        )
        findings = [
            Finding(
                attribute=attr,
                status="pass",
                score=100.0,
                measured_value="test",
                threshold="test",
                evidence=[],
                remediation=None,
                error_message=None,
            )
            for _ in range(25)
        ]

        assessment = Assessment(
            repository=repo,
            timestamp=datetime.now(),
            overall_score=75.0,
            certification_level="Gold",
            attributes_assessed=20,
            attributes_skipped=5,
            attributes_total=25,
            findings=findings,
            config=None,
            duration_seconds=1.5,
        )

        assert assessment.overall_score == 75.0
        assert assessment.certification_level == "Gold"

    def test_assessment_determine_certification(self):
        """Test certification level determination."""
        assert Assessment.determine_certification_level(95.0) == "Platinum"
        assert Assessment.determine_certification_level(80.0) == "Gold"
        assert Assessment.determine_certification_level(65.0) == "Silver"
        assert Assessment.determine_certification_level(45.0) == "Bronze"
        assert Assessment.determine_certification_level(20.0) == "Needs Improvement"
