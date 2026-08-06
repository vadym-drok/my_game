# Nation Simulator — Design Guide

## Philosophy

This project is a personal game, not a commercial web application.

The goal is not to build a generic dashboard, but to create a pleasant game-like interface that motivates daily use.

Every UI decision should make the application feel more like managing an ancient civilization than using an admin panel.

---

# Theme

## Visual inspiration

- Heroes of Might and Magic III
- Ikariam
- Travian

Do NOT copy their layouts.

Instead, borrow their atmosphere and visual language.

---

# World

The interface should feel like the working table of a ruler in the Hellenistic period.

Imagine:

- Alexandria
- libraries
- maps
- scrolls
- bronze tools
- old stone buildings
- wooden furniture
- military planning room
- chronicles

The user is not "editing data".

The user is ruling a civilization.

---

# Style

The UI should feel:

- warm
- calm
- historical
- elegant
- readable

Avoid flashy modern web styles.

---

# Materials

Use colors inspired by:

- bronze
- dark olive wood
- stone
- parchment
- aged paper

Avoid pure saturated colors.

---

# Colors

Preferred palette:

Background:
deep olive / dark green

Surface:
slightly lighter green

Primary:
warm green

Secondary:
bronze

Warning:
ochre

Danger:
terracotta

Text:
warm white

Secondary text:
muted parchment

---

# Buttons

Buttons should look like game controls, not Bootstrap buttons.

There should be only a few button styles:

- Primary
- Secondary
- Warning
- Danger
- Icon button

Every button of the same type should look identical across the entire project.

---

# Cards

Cards should look like information panels.

Use:

- subtle borders
- soft shadows
- comfortable spacing

Avoid excessive effects.

---

# Icons

Prefer icons over excessive text.

Use lucide-react.

Icons should support the interface, not decorate it.

---

# Animations

Animations should be subtle.

Prefer:

- hover
- soft transitions
- small color changes

Avoid:

- bounce
- glow
- large scaling
- flashy effects

---

# UX Principles

The project is designed for a single experienced user.

Do not simplify workflows for beginners.

Do not hide useful controls.

Fast interaction is more important than preventing mistakes.

---

# Development Rule

Every UI improvement should answer:

"Does this make the application feel more like an ancient civilization strategy game?"

If the answer is no, reconsider the design.
