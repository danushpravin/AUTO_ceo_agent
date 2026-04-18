# Channel Dependency Risk — Thresholds and Interpretation Framework

## What Channel Dependency Risk Measures

Channel dependency risk measures the degree to which a business's revenue and profit are concentrated in a small number of sales or marketing channels. A business that generates 70% of its revenue through a single channel — whether that is one e-commerce platform, one retail partner, one marketing channel, or one geographic market — is structurally fragile. Channel concentration creates single points of failure that can collapse revenue without warning when platform algorithms change, partner relationships deteriorate, or channel economics shift.

## Revenue Concentration Threshold

When a single channel contributes 50% or more of total business revenue, the business has meaningful channel dependency risk. This threshold reflects the point at which a channel disruption — platform policy change, partner contract termination, algorithm update, or market shift — would cause an immediately material revenue impact that cannot be absorbed or quickly replaced by other channels.

Threshold: Single channel revenue share of 50% or above triggers a CHANNEL_REVENUE_CONCENTRATION flag at medium severity. Above 70%, severity escalates to high. A business with one channel above 70% revenue share is not a multi-channel business — it is a single-channel business with minor secondary channels providing the illusion of diversification.

## Profit Concentration Threshold

Profit concentration is more dangerous than revenue concentration. A channel can contribute 50% of revenue but only 30% of profit if other channels are more efficient. The reverse — a channel contributing 70% or more of total profit — means that if that channel's economics deteriorate (rising CAC, platform fee increases, margin compression), the entire profit pool of the business is at risk simultaneously.

Threshold: Single channel profit share of 70% or above triggers a PROFIT_CONCENTRATION flag at high severity. This is the most critical channel risk flag because it indicates that the business's economic viability is dependent on a single channel remaining healthy.

## ROAS Illusion: The Hidden Channel Value Destroyer

A channel can generate positive revenue while simultaneously destroying net business value. This occurs when a channel's ROAS looks acceptable in isolation but, after accounting for product cost and marketing spend, the channel generates negative net profit margin. This is called the ROAS illusion — the channel appears to be working on marketing metrics while silently bleeding the business. Businesses scale into ROAS illusion channels because top-line revenue grows, masking the underlying margin destruction.

Threshold: Any channel with positive revenue but negative net profit margin triggers a ROAS_ILLUSION flag at high severity. There is no acceptable version of a revenue-generating channel with negative net margin at scale — it is a value destruction engine that must be restructured or eliminated.

## Single Healthy Channel Dependency

Beyond concentration thresholds, the absolute number of economically healthy channels matters. A business with four channels but only one generating positive net profit margin (above 5%) is functionally a single-channel business even if revenue appears distributed. The healthy channel is subsidising the others, and its loss would require the business to restructure entirely.

Threshold: Fewer than two channels meeting the minimum healthy margin threshold of 5% net profit margin triggers a SINGLE_CHANNEL_DEPENDENCY flag at high severity. The business needs at least two independently profitable channels to have meaningful resilience.

## Interpreting Channel Dependency in Context

Channel dependency flags should always be interpreted alongside marketing efficiency and product portfolio signals. A channel concentration flag is significantly more dangerous when combined with a ROAS illusion in the dominant channel, or when the dominant channel's primary products are classified as FAKE_GROWTH in the portfolio analysis. These combinations indicate a business where both the revenue source and the revenue quality are simultaneously fragile.

## Healthy Channel Distribution

A structurally resilient business has at least three channels each contributing between 15% and 50% of total revenue, with no single channel above 50%, and at least two channels generating positive net profit margin above 10%. Revenue distribution does not need to be equal — a 45/35/20 split across three channels is healthy. What is unhealthy is a 70/20/10 split where the dominant channel also has thin margins or ROAS illusion dynamics.