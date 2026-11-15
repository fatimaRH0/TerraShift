"""
crop_icons.py - One flat illustration per crop (inline SVG, 64x64), drawn for TerraShift.
No internet needed, no licence issue. Use icon(name, size) to get the <svg> string.
"""

BG = {  # soft background circle per crop
    "Wheat": "#FBF0D5", "Barley": "#F8EED8", "Oat": "#F4EFDF", "Maize": "#FCF3CF", "Sorghum": "#F8E3D8",
    "Chickpea": "#F6EBD9", "Lentil": "#F7E6D8", "Faba bean": "#E5F2DE", "Pea": "#E3F3DD", "Peanut": "#F3E8D8",
    "Potato": "#F1E7DA", "Tomato": "#FBE3DF", "Pepper": "#FBE1DD", "Onion": "#F2E3EE", "Carrot": "#FCE9D9",
    "Sugar beet": "#F3E1EA", "Sunflower": "#FDF3CC", "Rapeseed": "#FBF5CC", "Melon": "#EEF3D9",
    "Watermelon": "#E2F1E0", "Fallow": "#EFE7DD",
}

_GRAIN_EAR = lambda c, d: (  # an ear of grain: stem + pairs of kernels
    f'<path d="M32 58V22" stroke="#9A7B2F" stroke-width="2.4" stroke-linecap="round"/>'
    + "".join(f'<ellipse cx="{32 - 5.2}" cy="{y}" rx="4.2" ry="6.4" transform="rotate(-28 {26.8} {y})" fill="{c}"/>'
              f'<ellipse cx="{32 + 5.2}" cy="{y}" rx="4.2" ry="6.4" transform="rotate(28 {37.2} {y})" fill="{d}"/>'
              for y in (20, 29, 38, 47))
    + f'<ellipse cx="32" cy="13" rx="3.6" ry="6" fill="{c}"/>')

