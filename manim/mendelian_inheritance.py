
"""
Manim scene for teaching Mendelian inheritance and parent-offspring resemblance.

This file is intentionally written for a beginner-friendly workflow:
1. Edit the example haplotypes or timings below.
2. Render a quick draft while you are iterating.
3. Render a higher-quality version when the pacing feels right.

Common render commands from the project root:
    manim -pql manim/mendelian_inheritance.py MendelianInheritanceScene
    python -m manim -pql manim/mendelian_inheritance.py MendelianInheritanceScene
    py -m manim -pql manim/mendelian_inheritance.py MendelianInheritanceScene

Higher quality:
    manim -pqh manim/mendelian_inheritance.py MendelianInheritanceScene
"""

from manim import *
import numpy as np


# ---------------------------------------------------------------------------
# Top-level configuration block
# ---------------------------------------------------------------------------
# These arrays define the worked example shown in the animation.
# The parent carries two homologous haplotypes, each coded as a row of 0/1 alleles.
# We deliberately include loci with genotype counts 0, 1, and 2 so that the
# viewer can see both deterministic transmission and random transmission.
PARENT_HAPLOTYPE_1 = [1, 0, 1, 1, 0, 0]
PARENT_HAPLOTYPE_2 = [0, 1, 1, 0, 1, 0]

# Each entry says which parental haplotype contributes the allele to the gamete.
# 0 means "take the allele from haplotype 1" and 1 means "take it from haplotype 2".
# This fixed pattern keeps the rendered animation reproducible.
TRANSMISSION_PATTERN = [0, 1, 0, 1, 1, 0]

# Symbolic additive effects. These are not numerically used in the animation,
# but keeping them explicit in the code helps show where the weighted sums come from.
ALLELE_EFFECT_LABELS = [r"\beta_1", r"\beta_2", r"\beta_3", r"\beta_4", r"\beta_5", r"\beta_6"]

# Timing is separated from the animation logic so you can later slow down or
# speed up the lecture without rewriting the teaching structure.
TIMING = {
    "short_pause": 0.8,
    "medium_pause": 1.4,
    "long_pause": 2.2,
    "locus_animation": 0.85,
}

# Color roles are named semantically rather than by object, which makes the
# file easier to extend later when you add assortative mating or LD material.
COLORS = {
    "haplotype_1": BLUE_E,
    "haplotype_2": TEAL_E,
    "genotype": ORANGE,
    "gamete": GREEN_E,
    "segregation": PURPLE_B,
    "highlight": YELLOW,
    "assumption": GREY_B,
    "muted": GREY_C,
    "title": WHITE,
}

# Layout constants are grouped here so the spatial structure stays stable.
# A later extension could reuse the same left-side "genome panel" and simply
# swap in new transmission logic or new summary equations.
LAYOUT = {
    "cells_center_x": -1.0,
    "label_buffer": 0.45,
    "cell_gap": 0.14,
    "cell_width": 0.78,
    "cell_height": 0.58,
    "locus_label_y_offset": 0.28,
    "right_panel_center": np.array([3.85, 0.9, 0.0]),
    "summary_center": np.array([0.0, 0.15, 0.0]),
}


def compute_genotype_counts(haplotype_1, haplotype_2):
    """Return x_{jp}, the parent's genotype count at each locus."""
    return [upper + lower for upper, lower in zip(haplotype_1, haplotype_2)]


def compute_transmitted_alleles(haplotype_1, haplotype_2, transmission_pattern):
    """Return z_j, the allele transmitted by the focal parent at each locus."""
    transmitted = []
    for upper, lower, chosen_haplotype in zip(
        haplotype_1, haplotype_2, transmission_pattern
    ):
        transmitted.append(upper if chosen_haplotype == 0 else lower)
    return transmitted


def compute_segregation_deviations(genotype_counts, transmitted_alleles):
    r"""Return \epsilon_j = z_j - (1/2) x_{jp}."""
    return [transmitted - 0.5 * genotype for genotype, transmitted in zip(genotype_counts, transmitted_alleles)]


