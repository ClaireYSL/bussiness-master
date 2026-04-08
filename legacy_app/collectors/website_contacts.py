from __future__ import annotations

import html
import re
from typing import Any, Optional
from urllib.parse import urljoin

from collectors.base import BaseCollector, CollectedRecord

EMAIL_RE = re.compile(r"(?<![\w.-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
MOBILE_RE = re.compile(r"(?<!\d)(?:\+?86[-\s]?)?1[3-9]\d{9}(?!\d)")
LANDLINE_RE = re.compile(r"(?<!\d)(?:\+?86[-\s]?)?0\d{2,3}[-\s]?\d{7,8}(?!\d)")
CONTACT_HINTS = (
    "contact",
    "connect",
    "business",
    "sales",
    "support",
    "service",
    "message",
    "form",
    "咨询",
    "联系",
    "合作",
    "客服",
    "商务",
    "留言",
)


def _normalize_url(value: str, base_url: Optional[str] = None) -> str:
    candidate = value.strip()
    if base_url and not candidate.startswith(("http://", "https://", "mailto:", "tel:")):
        candidate = urljoin(base_url, candidate)
    return candidate.rstrip("/")


def _extract_links(html_text: str, base_url: Optional[str] = None) -> list[str]:
    links: list[str] = []
    for match in re.finditer(r'href=["\']([^"\']+)["\']', html_text, flags=re.IGNORECASE):
        href = html.unescape(match.group(1)).strip()
        if not href:
            continue
        normalized = _normalize_url(href, base_url=base_url)
        if any(hint in normalized.lower() for hint in CONTACT_HINTS) or normalized.lower().startswith(
            ("mailto:", "tel:", "weixin:", "wx:")
        ):
            links.append(normalized)
    return links


def _extract_wechat_entries(html_text: str) -> list[str]:
    entries: list[str] = []
    if "mp.weixin.qq.com" in html_text.lower():
        entries.append("https://mp.weixin.qq.com")
    if "公众号" in html_text or "wechat" in html_text.lower() or "微信" in html_text:
        entries.append("wechat")
    return entries


def extract_public_contacts(html_text: str, *, source_url: Optional[str] = None) -> list[dict[str, Any]]:
    text = html.unescape(html_text or "")
    contacts: list[dict[str, Any]] = []

    for email in dict.fromkeys(EMAIL_RE.findall(text)):
        contacts.append(
            {
                "contact_type": "email",
                "contact_value": email,
                "source_url": source_url,
                "is_public": True,
            }
        )

    for phone in dict.fromkeys([*MOBILE_RE.findall(text), *LANDLINE_RE.findall(text)]):
        contacts.append(
            {
                "contact_type": "phone",
                "contact_value": phone,
                "source_url": source_url,
                "is_public": True,
            }
        )

    for link in dict.fromkeys(_extract_links(text, base_url=source_url)):
        contact_type = "form_url"
        lowered = link.lower()
        source_link = link
        if lowered.startswith("mailto:"):
            contact_type = "email"
            link = link.split(":", 1)[1]
        elif lowered.startswith("tel:"):
            contact_type = "phone"
            link = link.split(":", 1)[1]
        elif "mp.weixin.qq.com" in lowered or "wechat" in lowered or "weixin" in lowered:
            contact_type = "official_account"

        contacts.append(
            {
                "contact_type": contact_type,
                "contact_value": link,
                "source_url": source_link,
                "is_public": True,
            }
        )

    for entry in dict.fromkeys(_extract_wechat_entries(text)):
        contacts.append(
            {
                "contact_type": "wechat_service" if entry == "wechat" else "official_account",
                "contact_value": entry,
                "source_url": source_url,
                "is_public": True,
            }
        )

    return contacts


class WebsiteContactsCollector(BaseCollector):
    source_platform = "website_contacts"

    async def fetch(self) -> list[CollectedRecord]:
        return []

    def collect(self, company: Any, *, source_html: Optional[str] = None) -> list[dict[str, Any]]:
        website = getattr(company, "website", None)
        if not website or not source_html:
            return []

        website_url = str(website).strip()
        if not website_url:
            return []

        return extract_public_contacts(source_html, source_url=website_url)
