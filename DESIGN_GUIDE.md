# Nation Simulator — Design Guide

## 1. Purpose

Nation Simulator is a personal game, not a commercial web application and not an admin dashboard.

The interface should feel like a strategy game about managing and developing an ancient civilization.

The user is not "editing data".

The user is ruling a nation, developing settlements, managing resources, assigning workers, constructing buildings, researching technologies, exploring locations, and watching the civilization grow over time.

Every major UI decision should answer:

> Does this make the application feel more like an Ancient Greek strategy game?

If the answer is no, reconsider the design.

---

# 2. Core Visual Direction

The primary visual direction is:

**Ancient Greek / Hellenistic strategy game interface**

The UI should combine:

- Ancient Greek visual identity
- Hellenistic Mediterranean atmosphere
- classic strategy-game interface design
- parchment and aged paper
- bronze and antique gold
- dark navy / blue-black structural areas
- painted game artwork
- clear information hierarchy
- restrained historical ornamentation

The final result should feel closer to a classic PC strategy game than to a modern website.

---

# 3. Visual Inspiration

Primary inspirations:

- Heroes of Might and Magic III
- Ikariam
- Travian
- Ancient Greek and Hellenistic art
- Mediterranean cities
- Alexandria
- ancient maps and chronicles
- Greek architectural ornament
- bronze objects
- parchment manuscripts

These references define atmosphere and visual language.

Do NOT directly copy their layouts or assets.

The application should develop its own consistent visual identity.

---

# 4. World and Atmosphere

The interface should feel like a combination of:

- a ruler's administrative chamber
- a strategic planning table
- an ancient chronicle
- a map room
- a Hellenistic archive

Imagine:

- Alexandria
- coastal Greek poleis
- temples
- libraries
- scrolls
- maps
- bronze instruments
- carved stone
- wooden furniture
- merchant ships
- chronicles
- military planning rooms
- warehouses and workshops

The visual identity should suggest that the interface belongs to the world itself.

It should not feel like modern software with an Ancient Greek skin placed on top.

---

# 5. Overall Mood

The interface should feel:

- historical
- warm
- calm
- elegant
- slightly aged
- handcrafted
- readable
- information-dense
- game-like

It should NOT feel:

- futuristic
- corporate
- minimalist SaaS
- mobile-first
- sterile
- glossy
- neon
- overly cartoonish

The UI may contain fantasy elements because the game world can include mythology, but the foundation should remain Ancient Greek / Hellenistic.

---

# 6. Application Structure

The main application uses a persistent GameShell.

Desktop structure:

```text
┌───────────────┬─────────────────────────────────────────────┐
│               │ RESOURCE BAR                                │
│               ├─────────────────────────────────────────────┤
│               │                                             │
│   SIDEBAR     │              PAGE CONTENT                   │
│               │                                             │
│               │                                             │
│               │                                             │
└───────────────┴─────────────────────────────────────────────┘
```

The main structural layers are:

1. Sidebar
2. ResourceBar
3. PageHeader
4. Page Content
5. Panels / Sections

These elements should remain visually consistent across the entire application.

---

# 7. Material Hierarchy

The interface should visually separate structural UI from information content.

## Game Shell

Sidebar and ResourceBar should use:

- dark navy
- blue-black
- charcoal-blue
- very dark desaturated tones

These areas represent the permanent game HUD.

## Page Content

The main content area should primarily use:

- parchment
- aged paper
- warm cream
- sand
- light beige

This creates strong visual separation:

```text
DARK GAME SHELL
        ↓
LIGHT PARCHMENT CONTENT
```

## Accents

Use:

- bronze
- antique gold
- muted ochre

for:

- borders
- separators
- important icons
- selected navigation
- decorative lines
- important values
- small ornaments

---

# 8. Color System

Colors should be centralized through design tokens / CSS variables.

Avoid scattering hardcoded colors throughout components.

The exact palette may evolve, but the semantic structure should remain stable.

## Shell

Suggested direction:

```css
--shell-bg: #07151d;
--sidebar-bg: #081820;
--topbar-bg: #091a22;
```

These are reference values, not mandatory final values.