SVG = {
    "Wheat": _GRAIN_EAR("#E2B33C", "#D49B24") + '<path d="M28 50c-6 2-10 6-12 10M36 50c6 2 10 6 12 10" stroke="#8DB04A" stroke-width="2.4" fill="none" stroke-linecap="round"/>',
    "Barley": _GRAIN_EAR("#D9B866", "#C9A24D") + "".join(
        f'<path d="M{26 if i % 2 == 0 else 38} {18 + 9 * (i // 2)}l{-9 if i % 2 == 0 else 9} -12" stroke="#C9A24D" stroke-width="1.3" stroke-linecap="round"/>'
        for i in range(8)),
    "Oat": '<path d="M32 58V14" stroke="#A88A4A" stroke-width="2.2" stroke-linecap="round"/>' + "".join(
        f'<path d="M32 {y}q{s * 8} 2 {s * 10} 10" stroke="#A88A4A" stroke-width="1.6" fill="none"/>'
        f'<ellipse cx="{32 + s * 10}" cy="{y + 13}" rx="3.2" ry="5.2" fill="#DCC48A"/>'
        for y, s in ((14, -1), (19, 1), (26, -1), (31, 1), (38, -1))),
    "Maize": '<path d="M22 54c-4-12 0-30 10-40 10 10 14 28 10 40z" fill="#7FB04A"/>'
             '<path d="M32 12c-6 6-8 14-8 24s3 18 8 20c5-2 8-10 8-20s-2-18-8-24z" fill="#F2C536"/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="1.7" fill="#E0A81E"/>' for x in (29, 32, 35) for y in range(20, 52, 5))
             + '<path d="M18 58c2-10 8-16 14-18M46 58c-2-10-8-16-14-18" stroke="#5E9A3A" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "Sorghum": '<path d="M32 58V30" stroke="#7A9A3A" stroke-width="2.6" stroke-linecap="round"/>'
               '<path d="M32 40c-8-2-14 2-16 8M32 46c8-2 14 2 16 8" stroke="#7FB04A" stroke-width="3" fill="none" stroke-linecap="round"/>'
               + "".join(f'<circle cx="{32 + dx}" cy="{y}" r="3.1" fill="{c}"/>' for dx, y, c in
                         ((-6, 22, "#B5502E"), (0, 19, "#C2603A"), (6, 22, "#B5502E"), (-4, 14, "#C2603A"), (4, 14, "#B5502E"),
                          (0, 9, "#C2603A"), (-7, 28, "#A94A2B"), (7, 28, "#A94A2B"), (0, 26, "#C2603A"))),
    "Chickpea": '<path d="M14 40c0-12 10-20 22-18 9 2 14 10 12 18-2 10-14 14-24 11-6-2-10-6-10-11z" fill="#A9C46A"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#E8C98E"/><path d="M{x - 2} {y - 3}q3 -2 4 2" stroke="#C9A462" stroke-width="1.2" fill="none"/>'
                          for x, y in ((24, 44), (36, 46), (30, 34))),
    "Lentil": "".join(f'<ellipse cx="{x}" cy="{y}" rx="7" ry="4.6" fill="{c}"/>' for x, y, c in
                      ((22, 26, "#C9783E"), (36, 22, "#D88A4A"), (44, 34, "#C9783E"), (28, 38, "#D88A4A"),
                       (40, 46, "#C9783E"), (22, 48, "#D88A4A"), (32, 30, "#E09A5C"))),
    "Faba bean": '<path d="M12 44C12 26 30 14 50 16c4 0 4 6 0 8-14 6-22 16-26 28-4 6-12 2-12-8z" fill="#6FA845"/>'
                 '<path d="M16 42c2-12 14-20 30-22" stroke="#4F8A31" stroke-width="1.6" fill="none"/>'
                 + "".join(f'<ellipse cx="{x}" cy="{y}" rx="5" ry="6.4" fill="#A8D27A" transform="rotate(-40 {x} {y})"/>'
                           for x, y in ((22, 38), (31, 30), (40, 24))),
    "Pea": '<path d="M10 36c8-10 34-14 46-4-8 10-36 14-46 4z" fill="#5FA83E"/>'
           + "".join(f'<circle cx="{x}" cy="{34 - (x - 18) * 0.12:.1f}" r="5.4" fill="#9AD15E"/>' for x in (18, 28, 38, 47))
           + '<path d="M56 32c3-4 4-9 2-13" stroke="#5FA83E" stroke-width="2" fill="none" stroke-linecap="round"/>',
    "Peanut": '<path d="M24 14c8 0 12 6 11 12-1 4 0 7 3 10 5 5 4 16-6 18-9 2-14-4-14-10 0-4 2-7 1-10-3-8-1-20 5-20z" fill="#D9AE73"/>'
              '<path d="M22 22h8M21 30h9M26 44h10M27 50h8" stroke="#BE9157" stroke-width="1.4" stroke-linecap="round"/>',
    "Potato": '<path d="M14 36c0-12 12-20 24-18 10 2 14 10 12 18-2 10-14 16-24 14-8-2-12-8-12-14z" fill="#C8955C"/>'
              + "".join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#8E6236"/>' for x, y in ((24, 30), (36, 27), (40, 38), (28, 42), (20, 37))),
    "Tomato": '<circle cx="32" cy="36" r="18" fill="#E5483B"/><path d="M22 30c2-6 8-9 12-9" stroke="#F7887E" stroke-width="3" fill="none" stroke-linecap="round"/>'
              '<path d="M32 20l-5-5 2 7-8-1 7 4 4 0 4 0 7-4-8 1 2-7z" fill="#4E9A3A"/><path d="M32 18v-6" stroke="#4E9A3A" stroke-width="2.4" stroke-linecap="round"/>',
    "Pepper": '<path d="M24 20c-6 4-8 14-6 24 2 8 8 14 14 14s12-6 13-14c2-10 0-20-6-24-4-2-11-2-15 0z" fill="#E0402F"/>'
              '<path d="M26 26c-2 6-2 14 0 20" stroke="#F58A7C" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
              '<path d="M24 20c4-3 12-3 16 0l-3-4h-10z" fill="#4E9A3A"/><path d="M32 16c0-4 2-7 6-8" stroke="#4E9A3A" stroke-width="2.6" fill="none" stroke-linecap="round"/>',
    "Onion": '<path d="M32 14c-4 8-16 14-16 28 0 9 7 16 16 16s16-7 16-16c0-14-12-20-16-28z" fill="#A9487C"/>'
             '<path d="M32 18c-2 8-8 14-8 24M32 18c2 8 8 14 8 24" stroke="#C878A2" stroke-width="1.6" fill="none"/>'
             '<path d="M32 14V6M30 8l2-2 2 2" stroke="#6FA845" stroke-width="2.2" stroke-linecap="round" fill="none"/>'
             '<path d="M27 57l-2 4M32 58v4M37 57l2 4" stroke="#C8B79A" stroke-width="1.4" stroke-linecap="round"/>',
    "Carrot": '<path d="M24 24l18 4c-4 10-12 22-22 32-2 2-4 0-3-2 2-12 4-24 7-34z" fill="#F08A2C"/>'
              '<path d="M26 32l6 2M24 40l5 2M22 48l4 1" stroke="#D2701C" stroke-width="1.6" stroke-linecap="round"/>'
              '<path d="M33 25c-2-8 0-14 4-18M36 26c2-8 8-12 14-12M34 25c4-6 10-6 14-4" stroke="#5FA83E" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "Sugar beet": '<path d="M18 30c0-8 6-12 14-12s14 4 14 12c0 10-6 20-14 30-8-10-14-20-14-30z" fill="#EFE3D3"/>'
                  '<path d="M18 30c0-8 6-12 14-12s14 4 14 12" fill="#B5527F" opacity=".35"/>'
                  '<path d="M26 34c2 8 4 14 6 20" stroke="#D9C6AE" stroke-width="1.6" fill="none"/>'
                  '<path d="M30 18c-6-8-14-10-18-6 4 6 12 8 18 6zM34 18c6-8 14-10 18-6-4 6-12 8-18 6zM32 18c0-8 2-12 6-14" fill="#5FA83E" stroke="#5FA83E" stroke-width="1.5"/>',
    "Sunflower": "".join(f'<ellipse cx="32" cy="16" rx="5" ry="10" fill="#F6C531" transform="rotate({a} 32 30)"/>' for a in range(0, 360, 30))
                 + '<circle cx="32" cy="30" r="10" fill="#7A4E2A"/>'
                 + "".join(f'<circle cx="{32 + dx}" cy="{30 + dy}" r="1.3" fill="#5A361C"/>' for dx, dy in ((-4, -3), (3, -4), (5, 2), (-2, 5), (0, 0), (-5, 2)))
                 + '<path d="M32 40v20" stroke="#5FA83E" stroke-width="3" stroke-linecap="round"/>',
    "Rapeseed": '<path d="M32 60V24M32 40l-10-8M32 46l10-8" stroke="#6FA845" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
                + "".join(f'<g transform="translate({x} {y})">' + "".join(
                    f'<ellipse cx="0" cy="-3.4" rx="2.4" ry="3.6" fill="#F5D530" transform="rotate({a})"/>' for a in (0, 90, 180, 270))
                          + '<circle r="1.6" fill="#E3A915"/></g>' for x, y in ((32, 16), (24, 22), (40, 22), (22, 31), (42, 31), (32, 26))),
    "Melon": '<circle cx="32" cy="36" r="19" fill="#C9D27C"/>'
             '<path d="M18 26c8 4 20 4 28 0M14 36c10 4 26 4 36 0M18 46c8 4 20 4 28 0M32 17c-6 8-6 30 0 38M32 17c6 8 6 30 0 38" stroke="#A3AE4E" stroke-width="1.4" fill="none"/>'
             '<path d="M32 17v-6" stroke="#6FA845" stroke-width="2.4" stroke-linecap="round"/>',
    "Watermelon": '<path d="M8 30h48c0 14-11 24-24 24S8 44 8 30z" fill="#3E8A3A"/>'
                  '<path d="M12 30h40c0 11-9 19-20 19s-20-8-20-19z" fill="#EF5A55"/>'
                  + "".join(f'<ellipse cx="{x}" cy="{y}" rx="1.4" ry="2.2" fill="#2B2B2B"/>' for x, y in ((22, 36), (30, 41), (38, 36), (34, 34), (26, 34), (42, 40)))
                  + '<path d="M12 30h40" stroke="#BFE3A5" stroke-width="2"/>',
    "Fallow": '<path d="M8 44c8-4 16-4 24 0s16 4 24 0v12H8z" fill="#9C7451"/>'
              '<path d="M8 50c8-3 16-3 24 0s16 3 24 0" stroke="#7E5A3B" stroke-width="1.6" fill="none"/>'
              '<path d="M32 44V30" stroke="#6FA845" stroke-width="2.4" stroke-linecap="round"/>'
              '<path d="M32 34c-6 0-10-4-10-9 6 0 10 4 10 9zM32 32c6 0 10-4 10-9-6 0-10 4-10 9z" fill="#7FB04A"/>',
}


def icon(name, size=48):
    """<svg> of the crop in a soft circle (falls back to a sprout)."""
    body = SVG.get(name, SVG["Fallow"])
    bg = BG.get(name, "#EEF1EC")
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" role="img" aria-label="{name}">'
            f'<circle cx="32" cy="32" r="32" fill="{bg}"/>{body}</svg>')
