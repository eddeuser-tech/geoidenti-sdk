#!/usr/bin/env python3
"""
GeoIdenti SDK - Quick Demo
==========================

A six-section walkthrough of the GeoIdenti SDK against a live engine.

Sections:
  1. Health      — service health check (no auth required)
  2. Status      — authenticated API status and role
  3. Analyze     — submit two portrait URLs for face + location analysis
  4. Label       — assign a human name to the first face vector
  5. Search      — filter search by identity name
  6. Hybrid      — face-vector + semantic search

Requirements:
  pip install geoidenti-sdk

Auth:
  Analyst-level API key is sufficient for all sections.
  export GEOIDENTI_API_KEY="<your-analyst-jwt>"
  export GEOIDENTI_BASE_URL="http://localhost:8000/v1"  # optional

Usage:
  python3 demo.py
"""

import os
import sys

from geoidenti_sdk import GeoIdenti

# ---------------------------------------------------------------------------
# Two public Unsplash portrait URLs used for the Analyze section.
# These match the first two entries in integration/sample_images.json.
# ---------------------------------------------------------------------------
DEMO_IMAGES = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
    "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400",
]


class GeoIdentiDemo:
    """Six-section live walkthrough of the GeoIdenti SDK."""

    def __init__(self):
        self._require_env()
        api_key = os.environ["GEOIDENTI_API_KEY"]
        base_url = os.environ.get("GEOIDENTI_BASE_URL", "https://api.geoidenti.com/v1")
        self.client = GeoIdenti(api_key=api_key, base_url=base_url)
        # Populated by section_analyze(); consumed by section_label() and
        # section_hybrid_search().
        self.analyze_results = []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _require_env():
        if not os.environ.get("GEOIDENTI_API_KEY"):
            print(
                "\n❌  GEOIDENTI_API_KEY is not set.\n"
                "\n"
                "   Export your analyst JWT before running:\n"
                "     export GEOIDENTI_API_KEY=\"<your-jwt-token>\"\n"
                "     export GEOIDENTI_BASE_URL=\"http://localhost:8000/v1\"  # if not using production\n"
            )
            sys.exit(1)

    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def section_health(self):
        self.print_header("Section 1 — Health Check")
        result = self.client.health()
        print(f"✅ Status:  {result.get('status', 'n/a')}")
        print(f"   Version: {result.get('version', 'n/a')}")
        print(f"   Time:    {result.get('timestamp', 'n/a')}")

    def section_status(self):
        self.print_header("Section 2 — API Status")
        result = self.client.status()
        print(f"✅ Status: {result.get('status', 'n/a')}")
        print(f"   User:   {result.get('user', 'n/a')}")
        print(f"   Role:   {result.get('role', 'n/a')}")

    def section_analyze(self):
        self.print_header("Section 3 — Analyze Images")
        for i, url in enumerate(DEMO_IMAGES, 1):
            print(f"\n🔍 Image {i}: {url}")
            result = self.client.analyze(url)
            self.analyze_results.append(result)
            loc = result.get("location", {})
            print(f"   ✅ vector_id:        {result.get('vector_id', 'n/a')}")
            print(f"   📍 city:             {loc.get('city', 'n/a')}")
            print(f"   📍 country:          {loc.get('country', 'n/a')}")
            print(f"   🔍 inferred_identity: {result.get('inferred_identity', 'n/a')}")

    def section_label(self):
        self.print_header("Section 4 — Label Identity")
        if not self.analyze_results:
            print("⚠️  No analyze results available — skipping label step.")
            return
        vector_id = self.analyze_results[0].get("vector_id")
        if not vector_id:
            print("⚠️  First analyze result has no vector_id — skipping label step.")
            return
        result = self.client.label_identity(vector_id, "Alex Rivera")
        print(f"✅ Labeled vector {vector_id} → 'Alex Rivera'")
        print(f"   Response: {result}")

    def section_search(self):
        self.print_header("Section 5 — Search by Identity")
        results = self.client.search(identity_name="Alex Rivera", limit=5)
        print(f"✅ {len(results)} result(s) for identity_name='Alex Rivera'\n")
        if results:
            header = f"  {'identity_name':<22} {'city':<16} {'confidence':<10} image_url"
            print(header)
            print(f"  {'-'*22} {'-'*16} {'-'*10} {'-'*40}")
            for r in results:
                print(
                    f"  {r.get('identity_name',''):<22} "
                    f"{r.get('city',''):<16} "
                    f"{str(r.get('confidence','')):<10} "
                    f"{r.get('image_url','')}"
                )
        else:
            print("   ℹ️  No results returned. The engine may need a moment to index the")
            print("   labeled vector. Re-run this section after a few seconds.")

    def section_hybrid_search(self):
        self.print_header("Section 6 — Hybrid Face + Semantic Search")
        if not self.analyze_results:
            print("⚠️  No analyze results available — skipping hybrid search.")
            return
        face_vector = self.analyze_results[0].get("face_vector")
        if not face_vector:
            print("⚠️  First analyze result has no face_vector — skipping hybrid search.")
            return
        results = self.client.search_vector(
            face_vector=face_vector,
            semantic_query="outdoor portrait",
            limit=5,
        )
        print(f"✅ {len(results)} result(s) — face vector × semantic_query='outdoor portrait'\n")
        if results:
            header = f"  {'identity_name':<22} {'city':<16} {'confidence':<10} image_url"
            print(header)
            print(f"  {'-'*22} {'-'*16} {'-'*10} {'-'*40}")
            for r in results:
                print(
                    f"  {r.get('identity_name',''):<22} "
                    f"{r.get('city',''):<16} "
                    f"{str(r.get('confidence','')):<10} "
                    f"{r.get('image_url','')}"
                )

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self):
        print("🚀 GeoIdenti SDK — Quick Demo")
        print("=" * 60)
        print("Analyst-level walkthrough:")
        print("  1. Health check    4. Label identity")
        print("  2. API status      5. Search by name")
        print("  3. Analyze images  6. Hybrid search")
        print("=" * 60)

        sections = [
            self.section_health,
            self.section_status,
            self.section_analyze,
            self.section_label,
            self.section_search,
            self.section_hybrid_search,
        ]

        for section_fn in sections:
            try:
                section_fn()
            except Exception as exc:
                print(f"\n❌ {section_fn.__name__} failed: {exc}")

        self.print_header("Demo Complete")
        print("🎉 All sections finished.")
        print("\nNext steps:")
        print("  • Run the full pipeline: python3 integration/image_url_demo.py")
        print("  • See DEMO.md for setup guide and curl equivalents")


def main():
    demo = GeoIdentiDemo()
    demo.run()


if __name__ == "__main__":
    main()
