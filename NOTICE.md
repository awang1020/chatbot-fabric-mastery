# Notice

## Scope of the licence

The [MIT licence](LICENSE) covers the **source code only**.

## Newsletter content

The editions cached under `data/newsletters/` and the answers the assistant
derives from them remain the copyright of Antoine Wang and are published at
<https://blog.antoinewang-tech.com>. They are committed here solely so the
retrieval index can be rebuilt, and are **not** licensed for redistribution.

## Trademarks

Microsoft, Microsoft Fabric, Power BI and Azure are trademarks of the Microsoft
group of companies. This project is independent and is not affiliated with,
endorsed by, or sponsored by Microsoft.

## Third-party dependencies

Runtime dependencies are pinned in [requirements.txt](requirements.txt) and keep
their own licences.

### Known advisories accepted as not applicable

`chromadb` carries open advisories (including two rated critical) with no
patched release available. They are exploited through the **Chroma server HTTP
API** (`/api/v2/tenants/.../collections`, `trust_remote_code`).

This project embeds Chroma through `chromadb.PersistentClient`
(see [src/indexer.py](src/indexer.py)), never starts a Chroma server, and
exposes only Streamlit on port 8501. The vulnerable endpoints therefore do not
exist in this deployment. Dependabot keeps tracking them so the pins can be
bumped as soon as a fix ships.