The shell should appear dark navy / blue-black rather than green.

## Parchment

Suggested direction:

```css
--parchment: #d8c49a;
--parchment-light: #ead9b5;
--parchment-dark: #bca578;
```

Parchment should be warm but not strongly yellow.

Avoid bright cream or orange paper.

## Bronze / Gold

Suggested direction:

```css
--bronze: #9a6a2f;
--bronze-light: #c39752;
--bronze-dark: #62431f;
--antique-gold: #c69a43;
```

Gold should look aged rather than shiny.

Avoid bright yellow gold.

## Ink

Text on parchment should use dark ink-like colors.

Suggested direction:

```css
--ink: #2a2117;
--ink-muted: #665640;
```

Avoid pure black where possible.

## Text on Dark Background

Suggested direction:

```css
--text-on-dark: #eadfca;
--text-on-dark-muted: #afa48f;
```

## Semantic Colors

Semantic colors remain functional:

```text
green       positive / production / success
red         negative / danger / consumption
orange      warning
blue        informational
```

All semantic colors should be slightly muted to fit the historical palette.

Avoid modern highly saturated UI colors.

---

# 9. Typography

Typography is one of the primary tools for separating the game from a generic web application.

The UI should primarily use serif typography.

## Display / Page Titles

Recommended direction:

- Cinzel
- Marcellus
- similar classical serif

Used for:

- page titles
- nation names
- major headings
- important game labels

## Body Text

Recommended direction:

- Lora
- Libre Baskerville
- Crimson Pro
- similar highly readable serif

Used for descriptions, metadata, controls, event history, forms, and secondary information.

Do NOT use decorative display typography everywhere.

Typography must remain readable at normal desktop UI sizes.

---

# 10. Geometry

Avoid the geometry of modern SaaS applications.

## Border Radius

Preferred:

```text
0–6px
```

Most game panels should be square, almost square, or slightly rounded.

Avoid large modern card radii such as 16–24px unless there is a specific visual reason.

Do not use pill-shaped containers as a general UI style.

## Spacing

Prefer a consistent spacing scale:

```text
4px
8px
12px
16px
24px
32px
```

---

# 11. Borders and Depth

The interface should create depth primarily through:

- borders
- material contrast
- subtle inset shadows
- subtle outer shadows
- separators

Avoid large floating-card shadows.

Major panels use a visible bronze/brown edge. Internal sections use subtle parchment borders or dividers. Controls use clear but restrained borders.

---

# 12. GamePanel

GamePanel is the primary information container.

It should visually resemble a framed information area rather than a modern card.

Recommended characteristics:

- parchment background
- bronze/brown border
- subtle inner shadow
- minimal outer shadow
- low border radius
- comfortable padding

GamePanel should be reusable.

---

# 13. SectionHeader

SectionHeader defines internal information sections.

It may contain:

- optional icon
- title
- optional right-side information
- subtle divider

SectionHeader should be compact and visually stronger than body content without competing with PageHeader.

---

# 14. Buttons

Buttons should resemble strategy-game controls rather than modern web buttons.

Common button types:

- Primary
- Secondary
- Success
- Warning
- Danger
- Icon Button

Buttons of the same type must look identical across the application.

Use bronze, parchment, dark navy, subtle gradients where useful, defined borders, subtle inset/outset depth, and compact radius.

Avoid pill buttons, glassmorphism, neon colors, large shadows, and excessive gradients.

Hover should use a small brightness/material or border change. Pressed state may use a slight inset effect. Disabled state must remain clear and readable.

---

# 15. Form Controls

Inputs, selects and textareas should belong to the same material system.

Preferred characteristics:

- parchment / sand background
- bronze/brown border
- dark ink text
- compact radius
- clear focus state

Keyboard focus must remain clearly visible.

---

# 16. GameProgressBar

Progress bars may represent construction, research, population, storage, settlement development, and process progress.

Preferred appearance:

- thin or medium height
- restrained track
- clear fill
- subtle border
- slight inset appearance
- low radius

Avoid highly rounded modern progress bars.

---

# 17. StatusBadge