class MendelianInheritanceScene(Scene):
    """
    One master scene made of pedagogical sections.

    The scene is modular in the sense that each conceptual section lives in a
    separate method, and the data-generating logic is separated from the
    drawing logic. That makes it easier to later adapt the code for:
    - assortative mating
    - linkage disequilibrium
    - multiple parents or multiple offspring
    """

    def construct(self):
        # -------------------------------------------------------------------
        # Prepare data once at the start.
        # -------------------------------------------------------------------
        # By computing the genetics objects here, we keep the later animation
        # code focused on teaching rather than bookkeeping.
        self.haplotype_1 = PARENT_HAPLOTYPE_1
        self.haplotype_2 = PARENT_HAPLOTYPE_2
        self.transmission_pattern = TRANSMISSION_PATTERN
        self.effect_labels = ALLELE_EFFECT_LABELS

        self.genotype_counts = compute_genotype_counts(self.haplotype_1, self.haplotype_2)
        self.transmitted_alleles = compute_transmitted_alleles(
            self.haplotype_1,
            self.haplotype_2,
            self.transmission_pattern,
        )
        self.segregation_deviations = compute_segregation_deviations(
            self.genotype_counts,
            self.transmitted_alleles,
        )

        # We choose one heterozygous locus with z_j = 0 so that the segregation
        # deviation is visibly negative in the worked example.
        self.focus_locus = 3  # zero-based index: locus 4 in the displayed labels

        # Build the recurring left-side genome panel before the section methods
        # start. This avoids visual jumps between sections.
        self.build_static_layout()

        # Section-by-section teaching flow.
        self.play_parent_intro()
        self.play_gamete_formation()
        self.play_locus_decomposition()
        self.play_additive_value_aggregation()
        self.play_correlation_summary()

    # -----------------------------------------------------------------------
    # General helper methods
    # -----------------------------------------------------------------------
    def make_value_cell(
        self,
        value,
        box_color,
        fill_opacity=0.18,
        font_size=30,
    ):
        """
        Build one boxed allele/count cell.

        We keep each cell as a small dictionary so later code can address:
        - the rectangle itself (for highlighting)
        - the entry text (for copying into equations or gametes)
        - the grouped cell (for layout)
        """
        box = RoundedRectangle(
            corner_radius=0.08,
            width=LAYOUT["cell_width"],
            height=LAYOUT["cell_height"],
            stroke_color=box_color,
            stroke_width=2.0,
            fill_color=box_color,
            fill_opacity=fill_opacity,
        )

        entry = None
        if value is not None:
            entry = MathTex(str(value), font_size=font_size)
            entry.move_to(box.get_center())
        else:
            # A blank cell is still useful as a visual destination for the gamete.
            entry = VectorizedPoint(box.get_center())

        group = VGroup(box, entry)
        return {"box": box, "entry": entry, "group": group, "value": value}

    def build_row(self, values, label_tex, box_color):
        """
        Build one labeled row of boxes.

        Rows are used for:
        - the two parental haplotypes
        - genotype counts x_{jp}
        - transmitted alleles z_j
        """
        label = MathTex(label_tex, font_size=32)
        label.set_color(box_color if label_tex in {r"x_{jp}", r"z_j"} else WHITE)

        cell_items = [self.make_value_cell(value, box_color) for value in values]
        cells_group = VGroup(*[cell["group"] for cell in cell_items]).arrange(
            RIGHT,
            buff=LAYOUT["cell_gap"],
        )

        return {
            "label": label,
            "cells": cell_items,
            "cells_group": cells_group,
            "group": VGroup(label, cells_group),
        }

    def position_row(self, row, y_coordinate):
        """Place a row so that all rows share the same aligned locus positions."""
        row["cells_group"].move_to(np.array([LAYOUT["cells_center_x"], y_coordinate, 0.0]))
        row["label"].next_to(row["cells_group"], LEFT, buff=LAYOUT["label_buffer"])
        row["group"] = VGroup(row["label"], row["cells_group"])

    def build_locus_labels(self, reference_row):
        """Create one label above each locus."""
        labels = VGroup()
        for locus_index, cell in enumerate(reference_row["cells"], start=1):
            label = MathTex(fr"j={locus_index}", font_size=24)
            label.next_to(cell["box"], UP, buff=LAYOUT["locus_label_y_offset"])
            labels.add(label)
        return labels

    def make_right_panel_note(self, *lines, center=None):
        """
        Create a note in the fixed right-side teaching area.

        Using a single right panel keeps the left-side genome panel stable, which
        matters a lot for pedagogy: students should not spend attention on
        moving objects when the conceptual point is elsewhere.
        """
        note_lines = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        background = BackgroundRectangle(
            note_lines,
            buff=0.2,
            fill_opacity=0.12,
            stroke_opacity=0.0,
        )
        panel = VGroup(background, note_lines)
        note_center = LAYOUT["right_panel_center"] if center is None else center
        panel.move_to(note_center)
        return panel

    def column_group(self, locus_index, include_gamete=True):
        """Return the stack of cells in one locus column."""
        column_items = [
            self.haplotype_row_1["cells"][locus_index]["group"],
            self.haplotype_row_2["cells"][locus_index]["group"],
            self.genotype_row["cells"][locus_index]["group"],
        ]
        if include_gamete:
            column_items.append(self.gamete_row["cells"][locus_index]["group"])
        return VGroup(*column_items)

    def create_gamete_entry(self, locus_index, value):
        """
        Fill one previously blank gamete cell.

        We create the text on demand rather than upfront so the transmitted
        allele visibly appears only when that locus is animated.
        """
        target_cell = self.gamete_row["cells"][locus_index]
        target_entry = MathTex(str(value), font_size=30)
        target_entry.move_to(target_cell["box"].get_center())
        target_cell["group"].remove(target_cell["entry"])
        target_cell["entry"] = target_entry
        target_cell["group"].add(target_entry)
        return target_entry

    def color_equation(self, equation):
        """
        Apply a consistent color language across equations.

        This is intentionally simple: a few repeated colors are easier for the
        audience to learn than many one-off highlighting schemes.
        """
        equation.set_color_by_tex(r"g_p", COLORS["genotype"])
        equation.set_color_by_tex(r"g_c", COLORS["gamete"])
        equation.set_color_by_tex(r"g_{c\leftarrow p}", COLORS["gamete"])
        equation.set_color_by_tex(r"\epsilon", COLORS["segregation"])
        equation.set_color_by_tex(r"\epsilon_g", COLORS["segregation"])
        equation.set_color_by_tex(r"\epsilon_j", COLORS["segregation"])
        equation.set_color_by_tex(r"z_j", COLORS["gamete"])
        equation.set_color_by_tex(r"x_{jp}", COLORS["genotype"])
        equation.set_color_by_tex(r"\beta_j", WHITE)
        equation.set_color_by_tex(r"\sigma^2_g", COLORS["genotype"])
        return equation

    def build_static_layout(self):
        """Build the rows and reusable layout objects that persist across sections."""
        self.title = Text(
            "Mendelian Inheritance and the 0.50 Parent-Offspring Correlation",
            font_size=36,
        )
        self.title.to_edge(UP)

        self.subtitle = MathTex(
            r"\text{One focal parent, locus by locus, then summed across loci}",
            font_size=28,
        )
        self.subtitle.next_to(self.title, DOWN, buff=0.18)

        self.haplotype_row_1 = self.build_row(
            self.haplotype_1,
            r"\text{haplotype 1}",
            COLORS["haplotype_1"],
        )
        self.haplotype_row_2 = self.build_row(
            self.haplotype_2,
            r"\text{haplotype 2}",
            COLORS["haplotype_2"],
        )
        self.genotype_row = self.build_row(
            self.genotype_counts,
            r"x_{jp}",
            COLORS["genotype"],
        )

        # The gamete row starts empty and is filled locus by locus.
        self.gamete_row = self.build_row(
            [None] * len(self.haplotype_1),
            r"z_j",
            COLORS["gamete"],
        )

        self.position_row(self.haplotype_row_1, 1.45)
        self.position_row(self.haplotype_row_2, 0.55)
        self.position_row(self.genotype_row, -0.45)
        self.position_row(self.gamete_row, -2.0)

        self.locus_labels = self.build_locus_labels(self.haplotype_row_1)

        # A brace on the two haplotype rows helps the audience remember the
        # biological picture: two homologous chromosome copies in a diploid parent.
        haplotype_cells = VGroup(
            self.haplotype_row_1["cells_group"],
            self.haplotype_row_2["cells_group"],
        )
        self.haplotype_brace = Brace(haplotype_cells, RIGHT, buff=0.18)
        self.haplotype_brace_label = self.haplotype_brace.get_text(
            "two homologous haplotypes",
            buff=0.12,
        )
        self.haplotype_brace_label.scale(0.5)

        self.parent_group = VGroup(
            self.locus_labels,
            self.haplotype_row_1["group"],
            self.haplotype_row_2["group"],
            self.genotype_row["group"],
            self.gamete_row["group"],
        )

    # -----------------------------------------------------------------------
    # Section 1: introduce the diploid parent genotype
    # -----------------------------------------------------------------------
    def play_parent_intro(self):
        self.play(Write(self.title), FadeIn(self.subtitle, shift=0.15 * DOWN))
        self.wait(TIMING["short_pause"])

        self.play(
            LaggedStart(*[Write(label) for label in self.locus_labels], lag_ratio=0.08),
            run_time=1.1,
        )
        self.play(
            FadeIn(self.haplotype_row_1["group"], shift=0.15 * RIGHT),
            FadeIn(self.haplotype_row_2["group"], shift=0.15 * RIGHT),
            run_time=1.0,
        )
        self.wait(TIMING["short_pause"])

        self.play(
            Create(self.haplotype_brace),
            FadeIn(self.haplotype_brace_label, shift=0.1 * RIGHT),
            run_time=0.9,
        )
        self.wait(TIMING["medium_pause"])

        genotype_formula = self.color_equation(
            MathTex(
                r"x_{jp}",
                r"=",
                r"h_{j1}",
                r"+",
                r"h_{j2}",
                font_size=36,
            )
        )
        genotype_formula.scale(0.9)
        genotype_formula.move_to(np.array([3.35, -0.35, 0.0]))

        example_highlight = SurroundingRectangle(
            self.column_group(0, include_gamete=False),
            color=COLORS["highlight"],
            buff=0.12,
        )
        example_note = self.make_right_panel_note(
            self.color_equation(
                MathTex(r"x_{jp}=h_{j1}+h_{j2}", font_size=34)
            ),
            MathTex(r"\text{Count how many 1 alleles the parent carries at locus }j", font_size=28),
            MathTex(r"\text{Example at }j=1:\ 1+0=1", font_size=28),
        )

        self.play(FadeIn(self.genotype_row["group"], shift=0.15 * RIGHT))
        self.play(Create(example_highlight), FadeIn(example_note), Write(genotype_formula))
        self.wait(TIMING["medium_pause"])
        self.play(FadeOut(example_highlight), FadeOut(example_note))

        self.genotype_formula = genotype_formula

    # -----------------------------------------------------------------------
    # Section 2: show locus-by-locus gamete formation
    # -----------------------------------------------------------------------
    def play_gamete_formation(self):
        gamete_intro = self.make_right_panel_note(
            MathTex(
                r"\text{Gamete formation: exactly one parental allele enters the gamete at each locus}",
                font_size=28,
            ),
        )
        self.play(FadeIn(self.gamete_row["group"], shift=0.15 * RIGHT), FadeIn(gamete_intro))
        self.wait(TIMING["short_pause"])

        for locus_index, (genotype_count, transmitted_value, chosen_haplotype) in enumerate(
            zip(
                self.genotype_counts,
                self.transmitted_alleles,
                self.transmission_pattern,
            )
        ):
            column_highlight = SurroundingRectangle(
                self.column_group(locus_index, include_gamete=False),
                color=COLORS["highlight"],
                buff=0.12,
            )

            if genotype_count == 1:
                note = self.make_right_panel_note(
                    self.color_equation(MathTex(r"x_{jp}=1", font_size=36)),
                    MathTex(
                        r"\Pr(\text{upper allele})=\Pr(\text{lower allele})=\tfrac{1}{2}",
                        font_size=30,
                    ),
                )
            else:
                note = self.make_right_panel_note(
                    self.color_equation(MathTex(r"x_{jp}\in\{0,2\}", font_size=36)),
                    MathTex(r"\text{Both homologs carry the same allele, so transmission is deterministic}", font_size=28),
                )

            source_row = self.haplotype_row_1 if chosen_haplotype == 0 else self.haplotype_row_2
            source_cell = source_row["cells"][locus_index]
            target_cell = self.gamete_row["cells"][locus_index]

            source_highlight = SurroundingRectangle(
                source_cell["box"],
                color=COLORS["gamete"],
                buff=0.08,
            )
            target_highlight = SurroundingRectangle(
                target_cell["box"],
                color=COLORS["gamete"],
                buff=0.08,
            )

            transmitted_arrow = Arrow(
                source_cell["box"].get_bottom(),
                target_cell["box"].get_top(),
                buff=0.08,
                stroke_width=4,
                color=COLORS["gamete"],
                max_tip_length_to_length_ratio=0.18,
            )

            target_entry = self.create_gamete_entry(locus_index, transmitted_value)

            self.play(Create(column_highlight), FadeTransform(gamete_intro, note), run_time=0.55)
            self.play(Create(source_highlight), Create(target_highlight), run_time=0.35)
            self.play(GrowArrow(transmitted_arrow), run_time=0.4)
            self.play(
                TransformFromCopy(source_cell["entry"], target_entry),
                run_time=TIMING["locus_animation"],
            )
            self.wait(0.15)
            self.play(
                FadeOut(column_highlight),
                FadeOut(source_highlight),
                FadeOut(target_highlight),
                FadeOut(transmitted_arrow),
                run_time=0.35,
            )
            gamete_intro = note

        self.wait(TIMING["medium_pause"])

        self.transmitted_brace = Brace(self.gamete_row["cells_group"], DOWN, buff=0.18)
        self.transmitted_brace_label = self.transmitted_brace.get_text(
            "transmitted allele from the focal parent",
            buff=0.1,
        )
        self.transmitted_brace_label.scale(0.48)

        self.play(Create(self.transmitted_brace), FadeIn(self.transmitted_brace_label, shift=0.1 * DOWN))
        self.wait(TIMING["short_pause"])
        self.play(FadeOut(gamete_intro))

    # -----------------------------------------------------------------------
    # Section 3: connect a transmitted allele to 1/2 x_{jp} + \epsilon_j
    # -----------------------------------------------------------------------
    def play_locus_decomposition(self):
        focus_column = self.column_group(self.focus_locus, include_gamete=True)
        focus_highlight = SurroundingRectangle(
            focus_column,
            color=COLORS["highlight"],
            buff=0.14,
        )

        other_objects = VGroup()
        for locus_index in range(len(self.haplotype_1)):
            if locus_index != self.focus_locus:
                other_objects.add(
                    self.haplotype_row_1["cells"][locus_index]["group"],
                    self.haplotype_row_2["cells"][locus_index]["group"],
                    self.genotype_row["cells"][locus_index]["group"],
                    self.gamete_row["cells"][locus_index]["group"],
                    self.locus_labels[locus_index],
                )

        locus_heading = MathTex(
            r"\text{At a heterozygous locus, the transmitted allele fluctuates around } \tfrac{1}{2}x_{jp}",
            font_size=28,
        )
        decomposition_general = self.color_equation(
            MathTex(
                r"z_j",
                r"=",
                r"\tfrac{1}{2}x_{jp}",
                r"+",
                r"\epsilon_j",
                font_size=40,
            )
        )
        decomposition_example = self.color_equation(
            MathTex(
                r"\text{Here at }j=4:\quad 0 = \tfrac{1}{2}(1) - \tfrac{1}{2}",
                font_size=34,
            )
        )

        right_panel = self.make_right_panel_note(
            locus_heading,
            decomposition_general,
            decomposition_example,
        )

        case_summary = VGroup(
            self.color_equation(MathTex(r"x_{jp}=0 \Rightarrow z_j=0,\ \epsilon_j=0", font_size=30)),
            self.color_equation(MathTex(r"x_{jp}=2 \Rightarrow z_j=1,\ \epsilon_j=0", font_size=30)),
            self.color_equation(
                MathTex(
                    r"x_{jp}=1 \Rightarrow z_j\in\{0,1\},\ \epsilon_j\in\{-\tfrac{1}{2},+\tfrac{1}{2}\}",
                    font_size=30,
                )
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        case_box = BackgroundRectangle(
            case_summary,
            buff=0.22,
            fill_opacity=0.12,
            stroke_opacity=0.0,
        )
        case_panel = VGroup(case_box, case_summary)
        case_panel.move_to(np.array([3.7, -1.4, 0.0]))

        self.play(other_objects.animate.set_opacity(0.2), Create(focus_highlight), run_time=0.8)
        self.play(FadeIn(right_panel, shift=0.12 * RIGHT), run_time=0.9)
        self.wait(TIMING["medium_pause"])
        self.play(FadeIn(case_panel, shift=0.12 * UP), run_time=0.8)
        self.wait(TIMING["long_pause"])

        self.play(other_objects.animate.set_opacity(1.0), FadeOut(focus_highlight), run_time=0.8)
        self.play(FadeOut(right_panel), FadeOut(case_panel), run_time=0.6)

    # -----------------------------------------------------------------------
    # Section 4: sum across loci to get additive genetic values
    # -----------------------------------------------------------------------
    def play_additive_value_aggregation(self):
        # The screen is already dense by this point, so we avoid stacking extra
        # braces above and below the genome rows. Instead, we lightly highlight
        # the relevant rows and keep the equations in a dedicated right-hand area.
        genotype_highlight = SurroundingRectangle(
            self.genotype_row["cells_group"],
            color=COLORS["genotype"],
            buff=0.12,
        )
        gamete_highlight = SurroundingRectangle(
            self.gamete_row["cells_group"],
            color=COLORS["gamete"],
            buff=0.12,
        )

        aggregation_heading = MathTex(
            r"\text{Now weight each locus by }\beta_j\text{ and sum across loci}",
            font_size=28,
        )
        parent_value_eq = self.color_equation(
            MathTex(r"g_p = \sum_j \beta_j x_{jp}", font_size=34)
        )
        transmitted_value_eq = self.color_equation(
            MathTex(r"g_{c\leftarrow p} = \sum_j \beta_j z_j", font_size=34)
        )
        aggregation_step_2 = self.color_equation(
            MathTex(
                r"g_{c\leftarrow p}",
                r"=",
                r"\sum_j \beta_j\left(\tfrac{1}{2}x_{jp}+\epsilon_j\right)",
                font_size=38,
            )
        )
        aggregation_step_3 = self.color_equation(
            MathTex(
                r"g_{c\leftarrow p}",
                r"=",
                r"\tfrac{1}{2}g_p",
                r"+",
                r"\sum_j \beta_j \epsilon_j",
                font_size=38,
            )
        )
        aggregation_step_4 = self.color_equation(
            MathTex(
                r"g_{c\leftarrow p}",
                r"=",
                r"\tfrac{1}{2}g_p",
                r"+",
                r"\epsilon_g",
                font_size=38,
            )
        )
        segregation_definition = self.color_equation(
            MathTex(r"\epsilon_g = \sum_j \beta_j \epsilon_j", font_size=32)
        )

        aggregation_heading.move_to(np.array([3.75, 2.0, 0.0]))
        parent_value_eq.move_to(np.array([3.75, 1.25, 0.0]))
        transmitted_value_eq.move_to(np.array([3.75, 0.35, 0.0]))
        aggregation_step_2.move_to(transmitted_value_eq)
        aggregation_step_3.move_to(transmitted_value_eq)
        aggregation_step_4.move_to(transmitted_value_eq)
        segregation_definition.next_to(aggregation_step_4, DOWN, aligned_edge=LEFT, buff=0.22)

        self.play(
            FadeOut(self.genotype_formula),
            FadeOut(self.transmitted_brace),
            FadeOut(self.transmitted_brace_label),
            Create(genotype_highlight),
            Create(gamete_highlight),
            run_time=0.8,
        )
        self.play(
            FadeIn(aggregation_heading),
            FadeIn(parent_value_eq),
            FadeIn(transmitted_value_eq),
            run_time=0.8,
        )
        self.wait(TIMING["medium_pause"])

        current_aggregation_eq = transmitted_value_eq
        self.play(
            TransformMatchingTex(
                current_aggregation_eq,
                aggregation_step_2,
                replace_mobject_with_target_in_scene=True,
            ),
            run_time=1.0,
        )
        self.wait(TIMING["short_pause"])
        current_aggregation_eq = aggregation_step_2

        self.play(
            TransformMatchingTex(
                current_aggregation_eq,
                aggregation_step_3,
                replace_mobject_with_target_in_scene=True,
            ),
            run_time=1.0,
        )
        self.wait(TIMING["short_pause"])
        current_aggregation_eq = aggregation_step_3

        self.play(
            TransformMatchingTex(
                current_aggregation_eq,
                aggregation_step_4,
                replace_mobject_with_target_in_scene=True,
            ),
            FadeIn(segregation_definition),
            run_time=1.0,
        )
        self.wait(TIMING["long_pause"])

        self.parent_share_equation = aggregation_step_4

        self.play(
            FadeOut(genotype_highlight),
            FadeOut(gamete_highlight),
            FadeOut(parent_value_eq),
            FadeOut(aggregation_heading),
            FadeOut(segregation_definition),
            aggregation_step_4.animate.move_to(np.array([0.0, 1.65, 0.0])),
            run_time=0.9,
        )

    # -----------------------------------------------------------------------
    # Section 5: connect the decomposition to the 0.50 correlation
    # -----------------------------------------------------------------------
    def play_correlation_summary(self):
        # The full genome panel has done its job by this point, so we fade it
        # out to give the algebra more space and to reduce visual load.
        left_panel_objects = VGroup(
            self.locus_labels,
            self.haplotype_row_1["group"],
            self.haplotype_row_2["group"],
            self.genotype_row["group"],
            self.gamete_row["group"],
            self.haplotype_brace,
            self.haplotype_brace_label,
        )

        assumption_line = MathTex(
            r"\text{Now collapse the locus picture into the slide equation}",
            font_size=28,
            color=COLORS["assumption"],
        )
        assumption_line.next_to(self.title, DOWN, buff=0.25)

        parent_relation = self.color_equation(
            MathTex(r"g_c = \tfrac{1}{2}g_p + \epsilon", font_size=40)
        )
        parent_relation.move_to(np.array([0.0, 1.55, 0.0]))

        epsilon_note = VGroup(
            MathTex(
                r"\epsilon \text{ collects the other parent and Mendelian sampling}",
                font_size=28,
                color=COLORS["assumption"],
            ),
            MathTex(
                r"\operatorname{Cov}(g_p,\epsilon)=0 \quad \text{under random mating}",
                font_size=32,
                color=COLORS["assumption"],
            ),
        ).arrange(DOWN, buff=0.18)
        epsilon_note.next_to(parent_relation, DOWN, buff=0.3)

        covariance_step = self.color_equation(
            MathTex(
                r"\operatorname{Cov}(g_p,g_c)",
                r"=",
                r"\operatorname{Cov}(g_p,\tfrac{1}{2}g_p)",
                r"+",
                r"0",
                font_size=36,
            )
        )
        covariance_step.next_to(epsilon_note, DOWN, buff=0.55)

        covariance_final = self.color_equation(
            MathTex(
                r"\operatorname{Cov}(g_p,g_c)",
                r"=",
                r"\tfrac{1}{2}\operatorname{Var}(g_p)",
                r"=",
                r"\tfrac{1}{2}\sigma^2_g",
                font_size=38,
            )
        )
        covariance_final.move_to(covariance_step)

        correlation_line = self.color_equation(
            MathTex(
                r"\operatorname{Corr}(g_p,g_c)",
                r"=",
                r"0.50",
                font_size=40,
            )
        )
        correlation_line.next_to(covariance_final, DOWN, buff=0.55)

        self.play(
            FadeOut(left_panel_objects),
            FadeOut(self.subtitle),
            FadeIn(assumption_line),
            TransformMatchingTex(
                self.parent_share_equation,
                parent_relation,
                replace_mobject_with_target_in_scene=True,
            ),
            run_time=0.9,
        )
        self.wait(TIMING["short_pause"])
        self.play(FadeIn(epsilon_note, shift=0.15 * DOWN))
        self.wait(TIMING["short_pause"])
        self.play(FadeIn(covariance_step))
        self.wait(TIMING["short_pause"])
        self.play(
            TransformMatchingTex(
                covariance_step,
                covariance_final,
                replace_mobject_with_target_in_scene=True,
            ),
            run_time=1.0,
        )
        self.wait(TIMING["short_pause"])
        self.play(FadeIn(correlation_line))
        self.wait(TIMING["long_pause"])

        summary_title = Text("Summary", font_size=40)
        summary_title.to_edge(UP)

        summary_bullets = VGroup(
            Tex(
                r"$\bullet$ each offspring gets a random half of each parent's alleles",
                font_size=28,
            ),
            Tex(
                r"$\bullet$ at locus $j$, $x_{jc}$ fluctuates around $\tfrac{1}{2}x_{jp}$ because of Mendelian sampling",
                font_size=28,
            ),
            Tex(
                r"$\bullet$ with $g_i=\sum_j \beta_j x_{ij}$, $\operatorname{Cov}(g_p,g_c)=\tfrac{1}{2}\sigma^2_g$ and $\operatorname{Corr}(g_p,g_c)=0.50$",
                font_size=28,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        summary_bullets.move_to(LAYOUT["summary_center"])

        self.play(
            FadeOut(assumption_line),
            FadeOut(parent_relation),
            FadeOut(epsilon_note),
            FadeOut(covariance_final),
            FadeOut(correlation_line),
            Transform(self.title, summary_title),
            run_time=1.0,
        )
        self.play(FadeIn(summary_bullets, shift=0.2 * UP))
        self.wait(3.0)



