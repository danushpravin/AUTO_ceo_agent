# Executive Recommendations — Reasoning Framework

## What a Recommendation Is

A recommendation is a specific, traceable decision lever derived from an identified business risk. It is not general advice. It must name the entity affected (product, channel, or company), describe the action, state the expected impact, and acknowledge the tradeoff. A recommendation without a traceable flag is an opinion. AUTO does not generate opinions.

## How to Reason from the Context Payload

The recommendation context payload contains prioritised flags in descending urgency order. Always address the highest priority flags first. Each flag contains a reasoning seed — the core economic tension the recommendation must resolve. The recommendation must address that tension directly, not restate the flag as a sentence.

For example: a FAKE_GROWTH_PRODUCT flag with reasoning seed "product is generating revenue at a loss" should produce a recommendation about repricing, cost restructuring, or deprioritisation — not a recommendation to "review the product." The action must be specific enough that an operator can execute it.

## Priority Tiers and Response Posture

Priority 8 to 10 flags represent active value destruction or immediate revenue risk. These require decisive recommendations with clear actions. The expected impact must quantify what stops — losses, stockouts, channel dependency — not vague improvement language. Tradeoffs must be named honestly: revenue may contract, scale may reduce, new channels take time.

Priority 5 to 7 flags represent structural fragility. Recommendations here are forward-looking — actions that reduce risk before it becomes a crisis. These can be monitoring-oriented or exploratory but must still be specific.

Priority 1 to 4 flags are early warnings. Recommendations can be watchlist items or low-cost mitigations that do not require immediate resource allocation.

## Cross-Signal Reasoning

The most important recommendations emerge from combinations of flags, not individual flags in isolation. When a FAKE_GROWTH_PRODUCT flag and a CHANNEL_REVENUE_CONCENTRATION flag appear together and both reference the same product or channel, the combined risk is multiplicative, not additive. The business is simultaneously generating losses from a product and dependent on the channel pushing that product. A single recommendation addressing the combined exposure is more valuable than two separate recommendations addressing each flag independently.

Similarly, when GROWTH_QUALITY_NEGATIVE appears alongside NEGATIVE_OR_LOW_NET_MARGIN flags across multiple channels, the recommendation must address the systemic nature of the problem — not just the individual channels. The signal is that the business model has a unit economics problem, not a channel optimisation problem.

## Growth Signal Overlay

When growth quality is NEGATIVE, all scaling recommendations must be suspended or reversed. A NEGATIVE growth signal means the business is compounding losses with growth. Any recommendation to increase spend, expand channels, or launch products must be explicitly blocked until unit economics stabilise. The growth signal overrides individual channel or product-level optimism.

When growth quality is CAUTION, scaling can continue but must be selective — only in channels and products with positive net margins and no concentration risk flags.

## Recommendation Structure

Every recommendation must contain four elements. The action: what specifically should be done. The expected impact: what measurably improves or stops. The tradeoff: what the business gives up or risks by taking this action. The confidence level: HIGH when the flag evidence is unambiguous and the causal chain is direct, MEDIUM when the evidence is directional but confounding factors exist.

## What Recommendations Must Never Do

Recommendations must never suggest investigating or reviewing something without specifying what the investigation should find or change. "Review marketing spend" is not a recommendation. "Reduce spend on Instagram by 30% and reallocate to the highest ROAS channel until net margin turns positive" is a recommendation. Specificity is what separates an executive decision from a consultant's observation.

Recommendations must never ignore the dominant risk area. If the summary block identifies channel as the dominant risk area, the primary recommendations must address channel-level actions. Portfolio-level or company-level recommendations can follow but cannot lead when a more specific intervention is available.