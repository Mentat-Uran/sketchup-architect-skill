# Architectural design from an incomplete brief

This is an authored design method, not an official SketchUp architectural standard. The local official library grounds modeling behavior; researched real buildings ground design comparisons. Neither supplies site-specific planning law, structural calculations, or a universal building program.

## Establish the design basis

Separate **given**, **assumed**, **derived**, and **unresolved** facts. Capture building type, users/capacity, area meaning (site, footprint, gross floor area, or net usable), site dimensions/slope/access, north and climate if known, floors/height, key functions, style/material preferences, existing objects to retain, and expected deliverables.

If “600 m² building” is ambiguous, adopt gross floor area as a stated working assumption when context permits. Never silently treat the same number as both gross and net. Unknown north, terrain, boundaries, and climate remain provisional: pick a useful modeling orientation without inventing a real survey or location. A missing jurisdiction need not block a concept, but statutory setbacks, exit counts, accessibility dimensions, FAR, coverage, and fire ratings remain unverified.

Turn sparse input into a brief a person can assess: intended experience; activities and capacity; necessary support spaces; key constraints; a measurable success criterion. Avoid a long questionnaire. If area and requested capacity cannot fit, calculate the conflict and continue with a clearly stated feasible alternative within the user's priorities.

## Research the design questions before choosing a scheme

Once a provisional brief and core constraints are clear, follow [precedent research](precedent-research.md) before settling the spatial organization, volume or visual language. Search autonomously for relevant built work, inspect usable project documentation, and compare solutions to this task's actual problems. A preliminary area budget may help select comparable scales; it must not become a fixed scheme justified by cases found afterward.

Carry the synthesis into design as specific decisions: for example, separate an all-hours community threshold from supervised reading space, then test entrances and operating zones in the new plan. Explain conditions, tradeoffs and what is rejected. A precedent's room sizes, unusual roof, structural spans or material skin are not automatically suitable for a different site, climate, capacity or budget. Keep unsupported aspects unknown rather than filling case descriptions with architectural-sounding guesses.

## Program and area balance

Derive spaces from activities and operations, not a fixed room list. For each important space, reason from occupants, furniture/equipment, clearance and access. Include storage, toilets, circulation, service/plant and envelope/structure allowances appropriate to the type. Do not apply one net-to-gross ratio to every building.

Track at least gross counted area per floor and net program, circulation, service, and wall/structure area. Separate outdoor terraces, voids, double-height spaces, covered exterior zones and site works. An atrium occupies air on upper levels; do not count a nonexistent floor. Parking and basements need an explicit counting convention. State conceptual area conventions; replace them if the user provides a legal measurement standard.

Check `sum(net spaces + non-overlapping circulation/service + wall allowance)` against gross area. If the building does not fit the site or budget, change organization before adding facade detail. Favor a small number of dimensions that remain coordinated: floor elevations, structural bays, room depths, circulation widths and envelope thicknesses. Ratios and modules are outputs of reasoning, not compulsory generator parameters.

## Organize relations before shapes

Build an adjacency/access graph: public arrival, distribution, private or quiet zones, staff/service routes, deliveries and outdoor connections. Mark desired adjacencies and conflicts (noisy/quiet, clean/dirty, public/private). Trace a visitor, a daily user and a service person through the actual plan. Test vertical connections across all occupied levels; a graph edge between rooms is only a design intent until a physical door, passage, stair or lift is modeled.

Choose the organizing idea that resolves these relations: courtyard, linear bar, pavilion cluster, compact core, atrium, split levels, perimeter block, adaptive reuse, or another arrangement. These are options, not presets. Use the precedent comparison to generate and challenge options, not to dictate a silhouette. Where two arrangements offer a consequential tradeoff, compare their area fit, daylight opportunity, walking distance, structural simplicity, site use and spatial character. Select a direction and explain the tradeoff in a few sentences.

## Develop plan and section together

- Establish ground datum, floor-to-floor elevations, clear heights, roof depth and grade transitions.
- Lay out structure and spatial bays, then rooms, passages and envelope. Keep likely supports aligned vertically and explain deliberate transfers or cantilevers.
- Locate stairs/lifts early. Calculate stair rise and number of risers from actual level difference, then tread runs, landings, floor openings and headroom. A stacked stair-shaped object without an opening is not circulation. If universal access is part of the brief, trace a continuous step-free route and reserve actual lift/ramp space.
- Coordinate doors with furniture and approach space; windows with use, privacy and likely daylight. Glazing is not a substitute for wall openings. Put occupied depth, views and shading into the massing decision.
- For sloping sites, resolve arrival, finished floor elevations, retaining/terracing and drainage direction before smoothing terrain. Keep assumed terrain separate from measured survey data.

Structural dimensions are conceptual placeholders unless supplied or calculated by a qualified workflow. Explain the load path (roof/slab to beams/walls/columns to conceptual foundations), plausible span strategy and stability idea. Do not imply that visual alignment establishes structural adequacy. Flag exceptional spans and transfers as items for engineering refinement.

## Make form, facade and site follow the scheme

Compose volume from program and section: primary/secondary masses, voids, setbacks, roof silhouette and entrance legibility. Give solid/void balance, facade bay rhythm, base/body/roof relationships, material transitions and weather protection a reason. Vary openings according to space, orientation and privacy rather than random decoration. Limit materials to a coherent palette with scale-aware texture and joints where useful.

Connect building and site through thresholds, paths, gardens/courts, service access and usable outdoor places. Preserve context and requested landscape. Reserve drainage and servicing space conceptually; avoid pretending that an invented flat green slab is verified terrain.

## Completion at the requested stage

| Stage | Sufficient model information |
| --- | --- |
| Massing study | Site envelope, differentiated volumes/voids, levels, area logic, access concept and useful comparison views |
| Architectural scheme (default for “complete building”) | Real spatial layout, slabs/roof/walls, openings, usable circulation and stairs, conceptual structure, facade/material system, site relationships, furnished scale cues and readable plans/sections |
| Further development | Resolve requested assemblies/details and coordination issues without claiming construction certification |

Do not claim a full scheme if inaccessible rooms, missing services, blocked stairs, unaccounted floor area or exterior-only geometry remain. Record intentional simplifications such as symbolic sanitary fixtures, conceptual foundations and schematic MEP zones.

## Adapt across tasks

- Small house: derive privacy, family/common relations, wet-service clustering and outdoor living; do not import a public-building corridor pattern.
- Community/library/cafe: separate quiet/noisy activities, public arrival and back-of-house; size support facilities and outdoor spill-out with the program.
- Workplace/mixed use: distinguish tenant/public/service access, repeatable bays, cores and vertical stacking; preserve different ground and upper-floor needs.
- Retrofit: survey the current model first, distinguish retained/demolished/new elements, and let existing structure and circulation constrain the scheme.

For a follow-up such as “make the roof pitched and enlarge the cafe,” compute the area, section, structure, daylight and facade consequences; update affected elements and quantities while preserving the rest of the design.
