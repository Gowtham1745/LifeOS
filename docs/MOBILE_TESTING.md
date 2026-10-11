# Mobile layout testing

Test LifeOS on real devices where possible, and use responsive browser tools for repeatable checks.

## Suggested viewport widths

| Device class | Width |
| --- | ---: |
| Small phone | 320 px |
| Typical phone | 360–390 px |
| Large phone | 430 px |
| Tablet portrait | 768 px |
| Laptop | 1280 px |
| Wide desktop | 1440 px |

## What to inspect

- Page title and search controls do not collide.
- The momentum card wraps without overlapping its score ring.
- Cards fit the viewport without accidental horizontal scrolling.
- Text remains readable at default browser zoom.
- Bottom navigation does not cover the last content row.
- Inputs are usable with the on-screen keyboard.
- Focus indicators are visible with an external keyboard.
- Both color themes maintain sufficient contrast.

Record the viewport and browser with every layout bug so the fix can be reproduced.
