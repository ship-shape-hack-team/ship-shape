"""API documentation completeness assessor for quality profiling."""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

from ...models.attribute import Attribute
from ...models.finding import Finding
from ...models.repository import Repository
from ..base import BaseAssessor


class APIDocumentationAssessor(BaseAssessor):
    """Assess API documentation completeness and quality."""

    @property
    def attribute_id(self) -> str:
        return "quality_api_documentation"

    @property
    def tier(self) -> int:
        return 1  # Critical

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="API Documentation Completeness",
            category="Documentation",
            tier=self.tier,
            description="OpenAPI/Swagger specs, endpoint documentation, request/response schemas",
            criteria="API spec present with 80%+ endpoints documented",
            default_weight=0.15,
        )

    def assess(self, repository: Repository) -> Finding:
        """Assess API documentation for the repository.

        Args:
            repository: Repository to assess

        Returns:
            Finding with API documentation metrics and score
        """
        try:
            repo_path = Path(repository.path)

            # Look for API specification files
            api_specs = self._find_api_specs(repo_path)

            if not api_specs:
                # Check if this repo likely has an API
                has_api_code = self._has_api_code(repo_path)
                
                if has_api_code:
                    return Finding(
                        attribute=self.attribute,
                        status="fail",
                        score=0,
                        measured_value=0,
                        threshold=80,
                        evidence=["API code detected but no API specification found"],
                        remediation="Add OpenAPI/Swagger specification. Use tools like swagger-jsdoc, fastapi (auto-generates), or manually create openapi.yaml",
                        error_message=None,
                    )
                else:
                    # Not an API project, skip
                    return Finding(
                        attribute=self.attribute,
                        status="skipped",
                        score=0,
                        measured_value=0,
                        threshold=80,
                        evidence=["No API code detected - not applicable"],
                        remediation="N/A - Repository does not appear to be an API project",
                        error_message=None,
                    )

            # Analyze API spec quality
            spec_analysis = self._analyze_api_spec(api_specs[0])
            score = self._calculate_score(spec_analysis)
            evidence_str = self._format_evidence(spec_analysis, api_specs[0])
            remediation_str = self._generate_remediation(spec_analysis)

            if score >= 80:
                return Finding(
                    attribute=self.attribute,
                    status="pass",
                    score=score,
                    measured_value=score,
                    threshold=80,
                    evidence=[evidence_str],
                    remediation=remediation_str,
                    error_message=None,
                )
            else:
                return Finding(
                    attribute=self.attribute,
                    status="fail",
                    score=score,
                    measured_value=score,
                    threshold=80,
                    evidence=[evidence_str],
                    remediation=remediation_str,
                    error_message=None,
                )

        except Exception as e:
            return Finding.error(
                attribute=self.attribute,
                reason=f"API documentation assessment failed: {str(e)}"
            )

    def _find_api_specs(self, repo_path: Path) -> List[Path]:
        """Find API specification files (OpenAPI/Swagger)."""
        spec_patterns = [
            "**/openapi.yaml",
            "**/openapi.yml",
            "**/openapi.json",
            "**/swagger.yaml",
            "**/swagger.yml",
            "**/swagger.json",
            "**/api-spec.yaml",
            "**/api-spec.yml",
            "**/api.yaml",
            "**/api.yml",
            "**/docs/openapi*.yaml",
            "**/docs/swagger*.yaml",
            "**/specs/openapi*.yaml",
        ]

        found_specs = []
        for pattern in spec_patterns:
            found_specs.extend(repo_path.glob(pattern))

        return found_specs

    def _has_api_code(self, repo_path: Path) -> bool:
        """Detect if repository contains API code."""
        api_indicators = [
            # Python API frameworks
            ("**/*.py", ["fastapi", "flask", "django.urls", "@app.route", "@router.", "APIRouter"]),
            # JavaScript/TypeScript API frameworks
            ("**/*.js", ["express", "app.get(", "app.post(", "router.get(", "router.post("]),
            ("**/*.ts", ["express", "@Get(", "@Post(", "@Controller(", "NestJS"]),
            # Go API frameworks
            ("**/*.go", ["http.HandleFunc", "gin.Engine", "mux.Router", "chi.Router"]),
            # Java API frameworks
            ("**/*.java", ["@RestController", "@RequestMapping", "@GetMapping", "@PostMapping"]),
        ]

        for pattern, keywords in api_indicators:
            for file in list(repo_path.glob(pattern))[:20]:  # Sample first 20 files
                try:
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    if any(keyword in content for keyword in keywords):
                        return True
                except Exception:
                    continue

        return False

    def _analyze_api_spec(self, spec_path: Path) -> Dict[str, Any]:
        """Analyze API specification file."""
        try:
            # Load spec file
            content = spec_path.read_text(encoding='utf-8')
            
            if spec_path.suffix == '.json':
                spec_data = json.loads(content)
            else:  # YAML
                spec_data = yaml.safe_load(content)

            if not spec_data:
                return {"error": "Empty or invalid spec file"}

            # Extract metrics
            analysis = {
                "spec_format": "OpenAPI 3.x" if spec_data.get("openapi", "").startswith("3") else "Swagger 2.0",
                "has_info": bool(spec_data.get("info")),
                "has_servers": bool(spec_data.get("servers")),
                "endpoint_count": 0,
                "documented_endpoints": 0,
                "has_schemas": False,
                "has_auth": False,
                "has_examples": False,
            }

            # Count endpoints
            paths = spec_data.get("paths", {})
            analysis["endpoint_count"] = sum(
                len([m for m in methods.keys() if m in ["get", "post", "put", "patch", "delete"]])
                for methods in paths.values() if isinstance(methods, dict)
            )

            # Check documented endpoints (have description)
            for path, methods in paths.items():
                if isinstance(methods, dict):
                    for method, details in methods.items():
                        if method in ["get", "post", "put", "patch", "delete"]:
                            if isinstance(details, dict) and (details.get("description") or details.get("summary")):
                                analysis["documented_endpoints"] += 1

            # Check for schemas/components
            schemas = spec_data.get("components", {}).get("schemas", {}) or spec_data.get("definitions", {})
            analysis["has_schemas"] = len(schemas) > 0
            analysis["schema_count"] = len(schemas)

            # Check for authentication
            auth_methods = spec_data.get("components", {}).get("securitySchemes", {}) or spec_data.get("securityDefinitions", {})
            analysis["has_auth"] = len(auth_methods) > 0

            # Check for examples
            for path, methods in paths.items():
                if isinstance(methods, dict):
                    for method, details in methods.items():
                        if isinstance(details, dict):
                            responses = details.get("responses", {})
                            for response in responses.values():
                                if isinstance(response, dict) and ("examples" in response or "example" in response):
                                    analysis["has_examples"] = True
                                    break
                        if analysis["has_examples"]:
                            break
                if analysis["has_examples"]:
                    break

            return analysis

        except Exception as e:
            return {"error": f"Failed to parse spec: {str(e)}"}

    def _calculate_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate score based on API documentation quality."""
        if "error" in analysis:
            return 0

        score = 0

        # Spec exists (20 points)
        score += 20

        # Has basic info section (10 points)
        if analysis.get("has_info"):
            score += 10

        # Endpoints documented (40 points max)
        if analysis.get("endpoint_count", 0) > 0:
            doc_ratio = analysis.get("documented_endpoints", 0) / analysis.get("endpoint_count", 1)
            score += doc_ratio * 40

        # Has schemas/components (15 points)
        if analysis.get("has_schemas"):
            score += 15

        # Has authentication documented (10 points)
        if analysis.get("has_auth"):
            score += 10

        # Has examples (5 points)
        if analysis.get("has_examples"):
            score += 5

        return min(100, score)

    def _format_evidence(self, analysis: Dict[str, Any], spec_path: Path) -> str:
        """Format evidence string."""
        if "error" in analysis:
            return f"Spec file found but invalid: {analysis['error']}"

        parts = [
            f"Spec: {spec_path.name} ({analysis.get('spec_format', 'Unknown')})",
            f"Endpoints: {analysis.get('documented_endpoints', 0)}/{analysis.get('endpoint_count', 0)} documented",
        ]

        if analysis.get("has_schemas"):
            parts.append(f"Schemas: {analysis.get('schema_count', 0)} defined")

        if analysis.get("has_auth"):
            parts.append("✓ Auth documented")

        if analysis.get("has_examples"):
            parts.append("✓ Examples included")

        return " | ".join(parts)

    def _generate_remediation(self, analysis: Dict[str, Any]) -> str:
        """Generate remediation advice."""
        if "error" in analysis:
            return f"Fix API specification: {analysis['error']}"

        issues = []

        # Check documentation completeness
        endpoint_count = analysis.get("endpoint_count", 0)
        documented_count = analysis.get("documented_endpoints", 0)
        
        if endpoint_count > 0:
            doc_ratio = documented_count / endpoint_count
            if doc_ratio < 0.8:
                issues.append(f"Document all endpoints (currently {documented_count}/{endpoint_count})")

        if not analysis.get("has_schemas"):
            issues.append("Add request/response schemas to components/definitions section")

        if not analysis.get("has_auth"):
            issues.append("Document authentication methods if API requires auth")

        if not analysis.get("has_examples"):
            issues.append("Add request/response examples for better clarity")

        if not issues:
            return "Excellent API documentation. Consider adding more examples and keeping spec up to date."

        return "; ".join(issues)
