# NexGenWebLab Design Tokens

Source of truth for all brand visual properties across marketing site (frontend 1/), React app (frontend 2/), and admin panel (admin/).

## Brand Colors

| Token | Hex | CSS Variable | Tailwind |
|---|---|---|---|
| Primary (purple) | `#6D28D9` | `--purple` | `primary`, `bg-primary`, `text-primary` |
| Primary hover | `#5B21B6` | — | — |
| Primary light | `#8B5CF6` | `--purple-light` | — |
| Secondary (pink) | `#DB2777` | `--pink` | `secondary`, `bg-secondary`, `text-secondary` |
| Secondary hover | `#BE185D` | — | — |
| Secondary light | `#F472B6` | `--pink-light` | — |
| Gradient | `linear-gradient(135deg, #6D28D9, #DB2777)` | `--gradient` | `bg-gradient-to-r from-primary to-secondary` |
| Gradient hover | `linear-gradient(135deg, #5B21B6, #BE185D)` | `--gradient-hover` | — |

## Neutral Palette

| Token | Hex | Usage |
|---|---|---|
| `--slate-50` | `#f8fafc` | Page background |
| `--slate-100` | `#f1f5f9` | Card borders, tab backgrounds |
| `--slate-200` | `#e2e8f0` | Input borders, dividers |
| `--slate-300` | `#cbd5e1` | Disabled elements |
| `--slate-400` | `#94a3b8` | Caption text, icons |
| `--slate-500` | `#64748b` | Body text, secondary text |
| `--slate-600` | `#475569` | Labels, muted text |
| `--slate-700` | `#334155` | Subheadings |
| `--slate-800` | `#1e293b` | Dark headings |
| `--slate-900` | `#0f172a` | Primary headings |

## Semantic Colors

| Token | Hex | Usage |
|---|---|---|
| `--red` | `#ef4444` | Errors, critical issues |
| `--red-light` | `#fef2f2` | Error backgrounds |
| `--amber` | `#f59e0b` | Warnings |
| `--amber-light` | `#fffbeb` | Warning backgrounds |
| `--green` | `#10b981` | Success, pro badge |
| `--green-light` | `#ecfdf5` | Success backgrounds |
| `--blue` | `#3b82f6` | Info |
| `--blue-light` | `#eff6ff` | Info backgrounds |

## Typography

| Role | Family | Weight |
|---|---|---|
| Headings | `'Inter', -apple-system, BlinkMacSystemFont, sans-serif` | 800–900 (font-black) |
| Body | `'Inter', -apple-system, BlinkMacSystemFont, sans-serif` | 400–700 |
| Monospace | `'SF Mono', 'Fira Code', 'Cascadia Code', monospace` | — |

### Font Sizes

| Level | Desktop | Mobile |
|---|---|---|
| h1 | `text-4xl md:text-6xl lg:text-7xl` (36–72px) | `text-4xl` |
| h2 | `text-3xl md:text-4xl lg:text-5xl` (30–48px) | `text-3xl` |
| h3 | `text-xl lg:text-2xl` (20–24px) | `text-xl` |
| Body | `text-base` (16px) | `text-base` |
| Caption | `text-xs` (12px) | `text-xs` |
| Small | `text-sm` (14px) | `text-sm` |

## Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | 8px | Buttons, inputs, cards |
| `--radius-md` | 12px | Tab bars, cards |
| `--radius-lg` | 18px | Large cards, containers |
| `--radius-xl` | 24px | Modals, login panels |
| Full | 999px | Badges, pills |

## Shadows

| Token | Value |
|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.03)` |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.06)` |
| `--shadow-lg` | `0 10px 40px -10px rgba(0,0,0,0.08)` |

## Button Styles

### Primary (`.btn-primary` / gradient CTA)
- Height: 48px (app) / auto (marketing)
- Padding: 0 24px
- Background: `var(--gradient)` / `bg-gradient-to-r from-primary to-secondary`
- Color: white
- Font: 700 (bold) or 900 (black for marketing)
- Radius: 8px (`--radius-sm`) or `rounded-xl`
- Hover: brighten, slight lift (`transform: translateY(-1px)`)
- Marketing site: also uses `bg-slate-900 text-white` for secondary primary CTAs

### Secondary (`.btn-secondary` / outline)
- Height: 40px
- Padding: 0 16px
- Background: white
- Border: 1px solid `--slate-200`
- Color: `--slate-600`
- Font: 600, 13px
- Radius: 8px
- Hover: border `--purple`, color `--purple`

### Ghost (`.nav-item`, text-only buttons)
- No border/background
- Color: `--slate-600`
- Font: 600, 14px
- Hover: `rgba(109,40,217,0.05)` background

## Input Styles
- Height: 48px
- Border: 2px solid `--slate-200`
- Radius: 8px (`--radius-sm`)
- Background: `--slate-50`
- Font: 500–700, 15px
- Focus: border `--purple`, background white, `0 0 0 3px rgba(109,40,217,0.08)` ring

## Logo
- File: `/assets/images/logo.png`
- Max width: 180px (app sidebar)
- Height: auto (keeps aspect ratio)
- Marketing nav height: `h-7` (28px)
- Footer (dark bg): `brightness-0 invert`

## Spacing Scale
- `8px` (`gap-2`), `12px` (`gap-3`), `16px` (`gap-4`), `20px` (`gap-5`), `24px` (`gap-6`)
- Section padding: `py-10` (40px), `py-16` (64px), `py-20` (80px)
