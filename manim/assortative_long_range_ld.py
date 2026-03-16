"""
Manim scene for teaching assortative mating and long-range linkage disequilibrium.

This file intentionally mirrors the teaching style of
`mendelian_inheritance_v2.py`:
1. Edit the small deterministic example at the top.
2. Render a quick draft while you tune the pacing.
3. Render a higher-quality version once the lecture flow feels right.

Common render commands from the project root:
    manim -pql manim/assortative_long_range_ld.py AssortativeLongRangeLDScene
    python -m manim -pql manim/assortative_long_range_ld.py AssortativeLongRangeLDScene

Higher quality:
    manim -pqh manim/assortative_long_range_ld.py AssortativeLongRangeLDScene

To export multiple MP4 files at explicit cut points:
    manim --save_sections --format=mp4 --fps 30 -r 1280,720 \
        manim/assortative_long_range_ld.py AssortativeLongRangeLDScene

Note:
    In this local environment, `python` or `manim` may not be on PATH.
    If so, run the same command with the explicit Python interpreter that has
    Manim installed.
"""

from manim import *
import numpy as np


# ---------------------------------------------------------------------------
# Top-level configuration block
# ---------------------------------------------------------------------------
# Candidate phenotypes for the initial assortative-mating step.
# We keep the example tiny and deterministic so the pairing pattern is easy to
# follow during a lecture.
PATERNAL_CANDIDATES = [
    {"label": "P1", "y": 1.2, "g": 0.8, "e": 0.4},
    {"label": "P2", "y": 1.9, "g": 1.2, "e": 0.7},
    {"label": "P3", "y": 2.5, "g": 1.7, "e": 0.8},
    {"label": "P4", "y": 3.1, "g": 2.2, "e": 0.9},
    {"label": "P5", "y": 4.0, "g": 2.8, "e": 1.2},
]

MATERNAL_CANDIDATES = [
    {"label": "M1", "y": 3.0, "g": 2.0, "e": 1.0},
    {"label": "M2", "y": 1.1, "g": 0.7, "e": 0.4},
    {"label": "M3", "y": 2.4, "g": 1.6, "e": 0.8},
    {"label": "M4", "y": 4.1, "g": 2.9, "e": 1.2},
    {"label": "M5", "y": 1.8, "g": 1.1, "e": 0.7},
]

# After positive assortment, paternal row i is paired with maternal candidate
# ASSORTED_PAIR_ORDER[i]. We do not estimate a sample correlation from five
# people; we simply use this fixed ordering to illustrate the conceptual target
# Corr(y_m, y_p) = mu > 0.
ASSORTED_PAIR_ORDER = [1, 4, 2, 0, 3]
ASSORTMENT_MU_LABEL = r"\mu>0"

# Genome toy example used after the phenotype step.
# There are 10 loci in total, with five trait-relevant loci spread across the
# row. Interleaving relevant and neutral loci makes the later contrast much
# clearer than placing all relevant loci in one block.
NUM_LOCI = 10
TRAIT_RELEVANT_LOCI = [0, 2, 4, 6, 8]
NEUTRAL_LOCI = [1, 3, 5, 7, 9]

# One focal trait locus and one focal neutral locus used for the locus-view
# section. These are zero-based indices in the code.
FOCAL_TRAIT_LOCUS = 4
FOCAL_NEUTRAL_LOCUS = 3