StatusBadge may represent Good, Average, Poor, Active, Paused, Hunger, Warning, or Completed.

Badges should be compact.

Avoid excessive pill styling.

Semantic colors should be muted and consistent with the global palette.

---

# 18. Sidebar

Sidebar is permanent game navigation.

Desktop target width:

```text
approximately 170–200px
```

The actual application routes are always the source of truth.

Do NOT create navigation items simply because they appear in a design concept.

Use dark navy / blue-black background, bronze separators, warm light text, and bronze/gold icons.

Active navigation should feel like a selected game menu item using a bronze edge, subtle inset panel, material change, or side marker.

Avoid modern bright-blue outline selection.

The existing nation emblem may be displayed prominently near the top.

---

# 19. ResourceBar

ResourceBar is the global game HUD.

It displays important resources and global values.

Typical resources may include:

- Food
- Wood
- Stone
- General Points

The real application state is always the source of truth.

Do not invent resources for visual symmetry.

Typical hierarchy:

```text
[ICON] 130
       +4/day
```

The resource value is visually dominant. Production/consumption rate is secondary.

General Points are a special global resource and may receive slightly greater visual prominence.

---

# 20. PageHeader

PageHeader introduces the current page.

It may contain:

- eyebrow/context
- title
- subtitle
- optional right-side content

PageHeader should support future illustrated backgrounds.

Do not hardcode page-specific content inside the reusable component.

---

# 21. Settlement Panorama

A settlement panorama is an important future visual layer.

Visual direction:

- Ancient Greek / Hellenistic coastal settlement
- Mediterranean environment
- temples
- houses
- harbor
- merchant ships
- hills
- vegetation

The panorama should provide atmosphere without reducing text readability.

Recommended shape:

```text
wide cinematic image
approximately 4:1 – 6:1 aspect ratio
```

The panorama may later evolve as the settlement develops, but this should not be implemented unless explicitly requested.

---

# 22. Icons

There are two distinct icon categories.

## UI Icons

For generic actions such as settings, close, expand, collapse, location marker, plus, minus, play, and pause, use `lucide-react` where appropriate.

## Game Icons

Important game concepts should gradually use custom illustrated assets.

Examples:

- Food
- Wood
- Stone
- Population
- General Points
- Buildings
- Items
- special abilities

Do NOT use lucide-react as the permanent visual solution for important game resources when a custom asset exists.

---

# 23. Game Art Direction

Primary art direction:

**hand-painted fantasy strategy game icon / illustration inspired by classic 90s strategy games**

Characteristics:

- painterly shading
- clear silhouette
- vibrant but historically grounded colors
- slightly stylized realism
- readable forms
- Ancient Greek / Bronze Age / Hellenistic influence
- subtle fantasy atmosphere

Avoid photorealism, flat vector icons, modern emoji style, overly cartoonish proportions, excessive micro-detail, and modern objects.

---

# 24. Small Game Icons

Small resource and object icons must remain readable at:

```text
32×32 px
```

The source image may be larger, but its silhouette and composition must remain understandable when scaled down.

Use strong silhouette, limited number of objects, clear lighting, strong value separation, and minimal unnecessary detail.

Avoid clutter.

---

# 25. Transparent Assets

Standalone game objects should normally use transparent backgrounds.

Examples:

- resource icons
- workers
- population
- items
- nation emblems
- isolated buildings when appropriate

Requirements:

- true alpha transparency
- no artificial square background
- no border unless explicitly required
- no text
- object should use most of the available canvas
- unnecessary empty margins should be avoided

Square format (`1:1`) is preferred for icons.

---

# 26. Rectangular Illustrations

Some UI elements require rectangular scene illustrations.

Examples:

- Processes
- settlement panorama
- building scenes
- location scenes

Process illustrations should communicate the activity immediately.

Avoid unnecessary background complexity.

The primary action should remain clear at small UI sizes.

---

# 27. Nation Emblems

Nation emblems are symbolic rather than realistic illustrations.

They should feel inspired by ancient coins, shields, pottery, seals, and carved symbols.

The current Octopus emblem is an example of this direction.

Use simplified shapes, strong silhouette, limited detail, and historical stylization.

