#!/usr/bin/env python3
"""
GeoIdenti SDK - Image URL Pipeline Demo
========================================

Full biometric identity pipeline using only the GeoIdenti SDK client.
Reads a sidecar of public image URLs and optional identity metadata from
integration/sample_images.json, then runs four sequential passes:

  1. Analyze   — submit each URL to POST /v1/analyze
  2. Label     — assign explicit identity labels for sidecar-tagged entries
  3. Propagate — spread labels to similar unlabeled vectors (post-processing pass)
  4. Search    — validate labeled identities appear in filter search results
  5. Hybrid    — face-vector + semantic search using the first stored embedding
  6. Summary   — table of image_url → city → identity_name → vector_id

Requirements:
  pip install geoidenti-sdk

Auth:
  Admin-level API key required (label + propagate steps need admin role).
  export GEOIDENTI_API_KEY="<your-admin-jwt>"
  export GEOIDENTI_BASE_URL="http://localhost:8000/v1"  # optional

Usage:
  python3 integration/image_url_demo.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from geoidenti_sdk import GeoIdenti

SIDECAR_PATH = Path(__file__).resolve().parent / "sample_images.json"


class ImageUrlDemo:
    """Full pipeline demo driven entirely by the GeoIdenti SDK."""

    def __init__(self):
        self._require_env()
        api_key = os.environ["GEOIDENTI_API_KEY"]
        base_url = os.environ.get("GEOIDENTI_BASE_URL", "https://api.geoidenti.com/v1")
        self.client = GeoIdenti(api_key=api_key, base_url=base_url)
        self.sample_images: List[Dict[str, Any]] = self._load_sample_images()
        # Populated by run_analyze_pass(); consumed by later passes.
        # Each entry: {image_url, identity_name, vector_id, face_vector, city, country,
        #              inferred_identity, relationship, optional_search_field_1}
        self.results: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _require_env():
        if not os.environ.get("GEOIDENTI_API_KEY"):
            print(
                "\n❌  GEOIDENTI_API_KEY is not set.\n"
                "\n"
                "   Export your admin JWT before running:\n"
                "     export GEOIDENTI_API_KEY=\"<your-admin-jwt>\"\n"
                "     export GEOIDENTI_BASE_URL=\"http://localhost:8000/v1\"  # if not using production\n"
            )
            sys.exit(1)

    def _load_sample_images(self) -> List[Dict[str, Any]]:
        if not SIDECAR_PATH.exists():
            print(
                f"\n❌  Sidecar not found: {SIDECAR_PATH}\n"
                "   Expected integration/sample_images.json alongside this script.\n"
            )
            sys.exit(1)
        with open(SIDECAR_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        print(f"📋 Loaded {len(data)} entr{'y' if len(data) == 1 else 'ies'} from sample_images.json")
        return data

    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")

    # ------------------------------------------------------------------
    # Pass 1 — Analyze
    # ------------------------------------------------------------------

    def run_analyze_pass(self):
        self.print_header("Pass 1 — Analyze Images")
        print(f"Submitting {len(self.sample_images)} URL(s) to POST /v1/analyze...\n")

        for i, entry in enumerate(self.sample_images, 1):
            url = entry["image_url"]
            identity_name: Optional[str] = entry.get("identity_name")
            relationship: Optional[str] = entry.get("relationship")
            optional_search_field_1: Optional[str] = entry.get("optional_search_field_1")

            print(f"🔍 [{i}/{len(self.sample_images)}] {url}")
            try:
                result = self.client.analyze(
                    url,
                    identity_name=identity_name,
                    relationship=relationship,
                    optional_search_field_1=optional_search_field_1,
                )
                loc = result.get("location", {})
                city = loc.get("city", "n/a")
                country = loc.get("country", "n/a")
                vector_id = result.get("vector_id", "")
                face_vector = result.get("face_vector")
                inferred = result.get("inferred_identity", False)

                print(f"   ✅ vector_id:        {vector_id or 'n/a'}")
                print(f"   📍 city:             {city}")
                print(f"   📍 country:          {country}")
                print(f"   🔍 inferred_identity: {inferred}")

                self.results.append({
                    "image_url": url,
                    "identity_name": identity_name,
                    "relationship": relationship,
                    "optional_search_field_1": optional_search_field_1,
                    "vector_id": vector_id,
                    "face_vector": face_vector,
                    "city": city,
                    "country": country,
                    "inferred_identity": inferred,
                })
            except Exception as exc:
                print(f"   ❌ Analyze failed: {exc}")
                self.results.append({
                    "image_url": url,
                    "identity_name": identity_name,
                    "relationship": relationship,
                    "optional_search_field_1": optional_search_field_1,
                    "vector_id": None,
                    "face_vector": None,
                    "city": "n/a",
                    "country": "n/a",
                    "inferred_identity": False,
                    "error": str(exc),
                })

        stored = sum(1 for r in self.results if r.get("vector_id"))
        print(f"\n📊 Analyze complete — {stored}/{len(self.sample_images)} vector(s) stored.")

    # ------------------------------------------------------------------
    # Pass 2 — Label
    # ------------------------------------------------------------------

    def run_label_pass(self):
        self.print_header("Pass 2 — Label Identities")
        labeled = [r for r in self.results if r.get("identity_name") and r.get("vector_id")]

        if not labeled:
            print("⚠️  No sidecar-labeled entries with a stored vector_id — skipping label pass.")
            return

        print(f"Applying explicit labels for {len(labeled)} vector(s)...\n")
        for r in labeled:
            try:
                result = self.client.label_identity(r["vector_id"], r["identity_name"])
                print(f"✅ {r['vector_id']} → '{r['identity_name']}'  ({result})")
            except Exception as exc:
                print(f"❌ label_identity failed for {r['vector_id']}: {exc}")

    # ------------------------------------------------------------------
    # Pass 3 — Propagation (post-processing pass)
    # ------------------------------------------------------------------

    def run_propagation_pass(self):
        self.print_header("Pass 3 — Propagation Pass")
        labeled = [r for r in self.results if r.get("identity_name") and r.get("image_url")]

        if not labeled:
            print("⚠️  No labeled entries available for propagation — skipping.")
            return

        print(
            f"Propagating labels from {len(labeled)} source image(s) to similar vectors...\n"
            "  similarity_threshold=0.85, dry_run=False\n"
        )

        for r in labeled:
            try:
                result = self.client.propagate_from_image(
                    r["image_url"],
                    r["identity_name"],
                    relationship=r.get("relationship"),
                    optional_search_field_1=r.get("optional_search_field_1"),
                    similarity_threshold=0.85,
                    dry_run=False,
                )
                updated_count = result.get("updated_count", 0)
                conflicts = result.get("conflicts", [])
                threshold_used = result.get("threshold_used", 0.85)

                status = "✅" if updated_count > 0 else "ℹ️ "
                print(f"{status} '{r['identity_name']}' — updated_count={updated_count}, "
                      f"threshold={threshold_used}")
                if conflicts:
                    print(f"   ⚠️  conflicts: {conflicts}")
            except Exception as exc:
                print(f"❌ propagate_from_image failed for '{r['identity_name']}': {exc}")

    # ------------------------------------------------------------------
    # Pass 4 — Search Validation
    # ------------------------------------------------------------------

    def run_search_validation(self):
        self.print_header("Pass 4 — Search Validation")
        labeled_names = sorted({
            r["identity_name"]
            for r in self.results
            if r.get("identity_name") and r.get("vector_id")
        })

        if not labeled_names:
            print("⚠️  No labeled identities to validate — skipping.")
            return

        print(f"Validating {len(labeled_names)} labeled identity/identities via GET /v1/search...\n")
        for name in labeled_names:
            try:
                results = self.client.search(identity_name=name, limit=10)
                if results:
                    print(f"✅ '{name}' — {len(results)} result(s) returned")
                    header = f"   {'city':<16} {'confidence':<10} image_url"
                    print(header)
                    print(f"   {'-'*16} {'-'*10} {'-'*40}")
                    for item in results:
                        print(
                            f"   {item.get('city', ''):<16} "
                            f"{str(item.get('confidence', '')):<10} "
                            f"{item.get('image_url', '')}"
                        )
                else:
                    print(f"⚠️  '{name}' — no results returned. The engine may need a moment to index.")
            except Exception as exc:
                print(f"❌ search failed for '{name}': {exc}")

    # ------------------------------------------------------------------
    # Pass 5 — Hybrid Search
    # ------------------------------------------------------------------

    def run_hybrid_search_demo(self):
        self.print_header("Pass 5 — Hybrid Face + Semantic Search")
        first = next((r for r in self.results if r.get("face_vector")), None)
        if not first:
            print("⚠️  No face_vector available from analyze pass — skipping hybrid search.")
            return

        print(f"Source vector from: {first['image_url']}")
        print("semantic_query='family outdoor', limit=5\n")
        try:
            results = self.client.search_vector(
                face_vector=first["face_vector"],
                semantic_query="family outdoor",
                limit=5,
            )
            print(f"✅ {len(results)} result(s)\n")
            if results:
                header = f"  {'identity_name':<22} {'city':<16} {'confidence':<10} image_url"
                print(header)
                print(f"  {'-'*22} {'-'*16} {'-'*10} {'-'*40}")
                for r in results:
                    print(
                        f"  {r.get('identity_name', ''):<22} "
                        f"{r.get('city', ''):<16} "
                        f"{str(r.get('confidence', '')):<10} "
                        f"{r.get('image_url', '')}"
                    )
        except Exception as exc:
            print(f"❌ search_vector failed: {exc}")

    # ------------------------------------------------------------------
    # Pass 6 — Summary
    # ------------------------------------------------------------------

    def print_summary(self):
        self.print_header("Summary")
        print(f"  {'image_url':<45} {'city':<16} {'identity_name':<22} vector_id")
        print(f"  {'-'*45} {'-'*16} {'-'*22} {'-'*36}")
        for r in self.results:
            url_short = r["image_url"].split("?")[0].split("/")[-1]
            url_display = r["image_url"][:43] + ".." if len(r["image_url"]) > 45 else r["image_url"]
            print(
                f"  {url_display:<45} "
                f"{r.get('city', 'n/a'):<16} "
                f"{(r.get('identity_name') or '—'):<22} "
                f"{r.get('vector_id') or '—'}"
            )

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self):
        print("🚀 GeoIdenti SDK — Image URL Pipeline Demo")
        print("=" * 60)
        print("Admin-level full pipeline:")
        print("  1. Analyze all 6 sample URLs")
        print("  2. Label sidecar-tagged identities")
        print("  3. Propagate labels to similar unlabeled vectors")
        print("  4. Validate labeled identities appear in search")
        print("  5. Hybrid face + semantic search")
        print("  6. Summary table")
        print("=" * 60)

        passes = [
            self.run_analyze_pass,
            self.run_label_pass,
            self.run_propagation_pass,
            self.run_search_validation,
            self.run_hybrid_search_demo,
            self.print_summary,
        ]

        for pass_fn in passes:
            try:
                pass_fn()
            except Exception as exc:
                print(f"\n❌ {pass_fn.__name__} failed: {exc}")

        self.print_header("Demo Complete")
        print("🎉 Pipeline finished.")
        print("\nNext steps:")
        print("  • Inspect results in the engine: curl .../v1/search?identity_name=Alex+Rivera")
        print("  • See DEMO.md for curl equivalents and troubleshooting guide")


def main():
    demo = ImageUrlDemo()
    demo.run()


if __name__ == "__main__":
    main()
