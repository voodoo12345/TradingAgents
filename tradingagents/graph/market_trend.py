from __future__ import annotations

import re
from typing import Iterable, Optional


_BULLISH_TERMS = (
    "bullish",
    "uptrend",
    "upward",
    "higher",
    "positive",
    "strengthening",
    "long",
    "breakout",
    "golden cross",
    "turning positive",
)

_BEARISH_TERMS = (
    "bearish",
    "downtrend",
    "downward",
    "lower",
    "negative",
    "weakening",
    "short",
    "breakdown",
    "death cross",
)


def _split_clauses(text: str) -> list[str]:
    if not text:
        return []
    clauses = re.split(r"[\n\r\.!?。]+", text)
    return [clause.strip() for clause in clauses if clause.strip()]


def _indicator_sentiment(text: str, keywords: Iterable[str]) -> Optional[bool]:
    clauses = _split_clauses(text.lower())
    bullish = 0
    bearish = 0

    for clause in clauses:
        if any(keyword in clause for keyword in keywords):
            if any(term in clause for term in _BULLISH_TERMS):
                bullish += 1
            if any(term in clause for term in _BEARISH_TERMS):
                bearish += 1

    if bullish and not bearish:
        return True
    if bearish and not bullish:
        return False
    return None


def _moving_average_majority_bullish(text: str) -> bool:
    ma_keywords = {
        "close_10_ema": ["close_10_ema", "10 ema"],
        "close_50_sma": ["close_50_sma", "50 sma"],
        "close_200_sma": ["close_200_sma", "200 sma"],
    }

    bullish = 0
    bearish = 0
    for keywords in ma_keywords.values():
        sentiment = _indicator_sentiment(text, keywords)
        if sentiment is True:
            bullish += 1
        elif sentiment is False:
            bearish += 1

    return bullish > bearish and bullish > 0


def is_bullish_trend(market_report: str) -> bool:
    """Determine if the market report indicates a bullish trend."""
    if not market_report:
        return False

    adx_bullish = _indicator_sentiment(market_report, ["adx"])
    di_bullish = _indicator_sentiment(
        market_report,
        ["plus_di", "+di", "positive directional", "plus di"],
    )
    di_adx_bullish = adx_bullish is True and di_bullish is True

    obv_bullish = _indicator_sentiment(market_report, ["obv", "on-balance volume"]) is True
    two_poles_bullish = (
        _indicator_sentiment(
            market_report,
            ["two_poles_trend_finder", "two poles trend finder"],
        )
        is True
    )
    ma_bullish = _moving_average_majority_bullish(market_report)

    return di_adx_bullish and obv_bullish and two_poles_bullish and ma_bullish