Avoid realistic biological detail.

---

# 28. Texture Policy

Textures should support materials, not dominate them.

Allowed:

- subtle parchment grain
- subtle paper variation
- very light stone/wood noise
- CSS gradients
- small repeating textures
- subtle overlays

Avoid large texture files when unnecessary, high-contrast noise, dirty/grunge effects that hurt readability, and clearly visible repeating patterns.

Users should notice the material feeling before they notice the texture itself.

---

# 29. Ornamentation

Greek ornamentation is allowed but should be hierarchical.

Examples:

- meander / Greek key
- laurel branches
- simple geometric borders
- column motifs
- bronze corner details

Use ornament primarily for major shell areas, important headers, nation identity, special panels, and major navigation boundaries.

Do NOT place complex Greek borders around every card.

Ornament should communicate importance.

---

# 30. Visual Hierarchy

Recommended hierarchy:

```text
Nation / Page Identity
        ↓
Global Resources
        ↓
Major Page Sections
        ↓
Important Values / Actions
        ↓
Secondary Information
        ↓
Metadata
```

The more common an element is, the simpler it should generally be.

---

# 31. Information Density

This is a desktop strategy game interface.

Moderately high information density is desirable.

Do not excessively simplify screens or hide useful information merely to make the page look minimal.

The user should be able to quickly understand current resources, population, active processes, available workers, progress, warnings, and recent events.

---

# 32. UX Principles

The application is designed for a single experienced user.

Therefore:

- fast interaction is important
- useful information may remain visible
- advanced controls do not need to be hidden
- confirmation dialogs should only exist when useful
- workflows do not need to be simplified for beginners

Controls must remain understandable, destructive actions should be visually distinct, and important state changes should be visible.

---

# 33. Interaction

Animations should be subtle.

Preferred:

- hover
- short color transition
- border transition
- slight inset/pressed state
- subtle progress movement where appropriate

Avoid bounce, glow, large scaling, excessive movement, flashy effects, and long animations.

---

# 34. Accessibility

Historical styling must not reduce usability.

Always preserve:

- readable contrast
- visible keyboard focus
- clear hover states
- clear disabled states
- comfortable click targets
- readable text sizes

Decorative visuals must never make important information difficult to read.

---

# 35. Responsive Strategy

Primary target:

```text
Desktop
```

Important desktop widths:

```text
1280px
1440px
1920px
```

The UI should use available horizontal space effectively.

Avoid narrow centered web-page layouts.

Mobile is not currently the primary design target, but components should not make future responsive support unnecessarily difficult.

---

# 36. Localization

The application supports localization.

UI architecture must not assume that labels have fixed lengths.

Technical names, component names and code remain in English.

User-facing text should continue using the existing localization system.

Do not hardcode translated UI strings directly into shared components.

---

# 37. Asset Organization

Recommended direction:

```text
/public/images/

    ui/
        textures/
        ornaments/

    general/
        settlement/

    resources/

    processes/

    buildings/

    locations/

    items/

    nations/
```

Adapt this structure to the existing project if another established asset structure already exists.

Do not duplicate assets unnecessarily.

---

# 38. Asset Formats

## WebP

Use for rectangular illustrations, process artwork, settlement panoramas, large non-transparent images, and textures where appropriate.

## PNG / WebP with alpha

Use for resource icons, isolated objects, emblems, and transparent game assets.

## SVG / lucide-react

Use primarily for generic UI controls, simple interface symbols, and functional icons.

Do not convert painterly game artwork into SVG.

---

# 39. Naming Convention

Asset filenames should be descriptive and predictable.

Prefer lowercase `snake_case`.

Examples:

```text
food.webp
wood.webp
stone.webp

food_gathering.webp
woodcutters.webp
stonecutters.webp

warehouse.webp
wooden_wall.webp

octopus_emblem.webp
```

Avoid names such as `image1.png`, `final2.png`, `new_icon.png`, or `test123.webp`.

---

# 40. Concept References

Design concept screenshots define:

- visual direction
- hierarchy
- atmosphere
- density
- materials
- overall composition

They do NOT automatically define:

- game mechanics
- navigation structure
- available resources
- routes
- buttons
- data
- functionality

The real application remains the source of truth for functionality.

Never create functionality merely because it appears in a concept image.

---

# 41. Component Reuse

Global visual language should be implemented through reusable components.

Preferred shared components include:

```text
GameShell
Sidebar
ResourceBar
PageHeader

GamePanel
SectionHeader
GameButton
GameProgressBar
StatusBadge
```

Additional components should be created when repeated UI patterns justify them.

Avoid page-specific versions of the same visual element when a shared component can solve the same problem.

---

# 42. Development Principles

When implementing UI changes:

1. Inspect existing architecture first.
2. Reuse existing components where possible.
3. Do not rewrite business logic for visual reasons.
4. Do not change API contracts for visual reasons.
5. Keep game mechanics separate from presentation.
6. Prefer reusable components.
7. Prefer design tokens over hardcoded styles.
8. Avoid unrelated refactoring.
9. Preserve existing localization.
10. Preserve existing functionality.

---

# 43. What to Avoid

Do NOT drift toward:

- generic SaaS dashboard
- Material Design
- Bootstrap appearance
- Tailwind-template appearance
- glassmorphism
- neumorphism
- modern fintech dashboard
- giant rounded cards
- pill-shaped everything
- excessive whitespace
- excessive minimalism
- neon colors
- pure white backgrounds
- pure black backgrounds
- flat vector game art
- excessive gradients
- excessive shadows

The game should have visual texture and personality while remaining readable.

---

# 44. Design Layers

The visual system should be built in layers.

## Layer 1 — Structure

```text
GameShell
Sidebar
ResourceBar
Page Content
```

## Layer 2 — Visual Foundation

```text
Color system
Typography
Parchment
Borders
GamePanel
Buttons
Controls
Progress bars
```

## Layer 3 — Game Art

```text
Resource icons
Nation emblem
Settlement panorama
Process illustrations
Building illustrations
Location illustrations
Item illustrations
```

## Layer 4 — Page Composition

```text
Overview
Processes
Buildings
Nations
Locations
Items
Personal Tasks
```

## Layer 5 — Polish

```text
Greek ornaments
Laurels
Decorative frames
Corner details
Micro-interactions
Final spacing
Final visual balance
```

Do not solve all layers at once.

---

# 45. Redesign Roadmap

## Stage 1 — Game Shell

Status:

```text
COMPLETED
```

Implemented foundation:

- persistent Sidebar
- ResourceBar
- shared Page Content area
- reusable application shell

## Stage 2 — Visual Foundation

Current target.

Implement:

- final base color system
- dark navy / blue-black shell
- parchment content
- bronze/gold accents
- typography system
- GamePanel
- SectionHeader
- GameButton
- GameProgressBar
- StatusBadge
- form control styling
- consistent borders
- spacing
- depth system

Do NOT yet focus on major illustration work.

## Stage 3 — Game Art Layer

Introduce:

- final resource icons
- nation emblem integration
- settlement panorama
- process illustrations
- essential decorative assets

Replace temporary generic icons where appropriate.

## Stage 4 — Page-by-Page Redesign

Redesign page composition individually:

- Overview
- Processes
- Buildings
- Nations
- Locations
- Items
- Personal Tasks

Use the established Design System rather than creating new page-specific visual languages.

## Stage 5 — Final Polish

Add carefully:

- Greek ornamentation
- decorative borders
- laurels
- special separators
- corner details
- final hover states
- subtle micro-interactions
- final spacing adjustments

Decoration should be the final layer, not the foundation.

---

# 46. Final Design Test

Before accepting a UI change, ask:

### Identity

Does this look like part of an Ancient Greek / Hellenistic strategy game?

### Consistency

Does it use the established Design System?

### Functionality

Does it preserve existing game behavior?

### Readability

Can important information be understood quickly?

### Restraint

Is decoration supporting hierarchy rather than overwhelming it?

### Reuse

Could this UI pattern use an existing shared component?

### Atmosphere

Does the interface make managing the application feel like managing a civilization?

If several answers are "no", reconsider the implementation.
