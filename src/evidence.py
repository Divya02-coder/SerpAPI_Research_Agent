class EvidenceLedger:

    def __init__(self):
        self.sources = []
        self.url_to_id = {}

    def reset(self):
        """
        Clear all evidence collected for the current research question.
        """
        self.sources = []
        self.url_to_id = {}

    def add_source(self, source):
        """
        Add a source and assign it an ID such as S1, S2, S3...
        Duplicate URLs are not added twice.
        """

        url = source.get("url", "").strip()

        if not url:
            return None

        # Avoid duplicate sources
        if url in self.url_to_id:
            return self.url_to_id[url]

        source_id = f"S{len(self.sources) + 1}"

        enriched_source = source.copy()
        enriched_source["source_id"] = source_id

        self.sources.append(enriched_source)
        self.url_to_id[url] = source_id

        return source_id

    def process_result(self, result):
        """
        Add all sources returned by a search and attach
        source IDs to them.
        """

        processed_sources = []

        for source in result.get("sources", []):

            source_id = self.add_source(source)

            enriched_source = source.copy()
            enriched_source["source_id"] = source_id

            processed_sources.append(enriched_source)

        result_copy = result.copy()
        result_copy["sources"] = processed_sources

        return result_copy

    def get_context(self):
        """
        Return the collected evidence in a format that
        can be given to the model.
        """

        if not self.sources:
            return "No evidence collected yet."

        lines = []

        for source in self.sources:

            lines.append(
                f"[{source['source_id']}] "
                f"{source.get('title', '')} | "
                f"{source.get('domain', '')} | "
                f"{source.get('url', '')}\n"
                f"Snippet: {source.get('snippet', '')}"
            )

        return "\n\n".join(lines)

    def summary(self):
        """
        Return basic research statistics.
        """

        domains = set()

        for source in self.sources:

            domain = source.get("domain")

            if domain:
                domains.add(domain)

        return {
            "total_sources": len(self.sources),
            "unique_domains": len(domains),
            "domains": sorted(domains)
        }

    def formatted_sources(self):
        """
        Return sources in a readable format for /sources.
        """

        if not self.sources:
            return ""

        lines = []

        for source in self.sources:

            lines.append(
                f"[{source['source_id']}] "
                f"{source.get('title', '')}\n"
                f"    {source.get('url', '')}"
            )

        return "\n".join(lines)