# Fixed parental haplotypes inherited by the offspring in the worked example.
# They are already "post-assortment" in the pedagogical sense:
# relevant loci are the ones whose cross-mate correlation we want to explain.
PATERNAL_TRANSMITTED_HAPLOTYPE = [1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
MATERNAL_TRANSMITTED_HAPLOTYPE = [0, 1, 1, 0, 1, 1, 1, 0, 1, 1]

# Fixed recombination pattern for the next generation.
# 0 means "copy from the offspring's paternal haplotype row".
# 1 means "copy from the offspring's maternal haplotype row".
RECOMBINATION_SOURCE_PATTERN = [0, 0, 1, 1, 0, 0, 1, 1, 1, 1]
RECOMBINATION_BREAKS = [2, 4, 6]

# Timing stays separate from the animation logic so the lecture can be sped up
# or slowed down without rewriting the teaching structure.
TIMING = {
    "short_pause": 1.0,
    "medium_pause": 1.8,
    "long_pause": 2.8,
    "pair_move": 0.95,
    "corr_step": 0.9,
    "segment_step": 0.8,
}

# Semantic color roles make it easier to extend the file later.
COLORS = {
    "paternal": BLUE_E,
    "maternal": TEAL_E,
    "phenotype": WHITE,
    "genetic": GREEN_E,
    "environment": ORANGE,
    "trait_locus": GOLD_E,
    "neutral_locus": GREY_B,
    "highlight": YELLOW,
    "muted": GREY_C,
    "trans": PURPLE_B,
    "cis": GREEN_B,
    "gamete": MAROON_B,
    "note": GREY_B,
    "title": WHITE,
}

# Layout constants keep the spatial logic stable.
# The left side hosts the main objects being explained.
# The right side hosts notes and equations that can change without moving the
# core visual story around.
LAYOUT = {
    "paternal_column_x": -3.55,
    "maternal_column_x": -0.75,
    "cards_center_y": 0.0,
    "card_width": 2.28,
    "card_height": 1.12,
    "card_gap": 0.16,
    "card_label_y": 0.32,
    "card_line_gap": 0.05,
    "card_contents_shift": 0.02,
    "right_panel_center": np.array([4.05, 0.85, 0.0]),
    "right_panel_max_width": 4.85,
    "legend_center": np.array([4.0, -2.15, 0.0]),
    "cells_center_x": -1.6,
    "label_buffer": 0.44,
    "cell_gap": 0.09,
    "cell_width": 0.58,
    "cell_height": 0.54,
    "locus_label_y_offset": 0.20,
    "genome_paternal_y": 0.95,
    "genome_maternal_y": -0.05,
    "genome_gamete_y": -1.65,
}

# If True, calls to self.mark_video_split(...) create new section files when
# rendered with --save_sections.
ENABLE_VIDEO_SPLITS = True


def format_decimal(value):
    """Return one decimal place for the small worked example."""
    return f"{value:.1f}"


def apply_source_pattern(upper_values, lower_values, source_pattern):
    """Build the deterministic mosaic haplotype implied by a source pattern."""
    return [
        upper if source == 0 else lower
        for upper, lower, source in zip(upper_values, lower_values, source_pattern)
    ]


def compute_contiguous_segments(source_pattern):
    """
    Group a recombination source pattern into contiguous chunks.

    This lets the animation move segment-by-segment rather than one SNP at a
    time, which is both clearer and closer to how recombination is usually
    described pedagogically.
    """
    segments = []
    start = 0
    current_source = source_pattern[0]

    for index in range(1, len(source_pattern) + 1):
        if index == len(source_pattern) or source_pattern[index] != current_source:
            segments.append(
                {
                    "start": start,
                    "end": index - 1,
                    "source": current_source,
                }
            )
            if index < len(source_pattern):
                start = index
                current_source = source_pattern[index]

    return segments


class AssortativeLongRangeLDScene(Scene):
    """
    One master scene composed of pedagogical sections.

    The visual structure follows the same philosophy as the Mendelian
    inheritance scene:
    - left side: the main worked example
    - right side: compact notes and equations
    - section methods: one conceptual step per method
    """

    def construct(self):
        # -------------------------------------------------------------------
        # Prepare data once at the top.
        # -------------------------------------------------------------------
        self.paternal_candidates = PATERNAL_CANDIDATES
        self.maternal_candidates = MATERNAL_CANDIDATES
        self.assorted_pair_order = ASSORTED_PAIR_ORDER
        self.assorted_maternal_candidates = [
            self.maternal_candidates[index] for index in self.assorted_pair_order
        ]

        self.trait_relevant_loci = TRAIT_RELEVANT_LOCI
        self.neutral_loci = NEUTRAL_LOCI
        self.focal_trait_locus = FOCAL_TRAIT_LOCUS
        self.focal_neutral_locus = FOCAL_NEUTRAL_LOCUS

        self.paternal_haplotype = PATERNAL_TRANSMITTED_HAPLOTYPE
        self.maternal_haplotype = MATERNAL_TRANSMITTED_HAPLOTYPE
        self.recombination_pattern = RECOMBINATION_SOURCE_PATTERN
        self.recombination_breaks = RECOMBINATION_BREAKS
        self.recombination_segments = compute_contiguous_segments(self.recombination_pattern)
        self.mosaic_haplotype = apply_source_pattern(
            self.paternal_haplotype,
            self.maternal_haplotype,
            self.recombination_pattern,
        )

        self.active_note = None

        # Build recurring objects once so later sections only change emphasis.
        self.build_static_layout()

        # Section-by-section teaching flow.
        self.play_intro_assortment()
        self.play_component_decomposition()

        self.mark_video_split("part_02_trait_specificity_to_locus")

        self.play_trait_specificity()
        self.play_locus_view()
        self.play_offspring_trans_view()

        self.mark_video_split("part_03_recombination_to_summary")

        self.play_recombination_to_cis()
        self.play_gwas_summary()

    # -----------------------------------------------------------------------
    # General helper methods
    # -----------------------------------------------------------------------
    def mark_video_split(self, section_name):
        """Start a new output section when rendering with --save_sections."""
        if ENABLE_VIDEO_SPLITS:
            self.next_section(section_name)

    def color_equation(self, equation):
        """
        Apply a consistent color language across equations and note panels.

        Keeping a small, repeated color vocabulary matters pedagogically: the
        audience can learn the code once and then spend attention on the idea.
        """
        equation.set_color_by_tex("y", COLORS["phenotype"])
        equation.set_color_by_tex("g", COLORS["genetic"])
        equation.set_color_by_tex("e", COLORS["environment"])
        equation.set_color_by_tex(r"\mu", COLORS["highlight"])
        equation.set_color_by_tex("T", COLORS["trait_locus"])
        equation.set_color_by_tex(r"\hat b_j^{\mathrm{marg}}", COLORS["highlight"])
        equation.set_color_by_tex(r"\beta_j", COLORS["trait_locus"])
        equation.set_color_by_tex(r"r_{jk}", COLORS["trans"])
        equation.set_color_by_tex(r"\beta_k", COLORS["trait_locus"])
        return equation

    def make_right_panel_note(self, *lines, center=None):
        """Create the fixed right-side teaching panel used throughout the scene."""
        note_lines = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        if note_lines.width > LAYOUT["right_panel_max_width"]:
            note_lines.scale_to_fit_width(LAYOUT["right_panel_max_width"])
        background = BackgroundRectangle(
            note_lines,
            buff=0.22,
            fill_opacity=0.12,
            stroke_opacity=0.0,
        )
        panel = VGroup(background, note_lines)
        panel.move_to(LAYOUT["right_panel_center"] if center is None else center)
        return panel

    def swap_note(self, new_note):
        """Replace the current right-panel note without moving the main objects."""
        if self.active_note is None:
            self.play(FadeIn(new_note, shift=0.10 * UP), run_time=0.6)
        else:
            self.play(
                FadeOut(self.active_note, shift=0.10 * DOWN),
                FadeIn(new_note, shift=0.10 * UP),
                run_time=0.6,
            )
        self.active_note = new_note

    def make_phenotype_card(self, person_data, box_color):
        """
        Build one phenotype card with y, g, and e.

        The card is created in its fully informative form, but the g/e lines
        start hidden. That lets Section 2 reveal the decomposition without
        changing the card layout itself.
        """
        box = RoundedRectangle(
            corner_radius=0.08,
            width=LAYOUT["card_width"],
            height=LAYOUT["card_height"],
            stroke_color=box_color,
            stroke_width=2.0,
            fill_color=box_color,
            fill_opacity=0.08,
        )

        header = Text(person_data["label"], font_size=20, color=box_color)

        y_line = MathTex(
            "y",
            "=",
            format_decimal(person_data["y"]),
            font_size=28,
        )
        y_line[0].set_color(COLORS["phenotype"])

        g_line = MathTex(
            "g",
            "=",
            format_decimal(person_data["g"]),
            font_size=24,
        )
        g_line[0].set_color(COLORS["genetic"])

        e_line = MathTex(
            "e",
            "=",
            format_decimal(person_data["e"]),
            font_size=24,
        )
        e_line[0].set_color(COLORS["environment"])

        line_group = VGroup(header, y_line, g_line, e_line).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=LAYOUT["card_line_gap"],
        )
        line_group.move_to(box.get_center() + DOWN * LAYOUT["card_contents_shift"])
        line_group.align_to(box, LEFT).shift(RIGHT * 0.18)

        component_group = VGroup(g_line, e_line)
        component_group.set_opacity(0.0)

        group = VGroup(box, line_group)

        return {
            "box": box,
            "header": header,
            "y_line": y_line,
            "g_line": g_line,
            "e_line": e_line,
            "component_group": component_group,
            "group": group,
            "data": person_data,
        }

    def build_candidate_column(self, people, heading_text, box_color, column_x):
        """Build one vertically aligned candidate column for the mate-sorting step."""
        cards = [self.make_phenotype_card(person, box_color) for person in people]
        cards_group = VGroup(*[card["group"] for card in cards]).arrange(
            DOWN,
            buff=LAYOUT["card_gap"],
        )

        heading = Text(heading_text, font_size=24, color=box_color)
        column_group = VGroup(heading, cards_group).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.22,
        )
        column_group.move_to(np.array([column_x, LAYOUT["cards_center_y"], 0.0]))

        return {
            "heading": heading,
            "cards": cards,
            "cards_group": cards_group,
            "group": column_group,
        }

    def make_pair_connector(self, left_card, right_card, color):
        """Create one clean horizontal pairing link between two matched mates."""
        return Line(
            left_card["box"].get_right() + RIGHT * 0.02,
            right_card["box"].get_left() + LEFT * 0.02,
            color=color,
            stroke_width=3.0,
        )

    def make_locus_cell(self, value, row_color, locus_index):
        """
        Build one boxed locus cell.

        Each cell shows two different ideas at once:
        - row identity: outer stroke color (paternal, maternal, or gamete)
        - locus type: inner fill color (trait-relevant vs neutral)
        """
        outer_box = RoundedRectangle(
            corner_radius=0.06,
            width=LAYOUT["cell_width"],
            height=LAYOUT["cell_height"],
            stroke_color=row_color,
            stroke_width=2.0,
            fill_color=row_color,
            fill_opacity=0.08,
        )

        locus_fill_color = (
            COLORS["trait_locus"]
            if locus_index in self.trait_relevant_loci
            else COLORS["neutral_locus"]
        )
        locus_fill_opacity = 0.24 if locus_index in self.trait_relevant_loci else 0.14

        inner_fill = RoundedRectangle(
            corner_radius=0.05,
            width=LAYOUT["cell_width"] * 0.82,
            height=LAYOUT["cell_height"] * 0.72,
            stroke_width=0.0,
            fill_color=locus_fill_color,
            fill_opacity=locus_fill_opacity,
        )
        inner_fill.move_to(outer_box.get_center())

        if value is not None:
            entry = MathTex(str(value), font_size=28)
            entry.move_to(outer_box.get_center())
        else:
            entry = VectorizedPoint(outer_box.get_center())

        group = VGroup(outer_box, inner_fill, entry)

        return {
            "box": outer_box,
            "inner_fill": inner_fill,
            "entry": entry,
            "group": group,
            "value": value,
            "locus_index": locus_index,
        }

    def make_haplotype_row(self, values, label_tex, row_color):
        """Build one labeled haplotype row for the genome sections."""
        label = MathTex(label_tex, font_size=30)
        label.set_color(row_color)

        cells = [
            self.make_locus_cell(value, row_color, locus_index)
            for locus_index, value in enumerate(values)
        ]

        cells_group = VGroup(*[cell["group"] for cell in cells]).arrange(
            RIGHT,
            buff=LAYOUT["cell_gap"],
        )

        return {
            "label": label,
            "cells": cells,
            "cells_group": cells_group,
            "group": VGroup(label, cells_group),
            "row_color": row_color,
        }

    def position_row(self, row, y_coordinate):
        """Align a row so later sections can swap labels without moving cells."""
        row["cells_group"].move_to(np.array([LAYOUT["cells_center_x"], y_coordinate, 0.0]))
        row["label"].next_to(row["cells_group"], LEFT, buff=LAYOUT["label_buffer"])
        row["group"] = VGroup(row["label"], row["cells_group"])

    def build_locus_labels(self, reference_row):
        """Create one small locus label above each cell."""
        labels = VGroup()
        for locus_index, cell in enumerate(reference_row["cells"], start=1):
            label = MathTex(fr"j={locus_index}", font_size=22)
            label.next_to(cell["box"], UP, buff=LAYOUT["locus_label_y_offset"])
            labels.add(label)
        return labels

    def mark_trait_relevant_loci(self):
        """
        Build a legend and a set of subtle emphasis objects for locus types.

        The row already encodes locus type through color, but the extra legend
        makes the contrast explicit exactly when the lecture needs it.
        """
        relevant_chip = RoundedRectangle(
            corner_radius=0.05,
            width=0.44,
            height=0.34,
            stroke_width=0.0,
            fill_color=COLORS["trait_locus"],
            fill_opacity=0.28,
        )
        neutral_chip = RoundedRectangle(
            corner_radius=0.05,
            width=0.44,
            height=0.34,
            stroke_width=0.0,
            fill_color=COLORS["neutral_locus"],
            fill_opacity=0.18,
        )

        relevant_label = Text("trait-relevant locus", font_size=22)
        neutral_label = Text("unrelated locus", font_size=22, color=COLORS["muted"])

        relevant_item = VGroup(relevant_chip, relevant_label).arrange(RIGHT, buff=0.18)
        neutral_item = VGroup(neutral_chip, neutral_label).arrange(RIGHT, buff=0.18)
        legend = VGroup(relevant_item, neutral_item).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.20,
        )

        background = BackgroundRectangle(
            legend,
            buff=0.18,
            fill_opacity=0.10,
            stroke_opacity=0.0,
        )
        panel = VGroup(background, legend)
        panel.move_to(LAYOUT["legend_center"])

        relevant_pulses = VGroup(
            *[
                SurroundingRectangle(
                    self.paternal_row["cells"][index]["group"],
                    color=COLORS["trait_locus"],
                    buff=0.05,
                    stroke_width=2.0,
                )
                for index in self.trait_relevant_loci
            ],
            *[
                SurroundingRectangle(
                    self.maternal_row["cells"][index]["group"],
                    color=COLORS["trait_locus"],
                    buff=0.05,
                    stroke_width=2.0,
                )
                for index in self.trait_relevant_loci
            ],
        )

        neutral_pulses = VGroup(
            *[
                SurroundingRectangle(
                    self.paternal_row["cells"][index]["group"],
                    color=COLORS["muted"],
                    buff=0.05,
                    stroke_width=1.5,
                )
                for index in self.neutral_loci
            ],
            *[
                SurroundingRectangle(
                    self.maternal_row["cells"][index]["group"],
                    color=COLORS["muted"],
                    buff=0.05,
                    stroke_width=1.5,
                )
                for index in self.neutral_loci
            ],
        )

        return {
            "panel": panel,
            "relevant_pulses": relevant_pulses,
            "neutral_pulses": neutral_pulses,
        }

    def highlight_focal_locus(self, row, locus_index, label_tex, color):
        """Highlight one focal locus and annotate it with a short label."""
        focus_box = SurroundingRectangle(
            row["cells"][locus_index]["group"],
            color=color,
            buff=0.07,
            stroke_width=3.0,
        )

        label = MathTex(label_tex, font_size=28)
        label.set_color(color)
        label.next_to(focus_box, UP, buff=0.10)

        return {"box": focus_box, "label": label}

    def draw_correlation_links(
        self,
        source_mobjects,
        target_mobjects,
        color,
        stroke_width=3.0,
        tip=False,
        pairwise=False,
        vertical=False,
    ):
        """
        Draw clean link objects between sources and targets.

        The helper supports three common cases used in this file:
        - pairwise links between two aligned columns of phenotype components
        - one-to-many links from one focal locus to many loci in the other parent
        - simple between-row links for the trans-correlation section
        """
        links = VGroup()

        if pairwise:
            pairs = list(zip(source_mobjects, target_mobjects))
        elif len(source_mobjects) == 1:
            pairs = [(source_mobjects[0], target) for target in target_mobjects]
        elif len(target_mobjects) == 1:
            pairs = [(source, target_mobjects[0]) for source in source_mobjects]
        else:
            pairs = [(source, target) for source in source_mobjects for target in target_mobjects]

        for pair_index, (source, target) in enumerate(pairs):
            if vertical:
                link = Line(
                    source.get_bottom(),
                    target.get_top(),
                    color=color,
                    stroke_width=stroke_width,
                )
            else:
                start = source.get_right() if source.get_center()[0] <= target.get_center()[0] else source.get_left()
                end = target.get_left() if source.get_center()[0] <= target.get_center()[0] else target.get_right()
                dx = target.get_center()[0] - source.get_center()[0]
                bend = 0.22 if dx >= 0 else -0.22
                bend += 0.02 * (pair_index - 1.5)
                link = ArcBetweenPoints(
                    start,
                    end,
                    angle=bend,
                    color=color,
                    stroke_width=stroke_width,
                )
                if tip:
                    tip_mob = ArrowTriangleFilledTip(length=0.12, width=0.12)
                    tip_mob.set_fill(color)
                    tip_mob.set_stroke(color)
                    tip_mob.move_to(link.point_from_proportion(1.0))
                    tip_mob.rotate(link.get_angle())
                    link = VGroup(link, tip_mob)
            links.add(link)

        return links

    def make_recombination_mosaic(self):
        """
        Build the blank target row plus reusable segment metadata.

        The recombination animation later copies chunks from the two source
        haplotypes into this target row. We precompute the segment geometry here
        so Section 6 can focus on the teaching logic.
        """
        gamete_row = self.make_haplotype_row(
            [None] * NUM_LOCI,
            r"\text{next-gen gamete}",
            COLORS["gamete"],
        )
        self.position_row(gamete_row, LAYOUT["genome_gamete_y"])

        segments = []
        for segment in self.recombination_segments:
            start = segment["start"]
            end = segment["end"]
            source_row = self.paternal_row if segment["source"] == 0 else self.maternal_row

            source_group = VGroup(
                *[source_row["cells"][index]["group"] for index in range(start, end + 1)]
            )
            target_group = VGroup(
                *[gamete_row["cells"][index]["group"] for index in range(start, end + 1)]
            )

            source_highlight = SurroundingRectangle(
                source_group,
                color=source_row["row_color"],
                buff=0.06,
                stroke_width=3.0,
            )
            target_highlight = SurroundingRectangle(
                target_group,
                color=COLORS["gamete"],
                buff=0.06,
                stroke_width=3.0,
            )
            transfer_arrow = Arrow(
                source_group.get_bottom(),
                target_group.get_top(),
                color=COLORS["gamete"],
                stroke_width=4.0,
                buff=0.10,
                max_tip_length_to_length_ratio=0.18,
            )

            segments.append(
                {
                    "start": start,
                    "end": end,
                    "source": segment["source"],
                    "source_row": source_row,
                    "source_group": source_group,
                    "target_group": target_group,
                    "source_highlight": source_highlight,
                    "target_highlight": target_highlight,
                    "transfer_arrow": transfer_arrow,
                }
            )

        crossover_lines = VGroup()
        crossover_labels = VGroup()
        for break_index in self.recombination_breaks:
            left_box = gamete_row["cells"][break_index - 1]["box"]
            right_box = gamete_row["cells"][break_index]["box"]
            x_coordinate = 0.5 * (left_box.get_right()[0] + right_box.get_left()[0])
            top_y = self.paternal_row["cells"][0]["box"].get_top()[1] + 0.18
            bottom_y = gamete_row["cells"][0]["box"].get_bottom()[1] - 0.18

            crossover_line = DashedLine(
                start=np.array([x_coordinate, top_y, 0.0]),
                end=np.array([x_coordinate, bottom_y, 0.0]),
                color=COLORS["highlight"],
                dash_length=0.08,
                dashed_ratio=0.60,
                stroke_width=3.0,
            )
            crossover_label = Text(
                "xover",
                font_size=18,
                color=COLORS["highlight"],
            )
            crossover_label.next_to(crossover_line, DOWN, buff=0.10)

            crossover_lines.add(crossover_line)
            crossover_labels.add(crossover_label)

        return {
            "row": gamete_row,
            "segments": segments,
            "crossover_lines": crossover_lines,
            "crossover_labels": crossover_labels,
        }

    def build_static_layout(self):
        """Build the recurring objects used across the whole scene."""
        self.paternal_column = self.build_candidate_column(
            self.paternal_candidates,
            "Potential fathers",
            COLORS["paternal"],
            LAYOUT["paternal_column_x"],
        )
        self.maternal_column = self.build_candidate_column(
            self.maternal_candidates,
            "Potential mothers",
            COLORS["maternal"],
            LAYOUT["maternal_column_x"],
        )

        self.maternal_slot_positions = [
            card["group"].get_center().copy() for card in self.maternal_column["cards"]
        ]
        self.maternal_cards_by_slot = [
            self.maternal_column["cards"][candidate_index]
            for candidate_index in self.assorted_pair_order
        ]

        self.paternal_row = self.make_haplotype_row(
            self.paternal_haplotype,
            r"\text{father trait haplotype}",
            COLORS["paternal"],
        )
        self.maternal_row = self.make_haplotype_row(
            self.maternal_haplotype,
            r"\text{mother trait haplotype}",
            COLORS["maternal"],
        )
        self.position_row(self.paternal_row, LAYOUT["genome_paternal_y"])
        self.position_row(self.maternal_row, LAYOUT["genome_maternal_y"])

        self.locus_labels = self.build_locus_labels(self.paternal_row)
        self.genome_panel = VGroup(
            self.locus_labels,
            self.paternal_row["group"],
            self.maternal_row["group"],
        )

        self.locus_type_objects = self.mark_trait_relevant_loci()

        self.mosaic_setup = self.make_recombination_mosaic()

    # -----------------------------------------------------------------------
    # Section 1: assortative mating on phenotype
    # -----------------------------------------------------------------------
    def play_intro_assortment(self):
        self.wait(TIMING["short_pause"] * 0.5)

        intro_note = self.make_right_panel_note(
            Text("Positive assortment pairs similar phenotypes.", font_size=26),
            self.color_equation(
                MathTex(
                    r"\mathrm{Corr}(y_m,y_p)=" + ASSORTMENT_MU_LABEL,
                    font_size=36,
                )
            ),
        )

        self.play(
            FadeIn(self.paternal_column["heading"], shift=0.12 * UP),
            FadeIn(self.maternal_column["heading"], shift=0.12 * UP),
            run_time=0.8,
        )
        self.play(
            LaggedStart(
                *[FadeIn(card["group"], shift=0.14 * RIGHT) for card in self.paternal_column["cards"]],
                lag_ratio=0.08,
            ),
            LaggedStart(
                *[FadeIn(card["group"], shift=0.14 * RIGHT) for card in self.maternal_column["cards"]],
                lag_ratio=0.08,
            ),
            run_time=1.4,
        )
        self.swap_note(intro_note)
        self.wait(TIMING["medium_pause"])

        # The core visual move: maternal cards slide into the order implied by
        # positive assortment. We keep the paternal side fixed so the viewer can
        # see that the pairing pattern, not the paternal distribution, changes.
        move_animations = []
        for slot_index, card in enumerate(self.maternal_cards_by_slot):
            move_animations.append(
                card["group"].animate.move_to(self.maternal_slot_positions[slot_index])
            )

        sorting_note = self.make_right_panel_note(
            Text("Match low with low, high with high.", font_size=26),
            self.color_equation(
                MathTex(
                    r"\mathrm{Corr}(y_m,y_p)=" + ASSORTMENT_MU_LABEL,
                    font_size=36,
                )
            ),
        )

        self.swap_note(sorting_note)
        self.play(
            LaggedStart(*move_animations, lag_ratio=0.12),
            run_time=TIMING["pair_move"] * 1.5,
        )

        self.pair_connectors = VGroup(
            *[
                self.make_pair_connector(
                    self.paternal_column["cards"][slot_index],
                    self.maternal_cards_by_slot[slot_index],
                    COLORS["highlight"],
                )
                for slot_index in range(len(self.paternal_column["cards"]))
            ]
        )

        self.play(Create(self.pair_connectors), run_time=0.9)
        self.wait(TIMING["long_pause"])

    # -----------------------------------------------------------------------
    # Section 2: phenotype decomposition induces multiple cross-mate correlations
    # -----------------------------------------------------------------------
    def play_component_decomposition(self):
        decomposition_note = self.make_right_panel_note(
            self.color_equation(MathTex(r"y=g+e", font_size=38)),
            Text("Mates were sorted on y, not on g and e separately.", font_size=23),
        )
        self.swap_note(decomposition_note)

        # Reveal the hidden component lines while the cards stay in the same
        # positions. This preserves the visual memory of the pairing step.
        self.play(
            LaggedStart(
                *[
                    card["component_group"].animate.set_opacity(1.0)
                    for card in self.paternal_column["cards"]
                ],
                lag_ratio=0.04,
            ),
            LaggedStart(
                *[
                    card["component_group"].animate.set_opacity(1.0)
                    for card in self.maternal_cards_by_slot
                ],
                lag_ratio=0.04,
            ),
            run_time=1.2,
        )
        self.wait(TIMING["short_pause"])

        component_steps = [
            {
                "sources": [card["g_line"] for card in self.paternal_column["cards"]],
                "targets": [card["g_line"] for card in self.maternal_cards_by_slot],
                "equation": self.color_equation(
                    MathTex(r"\mathrm{Corr}(g_m,g_p)>0", font_size=34)
                ),
            },
            {
                "sources": [card["e_line"] for card in self.paternal_column["cards"]],
                "targets": [card["e_line"] for card in self.maternal_cards_by_slot],
                "equation": self.color_equation(
                    MathTex(r"\mathrm{Corr}(e_m,e_p)>0", font_size=34)
                ),
            },
            {
                "sources": [card["e_line"] for card in self.paternal_column["cards"]],
                "targets": [card["g_line"] for card in self.maternal_cards_by_slot],
                "equation": self.color_equation(
                    MathTex(r"\mathrm{Corr}(g_m,e_p)>0", font_size=34)
                ),
            },
            {
                "sources": [card["g_line"] for card in self.paternal_column["cards"]],
                "targets": [card["e_line"] for card in self.maternal_cards_by_slot],
                "equation": self.color_equation(
                    MathTex(r"\mathrm{Corr}(e_m,g_p)>0", font_size=34)
                ),
            },
        ]

        for step in component_steps:
            note = self.make_right_panel_note(
                self.color_equation(MathTex(r"y=g+e", font_size=38)),
                step["equation"],
                Text("Phenotype-based matching pushes correlation into components.", font_size=21),
            )
            links = self.draw_correlation_links(
                step["sources"],
                step["targets"],
                color=COLORS["trans"],
                stroke_width=2.6,
                pairwise=True,
            )

            self.swap_note(note)
            self.play(Create(links), run_time=TIMING["corr_step"])
            self.wait(TIMING["short_pause"])
            self.play(FadeOut(links), run_time=0.4)

        summary_note = self.make_right_panel_note(
            self.color_equation(MathTex(r"y=g+e", font_size=36)),
            self.color_equation(MathTex(r"\mathrm{Corr}(g_m,g_p)>0", font_size=28)),
            self.color_equation(MathTex(r"\mathrm{Corr}(e_m,e_p)>0", font_size=28)),
            self.color_equation(MathTex(r"\mathrm{Corr}(g_m,e_p)>0", font_size=28)),
            self.color_equation(MathTex(r"\mathrm{Corr}(e_m,g_p)>0", font_size=28)),
        )
        self.swap_note(summary_note)
        self.wait(TIMING["long_pause"])

    # -----------------------------------------------------------------------
    # Section 3: only trait-relevant loci are affected
    # -----------------------------------------------------------------------
    def play_trait_specificity(self):
        focus_row_index = 2
        focus_pair = VGroup(
            self.paternal_column["cards"][focus_row_index]["group"],
            self.maternal_cards_by_slot[focus_row_index]["group"],
        )
        focus_box = SurroundingRectangle(
            focus_pair,
            color=COLORS["highlight"],
            buff=0.10,
            stroke_width=3.0,
        )

        zoom_note = self.make_right_panel_note(
            Text("Now zoom in on one assortatively matched pair.", font_size=25),
            Text("The next steps live at the locus level.", font_size=23),
        )
        self.swap_note(zoom_note)
        self.play(Create(focus_box), run_time=0.6)
        self.wait(TIMING["short_pause"])

        # We do a clean scene transition here: the phenotype story has done its
        # job, so we fade it out and replace it with a locus-level schematic.
        self.play(
            FadeOut(self.pair_connectors),
            FadeOut(focus_box),
            FadeOut(self.paternal_column["group"]),
            FadeOut(self.maternal_column["group"]),
            FadeIn(self.genome_panel, shift=0.12 * UP),
            run_time=1.0,
        )

        trait_note = self.make_right_panel_note(
            self.color_equation(MathTex(r"g=\sum_{k\in T}\beta_k x_k", font_size=34)),
            Text("Only loci in T help build the assorted trait.", font_size=24),
            Text("Unrelated loci stay visually quiet and statistically unaffected.", font_size=21),
        )
        self.swap_note(trait_note)
        self.play(
            FadeIn(self.locus_type_objects["panel"], shift=0.12 * UP),
            run_time=0.7,
        )

        self.play(
            Create(self.locus_type_objects["relevant_pulses"]),
            run_time=0.7,
        )
        self.wait(TIMING["short_pause"])
        self.play(FadeOut(self.locus_type_objects["relevant_pulses"]), run_time=0.3)

        self.play(
            Create(self.locus_type_objects["neutral_pulses"]),
            run_time=0.7,
        )
        self.wait(TIMING["short_pause"])
        self.play(FadeOut(self.locus_type_objects["neutral_pulses"]), run_time=0.3)
        self.wait(TIMING["medium_pause"])

    # -----------------------------------------------------------------------
    # Section 4: one focal trait locus links broadly across the other parent
    # -----------------------------------------------------------------------
    def play_locus_view(self):
        self.trait_focus = self.highlight_focal_locus(
            self.paternal_row,
            self.focal_trait_locus,
            "p",
            COLORS["trait_locus"],
        )
        self.neutral_focus = self.highlight_focal_locus(
            self.paternal_row,
            self.focal_neutral_locus,
            "u",
            COLORS["neutral_locus"],
        )

        maternal_trait_targets = [
            self.maternal_row["cells"][index]["group"] for index in self.trait_relevant_loci
        ]
        self.long_range_links = self.draw_correlation_links(
            [self.paternal_row["cells"][self.focal_trait_locus]["group"]],
            maternal_trait_targets,
            color=COLORS["trans"],
            stroke_width=2.8,
            tip=False,
        )

        neutral_callout = Text(
            "no induced long-range links",
            font_size=20,
            color=COLORS["muted"],
        )
        neutral_callout.next_to(
            self.neutral_focus["box"],
            DOWN,
            buff=0.12,
        )

        locus_note = self.make_right_panel_note(
            Text("A trait locus can correlate with many trait loci in the mate.", font_size=24),
            self.color_equation(MathTex(r"p\in T \Rightarrow \text{many maternal }k\in T", font_size=30)),
            Text("A neutral locus u does not enter this pathway.", font_size=22, color=COLORS["muted"]),
        )
        self.swap_note(locus_note)

        self.play(
            Create(self.trait_focus["box"]),
            FadeIn(self.trait_focus["label"], shift=0.08 * UP),
            Create(self.neutral_focus["box"]),
            FadeIn(self.neutral_focus["label"], shift=0.08 * UP),
            run_time=0.8,
        )
        self.play(Create(self.long_range_links), run_time=1.0)
        self.play(FadeIn(neutral_callout, shift=0.08 * DOWN), run_time=0.5)
        self.neutral_callout = neutral_callout
        self.wait(TIMING["long_pause"])

    # -----------------------------------------------------------------------
    # Section 5: offspring inherits between-haplotype trans correlation
    # -----------------------------------------------------------------------
    def play_offspring_trans_view(self):
        # The same two rows now become the offspring's two inherited haplotypes.
        new_paternal_label = MathTex(r"\text{offspring paternal haplotype}", font_size=28)
        new_paternal_label.set_color(COLORS["paternal"])
        new_paternal_label.next_to(
            self.paternal_row["cells_group"], LEFT, buff=LAYOUT["label_buffer"]
        )

        new_maternal_label = MathTex(r"\text{offspring maternal haplotype}", font_size=28)
        new_maternal_label.set_color(COLORS["maternal"])
        new_maternal_label.next_to(
            self.maternal_row["cells_group"], LEFT, buff=LAYOUT["label_buffer"]
        )

        relevant_top_cells = VGroup(
            *[self.paternal_row["cells"][index]["group"] for index in self.trait_relevant_loci]
        )
        relevant_bottom_cells = VGroup(
            *[self.maternal_row["cells"][index]["group"] for index in self.trait_relevant_loci]
        )

        self.trans_links = self.draw_correlation_links(
            [self.paternal_row["cells"][index]["group"] for index in self.trait_relevant_loci],
            [self.maternal_row["cells"][index]["group"] for index in self.trait_relevant_loci],
            color=COLORS["trans"],
            stroke_width=2.8,
            pairwise=True,
            vertical=True,
        )

        self.trans_brace = Brace(
            VGroup(relevant_top_cells, relevant_bottom_cells),
            RIGHT,
            buff=0.16,
        )
        self.trans_brace.set_color(COLORS["trans"])
        self.trans_brace_label = self.trans_brace.get_text("trans correlation", buff=0.10)
        self.trans_brace_label.scale(0.50)
        self.trans_brace_label.set_color(COLORS["trans"])

        trans_note = self.make_right_panel_note(
            Text("The offspring inherits one correlated paternal row and one correlated maternal row.", font_size=22),
            Text("At trait-relevant loci, the correlation is between haplotypes.", font_size=22),
            self.color_equation(MathTex(r"\text{trans correlation}", font_size=30)),
        )
        self.swap_note(trans_note)

        self.play(
            Transform(self.paternal_row["label"], new_paternal_label),
            Transform(self.maternal_row["label"], new_maternal_label),
            FadeOut(self.long_range_links),
            FadeOut(self.neutral_callout),
            run_time=0.8,
        )
        self.play(
            FadeOut(self.trait_focus["box"]),
            FadeOut(self.trait_focus["label"]),
            FadeOut(self.neutral_focus["box"]),
            FadeOut(self.neutral_focus["label"]),
            run_time=0.4,
        )

        self.play(
            Create(self.trans_links),
            Create(self.trans_brace),
            FadeIn(self.trans_brace_label, shift=0.08 * RIGHT),
            run_time=0.9,
        )
        self.wait(TIMING["long_pause"])

    # -----------------------------------------------------------------------
    # Section 6: recombination turns trans correlation into cis correlation
    # -----------------------------------------------------------------------
    def play_recombination_to_cis(self):
        recombination_note = self.make_right_panel_note(
            Text("In the next generation, recombination mixes the two parental copies.", font_size=22),
            Text("Earlier trans correlation can now reappear within one gamete.", font_size=22),
            self.color_equation(MathTex(r"\text{trans} \to \text{cis}", font_size=30)),
        )
        self.swap_note(recombination_note)

        self.play(
            FadeIn(self.mosaic_setup["row"]["group"], shift=0.12 * UP),
            FadeIn(self.mosaic_setup["crossover_lines"]),
            FadeIn(self.mosaic_setup["crossover_labels"]),
            run_time=0.8,
        )
        self.wait(TIMING["short_pause"])

        for segment in self.mosaic_setup["segments"]:
            self.play(
                Create(segment["source_highlight"]),
                Create(segment["target_highlight"]),
                GrowArrow(segment["transfer_arrow"]),
                run_time=0.35,
            )

            target_entries = []
            source_entries = []
            for locus_index in range(segment["start"], segment["end"] + 1):
                value = self.mosaic_haplotype[locus_index]
                target_entry = MathTex(str(value), font_size=28)
                target_entry.move_to(
                    self.mosaic_setup["row"]["cells"][locus_index]["box"].get_center()
                )
                target_entries.append(target_entry)
                source_entries.append(segment["source_row"]["cells"][locus_index]["entry"])

            self.play(
                *[
                    TransformFromCopy(source_entry.copy(), target_entry)
                    for source_entry, target_entry in zip(source_entries, target_entries)
                ],
                run_time=TIMING["segment_step"],
            )

            for locus_index, target_entry in zip(
                range(segment["start"], segment["end"] + 1),
                target_entries,
            ):
                target_cell = self.mosaic_setup["row"]["cells"][locus_index]
                target_cell["group"].remove(target_cell["entry"])
                target_cell["entry"] = target_entry
                target_cell["group"].add(target_entry)

            self.play(
                FadeOut(segment["source_highlight"]),
                FadeOut(segment["target_highlight"]),
                FadeOut(segment["transfer_arrow"]),
                run_time=0.25,
            )

        # Once the mosaic row is complete, we can change the visual language
        # from between-row links (trans) to within-row links (cis).
        cis_pairs = [
            (self.trait_relevant_loci[index], self.trait_relevant_loci[index + 1])
            for index in range(len(self.trait_relevant_loci) - 1)
        ]
        self.cis_links = VGroup()
        for left_index, right_index in cis_pairs:
            start = self.mosaic_setup["row"]["cells"][left_index]["box"].get_bottom()
            end = self.mosaic_setup["row"]["cells"][right_index]["box"].get_bottom()
            cis_link = ArcBetweenPoints(
                start,
                end,
                angle=-0.55,
                color=COLORS["cis"],
                stroke_width=3.2,
            )
            self.cis_links.add(cis_link)

        self.cis_boxes = VGroup(
            *[
                SurroundingRectangle(
                    self.mosaic_setup["row"]["cells"][index]["group"],
                    color=COLORS["cis"],
                    buff=0.05,
                    stroke_width=2.6,
                )
                for index in self.trait_relevant_loci
            ]
        )

        cis_label = Text("cis correlation / long-range LD", font_size=24, color=COLORS["cis"])
        cis_label.next_to(self.mosaic_setup["row"]["cells_group"], DOWN, buff=0.48)
        self.cis_label = cis_label

        cis_note = self.make_right_panel_note(
            Text("Recombination shuffles the two trans-correlated parental copies into one gamete.", font_size=21),
            Text("Now trait-relevant loci co-occur within the same haplotype.", font_size=22),
            Text("Neutral loci still do not acquire the same highlighted structure.", font_size=20, color=COLORS["muted"]),
        )
        self.swap_note(cis_note)

        self.play(
            FadeOut(self.trans_links),
            FadeOut(self.trans_brace),
            FadeOut(self.trans_brace_label),
            Create(self.cis_boxes),
            Create(self.cis_links),
            FadeIn(self.cis_label, shift=0.10 * DOWN),
            run_time=1.0,
        )
        self.wait(TIMING["long_pause"])

    # -----------------------------------------------------------------------
    # Section 7: marginal GWAS coefficients absorb correlated signal
    # -----------------------------------------------------------------------
    def play_gwas_summary(self):
        focal_j = self.highlight_focal_locus(
            self.mosaic_setup["row"],
            self.focal_trait_locus,
            "j",
            COLORS["highlight"],
        )

        final_note = self.make_right_panel_note(
            Text("Marginal GWAS-style coefficient at locus j:", font_size=24),
            self.color_equation(
                MathTex(
                    r"\hat b_j^{\mathrm{marg}} \sim \beta_j + \sum_{k\in T,\ k\neq j} r_{jk}\beta_k",
                    font_size=30,
                )
            ),
            Text("So j picks up its direct effect plus tagged signal from correlated trait loci.", font_size=21),
            Text("Loci unrelated to the assorted trait do not enter this induced long-range-LD path.", font_size=19, color=COLORS["muted"]),
        )
        self.swap_note(final_note)

        self.play(
            Create(focal_j["box"]),
            FadeIn(focal_j["label"], shift=0.08 * UP),
            run_time=0.6,
        )
        self.wait(TIMING["long_pause"])

